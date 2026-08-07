"""Tests for hypeagent.store — the research artifact store (§2.6, §8.6)."""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest
import yaml

from hypeagent.store import (
    NormalizedSignal,
    SpecialCategoryLexicon,
    SourceDenyList,
    Store,
    hash_handle,
    load_or_create_handle_hash_key,
)


def _signal(canonical_key="url:https://example.com/a", handle="alice123", excerpt="An AI agent for sales automation launched today", **overrides):
    defaults = dict(
        canonical_key=canonical_key,
        source="hacker_news",
        source_family="developer_technical_discourse",
        language="en",
        title="An AI agent launch",
        excerpt=excerpt,
        metrics={"score": 100},
        raw_author_handle=handle,
        near_dup_fingerprint="fp1",
        evidence_class="counted",
        injection_flagged=False,
        retrieval_time=datetime.now().astimezone(),
        canonical_link="https://example.com/a",
        domain="example.com",
        method="official API",
    )
    defaults.update(overrides)
    return NormalizedSignal(**defaults)


def _store(tmp_path) -> Store:
    return Store.open(tmp_path / "logs", tmp_path / "secrets")


def _lexicon(**terms) -> SpecialCategoryLexicon:
    return SpecialCategoryLexicon(terms_by_category=terms or {"health_condition": ["depression"]})


class TestHandleHashing:
    def test_handle_hashing_is_deterministic_and_key_persists(self, tmp_path):
        key1 = load_or_create_handle_hash_key(tmp_path / "secrets")
        key2 = load_or_create_handle_hash_key(tmp_path / "secrets")
        assert key1 == key2
        assert hash_handle("alice123", key1) == hash_handle("alice123", key2)

    def test_gitignore_created_alongside_key(self, tmp_path):
        load_or_create_handle_hash_key(tmp_path / "secrets")
        gitignore = (tmp_path / "secrets" / ".gitignore").read_text(encoding="utf-8")
        assert gitignore.strip() == "*"

    def test_raw_handle_never_stored_but_rehash_finds_the_record(self, tmp_path):
        store = _store(tmp_path)
        try:
            sig = _signal(handle="alice123")
            stored, _ = store.store_signal(sig, run_id="2026-08-10_a1a1", lexicon=_lexicon())
            assert stored
            record = store.get_signal(sig.canonical_key)
            assert "alice123" not in (record.hashed_handle or "")
            expected = store.hash_handle("alice123")
            assert record.hashed_handle == expected
        finally:
            store.close()

        # Raw handle never appears anywhere on disk in the DB file.
        db_bytes = (tmp_path / "logs" / "state" / "engine.db").read_bytes()
        assert b"alice123" not in db_bytes


class TestSpecialCategoryLexicon:
    def test_lexicon_hit_means_item_never_stored(self, tmp_path):
        store = _store(tmp_path)
        try:
            sig = _signal(excerpt="A community discussion about living with depression and AI tools")
            stored, category = store.store_signal(sig, run_id="r1", lexicon=_lexicon(health_condition=["depression"]))
            assert stored is False
            assert category == "health_condition"
            assert store.get_signal(sig.canonical_key) is None
        finally:
            store.close()

    def test_clean_excerpt_is_stored(self, tmp_path):
        store = _store(tmp_path)
        try:
            sig = _signal()
            stored, category = store.store_signal(sig, run_id="r1", lexicon=_lexicon(health_condition=["depression"]))
            assert stored is True
            assert category is None
        finally:
            store.close()


class TestSourceDenyList:
    def test_denied_source_is_denied(self):
        deny = SourceDenyList(denied_sources={"some_forum"}, denied_communities={"some_subreddit"})
        assert deny.is_denied("some_forum")
        assert deny.is_denied("some_subreddit")
        assert not deny.is_denied("hacker_news")


class TestIdempotency:
    def test_same_day_capture_is_found(self, tmp_path):
        store = _store(tmp_path)
        try:
            store.record_request(
                run_id="2026-08-10_a1a1", run_date="2026-08-10", theme="hypedigitaly", source="hacker_news",
                query_sig="topstories", endpoint="https://x", method="GET", status="ok", rung="primary",
                payload=b"hello",
            )
            hit = store.find_idempotent_capture(theme="hypedigitaly", source="hacker_news", query_sig="topstories", run_date="2026-08-10")
            assert hit is not None
            miss = store.find_idempotent_capture(theme="hypedigitaly", source="hacker_news", query_sig="topstories", run_date="2026-08-11")
            assert miss is None
        finally:
            store.close()

    def test_stale_payload_detection_via_previous_capture(self, tmp_path):
        store = _store(tmp_path)
        try:
            store.record_request(
                run_id="2026-08-10_a1a1", run_date="2026-08-10", theme="hypedigitaly", source="hacker_news",
                query_sig="topstories", endpoint="https://x", method="GET", status="ok", rung="primary",
                payload=b"same-bytes",
            )
            prior = store.previous_capture(theme="hypedigitaly", source="hacker_news", query_sig="topstories", before_run_id="2026-08-11_b2b2")
            assert prior is not None
            from hypeagent.store import sha256_hex

            assert prior.payload_sha256 == sha256_hex(b"same-bytes")
        finally:
            store.close()


