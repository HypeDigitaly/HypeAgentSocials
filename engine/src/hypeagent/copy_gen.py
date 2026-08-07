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
import re
from collections.abc import Callable
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
    # W8-10 Phase 1 (copywriter-audit finding: attempt 1 of run e4d8 came
    # back IN CZECH, a silent locale flip -- the prompt never stated an
    # output language at all). Goal-scoped to EN; the field exists so a
    # future non-EN goal has somewhere to put it without a new request shape.
    language: str = "en"
    # W8-10 Phase 5 (``generation.post_mix``): value_only | playbook |
    # promotional — mirrors ``SpinResult.post_type`` (``build_copy_request``
    # carries it straight through).
    post_type: str = "promotional"

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
            "language": self.language,
            "post_type": self.post_type,
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

# W8-9 (carousel-completeness fix): the style guide's own carousel contract
# is 6-10 slides including a closing end-card — with the token-starvation
# fix (larger per-node ``max_tokens``) this should hold on the first
# attempt, but a deficient response is still handled explicitly rather than
# silently shipped short (the live-run defect: carousels came out with as
# few as 2-4 slides).
MIN_CAROUSEL_SLIDES = 6


def _platform_skeleton(style_guide: dict[str, Any], destination: str) -> dict[str, Any]:
    platforms = style_guide.get("platforms") or {}
    block = platforms.get(destination)
    return block if isinstance(block, dict) else {}


def _viral_playbook_section(viral_playbook: Any | None, topic: str) -> str:
    """``viral_playbook`` is an ``analysis.ViralPlaybook`` — typed ``Any``
    here (duck-typed via ``theme_playbook``/``skipped``/``degraded``) so
    this module never has to import ``analysis`` (which itself imports
    ``llm``, imported here already) purely for a type annotation.

    W8-10 Phase 5: also folds in the run-level fields (``connecting_thread``,
    ``viral_tactics_digest``, ``do_not_do``) the marketer audit found were
    fetched every run and never consumed by copy — read via ``getattr`` (not
    an import of ``hypeagent.analysis``) so a future field ``analysis.py``
    adds to either the per-theme or the global playbook shape renders here
    automatically, with no further change needed in this module."""
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

    payload: dict[str, Any] = dict(theme_pb.to_yaml_dict())
    connecting_thread = getattr(viral_playbook, "connecting_thread", None)
    if connecting_thread:
        payload["connecting_thread"] = connecting_thread
    viral_tactics_digest = getattr(viral_playbook, "viral_tactics_digest", None)
    if viral_tactics_digest:
        payload["viral_tactics_digest"] = viral_tactics_digest
    do_not_do = getattr(viral_playbook, "do_not_do", None)
    if do_not_do:
        payload["do_not_do"] = do_not_do
    return yaml.safe_dump(payload, allow_unicode=True, sort_keys=False)


# ---------------------------------------------------------------------------
# W8-10 Phase 1 — exemplar/excerpt injection (copywriter-audit finding #4:
# ``exemplar_pool_paths``/``excerpt_refs`` were carried on every request and
# NEVER reached the prompt at all). Voice/rhythm anchors only — framed
# explicitly as "match the rhythm, not the content" so the model never
# mistakes an exemplar for a source of claims or topics.
# ---------------------------------------------------------------------------

_EXEMPLAR_CHAR_CAP = 4000
_MAX_RESOLVED_EXCERPTS = 3


