# CardForge

CardForge converts raw files into editable website cards for agents, services, notes, and datasets.

## Why this exists
AI operators and autonomous agents need a deterministic path from messy raw data to structured visual artifacts.
CardForge is that path: ingest, infer, normalize, persist, render, revise.

## Core capabilities
- Ingest mixed folder data (`md/txt/json/yaml/csv/xlsx`)
- Infer card types (`agent`, `service`, `dataset`, `note`)
- Persist cards + revision history in SQLite
- Upsert by source path (watch mode does not spam duplicate cards)
- Render editable card deck in browser
- Render dataset charts in-card (Chart.js)
- Watch folders for file changes and auto-reingest

## Quickstart
### 1) Start API
```bash
cd apps/api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 127.0.0.1 --port 18000 --reload
```

### 2) Start web UI
```bash
cd apps/web
python3 -m http.server 13000 --bind 127.0.0.1
```
Open `http://127.0.0.1:13000`

### 3) Ingest a folder
Use UI input + **Ingest Folder**, or API:
```bash
curl -s -X POST http://127.0.0.1:18000/ingest/folder   -H 'content-type: application/json'   -d '{"path":"/absolute/path/to/data"}'
```

## Repository map
- `apps/api/` FastAPI backend + SQLite + watcher
- `apps/web/` static frontend (cards + charts)
- `packages/schema/` JSON schema
- `docs/` operations + agent documentation

## Agent-first docs
Start here:
1. `docs/AGENT_PLAYBOOK.md`
2. `docs/API_REFERENCE.md`
3. `docs/INGESTION_SPEC.md`
4. `docs/ARCHITECTURE.md`
5. `docs/OPERATIONS_RUNBOOK.md`