class TestTargetedDeletion:
    def test_delete_by_canonical_key_removes_live_record(self, tmp_path):
        store = _store(tmp_path)
        try:
            sig = _signal()
            store.store_signal(sig, run_id="r1", lexicon=_lexicon())
            assert store.get_signal(sig.canonical_key) is not None
            report = store.delete_by_canonical_key(sig.canonical_key)
            assert report.normalized_record_deleted is True
            assert store.get_signal(sig.canonical_key) is None
        finally:
            store.close()

    def test_delete_by_canonical_key_reaches_inside_an_archived_pack(self, tmp_path):
        store = _store(tmp_path)
        try:
            sig = _signal(excerpt="Original excerpt text")
            store.store_signal(sig, run_id="r1", lexicon=_lexicon())

            # Simulate what packaging.py writes: a signals/*.yaml two-part record.
            pack_dir = tmp_path / "logs" / "runs" / "r1" / "pack"
            (pack_dir / "signals").mkdir(parents=True)
            signal_file = pack_dir / "signals" / "sig.yaml"
            doc = {
                "canonical_key": sig.canonical_key,
                "durable": {"canonical_key": sig.canonical_key, "source": "hacker_news", "domain": "example.com", "method": "official API", "retrieval_time": "2026-08-10"},
                "verbatim": {"excerpt": "Original excerpt text", "canonical_link": "https://example.com/a"},
            }
            signal_file.write_text(yaml.safe_dump(doc, allow_unicode=True), encoding="utf-8")
            store.register_pack_keys(run_id="r1", pack_path=str(pack_dir), entries=[(sig.canonical_key, str(signal_file))])

            report = store.delete_by_canonical_key(sig.canonical_key)
            assert str(signal_file) in report.packs_rewritten

            rewritten = yaml.safe_load(signal_file.read_text(encoding="utf-8"))
            assert "Original excerpt text" not in yaml.safe_dump(rewritten)
            assert "deleted on request" in rewritten["verbatim"]["excerpt"]
            # The durable half is untouched.
            assert rewritten["durable"]["source"] == "hacker_news"
        finally:
            store.close()


class TestExpiryJob:
    def test_verbatim_half_expires_and_rewrites_packed_pack(self, tmp_path):
        store = _store(tmp_path)
        try:
            old_time = datetime.now().astimezone() - timedelta(days=31)
            sig = _signal(excerpt="This excerpt should expire", retrieval_time=old_time)
            store.store_signal(sig, run_id="r1", lexicon=_lexicon())

            pack_dir = tmp_path / "logs" / "runs" / "r1" / "pack"
            (pack_dir / "signals").mkdir(parents=True)
            signal_file = pack_dir / "signals" / "sig.yaml"
            doc = {
                "canonical_key": sig.canonical_key,
                "durable": {"canonical_key": sig.canonical_key, "source": "hacker_news", "domain": "example.com", "method": "official API", "retrieval_time": "2026-07-01"},
                "verbatim": {"excerpt": "This excerpt should expire", "canonical_link": "https://example.com/a"},
            }
            signal_file.write_text(yaml.safe_dump(doc, allow_unicode=True), encoding="utf-8")
            store.register_pack_keys(run_id="r1", pack_path=str(pack_dir), entries=[(sig.canonical_key, str(signal_file))])

            report = store.run_expiry_job()
            assert report.verbatim_expired >= 1
            assert report.packs_rewritten >= 1

            rewritten = yaml.safe_load(signal_file.read_text(encoding="utf-8"))
            assert "expired" in rewritten["verbatim"]["excerpt"]
            assert sig.canonical_key in rewritten["verbatim"]["excerpt"]
            assert rewritten["durable"]["source"] == "hacker_news"  # durable half remains
        finally:
            store.close()

    def test_raw_payload_deleted_after_30_days(self, tmp_path):
        store = _store(tmp_path)
        try:
            old_time = datetime.now().astimezone() - timedelta(days=31)
            store.record_request(
                run_id="r1", run_date="2026-07-01", theme="hypedigitaly", source="hacker_news",
                query_sig="topstories", endpoint="https://x", method="GET", status="ok", rung="primary",
                payload=b"expiring bytes", now=old_time,
            )
            report = store.run_expiry_job()
            assert report.raw_payloads_deleted == 1
        finally:
            store.close()

    def test_normalized_records_pruned_after_90_days(self, tmp_path):
        store = _store(tmp_path)
        try:
            old_time = datetime.now().astimezone() - timedelta(days=91)
            sig = _signal(retrieval_time=old_time)
            store.store_signal(sig, run_id="r1", lexicon=_lexicon())
            report = store.run_expiry_job()
            assert report.normalized_records_pruned == 1
            assert store.get_signal(sig.canonical_key) is None
        finally:
            store.close()


