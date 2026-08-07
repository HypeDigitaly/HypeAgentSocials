"""Tests for ``hypeagent.process_summary`` (RUN_TRACE_SPEC.md §6, W8-8):
the automatically-generated, human-readable ``process_summary.md`` and its
``python -m hypeagent --summarize <run_id>`` regeneration CLI."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from hypeagent import main as main_module
from hypeagent import media_gen, process_summary
from hypeagent.collectors.base import FixtureFetcher
from hypeagent.exit_codes import EXIT_CODE_MAP, ExitClass
from test_media_gen import (
    RESULT_IMAGE_URL,
    QueuedFetcher,
    _create_task_ok,
    _credit_balance,
    _image_response,
    _record_info_success,
)
from test_phase1_pipeline import _default_fixture_responses, _write_config
from test_resume import _resume_with_new_ctx, _run_once_with_ctx, _write_valid_response
from test_run import _write_minimal_config

FIXTURES = Path(__file__).parent / "fixtures"


def _write_config_with_virlo(tmp_path: Path) -> None:
    """The ordinary Phase-1/M3/M4 fixture config (``test_phase1_pipeline``'s
    own helper), plus a Virlo source enabled — for the one end-to-end test
    that exercises §3's Virlo-specific extraction block."""
    _write_config(tmp_path)
    theme_path = tmp_path / "config" / "themes" / "hypedigitaly.yaml"
    text = theme_path.read_text(encoding="utf-8")
    anchor = "      circuit_breaker_threshold: 2\nranking:\n"
    assert anchor in text, "test_phase1_pipeline._write_config's theme fixture shape changed"
    replacement = (
        "      circuit_breaker_threshold: 2\n"
        "    virlo:\n"
        "      enabled: true\n"
        "      family: short_form_trends\n"
        "      circuit_breaker_threshold: 2\n"
        "      budget_max_calls: 4\n"
        # This test exercises §3's theme-extraction block only (digest +
        # single-monitor read, pre-W8-9-Phase-2 shape) -- explicitly opt
        # back into the old always-on digest and opt OUT of the new
        # sub-path/media-download surface, so this fixture config (which
        # registers no /videos or /slideshows fixtures) keeps its exact
        # pre-Phase-2 behavior rather than picking up the new SourceConfig
        # defaults meant for production.
        "      trends_digest_enabled: true\n"
        "      subpath_page_cap: 0\n"
        "      media_download_cap: 0\n"
        "ranking:\n"
    )
    theme_path.write_text(text.replace(anchor, replacement), encoding="utf-8")
    (tmp_path / "secrets").mkdir(parents=True, exist_ok=True)
    (tmp_path / "secrets" / "virlo.key").write_text("virlo_test_key_value", encoding="utf-8")


def _virlo_fixture_responses() -> dict:
    return {
        "v1/trends/digest": _fr(FIXTURES / "virlo_trends_digest.json"),
        "v1/agents/9c96fddf-dc35-4be0-bbd9-12f4d22aea12": _fr(FIXTURES / "virlo_agent_monitor.json"),
    }


def _fr(path: Path):
    from hypeagent.collectors.base import FetchResponse

    return FetchResponse(status=200, headers={}, body=path.read_bytes(), latency_ms=4)


