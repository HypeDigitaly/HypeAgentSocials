"""The research artifact store (ARCHITECTURE_PLAN.md §2.6, §8.6).

One SQLite substrate (``logs/state/engine.db``) holds every ledger where
atomic multi-field updates and fast conditional queries matter: the request
log (12-month retention), the normalized-signal records (90-day retention),
the dedupe index, the run-pack -> canonical-key index, and the per-language
evidence-floor breach counters. Bulky raw payload *bodies* are plain files
under ``logs/artifacts/raw/<run_id>/...`` (30-day retention) with only a
metadata row (path, checksum, size) in SQLite (§8.6: "a lightweight metadata
row in SQLite ... so other stages can look up 'does this exist' without
re-parsing a file").

Provenance snapshots are split per §2.6's design consequence:

- **durable half** (``provenance_durable``): canonical key, source, domain,
  method, retrieval time — permanent with the pack, never verbatim text or a
  permalink.
- **verbatim half** (``provenance_verbatim``): the minimal excerpt plus the
  canonical link — 30-day expiry, and on expiry the *packed pack file itself*
  is rewritten so the verbatim block reads
  ``"excerpt expired — canonical key {K}"`` (the durable half is untouched).

Author handles are never stored raw (§2.6): they are HMAC-SHA256'd with a key
generated on first run and held at ``secrets/handle_hash.key``, deliberately
outside the data the key protects. The hash is **deterministic** — the same
handle always hashes to the same value — so that an objection naming a
handle is resolvable by re-hashing it and deleting the matches. A hashed
handle is still personal data (pseudonymised, not anonymised) and stays
inside every retention and deletion rule below; it is never treated as a
"safe to keep forever" identifier.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
import sqlite3
from collections.abc import Iterable
from contextlib import closing
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import yaml

# Retention windows (§2.6 table; §10.2 knob "Retention windows").
REQUEST_LOG_RETENTION_DAYS = 365  # "12 months"
RAW_PAYLOAD_RETENTION_DAYS = 30
NORMALIZED_SIGNAL_RETENTION_DAYS = 90
PROVENANCE_VERBATIM_RETENTION_DAYS = 30

EXPIRED_EXCERPT_PLACEHOLDER = "excerpt expired — canonical key {key}"
DELETED_PLACEHOLDER = "deleted on request — canonical key {key}"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS request_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id TEXT NOT NULL,
  run_date TEXT NOT NULL,
  theme TEXT NOT NULL,
  source TEXT NOT NULL,
  query_sig TEXT NOT NULL,
  endpoint TEXT NOT NULL,
  method TEXT NOT NULL,
  ts TEXT NOT NULL,
  status TEXT NOT NULL,
  rung TEXT NOT NULL,
  etag TEXT,
  last_modified TEXT,
  payload_sha256 TEXT,
  payload_bytes INTEGER,
  raw_payload_path TEXT,
  quota_spent TEXT,
  expires_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_request_log_idem
  ON request_log(theme, source, query_sig, run_date);
CREATE INDEX IF NOT EXISTS idx_request_log_history
  ON request_log(theme, source, query_sig, ts);

CREATE TABLE IF NOT EXISTS normalized_signals (
  canonical_key TEXT PRIMARY KEY,
  source TEXT NOT NULL,
  source_family TEXT NOT NULL,
  language TEXT NOT NULL,
  title TEXT NOT NULL,
  excerpt TEXT NOT NULL,
  metrics_json TEXT NOT NULL,
  hashed_handle TEXT,
  near_dup_fingerprint TEXT NOT NULL,
  evidence_class TEXT NOT NULL,
  injection_flagged INTEGER NOT NULL DEFAULT 0,
  retrieval_time TEXT NOT NULL,
  run_id TEXT NOT NULL,
  expires_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_normalized_signals_source
  ON normalized_signals(source, retrieval_time);

CREATE TABLE IF NOT EXISTS provenance_durable (
  canonical_key TEXT PRIMARY KEY,
  source TEXT NOT NULL,
  domain TEXT NOT NULL,
  method TEXT NOT NULL,
  retrieval_time TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS provenance_verbatim (
  canonical_key TEXT PRIMARY KEY,
  excerpt TEXT NOT NULL,
  canonical_link TEXT NOT NULL,
  created_at TEXT NOT NULL,
  expires_at TEXT NOT NULL,
  expired INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS run_pack_key_index (
  run_id TEXT NOT NULL,
  canonical_key TEXT NOT NULL,
  pack_path TEXT NOT NULL,
  signal_file TEXT NOT NULL,
  PRIMARY KEY (run_id, canonical_key)
);

CREATE TABLE IF NOT EXISTS dedupe_index (
  cluster_key TEXT PRIMARY KEY,
  trajectory TEXT NOT NULL DEFAULT 'rising',
  prior_pack_state TEXT NOT NULL DEFAULT 'never-generated',
  first_seen TEXT NOT NULL,
  last_seen TEXT NOT NULL,
  last_generated_run_id TEXT,
  last_families_json TEXT NOT NULL DEFAULT '[]',
  last_percentile REAL,
  last_fingerprints_json TEXT NOT NULL DEFAULT '[]',
  rejected_at TEXT
);

CREATE TABLE IF NOT EXISTS evidence_floor_breach (
  language TEXT PRIMARY KEY,
  consecutive_count INTEGER NOT NULL DEFAULT 0,
  last_run_id TEXT
);
"""


