"""The OpenRouter LLM client (W8-9 Q2; FLOW_MAP.md §3's four LLM nodes all
share this one client): ``anthropic/claude-sonnet-5`` via
``POST {base_url}/chat/completions``, JSON-contract calls with a bounded
corrective retry, vision content-parts, and per-run budget enforcement.

**Request/response shapes below are live-verified (2026-08-07) against the
real OpenRouter API, not assumed** — see the inline notes at each shape
decision:

- ``response_format: {"type": "json_object"}`` IS honoured by
  ``anthropic/claude-sonnet-5`` via OpenRouter: a live call with this field
  set returned ``choices[0].message.content`` as a bare, directly
  ``json.loads``-able JSON object (no prose, no code fence). Sent on every
  call regardless, since it costs nothing when honoured and this module's
  own :func:`_parse_json_content` still has to be robust to a model that
  ignores it (verified separately: a live call WITHOUT
  ``response_format`` wrapped its JSON in explanatory prose plus a
  ```` ```json ... ``` ```` fence — exactly the shape the robust extraction
  path below exists for).
- Vision content-parts ARE accepted in the shape the OpenAI-compatible
  chat-completions surface documents: ``{"type": "image_url",
  "image_url": {"url": "data:<mime>;base64,<...>"}}`` alongside a
  ``{"type": "text", ...}`` part in the same user message's ``content``
  list — verified live with a 1x1 PNG data URL.
- ``usage`` on every OpenRouter response carries ``prompt_tokens``,
  ``completion_tokens``, ``total_tokens``, AND (OpenRouter-specific,
  observed on every one of this milestone's live calls) a direct ``cost``
  field in USD — :func:`LlmClient._record_spend` prefers that reported
  figure over the estimated-from-tokens fallback whenever it is present.

Money/telemetry discipline mirrors ``media_gen.KieClient`` exactly: the API
key is used only to build the ``Authorization`` header for the raw HTTP
call and is never part of the traced ``request``/``response`` dicts (both
built via :meth:`hypeagent.trace.TraceWriter`'s allowlist redaction); a
defensive scrub additionally strips the literal key value out of any
exception text before it is raised or traced, in case a transport error
ever echoes the outgoing URL/headers back.

**Third-party verbatim text may reach the *prompt* sent to OpenRouter**
(HARD CONSTRAINT: Virlo captions/panel texts are a research-artifact class,
not a trace class) but this module never puts prompt or response CONTENT
into the trace — only counts, character/byte lengths, and sha256 hashes
(``CALL_ALLOWED_KEYS`` / ``RESPONSE_ALLOWED_KEYS`` below), exactly the
discipline ``media_gen.KieClient.create_task`` already established for
image prompts.
"""

from __future__ import annotations

import base64
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from hypeagent.collectors.base import FetchError, Fetcher
from hypeagent.config_load import LlmConfig
from hypeagent.trace import TraceWriter

CALL_ALLOWED_KEYS = {
    "model", "node", "max_tokens", "temperature", "message_count", "has_image",
    "prompt_sha256", "prompt_chars", "response_format",
}
RESPONSE_ALLOWED_KEYS = {
    "finish_reason", "prompt_tokens", "completion_tokens", "total_tokens",
    "content_sha256", "content_len", "error", "id",
}


class LlmError(Exception):
    """Base class for every genuine LLM-call failure this module raises.
    Callers (stages) catch this to degrade — never let it propagate as an
    unhandled exception that fails the run (§ every LLM node's failure
    behaviour in FLOW_MAP.md §3)."""


class LlmBudgetExceededError(LlmError):
    """Either the per-run USD cap or the per-run call cap has already been
    reached; no HTTP call was made for this attempt."""


class LlmTransportError(LlmError):
    """The HTTP call itself did not complete (network error, timeout)."""


class LlmApiError(LlmError):
    """A clean HTTP response reporting a definite failure (non-2xx status,
    an OpenRouter ``error`` object, or unparseable response JSON)."""


class LlmParseError(LlmError):
    """The model's ``content`` could not be parsed as a single JSON object,
    even after the one corrective retry."""


# ---------------------------------------------------------------------------
# Content-part helpers (vision).
# ---------------------------------------------------------------------------

_MIME_BY_SUFFIX = {
    ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
    ".webp": "image/webp", ".gif": "image/gif",
}


def guess_image_mime(path: Path) -> str:
    return _MIME_BY_SUFFIX.get(Path(path).suffix.lower(), "image/jpeg")


