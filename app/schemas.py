from datetime import datetime

from pydantic import BaseModel


class EventOut(BaseModel):
    id: int
    name: str
    venue: str
    event_date: datetime
    source: str
    external_id: str
    source_url: str | None = None

    class Config:
        from_attributes = True


class CollectorRunOut(BaseModel):
    id: int
    source: str
    started_at: datetime
    finished_at: datetime | None
    status: str
    items_fetched: int
    items_upserted: int
    error_message: str | None

    class Config:
        from_attributes = True
