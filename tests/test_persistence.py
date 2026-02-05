from datetime import datetime, timezone

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app import models
from app.services.normalizer import NormalizedEvent
from app.services.persistence import upsert_events


def _make_session() -> Session:
    engine = create_engine("sqlite:///:memory:", future=True)
    models.Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)()


def test_upsert_events_enforces_uniqueness() -> None:
    session = _make_session()
    event = NormalizedEvent(
        source="example_api",
        external_id="evt_789",
        name="One Night Only",
        venue="Main Stage",
        event_date=datetime(2032, 6, 1, 19, 0, tzinfo=timezone.utc),
        source_url="https://tickets.example.com/events/evt_789",
        price=120.0,
        currency="EUR",
    )

    upsert_events(session, [event])
    upsert_events(
        session,
        [
            NormalizedEvent(
                source="example_api",
                external_id="evt_789",
                name="One Night Only - Updated",
                venue="Main Stage",
                event_date=event.event_date,
                source_url="https://tickets.example.com/events/evt_789",
                price=125.0,
                currency="EUR",
            )
        ],
    )

    events = list(
        session.scalars(
            select(models.Event).where(models.Event.external_id == "evt_789")
        )
    )
    listings = list(session.scalars(select(models.Listing)))
    snapshots = list(session.scalars(select(models.PriceSnapshot)))

    assert len(events) == 1
    assert events[0].name == "One Night Only - Updated"
    assert len(listings) == 1
    assert len(snapshots) == 2
