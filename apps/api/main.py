from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import CardCreate, CardPatch, IngestFolderRequest
from storage import InMemoryDB
from ingest import ingest_folder

app = FastAPI(title="CardForge API")
db = InMemoryDB()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/healthz')
def healthz():
    return {'ok': True}


@app.post('/cards')
def create_card(payload: CardCreate):
    c = db.create_card(payload.model_dump())
    return db.serialize(c)


@app.get('/cards')
def list_cards():
    return [db.serialize(c) for c in db.list_cards()]


@app.get('/cards/{card_id}')
def get_card(card_id: str):
    c = db.get_card(card_id)
    if not c:
        raise HTTPException(404, 'Card not found')
    return db.serialize(c)


@app.patch('/cards/{card_id}')
def patch_card(card_id: str, payload: CardPatch):
    patch = {k:v for k,v in payload.model_dump().items() if v is not None}
    c = db.update_card(card_id, patch, reason='patch')
    if not c:
        raise HTTPException(404, 'Card not found')
    return db.serialize(c)


@app.get('/cards/{card_id}/revisions')
def revisions(card_id: str):
    revs = db.get_revisions(card_id)
    return [r.__dict__ for r in revs]


@app.post('/cards/{card_id}/revert/{revision_id}')
def revert(card_id: str, revision_id: str):
    c = db.revert(card_id, revision_id)
    if not c:
        raise HTTPException(404, 'Card or revision not found')
    return db.serialize(c)


@app.post('/ingest/folder')
def ingest(req: IngestFolderRequest):
    try:
        result = ingest_folder(req.path)
    except FileNotFoundError as e:
        raise HTTPException(400, str(e))

    created_ids = []
    for payload in result['cards']:
        c = db.create_card(payload)
        created_ids.append(c.id)

    return {'created': len(created_ids), 'card_ids': created_ids, 'report': result['report']}
