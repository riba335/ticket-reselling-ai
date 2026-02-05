from __future__ import annotations

import logging
import os
from typing import Iterable, Sequence

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.collectors.base import BaseCollector
from app.services.normalizer import NormalizedEvent, normalize_event

logger = logging.getLogger(__name__)


class ExampleCollector(BaseCollector):
    name = "example_api"

    def __init__(self) -> None:
        self.api_key = os.getenv("EXAMPLE_API_KEY")
        self.base_url = os.getenv(
            "EXAMPLE_API_BASE_URL", "https://api.example.com/v1/events"
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
    def _fetch_from_api(self) -> Sequence[dict]:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        with httpx.Client(timeout=10.0) as client:
            response = client.get(self.base_url, headers=headers)
            response.raise_for_status()
            payload = response.json()
        return payload.get("events", [])

    def fetch(self) -> Sequence[dict]:
        if not self.api_key:
            logger.warning("EXAMPLE_API_KEY not set; skipping ExampleCollector fetch.")
            return []
        return self._fetch_from_api()

    def normalize(self, raw_events: Sequence[dict]) -> Iterable[NormalizedEvent]:
        for raw in raw_events:
            yield normalize_event(raw, source=self.name)
