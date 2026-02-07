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
- `SEED_COLLECTOR` (optional): Set to `1` to enable the local deterministic SeedCollector.
- `TICKETMASTER_API_KEY` (optional): Enables the Ticketmaster collector when set.
- `TICKETMASTER_API_BASE_URL` (optional): Override Ticketmaster discovery API base URL.

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


## Local development collector flow
Use the same `DATABASE_URL` for both API and worker so seeded data appears in the dashboard and API responses:

```bash
export DATABASE_URL=sqlite:///./app.db
export SEED_COLLECTOR=1
python -m app.worker
```

This inserts 10 deterministic seed events (`source=seed`) with one price snapshot per event and is idempotent across reruns.

When you are ready to connect a real official source, set a Ticketmaster API key:

```bash
export TICKETMASTER_API_KEY=your_key_here
python -m app.worker
```

If `TICKETMASTER_API_KEY` is missing, the collector is skipped without errors.

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
