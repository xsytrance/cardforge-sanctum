# CardForge Phase 2 Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Add persistence, live chart rendering, file-watch reingest, and deep agent documentation.

**Architecture:** Replace volatile in-memory storage with SQLite + revision table, add watch subsystem with debounce and source-path upsert, and enrich frontend with chart rendering from dataset previews.

**Tech Stack:** FastAPI, sqlite3, watchdog, Chart.js, static HTML/CSS/JS.

---

### Task 1: Replace in-memory storage with SQLite
- Files: `apps/api/storage.py`, `apps/api/main.py`
- Deliverables: tables (`cards`,`revisions`), CRUD, revision snapshots, upsert by source path.

### Task 2: Add watch mode
- Files: `apps/api/watcher.py`, `apps/api/models.py`, `apps/api/main.py`
- Deliverables: `/watch/start`, `/watch/stop`, `/watch/status` with debounce behavior.

### Task 3: Add dataset chart rendering
- Files: `apps/web/index.html`, `apps/web/app.js`, `apps/web/styles.css`
- Deliverables: chart canvas in cards + Chart.js rendering for numeric series.

### Task 4: Documentation expansion
- Files: `README.md`, `docs/*.md`
- Deliverables: architecture, API ref, ingestion spec, ops runbook, agent playbook.

### Task 5: End-to-end validation
- Commands: health, ingest, list cards, edit/revision, watch trigger.
- Deliverables: reproducible verification log.
