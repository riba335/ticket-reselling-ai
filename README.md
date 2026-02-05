# Ticket Reselling AI — MVP Foundation

Decision-support system for ticket reselling. This MVP exposes basic API endpoints, a minimal dashboard, and a scheduler stub that writes sample price snapshots every 10 minutes.

## Requirements
- Python 3.11+
- SQLite (default) or PostgreSQL

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Environment variables
- `DATABASE_URL` (optional): SQLAlchemy database URL. Defaults to `sqlite:///./app.db`.
- `EXAMPLE_API_KEY` (optional): API key for the ExampleCollector (official API placeholder).
- `EXAMPLE_API_BASE_URL` (optional): Override ExampleCollector base URL (defaults to `https://api.example.com/v1/events`).

Example for PostgreSQL:
```
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/ticket_reselling
```

## Database migrations
```bash
alembic upgrade head
```

## Run the API
```bash
uvicorn app.main:app --reload
```

Endpoints:
- `GET /health`
- `GET /events` (reads from DB)
- `GET /recommendations` (stub)
- `GET /collector/status` (recent collector runs per source)
- `GET /` dashboard page listing events

## Scheduler stub
On startup, the API schedules a background job every 10 minutes that writes a sample price snapshot and seeds a sample event/listing if needed.

## Collector worker
Run the collector loop every 10 minutes via APScheduler:
```bash
python -m app.worker
```

## Testing
```bash
ruff check .
pytest
```
