"""Fail-closed config loading (ARCHITECTURE_PLAN.md §11.3; config/README.md).

Semantics, shared by every config artifact under ``config/``:

- **Missing or unreadable file = stop.** Raises :class:`ConfigError` naming
  the exact missing/unreadable item — this is a presence-and-syntax check
  only (§11.3); credential *validity* is a separate, later concern.
- **Present-but-empty lists = valid RESOLVED-EMPTY state.** "Missing is not
  the same as empty" (§6.3) — an empty list is a deliberate, safe statement
  of zero entries, never a gate-off signal.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

import yaml

ResolutionState = Literal["resolved", "resolved-empty"]


class ConfigError(Exception):
    """Raised for fail-closed config conditions: missing, unreadable, or unparseable."""


@dataclass(frozen=True)
class ResolvedList:
    """One config list, resolved to an explicit state.

    ``state`` is ``"resolved-empty"`` when the list is present but has zero
    entries, and ``"resolved"`` otherwise. There is deliberately no
    "unresolved" state here: reaching this point already means the file
    loaded and parsed, so unresolved conditions have already raised.
    """

    name: str
    values: list[Any]
    state: ResolutionState


def resolve_list(name: str, values: list[Any] | None) -> ResolvedList:
    values = list(values) if values is not None else []
    state: ResolutionState = "resolved-empty" if len(values) == 0 else "resolved"
    return ResolvedList(name=name, values=values, state=state)


def load_yaml_config(path: Path, *, name: str | None = None) -> dict[str, Any]:
    """Load one YAML config file, fail-closed.

    ``name`` is the human-facing identifier used in error messages; it
    defaults to the file's own name.
    """
    label = name or path.name
    if not path.exists():
        raise ConfigError(f"missing config item: {label} (expected at {path})")
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ConfigError(f"unreadable config item: {label} ({path}): {exc}") from exc
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ConfigError(f"unparseable config item: {label} ({path}): {exc}") from exc
    if data is None:
        data = {}
    if not isinstance(data, dict):
        raise ConfigError(f"malformed config item: {label} ({path}): expected a mapping at top level")
    return data


_HARD_EXCLUDE_KEYS = ("topics", "framings", "claim_types", "do_not_mention_entities")


def load_hard_excludes(config_dir: Path) -> dict[str, ResolvedList]:
    """Load ``config/hard_excludes.yaml`` (§6.3 F-J, config/README.md).

    Missing/unreadable file -> ``ConfigError`` naming ``hard_excludes.yaml``
    (this is degrade condition 5 of §6.5 upstream of this loader; the caller
    decides what to do with the raised error). Present-but-empty lists
    resolve to ``RESOLVED-EMPTY``, a valid state.
    """
    path = config_dir / "hard_excludes.yaml"
    data = load_yaml_config(path, name="hard_excludes.yaml")
    excludes = data.get("hard_excludes")
    if excludes is None:
        excludes = {}
    if not isinstance(excludes, dict):
        raise ConfigError(
            f"malformed config item: hard_excludes.yaml ({path}): "
            "'hard_excludes' key must be a mapping"
        )
    return {key: resolve_list(key, excludes.get(key)) for key in _HARD_EXCLUDE_KEYS}


@dataclass(frozen=True)
class ThemeConfig:
    """Phase-1 resolved config bundle. Grows as later phases add sources."""

    hard_excludes: dict[str, ResolvedList] = field(default_factory=dict)
    fingerprint: str = ""


def _fingerprint(hard_excludes: dict[str, ResolvedList]) -> str:
    payload = json.dumps(
        {key: sorted(map(str, item.values)) for key, item in hard_excludes.items()},
        sort_keys=True,
        ensure_ascii=False,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def load_theme_config(config_dir: Path) -> ThemeConfig:
    """Load the Phase-1 config surface, fail-closed.

    Raises :class:`ConfigError` naming the exact missing/unreadable item if
    any required config file cannot be resolved.
    """
    hard_excludes = load_hard_excludes(config_dir)
    return ThemeConfig(hard_excludes=hard_excludes, fingerprint=_fingerprint(hard_excludes))
