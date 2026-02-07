from __future__ import annotations

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app import models
from app.collectors.seed import SeedCollector


def _make_session() -> Session:
    engine = create_engine("sqlite:///:memory:", future=True)
    models.Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)()


def test_seed_collector_inserts_10_events_and_is_idempotent(monkeypatch) -> None:
    monkeypatch.setenv("SEED_COLLECTOR", "1")
    session = _make_session()

    collector = SeedCollector()
    collector.run(session)

    first_events = list(session.scalars(select(models.Event).where(models.Event.source == "seed")))
    first_snapshots = list(session.scalars(select(models.PriceSnapshot)))

    assert len(first_events) == 10
    assert len(first_snapshots) == 10

    collector.run(session)

    second_events = list(session.scalars(select(models.Event).where(models.Event.source == "seed")))
    second_listings = list(session.scalars(select(models.Listing)))
    second_snapshots = list(session.scalars(select(models.PriceSnapshot)))

    assert len(second_events) == 10
    assert len(second_listings) == 10
    assert len(second_snapshots) == 10
