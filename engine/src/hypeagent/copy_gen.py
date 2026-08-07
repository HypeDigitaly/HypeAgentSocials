"""Copy generation: the ``TextModel`` protocol, two providers, and the
per-asset orchestration that ties spin -> a copy request -> the claim gate
-> a bounded repair loop (ARCHITECTURE_PLAN.md §6.9, §14.0, §14.3, §14.6;
GOAL_ROADMAP.md M3(c)).

``interactive-file`` is the finish-line path for this goal: the stage
writes a complete, self-contained brief to
``logs/runs/<run_id>/copy_requests/<asset_id>.yaml`` and the run pauses
that asset — if a matching ``copy_responses/<asset_id>.yaml`` exists it is
consumed and gated, otherwise the asset is held. Re-running the pipeline
against the **same run identity** (the unit of resumability this engine
has today — see the module-level note below) picks the response up without
re-writing the request or re-running anything upstream, because the
provider only writes a request file if one is not already on disk.

``openai-compatible-http`` is a generic, config-driven provider (base_url,
model, key file path) so a future key drops in with no code change. It is
disabled by default in the theme config, because no key exists for this
goal; a fixture test proves only the request shape.

**Resolved ambiguity, recorded here rather than re-litigated at every call
site:** GOAL_ROADMAP.md's M3(c) text says "re-running the same run-date
resumes and picks up responses." This engine mints a brand-new ``run_id``
(and therefore a brand-new ``logs/runs/<run_id>/`` directory) on every plain
process invocation (``run_identity.new_run_identity()`` in ``main.py``), so
the resumable unit this module's own logic implements is "the same run
identity, invoked again" (exactly the pattern the rest of this codebase's
own idempotency tests already use, e.g. ``test_phase1_pipeline.py``'s
explicit-``run_id`` reuse) rather than "the same calendar date, any
run_id." ``python -m hypeagent --resume <run_id>`` (``main.py``,
``stages.resume_pipeline``) is the explicit-act CLI surface for exactly
this same-run-identity resumption — it re-enters ``copy`` (this module)
plus ``media``/``packaging``/``digest`` without re-running collection,
ranking, brand_truth or spin, reading their prior output back from
``resume_state.yaml`` instead. A true resume-by-calendar-date across a
*different* run_id (picking up yesterday's held assets from a brand-new
run) is still out of scope: that would re-enter ranking's cross-day dedupe
and immediately suppress everything as "generated previously" (§2.8a).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Protocol

import yaml

from hypeagent.claim_gate import ClaimGateVerdict, run_claim_gate
from hypeagent.brand_truth import ClaimSnapshot
from hypeagent.collectors.base import Fetcher
from hypeagent.config_load import OpenAICompatibleConfig, ResolvedList
from hypeagent.spin import SpinResult

AI_DISCLOSURE_LINE = "[AI-generated content]"


class CopyProviderError(Exception):
    """Raised by a ``TextModel`` provider on a genuine failure to produce
    copy (config error, transport error, malformed response) — distinct
    from the interactive-file provider's ordinary "held" outcome, which is
    not an error and is signalled by returning ``None``."""


@dataclass(frozen=True)
class CopyRequest:
    """A complete, self-contained brief — every field a copy provider (or a
    human filling the interactive-file response) needs, with nothing to
    look up elsewhere."""

    asset_id: str
    cluster_key: str
    destination: str  # linkedin | instagram_feed
    attempt: int
    topic: str
    excerpt_refs: list[str]
    spin_rationale: str
    icp_text: str
    pain: str
    offer_text: str | None
    mapping_distance: str
    value_only: bool
    cta_class: str
    cta_text: str
    allowed_facts: list[dict[str, Any]]
    negative_capabilities: list[str]
    pricing_policy_line: str
    hard_excludes: dict[str, list[str]]
    destination_constraints: dict[str, Any]
    exemplar_pool_paths: list[str]
    disclosure_requirement: str
    snapshot_id: str
    prior_failing_spans: list[str] = field(default_factory=list)

    def to_yaml_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "cluster_key": self.cluster_key,
            "destination": self.destination,
            "attempt": self.attempt,
            "topic": self.topic,
            "excerpt_refs": self.excerpt_refs,
            "spin_rationale": self.spin_rationale,
            "icp": self.icp_text,
            "pain": self.pain,
            "offer": self.offer_text,
            "mapping_distance": self.mapping_distance,
            "value_only_variant": self.value_only,
            "cta_class": self.cta_class,
            "cta_text": self.cta_text,
            "allowed_facts": self.allowed_facts,
            "negative_capabilities": self.negative_capabilities,
            "pricing_policy": self.pricing_policy_line,
            "hard_excludes": self.hard_excludes,
            "destination_constraints": self.destination_constraints,
            "exemplar_pool_paths": self.exemplar_pool_paths,
            "disclosure_requirement": self.disclosure_requirement,
            "snapshot_id": self.snapshot_id,
            "prior_failing_spans": self.prior_failing_spans,
            "response_shape_expected": {
                "headline": "string, image overlay text, <= 12 words",
                "caption": "string, <= 2200 chars, must include the AI-content disclosure line",
                "image_brief": "string, scene description (people-free, no product depiction; logo overlay applied post-generation, not generated)",
            },
        }


@dataclass(frozen=True)
class CopyResult:
    headline: str
    caption: str
    image_brief: str
    provider: str
    raw: dict[str, Any] | None = None


class TextModel(Protocol):
    """``generate`` returns ``None`` to mean "held — no output yet" (the
    interactive-file provider's normal resting state); every other provider
    either returns a ``CopyResult`` or raises ``CopyProviderError``."""

    def generate(self, request: CopyRequest) -> CopyResult | None: ...


# ---------------------------------------------------------------------------
# Provider 1: interactive-file — the finish-line path for this goal.
# ---------------------------------------------------------------------------


class InteractiveFileProvider:
    def __init__(self, run_dir: Path) -> None:
        self.run_dir = Path(run_dir)

    def _paths(self, request: CopyRequest) -> tuple[Path, Path]:
        suffix = "" if request.attempt <= 1 else f".attempt{request.attempt}"
        req_path = self.run_dir / "copy_requests" / f"{request.asset_id}{suffix}.yaml"
        resp_path = self.run_dir / "copy_responses" / f"{request.asset_id}{suffix}.yaml"
        return req_path, resp_path

    def request_path(self, request: CopyRequest) -> Path:
        return self._paths(request)[0]

    def generate(self, request: CopyRequest) -> CopyResult | None:
        req_path, resp_path = self._paths(request)
        req_path.parent.mkdir(parents=True, exist_ok=True)
        if not req_path.exists():
            req_path.write_text(
                yaml.safe_dump(request.to_yaml_dict(), allow_unicode=True, sort_keys=False),
                encoding="utf-8",
            )
        if not resp_path.exists():
            return None
        data = yaml.safe_load(resp_path.read_text(encoding="utf-8")) or {}
        if not isinstance(data, dict):
            raise CopyProviderError(f"malformed copy response at {resp_path}: expected a mapping")
        return CopyResult(
            headline=str(data.get("headline", "")),
            caption=str(data.get("caption", "")),
            image_brief=str(data.get("image_brief", "")),
            provider="interactive-file",
            raw=data,
        )


# ---------------------------------------------------------------------------
# Provider 2: openai-compatible-http — generic, config-driven, disabled by
# default; structure proven by a fixture test of the request shape only.
# ---------------------------------------------------------------------------


class OpenAICompatibleProvider:
    def __init__(self, config: OpenAICompatibleConfig, fetcher: Fetcher) -> None:
        self.config = config
        self.fetcher = fetcher

    def generate(self, request: CopyRequest) -> CopyResult:
        if not self.config.enabled:
            raise CopyProviderError("openai-compatible-http provider is disabled in theme config")
        key_path = Path(self.config.key_path) if self.config.key_path else None
        if key_path is None or not key_path.exists():
            raise CopyProviderError(f"openai-compatible-http API key file missing at {self.config.key_path!r}")
        api_key = key_path.read_text(encoding="utf-8").strip()
        if not api_key:
            raise CopyProviderError(f"openai-compatible-http API key file at {key_path} is empty")

        prompt = _build_prompt(request)
        body = json.dumps(
            {
                "model": self.config.model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": self.config.max_tokens,
            }
        ).encode("utf-8")
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        url = f"{self.config.base_url.rstrip('/')}/chat/completions"
        response = self.fetcher.fetch(url, headers=headers, method="POST", body=body)
        try:
            payload = json.loads(response.body)
            content = payload["choices"][0]["message"]["content"]
            parsed = json.loads(content)
        except (KeyError, IndexError, json.JSONDecodeError, TypeError) as exc:
            raise CopyProviderError(f"openai-compatible-http: could not parse model response: {exc}") from exc
        return CopyResult(
            headline=str(parsed.get("headline", "")),
            caption=str(parsed.get("caption", "")),
            image_brief=str(parsed.get("image_brief", "")),
            provider="openai-compatible-http",
            raw=parsed,
        )


def _build_prompt(request: CopyRequest) -> str:
    return (
        "Write social copy as JSON with keys headline, caption, image_brief. "
        f"Topic: {request.topic}. ICP: {request.icp_text}. Pain: {request.pain}. "
        f"Offer: {request.offer_text or 'none — value-only'}. CTA class: {request.cta_class}. "
        f"Destination: {request.destination}. Must include an AI-generated-content disclosure "
        f"line in the caption. Allowed facts: {json.dumps(request.allowed_facts, ensure_ascii=False)}."
    )


# ---------------------------------------------------------------------------
# Request assembly + the per-asset gate/repair orchestration.
# ---------------------------------------------------------------------------

_DESTINATION_CONSTRAINTS: dict[str, dict[str, Any]] = {
    "linkedin": {
        "headline_max_words": 12,
        "caption_max_chars": 2200,
        "format": "static-image post",
        "people_free_composition": True,
        "no_product_depiction": True,
    },
    "instagram_feed": {
        "headline_max_words": 12,
        "caption_max_chars": 2200,
        "format": "static-image post",
        "people_free_composition": True,
        "no_product_depiction": True,
    },
}


def build_copy_request(
    *,
    asset_id: str,
    destination: str,
    spin: SpinResult,
    excerpt_refs: list[str],
    allowed_facts: list[dict[str, Any]],
    negative_capabilities: list[str],
    pricing_policy_line: str,
    hard_excludes: dict[str, ResolvedList],
    exemplar_pool_paths: list[str],
    snapshot_id: str,
    attempt: int = 1,
    prior_failing_spans: list[str] | None = None,
) -> CopyRequest:
    return CopyRequest(
        asset_id=asset_id,
        cluster_key=spin.cluster_key,
        destination=destination,
        attempt=attempt,
        topic=spin.topic,
        excerpt_refs=excerpt_refs,
        spin_rationale=spin.rationale_line,
        icp_text=spin.icp_text,
        pain=spin.pain,
        offer_text=spin.offer_text,
        mapping_distance=spin.mapping_distance,
        value_only=spin.value_only,
        cta_class=spin.cta_class,
        cta_text=spin.cta_text,
        allowed_facts=allowed_facts,
        negative_capabilities=negative_capabilities,
        pricing_policy_line=pricing_policy_line,
        hard_excludes={k: [str(v) for v in item.values] for k, item in hard_excludes.items()},
        destination_constraints=_DESTINATION_CONSTRAINTS.get(destination, {}),
        exemplar_pool_paths=exemplar_pool_paths,
        disclosure_requirement=f'caption must contain an AI-content disclosure marker, e.g. "{AI_DISCLOSURE_LINE}"',
        snapshot_id=snapshot_id,
        prior_failing_spans=prior_failing_spans or [],
    )


@dataclass
class AssetCopyStatus:
    asset_id: str
    cluster_key: str
    destination: str
    status: str  # held — awaiting operator copy | gated-pass | blocked — claim gate (...)
    attempt: int
    failing_spans: list[str] = field(default_factory=list)
    headline: str | None = None
    caption: str | None = None
    image_brief: str | None = None
    request_path: str | None = None


def process_copy_asset(
    *,
    provider: TextModel,
    request: CopyRequest,
    snapshot: ClaimSnapshot,
    hard_excludes: dict[str, ResolvedList] | None = None,
    max_attempts: int = 2,
    trace: Any = None,
    stage: str = "copy",
) -> AssetCopyStatus:
    """Run one copy asset through generation and the claim gate, honouring
    the combined per-artifact repair ceiling (§14.0): on a block, a
    regeneration request is written (same brief + the specific failing
    spans as corrective context) up to ``max_attempts`` attempts total.
    Never fabricates a fix silently — an exhausted budget blocks the asset
    with the reason recorded, it does not retry forever."""
    current = request
    request_path_str: str | None = None
    while True:
        if hasattr(provider, "request_path"):
            request_path_str = str(provider.request_path(current))  # type: ignore[attr-defined]
        try:
            result = provider.generate(current)
        except CopyProviderError as exc:
            # §11.3 fifth fail-closed trigger: a gate/provider that cannot
            # run never defaults open.
            return AssetCopyStatus(
                asset_id=current.asset_id, cluster_key=current.cluster_key, destination=current.destination,
                status=f"blocked — copy provider unavailable ({exc})", attempt=current.attempt,
                request_path=request_path_str,
            )
        if result is None:
            return AssetCopyStatus(
                asset_id=current.asset_id, cluster_key=current.cluster_key, destination=current.destination,
                status="held — awaiting operator copy", attempt=current.attempt, request_path=request_path_str,
            )

        verdict: ClaimGateVerdict = run_claim_gate(
            headline=result.headline, caption=result.caption, image_brief=result.image_brief,
            snapshot=snapshot, hard_excludes=hard_excludes,
        )
        if trace is not None:
            failing_span_summary = "; ".join(f"{s.field_name}:{s.kind}:{s.text}" for s in verdict.failing_spans) or None
            trace.gate_verdict(
                stage, gate="claim_gate", asset_id=current.asset_id, verdict=verdict.verdict,
                failing_span=failing_span_summary, regeneration_counter=current.attempt,
            )

        if verdict.verdict == "pass":
            return AssetCopyStatus(
                asset_id=current.asset_id, cluster_key=current.cluster_key, destination=current.destination,
                status="gated-pass", attempt=current.attempt,
                headline=result.headline, caption=result.caption, image_brief=result.image_brief,
                request_path=request_path_str,
            )

        failing_span_texts = [f"{s.field_name}: {s.kind} '{s.text}' — {s.reason}" for s in verdict.failing_spans]
        if current.attempt >= max_attempts:
            return AssetCopyStatus(
                asset_id=current.asset_id, cluster_key=current.cluster_key, destination=current.destination,
                status="blocked — claim gate (repair budget exhausted)", attempt=current.attempt,
                failing_spans=failing_span_texts, request_path=request_path_str,
            )
        current = replace(current, attempt=current.attempt + 1, prior_failing_spans=failing_span_texts)
