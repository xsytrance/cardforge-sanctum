# CardForge

Mobile-first web system that turns folders of text/media/spreadsheets into beautiful, editable trading-card style views.

## Monorepo Layout

- `apps/web` — Next.js frontend (card rendering + editor)
- `apps/api` — FastAPI backend (ingestion, card CRUD, revisions)
- `apps/worker` — background ingestion jobs
- `packages/schema` — canonical CardSchema JSON Schema + examples
- `docs` — product, architecture, and execution plans

## Quick Start (Scaffold Stage)

```bash
cd /home/xsyprime/Apps/cardforge
python3 -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn pydantic
```

This repository currently contains architecture docs and schema definitions for execution kickoff.
