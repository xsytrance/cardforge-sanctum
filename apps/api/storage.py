from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List
import uuid


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Revision:
    id: str
    card_id: str
    at: str
    reason: str
    snapshot: Dict[str, Any]


@dataclass
class Card:
    id: str
    type: str
    title: str
    subtitle: str = ""
    description: str = ""
    fields: Dict[str, Any] = field(default_factory=dict)
    source: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utcnow_iso)
    updated_at: str = field(default_factory=utcnow_iso)


class InMemoryDB:
    def __init__(self):
        self.cards: Dict[str, Card] = {}
        self.revisions: Dict[str, List[Revision]] = {}

    def create_card(self, payload: Dict[str, Any]) -> Card:
        c = Card(id=str(uuid.uuid4()), **payload)
        self.cards[c.id] = c
        self.revisions[c.id] = [Revision(
            id=str(uuid.uuid4()), card_id=c.id, at=utcnow_iso(), reason="create", snapshot=self.serialize(c)
        )]
        return c

    def list_cards(self) -> List[Card]:
        return list(self.cards.values())

    def get_card(self, card_id: str) -> Card | None:
        return self.cards.get(card_id)

    def update_card(self, card_id: str, patch: Dict[str, Any], reason: str = "update") -> Card | None:
        c = self.cards.get(card_id)
        if not c:
            return None
        for k, v in patch.items():
            if hasattr(c, k):
                setattr(c, k, v)
        c.updated_at = utcnow_iso()
        self.revisions[card_id].append(Revision(
            id=str(uuid.uuid4()), card_id=card_id, at=utcnow_iso(), reason=reason, snapshot=self.serialize(c)
        ))
        return c

    def get_revisions(self, card_id: str) -> List[Revision]:
        return self.revisions.get(card_id, [])

    def revert(self, card_id: str, revision_id: str) -> Card | None:
        c = self.cards.get(card_id)
        if not c:
            return None
        rev = next((r for r in self.revisions.get(card_id, []) if r.id == revision_id), None)
        if not rev:
            return None
        snap = rev.snapshot
        for k, v in snap.items():
            if hasattr(c, k):
                setattr(c, k, v)
        c.updated_at = utcnow_iso()
        self.revisions[card_id].append(Revision(
            id=str(uuid.uuid4()), card_id=card_id, at=utcnow_iso(), reason=f"revert:{revision_id}", snapshot=self.serialize(c)
        ))
        return c

    @staticmethod
    def serialize(card: Card) -> Dict[str, Any]:
        return {
            "id": card.id,
            "type": card.type,
            "title": card.title,
            "subtitle": card.subtitle,
            "description": card.description,
            "fields": card.fields,
            "source": card.source,
            "created_at": card.created_at,
            "updated_at": card.updated_at,
        }