class TestProcessSummaryFullPipeline:
    def test_generated_at_run_end_with_all_sections_and_virlo_detail(self, tmp_path):
        _write_config_with_virlo(tmp_path)
        responses = dict(_default_fixture_responses())
        responses.update(_virlo_fixture_responses())
        fetcher = FixtureFetcher(responses=responses)
        run_id = "2026-08-10_psumA"
        ctx, run_dir, trace_path, exit_class_value = _run_once_with_ctx(tmp_path, fetcher, run_id)

        summary_path = run_dir / process_summary.PROCESS_SUMMARY_FILENAME
        assert summary_path.exists(), "process_summary.md must be generated automatically at run end"
        text = summary_path.read_text(encoding="utf-8")

        for heading in (
            "# Process Summary",
            "## Per-platform I/O",
            "## Per-source extraction",
            "## Ranking outcome",
            "## Copy I/O",
            "## Image generation",
            "## Spend summary",
            "## Data-hygiene footnote",
        ):
            assert heading in text, f"missing section: {heading}"

        assert "virlo" in text
        assert "Virlo — theme extraction detail" in text
        assert "AI Agents for Business Automation and Outbound Sales" in text
        assert "Claude Code for Development and Automation" in text
        assert "tactics" in text
        assert "why_it_works" in text
        assert "no model judgment" in text  # FIT_METHOD_LABEL verbatim, per RUN_TRACE_SPEC §6 item 4

        # Own trace link, present unconditionally.
        assert "../trace.md" in text
        # Redaction rules restated in the footnote.
        assert "Secrets never appear" in text

    def test_summarize_cli_regenerates_the_same_run(self, tmp_path):
        _write_config_with_virlo(tmp_path)
        responses = dict(_default_fixture_responses())
        responses.update(_virlo_fixture_responses())
        fetcher = FixtureFetcher(responses=responses)
        run_id = "2026-08-10_psumB"
        ctx, run_dir, trace_path, exit_class_value = _run_once_with_ctx(tmp_path, fetcher, run_id)

        summary_path = run_dir / process_summary.PROCESS_SUMMARY_FILENAME
        assert summary_path.exists()
        summary_path.unlink()
        assert not summary_path.exists()

        written = process_summary.generate_process_summary(
            run_id, config_dir=tmp_path / "config", logs_dir=tmp_path / "logs", secrets_dir=tmp_path / "secrets",
        )
        assert written == summary_path
        assert summary_path.exists()
        assert "# Process Summary" in summary_path.read_text(encoding="utf-8")


