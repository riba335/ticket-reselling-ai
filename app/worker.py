from __future__ import annotations

import logging
from datetime import timezone

from apscheduler.schedulers.blocking import BlockingScheduler

from app.collectors.registry import get_enabled_collectors
from app.db import SessionLocal

logger = logging.getLogger(__name__)


def run_collectors() -> None:
    collectors = get_enabled_collectors()
    if not collectors:
        logger.warning("No collectors enabled.")
        return

    db = SessionLocal()
    try:
        for collector in collectors:
            logger.info("Running collector: %s", collector.name)
            collector.run(db)
    finally:
        db.close()


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    scheduler = BlockingScheduler(timezone=timezone.utc)
    scheduler.add_job(
        run_collectors,
        "interval",
        minutes=10,
        coalesce=True,
        max_instances=1,
        misfire_grace_time=300,
    )
    logger.info("Collector worker started.")
    scheduler.start()


if __name__ == "__main__":
    main()
