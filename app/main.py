from datetime import datetime, timezone
from typing import Generator

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.db import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Ticket Reselling AI")

templates = Jinja2Templates(directory="app/templates")


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _seed_listing(db: Session) -> models.Listing:
    event = db.scalar(select(models.Event))
    if event is None:
        event = models.Event(
            name="Sample Concert",
            venue="Demo Arena",
            event_date=datetime.now(timezone.utc),
        )
        db.add(event)
        db.flush()
    listing = db.scalar(select(models.Listing).where(models.Listing.event_id == event.id))
    if listing is None:
        listing = models.Listing(event_id=event.id, price=120.0, currency="EUR")
        db.add(listing)
        db.flush()
    return listing


def write_sample_snapshot() -> None:
    db = SessionLocal()
    try:
        listing = _seed_listing(db)
        snapshot = models.PriceSnapshot(
            listing_id=listing.id,
            price=listing.price,
            currency=listing.currency,
            snapped_at=datetime.now(timezone.utc),
        )
        db.add(snapshot)
        db.commit()
    finally:
        db.close()


@app.on_event("startup")
async def start_scheduler() -> None:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(write_sample_snapshot, "interval", minutes=10)
    scheduler.start()
    app.state.scheduler = scheduler


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/events", response_model=list[schemas.EventOut])
async def list_events(db: Session = Depends(get_db)) -> list[schemas.EventOut]:
    return crud.get_events(db)


@app.get("/recommendations")
async def recommendations() -> dict[str, str]:
    return {
        "status": "stub",
        "message": "Recommendation engine will return BUY/SKIP decisions here.",
    }


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})
