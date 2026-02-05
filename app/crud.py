from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models


def get_events(db: Session) -> list[models.Event]:
    return list(db.scalars(select(models.Event).order_by(models.Event.event_date)))
