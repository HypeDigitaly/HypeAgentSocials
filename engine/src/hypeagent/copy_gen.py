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
from hypeagent.llm import LlmClient, LlmError
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
    # W8-9 Q3b: carousel destinations (instagram_feed/tiktok) carry per-slide
    # copy here — ``None`` for every non-carousel path (linkedin, and every
    # pre-existing provider/test), so this is a purely additive, backward-
    # compatible field. Each slide dict is ``{"role", "title", "body",
    # "component"}`` (component optional/empty string when unused).
    slides: list[dict[str, str]] | None = None


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
        suffix = _attempt_suffix(request.attempt)
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
    """W8-9 Q2 fix: the original version of this prompt dropped most of
    ``CopyRequest`` on the floor -- most notably ``prior_failing_spans``,
    which meant a regeneration attempt on this provider carried no
    corrective context at all and would very likely reproduce the exact
    same claim-gate failure. Every field that changes attempt-to-attempt
    (failing spans) or that the model must never violate (negative
    capabilities, hard excludes) is now included."""
    parts = [
        "Write social copy as JSON with keys headline, caption, image_brief. "
        f"Topic: {request.topic}. ICP: {request.icp_text}. Pain: {request.pain}. "
        f"Offer: {request.offer_text or 'none — value-only'}. CTA class: {request.cta_class}. "
        f"Destination: {request.destination}. Must include an AI-generated-content disclosure "
        f"line in the caption. Allowed facts: {json.dumps(request.allowed_facts, ensure_ascii=False)}.",
        f"Negative capabilities (never imply any of these): "
        f"{json.dumps(request.negative_capabilities, ensure_ascii=False)}.",
        f"Hard excludes (never mention any of these): {json.dumps(request.hard_excludes, ensure_ascii=False)}.",
    ]
    if request.prior_failing_spans:
        parts.append(
            "Your previous attempt was BLOCKED by the claim gate for these exact reasons — fix every "
            f"one of them in this attempt: {json.dumps(request.prior_failing_spans, ensure_ascii=False)}."
        )
    return " ".join(parts)


# ---------------------------------------------------------------------------
# Provider 3: openrouter — N-C Copywriter, the enabled LLM path (W8-9 Q3b).
# Grounds in everything ``CopyRequest`` carries PLUS what it never carried at
# all: the brand identity one-liner, the FULL style_guide platform skeleton
# for the destination, and this run's viral-playbook section for the
# topic — see FLOW_MAP.md §3's N-C row for the exact input/output contract.
# ---------------------------------------------------------------------------

_CAROUSEL_DESTINATIONS = ("instagram_feed", "tiktok")


def _platform_skeleton(style_guide: dict[str, Any], destination: str) -> dict[str, Any]:
    platforms = style_guide.get("platforms") or {}
    block = platforms.get(destination)
    return block if isinstance(block, dict) else {}


def _viral_playbook_section(viral_playbook: Any | None, topic: str) -> str:
    """``viral_playbook`` is an ``analysis.ViralPlaybook`` — typed ``Any``
    here (duck-typed via ``theme_playbook``/``skipped``/``degraded``) so
    this module never has to import ``analysis`` (which itself imports
    ``llm``, imported here already) purely for a type annotation."""
    if viral_playbook is None:
        return "No viral playbook available this run — ground purely in the style guide and your own judgment."
    theme_pb = None
    if hasattr(viral_playbook, "theme_playbook"):
        theme_pb = viral_playbook.theme_playbook(topic)
    if theme_pb is None:
        reason = getattr(viral_playbook, "skip_reason", None) or getattr(viral_playbook, "degrade_reason", None)
        if reason:
            return (
                f"No viral playbook available this run ({reason}) — ground purely in the style guide "
                "and your own judgment."
            )
        return "No matching theme in this run's viral playbook — ground purely in the style guide and your own judgment."
    return yaml.safe_dump(theme_pb.to_yaml_dict(), allow_unicode=True, sort_keys=False)


