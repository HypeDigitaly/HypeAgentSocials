"""The run exit-class taxonomy.

Nine named classes (ARCHITECTURE_PLAN.md §8.8, D-18; SYNTHESIS §4.7), each
mapped to one distinct process exit code for scheduler-level monitoring. The
numeric mapping itself is deferred to implementation by the plan; the string
values below are the canonical, verbatim class names and MUST NOT be
renamed or reworded — they are what appears in the run ledger and the trace.
"""

from __future__ import annotations

from enum import Enum


class ExitClass(str, Enum):
    """The nine exit classes, verbatim from §8.8."""

    SUCCESS = "success"
    COMPLETED_WITH_PENDING_MEDIA = "completed-with-pending-media"
    PARTIAL_SUCCESS_DEGRADED_SOURCES = "partial-success — degraded sources"
    PARTIAL_SUCCESS_BUDGET_CAPPED_MID_PACK = "partial-success — budget-capped mid-pack"
    COMPLETED_DEGRADED = "completed-degraded"
    BUDGET_STOP = "budget-stop"
    POLICY_STOP = "policy-stop"
    SKIPPED_OVERLAP = "skipped-overlap"
    HARD_FAILURE = "hard-failure"


# Numeric process exit codes. Deliberately coarse (§8.8: "a highly granular
# per-stage-per-reason numeric code was equally rejected"); full detail lives
# in the run ledger and the trace, not in this mapping.
EXIT_CODE_MAP: dict[ExitClass, int] = {
    ExitClass.SUCCESS: 0,
    ExitClass.COMPLETED_WITH_PENDING_MEDIA: 0,
    ExitClass.PARTIAL_SUCCESS_DEGRADED_SOURCES: 10,
    ExitClass.PARTIAL_SUCCESS_BUDGET_CAPPED_MID_PACK: 11,
    ExitClass.COMPLETED_DEGRADED: 20,
    ExitClass.BUDGET_STOP: 30,
    ExitClass.POLICY_STOP: 40,
    ExitClass.SKIPPED_OVERLAP: 75,
    ExitClass.HARD_FAILURE: 1,
}


def exit_code_for(exit_class: ExitClass) -> int:
    """Return the process exit code for an exit class."""
    return EXIT_CODE_MAP[exit_class]
