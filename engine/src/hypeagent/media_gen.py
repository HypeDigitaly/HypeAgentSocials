"""Kie.ai draft-tier IMAGE generation (GOAL_ROADMAP.md M4; ARCHITECTURE_PLAN.md
§4.6-§4.7, §5.2-§5.7, §8.5, §8.11, §8.13).

Scope, exactly as the goal bounds it: **images only, draft tier only,
drafts only** -- nothing publishes, no video, no voice, no FFmpeg
composition/overlay (the pack carries the raw generated image plus its
brief; logo overlay is a later phase).

Three things this module makes true by construction, not by discipline:

1. **The write-ahead spend ledger IS the idempotency mechanism** (§8.5).
   :class:`hypeagent.store.Store`'s ``media_intents`` table commits an
   intent row identified by (theme, run_date, cluster_key, asset_slot,
   language, prompt_pattern_version, attempt) *before* ``createTask`` is
   called. The provider's task id is written the moment it is returned.
   On restart, an unresolved row is resolved by querying ``recordInfo``,
   never by blind resubmission -- see :meth:`MediaGenerator.resolve_pending`,
   run as phase 0 of every media stage invocation.
2. **Both caps are checked at every submission, and whichever trips first
   stops that submission** (§8.11) -- ``count-capped`` and ``budget-capped``
   are distinct, named statuses, never merged into one "capped" bucket.
3. **The Kie API key never reaches the trace.** ``KieClient`` builds the
   ``Authorization`` header outside the dict that gets traced (same
   discipline as ``collectors/virlo.py``); provider result URLs are
   downloaded and re-hosted immediately and never appear in a pack (§5.5).

**Simplifications named here, not hidden**, matching this codebase's own
convention of stating a narrowed scope explicitly (e.g. ``brand_truth``'s
one-trigger degrade posture):

- The refusal ladder (§5.6: sanitize-and-rewrite -> model swap -> degrade)
  is simplified to its own terminal rung: a provider-reported content
  refusal degrades the asset straight to plan-only with the reason
  attached. The two earlier rungs are not implemented this milestone.
- The ``submitted-unknown`` -> ``paid-lost`` terminal disposition's
  *window* is tracked (bounded by ``resolution_window_days``), but the
  "exactly one fresh attempt under a new identity, on explicit operator
  action" step is not built -- there is no operator-action surface in this
  engine yet. The row is named in the digest and never auto-resubmitted,
  which is the money-safety property that actually matters.
- Balance-delta reconciliation runs once per resolved submission this run
  (not continuously); good enough to trip the circuit breaker mid-pack
  and to halt further submissions, which is the behaviour §8.13 requires.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from hypeagent.collectors.base import FetchError, Fetcher
from hypeagent.config_load import ConfigError, MediaConfig, load_yaml_config
from hypeagent.store import MediaIntentAlreadyExists, MediaIntentRow, Store
from hypeagent.trace import TraceWriter

PROMPT_PATTERN_VERSION = 1
ATTEMPT_MAX = 2

CREATE_TASK_ALLOWED_KEYS = {"model", "input_keys", "prompt_sha256", "prompt_len", "output_format", "aspect_ratio"}
RECORD_INFO_ALLOWED_KEYS = {"taskId"}
RESPONSE_ALLOWED_KEYS = {
    "bytes", "error", "code", "msg", "taskId", "state", "model", "failCode", "failMsg",
    "progress", "creditsConsumed", "result_url_count",
}

# Injected, non-configurable prompt constraints (R2-M18 people-free default;
# Policy A no-product-depiction; this milestone additionally forbids ALL
# rendered text/lettering, because the claim gate's surface must stay
# closed -- the copy headline is overlay-for-later, never burned into the
# image, §14.3/§14.6).
_NEGATIVE_CONSTRAINTS = (
    "no people, no human figures, no faces, no hands; "
    "no text, no lettering, no words, no captions, no typography of any kind; "
    "no logos, no brand marks; "
    "no product screenshots, no app UI, no dashboards, no software interfaces"
)


class MediaGenerationError(Exception):
    """A genuine, non-retryable failure in the media stage's own machinery
    (bad registry, missing key file at fail-closed points, tier-ceiling
    violation). Distinct from a provider-side refusal or transport failure,
    both of which are ordinary outcomes handled per-asset."""


# ---------------------------------------------------------------------------
# Model registry (§5.2).
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ModelRoute:
    route_id: str
    tier: str
    display: str
    model_string: str
    price_credits: float
    price_usd: float


@dataclass(frozen=True)
class ModelRegistry:
    registry_version: int
    price_snapshot_date: str
    credit_usd: float
    create_task_url: str
    record_info_url: str
    routes: dict[str, ModelRoute]
    draft_route_id: str
    fallback_draft_route_id: str
    tier_ceiling: str
    people_free_composition: bool
    policy_a_no_product_depiction: bool

    @property
    def draft_route(self) -> ModelRoute:
        return self.routes[self.draft_route_id]

    @property
    def fallback_draft_route(self) -> ModelRoute:
        return self.routes[self.fallback_draft_route_id]


def load_model_registry(path: Path) -> ModelRegistry:
    """Load ``config/model_registry.yaml``, fail-closed (§11.3 discipline:
    a media stage cannot route anything without knowing the roster)."""
    data = load_yaml_config(Path(path), name="model_registry.yaml")
    meta = data.get("meta") or {}
    routes_block = data.get("routes") or []
    if not routes_block:
        raise ConfigError(f"malformed config item: model_registry.yaml ({path}): 'routes' must be non-empty")
    routes: dict[str, ModelRoute] = {}
    for entry in routes_block:
        route = ModelRoute(
            route_id=str(entry["route_id"]),
            tier=str(entry["tier"]),
            display=str(entry.get("display", "")),
            model_string=str(entry["model_string"]),
            price_credits=float(entry["price_credits"]),
            price_usd=float(entry["price_usd"]),
        )
        routes[route.route_id] = route
    defaults = data.get("defaults") or {}
    draft_route_id = str(defaults.get("draft_route", ""))
    if draft_route_id not in routes:
        raise ConfigError(
            f"malformed config item: model_registry.yaml ({path}): "
            f"defaults.draft_route {draft_route_id!r} is not a registered route"
        )
    return ModelRegistry(
        registry_version=int(meta.get("registry_version", 1)),
        price_snapshot_date=str(meta.get("price_snapshot_date", "")),
        credit_usd=float(meta.get("credit_usd", 0.005)),
        create_task_url=str(meta.get("create_task_url", "https://api.kie.ai/api/v1/jobs/createTask")),
        record_info_url=str(meta.get("record_info_url", "https://api.kie.ai/api/v1/jobs/recordInfo")),
        routes=routes,
        draft_route_id=draft_route_id,
        fallback_draft_route_id=str(defaults.get("fallback_draft_route", draft_route_id)),
        tier_ceiling=str(defaults.get("tier_ceiling", "draft")),
        people_free_composition=bool(defaults.get("people_free_composition", True)),
        policy_a_no_product_depiction=bool(defaults.get("policy_a_no_product_depiction", True)),
    )


# ---------------------------------------------------------------------------
# Prompt composition.
# ---------------------------------------------------------------------------


def compose_prompt(image_brief: str, registry: ModelRegistry) -> str:
    """Compose the final image prompt from a copy asset's ``image_brief``
    plus the injected, non-configurable constraints (§5.3 routing contract's
    negative-prompt layer; people-free default R2-M18; Policy A). The
    brief's headline is never included here -- it is overlay-for-later, not
    part of the image (GOAL_ROADMAP.md M4 scope note)."""
    constraints = [_NEGATIVE_CONSTRAINTS]
    if not registry.people_free_composition:  # pragma: no cover - v1 default is always True
        constraints = [c for c in constraints if "no people" not in c]
    return f"{image_brief.strip()} Constraints: {'; '.join(constraints)}."


def prompt_sha256(prompt: str) -> str:
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Kie API client.
# ---------------------------------------------------------------------------


class KieTransportError(Exception):
    """The HTTP call itself failed to complete (network error, timeout) --
    the genuinely ambiguous case: we do not know whether the provider
    received the request. Distinct from :class:`KieApiError`, a clean
    response that names a definite failure."""


class KieApiError(Exception):
    """A clean HTTP response reporting a definite, non-ambiguous failure
    (non-200 ``code``, or a JSON body that will not parse)."""


@dataclass
class CreateTaskResult:
    task_id: str
    raw: dict[str, Any]


@dataclass
class RecordInfoResult:
    task_id: str
    state: str
    model: str | None
    result_urls: list[str]
    fail_code: str | None
    fail_msg: str | None
    credits_consumed: float | None
    raw: dict[str, Any]

    @property
    def is_success(self) -> bool:
        return self.state == "success"

    @property
    def is_failure(self) -> bool:
        return self.state == "fail"

    @property
    def is_terminal(self) -> bool:
        return self.is_success or self.is_failure


class KieClient:
    """Thin wrapper over the two-endpoint Kie jobs API plus the credit
    balance read, all traced per RUN_TRACE_SPEC.md with allowlist redaction.
    The API key is read once by the caller and passed in; it is used only
    to build the ``Authorization`` header for the raw HTTP call, which is
    never part of the traced ``request`` dict (same discipline as
    ``collectors/virlo.py``)."""

    def __init__(
        self, *, fetcher: Fetcher, api_key: str, trace: TraceWriter, registry: ModelRegistry, stage: str = "media"
    ) -> None:
        self.fetcher = fetcher
        self._api_key = api_key
        self.trace = trace
        self.registry = registry
        self.stage = stage

    def _headers(self, *, json_body: bool) -> dict[str, str]:
        headers = {"Authorization": f"Bearer {self._api_key}"}
        if json_body:
            headers["Content-Type"] = "application/json"
        return headers

    def create_task(self, *, model: str, input_: dict[str, Any], purpose: str) -> CreateTaskResult:
        body_dict = {"model": model, "input": input_}
        body = json.dumps(body_dict).encode("utf-8")
        prompt = str(input_.get("prompt", ""))
        call_seq = self.trace.api_call(
            self.stage,
            platform="kie",
            endpoint=self.registry.create_task_url,
            method="POST",
            request={
                "model": model,
                "input_keys": sorted(input_.keys()),
                "prompt_sha256": prompt_sha256(prompt),
                "prompt_len": len(prompt),
                "output_format": input_.get("output_format"),
                "aspect_ratio": input_.get("aspect_ratio"),
            },
            allowed_keys=CREATE_TASK_ALLOWED_KEYS,
            attempt=1,
            purpose=purpose,
        )
        try:
            response = self.fetcher.fetch(
                self.registry.create_task_url, headers=self._headers(json_body=True), method="POST", body=body
            )
        except FetchError as exc:
            self.trace.api_response(
                self.stage, seq_of_call=call_seq, status="error", latency_ms=0, bytes_=None,
                ids_returned=None, cost=None, outcome_class="transient",
                response_summary={"error": str(exc)}, allowed_keys={"error"},
            )
            raise KieTransportError(str(exc)) from exc

        try:
            payload = json.loads(response.body)
        except (json.JSONDecodeError, TypeError) as exc:
            self.trace.api_response(
                self.stage, seq_of_call=call_seq, status=response.status, latency_ms=response.latency_ms,
                bytes_=len(response.body), ids_returned=None, cost=None, outcome_class="permanent-endpoint",
                response_summary={"error": "malformed JSON"}, allowed_keys={"error"},
            )
            raise KieApiError(f"createTask: malformed JSON response: {exc}") from exc

        code = payload.get("code")
        outcome_class = "ok" if code == 200 else "permanent-endpoint"
        task_id = ((payload.get("data") or {}).get("taskId")) if isinstance(payload.get("data"), dict) else None
        self.trace.api_response(
            self.stage, seq_of_call=call_seq, status=response.status, latency_ms=response.latency_ms,
            bytes_=len(response.body), ids_returned=[task_id] if task_id else [],
            cost=None, outcome_class=outcome_class,
            response_summary={"code": code, "msg": payload.get("msg"), "taskId": task_id},
            allowed_keys=RESPONSE_ALLOWED_KEYS,
        )
        if code != 200 or not task_id:
            raise KieApiError(f"createTask failed: code={code} msg={payload.get('msg')}")
        return CreateTaskResult(task_id=task_id, raw=payload)

    def record_info(self, task_id: str, *, purpose: str) -> RecordInfoResult:
        url = f"{self.registry.record_info_url}?taskId={task_id}"
        call_seq = self.trace.api_call(
            self.stage, platform="kie", endpoint=self.registry.record_info_url, method="GET",
            request={"taskId": task_id}, allowed_keys=RECORD_INFO_ALLOWED_KEYS, attempt=1, purpose=purpose,
        )
        try:
            response = self.fetcher.fetch(url, headers=self._headers(json_body=False), method="GET")
        except FetchError as exc:
            self.trace.api_response(
                self.stage, seq_of_call=call_seq, status="error", latency_ms=0, bytes_=None,
                ids_returned=None, cost=None, outcome_class="transient",
                response_summary={"error": str(exc)}, allowed_keys={"error"},
            )
            raise KieTransportError(str(exc)) from exc

        try:
            payload = json.loads(response.body)
        except (json.JSONDecodeError, TypeError) as exc:
            self.trace.api_response(
                self.stage, seq_of_call=call_seq, status=response.status, latency_ms=response.latency_ms,
                bytes_=len(response.body), ids_returned=None, cost=None, outcome_class="permanent-endpoint",
                response_summary={"error": "malformed JSON"}, allowed_keys={"error"},
            )
            raise KieApiError(f"recordInfo: malformed JSON response: {exc}") from exc

        code = payload.get("code")
        data = payload.get("data") if isinstance(payload.get("data"), dict) else {}
        state = str(data.get("state", "unknown"))
        outcome_class = "ok" if code == 200 else "permanent-endpoint"
        self.trace.api_response(
            self.stage, seq_of_call=call_seq, status=response.status, latency_ms=response.latency_ms,
            bytes_=len(response.body), ids_returned=[task_id], cost={"credits": data.get("creditsConsumed")},
            outcome_class=outcome_class,
            response_summary={
                "code": code, "state": state, "model": data.get("model"),
                "failCode": data.get("failCode"), "failMsg": data.get("failMsg"),
                "progress": data.get("progress"), "creditsConsumed": data.get("creditsConsumed"),
            },
            allowed_keys=RESPONSE_ALLOWED_KEYS,
        )
        if code != 200:
            raise KieApiError(f"recordInfo failed: code={code} msg={payload.get('msg')}")

        result_json_raw = data.get("resultJson") or "{}"
        try:
            result_json = json.loads(result_json_raw) if isinstance(result_json_raw, str) else (result_json_raw or {})
        except json.JSONDecodeError:
            result_json = {}
        return RecordInfoResult(
            task_id=str(data.get("taskId", task_id)),
            state=state,
            model=data.get("model"),
            result_urls=list(result_json.get("resultUrls") or []),
            fail_code=data.get("failCode") or None,
            fail_msg=data.get("failMsg") or None,
            credits_consumed=data.get("creditsConsumed"),
            raw=payload,
        )

    def get_credit_balance(self, *, purpose: str) -> float | None:
        """GET the account's current credit balance. Returns ``None`` (never
        raises) on any failure -- balance reconciliation is best-effort and
        its absence degrades gracefully (§8.13's reconciliation still runs
        on whatever side it has)."""
        url = "https://api.kie.ai/api/v1/chat/credit"
        call_seq = self.trace.api_call(
            self.stage, platform="kie", endpoint=url, method="GET",
            request={}, allowed_keys=set(), attempt=1, purpose=purpose,
        )
        try:
            response = self.fetcher.fetch(url, headers=self._headers(json_body=False), method="GET")
            payload = json.loads(response.body)
        except (FetchError, json.JSONDecodeError, TypeError) as exc:
            self.trace.api_response(
                self.stage, seq_of_call=call_seq, status="error", latency_ms=0, bytes_=None,
                ids_returned=None, cost=None, outcome_class="transient",
                response_summary={"error": str(exc)}, allowed_keys={"error"},
            )
            return None
        code = payload.get("code")
        balance = payload.get("data")
        self.trace.api_response(
            self.stage, seq_of_call=call_seq, status=response.status, latency_ms=response.latency_ms,
            bytes_=len(response.body), ids_returned=None, cost=None,
            outcome_class="ok" if code == 200 else "permanent-endpoint",
            response_summary={"code": code, "balance": balance}, allowed_keys={"code", "balance"},
        )
        if code != 200 or not isinstance(balance, (int, float)):
            return None
        return float(balance)


# ---------------------------------------------------------------------------
# Download + re-host (§5.5).
# ---------------------------------------------------------------------------

_PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
_JPEG_MAGIC = b"\xff\xd8\xff"
_WEBP_MAGIC = b"RIFF"


def _looks_like_image(data: bytes) -> bool:
    return bool(data) and (
        data.startswith(_PNG_MAGIC) or data.startswith(_JPEG_MAGIC) or data.startswith(_WEBP_MAGIC)
    )


@dataclass
class DownloadResult:
    ok: bool
    checksum_sha256: str | None
    bytes_: int
    reason: str | None = None


def download_and_checksum(fetcher: Fetcher, url: str, dest_path: Path) -> DownloadResult:
    """Download one result image and verify it before it is ever marked
    complete (§5.5: "a truncated download is never marked done"). Never
    writes the provider URL anywhere on disk or in the trace -- the caller
    passes it in and it dies with this call frame."""
    try:
        response = fetcher.fetch(url, method="GET")
    except FetchError as exc:
        return DownloadResult(ok=False, checksum_sha256=None, bytes_=0, reason=f"download transport error: {exc}")
    body = response.body
    if not _looks_like_image(body):
        return DownloadResult(
            ok=False, checksum_sha256=None, bytes_=len(body or b""),
            reason="truncated or non-image payload (bad magic bytes)",
        )
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    dest_path.write_bytes(body)
    checksum = hashlib.sha256(body).hexdigest()
    return DownloadResult(ok=True, checksum_sha256=checksum, bytes_=len(body))


# ---------------------------------------------------------------------------
# §5.6 three-state delivered-route inference.
# ---------------------------------------------------------------------------

IDENTITY_REPORTED = "identity-reported"
SUBSTITUTED_UNKNOWN = "substituted — identity unknown"
ASSUMED_AS_REQUESTED = "assumed-as-requested"


def infer_delivered_route_state(
    *,
    requested_model: str,
    reported_model: str | None,
    requested_aspect: str | None = None,
    reported_aspect: str | None = None,
) -> tuple[str, str | None]:
    """§5.6's three-state rule. Returns ``(state, working_identity)``.

    The reported ``model`` field is used as a real identity signal only
    when it *diverges* from what was requested -- a field that always
    echoes the request tells us nothing we did not already know, and
    trusting it as confirmation would make ``identity-reported`` meaningless
    (see model_registry.yaml's verification note: the one real round trip
    performed for this route echoed the request, which is not evidence
    either way). Any other divergence (a different aspect delivered than
    requested) is the "side-effect signature" §5.6 says is the *actual*
    evidence for a silent substitution, without an identity attached.
    """
    if reported_model and reported_model != requested_model:
        return IDENTITY_REPORTED, reported_model
    divergence = (
        requested_aspect is not None and reported_aspect is not None and requested_aspect != reported_aspect
    )
    if divergence:
        return SUBSTITUTED_UNKNOWN, None
    return ASSUMED_AS_REQUESTED, requested_model


# ---------------------------------------------------------------------------
# Cost gate (§8.11).
# ---------------------------------------------------------------------------

STATUS_COUNT_CAPPED = "not generated — count capped"
STATUS_BUDGET_CAPPED = "not generated — budget capped"


@dataclass
class CapDecision:
    allowed: bool
    status: str | None


def check_caps(
    *,
    count_so_far: int,
    usd_so_far_run: float,
    usd_so_far_day: float,
    expected_cost_usd: float,
    count_cap: int,
    run_usd_cap: float,
    day_usd_cap: float,
) -> CapDecision:
    """Both caps are checked at every submission; whichever trips first
    stops that submission, and both outcomes are distinct, named statuses
    (§8.11). Count is checked first only because it is the cheaper knob to
    reason about -- when both trip simultaneously the count-capped status is
    reported, which is a deterministic tie-break, not a precedence claim."""
    if count_so_far >= count_cap:
        return CapDecision(False, STATUS_COUNT_CAPPED)
    if usd_so_far_run + expected_cost_usd > run_usd_cap:
        return CapDecision(False, STATUS_BUDGET_CAPPED)
    if usd_so_far_day + expected_cost_usd > day_usd_cap:
        return CapDecision(False, STATUS_BUDGET_CAPPED)
    return CapDecision(True, None)


# ---------------------------------------------------------------------------
# Per-asset plan + status.
# ---------------------------------------------------------------------------


@dataclass
class MediaAssetPlan:
    asset_id: str
    cluster_key: str
    destination: str
    language: str
    copy_status: str
    image_brief: str | None


def plan_media_assets(copy_asset_statuses: list[Any], *, language: str = "en") -> list[MediaAssetPlan]:
    """Build one media plan entry per copy asset (§4.6: "plan-only is
    always produced"). ``copy_asset_statuses`` is a list of
    ``copy_gen.AssetCopyStatus`` -- typed as ``Any`` here to avoid a
    circular import; only the four attributes below are read."""
    plans: list[MediaAssetPlan] = []
    for status in copy_asset_statuses:
        plans.append(
            MediaAssetPlan(
                asset_id=status.asset_id,
                cluster_key=status.cluster_key,
                destination=status.destination,
                language=language,
                copy_status=status.status,
                image_brief=status.image_brief if status.status == "gated-pass" else None,
            )
        )
    return plans


@dataclass
class MediaAssetStatus:
    asset_id: str
    cluster_key: str
    destination: str
    status: str
    route_id: str | None = None
    model_string: str | None = None
    expected_cost_usd: float | None = None
    observed_cost_usd: float | None = None
    delivered_route_state: str | None = None
    image_path: str | None = None
    task_id: str | None = None
    reason: str | None = None


@dataclass
class MediaStageResult:
    statuses: list[MediaAssetStatus] = field(default_factory=list)
    circuit_breaker_tripped: bool = False
    balance_before: float | None = None
    balance_after: float | None = None
    pending_count: int = 0
    submitted_unknown_count: int = 0
    total_spent_usd: float = 0.0
    total_expected_usd: float = 0.0


# ---------------------------------------------------------------------------
# The orchestrator.
# ---------------------------------------------------------------------------


class MediaGenerator:
    """Owns one media stage invocation: phase-0 resolution of prior
    unresolved intents, then the cost-gated submit/poll/download loop for
    this run's planned assets."""

    def __init__(
        self,
        *,
        store: Store,
        trace: TraceWriter,
        registry: ModelRegistry,
        media_config: MediaConfig,
        kie_client: KieClient,
        theme: str,
        run_id: str,
        run_date: str,
        pack_media_dir: Path,
        sleep_fn: Any = time.sleep,
        now_fn: Any = lambda: datetime.now().astimezone(),
        stage: str = "media",
    ) -> None:
        self.store = store
        self.trace = trace
        self.registry = registry
        self.config = media_config
        self.kie = kie_client
        self.theme = theme
        self.run_id = run_id
        self.run_date = run_date
        self.pack_media_dir = pack_media_dir
        self._sleep = sleep_fn
        self._now = now_fn
        self.stage = stage

    # -- phase 0: adopt pending jobs, resolve unresolved intents ----------

    def resolve_pending(self) -> None:
        """Run at the start of every media stage invocation, before any new
        submission (§4.7, §8.13 phase 0). Never resubmits blind."""
        for row in self.store.unresolved_media_intents(self.theme):
            self._resolve_one_row(row)

    def _resolve_one_row(self, row: MediaIntentRow) -> None:
        if row.task_id is None:
            # Sub-case A (§8.5): crash before the task id was ever written.
            # Unreachable by query -- there is nothing to resolve it with.
            self.store.update_media_intent(row.id, state="submitted-unknown", submitted_unknown_subcase="A")
            self.trace.decision(
                self.stage,
                decision=(
                    f"media intent {row.cluster_key}/{row.asset_slot} has no task id (crash before "
                    "submission response) -- submitted-unknown, sub-case A, never auto-resubmitted"
                ),
                rule="ARCHITECTURE_PLAN §8.5/§8.13: no task id means the status endpoint is unreachable by query",
            )
            return None
        try:
            info = self.kie.record_info(row.task_id, purpose="phase-0 resolution of a prior unresolved media job")
        except (KieTransportError, KieApiError) as exc:
            self.store.update_media_intent(row.id, state="submitted-unknown", submitted_unknown_subcase="B")
            self.trace.decision(
                self.stage,
                decision=(
                    f"media intent {row.cluster_key}/{row.asset_slot} (task {row.task_id}) could not be "
                    f"resolved by query ({exc}) -- submitted-unknown, sub-case B"
                ),
                rule="ARCHITECTURE_PLAN §8.13: an unresolvable resolve-by-query on a known task id",
            )
            return None
        if info.is_success:
            self._complete_success(row, info)
            return
        if info.is_failure:
            self._complete_failure(row, info)
            return None
        # Still pending -- leave it polling; a later run (or this run's own
        # poll loop, if it belongs to this run) will pick it up again.
        return None

    # -- cost gate + submission loop ----------------------------------------

    def process(self, plans: list[MediaAssetPlan]) -> MediaStageResult:
        result = MediaStageResult()
        self.resolve_pending()

        spent_usd_run = 0.0
        count_run = 0
        circuit_tripped = False
        ledger_recorded_usd = 0.0
        balance_fetched = False

        route = self.registry.draft_route
        if self.registry.tier_ceiling != "draft":
            raise MediaGenerationError(
                f"tier_ceiling {self.registry.tier_ceiling!r} exceeds this goal's draft-only policy — policy-stop"
            )
        if route.tier != "draft":
            raise MediaGenerationError(f"draft_route {route.route_id!r} is not tier=draft — policy-stop")

        for plan in plans:
            if plan.copy_status != "gated-pass":
                status_text = (
                    "awaiting copy — not submitted"
                    if plan.copy_status.startswith("held")
                    else "not generated — copy blocked (no approved brief)"
                )
                result.statuses.append(
                    MediaAssetStatus(
                        asset_id=plan.asset_id, cluster_key=plan.cluster_key, destination=plan.destination,
                        status=status_text,
                    )
                )
                continue

            if circuit_tripped:
                result.statuses.append(
                    MediaAssetStatus(
                        asset_id=plan.asset_id, cluster_key=plan.cluster_key, destination=plan.destination,
                        status="not generated — unexplained-spend circuit breaker",
                    )
                )
                continue

            if self.config.dry_run:
                result.statuses.append(
                    MediaAssetStatus(
                        asset_id=plan.asset_id, cluster_key=plan.cluster_key, destination=plan.destination,
                        status="plan-only — dry run", route_id=route.route_id, model_string=route.model_string,
                        expected_cost_usd=route.price_usd,
                    )
                )
                continue

            # An existing (identity, attempt) row means a submission was
            # already attempted -- possibly in a prior invocation of this
            # same run_id, possibly moments ago in this very call. Resolve
            # it in place; this is NEVER a new submission, so it is exempt
            # from caps, cap accounting and the circuit breaker (no new
            # money can move here -- see §8.5's uniqueness rule).
            identity_kwargs = dict(
                theme=self.theme, run_date=self.run_date, cluster_key=plan.cluster_key,
                asset_slot=plan.destination, language=plan.language,
                prompt_pattern_version=PROMPT_PATTERN_VERSION, attempt=1,
            )
            existing = self.store.find_media_intent(**identity_kwargs)
            if existing is not None:
                if not existing.terminal:
                    self._resolve_one_row(existing)
                refreshed = self.store.get_media_intent(existing.id)
                result.statuses.append(self._status_from_row(plan, refreshed or existing))
                continue

            day_spend = self.store.media_spend_usd_for_day(theme=self.theme, run_date=self.run_date)
            decision = check_caps(
                count_so_far=count_run, usd_so_far_run=spent_usd_run, usd_so_far_day=day_spend,
                expected_cost_usd=route.price_usd, count_cap=self.config.per_run_count_cap,
                run_usd_cap=self.config.per_run_usd_cap, day_usd_cap=self.config.per_day_usd_cap,
            )
            if not decision.allowed:
                self.trace.decision(
                    self.stage,
                    decision=f"asset {plan.asset_id}: {decision.status}",
                    rule="ARCHITECTURE_PLAN §8.11: both caps checked at every submission, whichever trips first stops it",
                )
                result.statuses.append(
                    MediaAssetStatus(
                        asset_id=plan.asset_id, cluster_key=plan.cluster_key, destination=plan.destination,
                        status=decision.status, route_id=route.route_id, expected_cost_usd=route.price_usd,
                    )
                )
                continue

            if not balance_fetched:
                result.balance_before = self.kie.get_credit_balance(purpose="pre-submission balance snapshot")
                balance_fetched = True

            asset_status = self._submit_new(plan, route, identity_kwargs)
            result.statuses.append(asset_status)
            # Every branch below is reached only for a genuinely NEW
            # submission attempt this call (a createTask call was actually
            # made) -- the no-submission outcomes (awaiting-copy, capped,
            # dry-run, circuit-breaker-skip, already-exists) are handled by
            # the ``continue``s above.
            count_run += 1
            if asset_status.status == "generated":
                spent_usd_run += asset_status.observed_cost_usd or route.price_usd
                ledger_recorded_usd += asset_status.observed_cost_usd or route.price_usd
            elif asset_status.status in ("pending — adopted by a later run", "submitted-unknown"):
                spent_usd_run += route.price_usd
                ledger_recorded_usd += route.price_usd
                if asset_status.status == "pending — adopted by a later run":
                    result.pending_count += 1
                else:
                    result.submitted_unknown_count += 1
            # A definite provider-reported failure is not charged per Kie's
            # documentation (§5.6); nothing added to spend for "failed — *".

            circuit_tripped = self._check_circuit_breaker(result, ledger_recorded_usd)

        result.total_spent_usd = spent_usd_run
        result.total_expected_usd = sum(s.expected_cost_usd or 0.0 for s in result.statuses)
        result.circuit_breaker_tripped = circuit_tripped
        return result

    def _check_circuit_breaker(self, result: MediaStageResult, ledger_recorded_usd: float) -> bool:
        balance_now = self.kie.get_credit_balance(purpose="post-submission balance reconciliation")
        result.balance_after = balance_now
        if result.balance_before is None or balance_now is None:
            return False
        delta_credits = result.balance_before - balance_now
        delta_usd = delta_credits * self.registry.credit_usd
        denom = max(ledger_recorded_usd, 0.01)
        relative_divergence = abs(delta_usd - ledger_recorded_usd) / denom
        self.trace.spend(
            self.stage, wallet="media", expected=ledger_recorded_usd, ledger_recorded=ledger_recorded_usd,
            balance_delta=delta_usd,
        )
        if relative_divergence > self.config.unexplained_spend_threshold:
            self.trace.degrade(
                self.stage,
                condition=(
                    f"unexplained-spend: ledger recorded ${ledger_recorded_usd:.4f}, observed balance delta "
                    f"${delta_usd:.4f} ({relative_divergence:.0%} divergence) — halting new submissions"
                ),
                caused="W2-02 circuit breaker (simplified): no new media submissions for the remainder of this run",
            )
            return True
        return False

    def _submit_new(self, plan: MediaAssetPlan, route: ModelRoute, identity_kwargs: dict[str, Any]) -> MediaAssetStatus:
        """Commit the write-ahead intent row and submit -- called only when
        ``process()`` has confirmed no (identity, attempt) row already
        exists. The row is committed BEFORE ``createTask`` is called (§8.5);
        :class:`MediaIntentAlreadyExists` is still handled defensively below
        in case of a race between the existence check and this insert."""
        assert plan.image_brief is not None
        prompt = compose_prompt(plan.image_brief, self.registry)
        try:
            row = self.store.insert_media_intent(
                run_id=self.run_id, route_id=route.route_id, model_string=route.model_string,
                requested_aspect=self.config.aspect_ratio, requested_output_format=self.config.output_format,
                prompt_sha256=prompt_sha256(prompt), prompt_full=prompt, expected_cost_credits=route.price_credits,
                expected_cost_usd=route.price_usd, **identity_kwargs,
            )
        except MediaIntentAlreadyExists:
            existing2 = self.store.find_media_intent(**identity_kwargs)
            assert existing2 is not None
            return self._status_from_row(plan, existing2)

        try:
            created = self.kie.create_task(
                model=route.model_string,
                input_={"prompt": prompt, "output_format": self.config.output_format, "aspect_ratio": self.config.aspect_ratio},
                purpose=f"draft-tier image generation for {plan.cluster_key}/{plan.destination}",
            )
        except KieTransportError as exc:
            # Sub-case A candidate: we truly do not know if the provider
            # received this. No task id was ever obtained.
            self.store.update_media_intent(row.id, state="submitted-unknown", submitted_unknown_subcase="A")
            self.trace.decision(
                self.stage,
                decision=f"createTask transport failure for {plan.asset_id}: {exc} -- submitted-unknown, sub-case A",
                rule="ARCHITECTURE_PLAN §8.5: money may have moved; no task id means unreachable by query",
            )
            return MediaAssetStatus(
                asset_id=plan.asset_id, cluster_key=plan.cluster_key, destination=plan.destination,
                status="submitted-unknown", route_id=route.route_id, model_string=route.model_string,
                expected_cost_usd=route.price_usd, reason=str(exc),
            )
        except KieApiError as exc:
            # A clean, definite rejection before any task existed -- not
            # ambiguous, not charged, terminal.
            self.store.update_media_intent(row.id, state="failed", fail_reason=str(exc), terminal=True, resolved_at=self._now())
            return MediaAssetStatus(
                asset_id=plan.asset_id, cluster_key=plan.cluster_key, destination=plan.destination,
                status="failed — createTask rejected", route_id=route.route_id, model_string=route.model_string,
                expected_cost_usd=route.price_usd, reason=str(exc),
            )

        self.store.set_media_task_id(row.id, created.task_id)
        return self._poll_to_resolution(plan, route, row.id, created.task_id)

    def _poll_to_resolution(self, plan: MediaAssetPlan, route: ModelRoute, row_id: int, task_id: str) -> MediaAssetStatus:
        deadline = self.config.poll_timeout_seconds
        elapsed = 0.0
        while True:
            try:
                info = self.kie.record_info(task_id, purpose=f"poll job status for {plan.asset_id}")
            except (KieTransportError, KieApiError):
                self.store.update_media_intent(row_id, state="submitted-unknown", submitted_unknown_subcase="B")
                return MediaAssetStatus(
                    asset_id=plan.asset_id, cluster_key=plan.cluster_key, destination=plan.destination,
                    status="submitted-unknown", route_id=route.route_id, model_string=route.model_string,
                    expected_cost_usd=route.price_usd, task_id=task_id,
                )
            if info.is_success:
                row = self.store.get_media_intent(row_id)
                assert row is not None
                self._complete_success(row, info)
                refreshed = self.store.get_media_intent(row_id)
                return self._status_from_row(plan, refreshed)
            if info.is_failure:
                row = self.store.get_media_intent(row_id)
                assert row is not None
                self._complete_failure(row, info)
                return MediaAssetStatus(
                    asset_id=plan.asset_id, cluster_key=plan.cluster_key, destination=plan.destination,
                    status="failed — provider refused" if _looks_like_refusal(info) else "failed — provider error",
                    route_id=route.route_id, model_string=route.model_string, task_id=task_id,
                    reason=info.fail_msg or info.fail_code,
                )
            if elapsed >= deadline:
                self.trace.degrade(
                    self.stage,
                    condition=f"asset {plan.asset_id} still pending at poll timeout ({deadline}s)",
                    caused="§8.13: job stays 'polling', adopted by a later run's phase-0 resolution",
                )
                return MediaAssetStatus(
                    asset_id=plan.asset_id, cluster_key=plan.cluster_key, destination=plan.destination,
                    status="pending — adopted by a later run", route_id=route.route_id,
                    model_string=route.model_string, expected_cost_usd=route.price_usd, task_id=task_id,
                )
            self._sleep(self.config.poll_interval_seconds)
            elapsed += self.config.poll_interval_seconds

    def _complete_success(self, row: MediaIntentRow, info: RecordInfoResult) -> None:
        if not info.result_urls:
            self.store.update_media_intent(
                row.id, state="failed", fail_reason="success state with no resultUrls", terminal=True,
                resolved_at=self._now(),
            )
            return None
        dest_path = self.pack_media_dir / f"{row.cluster_key}_{row.asset_slot}.{self.config.output_format}"
        outcome = download_and_checksum(self.kie.fetcher, info.result_urls[0], dest_path)
        if not outcome.ok:
            # Retry once (§5.5: a truncated download is never marked done).
            outcome = download_and_checksum(self.kie.fetcher, info.result_urls[0], dest_path)
        if not outcome.ok:
            self.store.update_media_intent(
                row.id, state="failed", fail_reason=f"download failed: {outcome.reason}", terminal=True,
                resolved_at=self._now(),
            )
            self.trace.decision(
                self.stage,
                decision=f"asset {row.cluster_key}/{row.asset_slot}: download never completed ({outcome.reason})",
                rule="ARCHITECTURE_PLAN §5.5: a truncated download is never marked complete",
            )
            return None

        delivered_state, delivered_model = infer_delivered_route_state(
            requested_model=row.model_string, reported_model=info.model,
        )
        observed_usd = (info.credits_consumed * self.registry.credit_usd) if info.credits_consumed else row.expected_cost_usd
        self.store.update_media_intent(
            row.id, state="done", delivered_route_state=delivered_state, delivered_model=delivered_model,
            observed_cost_credits=info.credits_consumed, observed_cost_usd=observed_usd,
            image_path=str(dest_path), checksum_sha256=outcome.checksum_sha256, terminal=True,
            resolved_at=self._now(),
        )
        _write_provenance_yaml(
            self.pack_media_dir, row=row, delivered_state=delivered_state, delivered_model=delivered_model,
            checksum=outcome.checksum_sha256, observed_cost_usd=observed_usd, image_path=dest_path,
            registry=self.registry, prompt_full=row.prompt_full,
        )
        return None

    def _complete_failure(self, row: MediaIntentRow, info: RecordInfoResult) -> None:
        self.store.update_media_intent(
            row.id, state="failed", fail_reason=info.fail_msg or info.fail_code or "provider reported failure",
            terminal=True, resolved_at=self._now(),
        )

    def _status_from_row(self, plan: MediaAssetPlan, row: MediaIntentRow | None) -> MediaAssetStatus:
        if row is None:
            return MediaAssetStatus(
                asset_id=plan.asset_id, cluster_key=plan.cluster_key, destination=plan.destination,
                status="submitted-unknown",
            )
        if row.state == "done":
            return MediaAssetStatus(
                asset_id=plan.asset_id, cluster_key=plan.cluster_key, destination=plan.destination,
                status="generated", route_id=row.route_id, model_string=row.model_string,
                expected_cost_usd=row.expected_cost_usd, observed_cost_usd=row.observed_cost_usd,
                delivered_route_state=row.delivered_route_state, image_path=row.image_path, task_id=row.task_id,
            )
        if row.state == "failed":
            return MediaAssetStatus(
                asset_id=plan.asset_id, cluster_key=plan.cluster_key, destination=plan.destination,
                status="failed — provider refused" if row.fail_reason and _refusal_text(row.fail_reason) else "failed — provider error",
                route_id=row.route_id, model_string=row.model_string, task_id=row.task_id, reason=row.fail_reason,
            )
        if row.state == "submitted-unknown":
            return MediaAssetStatus(
                asset_id=plan.asset_id, cluster_key=plan.cluster_key, destination=plan.destination,
                status="submitted-unknown", route_id=row.route_id, model_string=row.model_string,
                expected_cost_usd=row.expected_cost_usd, task_id=row.task_id,
            )
        # Still polling/intent -- treat as pending-adopted for display.
        return MediaAssetStatus(
            asset_id=plan.asset_id, cluster_key=plan.cluster_key, destination=plan.destination,
            status="pending — adopted by a later run", route_id=row.route_id, model_string=row.model_string,
            expected_cost_usd=row.expected_cost_usd, task_id=row.task_id,
        )


def _looks_like_refusal(info: RecordInfoResult) -> bool:
    text = f"{info.fail_code or ''} {info.fail_msg or ''}".lower()
    return any(term in text for term in ("polic", "content", "moderat", "refus", "reject", "safety"))


def _refusal_text(reason: str) -> bool:
    text = reason.lower()
    return any(term in text for term in ("polic", "content", "moderat", "refus", "reject", "safety"))


def _write_provenance_yaml(
    pack_media_dir: Path,
    *,
    row: MediaIntentRow,
    delivered_state: str,
    delivered_model: str | None,
    checksum: str | None,
    observed_cost_usd: float | None,
    image_path: Path,
    registry: ModelRegistry,
    prompt_full: str | None = None,
) -> None:
    """Per-asset provenance record (§5.6/§12.2), stored beside the image.
    Provider URLs are never written here or anywhere else in the pack.

    ``prompt_full`` (W8-8) is the complete, exact prompt sent to the image
    model -- own-authored content (the copy asset's ``image_brief`` plus the
    injected negative constraints from :func:`compose_prompt`), not
    third-party text, so unlike the trace's own redaction rule (sha256 +
    length only, RUN_TRACE_SPEC §3) it is safe and useful to keep in full
    here, beside the image it produced."""
    doc = {
        "asset_id": f"{row.cluster_key}_{row.asset_slot}",
        "cluster_key": row.cluster_key,
        "destination": row.asset_slot,
        "language": row.language,
        "requested_route": row.route_id,
        "requested_model": row.model_string,
        "delivered_route_state": delivered_state,
        "delivered_model": delivered_model,
        "price_snapshot_date": registry.price_snapshot_date,
        "task_id": row.task_id,
        "checksum_sha256": checksum,
        "observed_cost_usd": observed_cost_usd,
        "image_path": str(image_path),
        "prompt_pattern_version": row.prompt_pattern_version,
        "prompt_sha256": row.prompt_sha256,
        "prompt_full": prompt_full,
        "attempt": row.attempt,
        "created_at": row.created_at,
        "logo_overlay": "deferred to a later phase — this pack carries the raw generated image only",
    }
    provenance_path = pack_media_dir / f"{row.cluster_key}_{row.asset_slot}.provenance.yaml"
    provenance_path.write_text(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False), encoding="utf-8")