def _load_exemplar_block(
    exemplar_pool_paths: list[str],
    excerpt_refs: list[str],
    *,
    exemplar_base_dir: Path | None,
    excerpt_resolver: Callable[[str], str | None] | None,
) -> str:
    """Loads each configured exemplar file's raw text (truncated to
    :data:`_EXEMPLAR_CHAR_CAP` chars) plus up to
    :data:`_MAX_RESOLVED_EXCERPTS` resolved excerpt texts. A missing/
    unreadable exemplar file is skipped with a note, never an error — this
    is a voice aid, not a new failure surface. Returns ``""`` when nothing
    at all resolves (no exemplar paths configured, none readable, no
    resolver given)."""
    sections: list[str] = []
    notes: list[str] = []

    for raw_path in exemplar_pool_paths:
        candidates = [Path(raw_path)]
        if exemplar_base_dir is not None and not Path(raw_path).is_absolute():
            candidates.insert(0, Path(exemplar_base_dir) / raw_path)
        text: str | None = None
        for candidate in candidates:
            try:
                if candidate.exists():
                    text = candidate.read_text(encoding="utf-8")
                    break
            except OSError:
                continue
        if text is None:
            notes.append(f"(exemplar file not found/unreadable, skipped: {raw_path})")
            continue
        sections.append(f"--- exemplar: {raw_path} ---\n{text[:_EXEMPLAR_CHAR_CAP]}")

    if excerpt_resolver is not None:
        resolved = 0
        for ref in excerpt_refs:
            if resolved >= _MAX_RESOLVED_EXCERPTS:
                break
            try:
                text = excerpt_resolver(ref)
            except Exception:
                text = None
            if not text:
                continue
            sections.append(f"--- excerpt: {ref} ---\n{text[:_EXEMPLAR_CHAR_CAP]}")
            resolved += 1

    if not sections and not notes:
        return ""

    header = (
        "Voice/rhythm exemplars — match the SENTENCE RHYTHM and VOCABULARY LEVEL of the material "
        "below; do NOT reuse its exact phrases, its topics, or its claims:"
    )
    body = "\n\n".join(sections) if sections else "(no exemplar text resolved this run)"
    block = f"{header}\n\n{body}"
    if notes:
        block += "\n\n" + "\n".join(notes)
    return block


# ---------------------------------------------------------------------------
# W8-10 Phase 1 — the copywriter voice overhaul. The old prompt was 100%
# compliance and 0% voice (copywriter audit): no speaker, no register, no
# rhythm, and it literally handed the model the hedge phrase "creators are
# reporting..." (used 5x across 4 assets) plus an anxiety clause that made
# the model narrate its own compliance reasoning INTO the copy. Every
# compliance rule below is kept — restated plainly, without threat framing —
# alongside 12 countable voice rules the model is asked to self-check.
# ---------------------------------------------------------------------------

_VOICE_RULES_BLOCK = (
    "VOICE RULES — countable, self-check every one before you answer:\n"
    "1. First-person singular throughout. You are a named person writing this yourself (Pavel "
    "Čermák, HypeDigitaly's founder), on your phone, between calls — not a brand account.\n"
    "2. Your opening line is concrete and specific, grounded in something REAL from this run's "
    "viral playbook below (a real hook, a real tool, a real number someone else's post used). Do "
    "NOT invent a first-person incident and present it as fact — no \"this happened to me last "
    "week\" unless the material below genuinely gives you that scene. A fabricated anecdote is "
    "dishonest, not just against the rules.\n"
    "3. Vary sentence rhythm: at least 3 sentences under 6 words, and no two consecutive sentences "
    "share the same grammatical shape.\n"
    "4. At most ONE antithesis shape (\"it's not X, it's Y\" / \"X isn't Y, it's Z\") in the whole "
    "asset — count your own uses before answering.\n"
    "5. At most one em-dash per 150 words, and never a parenthetical pair of em-dashes.\n"
    "6. Never write a three-item parallel list in prose (the \", X, and Y\" shape).\n"
    "7. If you borrow a number from someone else's post (the viral playbook — never your own "
    "results), attribute it exactly once, as a single line at the very END of the asset, in your "
    "own words — never inline, and never explain to the reader why you're allowed to use it.\n"
    "8. Include exactly one concrete, usable artifact: a verbatim prompt, a verbatim search string, "
    "or a specific tool plus its exact setting. An abstract noun (workflow, system, layer, motion, "
    "engine) does not satisfy this — it must be something the reader can literally copy and use.\n"
    "9. The destination platform skeleton below is a MENU of beats, not a fill-in-the-blank form — "
    "use it as a guide and deliberately deviate from it in at least one visible way.\n"
    "10. Exactly one ask (one CTA) in the whole asset. Add a P.S. only if it carries genuinely new "
    "information — never a repeat, never a generic mindset throwaway line.\n"
    "11. Before you answer, re-read your own draft and delete the 3 weakest sentences.\n"
    "12. Output language: {language}."
)


