from datetime import datetime

from pydantic import BaseModel


class EventOut(BaseModel):
    id: int
    name: str
    venue: str
    event_date: datetime

    class Config:
        from_attributes = True