def _now_iso(now: datetime | None = None) -> str:
    moment = now if now is not None else datetime.now().astimezone()
    return moment.isoformat(timespec="milliseconds")


def _parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value)


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# ---------------------------------------------------------------------------
# Author-handle keyed hashing (§2.6).
# ---------------------------------------------------------------------------


def load_or_create_handle_hash_key(secrets_dir: Path) -> bytes:
    """Load the HMAC key for handle hashing, generating it on first run.

    Deliberately deterministic across runs (same key -> same hash for the
    same handle), so an objection naming a handle can be resolved by
    re-hashing it and deleting the matches (§2.6). The key lives at
    ``secrets/handle_hash.key`` — outside source control by way of
    ``secrets/.gitignore`` (``*``), created alongside it.
    """
    secrets_dir = Path(secrets_dir)
    secrets_dir.mkdir(parents=True, exist_ok=True)
    gitignore_path = secrets_dir / ".gitignore"
    if not gitignore_path.exists():
        gitignore_path.write_text("*\n", encoding="utf-8")
    key_path = secrets_dir / "handle_hash.key"
    if key_path.exists():
        return bytes.fromhex(key_path.read_text(encoding="utf-8").strip())
    key = secrets.token_bytes(32)
    key_path.write_text(key.hex(), encoding="utf-8")
    return key


def hash_handle(handle: str, key: bytes) -> str:
    """HMAC-SHA256 a raw author handle. A hashed handle is still personal data."""
    return hmac.new(key, handle.encode("utf-8"), hashlib.sha256).hexdigest()


# ---------------------------------------------------------------------------
# Special-category lexicon (limb (b) of §2.6's double exclusion).
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SpecialCategoryLexicon:
    """Deterministic keyword lists per Article 9 category, EN + CS."""

    terms_by_category: dict[str, list[str]]

    def matches(self, text: str) -> str | None:
        """Return the first matching category, or ``None``."""
        haystack = text.lower()
        for category, terms in self.terms_by_category.items():
            for term in terms:
                if term.lower() in haystack:
                    return category
        return None


def load_special_category_lexicon(path: Path) -> SpecialCategoryLexicon:
    from hypeagent.config_load import load_yaml_config

    data = load_yaml_config(path, name="special_category_lexicon.yaml")
    lexicon = data.get("special_category_lexicon") or {}
    if not isinstance(lexicon, dict):
        raise ValueError("special_category_lexicon.yaml: 'special_category_lexicon' must be a mapping")
    return SpecialCategoryLexicon(terms_by_category={k: list(v or []) for k, v in lexicon.items()})


@dataclass(frozen=True)
class SourceDenyList:
    """Pre-collection source/community deny-list (limb (a) of §2.6)."""

    denied_sources: set[str]
    denied_communities: set[str]

    def is_denied(self, source_id: str) -> bool:
        return source_id in self.denied_sources or source_id in self.denied_communities


