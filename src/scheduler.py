"""Simple persistent job scheduler using APScheduler."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Callable
from uuid import uuid4

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler

# ---------------------------------------------------------------------------
# Configure persistent job storage
_JOB_DB = Path("logs/jobs.sqlite")
_JOB_DB.parent.mkdir(parents=True, exist_ok=True)

_scheduler = BackgroundScheduler(
    jobstores={"default": SQLAlchemyJobStore(url=f"sqlite:///{_JOB_DB}")}
)
_scheduler.start()


def schedule(task: Callable[[Any], Any], run_at: datetime, payload: Any) -> str:
    """Schedule ``task`` to run at ``run_at`` with ``payload``.

    Parameters
    ----------
    task:
        Callable executed when the job triggers.  The function must be
        importable for persistence.
    run_at:
        ``datetime`` when the task should execute.
    payload:
        Arbitrary data passed as the first positional argument to ``task``.

    Returns
    -------
    str
        Identifier of the scheduled job which can be used with ``cancel``.
    """

    job_id = str(uuid4())
    _scheduler.add_job(task, "date", run_date=run_at, args=[payload], id=job_id)
    return job_id


def cancel(task_id: str) -> bool:
    """Cancel a previously scheduled job.

    Returns ``True`` if the job was cancelled, ``False`` if no such job
    exists."""

    job = _scheduler.get_job(task_id)
    if not job:
        return False
    job.remove()
    return True
