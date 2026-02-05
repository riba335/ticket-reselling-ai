from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models
from app.services.normalizer import NormalizedEvent


def upsert_events(db: Session, events: Iterable[NormalizedEvent]) -> int:
    upserted = 0
    for event in events:
        existing = db.scalar(
            select(models.Event).where(
                models.Event.source == event.source,
                models.Event.external_id == event.external_id,
            )
        )
        if existing:
            existing.name = event.name
            existing.venue = event.venue
            existing.event_date = event.event_date
            existing.source_url = event.source_url
            event_id = existing.id
        else:
            new_event = models.Event(
                name=event.name,
                venue=event.venue,
                event_date=event.event_date,
                source=event.source,
                external_id=event.external_id,
                source_url=event.source_url,
            )
            db.add(new_event)
            db.flush()
            event_id = new_event.id

        if event.price is not None:
            listing = db.scalar(
                select(models.Listing).where(models.Listing.event_id == event_id)
            )
            if listing is None:
                listing = models.Listing(
                    event_id=event_id,
                    price=float(event.price),
                    currency=event.currency,
                )
                db.add(listing)
                db.flush()
            else:
                listing.price = float(event.price)
                listing.currency = event.currency

            snapshot = models.PriceSnapshot(
                listing_id=listing.id,
                price=float(event.price),
                currency=event.currency,
                snapped_at=datetime.now(timezone.utc),
            )
            db.add(snapshot)

        upserted += 1

    db.commit()
    return upserted