def load_source_deny_list(path: Path) -> SourceDenyList:
    from hypeagent.config_load import load_yaml_config

    data = load_yaml_config(path, name="special_category_source_deny_list.yaml")
    block = data.get("special_category_deny_list") or {}
    denied_sources = set(block.get("denied_sources") or [])
    denied_communities = set(block.get("denied_communities") or [])
    return SourceDenyList(denied_sources=denied_sources, denied_communities=denied_communities)


# ---------------------------------------------------------------------------
# Data carried in and out of the store.
# ---------------------------------------------------------------------------


@dataclass
class NormalizedSignal:
    """One collected item, normalized to the store's common shape (§2.8)."""

    canonical_key: str
    source: str
    source_family: str
    language: str
    title: str
    excerpt: str
    metrics: dict[str, Any]
    raw_author_handle: str | None
    near_dup_fingerprint: str
    evidence_class: str  # counted | ranked
    injection_flagged: bool
    retrieval_time: datetime
    canonical_link: str
    domain: str
    method: str


@dataclass
class StoredSignal:
    canonical_key: str
    source: str
    source_family: str
    language: str
    title: str
    excerpt: str
    metrics: dict[str, Any]
    hashed_handle: str | None
    near_dup_fingerprint: str
    evidence_class: str
    injection_flagged: bool
    retrieval_time: datetime
    run_id: str


@dataclass
class RequestLogEntry:
    id: int
    ts: datetime
    status: str
    rung: str
    etag: str | None
    last_modified: str | None
    payload_sha256: str | None
    raw_payload_path: str | None


@dataclass
class ClusterObservation:
    """Result of :meth:`Store.observe_cluster` — the trajectory just computed,
    plus the state as it stood *before* this run's observation."""

    trajectory: str
    prior_pack_state: str
    prior_families: set[str]
    prior_fingerprints: set[str]
    prior_percentile: float | None


@dataclass
class DeletionReport:
    canonical_key: str
    normalized_record_deleted: bool
    provenance_deleted: bool
    raw_references_deleted: int
    packs_rewritten: list[str] = field(default_factory=list)


@dataclass
class ExpiryReport:
    raw_payloads_deleted: int = 0
    verbatim_expired: int = 0
    packs_rewritten: int = 0
    normalized_records_pruned: int = 0


