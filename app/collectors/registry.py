from __future__ import annotations

import logging
import os
from typing import Sequence

from app.collectors.base import BaseCollector
from app.collectors.seed import SeedCollector
from app.collectors.ticketmaster import TicketmasterCollector

logger = logging.getLogger(__name__)


def get_enabled_collectors() -> Sequence[BaseCollector]:
    collectors: list[BaseCollector] = []

    if os.getenv("SEED_COLLECTOR") == "1":
        collectors.append(SeedCollector())

    if os.getenv("TICKETMASTER_API_KEY"):
        collectors.append(TicketmasterCollector())
    else:
        logger.info("TICKETMASTER_API_KEY not set; TicketmasterCollector disabled.")

    return collectors