def text_content_part(text: str) -> dict[str, Any]:
    return {"type": "text", "text": text}


def image_content_part(data: bytes, *, mime: str = "image/jpeg") -> dict[str, Any]:
    """Build one vision content-part from raw image bytes — the exact shape
    verified live (module docstring)."""
    encoded = base64.b64encode(data).decode("ascii")
    return {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{encoded}"}}


def image_content_part_from_file(path: Path) -> dict[str, Any]:
    path = Path(path)
    return image_content_part(path.read_bytes(), mime=guess_image_mime(path))


# ---------------------------------------------------------------------------
# Robust JSON extraction — the "prompt + robust extraction" half of the
# JSON contract (module docstring: a model that ignores ``response_format``
# still has to be handled).
# ---------------------------------------------------------------------------

_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)


def _extract_first_json_object(text: str) -> dict[str, Any] | None:
    """Scan for the first balanced ``{...}`` block (string- and
    escape-aware, so a brace inside a quoted string never miscounts depth)
    and try to parse it. Returns ``None`` if nothing balanced parses to a
    JSON object."""
    start = text.find("{")
    while start != -1:
        depth = 0
        in_string = False
        escape = False
        for i in range(start, len(text)):
            ch = text[i]
            if in_string:
                if escape:
                    escape = False
                elif ch == "\\":
                    escape = True
                elif ch == '"':
                    in_string = False
                continue
            if ch == '"':
                in_string = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    candidate = text[start : i + 1]
                    try:
                        parsed = json.loads(candidate)
                    except json.JSONDecodeError:
                        break
                    if isinstance(parsed, dict):
                        return parsed
                    break
        start = text.find("{", start + 1)
    return None


def _parse_json_content(content: str) -> tuple[dict[str, Any] | None, str | None]:
    """Try, in order: (1) the whole content as JSON, (2) the content of a
    ```` ```json ... ``` ```` fence as JSON, (3) the first balanced
    ``{...}`` block found anywhere in the text. Returns ``(parsed, None)``
    on success or ``(None, error_message)`` on failure."""
    if not content or not content.strip():
        return None, "empty response content"

    stripped = content.strip()
    try:
        parsed = json.loads(stripped)
        if isinstance(parsed, dict):
            return parsed, None
        return None, f"top-level JSON value is a {type(parsed).__name__}, not an object"
    except json.JSONDecodeError:
        pass

    fence_match = _FENCE_RE.search(content)
    if fence_match:
        try:
            parsed = json.loads(fence_match.group(1).strip())
            if isinstance(parsed, dict):
                return parsed, None
        except json.JSONDecodeError:
            pass

    obj = _extract_first_json_object(content)
    if obj is not None:
        return obj, None
    return None, "no parseable JSON object found in response content"


def _redact_secret(text: str, secret: str | None) -> str:
    if not secret:
        return text
    return text.replace(secret, "***REDACTED***")


@dataclass
class _LlmCallResult:
    content: str
    usage: dict[str, Any]


# ---------------------------------------------------------------------------
# The client.
# ---------------------------------------------------------------------------