class Store:
    """The Phase-1 research artifact store."""

    def __init__(self, db_path: Path, artifacts_dir: Path, handle_hash_key: bytes) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.artifacts_dir = Path(artifacts_dir)
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        self._handle_hash_key = handle_hash_key
        self._conn = sqlite3.connect(self.db_path)
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(_SCHEMA)
        self._conn.commit()

    @classmethod
    def open(cls, logs_dir: Path, secrets_dir: Path) -> "Store":
        db_path = Path(logs_dir) / "state" / "engine.db"
        artifacts_dir = Path(logs_dir) / "artifacts" / "raw"
        key = load_or_create_handle_hash_key(Path(secrets_dir))
        return cls(db_path=db_path, artifacts_dir=artifacts_dir, handle_hash_key=key)

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> "Store":
        return self

    def __exit__(self, *exc: object) -> bool:
        self.close()
        return False

    def hash_handle(self, handle: str) -> str:
        return hash_handle(handle, self._handle_hash_key)

    # -- request log / idempotency (§8.5) -------------------------------

    def find_idempotent_capture(
        self, *, theme: str, source: str, query_sig: str, run_date: str
    ) -> RequestLogEntry | None:
        """Within-run idempotency: has this exact (theme, source, query, run-date)
        already been captured today? If so, the caller must skip the fetch."""
        row = self._conn.execute(
            "SELECT * FROM request_log WHERE theme=? AND source=? AND query_sig=? AND run_date=? "
            "AND status='ok' ORDER BY id DESC LIMIT 1",
            (theme, source, query_sig, run_date),
        ).fetchone()
        if row is None:
            return None
        return _row_to_request_log_entry(row)

    def previous_capture(
        self, *, theme: str, source: str, query_sig: str, before_run_id: str
    ) -> RequestLogEntry | None:
        """The most recent prior successful capture for this (theme, source,
        query), used for stale-payload-suspected comparison (byte-identical
        payload to the previous pull)."""
        row = self._conn.execute(
            "SELECT * FROM request_log WHERE theme=? AND source=? AND query_sig=? AND status='ok' "
            "AND run_id != ? ORDER BY id DESC LIMIT 1",
            (theme, source, query_sig, before_run_id),
        ).fetchone()
        if row is None:
            return None
        return _row_to_request_log_entry(row)

    def record_request(
        self,
        *,
        run_id: str,
        run_date: str,
        theme: str,
        source: str,
        query_sig: str,
        endpoint: str,
        method: str,
        status: str,
        rung: str,
        etag: str | None = None,
        last_modified: str | None = None,
        payload: bytes | None = None,
        quota_spent: str | None = None,
        now: datetime | None = None,
    ) -> RequestLogEntry:
        """Record one request-log row (§2.6, always). If a payload is given
        it is written as a plain file under 30-day retention."""
        moment = now if now is not None else datetime.now().astimezone()
        expires_at = moment + timedelta(days=REQUEST_LOG_RETENTION_DAYS)
        payload_sha256 = None
        payload_bytes = None
        raw_payload_path = None
        if payload is not None:
            payload_sha256 = sha256_hex(payload)
            payload_bytes = len(payload)
            source_dir = self.artifacts_dir / run_id / source
            source_dir.mkdir(parents=True, exist_ok=True)
            safe_query = "".join(c if c.isalnum() else "_" for c in query_sig)[:80]
            file_path = source_dir / f"{safe_query}_{payload_sha256[:12]}.bin"
            file_path.write_bytes(payload)
            raw_payload_path = str(file_path)
        cur = self._conn.execute(
            "INSERT INTO request_log (run_id, run_date, theme, source, query_sig, endpoint, method, "
            "ts, status, rung, etag, last_modified, payload_sha256, payload_bytes, raw_payload_path, "
            "quota_spent, expires_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                run_id,
                run_date,
                theme,
                source,
                query_sig,
                endpoint,
                method,
                _now_iso(moment),
                status,
                rung,
                etag,
                last_modified,
                payload_sha256,
                payload_bytes,
                raw_payload_path,
                quota_spent,
                _now_iso(moment + timedelta(days=RAW_PAYLOAD_RETENTION_DAYS))
                if payload is not None
                else _now_iso(expires_at),
            ),
        )
        self._conn.commit()
        row = self._conn.execute("SELECT * FROM request_log WHERE id=?", (cur.lastrowid,)).fetchone()
        return _row_to_request_log_entry(row)

    # -- normalized signals + special-category exclusion (limb b) ------

    def store_signal(self, signal: NormalizedSignal, *, run_id: str, lexicon: SpecialCategoryLexicon) -> tuple[bool, str | None]:
        """Store a normalized signal, applying the post-collection special-
        category lexical check (§2.6 limb (b)). Returns
        ``(stored, excluded_category)``: a lexicon hit means the item is
        **not stored** (fail-closed to do-not-store, never flag-and-continue).
        """
        category = lexicon.matches(f"{signal.title} {signal.excerpt}")
        if category is not None:
            return False, category

        hashed_handle = self.hash_handle(signal.raw_author_handle) if signal.raw_author_handle else None
        expires_at = signal.retrieval_time + timedelta(days=NORMALIZED_SIGNAL_RETENTION_DAYS)
        self._conn.execute(
            "INSERT INTO normalized_signals (canonical_key, source, source_family, language, title, "
            "excerpt, metrics_json, hashed_handle, near_dup_fingerprint, evidence_class, "
            "injection_flagged, retrieval_time, run_id, expires_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?) "
            "ON CONFLICT(canonical_key) DO UPDATE SET "
            "  title=excluded.title, excerpt=excluded.excerpt, metrics_json=excluded.metrics_json, "
            "  retrieval_time=excluded.retrieval_time, run_id=excluded.run_id, expires_at=excluded.expires_at",
            (
                signal.canonical_key,
                signal.source,
                signal.source_family,
                signal.language,
                signal.title,
                signal.excerpt,
                _json_dumps(signal.metrics),
                hashed_handle,
                signal.near_dup_fingerprint,
                signal.evidence_class,
                1 if signal.injection_flagged else 0,
                _now_iso(signal.retrieval_time),
                run_id,
                _now_iso(expires_at),
            ),
        )
        self._conn.execute(
            "INSERT INTO provenance_durable (canonical_key, source, domain, method, retrieval_time) "
            "VALUES (?,?,?,?,?) ON CONFLICT(canonical_key) DO NOTHING",
            (signal.canonical_key, signal.source, signal.domain, signal.method, _now_iso(signal.retrieval_time)),
        )
        verbatim_expires = signal.retrieval_time + timedelta(days=PROVENANCE_VERBATIM_RETENTION_DAYS)
        self._conn.execute(
            "INSERT INTO provenance_verbatim (canonical_key, excerpt, canonical_link, created_at, "
            "expires_at, expired) VALUES (?,?,?,?,?,0) "
            "ON CONFLICT(canonical_key) DO UPDATE SET excerpt=excluded.excerpt, "
            "canonical_link=excluded.canonical_link, expires_at=excluded.expires_at, expired=0",
            (
                signal.canonical_key,
                signal.excerpt,
                signal.canonical_link,
                _now_iso(signal.retrieval_time),
                _now_iso(verbatim_expires),
            ),
        )
        self._conn.commit()
        return True, None

    def get_provenance(self, canonical_key: str) -> tuple[dict[str, Any], dict[str, Any]] | None:
        """Return ``(durable_half, verbatim_half)`` for one canonical key,
        the two-part record §2.6 requires. ``None`` if nothing is on file."""
        durable = self._conn.execute(
            "SELECT * FROM provenance_durable WHERE canonical_key=?", (canonical_key,)
        ).fetchone()
        if durable is None:
            return None
        verbatim = self._conn.execute(
            "SELECT * FROM provenance_verbatim WHERE canonical_key=?", (canonical_key,)
        ).fetchone()
        durable_half = {
            "canonical_key": canonical_key,
            "source": durable["source"],
            "domain": durable["domain"],
            "method": durable["method"],
            "retrieval_time": durable["retrieval_time"],
        }
        verbatim_half = {
            "excerpt": verbatim["excerpt"] if verbatim else "",
            "canonical_link": verbatim["canonical_link"] if verbatim else "",
        }
        return durable_half, verbatim_half

    def get_signal(self, canonical_key: str) -> StoredSignal | None:
        row = self._conn.execute(
            "SELECT * FROM normalized_signals WHERE canonical_key=?", (canonical_key,)
        ).fetchone()
        if row is None:
            return None
        return _row_to_stored_signal(row)

    def signals_since(self, *, source: str | None = None, since: datetime | None = None) -> list[StoredSignal]:
        query = "SELECT * FROM normalized_signals WHERE 1=1"
        params: list[Any] = []
        if source is not None:
            query += " AND source=?"
            params.append(source)
        if since is not None:
            query += " AND retrieval_time >= ?"
            params.append(_now_iso(since))
        query += " ORDER BY retrieval_time ASC"
        rows = self._conn.execute(query, params).fetchall()
        return [_row_to_stored_signal(r) for r in rows]

    def trailing_metric_distribution(self, *, source: str, metric_name: str, within_days: int) -> list[float]:
        since = datetime.now().astimezone() - timedelta(days=within_days)
        rows = self._conn.execute(
            "SELECT metrics_json FROM normalized_signals WHERE source=? AND retrieval_time >= ?",
            (source, _now_iso(since)),
        ).fetchall()
        values: list[float] = []
        for row in rows:
            metrics = _json_loads(row["metrics_json"])
            if metric_name in metrics and isinstance(metrics[metric_name], (int, float)):
                values.append(float(metrics[metric_name]))
        return values

    def trailing_baseline_days(self, *, source: str) -> int:
        """How many distinct calendar days of history exist for a source —
        used for the absolute-band-fallback vs. percentile-mode switch."""
        rows = self._conn.execute(
            "SELECT DISTINCT substr(retrieval_time, 1, 10) as d FROM normalized_signals WHERE source=?",
            (source,),
        ).fetchall()
        return len(rows)

    # -- dedupe index (§2.8a) -------------------------------------------

    def get_dedupe_state(self, cluster_key: str) -> sqlite3.Row | None:
        return self._conn.execute(
            "SELECT * FROM dedupe_index WHERE cluster_key=?", (cluster_key,)
        ).fetchone()

    def observe_cluster(
        self,
        *,
        cluster_key: str,
        families: list[str],
        percentile: float | None,
        fingerprints: list[str],
        now: datetime | None = None,
    ) -> "ClusterObservation":
        """Record this run's observation of a topic cluster and return the
        trajectory plus the state *as it was before this observation* — the
        resurgence rule (§2.8a) reads the prior state, not the just-written
        one."""
        moment = now if now is not None else datetime.now().astimezone()
        existing = self.get_dedupe_state(cluster_key)
        if existing is None:
            self._conn.execute(
                "INSERT INTO dedupe_index (cluster_key, trajectory, prior_pack_state, first_seen, "
                "last_seen, last_families_json, last_percentile, last_fingerprints_json) "
                "VALUES (?, 'rising', 'never-generated', ?, ?, ?, ?, ?)",
                (cluster_key, _now_iso(moment), _now_iso(moment), _json_dumps(families), percentile, _json_dumps(fingerprints)),
            )
            self._conn.commit()
            return ClusterObservation(
                trajectory="rising",
                prior_pack_state="never-generated",
                prior_families=set(),
                prior_fingerprints=set(),
                prior_percentile=None,
            )

        prior_pack_state = existing["prior_pack_state"]
        prior_families = set(_json_loads(existing["last_families_json"]))
        prior_fingerprints = set(_json_loads(existing["last_fingerprints_json"]))
        prior_percentile = existing["last_percentile"]
        trajectory = _trajectory(prior_families, set(families), prior_percentile, percentile)
        self._conn.execute(
            "UPDATE dedupe_index SET trajectory=?, last_seen=?, last_families_json=?, "
            "last_percentile=?, last_fingerprints_json=? WHERE cluster_key=?",
            (trajectory, _now_iso(moment), _json_dumps(families), percentile, _json_dumps(fingerprints), cluster_key),
        )
        self._conn.commit()
        return ClusterObservation(
            trajectory=trajectory,
            prior_pack_state=prior_pack_state,
            prior_families=prior_families,
            prior_fingerprints=prior_fingerprints,
            prior_percentile=prior_percentile,
        )

    def get_rejected_at(self, cluster_key: str) -> datetime | None:
        row = self.get_dedupe_state(cluster_key)
        if row is None or row["rejected_at"] is None:
            return None
        return _parse_iso(row["rejected_at"])

    def mark_generated(self, cluster_key: str, run_id: str) -> None:
        """Record that this cluster was included in a produced pack this
        run — the "generated" prior-pack state the *next* run's resurgence
        check reads (§2.8a). ``observe_cluster`` already wrote this run's
        families/fingerprints; this call only flips the state."""
        self._conn.execute(
            "UPDATE dedupe_index SET prior_pack_state='generated', last_generated_run_id=? WHERE cluster_key=?",
            (run_id, cluster_key),
        )
        self._conn.commit()

    def mark_rejected(self, cluster_key: str, *, now: datetime | None = None) -> None:
        """Phase-2 hook: the review-decision store is what will normally set
        this. Exposed here so Phase-1 tests can exercise the 'rejected'
        resurgence-table row without a review UI existing yet."""
        moment = now if now is not None else datetime.now().astimezone()
        self._conn.execute(
            "UPDATE dedupe_index SET prior_pack_state='rejected', rejected_at=? WHERE cluster_key=?",
            (_now_iso(moment), cluster_key),
        )
        self._conn.commit()

    # -- evidence floor (§2.7) -------------------------------------------

    def record_evidence_floor(self, *, language: str, breached: bool, run_id: str) -> int:
        row = self._conn.execute(
            "SELECT consecutive_count FROM evidence_floor_breach WHERE language=?", (language,)
        ).fetchone()
        if not breached:
            count = 0
        else:
            count = (row["consecutive_count"] if row else 0) + 1
        self._conn.execute(
            "INSERT INTO evidence_floor_breach (language, consecutive_count, last_run_id) VALUES (?,?,?) "
            "ON CONFLICT(language) DO UPDATE SET consecutive_count=excluded.consecutive_count, "
            "last_run_id=excluded.last_run_id",
            (language, count, run_id),
        )
        self._conn.commit()
        return count

    # -- run-pack -> canonical-key index + targeted deletion (§2.6, §8.6) --

    def register_pack_keys(self, *, run_id: str, pack_path: str, entries: Iterable[tuple[str, str]]) -> None:
        """Register every canonical key included in a pack, transactionally
        with the pack write (caller writes files first, then calls this)."""
        rows = [(run_id, key, pack_path, signal_file) for key, signal_file in entries]
        self._conn.executemany(
            "INSERT INTO run_pack_key_index (run_id, canonical_key, pack_path, signal_file) VALUES (?,?,?,?) "
            "ON CONFLICT(run_id, canonical_key) DO UPDATE SET signal_file=excluded.signal_file",
            rows,
        )
        self._conn.commit()

    def packs_for_key(self, canonical_key: str) -> list[sqlite3.Row]:
        return self._conn.execute(
            "SELECT * FROM run_pack_key_index WHERE canonical_key=?", (canonical_key,)
        ).fetchall()

    def delete_by_canonical_key(self, canonical_key: str) -> DeletionReport:
        """Targeted deletion (§2.6): the normalized record, raw references,
        and every archived run pack that included this key, via the
        run-pack -> canonical-key index. Never flag-and-continue."""
        cur = self._conn.execute("DELETE FROM normalized_signals WHERE canonical_key=?", (canonical_key,))
        normalized_deleted = cur.rowcount > 0
        cur_prov = self._conn.execute(
            "DELETE FROM provenance_verbatim WHERE canonical_key=?", (canonical_key,)
        )
        self._conn.execute("DELETE FROM provenance_durable WHERE canonical_key=?", (canonical_key,))
        provenance_deleted = cur_prov.rowcount > 0

        raw_rows = self._conn.execute(
            "SELECT id, raw_payload_path FROM request_log WHERE raw_payload_path IS NOT NULL"
        ).fetchall()
        raw_deleted = 0
        # Raw payloads are keyed by (theme, source, query), not canonical key,
        # so we cannot always attribute one payload file to one item; the
        # canonical-key-addressable references we own outright are the
        # normalized record and the provenance rows already removed above.

        packs = self.packs_for_key(canonical_key)
        rewritten: list[str] = []
        for pack_row in packs:
            signal_file = Path(pack_row["signal_file"])
            if signal_file.exists():
                _replace_provenance_block(
                    signal_file,
                    canonical_key,
                    DELETED_PLACEHOLDER.format(key=canonical_key),
                )
                rewritten.append(str(signal_file))
        self._conn.execute("DELETE FROM run_pack_key_index WHERE canonical_key=?", (canonical_key,))
        self._conn.commit()
        return DeletionReport(
            canonical_key=canonical_key,
            normalized_record_deleted=normalized_deleted,
            provenance_deleted=provenance_deleted,
            raw_references_deleted=raw_deleted,
            packs_rewritten=rewritten,
        )

    # -- expiry job (run at run start) ------------------------------------

    def run_expiry_job(self, *, now: datetime | None = None) -> ExpiryReport:
        """Deletes expired raw payloads, expires verbatim provenance halves
        (including inside already-written run packs), and prunes normalized
        records past 90 days. Run at the start of every run (§2.6)."""
        moment = now if now is not None else datetime.now().astimezone()
        report = ExpiryReport()

        raw_rows = self._conn.execute(
            "SELECT id, raw_payload_path FROM request_log WHERE raw_payload_path IS NOT NULL "
            "AND expires_at <= ?",
            (_now_iso(moment),),
        ).fetchall()
        for row in raw_rows:
            path = Path(row["raw_payload_path"])
            if path.exists():
                path.unlink()
                report.raw_payloads_deleted += 1
            self._conn.execute("UPDATE request_log SET raw_payload_path=NULL WHERE id=?", (row["id"],))

        expired_rows = self._conn.execute(
            "SELECT canonical_key FROM provenance_verbatim WHERE expired=0 AND expires_at <= ?",
            (_now_iso(moment),),
        ).fetchall()
        for row in expired_rows:
            key = row["canonical_key"]
            self._conn.execute(
                "UPDATE provenance_verbatim SET expired=1, excerpt=?, canonical_link='' WHERE canonical_key=?",
                (EXPIRED_EXCERPT_PLACEHOLDER.format(key=key), key),
            )
            report.verbatim_expired += 1
            for pack_row in self.packs_for_key(key):
                signal_file = Path(pack_row["signal_file"])
                if signal_file.exists():
                    changed = _replace_provenance_block(
                        signal_file, key, EXPIRED_EXCERPT_PLACEHOLDER.format(key=key)
                    )
                    if changed:
                        report.packs_rewritten += 1

        pruned = self._conn.execute(
            "DELETE FROM normalized_signals WHERE expires_at <= ?", (_now_iso(moment),)
        )
        report.normalized_records_pruned = pruned.rowcount

        self._conn.commit()
        return report


