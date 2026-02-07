from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Iterable, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models
from app.collectors.base import BaseCollector
from app.services.normalizer import NormalizedEvent

logger = logging.getLogger(__name__)


class SeedCollector(BaseCollector):
    name = "seed"

    def fetch(self) -> Sequence[dict]:
        if os.getenv("SEED_COLLECTOR") != "1":
            logger.info("SEED_COLLECTOR is not set to 1; skipping SeedCollector fetch.")
            return []

        base_date = datetime(2030, 1, 1, 20, 0, tzinfo=timezone.utc)
        return [
            {
                "id": f"seed-event-{index:02d}",
                "name": f"Seed Event {index}",
                "venue": f"Seed Venue {((index - 1) % 3) + 1}",
                "event_date": (base_date + timedelta(days=index)).isoformat(),
                "url": f"https://seed.local/events/{index:02d}",
                "price": float(50 + index * 5),
                "currency": "EUR",
            }
            for index in range(1, 11)
        ]

    def normalize(self, raw_events: Sequence[dict]) -> Iterable[NormalizedEvent]:
        for raw in raw_events:
            yield NormalizedEvent(
                source=self.name,
                external_id=str(raw["id"]),
                name=str(raw["name"]),
                venue=str(raw["venue"]),
                event_date=datetime.fromisoformat(str(raw["event_date"])),
                source_url=str(raw["url"]),
                price=float(raw["price"]),
                currency=str(raw["currency"]),
            )

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

        if os.getenv("SEED_COLLECTOR") != "1":
            logger.info("SEED_COLLECTOR is not set to 1; skipping SeedCollector run.")
            run_record.status = "success"
            run_record.finished_at = datetime.now(timezone.utc)
            db.commit()
            return run_record

        try:
            raw_events = self.fetch()
            normalized_events = list(self.normalize(raw_events))
            items_upserted = 0

            for event in normalized_events:
                existing_event = db.scalar(
                    select(models.Event).where(
                        models.Event.source == event.source,
                        models.Event.external_id == event.external_id,
                    )
                )
                if existing_event is None:
                    existing_event = models.Event(
                        source=event.source,
                        external_id=event.external_id,
                        name=event.name,
                        venue=event.venue,
                        event_date=event.event_date,
                        source_url=event.source_url,
                    )
                    db.add(existing_event)
                    db.flush()
                else:
                    existing_event.name = event.name
                    existing_event.venue = event.venue
                    existing_event.event_date = event.event_date
                    existing_event.source_url = event.source_url

                listing = db.scalar(
                    select(models.Listing).where(models.Listing.event_id == existing_event.id)
                )
                if listing is None:
                    listing = models.Listing(
                        event_id=existing_event.id,
                        price=float(event.price or 0),
                        currency=event.currency,
                    )
                    db.add(listing)
                    db.flush()
                else:
                    listing.price = float(event.price or 0)
                    listing.currency = event.currency

                existing_snapshot = db.scalar(
                    select(models.PriceSnapshot).where(
                        models.PriceSnapshot.listing_id == listing.id
                    )
                )
                if existing_snapshot is None:
                    db.add(
                        models.PriceSnapshot(
                            listing_id=listing.id,
                            price=float(event.price or 0),
                            currency=event.currency,
                            snapped_at=datetime.now(timezone.utc),
                        )
                    )

                items_upserted += 1

            run_record.items_fetched = len(raw_events)
            run_record.items_upserted = items_upserted
            run_record.status = "success"
            run_record.finished_at = datetime.now(timezone.utc)
            db.commit()
            return run_record
        except Exception as exc:  # noqa: BLE001
            logger.exception("Collector %s failed", self.name)
            run_record.status = "failed"
            run_record.finished_at = datetime.now(timezone.utc)
            run_record.error_message = str(exc)
            db.commit()
            return run_record
