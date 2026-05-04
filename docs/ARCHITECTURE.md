# CardForge Sanctum Architecture

## Pipeline
1. **Discovery**: recursively enumerate files under folder.
2. **Parsing** by extension:
   - text: `.md/.txt`
   - structured: `.json/.yaml/.yml`
   - tabular: `.csv/.xlsx`
3. **Normalization** to common card payload shape.
4. **Type inference** (`agent/service/dataset/note`) + confidence score.
5. **Persistence**: SQLite upsert on `source.path`.
6. **Revisioning**: every create/update/revert writes a snapshot row.
7. **Visualization**: web renders editable cards + dataset charts.

## Components
- `apps/api/ingest.py` parser and inference engine
- `apps/api/storage.py` SQLite data access + revision system
- `apps/api/watcher.py` filesystem observer + debounce-triggered reingest
- `apps/api/main.py` API orchestration and endpoints
- `apps/web/app.js` UI logic, inline edits, chart rendering

## Data model (logical)
Card:
- identity: `id`, `type`, `title`
- editable display: `subtitle`, `description`
- payload: `fields` (arbitrary JSON)
- provenance: `source` (path, parser, confidence, editable_fields)
- lifecycle: `created_at`, `updated_at`

Revision:
- `id`, `card_id`, `at`, `reason`, `snapshot`

## Persistence strategy
- SQLite for local reliability and agent portability.
- Unique index on `source_path` to make watch-upsert deterministic.
- Revisions store complete snapshot JSON for simple rollbacks.