def _build_openrouter_prompt(
    request: CopyRequest,
    *,
    style_guide: dict[str, Any],
    viral_playbook: Any | None,
    brand_identity_one_liner: str,
) -> tuple[str, str, str]:
    """Returns ``(system, user_content, schema_hint)`` for
    ``LlmClient.call_json``."""
    wants_slides = request.destination in _CAROUSEL_DESTINATIONS
    skeleton = _platform_skeleton(style_guide, request.destination)

    system = (
        "You are the Copywriter (N-C) for HypeDigitaly's AI-agency social content pipeline "
        "(FLOW_MAP.md node N-C). "
        f"Brand: {brand_identity_one_liner} "
        "You write ONLY within the rules given below — you never state a price or a price-shaped "
        "figure, you never claim a number that is not in the allowed_facts list, you never use "
        "superlative/guarantee/therapeutic-outcome language, and you ALWAYS include the exact "
        f'disclosure line "{AI_DISCLOSURE_LINE}" in the caption. Trend-corpus numbers belong to the '
        'trend, not to us — attribute them explicitly ("creators are reporting..."), never claim '
        "them as our own results. Every deterministic rule you violate will be caught by a claim "
        "gate and sent back to you for repair, so follow them exactly the first time."
    )

    lines: list[str] = [
        f"Destination: {request.destination}",
        f"Topic: {request.topic}",
        f"ICP: {request.icp_text}",
        f"Pain: {request.pain}",
        f"Offer: {request.offer_text or 'none — value-only (far mapping distance: no product CTA)'}",
        f"Mapping distance: {request.mapping_distance} (value_only={request.value_only})",
        f"CTA class: {request.cta_class}; CTA text: {request.cta_text}",
        f"Pricing policy: {request.pricing_policy_line}",
        f"Allowed facts (ONLY these numbers/claims are citable): "
        f"{json.dumps(request.allowed_facts, ensure_ascii=False)}",
        f"Negative capabilities (never imply): {json.dumps(request.negative_capabilities, ensure_ascii=False)}",
        f"Hard excludes (never mention): {json.dumps(request.hard_excludes, ensure_ascii=False)}",
        f"Disclosure requirement: {request.disclosure_requirement}",
        "",
        "Destination platform skeleton (style_guide.yaml — follow this shape exactly):",
        yaml.safe_dump(skeleton, allow_unicode=True, sort_keys=False),
        "",
        "This run's viral playbook for this topic (winning hooks/formats/visual archetypes/numbers "
        "seen in the niche this week):",
        _viral_playbook_section(viral_playbook, request.topic),
    ]
    if request.prior_failing_spans:
        lines.append("")
        lines.append(
            "Your previous attempt was BLOCKED by the deterministic claim gate for these exact "
            "reasons — you MUST fix every one of them in this attempt (rewrite the offending text; "
            "do not merely repeat it):"
        )
        lines.extend(f"- {s}" for s in request.prior_failing_spans)
    if wants_slides:
        lines.append("")
        lines.append(
            "This destination is a carousel: produce 6-10 slides, each "
            '{"role": "cover"|"body"|"end_card", "title", "body", "component" (optional)}, '
            "per the platform skeleton above."
        )

    if wants_slides:
        schema_hint = (
            'Schema: {"headline": string, "caption": string, "slides": '
            '[{"role": "cover"|"body"|"end_card", "title": string, "body": string, '
            '"component": string|null}], "image_direction": string}. "slides" must have between 6 '
            "and 10 entries."
        )
    else:
        schema_hint = 'Schema: {"headline": string, "caption": string, "image_direction": string}'

    return system, "\n".join(lines), schema_hint


def _parse_openrouter_response(data: dict[str, Any]) -> CopyResult:
    headline = str(data.get("headline", ""))
    caption = str(data.get("caption", ""))
    image_direction = data.get("image_direction")
    if not image_direction:
        image_direction = data.get("image_brief", "")

    slides: list[dict[str, str]] | None = None
    slides_raw = data.get("slides")
    if isinstance(slides_raw, list) and slides_raw:
        slides = []
        for item in slides_raw:
            if not isinstance(item, dict):
                continue
            component = item.get("component")
            slides.append(
                {
                    "role": str(item.get("role", "body")),
                    "title": str(item.get("title", "")),
                    "body": str(item.get("body", "")),
                    "component": str(component) if component else "",
                }
            )

    return CopyResult(
        headline=headline, caption=caption, image_brief=str(image_direction), provider="openrouter",
        raw=data, slides=slides,
    )


class OpenRouterProvider:
    """N-C Copywriter (W8-9 Q3b) — the enabled LLM path, replacing
    ``OpenAICompatibleProvider`` wherever ``generation.copy_provider ==
    "openrouter"`` and ``generation.llm.enabled`` is true (provider
    selection lives in ``stages._build_copy_provider``).
    ``OpenAICompatibleProvider`` keeps working unchanged for backward
    compatibility; ``InteractiveFileProvider`` remains the configured
    fallback whenever the LLM is disabled or unavailable."""

    def __init__(
        self,
        *,
        llm_client: LlmClient,
        style_guide: dict[str, Any] | None,
        viral_playbook: Any | None,
        brand_identity_one_liner: str,
        node_name: str = "copywriter",
    ) -> None:
        self.llm_client = llm_client
        self.style_guide = style_guide or {}
        self.viral_playbook = viral_playbook
        self.brand_identity_one_liner = brand_identity_one_liner
        self.node_name = node_name

    def generate(self, request: CopyRequest) -> CopyResult:
        system, user_content, schema_hint = _build_openrouter_prompt(
            request, style_guide=self.style_guide, viral_playbook=self.viral_playbook,
            brand_identity_one_liner=self.brand_identity_one_liner,
        )
        try:
            data = self.llm_client.call_json(
                self.node_name, system=system, user_parts=user_content, schema_hint=schema_hint,
                purpose=f"N-C copywriter — {request.destination} copy for {request.cluster_key} (attempt {request.attempt})",
            )
        except LlmError as exc:
            raise CopyProviderError(f"openrouter copywriter: {exc}") from exc
        return _parse_openrouter_response(data)


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
    # W8-9 Q3b: carousel per-slide copy, gate-passed. ``None`` for every
    # non-carousel asset (unchanged shape for every existing consumer).
    slides: list[dict[str, str]] | None = None


