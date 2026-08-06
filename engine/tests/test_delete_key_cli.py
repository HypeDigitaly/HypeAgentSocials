"""Tests for ``python -m hypeagent --delete-key <canonical_key>`` (§2.6)."""

from __future__ import annotations

from datetime import datetime

import yaml

from hypeagent import main as main_module
from hypeagent.store import NormalizedSignal, SpecialCategoryLexicon, Store


def test_delete_key_cli_removes_live_record_and_rewrites_archived_pack(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)

    store = Store.open(tmp_path / "logs", tmp_path / "secrets")
    try:
        normalized = NormalizedSignal(
            canonical_key="hacker_news:42", source="hacker_news", source_family="developer_technical_discourse",
            language="en", title="A launch worth reading about", excerpt="A launch worth reading about, in full",
            metrics={"score": 10}, raw_author_handle="somebody", near_dup_fingerprint="fp42", evidence_class="counted",
            injection_flagged=False, retrieval_time=datetime.now().astimezone(),
            canonical_link="https://news.ycombinator.com/item?id=42", domain="news.ycombinator.com", method="official API",
        )
        stored, _ = store.store_signal(normalized, run_id="run1", lexicon=SpecialCategoryLexicon(terms_by_category={}))
        assert stored

        pack_dir = tmp_path / "logs" / "runs" / "run1" / "pack"
        (pack_dir / "signals").mkdir(parents=True)
        signal_file = pack_dir / "signals" / "hacker_news_42.yaml"
        durable, verbatim = store.get_provenance("hacker_news:42")
        doc = {"canonical_key": "hacker_news:42", "durable": durable, "verbatim": verbatim}
        signal_file.write_text(yaml.safe_dump(doc, allow_unicode=True), encoding="utf-8")
        store.register_pack_keys(run_id="run1", pack_path=str(pack_dir), entries=[("hacker_news:42", str(signal_file))])
    finally:
        store.close()

    exit_code = main_module.main(["--delete-key", "hacker_news:42"])
    assert exit_code == 0

    out = capsys.readouterr().out
    assert "hacker_news:42" in out
    assert "packs_rewritten=1" in out

    rewritten = yaml.safe_load(signal_file.read_text(encoding="utf-8"))
    assert "deleted on request" in rewritten["verbatim"]["excerpt"]
    assert rewritten["durable"]["source"] == "hacker_news"

    store2 = Store.open(tmp_path / "logs", tmp_path / "secrets")
    try:
        assert store2.get_signal("hacker_news:42") is None
    finally:
        store2.close()