class TestProcessSummaryCopyAndMediaFidelity:
    def test_resume_shows_full_copy_text_and_exact_image_prompt(self, tmp_path):
        _write_config(tmp_path)
        fetcher = FixtureFetcher(responses=_default_fixture_responses())
        run_id = "2026-08-10_psumC"
        ctx, run_dir, trace_path, exit_class_value = _run_once_with_ctx(tmp_path, fetcher, run_id)

        summary_path = run_dir / process_summary.PROCESS_SUMMARY_FILENAME
        assert summary_path.exists()
        held_text = summary_path.read_text(encoding="utf-8")
        assert "held — awaiting operator copy" in held_text

        statuses = ctx.extra.get("copy_asset_statuses", [])
        held = next(s for s in statuses if s.status == "held — awaiting operator copy")

        _write_valid_response(
            run_dir / "copy_responses", held.asset_id, headline="AI agents are changing outbound sales"
        )
        secrets_dir = tmp_path / "secrets"
        secrets_dir.mkdir(parents=True, exist_ok=True)
        (secrets_dir / "kie.key").write_text("kie_test_secret_value", encoding="utf-8")

        kie_fetcher = QueuedFetcher(
            responses={
                "createTask": [_create_task_ok("task_psum_1")],
                "recordInfo": [_record_info_success("task_psum_1")],
                "chat/credit": [_credit_balance(100.0), _credit_balance(96.0)],
                RESULT_IMAGE_URL: [_image_response()],
            }
        )
        _resume_with_new_ctx(tmp_path, run_id, fetcher_factory=lambda: kie_fetcher, secrets_dir=secrets_dir)

        summary_text = summary_path.read_text(encoding="utf-8")
        assert "gated-pass" in summary_text
        # Own-authored copy shown in full (RUN_TRACE_SPEC §6 redaction boundary).
        assert "AI agents are changing outbound sales" in summary_text
        assert "See how small businesses use AI chatbots" in summary_text
        # Own-authored image prompt shown in full, exactly as generated (no
        # "reconstructed" fallback needed — this run persists prompt_full).
        assert "A calm, people-free office scene, no product depiction." in summary_text
        assert "no people" in summary_text
        assert "reconstructed from the copy response" not in summary_text
        # Secrets and provider URLs never leak into the summary.
        assert "kie_test_secret_value" not in summary_text
        assert RESULT_IMAGE_URL not in summary_text

    def test_media_section_reconstructs_full_prompt_for_old_provenance_missing_prompt_full(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _write_config(tmp_path)

        run_id = "2020-01-01_oldprompt"
        run_dir = tmp_path / "logs" / "runs" / run_id
        (run_dir / "pack" / "media").mkdir(parents=True)
        (run_dir / "copy_responses").mkdir(parents=True)

        image_brief = "A calm, people-free office scene, no product depiction."
        (run_dir / "copy_responses" / "ck1_linkedin.yaml").write_text(
            yaml.safe_dump({"headline": "H", "caption": "C", "image_brief": image_brief}), encoding="utf-8"
        )

        registry = media_gen.load_model_registry(tmp_path / "config" / "model_registry.yaml")
        composed = media_gen.compose_prompt(image_brief, registry)
        sha = media_gen.prompt_sha256(composed)

        provenance_doc = {
            "asset_id": "ck1_linkedin",
            "cluster_key": "ck1",
            "destination": "linkedin",
            "language": "en",
            "requested_route": "img-draft-nano-banana",
            "requested_model": "google/nano-banana",
            "delivered_route_state": "assumed-as-requested",
            "delivered_model": "google/nano-banana",
            "price_snapshot_date": "2026-08-07",
            "task_id": "task_old_1",
            "checksum_sha256": "deadbeef",
            "observed_cost_usd": 0.02,
            "image_path": str(run_dir / "pack" / "media" / "ck1_linkedin.png"),
            "prompt_pattern_version": 1,
            "attempt": 1,
            "created_at": "2020-01-01T00:00:00+00:00",
            "logo_overlay": "deferred to a later phase — this pack carries the raw generated image only",
            # deliberately no prompt_full / prompt_sha256 -- the pre-W8-8 shape.
        }
        (run_dir / "pack" / "media" / "ck1_linkedin.provenance.yaml").write_text(
            yaml.safe_dump(provenance_doc, allow_unicode=True), encoding="utf-8"
        )

        trace_lines = [
            {
                "ts": "2020-01-01T00:00:00.000+00:00", "run_id": run_id, "seq": 1, "stage": "run",
                "event": "run_start",
                "detail": {"mode": "interactive", "theme": "hypedigitaly", "config_fingerprint": None, "engine_version": "0.0.1", "caps_in_force": {}},
            },
            {
                "ts": "2020-01-01T00:00:01.000+00:00", "run_id": run_id, "seq": 2, "stage": "media",
                "event": "api_call",
                "detail": {
                    "platform": "kie", "endpoint": "https://api.kie.ai/api/v1/jobs/createTask", "method": "POST",
                    "request": {"prompt_sha256": sha, "prompt_len": len(composed)}, "attempt": 1,
                    "purpose": "draft-tier image generation for ck1/linkedin",
                },
            },
            {
                "ts": "2020-01-01T00:00:02.000+00:00", "run_id": run_id, "seq": 3, "stage": "run",
                "event": "run_end", "detail": {"exit_class": "success", "totals": {}},
            },
        ]
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "trace.jsonl").write_text(
            "\n".join(json.dumps(line) for line in trace_lines) + "\n", encoding="utf-8"
        )

        exit_code = main_module.main(["--summarize", run_id])
        assert exit_code == 0
        text = (run_dir / process_summary.PROCESS_SUMMARY_FILENAME).read_text(encoding="utf-8")
        assert composed.replace("\n", "\n> ") in text
        assert "verified against the trace's recorded sha256" in text


