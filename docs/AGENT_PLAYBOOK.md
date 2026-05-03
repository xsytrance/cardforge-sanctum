# Agent Playbook: Build Cards from Raw Data

This guide is designed for autonomous coding/ops agents.

## Mission objective
Transform folder data into editable visual cards with provenance and revisions.

## Deterministic workflow
1. Validate API health (`GET /healthz`).
2. Run ingest (`POST /ingest/folder`).
3. Verify parse stats and errors in report.
4. Query cards (`GET /cards`) and count expected output.
5. For datasets, verify `table_preview` + chart renderability.
6. If using live sync, start watch (`POST /watch/start`).
7. Make source file change; confirm `watch/status.ingests_triggered` increments.

## Golden commands
```bash
curl -s http://127.0.0.1:18000/healthz
curl -s -X POST http://127.0.0.1:18000/ingest/folder -H 'content-type: application/json' -d '{"path":"/data"}'
curl -s http://127.0.0.1:18000/cards
curl -s -X POST http://127.0.0.1:18000/watch/start -H 'content-type: application/json' -d '{"path":"/data","debounce_seconds":2}'
curl -s http://127.0.0.1:18000/watch/status
```

## Agent extension points
- Add parsers in `apps/api/ingest.py`
- Add new inference signals in `KEY_PATTERNS` + `infer_type`
- Add chart synthesis rules in `apps/web/app.js` (`buildChartData`)
- Add governance metadata in `source` object

## Non-negotiable invariants
- No destructive mutation of source files during ingest.
- Every card mutation creates a revision snapshot.
- Watch mode must upsert, not duplicate, for same `source.path`.
