# AI Ticket Reselling System 2.0 — Rules

Goal:
- Decision-support system for ticket reselling: find opportunities and output BUY/SKIP with reasons.

Hard rules:
- No automated purchasing.
- No bypassing anti-bot protections.
- Use official APIs or permitted sources only.
- Never commit secrets (keys/tokens).

MVP Foundation (build this first):
- Backend API: GET /health, GET /events, GET /recommendations (stub ok)
- DB schema: events, listings, price_snapshots
- Job stub: runs every 10 minutes, writes a sample snapshot
- Minimal dashboard page listing events
- README: setup + env vars + how to run
- CI: lint + tests

Business settings:
- Alert rule (later): AttractiScore > 75 and profit > 30 EUR triggers WhatsApp alert.