def _attempt_suffix(attempt: int) -> str:
    return "" if attempt <= 1 else f".attempt{attempt}"


def _copy_request_path(run_dir: Path, request: CopyRequest) -> Path:
    return run_dir / "copy_requests" / f"{request.asset_id}{_attempt_suffix(request.attempt)}.yaml"


def _persist_llm_copy_io(run_dir: Path, request: CopyRequest, result: CopyResult | None) -> None:
    """Generic ``copy_requests``/``copy_responses`` persistence for any
    provider that does not manage its own file-based round trip (i.e.
    everything except ``InteractiveFileProvider``, which already writes its
    request file inside ``generate()`` and treats a missing response file as
    "held"). Own-authored content — full text allowed (RUN_TRACE_SPEC.md §6:
    this is not the third-party-text redaction rule's target)."""
    suffix = _attempt_suffix(request.attempt)
    req_dir = run_dir / "copy_requests"
    req_dir.mkdir(parents=True, exist_ok=True)
    req_path = req_dir / f"{request.asset_id}{suffix}.yaml"
    if not req_path.exists():
        req_path.write_text(
            yaml.safe_dump(request.to_yaml_dict(), allow_unicode=True, sort_keys=False), encoding="utf-8"
        )
    if result is None:
        return
    resp_dir = run_dir / "copy_responses"
    resp_dir.mkdir(parents=True, exist_ok=True)
    resp_path = resp_dir / f"{request.asset_id}{suffix}.yaml"
    doc: dict[str, Any] = {
        "headline": result.headline, "caption": result.caption, "image_brief": result.image_brief,
        "provider": result.provider,
    }
    if result.slides is not None:
        doc["slides"] = result.slides
    resp_path.write_text(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False), encoding="utf-8")


def process_copy_asset(
    *,
    provider: TextModel,
    request: CopyRequest,
    snapshot: ClaimSnapshot,
    hard_excludes: dict[str, ResolvedList] | None = None,
    max_attempts: int = 2,
    trace: Any = None,
    stage: str = "copy",
    run_dir: Path | None = None,
) -> AssetCopyStatus:
    """Run one copy asset through generation and the claim gate, honouring
    the combined per-artifact repair ceiling (§14.0): on a block, a
    regeneration request is written (same brief + the specific failing
    spans as corrective context) up to ``max_attempts`` attempts total.
    Never fabricates a fix silently — an exhausted budget blocks the asset
    with the reason recorded, it does not retry forever.

    ``run_dir`` (W8-9 Q3b) is used only for providers that do not manage
    their own file persistence (``InteractiveFileProvider`` is detected via
    its own ``request_path`` method, exactly as this function already
    detected it for the request-path-in-status behaviour) — every LLM
    provider's request/response still lands under ``copy_requests``/
    ``copy_responses`` for the process summary and provenance to read.
    """
    current = request
    request_path_str: str | None = None
    is_file_backed_provider = hasattr(provider, "request_path")
    while True:
        if is_file_backed_provider:
            request_path_str = str(provider.request_path(current))  # type: ignore[attr-defined]
        try:
            result = provider.generate(current)
        except CopyProviderError as exc:
            # §11.3 fifth fail-closed trigger: a gate/provider that cannot
            # run never defaults open.
            if run_dir is not None and not is_file_backed_provider:
                _persist_llm_copy_io(run_dir, current, None)
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

        if run_dir is not None and not is_file_backed_provider:
            _persist_llm_copy_io(run_dir, current, result)
            request_path_str = str(_copy_request_path(run_dir, current))

        verdict: ClaimGateVerdict = run_claim_gate(
            headline=result.headline, caption=result.caption, image_brief=result.image_brief,
            snapshot=snapshot, hard_excludes=hard_excludes, slides=result.slides,
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
                request_path=request_path_str, slides=result.slides,
            )

        failing_span_texts = [f"{s.field_name}: {s.kind} '{s.text}' — {s.reason}" for s in verdict.failing_spans]
        if current.attempt >= max_attempts:
            return AssetCopyStatus(
                asset_id=current.asset_id, cluster_key=current.cluster_key, destination=current.destination,
                status="blocked — claim gate (repair budget exhausted)", attempt=current.attempt,
                failing_spans=failing_span_texts, request_path=request_path_str,
            )
        current = replace(current, attempt=current.attempt + 1, prior_failing_spans=failing_span_texts)
