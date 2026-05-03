from __future__ import annotations
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Any, Literal
from datetime import datetime, timezone
import uuid

app = FastAPI(title="CardForge API", version="0.1.0")

CARD_TYPES = Literal["agent", "service", "workspace", "dataset", "generic"]

class Card(BaseModel):
    id: str
    type: CARD_TYPES
    title: str
    subtitle: str | None = None
    description: str | None = None
    stats: list[dict[str, Any]] = Field(default_factory=list)
    traits: list[str] = Field(default_factory=list)
    sections: list[dict[str, Any]] = Field(default_factory=list)
    source: dict[str, Any] | None = None
    editableFields: list[str] = Field(default_factory=list)
    updatedAt: datetime
    revision: int = 1

class CreateCard(BaseModel):
    type: CARD_TYPES
    title: str
    subtitle: str | None = None
    description: str | None = None

class PatchCard(BaseModel):
    title: str | None = None
    subtitle: str | None = None
    description: str | None = None
    traits: list[str] | None = None
    sections: list[dict[str, Any]] | None = None

CARDS: dict[str, Card] = {}
REVISIONS: dict[str, list[Card]] = {}


def now() -> datetime:
    return datetime.now(timezone.utc)

@app.get('/healthz')
def healthz() -> dict[str, str]:
    return {"status": "ok", "service": "cardforge-api"}

@app.get('/cards', response_model=list[Card])
def list_cards() -> list[Card]:
    return list(CARDS.values())

@app.post('/cards', response_model=Card)
def create_card(payload: CreateCard) -> Card:
    cid = str(uuid.uuid4())
    card = Card(
        id=cid,
        type=payload.type,
        title=payload.title,
        subtitle=payload.subtitle,
        description=payload.description,
        updatedAt=now(),
        editableFields=["title", "subtitle", "description", "traits", "sections"],
    )
    CARDS[cid] = card
    REVISIONS[cid] = [card]
    return card

@app.get('/cards/{card_id}', response_model=Card)
def get_card(card_id: str) -> Card:
    card = CARDS.get(card_id)
    if not card:
        raise HTTPException(status_code=404, detail='card not found')
    return card

@app.patch('/cards/{card_id}', response_model=Card)
def patch_card(card_id: str, payload: PatchCard) -> Card:
    card = CARDS.get(card_id)
    if not card:
        raise HTTPException(status_code=404, detail='card not found')

    data = card.model_dump()
    update = payload.model_dump(exclude_unset=True)
    data.update(update)
    data['revision'] = card.revision + 1
    data['updatedAt'] = now()

    updated = Card(**data)
    CARDS[card_id] = updated
    REVISIONS[card_id].append(updated)
    return updated

@app.get('/cards/{card_id}/revisions', response_model=list[Card])
def list_revisions(card_id: str) -> list[Card]:
    revs = REVISIONS.get(card_id)
    if not revs:
        raise HTTPException(status_code=404, detail='card not found')
    return revs

@app.post('/cards/{card_id}/revert/{revision}', response_model=Card)
def revert_card(card_id: str, revision: int) -> Card:
    revs = REVISIONS.get(card_id)
    if not revs:
        raise HTTPException(status_code=404, detail='card not found')

    target = None
    for r in revs:
        if r.revision == revision:
            target = r
            break
    if not target:
        raise HTTPException(status_code=404, detail='revision not found')

    data = target.model_dump()
    data['revision'] = CARDS[card_id].revision + 1
    data['updatedAt'] = now()
    restored = Card(**data)
    CARDS[card_id] = restored
    REVISIONS[card_id].append(restored)
    return restored

@app.post('/ingest/folder')
def ingest_folder(path: str) -> dict[str, Any]:
    # Stub for v1 parser pipeline
    return {
        'status': 'accepted',
        'path': path,
        'message': 'Ingestion pipeline scaffolded. Parser workers to be attached in Phase 2.'
    }
