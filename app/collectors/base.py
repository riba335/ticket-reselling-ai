from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Iterable, Sequence

from sqlalchemy.orm import Session

from app import models
from app.services import persistence
from app.services.normalizer import NormalizedEvent

logger = logging.getLogger(__name__)


class BaseCollector(ABC):
    name: str

    @abstractmethod
    def fetch(self) -> Sequence[dict]:
        """Fetch raw events from the source."""

    @abstractmethod
    def normalize(self, raw_events: Sequence[dict]) -> Iterable[NormalizedEvent]:
        """Normalize raw events to canonical schema."""

    def run(self, db: Session) -> models.CollectorRun:
        started_at = datetime.now(timezone.utc)
        run_record = models.CollectorRun(
            source=self.name,
            started_at=started_at,
            status="running",
            items_fetched=0,
            items_upserted=0,
        )
        db.add(run_record)
        db.commit()
        db.refresh(run_record)

        try:
            raw_events = self.fetch()
            normalized_events = list(self.normalize(raw_events))
            items_upserted = persistence.upsert_events(db, normalized_events)
            run_record.items_fetched = len(raw_events)
            run_record.items_upserted = items_upserted
            run_record.status = "success"
            run_record.finished_at = datetime.now(timezone.utc)
            db.commit()
            return run_record
        except Exception as exc:  # noqa: BLE001 - record collector failures
            logger.exception("Collector %s failed", self.name)
            run_record.status = "failed"
            run_record.finished_at = datetime.now(timezone.utc)
            run_record.error_message = str(exc)
            db.commit()
            return run_record
