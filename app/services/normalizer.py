from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping


@dataclass(frozen=True)
class NormalizedEvent:
    source: str
    external_id: str
    name: str
    venue: str
    event_date: datetime
    source_url: str | None = None
    price: float | None = None
    currency: str = "EUR"


def _parse_event_date(raw_value: Any) -> datetime:
    if isinstance(raw_value, datetime):
        event_date = raw_value
    elif isinstance(raw_value, str):
        event_date = datetime.fromisoformat(raw_value)
    else:
        raise ValueError("event_date must be a datetime or ISO 8601 string")

    if event_date.tzinfo is None:
        event_date = event_date.replace(tzinfo=timezone.utc)
    return event_date


def normalize_event(raw: Mapping[str, Any], source: str) -> NormalizedEvent:
    external_id = str(raw.get("id") or raw.get("external_id") or "")
    if not external_id:
        raise ValueError("raw event is missing an external id")

    name = str(raw.get("name") or "").strip()
    venue = str(raw.get("venue") or "").strip()
    if not name or not venue:
        raise ValueError("raw event must include name and venue")

    event_date = _parse_event_date(raw.get("event_date"))
    source_url = raw.get("url") or raw.get("source_url")
    price = raw.get("price")
    currency = raw.get("currency") or "EUR"

    return NormalizedEvent(
        source=source,
        external_id=external_id,
        name=name,
        venue=venue,
        event_date=event_date,
        source_url=source_url,
        price=price,
        currency=currency,
    )