class TestRegisterRawArtifact:
    """W8-9 Phase 2: a derived artifact (e.g. ``virlo_corpus.yaml``, a
    downloaded media file) rides the SAME 30-day raw-payload retention job
    that already covers HTTP payload bodies — no second expiry mechanism."""

    def test_registered_artifact_is_deleted_after_30_days(self, tmp_path):
        store = _store(tmp_path)
        try:
            artifact_path = tmp_path / "logs" / "runs" / "r1" / "virlo_corpus.yaml"
            artifact_path.parent.mkdir(parents=True)
            artifact_path.write_text("monitor_id: abc\n", encoding="utf-8")
            old_time = datetime.now().astimezone() - timedelta(days=31)

            store.register_raw_artifact(
                run_id="r1", run_date="2026-07-01", theme="hypedigitaly", source="virlo",
                query_sig="corpus:abc", endpoint="virlo-corpus", path=artifact_path, now=old_time,
            )
            assert artifact_path.exists()

            report = store.run_expiry_job()
            assert report.raw_payloads_deleted == 1
            assert not artifact_path.exists()
        finally:
            store.close()

    def test_registered_artifact_survives_within_retention_window(self, tmp_path):
        store = _store(tmp_path)
        try:
            artifact_path = tmp_path / "logs" / "runs" / "r1" / "virlo_corpus.yaml"
            artifact_path.parent.mkdir(parents=True)
            artifact_path.write_text("monitor_id: abc\n", encoding="utf-8")

            store.register_raw_artifact(
                run_id="r1", run_date="2026-08-01", theme="hypedigitaly", source="virlo",
                query_sig="corpus:abc", endpoint="virlo-corpus", path=artifact_path,
            )
            report = store.run_expiry_job()
            assert report.raw_payloads_deleted == 0
            assert artifact_path.exists()
        finally:
            store.close()

    def test_does_not_write_a_second_copy_of_the_file(self, tmp_path):
        """Unlike ``record_request``, this never writes bytes itself — the
        caller already has the file on disk."""
        store = _store(tmp_path)
        try:
            artifact_path = tmp_path / "logs" / "runs" / "r1" / "virlo_corpus.yaml"
            artifact_path.parent.mkdir(parents=True)
            artifact_path.write_text("monitor_id: abc\n", encoding="utf-8")

            entry = store.register_raw_artifact(
                run_id="r1", run_date="2026-08-01", theme="hypedigitaly", source="virlo",
                query_sig="corpus:abc", endpoint="virlo-corpus", path=artifact_path,
            )
            assert entry.raw_payload_path == str(artifact_path)
        finally:
            store.close()


class TestHandleHashKeyConfigDirResolution:
    """W8-9 Phase 1: ``HANDLE_HASH_KEY`` resolves from the environment/.env
    before the legacy ``secrets/handle_hash.key`` file, when ``config_dir``
    is given; ``config_dir=None`` reproduces the exact old behavior."""

    def test_config_dir_none_reproduces_old_behavior(self, tmp_path):
        key1 = load_or_create_handle_hash_key(tmp_path / "secrets")
        key2 = load_or_create_handle_hash_key(tmp_path / "secrets", config_dir=None)
        assert key1 == key2

    def test_dotenv_value_used_when_config_dir_given(self, tmp_path, monkeypatch):
        monkeypatch.delenv("HANDLE_HASH_KEY", raising=False)
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        hex_key = "11" * 32
        (tmp_path / ".env").write_text(f"HANDLE_HASH_KEY={hex_key}\n", encoding="utf-8")

        key = load_or_create_handle_hash_key(tmp_path / "secrets", config_dir=config_dir)
        assert key == bytes.fromhex(hex_key)

    def test_malformed_dotenv_value_falls_back_to_legacy_or_generated(self, tmp_path, monkeypatch):
        monkeypatch.delenv("HANDLE_HASH_KEY", raising=False)
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        (tmp_path / ".env").write_text("HANDLE_HASH_KEY=not_valid_hex!!\n", encoding="utf-8")

        # Never raises -- degrades to generating (or reading) the legacy file.
        key = load_or_create_handle_hash_key(tmp_path / "secrets", config_dir=config_dir)
        assert isinstance(key, bytes) and len(key) == 32
