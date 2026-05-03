# Operations Runbook

## Start services
API:
```bash
cd apps/api && source .venv/bin/activate && uvicorn main:app --host 127.0.0.1 --port 18000
```
Web:
```bash
cd apps/web && python3 -m http.server 13000 --bind 127.0.0.1
```

## Validation checklist
- [ ] `/healthz` returns `ok: true`
- [ ] ingest on sample folder returns `created_or_updated > 0`
- [ ] `/cards` returns records with provenance
- [ ] dataset cards display chart in UI
- [ ] edit card and verify new revision exists
- [ ] revert card revision works
- [ ] watch start/status/stop all function

## Common issues
1. `Folder not found` on ingest/watch
   - Use absolute path and ensure directory exists.
2. No chart visible
   - Ensure `table_preview` has numeric column beyond first key.
3. Duplicate cards after watch
   - Ensure `source.path` is present and stable.
4. Missing Python dependency
   - reinstall: `pip install -r apps/api/requirements.txt`

## Backup/restore SQLite
DB path: `apps/api/cardforge.db`
```bash
cp apps/api/cardforge.db /tmp/cardforge.db.bak
```
