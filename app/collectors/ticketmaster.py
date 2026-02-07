from __future__ import annotations

import logging
import os
from typing import Iterable, Sequence

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.collectors.base import BaseCollector
from app.services.normalizer import NormalizedEvent, normalize_event

logger = logging.getLogger(__name__)


class TicketmasterCollector(BaseCollector):
    name = "ticketmaster"

    def __init__(self) -> None:
        self.api_key = os.getenv("TICKETMASTER_API_KEY")
        self.base_url = os.getenv(
            "TICKETMASTER_API_BASE_URL",
            "https://app.ticketmaster.com/discovery/v2/events.json",
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
    def _fetch_from_api(self) -> Sequence[dict]:
        params = {"apikey": self.api_key, "size": 50}
        with httpx.Client(timeout=10.0) as client:
            response = client.get(self.base_url, params=params)
            response.raise_for_status()
            payload = response.json()

        return payload.get("_embedded", {}).get("events", [])

    def fetch(self) -> Sequence[dict]:
        if not self.api_key:
            logger.info(
                "TICKETMASTER_API_KEY not set; skipping TicketmasterCollector fetch."
            )
            return []
        return self._fetch_from_api()

    def normalize(self, raw_events: Sequence[dict]) -> Iterable[NormalizedEvent]:
        for raw in raw_events:
            dates = raw.get("dates", {}).get("start", {})
            venues = raw.get("_embedded", {}).get("venues", [])
            normalized_raw = {
                "id": raw.get("id"),
                "name": raw.get("name"),
                "venue": venues[0].get("name") if venues else "Unknown Venue",
                "event_date": dates.get("dateTime") or dates.get("localDate"),
                "url": raw.get("url"),
                "price": None,
                "currency": "EUR",
            }
            yield normalize_event(normalized_raw, source=self.name)