class LlmClient:
    """One OpenRouter chat-completions client, shared across every LLM node
    in a single pipeline invocation so the per-run budget (``per_run_usd_cap``
    / ``per_run_call_cap``) is enforced across ALL of them, not per-node
    (``stages.py`` constructs exactly one instance per run and caches it on
    ``RunContext.extra``)."""

    def __init__(
        self,
        *,
        config: LlmConfig,
        fetcher: Fetcher,
        api_key: str,
        trace: TraceWriter,
        stage: str = "analysis",
    ) -> None:
        self.config = config
        self.fetcher = fetcher
        self._api_key = api_key
        self.trace = trace
        self.stage = stage
        self.call_count = 0
        self.spent_usd = 0.0

    @property
    def _url(self) -> str:
        return f"{self.config.base_url.rstrip('/')}/chat/completions"

    def set_stage(self, stage: str) -> None:
        """Later stages sharing this client (copy, media/prompt-craft) call
        this so subsequent trace events land under the right stage name
        while the same budget accumulator keeps counting."""
        self.stage = stage

    def budget_remaining(self) -> tuple[int, float]:
        """``(calls_remaining, usd_remaining)`` — informational, for a
        caller that wants to decide whether it is worth building a prompt
        at all before calling in."""
        calls_remaining = max(0, self.config.per_run_call_cap - self.call_count)
        usd_remaining = max(0.0, self.config.per_run_usd_cap - self.spent_usd)
        return calls_remaining, usd_remaining

    def _check_budget(self, node_name: str) -> None:
        if self.call_count >= self.config.per_run_call_cap:
            raise LlmBudgetExceededError(
                f"{node_name}: per-run LLM call cap reached ({self.config.per_run_call_cap} calls) "
                "— no more LLM calls this run"
            )
        if self.spent_usd >= self.config.per_run_usd_cap:
            raise LlmBudgetExceededError(
                f"{node_name}: per-run LLM budget cap reached (${self.config.per_run_usd_cap:.2f}) "
                "— no more LLM calls this run"
            )

    # -- the JSON contract -------------------------------------------------

    def call_json(
        self,
        node_name: str,
        *,
        system: str,
        user_parts: str | list[dict[str, Any]],
        schema_hint: str = "",
        max_tokens: int | None = None,
        temperature: float | None = None,
        purpose: str = "",
    ) -> dict[str, Any]:
        """Call the model and return a parsed JSON object.

        On an unparseable/schema-miss response: ONE corrective retry
        (append the model's own bad output plus the parse error and "return
        only JSON" to the conversation), then raise :class:`LlmParseError`.
        Raises :class:`LlmBudgetExceededError` without ever touching the
        network if the run's budget is already exhausted; raises
        :class:`LlmTransportError` / :class:`LlmApiError` for transport/API
        failures. All four are subclasses of :class:`LlmError` — callers
        should catch that base class to degrade.
        """
        override = self.config.override_for(node_name)
        model = override.model or self.config.model
        temp = (
            temperature
            if temperature is not None
            else (override.temperature if override.temperature is not None else self.config.default_temperature)
        )
        tokens = (
            max_tokens
            if max_tokens is not None
            else (override.max_tokens if override.max_tokens is not None else self.config.default_max_tokens)
        )

        system_full = system
        if schema_hint:
            system_full = (
                f"{system}\n\nRespond with ONLY a single JSON object — no prose, no markdown code "
                f"fences. {schema_hint}"
            )

        has_image = isinstance(user_parts, list) and any(
            isinstance(p, dict) and p.get("type") == "image_url" for p in user_parts
        )
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": system_full},
            {"role": "user", "content": user_parts},
        ]

        result = self._call_once(
            node_name=node_name, model=model, messages=messages, max_tokens=tokens, temperature=temp,
            has_image=has_image, purpose=purpose or node_name, attempt=1,
        )
        parsed, error = _parse_json_content(result.content)
        if parsed is not None:
            return parsed

        # ONE corrective retry — the model sees its own bad output plus the
        # parse error, and is told again to return only JSON.
        messages.append({"role": "assistant", "content": result.content})
        messages.append(
            {
                "role": "user",
                "content": (
                    "Your previous response could not be parsed as a single JSON object. "
                    f"Parse error: {error}. Return ONLY the corrected JSON object — no prose, "
                    "no markdown code fences, no explanation."
                ),
            }
        )
        result2 = self._call_once(
            node_name=node_name, model=model, messages=messages, max_tokens=tokens, temperature=temp,
            has_image=has_image, purpose=f"{purpose or node_name} (corrective retry)", attempt=2,
        )
        parsed2, error2 = _parse_json_content(result2.content)
        if parsed2 is not None:
            return parsed2
        raise LlmParseError(
            f"{node_name}: model output not parseable as a JSON object after 1 corrective retry: {error2}"
        )

    # -- one raw HTTP round trip -------------------------------------------

    def _call_once(
        self,
        *,
        node_name: str,
        model: str,
        messages: list[dict[str, Any]],
        max_tokens: int,
        temperature: float,
        has_image: bool,
        purpose: str,
        attempt: int,
    ) -> _LlmCallResult:
        self._check_budget(node_name)

        body_dict = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "response_format": {"type": "json_object"},
        }
        body = json.dumps(body_dict).encode("utf-8")
        prompt_chars = sum(len(json.dumps(m.get("content"), ensure_ascii=False)) for m in messages)

        call_seq = self.trace.api_call(
            self.stage,
            platform="openrouter",
            endpoint=self._url,
            method="POST",
            request={
                "model": model, "node": node_name, "max_tokens": max_tokens, "temperature": temperature,
                "message_count": len(messages), "has_image": has_image,
                "prompt_sha256": hashlib.sha256(body).hexdigest(), "prompt_chars": prompt_chars,
                "response_format": "json_object",
            },
            allowed_keys=CALL_ALLOWED_KEYS,
            attempt=attempt,
            purpose=purpose,
        )
        headers = {"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"}
        try:
            response = self.fetcher.fetch(self._url, headers=headers, method="POST", body=body)
        except FetchError as exc:
            message = _redact_secret(str(exc), self._api_key)
            self.trace.api_response(
                self.stage, seq_of_call=call_seq, status="error", latency_ms=0, bytes_=None,
                ids_returned=None, cost=None, outcome_class="transient",
                response_summary={"error": message}, allowed_keys={"error"},
            )
            raise LlmTransportError(f"{node_name}: {message}") from exc

        try:
            payload = json.loads(response.body)
        except (json.JSONDecodeError, TypeError) as exc:
            self.trace.api_response(
                self.stage, seq_of_call=call_seq, status=response.status, latency_ms=response.latency_ms,
                bytes_=len(response.body), ids_returned=None, cost=None, outcome_class="permanent-endpoint",
                response_summary={"error": "malformed JSON response"}, allowed_keys={"error"},
            )
            raise LlmApiError(f"{node_name}: malformed JSON response: {exc}") from exc

        error_obj = payload.get("error")
        if error_obj:
            message = _redact_secret(json.dumps(error_obj, ensure_ascii=False), self._api_key)
            self.trace.api_response(
                self.stage, seq_of_call=call_seq, status=response.status, latency_ms=response.latency_ms,
                bytes_=len(response.body), ids_returned=None, cost=None, outcome_class="permanent-endpoint",
                response_summary={"error": message}, allowed_keys={"error"},
            )
            raise LlmApiError(f"{node_name}: OpenRouter error: {message}")

        choices = payload.get("choices") or []
        content = ""
        finish_reason = None
        if choices and isinstance(choices[0], dict):
            message_obj = choices[0].get("message") or {}
            content = str(message_obj.get("content") or "")
            finish_reason = choices[0].get("finish_reason")
        usage = payload.get("usage") or {}
        content_bytes = content.encode("utf-8")

        self.trace.api_response(
            self.stage, seq_of_call=call_seq, status=response.status, latency_ms=response.latency_ms,
            bytes_=len(response.body), ids_returned=[payload["id"]] if payload.get("id") else [],
            cost=self._cost_dict(usage), outcome_class="ok" if response.status < 400 else "permanent-endpoint",
            response_summary={
                "finish_reason": finish_reason,
                "prompt_tokens": usage.get("prompt_tokens"),
                "completion_tokens": usage.get("completion_tokens"),
                "total_tokens": usage.get("total_tokens"),
                "content_sha256": hashlib.sha256(content_bytes).hexdigest(),
                "content_len": len(content_bytes),
            },
            allowed_keys=RESPONSE_ALLOWED_KEYS,
        )
        self._record_spend(usage)
        self.call_count += 1

        if response.status >= 400:
            raise LlmApiError(f"{node_name}: HTTP {response.status}")
        return _LlmCallResult(content=content, usage=usage)

    def _estimate_usd(self, usage: dict[str, Any]) -> float:
        prompt_tokens = usage.get("prompt_tokens") or 0
        completion_tokens = usage.get("completion_tokens") or 0
        return (
            (prompt_tokens / 1_000_000) * self.config.usd_per_1m_input_tokens
            + (completion_tokens / 1_000_000) * self.config.usd_per_1m_output_tokens
        )

    def _cost_dict(self, usage: dict[str, Any]) -> dict[str, Any]:
        return {
            "prompt_tokens": usage.get("prompt_tokens"),
            "completion_tokens": usage.get("completion_tokens"),
            "reported_usd": usage.get("cost"),
        }

    def _record_spend(self, usage: dict[str, Any]) -> None:
        """Prefer OpenRouter's own reported ``usage.cost`` (observed on
        every live verification call this milestone); fall back to the
        configured per-1M-token estimate when absent (e.g. a fixture in
        tests, or a future response shape change)."""
        estimated = self._estimate_usd(usage)
        reported = usage.get("cost")
        actual = float(reported) if isinstance(reported, (int, float)) else estimated
        self.spent_usd += actual
        self.trace.spend(self.stage, wallet="llm", expected=round(estimated, 6), ledger_recorded=round(actual, 6))