def _build_openrouter_prompt(
    request: CopyRequest,
    *,
    style_guide: dict[str, Any],
    viral_playbook: Any | None,
    brand_identity_one_liner: str,
    exemplar_base_dir: Path | None = None,
    excerpt_resolver: Callable[[str], str | None] | None = None,
) -> tuple[str, str, str]:
    """Returns ``(system, user_content, schema_hint)`` for
    ``LlmClient.call_json``."""
    wants_slides = request.destination in _CAROUSEL_DESTINATIONS
    skeleton = _platform_skeleton(style_guide, request.destination)
    is_value_only = request.post_type == "value_only"

    # W8-10 Phase 5: a value_only post drops the brand entirely from the
    # prompt's identity line — the @hypedigitaly handle is image-direction
    # only (a small watermark), never named in copy.
    effective_brand = "" if is_value_only else brand_identity_one_liner
    brand_line = f"Brand: {effective_brand} " if effective_brand else ""

    system = (
        f"{brand_line}"
        f"{_VOICE_RULES_BLOCK.format(language=request.language)}\n\n"
        "COMPLIANCE — plain facts about this pipeline, not a threat: you never state a price or a "
        "price-shaped figure; you never claim a number that is not in the allowed_facts list below; "
        "you never use superlative, guarantee, or therapeutic-outcome language; you always include "
        f'the exact disclosure line "{AI_DISCLOSURE_LINE}" in the caption; you never mention anything '
        "in the hard-excludes or negative-capabilities lists below. A deterministic gate checks every "
        "one of these after you answer and tells you exactly what to fix if something slips through."
    )

    allowed_facts_label = (
        "Allowed facts — a CEILING only: you must never exceed these numbers/claims, but you are "
        "not required to use any of them"
        if is_value_only
        else "Allowed facts (ONLY these numbers/claims are citable)"
    )

    lines: list[str] = []
    playbook_block = [
        "This run's viral playbook for this topic (winning hooks/formats/visual archetypes/numbers "
        "seen in the niche this week — for a value-only post, this IS your substrate; ground the "
        "whole asset in it):",
        _viral_playbook_section(viral_playbook, request.topic),
        "",
    ]
    if is_value_only:
        # Phase 5: the playbook becomes the PRIMARY substrate for a
        # value-only post — placed first, ahead of even the destination/
        # topic housekeeping lines.
        lines.extend(playbook_block)

    lines.extend(
        [
            f"Destination: {request.destination}",
            f"Topic: {request.topic}",
            f"ICP: {request.icp_text}",
            f"Pain: {request.pain}",
            f"Offer: {request.offer_text or 'none — value-only (far mapping distance: no product CTA)'}",
            f"Mapping distance: {request.mapping_distance} (value_only={request.value_only})",
            f"Post type: {request.post_type}",
            f"CTA class: {request.cta_class}; CTA text: {request.cta_text}",
            f"Pricing policy: {request.pricing_policy_line}",
            f"{allowed_facts_label}: {json.dumps(request.allowed_facts, ensure_ascii=False)}",
            f"Negative capabilities (never imply): {json.dumps(request.negative_capabilities, ensure_ascii=False)}",
            f"Hard excludes (never mention): {json.dumps(request.hard_excludes, ensure_ascii=False)}",
            f"Disclosure requirement: {request.disclosure_requirement}",
            "",
            "Destination platform skeleton (style_guide.yaml — a MENU of beats to draw from, not a "
            "form to fill in; deviate from it in at least one visible way):",
            yaml.safe_dump(skeleton, allow_unicode=True, sort_keys=False),
            "",
        ]
    )
    if is_value_only:
        lines.append(
            "This is a VALUE-ONLY trend post: do not mention the brand, its products, or any brand "
            "URL anywhere in the copy. The @hypedigitaly handle appears only as a small visual "
            f'watermark (image direction), and the "{AI_DISCLOSURE_LINE}" disclosure line is still '
            "mandatory in the caption."
        )
        lines.append("")
    elif request.post_type == "playbook":
        lines.append(
            "This is a PLAYBOOK/lead-magnet post: your one ask (CTA) must be a comment-keyword "
            "lead-magnet ask (e.g. \"Comment 'WORD' and I'll send you the prompt set\") — not a link, "
            "not a generic follow ask."
        )
        lines.append("")

    if not is_value_only:
        lines.extend(playbook_block)

    exemplar_block = _load_exemplar_block(
        request.exemplar_pool_paths, request.excerpt_refs,
        exemplar_base_dir=exemplar_base_dir, excerpt_resolver=excerpt_resolver,
    )
    if exemplar_block:
        lines.append(exemplar_block)
        lines.append("")

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


