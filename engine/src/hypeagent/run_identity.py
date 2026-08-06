"""Run identity and the run-lock.

Per RUN_TRACE_SPEC.md §1: ``run_id = pinned run-date + short uid``, e.g.
``2026-08-10_a3f2``. The run-date is fixed once at run start and never
recomputed, so a run straddling midnight keeps using the date it started
with (ARCHITECTURE_PLAN.md §8.3, §17 Phase-2 acceptance: "a run straddling
midnight uses one pinned run-date throughout").

Locking is cross-platform and OS-mediated (§8.3): an exclusive lock held on
a dedicated run-lock file for the life of the process. Windows exclusive
file-open/share-deny and POSIX advisory ``flock`` are both kernel-guaranteed
to release on crash — no stale-lock bookkeeping is required. If the lock is
already held, the new invocation must exit immediately as
``skipped-overlap`` without touching the running instance (§8.3).
"""

from __future__ import annotations

import os
import secrets
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from types import TracebackType

try:  # pragma: no cover - platform selection, not branch logic
    import msvcrt

    _IS_WINDOWS = True
except ImportError:  # pragma: no cover - exercised only on POSIX
    import fcntl

    _IS_WINDOWS = False


@dataclass(frozen=True)
class RunIdentity:
    """A run's fixed identity, established once at run start."""

    run_id: str
    run_date: str
    started_at: datetime


def new_run_identity(now: datetime | None = None) -> RunIdentity:
    """Create a new pinned run identity.

    ``now`` is injectable for tests; production callers leave it as the
    default (current local time with explicit UTC offset).
    """
    moment = now if now is not None else datetime.now().astimezone()
    run_date = moment.date().isoformat()
    uid = secrets.token_hex(2)  # 4 hex characters
    return RunIdentity(run_id=f"{run_date}_{uid}", run_date=run_date, started_at=moment)


class RunLockHeld(Exception):
    """Raised when a run-lock is already held by a live process."""

    def __init__(self, path: Path) -> None:
        super().__init__(f"run-lock already held: {path}")
        self.path = path


class RunLock:
    """An exclusive, OS-mediated, crash-safe lock on a single lock file.

    Usage::

        lock = RunLock(logs_dir / "run.lock")
        lock.acquire()   # raises RunLockHeld if another run holds it
        try:
            ...
        finally:
            lock.release()

    Also usable as a context manager.
    """

    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self._fh = None  # type: ignore[assignment]

    def acquire(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fh = open(self.path, "a+b")
        try:
            fh.seek(0, os.SEEK_END)
            if fh.tell() == 0:
                # Ensure a lockable byte range exists.
                fh.write(b"0")
                fh.flush()
            fh.seek(0)
            if _IS_WINDOWS:
                msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)
            else:  # pragma: no cover - exercised only on POSIX
                fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            fh.close()
            raise RunLockHeld(self.path) from exc
        self._fh = fh

    def release(self) -> None:
        if self._fh is None:
            return
        try:
            self._fh.seek(0)
            if _IS_WINDOWS:
                try:
                    msvcrt.locking(self._fh.fileno(), msvcrt.LK_UNLCK, 1)
                except OSError:
                    pass
            else:  # pragma: no cover - exercised only on POSIX
                fcntl.flock(self._fh.fileno(), fcntl.LOCK_UN)
        finally:
            self._fh.close()
            self._fh = None

    def __enter__(self) -> "RunLock":
        self.acquire()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> bool:
        self.release()
        return False
