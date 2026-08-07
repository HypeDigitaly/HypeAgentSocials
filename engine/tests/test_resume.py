"""``python -m hypeagent --resume <run_id>`` (main.py, stages.resume_pipeline,
resume_state.py): re-enters ONLY copy/media/packaging/digest for an existing
run, reading collection/ranking/brand_truth/spin output back from
``resume_state.yaml`` instead of re-deriving it."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pytest
import yaml

from hypeagent import main as main_module
from hypeagent import media_gen, render_trace, resume_state as resume_state_module, run_identity, stages
from hypeagent.collectors.base import FixtureFetcher
from hypeagent.exit_codes import EXIT_CODE_MAP, ExitClass
from hypeagent.store import Store
from hypeagent.trace import TraceWriter, last_seq_in_trace
from test_media_gen import (
    RESULT_IMAGE_URL,
    QueuedFetcher,
    _create_task_ok,
    _credit_balance,
    _image_response,
    _record_info_success,
)
from test_phase1_pipeline import _default_fixture_responses, _write_config
from test_run import _write_minimal_config

FIXTURES = Path(__file__).parent / "fixtures"


def _run_once_with_ctx(tmp_path: Path, fetcher, run_id: str):
    identity = run_identity.RunIdentity(
        run_id=run_id, run_date=run_id.split("_")[0], started_at=datetime.now().astimezone()
    )
    logs_dir = tmp_path / "logs"
    run_dir = logs_dir / "runs" / identity.run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    trace_path = run_dir / "trace.jsonl"
    tw = TraceWriter(trace_path, identity.run_id)
    ctx = stages.RunContext(
        run_id=identity.run_id, config_dir=tmp_path / "config", logs_dir=logs_dir,
        theme_name="hypedigitaly", fetcher_factory=lambda: fetcher,
    )
    tw.run_start(mode="interactive", theme="hypedigitaly", config_fingerprint=None, engine_version="0.1.0")
    try:
        exit_class_value = stages.run_pipeline(ctx, tw)
    finally:
        if ctx.store is not None:
            ctx.store.close()
    tw.run_end(exit_class_value, totals={})
    tw.close()
    render_trace.render(trace_path)
    return ctx, run_dir, trace_path, exit_class_value


def _resume_with_new_ctx(tmp_path: Path, run_id: str, *, fetcher_factory=None, secrets_dir=None):
    """The exact sequence ``main.py``'s ``_resume_mode`` performs, against a
    brand-new ``RunContext``/``TraceWriter`` pair -- simulating a genuinely
    separate process invocation, the way ``--resume`` is meant to be used."""
    logs_dir = tmp_path / "logs"
    run_dir = logs_dir / "runs" / run_id
    trace_path = run_dir / "trace.jsonl"

    resume_state = resume_state_module.load_resume_state(run_dir)
    assert resume_state is not None

    resumed_at_seq = last_seq_in_trace(trace_path)
    ctx = stages.RunContext(
        run_id=run_id, config_dir=tmp_path / "config", logs_dir=logs_dir, theme_name="hypedigitaly",
        fetcher_factory=fetcher_factory, secrets_dir=secrets_dir,
    )
    tw = TraceWriter(trace_path, run_id, initial_seq=resumed_at_seq)
    try:
        tw.resume_marker(resumed_at_seq=resumed_at_seq)
        exit_class_value = stages.resume_pipeline(ctx, tw, resume_state)
        tw.run_end(exit_class_value, totals={"resume": True})
    finally:
        if ctx.store is not None:
            ctx.store.close()
        tw.close()
    render_trace.render(trace_path)
    return ctx, resumed_at_seq, exit_class_value


def _write_valid_response(resp_dir: Path, asset_id: str, *, headline="AI agents are changing outbound sales") -> None:
    resp_dir.mkdir(parents=True, exist_ok=True)
    (resp_dir / f"{asset_id}.yaml").write_text(
        yaml.safe_dump(
            {
                "headline": headline,
                "caption": "See how small businesses use AI chatbots. Learn more at example.com. [AI-generated content]",
                "image_brief": "A calm, people-free office scene, no product depiction.",
            }
        ),
        encoding="utf-8",
    )


def _trace_lines(trace_path: Path) -> list[dict]:
    return [json.loads(line) for line in trace_path.read_text(encoding="utf-8").splitlines() if line.strip()]


class TestResumeConsumesResponse:
    def test_resume_picks_up_response_and_completes_the_asset(self, tmp_path):
        _write_config(tmp_path)
        fetcher = FixtureFetcher(responses=_default_fixture_responses())
        run_id = "2026-08-10_res01"
        ctx, run_dir, trace_path, exit_class_value = _run_once_with_ctx(tmp_path, fetcher, run_id)

        statuses = ctx.extra.get("copy_asset_statuses", [])
        assert statuses, "fixture set is expected to produce at least one EN copy asset"
        held = next(s for s in statuses if s.status == "held — awaiting operator copy")

        requests_dir = run_dir / "copy_requests"
        assert (requests_dir / f"{held.asset_id}.yaml").exists()
        assert (run_dir / resume_state_module.RESUME_STATE_FILENAME).exists()

        # W8-9 Q3a: the analysis stage's viral_playbook.yaml path round-trips
        # into resume_state.yaml and back out on --resume, even on the
        # LLM-disabled default path (the file is always written, empty-but-
        # valid, exactly per hypeagent.analysis's module contract).
        assert ctx.extra.get("viral_playbook_path")
        assert Path(ctx.extra["viral_playbook_path"]).exists()
        resume_state_on_disk = resume_state_module.load_resume_state(run_dir)
        assert resume_state_on_disk.viral_playbook_path == ctx.extra["viral_playbook_path"]

        seq_after_first_pass = last_seq_in_trace(trace_path)
        stages_seen_before = {ev["stage"] for ev in _trace_lines(trace_path)}
        assert "collection" in stages_seen_before and "ranking" in stages_seen_before

        _write_valid_response(run_dir / "copy_responses", held.asset_id)

        ctx2, resumed_at_seq, exit_class_value2 = _resume_with_new_ctx(tmp_path, run_id)
        assert resumed_at_seq == seq_after_first_pass

        statuses2 = ctx2.extra.get("copy_asset_statuses", [])
        matching = next(s for s in statuses2 if s.asset_id == held.asset_id)
        assert matching.status == "gated-pass"
        assert matching.headline

        # ``analysis`` is not in RESUME_STAGE_NAMES (it never re-runs on
        # --resume) -- the resumed context still carries the ORIGINAL run's
        # viral_playbook_path forward from resume_state.yaml.
        assert ctx2.extra.get("viral_playbook_path") == ctx.extra["viral_playbook_path"]

        # No key file was ever provisioned -- media plans only, at zero cost.
        media_statuses = ctx2.extra.get("media_asset_statuses", [])
        gated_media = next(s for s in media_statuses if s.asset_id == held.asset_id)
        assert gated_media.status == "plan-only — no Kie API key configured"

        digest_text = (run_dir / "pack" / "digest.md").read_text(encoding="utf-8")
        assert "gated-pass" in digest_text

        # Exactly one request file for this asset (attempt 1) -- resume did
        # not rewrite/duplicate it.
        assert list(requests_dir.glob(f"{held.asset_id}*.yaml")) == [requests_dir / f"{held.asset_id}.yaml"]

        # Sequence numbering is monotonic across the whole (appended) file,
        # and collection/ranking/brand_truth/spin never ran a second time.
        all_lines = _trace_lines(trace_path)
        seqs = [ev["seq"] for ev in all_lines]
        assert seqs == list(range(1, len(seqs) + 1))
        resume_events = [ev for ev in all_lines if ev.get("detail", {}).get("resume") is True]
        assert len(resume_events) == 1
        assert resume_events[0]["detail"]["resumed_at_seq"] == seq_after_first_pass
        assert resume_events[0]["seq"] == seq_after_first_pass + 1

        stage_starts_after_marker = [
            ev["stage"] for ev in all_lines if ev["seq"] > resume_events[0]["seq"] and ev["event"] == "stage_start"
        ]
        assert set(stage_starts_after_marker) <= {"copy", "media", "packaging", "digest"}
        assert "collection" not in stage_starts_after_marker
        assert "ranking" not in stage_starts_after_marker
        assert "brand_truth" not in stage_starts_after_marker
        assert "spin" not in stage_starts_after_marker

    def test_resume_gates_pass_and_submits_media_in_one_call(self, tmp_path):
        """The full held -> gated-pass -> (mock) media submitted -> pack/
        digest updated round trip, driven by a single ``--resume``-shaped
        invocation: the operator drops a copy response AND a Kie key while
        the run was paused, and one resume call picks up both."""
        _write_config(tmp_path)
        fetcher = FixtureFetcher(responses=_default_fixture_responses())
        run_id = "2026-08-10_res01b"
        ctx, run_dir, trace_path, exit_class_value = _run_once_with_ctx(tmp_path, fetcher, run_id)

        statuses = ctx.extra.get("copy_asset_statuses", [])
        held = next(s for s in statuses if s.status == "held — awaiting operator copy")
        assert not (tmp_path / "secrets" / "kie.key").exists()

        _write_valid_response(run_dir / "copy_responses", held.asset_id)
        secrets_dir = tmp_path / "secrets"
        secrets_dir.mkdir(parents=True, exist_ok=True)
        (secrets_dir / "kie.key").write_text("kie_test_secret_value", encoding="utf-8")

        kie_fetcher = QueuedFetcher(
            responses={
                "createTask": [_create_task_ok("task_resume_1")],
                "recordInfo": [_record_info_success("task_resume_1")],
                "chat/credit": [_credit_balance(100.0), _credit_balance(96.0)],
                RESULT_IMAGE_URL: [_image_response()],
            }
        )
        ctx2, resumed_at_seq, exit_class_value2 = _resume_with_new_ctx(
            tmp_path, run_id, fetcher_factory=lambda: kie_fetcher, secrets_dir=secrets_dir,
        )

        matching = next(s for s in ctx2.extra["copy_asset_statuses"] if s.asset_id == held.asset_id)
        assert matching.status == "gated-pass"

        media_statuses = ctx2.extra["media_asset_statuses"]
        generated = next(s for s in media_statuses if s.asset_id == held.asset_id)
        assert generated.status == "generated"
        assert generated.image_path is not None
        assert Path(generated.image_path).exists()

        digest_text = (run_dir / "pack" / "digest.md").read_text(encoding="utf-8")
        assert "generated" in digest_text
        assert "media — actual spend" in digest_text.lower()

        # W8-9 Q4 pack layout: one folder per asset, ``hero.provenance.yaml`` inside it.
        provenance_path = run_dir / "pack" / "media" / f"{held.cluster_key}_{held.destination}" / "hero.provenance.yaml"
        assert provenance_path.exists()

        # The key and the provider's result URL never reach the trace.
        trace_text = trace_path.read_text(encoding="utf-8")
        assert "kie_test_secret_value" not in trace_text
        assert RESULT_IMAGE_URL not in trace_text

    def test_resume_with_no_response_stays_held_idempotently_at_zero_spend(self, tmp_path):
        _write_config(tmp_path)
        fetcher = FixtureFetcher(responses=_default_fixture_responses())
        run_id = "2026-08-10_res02"
        ctx, run_dir, trace_path, exit_class_value = _run_once_with_ctx(tmp_path, fetcher, run_id)
        calls_after_first = len(fetcher.calls)

        statuses = ctx.extra.get("copy_asset_statuses", [])
        held = next(s for s in statuses if s.status == "held — awaiting operator copy")

        requests_dir = run_dir / "copy_requests"
        before_files = {p.name: p.read_bytes() for p in requests_dir.glob("*.yaml")}

        ctx2, resumed_at_seq, exit_class_value2 = _resume_with_new_ctx(tmp_path, run_id)

        # Still held -- no response ever arrived.
        still_held = next(s for s in ctx2.extra["copy_asset_statuses"] if s.asset_id == held.asset_id)
        assert still_held.status == "held — awaiting operator copy"

        # No new/changed request files, no collector network calls, no media
        # spend -- resuming with nothing new to consume is a pure no-op on
        # every one of those axes.
        after_files = {p.name: p.read_bytes() for p in requests_dir.glob("*.yaml")}
        assert after_files == before_files
        assert len(fetcher.calls) == calls_after_first

        store = Store.open(tmp_path / "logs", tmp_path / "secrets")
        try:
            assert store.unresolved_media_intents("hypedigitaly") == []
            assert store.media_spend_usd_for_day(theme="hypedigitaly", run_date=run_id.split("_")[0]) == 0.0
        finally:
            store.close()

    def test_blocked_gate_on_resume_writes_attempt_2_repair_request(self, tmp_path):
        _write_config(tmp_path)
        fetcher = FixtureFetcher(responses=_default_fixture_responses())
        run_id = "2026-08-10_res03"
        ctx, run_dir, trace_path, exit_class_value = _run_once_with_ctx(tmp_path, fetcher, run_id)

        statuses = ctx.extra.get("copy_asset_statuses", [])
        held = next(s for s in statuses if s.status == "held — awaiting operator copy")

        # A superlative is an unconditional claim-gate block (test_claim_gate.py),
        # independent of the brand-facts fixture content -- deterministic.
        resp_dir = run_dir / "copy_responses"
        resp_dir.mkdir(parents=True, exist_ok=True)
        (resp_dir / f"{held.asset_id}.yaml").write_text(
            yaml.safe_dump(
                {
                    "headline": "The best AI agents platform",
                    "caption": "Guaranteed results. [AI-generated content]",
                    "image_brief": "A calm, people-free office scene.",
                }
            ),
            encoding="utf-8",
        )

        ctx2, resumed_at_seq, exit_class_value2 = _resume_with_new_ctx(tmp_path, run_id)

        matching = next(s for s in ctx2.extra["copy_asset_statuses"] if s.asset_id == held.asset_id)
        # Repair budget is 2 attempts (COPY_MAX_ATTEMPTS/default repair_budget):
        # attempt 1 is blocked, a fresh attempt-2 brief is written, and since no
        # attempt-2 response exists yet the asset holds again at attempt 2 —
        # not yet "blocked" (repair budget is not exhausted until attempt 2
        # itself also fails or is never answered further).
        assert matching.attempt == 2
        assert matching.status == "held — awaiting operator copy"

        requests_dir = run_dir / "copy_requests"
        attempt2_path = requests_dir / f"{held.asset_id}.attempt2.yaml"
        assert attempt2_path.exists()
        attempt2_doc = yaml.safe_load(attempt2_path.read_text(encoding="utf-8"))
        assert attempt2_doc["prior_failing_spans"]
        assert any("superlative" in span for span in attempt2_doc["prior_failing_spans"])

        # Answering attempt 2 on a SECOND resume exhausts nothing further --
        # a clean response now gates straight to pass.
        _write_valid_response(resp_dir, f"{held.asset_id}.attempt2")
        ctx3, resumed_at_seq_2, exit_class_value3 = _resume_with_new_ctx(tmp_path, run_id)
        assert resumed_at_seq_2 > resumed_at_seq
        final = next(s for s in ctx3.extra["copy_asset_statuses"] if s.asset_id == held.asset_id)
        assert final.status == "gated-pass"
        assert final.attempt == 2

        # Seq numbering stayed monotonic across all three invocations.
        seqs = [ev["seq"] for ev in _trace_lines(trace_path)]
        assert seqs == list(range(1, len(seqs) + 1))


class TestResumeMediaCapsCombineAcrossInvocations:
    def test_day_cap_spent_in_original_invocation_blocks_a_new_asset_on_resume(self, tmp_path):
        _write_config(tmp_path)
        theme_yaml = tmp_path / "config" / "themes" / "hypedigitaly.yaml"
        # NOTE: this REPLACES (YAML duplicate-key semantics: last one wins)
        # ``_write_config``'s own trailing ``generation:`` block -- its
        # ``route_by_class`` pin has to be repeated here too, or this
        # override would silently fall back to MediaConfig's own default
        # (the unregistered standard-tier route this fixture's minimal
        # registry does not carry).
        theme_yaml.write_text(
            theme_yaml.read_text(encoding="utf-8")
            + "\ngeneration:\n  media:\n    per_day_usd_cap: 0.02\n    route_by_class:\n"
            "      hero: img-draft-nano-banana\n      slide: img-draft-nano-banana\n",
            encoding="utf-8",
        )

        fetcher = FixtureFetcher(responses=_default_fixture_responses())
        run_id = "2026-08-10_medcap"
        ctx, run_dir, trace_path, exit_class_value = _run_once_with_ctx(tmp_path, fetcher, run_id)

        statuses = ctx.extra.get("copy_asset_statuses", [])
        by_dest = {s.destination: s for s in statuses}
        assert "linkedin" in by_dest and "instagram_feed" in by_dest
        linkedin = by_dest["linkedin"]
        insta = by_dest["instagram_feed"]

        resp_dir = run_dir / "copy_responses"
        _write_valid_response(resp_dir, linkedin.asset_id, headline="AI agents are changing outbound sales")

        # Still the same original invocation completing its own copy+media
        # work (the "re-run the same ctx" idempotency pattern this codebase's
        # own copy_gen.py docstring names) -- gate the linkedin asset and
        # generate its image, spending $0.02 against the (theme, run_date).
        t2 = TraceWriter(tmp_path / "logs" / "t2.jsonl", run_id)
        try:
            stages.stage_copy(ctx, t2)
        finally:
            t2.close()
        gated_linkedin = next(s for s in ctx.extra["copy_asset_statuses"] if s.asset_id == linkedin.asset_id)
        assert gated_linkedin.status == "gated-pass"

        secrets_dir = tmp_path / "secrets"
        secrets_dir.mkdir(parents=True, exist_ok=True)
        (secrets_dir / "kie.key").write_text("kie_test_secret_value", encoding="utf-8")
        ctx.store = Store.open(ctx.logs_dir, secrets_dir)

        kie_fetcher_1 = QueuedFetcher(
            responses={
                "createTask": [_create_task_ok("task_cap_1")],
                "recordInfo": [_record_info_success("task_cap_1")],
                "chat/credit": [_credit_balance(100.0), _credit_balance(96.0)],
                RESULT_IMAGE_URL: [_image_response()],
            }
        )
        ctx.fetcher_factory = lambda: kie_fetcher_1
        media_trace_1 = TraceWriter(tmp_path / "logs" / "media1.jsonl", run_id)
        try:
            stages.stage_media(ctx, media_trace_1)
        finally:
            media_trace_1.close()
        generated_1 = next(s for s in ctx.extra["media_asset_statuses"] if s.asset_id == linkedin.asset_id)
        assert generated_1.status == "generated"
        assert generated_1.observed_cost_usd == pytest.approx(0.02)
        ctx.store.close()

        # --- a genuinely separate resume invocation ---
        _write_valid_response(resp_dir, insta.asset_id, headline="Automating lead gen for small teams")
        never_touched_fetcher = QueuedFetcher(responses={})
        ctx2, resumed_at_seq, exit_class_value2 = _resume_with_new_ctx(
            tmp_path, run_id, fetcher_factory=lambda: never_touched_fetcher, secrets_dir=secrets_dir,
        )

        insta_status = next(s for s in ctx2.extra["media_asset_statuses"] if s.asset_id == insta.asset_id)
        assert insta_status.status == media_gen.STATUS_BUDGET_CAPPED
        assert exit_class_value2 == ExitClass.PARTIAL_SUCCESS_BUDGET_CAPPED_MID_PACK.value
        assert never_touched_fetcher.calls == []  # capped before any Kie call was ever made

        # linkedin's already-resolved row is reported again (idempotent),
        # not resubmitted or charged a second time.
        linkedin_status_again = next(s for s in ctx2.extra["media_asset_statuses"] if s.asset_id == linkedin.asset_id)
        assert linkedin_status_again.status == "generated"

        store_check = Store.open(tmp_path / "logs", secrets_dir)
        try:
            day_spend = store_check.media_spend_usd_for_day(theme="hypedigitaly", run_date=run_id.split("_")[0])
        finally:
            store_check.close()
        assert day_spend == pytest.approx(0.02)


class TestResumeCliRefusals:
    def test_refuses_nonexistent_run_id(self, tmp_path, monkeypatch, capsys):
        monkeypatch.chdir(tmp_path)
        exit_code = main_module.main(["--resume", "2026-01-01_ghost"])
        assert exit_code == main_module.EXIT_RESUME_TARGET_NOT_FOUND
        assert "cannot resume" in capsys.readouterr().err

    def test_refuses_run_dir_without_trace_jsonl(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        run_dir = tmp_path / "logs" / "runs" / "2026-01-01_notrace"
        run_dir.mkdir(parents=True)
        exit_code = main_module.main(["--resume", "2026-01-01_notrace"])
        assert exit_code == main_module.EXIT_RESUME_TARGET_NOT_FOUND

    def test_refuses_missing_run_id_argument(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        assert main_module.main(["--resume"]) == 2

    def test_refuses_run_that_never_reached_spin(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _write_minimal_config(tmp_path)

        def _boom(ctx, trace):
            raise RuntimeError("simulated crash before spin")

        original_stages = stages.CANONICAL_STAGES
        broken_stages = tuple(
            (name, _boom) if name == "collection" else (name, fn) for name, fn in stages.CANONICAL_STAGES
        )
        monkeypatch.setattr(stages, "CANONICAL_STAGES", broken_stages)
        exit_code = main_module.main([])
        assert exit_code == EXIT_CODE_MAP[ExitClass.HARD_FAILURE]

        run_dir = Path((tmp_path / "logs" / "latest.txt").read_text(encoding="utf-8").strip())
        assert not (run_dir / resume_state_module.RESUME_STATE_FILENAME).exists()

        # Restore the stage list (leaving ``monkeypatch.chdir`` intact) --
        # ``resume_pipeline`` doesn't touch ``collection`` anyway, but the
        # point of this test is the *refusal*, not another simulated crash.
        monkeypatch.setattr(stages, "CANONICAL_STAGES", original_stages)
        exit_code2 = main_module.main(["--resume", run_dir.name])
        assert exit_code2 == main_module.EXIT_RESUME_TARGET_NOT_FOUND

    def test_refuses_when_run_lock_held(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _write_minimal_config(tmp_path)
        exit_code = main_module.main([])
        assert exit_code == EXIT_CODE_MAP[ExitClass.SUCCESS]
        run_dir = Path((tmp_path / "logs" / "latest.txt").read_text(encoding="utf-8").strip())
        trace_lines_before = _trace_lines(run_dir / "trace.jsonl")

        lock = run_identity.RunLock(tmp_path / "logs" / "run.lock")
        lock.acquire()
        try:
            exit_code2 = main_module.main(["--resume", run_dir.name])
            assert exit_code2 == EXIT_CODE_MAP[ExitClass.SKIPPED_OVERLAP]
        finally:
            lock.release()

        # Refused before touching the target run's own trace at all.
        assert _trace_lines(run_dir / "trace.jsonl") == trace_lines_before


class TestResumeCliRoundTrip:
    def test_resume_cli_round_trip_is_idempotent_success(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _write_minimal_config(tmp_path)

        exit_code = main_module.main([])
        assert exit_code == EXIT_CODE_MAP[ExitClass.SUCCESS]

        run_dir = Path((tmp_path / "logs" / "latest.txt").read_text(encoding="utf-8").strip())
        run_id = run_dir.name
        assert (run_dir / resume_state_module.RESUME_STATE_FILENAME).exists()

        trace_path = run_dir / "trace.jsonl"
        seq_before_resume = last_seq_in_trace(trace_path)

        exit_code2 = main_module.main(["--resume", run_id])
        assert exit_code2 == EXIT_CODE_MAP[ExitClass.SUCCESS]

        all_lines = _trace_lines(trace_path)
        seqs = [ev["seq"] for ev in all_lines]
        assert seqs == list(range(1, len(seqs) + 1))
        resume_events = [ev for ev in all_lines if ev.get("detail", {}).get("resume") is True]
        assert len(resume_events) == 1
        assert resume_events[0]["detail"]["resumed_at_seq"] == seq_before_resume

        ledger_lines = (tmp_path / "logs" / "run_ledger.jsonl").read_text(encoding="utf-8").splitlines()
        assert len(ledger_lines) == 2
        entries = [json.loads(line) for line in ledger_lines]
        assert all(e["run_id"] == run_id for e in entries)
        assert all(e["exit_class"] == ExitClass.SUCCESS.value for e in entries)
        assert "resume" not in entries[0]  # the original invocation's row is unchanged in shape
        assert entries[1].get("resume") is True

        # latest.txt still points at the same (resumed) run.
        assert Path((tmp_path / "logs" / "latest.txt").read_text(encoding="utf-8").strip()) == run_dir