def _carousel_deficiency(slides: list[dict[str, str]] | None) -> str | None:
    """Returns a human-readable deficiency reason, or ``None`` when
    ``slides`` satisfies the style guide's carousel contract: at least
    :data:`MIN_CAROUSEL_SLIDES` slides, one of which is the closing
    ``role == "end_card"``. Never checks an upper bound — the schema hint
    already asks for at most 10, and an over-long response is not the
    defect this check exists for."""
    if not slides:
        return "no slides returned for a carousel destination"
    if len(slides) < MIN_CAROUSEL_SLIDES:
        return f"only {len(slides)} slides returned (style guide requires at least {MIN_CAROUSEL_SLIDES}, including an end_card)"
    if not any(s.get("role") == "end_card" for s in slides):
        return "no slide has role='end_card' (style guide requires a closing end-card slide)"
    return None


# ---------------------------------------------------------------------------
# W8-10 Phase 1 — the numbered-promise hard gate (marketer-audit finding:
# a "6 prompts" cover delivering 1 prompt is trust-damaging; a generic
# short/incomplete carousel still ships with a trace note, but a BROKEN
# NUMBERED PROMISE never should). Distinct from — and additional to —
# ``_carousel_deficiency`` above: this can hard-fail the asset to "held"
# even when the generic slide-count/end-card contract is satisfied.
# ---------------------------------------------------------------------------

_NUMBERED_PROMISE_RE = re.compile(
    r"\b(\d+)\s+(prompts?|steps?|tools?|ways?|apps?|tips?)\b", re.IGNORECASE
)


def _numbered_promise(headline: str, slides: list[dict[str, str]] | None) -> tuple[int, str] | None:
    """Returns ``(N, matched phrase)`` for the first numbered promise found
    in the headline or the cover slide's title — ``None`` when no such
    promise is made at all."""
    texts = [headline or ""]
    if slides:
        for slide in slides:
            if slide.get("role") == "cover":
                texts.append(slide.get("title") or "")
                break
    for text in texts:
        match = _NUMBERED_PROMISE_RE.search(text)
        if match:
            return int(match.group(1)), match.group(0)
    return None


def _content_slide_count(slides: list[dict[str, str]] | None) -> int:
    if not slides:
        return 0
    return sum(1 for s in slides if s.get("role") not in ("cover", "end_card"))


