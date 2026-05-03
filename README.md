# CardForge

CardForge ingests mixed raw folder data and turns it into editable web cards.

## Features
- Ingest: `.md`, `.txt`, `.json`, `.yaml/.yml`, `.csv`, `.xlsx`
- Auto card type inference: `agent`, `service`, `dataset`, `note`
- Editable cards + revision history + revert
- Source provenance (path/parser/confidence/editable fields)
- Mobile-first neon card deck UI

## Run

### API
```bash
cd apps/api
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 127.0.0.1 --port 18000 --reload
```

### Web
```bash
cd apps/web
python3 -m http.server 13000 --bind 127.0.0.1
```

Open: `http://127.0.0.1:13000`
