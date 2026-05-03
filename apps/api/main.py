from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import CardCreate, CardPatch, IngestFolderRequest, WatchStartRequest
from storage import SQLiteDB
from ingest import ingest_folder
from watcher import IngestWatchManager

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "cardforge.db"

app = FastAPI(title="CardForge API")
db = SQLiteDB(str(DB_PATH))


def _ingest_and_upsert(folder: str, watch_triggered: bool = False):
    result = ingest_folder(folder)
    created_or_updated = []
    for payload in result["cards"]:
        card = db.upsert_card_by_source(payload, reason="watch_ingest" if watch_triggered else "ingest_upsert")
        created_or_updated.append(card["id"])
    return {"count": len(created_or_updated), "card_ids": created_or_updated, "report": result["report"]}


watch_manager = IngestWatchManager(_ingest_and_upsert)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthz")
def healthz():
    return {"ok": True, "db_path": str(DB_PATH)}


@app.post("/cards")
def create_card(payload: CardCreate):
    return db.create_card(payload.model_dump())


@app.get("/cards")
def list_cards():
    return db.list_cards()


@app.get("/cards/{card_id}")
def get_card(card_id: str):
    c = db.get_card(card_id)
    if not c:
        raise HTTPException(404, "Card not found")
    return c


@app.patch("/cards/{card_id}")
def patch_card(card_id: str, payload: CardPatch):
    patch = {k: v for k, v in payload.model_dump().items() if v is not None}
    c = db.update_card(card_id, patch, reason="patch")
    if not c:
        raise HTTPException(404, "Card not found")
    return c


@app.get("/cards/{card_id}/revisions")
def revisions(card_id: str):
    return db.get_revisions(card_id)


@app.post("/cards/{card_id}/revert/{revision_id}")
def revert(card_id: str, revision_id: str):
    c = db.revert(card_id, revision_id)
    if not c:
        raise HTTPException(404, "Card or revision not found")
    return c


@app.post("/ingest/folder")
def ingest(req: IngestFolderRequest):
    try:
        res = _ingest_and_upsert(req.path)
    except FileNotFoundError as e:
        raise HTTPException(400, str(e))
    return {"created_or_updated": res["count"], "card_ids": res["card_ids"], "report": res["report"]}


@app.post("/watch/start")
def watch_start(req: WatchStartRequest):
    try:
        return watch_manager.start(req.path, debounce_seconds=req.debounce_seconds)
    except FileNotFoundError as e:
        raise HTTPException(400, str(e))


@app.post("/watch/stop")
def watch_stop():
    return watch_manager.stop()


@app.get("/watch/status")
def watch_status():
    return watch_manager.status()
