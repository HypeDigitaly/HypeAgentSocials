"""The four free Phase-1 collectors (ARCHITECTURE_PLAN.md §2.3).

Hacker News, Google News RSS, Hugging Face Hub and Product Hunt's public
feed — all zero-cost, no API keys, official APIs or feeds only (never
scraping, §2.4-§2.5). Transport is injected via the ``Fetcher`` protocol
(``base.py``) so every collector runs fully offline in tests against fixture
payloads.
"""

from __future__ import annotations

from hypeagent.collectors.base import CollectorRunResult, Fetcher, RawItem

__all__ = ["CollectorRunResult", "Fetcher", "RawItem"]