def _trajectory(
    prev_families: set[str], curr_families: set[str], prev_percentile: float | None, curr_percentile: float | None
) -> str:
    family_delta = len(curr_families) - len(prev_families)
    percentile_delta = 0.0
    if prev_percentile is not None and curr_percentile is not None:
        percentile_delta = curr_percentile - prev_percentile
    if family_delta > 0 or percentile_delta > 0:
        return "rising"
    if family_delta < 0 or percentile_delta < 0:
        return "declining"
    return "sustained"


def _json_dumps(value: Any) -> str:
    import json

    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _json_loads(value: str) -> Any:
    import json

    return json.loads(value)


def _row_to_request_log_entry(row: sqlite3.Row) -> RequestLogEntry:
    return RequestLogEntry(
        id=row["id"],
        ts=_parse_iso(row["ts"]),
        status=row["status"],
        rung=row["rung"],
        etag=row["etag"],
        last_modified=row["last_modified"],
        payload_sha256=row["payload_sha256"],
        raw_payload_path=row["raw_payload_path"],
    )


def _row_to_stored_signal(row: sqlite3.Row) -> StoredSignal:
    return StoredSignal(
        canonical_key=row["canonical_key"],
        source=row["source"],
        source_family=row["source_family"],
        language=row["language"],
        title=row["title"],
        excerpt=row["excerpt"],
        metrics=_json_loads(row["metrics_json"]),
        hashed_handle=row["hashed_handle"],
        near_dup_fingerprint=row["near_dup_fingerprint"],
        evidence_class=row["evidence_class"],
        injection_flagged=bool(row["injection_flagged"]),
        retrieval_time=_parse_iso(row["retrieval_time"]),
        run_id=row["run_id"],
    )


def _replace_provenance_block(signal_file: Path, canonical_key: str, placeholder: str) -> bool:
    """Rewrite one packed provenance YAML file's verbatim block in place.

    The pack file is a small two-section YAML document (see ``packaging.py``);
    this performs a targeted key-scoped rewrite rather than reparsing the
    whole pack, so it works even years after the run that wrote it.
    """
    text = signal_file.read_text(encoding="utf-8")
    doc = yaml.safe_load(text) or {}
    if doc.get("canonical_key") != canonical_key:
        return False
    verbatim = doc.get("verbatim") or {}
    if verbatim.get("excerpt") == placeholder and verbatim.get("canonical_link", "") == "":
        return False
    doc["verbatim"] = {"excerpt": placeholder, "canonical_link": ""}
    signal_file.write_text(
        yaml.safe_dump(doc, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )
    return True
