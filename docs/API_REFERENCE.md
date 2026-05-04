# CardForge Sanctum API Reference

Base URL: `http://127.0.0.1:18000`

## Health
### GET `/healthz`
Returns API health and database path.

## Cards
### POST `/cards`
Create a card manually.

### GET `/cards`
List cards, newest first by `updated_at`.

### GET `/cards/{card_id}`
Fetch one card.

### PATCH `/cards/{card_id}`
Patch editable fields.

### GET `/cards/{card_id}/revisions`
List revision snapshots for card.

### POST `/cards/{card_id}/revert/{revision_id}`
Revert card to revision snapshot.

## Ingestion
### POST `/ingest/folder`
Body:
```json
{"path":"/absolute/path"}
```
Behavior:
- parses supported files
- infers card type
- upserts by `source.path`
- records revisions (`ingest_upsert`)

## Watch mode
### POST `/watch/start`
Body:
```json
{"path":"/absolute/path","debounce_seconds":2}
```
Starts recursive folder watch.

### POST `/watch/stop`
Stops active watch observer.

### GET `/watch/status`
Returns current watch state counters and timestamps.
