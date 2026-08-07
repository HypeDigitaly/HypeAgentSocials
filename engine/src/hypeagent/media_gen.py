"""Kie.ai IMAGE generation (GOAL_ROADMAP.md M4/W8-9 Q4; ARCHITECTURE_PLAN.md
§4.6-§4.7, §5.2-§5.7, §8.5, §8.11, §8.13).

Scope: **images only** -- nothing publishes, no video, no voice, no FFmpeg
composition/overlay (the pack carries the raw generated image(s) plus their
briefs; logo overlay is a later phase). W8-9 Q4 raises the tier ceiling to
``standard`` (real, paid, standard-tier Nano Banana 2 generations for the
goal's finish-line test run) and wires per-slide carousel submission
alongside the single hero-image path.

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
- **N-E Vision-QA (W8-9 Q4)** runs only in the plan-aware fresh-submission
  path (``_submit_new`` -> ``_poll_to_resolution`` -> ``_complete_success``),
  where the crafted prompt's expected on-image text and archetype/register
  are known. A row adopted by ``resolve_pending``'s phase-0 pass (a prior
  process crashed after submitting but before this process ever built a
  plan) has no such context available and is provenance-recorded as
  ``qa: skipped-phase0-adoption`` rather than retroactively re-derived --
  named here rather than silently skipped.
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
from hypeagent.llm import LlmClient, LlmError, guess_image_mime, image_content_part, text_content_part
from hypeagent.store import MediaIntentAlreadyExists, MediaIntentRow, Store
from hypeagent.trace import TraceWriter

# W8-9 Q3c: bumped 1 -> 2. The hero-image path now prefers an N-D-crafted
# prompt (``promptcraft.craft_prompts``) over ``compose_prompt`` below when
# one is available -- a qualitatively different prompt-construction scheme
# (the old ``_NEGATIVE_CONSTRAINTS`` no-text/no-logo/no-people list is DEAD
# for the crafted path; the crafted prompt embeds gate-passed text to render
# VERBATIM, which the old scheme explicitly forbade). ``prompt_pattern_version``
# is part of a media intent's write-ahead identity tuple (``MediaGenerator.
# process``'s ``identity_kwargs``), so bumping it here means a resumed run
# reproducibly reuses the SAME scheme it started with rather than an
# in-place identity silently spanning two incompatible prompt styles.
PROMPT_PATTERN_VERSION = 2
ATTEMPT_MAX = 2

# W8-9 Q4: draft < standard, the only two tiers this registry names. Route
# selection checks ``TIER_ORDER[route.tier] <= TIER_ORDER[registry.tier_ceiling]``
# instead of the old two literal ``== "draft"`` hard-raises -- any route
# above the configured ceiling refuses with the same MediaGenerationError
# policy-stop class, regardless of which class (hero/slide) picked it.
TIER_ORDER = {"draft": 0, "standard": 1}

CREATE_TASK_ALLOWED_KEYS = {"model", "input_keys", "prompt_sha256", "prompt_len", "output_format", "aspect_ratio"}
RECORD_INFO_ALLOWED_KEYS = {"taskId"}
RESPONSE_ALLOWED_KEYS = {
    "bytes", "error", "code", "msg", "taskId", "state", "model", "failCode", "failMsg",
    "progress", "creditsConsumed", "result_url_count",
}

# Injected, non-configurable prompt constraints -- W8-9 Q4 replaces the old
# R2-M18/no-text/no-logo/Policy-A set entirely (not additively): text, logos
# of discussed third-party tools, generic people, and generic software UI
# are now ALLOWED. Only these three survive, because they are the ones this
# goal's operator actually cares about avoiding:
_NEGATIVE_CONSTRAINTS = (
    "no identifiable real individuals or celebrity likenesses; "
    "no NSFW or shocking content; "
    "nothing presented as a screenshot of HypeDigitaly's or HypeLead's own product UI"
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

    def resolve_route(self, route_id: str) -> ModelRoute:
        """Look up a route by id and enforce the tier-order policy-stop
        (W8-9 Q4): any route whose tier ranks above ``tier_ceiling`` in
        ``TIER_ORDER`` refuses here, replacing the two old literal
        ``== "draft"`` hard-raises with a genuine order comparison that
        works for any route/class combination, not just the single
        hard-coded draft route this used to be."""
        if route_id not in self.routes:
            raise MediaGenerationError(f"route_by_class names {route_id!r}, which is not a registered route")
        route = self.routes[route_id]
        route_rank = TIER_ORDER.get(route.tier)
        ceiling_rank = TIER_ORDER.get(self.tier_ceiling)
        if route_rank is None or ceiling_rank is None or route_rank > ceiling_rank:
            raise MediaGenerationError(
                f"route {route.route_id!r} tier {route.tier!r} exceeds tier_ceiling {self.tier_ceiling!r} — policy-stop"
            )
        return route


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


def compose_prompt(image_brief: str, registry: ModelRegistry) -> str:  # noqa: ARG001 - registry kept for call-site stability
    """Compose the final image prompt from a copy asset's ``image_brief``
    plus the injected, non-configurable W8-9 Q4 constraint set (§5.3 routing
    contract's negative-prompt layer). This is the fallback path only --
    used when no N-D-crafted prompt is available for this asset; a crafted
    prompt carries its own guardrails and is never run through here (no
    double-appending, module docstring).

    ``registry`` is accepted but no longer consulted for anything (W8-9 Q4
    deletes the old ``people_free_composition`` substring-filter mechanism
    outright -- it does not exist here to be re-triggered); the parameter
    stays so existing call sites do not need to change shape."""
    return f"{image_brief.strip()} Constraints: {_NEGATIVE_CONSTRAINTS}."


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
    """One image to (plan to) generate. W8-9 Q4: a gated-pass carousel copy
    asset now expands into one plan PER SLIDE (``asset_class="slide"``,
    ``slot="slide_01"``, ...) instead of the single representative plan
    every copy asset got before this milestone; a single-image destination
    (or any asset without a usable crafted slide set) still gets exactly one
    ``asset_class="hero"``, ``slot="hero"`` plan, unchanged in spirit from
    before."""

    asset_id: str
    cluster_key: str
    destination: str
    language: str
    copy_status: str
    asset_class: str = "hero"  # "hero" | "slide"
    slot: str = "hero"  # "hero" | "slide_01" | "slide_02" | ...
    image_brief: str | None = None
    # W8-9 Q3c/Q4: an N-D-crafted, gate-checked prompt for this exact slot,
    # when one is available and usable -- ``None`` falls back to
    # ``compose_prompt(image_brief, registry)`` (hero-class plans only;
    # there is no deterministic fallback composer for a carousel slide, so
    # a slide plan with no crafted prompt simply is not emitted, see
    # ``plan_media_assets``).
    crafted_prompt: str | None = None
    # W8-9 Q4 N-E vision-QA expectations, carried from the crafter's own
    # archetype/register pick and the copy asset's own text -- ``None``
    # whenever there is nothing crafted to verify (fallback/compose_prompt
    # path), which is this plan's own signal to skip QA rather than call an
    # LLM to check a constraint that was never asked for.
    qa_expected_text: str | None = None
    qa_archetype: str | None = None
    qa_register: str | None = None

    @property
    def asset_slot(self) -> str:
        """The media-intent ledger identity's ``asset_slot`` component
        (§8.5) -- exactly ``destination`` for a hero (unchanged from before
        this milestone, so existing hero ledger rows keep resolving), or
        ``"<destination>:<slot>"`` for a carousel slide (new, additive)."""
        return self.destination if self.asset_class == "hero" else f"{self.destination}:{self.slot}"


def _slide_text(slide: dict[str, str]) -> str:
    title = str(slide.get("title") or "").strip()
    body = str(slide.get("body") or "").strip()
    return " — ".join(part for part in (title, body) if part)


def plan_media_assets(
    copy_asset_statuses: list[Any], *, language: str = "en", crafted_prompts: dict[str, Any] | None = None
) -> list[MediaAssetPlan]:
    """Build media plan entries per copy asset (§4.6: "plan-only is always
    produced"). ``copy_asset_statuses`` is a list of
    ``copy_gen.AssetCopyStatus`` -- typed as ``Any`` here to avoid a
    circular import; only the attributes read below are used.

    ``crafted_prompts`` (W8-9 Q3c/Q4) maps ``asset_id`` -> a
    ``promptcraft.CraftedPromptSet`` -- typed ``Any`` for the same
    circular-import reason. A usable set carrying one or more
    ``slide_NN``-slotted images expands into one plan per slide (W8-9 Q4);
    otherwise its ``.hero_prompt()`` (or ``None``) drives a single hero plan,
    exactly as before this milestone."""
    crafted_prompts = crafted_prompts or {}
    plans: list[MediaAssetPlan] = []
    for status in copy_asset_statuses:
        if status.status != "gated-pass":
            plans.append(
                MediaAssetPlan(
                    asset_id=status.asset_id, cluster_key=status.cluster_key, destination=status.destination,
                    language=language, copy_status=status.status,
                )
            )
            continue

        crafted = crafted_prompts.get(status.asset_id)
        usable = crafted is not None and crafted.usable()
        slide_images = [img for img in (crafted.images if usable else []) if img.slot.startswith("slide")]
        slides_by_number = {i + 1: s for i, s in enumerate(status.slides or [])}

        if slide_images:
            for index, image in enumerate(slide_images, start=1):
                slide = slides_by_number.get(index, {})
                plans.append(
                    MediaAssetPlan(
                        asset_id=status.asset_id, cluster_key=status.cluster_key, destination=status.destination,
                        language=language, copy_status=status.status, asset_class="slide", slot=image.slot,
                        image_brief=status.image_brief, crafted_prompt=image.prompt,
                        qa_expected_text=_slide_text(slide) or None,
                        qa_archetype=crafted.archetype if crafted is not None else None,
                        qa_register=crafted.register if crafted is not None else None,
                    )
                )
        else:
            hero_prompt = crafted.hero_prompt() if crafted is not None else None
            plans.append(
                MediaAssetPlan(
                    asset_id=status.asset_id, cluster_key=status.cluster_key, destination=status.destination,
                    language=language, copy_status=status.status, asset_class="hero", slot="hero",
                    image_brief=status.image_brief, crafted_prompt=hero_prompt,
                    qa_expected_text=(status.headline or None) if hero_prompt else None,
                    qa_archetype=crafted.archetype if (crafted is not None and hero_prompt) else None,
                    qa_register=crafted.register if (crafted is not None and hero_prompt) else None,
                )
            )
    return plans


@dataclass
class MediaAssetStatus:
    asset_id: str
    cluster_key: str
    destination: str
    status: str
    slot: str = "hero"
    route_id: str | None = None
    model_string: str | None = None
    expected_cost_usd: float | None = None
    observed_cost_usd: float | None = None
    delivered_route_state: str | None = None
    image_path: str | None = None
    task_id: str | None = None
    reason: str | None = None
    qa_verdict: str | None = None


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


@dataclass
class _RunAccounting:
    """Mutable per-``process()``-call accounting, shared by every attempt
    (including a QA-triggered attempt 2) for every plan this call. Exists
    only so :meth:`MediaGenerator._submit_or_resolve` can be one function
    called for BOTH attempt numbers, instead of duplicating the cap-check /
    spend-accounting / circuit-breaker block that used to live inline in
    ``process()`` once per plan."""

    spent_usd_run: float = 0.0
    count_run: int = 0
    ledger_recorded_usd: float = 0.0
    balance_fetched: bool = False
    circuit_tripped: bool = False
    # W8-9 (spend-report ×N inflation fix): the last credit balance actually
    # observed (starts as ``result.balance_before`` on the first
    # reconciliation) -- lets :meth:`MediaGenerator._check_circuit_breaker`
    # report the balance movement attributable to JUST the submission that
    # triggered this reconciliation, not the cumulative movement since the
    # run started (the previous behaviour, which made every ``spend`` trace
    # event repeat the running total instead of that submission's own
    # delta -- summing the events then inflated the reported run spend by a
    # multiple of the true total).
    last_balance: float | None = None


def _parse_asset_slot(asset_slot: str) -> tuple[str, str]:
    """Inverse of :meth:`MediaAssetPlan.asset_slot`: recover
    ``(destination, slot)`` from the ledger identity's own ``asset_slot``
    column. Used by the phase-0 path, which resolves a row with no
    ``MediaAssetPlan`` in hand at all -- the encoding has to be
    self-describing from the DB alone."""
    if ":" in asset_slot:
        destination, slot = asset_slot.split(":", 1)
        return destination, slot
    return asset_slot, "hero"


# ---------------------------------------------------------------------------
# N-E Vision-QA gate (W8-9 Q4).
# ---------------------------------------------------------------------------

QA_SYSTEM_PROMPT = (
    "You are the Vision-QA gate (N-E) for HypeDigitaly's AI-agency social content pipeline "
    "(FLOW_MAP.md's post-generation QA node). You are shown one generated image plus the exact "
    "text that was supposed to render on it, verbatim, and the visual archetype/register it was "
    "meant to match. Judge strictly but fairly: minor glyph-rendering artifacts (slightly rough "
    "letterforms, small kerning oddities) are fine, but you must be STRICT about the actual words.\n\n"
    "text_matches must be true ONLY if EVERY required string is rendered EXACTLY — word-for-word, "
    "in full, with no duplication (e.g. 'to follow-up to follow-up'), no omission, no garbling, and "
    "no invented/substituted words. If even one required string is missing, cut off, duplicated, or "
    "altered, text_matches MUST be false. Decorative or background text that is not one of the "
    "required strings (e.g. fake screenshot chrome, ambient UI-looking text in the background) may "
    "be noted in mismatches WITHOUT failing text_matches — but any prominent garbled foreground text "
    "at display size (an unreadable label, an invented word, nonsense characters standing in for "
    "real text) MUST still fail text_matches, even if it is not one of the required strings, because "
    "it is a visible defect a viewer would notice. Always list every mismatch you observe — required "
    "or decorative — in the structured mismatches list; do not silently pass an image with visible "
    "text defects. Respond with ONLY the JSON schema given."
)


@dataclass
class VisionQaResult:
    status: str  # "pass" | "fail" | "skipped"
    text_matches: bool | None = None
    archetype_ok: bool | None = None
    mismatches: list[str] = field(default_factory=list)
    notes: str | None = None
    skip_reason: str | None = None

    def to_yaml_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "text_matches": self.text_matches,
            "archetype_ok": self.archetype_ok,
            "mismatches": self.mismatches,
            "notes": self.notes,
            "skip_reason": self.skip_reason,
        }


def run_vision_qa(
    *,
    llm_client: LlmClient | None,
    image_bytes: bytes,
    mime: str,
    expected_text: str | None,
    archetype: str | None,
    register: str | None,
    node_name: str = "vision_qa",
    purpose: str = "",
    trace: TraceWriter | None = None,
    stage: str = "media",
    asset_id: str = "",
    regeneration_counter: int | None = None,
) -> VisionQaResult:
    """N-E: one vision-QA call per downloaded image. Never raises -- an
    unavailable/disabled LLM, an exhausted per-run LLM budget, a call
    failure, or simply nothing to verify (no crafted on-image text for this
    plan) all degrade to ``status="skipped"`` with the reason named
    (provenance's ``qa: skipped-<reason>``), which is explicitly NOT a QA
    failure and never triggers a regeneration."""
    if not expected_text:
        return VisionQaResult(status="skipped", skip_reason="no crafted on-image text to verify for this asset")
    if llm_client is None:
        return VisionQaResult(status="skipped", skip_reason="LLM disabled or unavailable for this run")
    calls_remaining, usd_remaining = llm_client.budget_remaining()
    if calls_remaining <= 0 or usd_remaining <= 0:
        return VisionQaResult(status="skipped", skip_reason="LLM budget exhausted for this run")

    schema_hint = 'Schema: {"text_matches": bool, "archetype_ok": bool, "mismatches": [string], "notes": string}'
    user_parts = [
        image_content_part(image_bytes, mime=mime),
        text_content_part(
            f"Exact text that must appear on this image: {expected_text!r}\n"
            f"Intended visual archetype: {archetype!r}\nIntended register: {register!r}"
        ),
    ]
    try:
        data = llm_client.call_json(
            node_name, system=QA_SYSTEM_PROMPT, user_parts=user_parts, schema_hint=schema_hint, purpose=purpose,
            is_qa=True,
        )
    except LlmError as exc:
        return VisionQaResult(status="skipped", skip_reason=f"{type(exc).__name__}: {exc}")

    text_matches = bool(data.get("text_matches"))
    archetype_ok = bool(data.get("archetype_ok"))
    mismatches = [str(m) for m in (data.get("mismatches") or [])]
    notes = str(data.get("notes") or "") or None
    verdict = "pass" if (text_matches and archetype_ok) else "fail"
    if trace is not None:
        trace.gate_verdict(
            stage, gate="vision_qa", asset_id=asset_id, verdict=verdict,
            failing_span="; ".join(mismatches) or None, regeneration_counter=regeneration_counter,
        )
    return VisionQaResult(
        status=verdict, text_matches=text_matches, archetype_ok=archetype_ok, mismatches=mismatches, notes=notes,
    )


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
        llm_client: LlmClient | None = None,
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
        # W8-9 Q4 N-E vision-QA -- ``None`` (LLM disabled/unavailable this
        # run) degrades every QA call to ``status="skipped"``, never a hard
        # stage failure.
        self.llm_client = llm_client
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
        acct = _RunAccounting()

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
                        slot=plan.slot, status=status_text,
                    )
                )
                continue

            if acct.circuit_tripped:
                result.statuses.append(
                    MediaAssetStatus(
                        asset_id=plan.asset_id, cluster_key=plan.cluster_key, destination=plan.destination,
                        slot=plan.slot, status="not generated — unexplained-spend circuit breaker",
                    )
                )
                continue

            # W8-9 Q4: route/aspect are resolved per PLAN (hero vs slide,
            # and per-destination aspect ratio) rather than once for the
            # whole call -- ``resolve_route`` is where the tier-order
            # policy-stop lives now (replaces the two old literal
            # ``== "draft"`` hard-raises), evaluated lazily so a theme that
            # never actually emits a slide plan this run is never blocked by
            # a slide-class route it never uses.
            route_id = self.config.route_by_class.get(plan.asset_class, self.registry.draft_route_id)
            route = self.registry.resolve_route(route_id)
            aspect = self.config.aspect_ratio_by_destination.get(plan.destination, self.config.aspect_ratio)

            if self.config.dry_run:
                result.statuses.append(
                    MediaAssetStatus(
                        asset_id=plan.asset_id, cluster_key=plan.cluster_key, destination=plan.destination,
                        slot=plan.slot, status="plan-only — dry run", route_id=route.route_id,
                        model_string=route.model_string, expected_cost_usd=route.price_usd,
                    )
                )
                continue

            result.statuses.append(self._process_gated_plan(plan, route, aspect, acct, result))

        result.total_spent_usd = acct.spent_usd_run
        result.total_expected_usd = sum(s.expected_cost_usd or 0.0 for s in result.statuses)
        result.circuit_breaker_tripped = acct.circuit_tripped
        return result

    def _process_gated_plan(
        self, plan: MediaAssetPlan, route: ModelRoute, aspect: str, acct: _RunAccounting, result: MediaStageResult
    ) -> MediaAssetStatus:
        """Attempt 1, then -- only on a QA fail (never on a capped/failed/
        pending/submitted-unknown outcome, and never once the circuit
        breaker has tripped) -- exactly ONE regeneration at attempt 2
        (module docstring: "a real second paid submission, ledger-
        disciplined", §8.11's caps apply to it exactly like any other
        submission). A row that reaches ``ATTEMPT_MAX`` still failing QA is
        marked ``held-qa-failed`` inside :meth:`_complete_success` itself
        (it knows ``row.attempt`` there), so this method never needs its own
        "give up" branch -- ``_status_from_row`` already reports it."""
        status = self._submit_or_resolve(plan, route, aspect, attempt=1, acct=acct, result=result)
        # A regeneration attempt already on file (a PRIOR invocation's QA
        # failed and triggered one) is authoritative even when THIS call
        # resolves attempt 1 from a pre-existing terminal row and so never
        # re-runs QA on it itself (a resolved row's qa_verdict is not
        # reconstructed, module docstring) -- without this check, resuming
        # a held-qa-failed asset would silently forget attempt 2 ever
        # happened and report attempt 1's plain "generated" instead.
        attempt2_identity = dict(
            theme=self.theme, run_date=self.run_date, cluster_key=plan.cluster_key,
            asset_slot=plan.asset_slot, language=plan.language,
            prompt_pattern_version=PROMPT_PATTERN_VERSION, attempt=2,
        )
        attempt2_exists = self.store.find_media_intent(**attempt2_identity) is not None
        should_regenerate = attempt2_exists or (
            status.status == "generated" and status.qa_verdict == "fail" and not acct.circuit_tripped
        )
        if not should_regenerate:
            return status
        return self._submit_or_resolve(plan, route, aspect, attempt=2, acct=acct, result=result)

    def _submit_or_resolve(
        self, plan: MediaAssetPlan, route: ModelRoute, aspect: str, *, attempt: int,
        acct: _RunAccounting, result: MediaStageResult,
    ) -> MediaAssetStatus:
        """One (identity, attempt) submission-or-resolution, cap-checked and
        accounted exactly like ``process()``'s old single-attempt inline
        block -- factored out so attempt 1 and a QA-triggered attempt 2 for
        the SAME plan share one cap-check / spend-accounting / circuit-
        breaker code path instead of two copies of it."""
        identity_kwargs = dict(
            theme=self.theme, run_date=self.run_date, cluster_key=plan.cluster_key,
            asset_slot=plan.asset_slot, language=plan.language,
            prompt_pattern_version=PROMPT_PATTERN_VERSION, attempt=attempt,
        )
        # An existing (identity, attempt) row means a submission was already
        # attempted -- possibly in a prior invocation of this same run_id,
        # possibly moments ago in this very call. Resolve it in place; this
        # is NEVER a new submission, so it is exempt from caps, cap
        # accounting and the circuit breaker (no new money can move here --
        # see §8.5's uniqueness rule).
        existing = self.store.find_media_intent(**identity_kwargs)
        if existing is not None:
            if not existing.terminal:
                self._resolve_one_row(existing)
            refreshed = self.store.get_media_intent(existing.id)
            return self._status_from_row(plan, refreshed or existing)

        day_spend = self.store.media_spend_usd_for_day(theme=self.theme, run_date=self.run_date)
        decision = check_caps(
            count_so_far=acct.count_run, usd_so_far_run=acct.spent_usd_run, usd_so_far_day=day_spend,
            expected_cost_usd=route.price_usd, count_cap=self.config.per_run_count_cap,
            run_usd_cap=self.config.per_run_usd_cap, day_usd_cap=self.config.per_day_usd_cap,
        )
        if not decision.allowed:
            self.trace.decision(
                self.stage,
                decision=f"asset {plan.asset_id}/{plan.slot} (attempt {attempt}): {decision.status}",
                rule="ARCHITECTURE_PLAN §8.11: both caps checked at every submission, whichever trips first stops it",
            )
            return MediaAssetStatus(
                asset_id=plan.asset_id, cluster_key=plan.cluster_key, destination=plan.destination, slot=plan.slot,
                status=decision.status, route_id=route.route_id, expected_cost_usd=route.price_usd,
            )

        if not acct.balance_fetched:
            result.balance_before = self.kie.get_credit_balance(purpose="pre-submission balance snapshot")
            acct.balance_fetched = True

        asset_status = self._submit_new(plan, route, aspect, identity_kwargs, attempt=attempt)
        # Every branch below is reached only for a genuinely NEW submission
        # attempt this call (a createTask call was actually made) -- the
        # no-submission outcomes (capped, already-exists) are handled by the
        # returns above.
        acct.count_run += 1
        submission_cost_usd = 0.0
        if asset_status.status in ("generated", "held-qa-failed"):
            submission_cost_usd = asset_status.observed_cost_usd or route.price_usd
            acct.spent_usd_run += submission_cost_usd
            acct.ledger_recorded_usd += submission_cost_usd
        elif asset_status.status in ("pending — adopted by a later run", "submitted-unknown"):
            submission_cost_usd = route.price_usd
            acct.spent_usd_run += submission_cost_usd
            acct.ledger_recorded_usd += submission_cost_usd
            if asset_status.status == "pending — adopted by a later run":
                result.pending_count += 1
            else:
                result.submitted_unknown_count += 1
        # A definite provider-reported failure is not charged per Kie's
        # documentation (§5.6); nothing added to spend for "failed — *"
        # (``submission_cost_usd`` stays 0.0).

        if self._check_circuit_breaker(result, acct, submission_cost_usd):
            acct.circuit_tripped = True
        return asset_status

    def _check_circuit_breaker(
        self, result: MediaStageResult, acct: "_RunAccounting", submission_cost_usd: float
    ) -> bool:
        """Runs after every new submission this call. The trip decision
        itself stays CUMULATIVE, unchanged from before this fix (§8.13: it
        compares the TOTAL observed balance drift since this run's first
        submission against the TOTAL ledger-recorded spend so far -- a
        divergence trips regardless of which single submission it
        accumulated across).

        What the fix changes is the ``spend`` trace EVENT this emits: it now
        records only the DELTA this one submission contributed (to both
        ledger-recorded cost and observed balance movement), never the
        running cumulative total -- summing ``ledger_recorded`` across every
        ``spend`` event for a run now recovers the true total run spend
        instead of a multiple of it (the live-run defect: cumulative values
        0.04, 0.08, ... summed to $2.64 when the true spend was $0.44)."""
        balance_now = self.kie.get_credit_balance(purpose="post-submission balance reconciliation")
        result.balance_after = balance_now
        if result.balance_before is None or balance_now is None:
            return False

        delta_credits_cumulative = result.balance_before - balance_now
        delta_usd_cumulative = delta_credits_cumulative * self.registry.credit_usd
        denom = max(acct.ledger_recorded_usd, 0.01)
        relative_divergence = abs(delta_usd_cumulative - acct.ledger_recorded_usd) / denom

        previous_balance = acct.last_balance if acct.last_balance is not None else result.balance_before
        balance_delta_this_submission = (previous_balance - balance_now) * self.registry.credit_usd
        acct.last_balance = balance_now

        self.trace.spend(
            self.stage, wallet="media", expected=submission_cost_usd, ledger_recorded=submission_cost_usd,
            balance_delta=balance_delta_this_submission,
        )
        if relative_divergence > self.config.unexplained_spend_threshold:
            self.trace.degrade(
                self.stage,
                condition=(
                    f"unexplained-spend: ledger recorded ${acct.ledger_recorded_usd:.4f} cumulative this "
                    f"run, observed balance delta ${delta_usd_cumulative:.4f} cumulative "
                    f"({relative_divergence:.0%} divergence) — halting new submissions"
                ),
                caused="W2-02 circuit breaker (simplified): no new media submissions for the remainder of this run",
            )
            return True
        return False

    def _qa_runner_for(self, plan: MediaAssetPlan, *, regeneration_counter: int) -> Any:
        """Build the closure :meth:`_complete_success` calls (image path in
        hand) to run N-E vision-QA for THIS plan's expectations. Only the
        plan-aware submission path builds one (module docstring: phase-0
        adoption has no plan and passes ``qa_runner=None`` instead)."""

        def runner(image_path: Path) -> VisionQaResult:
            return run_vision_qa(
                llm_client=self.llm_client, image_bytes=image_path.read_bytes(),
                mime=guess_image_mime(image_path), expected_text=plan.qa_expected_text,
                archetype=plan.qa_archetype, register=plan.qa_register,
                purpose=f"N-E vision QA — {plan.asset_id}/{plan.slot} (attempt {regeneration_counter})",
                trace=self.trace, stage=self.stage, asset_id=f"{plan.asset_id}/{plan.slot}",
                regeneration_counter=regeneration_counter,
            )

        return runner

    def _submit_new(
        self, plan: MediaAssetPlan, route: ModelRoute, aspect: str, identity_kwargs: dict[str, Any], *, attempt: int
    ) -> MediaAssetStatus:
        """Commit the write-ahead intent row and submit -- called only when
        ``_submit_or_resolve`` has confirmed no (identity, attempt) row
        already exists. The row is committed BEFORE ``createTask`` is called
        (§8.5); :class:`MediaIntentAlreadyExists` is still handled
        defensively below in case of a race between the existence check and
        this insert."""
        assert plan.image_brief is not None or plan.crafted_prompt is not None
        # W8-9 Q3c/Q4: prefer the N-D-crafted, gate-checked prompt for this
        # exact slot when one is available; degrade to the pre-existing
        # deterministic template otherwise (crafter disabled/unavailable/
        # gate-blocked -- hero plans only, see ``plan_media_assets``).
        prompt = plan.crafted_prompt or compose_prompt(plan.image_brief or "", self.registry)
        try:
            row = self.store.insert_media_intent(
                run_id=self.run_id, route_id=route.route_id, model_string=route.model_string,
                requested_aspect=aspect, requested_output_format=self.config.output_format,
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
                input_={"prompt": prompt, "output_format": self.config.output_format, "aspect_ratio": aspect},
                purpose=f"{route.tier}-tier image generation for {plan.cluster_key}/{plan.destination}:{plan.slot} (attempt {attempt})",
            )
        except KieTransportError as exc:
            # Sub-case A candidate: we truly do not know if the provider
            # received this. No task id was ever obtained.
            self.store.update_media_intent(row.id, state="submitted-unknown", submitted_unknown_subcase="A")
            self.trace.decision(
                self.stage,
                decision=f"createTask transport failure for {plan.asset_id}/{plan.slot}: {exc} -- submitted-unknown, sub-case A",
                rule="ARCHITECTURE_PLAN §8.5: money may have moved; no task id means unreachable by query",
            )
            return MediaAssetStatus(
                asset_id=plan.asset_id, cluster_key=plan.cluster_key, destination=plan.destination, slot=plan.slot,
                status="submitted-unknown", route_id=route.route_id, model_string=route.model_string,
                expected_cost_usd=route.price_usd, reason=str(exc),
            )
        except KieApiError as exc:
            # A clean, definite rejection before any task existed -- not
            # ambiguous, not charged, terminal.
            self.store.update_media_intent(row.id, state="failed", fail_reason=str(exc), terminal=True, resolved_at=self._now())
            return MediaAssetStatus(
                asset_id=plan.asset_id, cluster_key=plan.cluster_key, destination=plan.destination, slot=plan.slot,
                status="failed — createTask rejected", route_id=route.route_id, model_string=route.model_string,
                expected_cost_usd=route.price_usd, reason=str(exc),
            )

        self.store.set_media_task_id(row.id, created.task_id)
        qa_runner = self._qa_runner_for(plan, regeneration_counter=attempt)
        return self._poll_to_resolution(plan, route, row.id, created.task_id, qa_runner=qa_runner)

    def _poll_to_resolution(
        self, plan: MediaAssetPlan, route: ModelRoute, row_id: int, task_id: str, *, qa_runner: Any = None
    ) -> MediaAssetStatus:
        deadline = self.config.poll_timeout_seconds
        elapsed = 0.0
        while True:
            try:
                info = self.kie.record_info(task_id, purpose=f"poll job status for {plan.asset_id}/{plan.slot}")
            except (KieTransportError, KieApiError):
                self.store.update_media_intent(row_id, state="submitted-unknown", submitted_unknown_subcase="B")
                return MediaAssetStatus(
                    asset_id=plan.asset_id, cluster_key=plan.cluster_key, destination=plan.destination,
                    slot=plan.slot, status="submitted-unknown", route_id=route.route_id,
                    model_string=route.model_string, expected_cost_usd=route.price_usd, task_id=task_id,
                )
            if info.is_success:
                row = self.store.get_media_intent(row_id)
                assert row is not None
                qa_result = self._complete_success(row, info, qa_runner=qa_runner)
                refreshed = self.store.get_media_intent(row_id)
                status = self._status_from_row(plan, refreshed)
                if qa_result is not None:
                    status.qa_verdict = qa_result.status
                return status
            if info.is_failure:
                row = self.store.get_media_intent(row_id)
                assert row is not None
                self._complete_failure(row, info)
                return MediaAssetStatus(
                    asset_id=plan.asset_id, cluster_key=plan.cluster_key, destination=plan.destination,
                    slot=plan.slot,
                    status="failed — provider refused" if _looks_like_refusal(info) else "failed — provider error",
                    route_id=route.route_id, model_string=route.model_string, task_id=task_id,
                    reason=info.fail_msg or info.fail_code,
                )
            if elapsed >= deadline:
                self.trace.degrade(
                    self.stage,
                    condition=f"asset {plan.asset_id}/{plan.slot} still pending at poll timeout ({deadline}s)",
                    caused="§8.13: job stays 'polling', adopted by a later run's phase-0 resolution",
                )
                return MediaAssetStatus(
                    asset_id=plan.asset_id, cluster_key=plan.cluster_key, destination=plan.destination,
                    slot=plan.slot, status="pending — adopted by a later run", route_id=route.route_id,
                    model_string=route.model_string, expected_cost_usd=route.price_usd, task_id=task_id,
                )
            self._sleep(self.config.poll_interval_seconds)
            elapsed += self.config.poll_interval_seconds

    def _complete_success(
        self, row: MediaIntentRow, info: RecordInfoResult, *, qa_runner: Any = None
    ) -> "VisionQaResult | None":
        """Download + checksum, run N-E vision-QA (when ``qa_runner`` is
        given -- the plan-aware submission path always supplies one; phase-0
        adoption never does, module docstring), and persist both the ledger
        row and the per-asset provenance YAML. Returns the QA verdict (or
        ``None`` when nothing was ever downloaded/marked done) so the caller
        can decide whether a regeneration attempt is warranted."""
        if not info.result_urls:
            self.store.update_media_intent(
                row.id, state="failed", fail_reason="success state with no resultUrls", terminal=True,
                resolved_at=self._now(),
            )
            return None
        destination, slot = _parse_asset_slot(row.asset_slot)
        asset_dir = self.pack_media_dir / f"{row.cluster_key}_{destination}"
        dest_path = asset_dir / f"{slot}.{self.config.output_format}"
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

        if qa_runner is not None:
            qa_result = qa_runner(dest_path)
        else:
            qa_result = VisionQaResult(
                status="skipped",
                skip_reason="phase0-adoption (no plan context available for text/archetype expectations this milestone)",
            )

        # W8-9 Q4: a QA fail on the LAST allowed attempt is held for
        # operator review rather than shipped as "generated" -- it stays
        # "done" in every other respect (terminal, image on disk, ledger
        # settled) so nothing here re-triggers a THIRD paid attempt.
        final_state = "held-qa-failed" if (qa_result.status == "fail" and row.attempt >= ATTEMPT_MAX) else "done"
        self.store.update_media_intent(
            row.id, state=final_state, delivered_route_state=delivered_state, delivered_model=delivered_model,
            observed_cost_credits=info.credits_consumed, observed_cost_usd=observed_usd,
            image_path=str(dest_path), checksum_sha256=outcome.checksum_sha256, terminal=True,
            resolved_at=self._now(),
        )
        _write_provenance_yaml(
            asset_dir, row=row, delivered_state=delivered_state, delivered_model=delivered_model,
            checksum=outcome.checksum_sha256, observed_cost_usd=observed_usd, image_path=dest_path,
            registry=self.registry, prompt_full=row.prompt_full, slot=slot, qa=qa_result, final_state=final_state,
        )
        return qa_result

    def _complete_failure(self, row: MediaIntentRow, info: RecordInfoResult) -> None:
        self.store.update_media_intent(
            row.id, state="failed", fail_reason=info.fail_msg or info.fail_code or "provider reported failure",
            terminal=True, resolved_at=self._now(),
        )

    def _status_from_row(self, plan: MediaAssetPlan, row: MediaIntentRow | None) -> MediaAssetStatus:
        if row is None:
            return MediaAssetStatus(
                asset_id=plan.asset_id, cluster_key=plan.cluster_key, destination=plan.destination,
                slot=plan.slot, status="submitted-unknown",
            )
        if row.state == "done":
            return MediaAssetStatus(
                asset_id=plan.asset_id, cluster_key=plan.cluster_key, destination=plan.destination, slot=plan.slot,
                status="generated", route_id=row.route_id, model_string=row.model_string,
                expected_cost_usd=row.expected_cost_usd, observed_cost_usd=row.observed_cost_usd,
                delivered_route_state=row.delivered_route_state, image_path=row.image_path, task_id=row.task_id,
            )
        if row.state == "held-qa-failed":
            return MediaAssetStatus(
                asset_id=plan.asset_id, cluster_key=plan.cluster_key, destination=plan.destination, slot=plan.slot,
                status="held-qa-failed", route_id=row.route_id, model_string=row.model_string,
                expected_cost_usd=row.expected_cost_usd, observed_cost_usd=row.observed_cost_usd,
                delivered_route_state=row.delivered_route_state, image_path=row.image_path, task_id=row.task_id,
                reason="N-E vision-QA failed on both attempts — held for operator review, never auto-shipped anyway",
            )
        if row.state == "failed":
            return MediaAssetStatus(
                asset_id=plan.asset_id, cluster_key=plan.cluster_key, destination=plan.destination, slot=plan.slot,
                status="failed — provider refused" if row.fail_reason and _refusal_text(row.fail_reason) else "failed — provider error",
                route_id=row.route_id, model_string=row.model_string, task_id=row.task_id, reason=row.fail_reason,
            )
        if row.state == "submitted-unknown":
            return MediaAssetStatus(
                asset_id=plan.asset_id, cluster_key=plan.cluster_key, destination=plan.destination, slot=plan.slot,
                status="submitted-unknown", route_id=row.route_id, model_string=row.model_string,
                expected_cost_usd=row.expected_cost_usd, task_id=row.task_id,
            )
        # Still polling/intent -- treat as pending-adopted for display.
        return MediaAssetStatus(
            asset_id=plan.asset_id, cluster_key=plan.cluster_key, destination=plan.destination, slot=plan.slot,
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
    asset_dir: Path,
    *,
    row: MediaIntentRow,
    delivered_state: str,
    delivered_model: str | None,
    checksum: str | None,
    observed_cost_usd: float | None,
    image_path: Path,
    registry: ModelRegistry,
    slot: str,
    qa: "VisionQaResult",
    final_state: str,
    prompt_full: str | None = None,
) -> None:
    """Per-slot provenance record (§5.6/§12.2), stored beside the image
    inside its asset's own ``pack/media/<cluster_key>_<destination>/``
    folder (W8-9 Q4 pack layout -- one folder per asset, one image + one
    provenance file per slot: ``hero.png``/``hero.provenance.yaml`` for a
    single-image destination, ``slide_01.png``/``slide_01.provenance.yaml``
    ... for a carousel). Provider URLs are never written here or anywhere
    else in the pack.

    ``prompt_full`` (W8-8) is the complete, exact prompt sent to the image
    model -- own-authored content (either an N-D-crafted prompt or
    :func:`compose_prompt`'s output), not third-party text, so unlike the
    trace's own redaction rule (sha256 + length only, RUN_TRACE_SPEC §3) it
    is safe and useful to keep in full here, beside the image it produced.

    ``qa`` (W8-9 Q4 N-E) is always present -- a ``status="skipped"`` verdict
    with its ``skip_reason`` is not a failure, just an honest "nothing was
    checked here and here is why"."""
    destination, _slot_from_asset_slot = _parse_asset_slot(row.asset_slot)
    doc = {
        "asset_id": f"{row.cluster_key}_{row.asset_slot}",
        "cluster_key": row.cluster_key,
        "destination": destination,
        "slot": slot,
        "language": row.language,
        "status": final_state,
        "requested_route": row.route_id,
        "requested_model": row.model_string,
        "requested_aspect": row.requested_aspect,
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
        "qa": qa.to_yaml_dict(),
        "logo_overlay": "deferred to a later phase — this pack carries the raw generated image only",
    }
    provenance_path = asset_dir / f"{slot}.provenance.yaml"
    provenance_path.parent.mkdir(parents=True, exist_ok=True)
    provenance_path.write_text(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False), encoding="utf-8")