def _numbered_promise_deficiency(headline: str, slides: list[dict[str, str]] | None) -> str | None:
    """Returns a human-readable deficiency reason when the headline/cover
    promises "N <plural noun>" (prompts/steps/tools/ways/apps/tips) but the
    carousel delivers fewer than N content slides (every slide that is
    neither the cover nor the end_card) — ``None`` when there is no numbered
    promise at all, or the promise is honoured."""
    promise = _numbered_promise(headline, slides)
    if promise is None:
        return None
    count, phrase = promise
    delivered = _content_slide_count(slides)
    if delivered < count:
        return (
            f'headline/cover promises "{phrase}" ({count}) but only {delivered} content slide(s) were '
            "delivered — numbered-promise hard gate"
        )
    return None


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
        trace: Any = None,
        stage: str = "copy",
        exemplar_base_dir: Path | None = None,
        excerpt_resolver: Callable[[str], str | None] | None = None,
    ) -> None:
        self.llm_client = llm_client
        self.style_guide = style_guide or {}
        self.viral_playbook = viral_playbook
        self.brand_identity_one_liner = brand_identity_one_liner
        self.node_name = node_name
        # W8-9 carousel-completeness fix — ``trace`` is optional (``None``
        # in every test that constructs this provider directly without a
        # live pipeline run, matching ``_build_copy_provider``'s own
        # None-safety note) so the corrective retry itself never needs one.
        self.trace = trace
        self.stage = stage
        # W8-10 Phase 1 — exemplar/excerpt injection: both optional and
        # ``None``-safe (every test that constructs this provider directly
        # without wiring a real run's config dir / store just gets no
        # exemplar block, exactly like today).
        self.exemplar_base_dir = exemplar_base_dir
        self.excerpt_resolver = excerpt_resolver

    def generate(self, request: CopyRequest) -> CopyResult | None:
        system, user_content, schema_hint = _build_openrouter_prompt(
            request, style_guide=self.style_guide, viral_playbook=self.viral_playbook,
            brand_identity_one_liner=self.brand_identity_one_liner,
            exemplar_base_dir=self.exemplar_base_dir, excerpt_resolver=self.excerpt_resolver,
        )
        try:
            data = self.llm_client.call_json(
                self.node_name, system=system, user_parts=user_content, schema_hint=schema_hint,
                purpose=f"N-C copywriter — {request.destination} copy for {request.cluster_key} (attempt {request.attempt})",
            )
        except LlmError as exc:
            raise CopyProviderError(f"openrouter copywriter: {exc}") from exc
        result = _parse_openrouter_response(data)

        if request.destination not in _CAROUSEL_DESTINATIONS:
            return result
        deficiency = _carousel_deficiency(result.slides)
        promise_deficiency = _numbered_promise_deficiency(result.headline, result.slides)
        if deficiency is None and promise_deficiency is None:
            return result

        # One corrective retry mentioning the exact deficiency/deficiencies.
        deficiency_texts = [d for d in (deficiency, promise_deficiency) if d is not None]
        corrective_content = (
            f"{user_content}\n\nYour previous response was DEFICIENT: {'; '.join(deficiency_texts)}. Return a "
            "corrected JSON response with the SAME schema that fixes this exactly: produce between "
            f"{MIN_CAROUSEL_SLIDES} and 10 slides total, with exactly one slide having "
            "role='end_card' as the final slide, and enough content slides (neither cover nor "
            "end_card) to honour any number your headline or cover title promises."
        )
        try:
            data2 = self.llm_client.call_json(
                self.node_name, system=system, user_parts=corrective_content, schema_hint=schema_hint,
                purpose=(
                    f"N-C copywriter — {request.destination} copy for {request.cluster_key} "
                    f"(attempt {request.attempt}, carousel-completeness corrective retry)"
                ),
            )
            retried = _parse_openrouter_response(data2)
        except LlmError:
            # The retry call itself failed. A generic (non-numbered-promise)
            # deficiency still never hard-fails -- keep the original result.
            # A numbered-promise deficiency DOES hard-fail even here: we
            # cannot verify the promise was fixed, and shipping "6 prompts"
            # with 1 delivered is the exact trust-damaging defect this gate
            # exists to stop.
            if promise_deficiency is not None:
                if self.trace is not None:
                    self.trace.decision(
                        self.stage,
                        decision=(
                            f"numbered-promise hard gate for {request.asset_id}: {promise_deficiency} — "
                            "corrective retry itself failed, held rather than shipping the broken promise"
                        ),
                        rule="W8-10 numbered-promise hard gate: HARD-fail to held, never accept-with-note",
                    )
                return None
            if self.trace is not None:
                self.trace.decision(
                    self.stage,
                    decision=(
                        f"carousel completeness corrective retry failed for {request.asset_id}: {deficiency} "
                        "— accepted with the original deficient slides"
                    ),
                    rule="W8-9 carousel completeness: accept-with-trace-note, never a hard fail",
                )
            return result

        promise_deficiency2 = _numbered_promise_deficiency(retried.headline, retried.slides)
        if promise_deficiency2 is not None:
            if self.trace is not None:
                self.trace.decision(
                    self.stage,
                    decision=(
                        f"numbered-promise hard gate for {request.asset_id}: {promise_deficiency2} persisted "
                        "after 1 corrective retry — HARD-fail to held, never accept-with-note"
                    ),
                    rule="W8-10 numbered-promise hard gate: HARD-fail to held, never accept-with-note",
                )
            return None

        deficiency2 = _carousel_deficiency(retried.slides)
        if deficiency2 is not None and self.trace is not None:
            self.trace.decision(
                self.stage,
                decision=(
                    f"carousel completeness deficiency persisted after 1 corrective retry for "
                    f"{request.asset_id}: {deficiency2} — accepted with trace note, not a hard fail"
                ),
                rule="W8-9 carousel completeness: accept-with-trace-note, never a hard fail",
            )
        return retried


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
    # W8-9 (marketer-audit finding): instagram_feed is a CAROUSEL destination
    # (style_guide.yaml's own carousel spec is injected alongside this) —
    # ``no_product_depiction`` contradicted W8-9 policy and the stale
    # "static-image post" format never matched what the copywriter was
    # actually asked to produce here.
    "instagram_feed": {
        "headline_max_words": 12,
        "caption_max_chars": 2200,
        "format": "carousel post",
        "people_free_composition": True,
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
    language: str = "en",
    post_type: str = "promotional",
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
        language=language,
        post_type=post_type,
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


# ---------------------------------------------------------------------------
# W8-10 Phase 2 — the humanness critic (new node N-F, EN). Runs AFTER the
# claim gate passes, BEFORE the asset is returned as "gated-pass". Two
# layers: a deterministic $0 regex pre-filter first (catches ~80% of the
# slop-tell/rhythm defects for free), then a config-gated LLM rewrite pass
# that is BLIND to the brief/style guide — it sees only the finished copy,
# the platform name, and sibling assets from the same run (the only way to
# catch cross-asset repetition, e.g. the live-run defect of "creators are
# reporting..." used 5x across 4 assets). The rewrite re-enters
# ``run_claim_gate``; a rewrite that fails the gate is discarded and the
# original gated copy ships — a critic failure never loses a shippable asset.
# ---------------------------------------------------------------------------

_SLOP_TELL_RE = re.compile(
    r"\b(actually|quietly|in the space|drowning in|isn't just|creators are reporting|game.?chang\w*|delve)\b",
    re.IGNORECASE,
)
_TRICOLON_RE = re.compile(r",\s+[^,.\n]+,\s+and\s+[^,.\n]+")
_ANTITHESIS_RE = re.compile(
    r"\b(isn't|is not|aren't|wasn't|weren't)\b[^.?!\n]{0,60}\b(it's|it is|they're|they are|that's)\b",
    re.IGNORECASE,
)
_EM_DASH_DENSITY_PER_WORD = 1 / 150  # style guide: at most 1 em-dash per 150 words

HUMANNESS_CRITIC_DEFAULT_MAX_TOKENS = 2000


def humanness_prefilter(text: str) -> list[str]:
    """Deterministic, $0 slop-tell/rhythm pre-filter (copywriter-audit
    Phase 2) over one asset's full text. Returns a list of human-readable
    findings; an empty list means nothing tripped. Never blocks anything by
    itself — findings feed the LLM critic as extra context (or are simply
    absent when everything is clean, saving the critic no time either way:
    per config, it still runs once per gated-pass asset)."""
    findings: list[str] = []
    if not text or not text.strip():
        return findings

    words = text.split()
    word_count = max(1, len(words))

    slop_hits = sorted({m.group(0).lower() for m in _SLOP_TELL_RE.finditer(text)})
    for hit in slop_hits:
        findings.append(f'slop-tell phrase found: "{hit}"')

    em_dash_count = text.count("—")
    if em_dash_count and (em_dash_count / word_count) > _EM_DASH_DENSITY_PER_WORD:
        findings.append(
            f"em-dash density too high: {em_dash_count} em-dash(es) across {word_count} words "
            "(style guide: at most 1 per 150 words)"
        )

    tricolon_hits = _TRICOLON_RE.findall(text)
    if tricolon_hits:
        findings.append(f'tricolon pattern (", X, and Y") found {len(tricolon_hits)} time(s)')

    antithesis_hits = _ANTITHESIS_RE.findall(text)
    if len(antithesis_hits) > 1:
        findings.append(f"X-not-Y antithesis shape used {len(antithesis_hits)} times (voice rule: at most once)")

    return findings


def _full_asset_text(result: CopyResult) -> str:
    """The complete rendered text of one asset — headline, caption, and
    every slide's title/body — for the pre-filter and for the sibling-
    repetition context handed to the critic."""
    parts = [result.headline or "", result.caption or ""]
    for slide in result.slides or []:
        parts.append(str(slide.get("title") or ""))
        parts.append(str(slide.get("body") or ""))
    return "\n".join(p for p in parts if p)


_HUMANNESS_CRITIC_RUBRIC = (
    "1. Named, first-person singular speaker voice — a real person talking, not a brand.\n"
    "2. Concrete, specific opening grounded in something real — no vague scene-setting, no "
    "fabricated first-person anecdote presented as fact.\n"
    "3. Rhythm: at least 3 sentences under 6 words; no two consecutive sentences share the same "
    "grammatical shape.\n"
    "4. At most one antithesis (\"it's not X, it's Y\") in the whole asset.\n"
    "5. At most one em-dash per 150 words; no parenthetical pairs of em-dashes.\n"
    "6. No three-item parallel lists in prose (the \", X, and Y\" shape).\n"
    "7. Any borrowed/trend number is attributed exactly once, as a single line at the very END — "
    "never inline, never explaining the compliance reasoning to the reader.\n"
    "8. Exactly one concrete, usable artifact (a verbatim prompt/search string/tool+setting) — "
    "abstract nouns like workflow/system/layer/motion/engine do not count.\n"
    "9. Exactly one ask (CTA); a P.S. only if it carries genuinely new information.\n"
    "10. No repeated phrase or structure across the sibling assets shown to you below — the same "
    "hedge phrase used across multiple assets in one run is an automatic fail.\n"
    "11. The swap test: replace the product/brand name with a random competitor's — if nothing "
    "breaks and the post still reads the same, it fails.\n"
    "12. Reads like one human actually wrote it in one sitting — not a template filled in."
)


def _build_humanness_critic_prompt(
    *, platform: str, asset_payload: dict[str, Any], sibling_texts: list[str], findings: list[str]
) -> tuple[str, str, str]:
    """Returns ``(system, user_content, schema_hint)``. Deliberately BLIND
    to the brief and the style guide — the critic sees only the finished
    copy, the platform name, and sibling assets from this same run."""
    system = (
        "You are a native-speaker editor who hates marketing copy. You were NOT given the brief, the "
        "brand's style guide, or any context about what this post is supposed to achieve — you judge "
        "ONLY whether it reads like a real human wrote it, against the rubric below. Your job is to "
        "REWRITE the asset when it fails the rubric, not to score it: return the full corrected asset "
        "in the exact same JSON shape you were given, changing only what needs to change. If the asset "
        "already passes every rubric item, return it unchanged.\n\n"
        f"Rubric:\n{_HUMANNESS_CRITIC_RUBRIC}"
    )
    lines = [f"Platform: {platform}", "", "Finished asset (JSON):", json.dumps(asset_payload, ensure_ascii=False, indent=2)]
    if findings:
        lines.append("")
        lines.append("A deterministic pre-filter already flagged these (fix them too, if still present):")
        lines.extend(f"- {f}" for f in findings)
    if sibling_texts:
        lines.append("")
        lines.append(
            "Other assets already finished in this same run — check rubric item 10 (cross-asset "
            "repetition) against them:"
        )
        for i, sib in enumerate(sibling_texts, start=1):
            lines.append(f"--- sibling asset {i} ---")
            lines.append(sib)
    schema_hint = (
        'Schema: same JSON shape as the finished asset shown to you (headline, caption, '
        'slides (if present), image_direction).'
    )
    return system, "\n".join(lines), schema_hint


def apply_humanness_critic(
    result: CopyResult,
    request: CopyRequest,
    *,
    llm_client: LlmClient | None,
    enabled: bool = True,
    sibling_texts: list[str] | None = None,
    snapshot: ClaimSnapshot,
    hard_excludes: dict[str, ResolvedList] | None = None,
    trace: Any = None,
    stage: str = "copy",
    node_name: str = "humanness_critic",
) -> CopyResult:
    """Runs the N-F humanness critic on one already claim-gate-passed asset.
    No-op (returns ``result`` unchanged) when disabled or when there is no
    LLM client at all (``InteractiveFileProvider``/``OpenAICompatibleProvider``
    runs, and every existing test that never wires an LLM client) — this is
    a pure addition, never a new failure surface for a non-LLM copy path."""
    if not enabled or llm_client is None:
        return result

    findings = humanness_prefilter(_full_asset_text(result))

    asset_payload: dict[str, Any] = {"headline": result.headline, "caption": result.caption, "image_direction": result.image_brief}
    if result.slides is not None:
        asset_payload["slides"] = result.slides

    system, user_content, schema_hint = _build_humanness_critic_prompt(
        platform=request.destination, asset_payload=asset_payload,
        sibling_texts=sibling_texts or [], findings=findings,
    )
    override_tokens = llm_client.config.override_for(node_name).max_tokens
    max_tokens = override_tokens if override_tokens is not None else HUMANNESS_CRITIC_DEFAULT_MAX_TOKENS
    try:
        data = llm_client.call_json(
            node_name, system=system, user_parts=user_content, schema_hint=schema_hint, max_tokens=max_tokens,
            purpose=f"N-F humanness critic — {request.destination} copy for {request.cluster_key}",
        )
    except LlmError as exc:
        if trace is not None:
            trace.decision(
                stage,
                decision=f"humanness critic call failed for {request.asset_id}: {exc} — kept the original gated copy",
                rule="W8-10 N-F: a critic failure never loses a shippable asset",
            )
        return result

    rewritten = _parse_openrouter_response(data)
    verdict = run_claim_gate(
        headline=rewritten.headline, caption=rewritten.caption, image_brief=rewritten.image_brief,
        snapshot=snapshot, hard_excludes=hard_excludes, slides=rewritten.slides,
    )
    if verdict.verdict != "pass":
        if trace is not None:
            trace.decision(
                stage,
                decision=(
                    f"humanness critic rewrite for {request.asset_id} failed the claim gate on re-entry "
                    "— kept the original gated copy"
                ),
                rule="W8-10 N-F: rewrite must re-pass run_claim_gate; a gate-fail never loses a shippable asset",
            )
        return result

    if trace is not None:
        note = f" ({len(findings)} pre-filter finding(s))" if findings else ""
        trace.decision(
            stage, decision=f"humanness critic rewrote {request.asset_id}{note}",
            rule="W8-10 N-F: humanness critic runs after the claim gate, blind to brief/style guide",
        )
    return rewritten


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
    llm_client: LlmClient | None = None,
    humanness_critic_enabled: bool = True,
    sibling_texts: list[str] | None = None,
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
            final_result = apply_humanness_critic(
                result, current, llm_client=llm_client, enabled=humanness_critic_enabled,
                sibling_texts=sibling_texts, snapshot=snapshot, hard_excludes=hard_excludes,
                trace=trace, stage=stage,
            )
            if run_dir is not None and not is_file_backed_provider and final_result is not result:
                # The critic rewrote the shipped copy -- overwrite the
                # already-persisted response file so provenance reflects
                # what actually shipped, not the pre-critic draft.
                _persist_llm_copy_io(run_dir, current, final_result)
            return AssetCopyStatus(
                asset_id=current.asset_id, cluster_key=current.cluster_key, destination=current.destination,
                status="gated-pass", attempt=current.attempt,
                headline=final_result.headline, caption=final_result.caption, image_brief=final_result.image_brief,
                request_path=request_path_str, slides=final_result.slides,
            )

        failing_span_texts = [f"{s.field_name}: {s.kind} '{s.text}' — {s.reason}" for s in verdict.failing_spans]
        if current.attempt >= max_attempts:
            return AssetCopyStatus(
                asset_id=current.asset_id, cluster_key=current.cluster_key, destination=current.destination,
                status="blocked — claim gate (repair budget exhausted)", attempt=current.attempt,
                failing_spans=failing_span_texts, request_path=request_path_str,
            )
        current = replace(current, attempt=current.attempt + 1, prior_failing_spans=failing_span_texts)