class TestProcessSummaryBestEffort:
    def test_summarizer_crash_never_changes_exit_class(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _write_minimal_config(tmp_path)

        def _boom(*args, **kwargs):
            raise RuntimeError("simulated summarizer crash")

        monkeypatch.setattr(process_summary, "generate_process_summary", _boom)

        exit_code = main_module.main([])
        assert exit_code == EXIT_CODE_MAP[ExitClass.SUCCESS]

        run_dir = Path((tmp_path / "logs" / "latest.txt").read_text(encoding="utf-8").strip())
        trace_lines = [
            json.loads(line) for line in (run_dir / "trace.jsonl").read_text(encoding="utf-8").splitlines()
        ]
        assert trace_lines[-1]["event"] == "run_end"
        assert trace_lines[-1]["detail"]["exit_class"] == ExitClass.SUCCESS.value
        error_events = [e for e in trace_lines if e["event"] == "error"]
        assert any("process summary" in e["detail"]["message"] for e in error_events)
        assert not (run_dir / process_summary.PROCESS_SUMMARY_FILENAME).exists()

        ledger_lines = (tmp_path / "logs" / "run_ledger.jsonl").read_text(encoding="utf-8").splitlines()
        ledger_entry = json.loads(ledger_lines[0])
        assert ledger_entry["exit_class"] == ExitClass.SUCCESS.value


class TestSummarizeCli:
    def test_regenerates_existing_run(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _write_minimal_config(tmp_path)
        main_module.main([])

        run_dir = Path((tmp_path / "logs" / "latest.txt").read_text(encoding="utf-8").strip())
        run_id = run_dir.name
        summary_path = run_dir / process_summary.PROCESS_SUMMARY_FILENAME
        assert summary_path.exists()
        summary_path.unlink()

        exit_code = main_module.main(["--summarize", run_id])
        assert exit_code == 0
        assert summary_path.exists()
        text = summary_path.read_text(encoding="utf-8")
        assert "# Process Summary" in text
        assert "## Data-hygiene footnote" in text

    def test_refuses_unknown_run_id(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        exit_code = main_module.main(["--summarize", "2020-01-01_ghost"])
        assert exit_code == main_module.EXIT_RESUME_TARGET_NOT_FOUND

    def test_usage_error_without_run_id(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        assert main_module.main(["--summarize"]) == 2

    def test_degrades_gracefully_for_synthetic_old_run_missing_new_fields(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _write_minimal_config(tmp_path)

        run_id = "2020-01-01_old1"
        run_dir = tmp_path / "logs" / "runs" / run_id
        run_dir.mkdir(parents=True)
        trace_lines = [
            {
                "ts": "2020-01-01T00:00:00.000+00:00", "run_id": run_id, "seq": 1, "stage": "run",
                "event": "run_start",
                "detail": {"mode": "interactive", "theme": "hypedigitaly", "config_fingerprint": None, "engine_version": "0.0.1", "caps_in_force": {}},
            },
            {
                "ts": "2020-01-01T00:00:05.000+00:00", "run_id": run_id, "seq": 2, "stage": "run",
                "event": "run_end", "detail": {"exit_class": "success", "totals": {}},
            },
        ]
        # No resume_state.yaml, no virlo_extraction.yaml, no copy_requests/,
        # no pack/media/ -- exactly the shape an engine version predating
        # W8-8 (or a run that crashed before spin) would leave behind.
        (run_dir / "trace.jsonl").write_text(
            "\n".join(json.dumps(line) for line in trace_lines) + "\n", encoding="utf-8"
        )

        exit_code = main_module.main(["--summarize", run_id])
        assert exit_code == 0
        text = (run_dir / process_summary.PROCESS_SUMMARY_FILENAME).read_text(encoding="utf-8")
        assert "# Process Summary" in text
        assert "never reached the spin stage" in text
        assert "no copy requests were written this run" in text.lower()
        assert "no media assets were generated" in text.lower()
        assert "no external api calls" in text.lower()
