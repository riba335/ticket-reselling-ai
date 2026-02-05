from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models


def get_events(db: Session) -> list[models.Event]:
    return list(db.scalars(select(models.Event).order_by(models.Event.event_date)))


def get_collector_runs_by_source(
    db: Session, limit_per_source: int
) -> dict[str, list[models.CollectorRun]]:
    runs = list(
        db.scalars(
            select(models.CollectorRun).order_by(models.CollectorRun.started_at.desc())
        )
    )
    grouped: dict[str, list[models.CollectorRun]] = {}
    for run in runs:
        grouped.setdefault(run.source, [])
        if len(grouped[run.source]) < limit_per_source:
            grouped[run.source].append(run)
    return grouped
