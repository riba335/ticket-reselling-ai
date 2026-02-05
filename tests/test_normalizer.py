from datetime import datetime, timezone

from app.services.normalizer import normalize_event


def test_normalize_event_defaults_timezone() -> None:
    raw = {
        "id": "evt_123",
        "name": "Sample Show",
        "venue": "Demo Arena",
        "event_date": "2030-05-01T19:30:00",
        "url": "https://tickets.example.com/events/evt_123",
        "price": 99.0,
        "currency": "EUR",
    }

    normalized = normalize_event(raw, source="example_api")

    assert normalized.external_id == "evt_123"
    assert normalized.source == "example_api"
    assert normalized.event_date.tzinfo == timezone.utc
    assert normalized.source_url == raw["url"]
    assert normalized.price == 99.0


def test_normalize_event_accepts_datetime() -> None:
    raw = {
        "external_id": "evt_456",
        "name": "Night Show",
        "venue": "City Hall",
        "event_date": datetime(2031, 1, 1, 20, 0, tzinfo=timezone.utc),
    }

    normalized = normalize_event(raw, source="example_api")

    assert normalized.external_id == "evt_456"
    assert normalized.event_date.tzinfo == timezone.utc
