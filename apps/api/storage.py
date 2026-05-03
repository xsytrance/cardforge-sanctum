from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import sqlite3
import uuid


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class SQLiteDB:
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _conn(self):
        c = sqlite3.connect(self.db_path)
        c.row_factory = sqlite3.Row
        return c

    def _init_schema(self):
        with self._conn() as con:
            con.executescript(
                """
                CREATE TABLE IF NOT EXISTS cards (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    subtitle TEXT NOT NULL DEFAULT '',
                    description TEXT NOT NULL DEFAULT '',
                    fields_json TEXT NOT NULL DEFAULT '{}',
                    source_json TEXT NOT NULL DEFAULT '{}',
                    source_path TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE UNIQUE INDEX IF NOT EXISTS idx_cards_source_path
                ON cards(source_path) WHERE source_path IS NOT NULL;

                CREATE TABLE IF NOT EXISTS revisions (
                    id TEXT PRIMARY KEY,
                    card_id TEXT NOT NULL,
                    at TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    snapshot_json TEXT NOT NULL,
                    FOREIGN KEY(card_id) REFERENCES cards(id) ON DELETE CASCADE
                );
                CREATE INDEX IF NOT EXISTS idx_revisions_card_at ON revisions(card_id, at);
                """
            )

    @staticmethod
    def _row_to_card(row: sqlite3.Row) -> Dict[str, Any]:
        return {
            "id": row["id"],
            "type": row["type"],
            "title": row["title"],
            "subtitle": row["subtitle"],
            "description": row["description"],
            "fields": json.loads(row["fields_json"] or "{}"),
            "source": json.loads(row["source_json"] or "{}"),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }

    def create_card(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        card_id = str(uuid.uuid4())
        now = utcnow_iso()
        source = payload.get("source", {}) or {}
        source_path = source.get("path")
        card = {
            "id": card_id,
            "type": payload["type"],
            "title": payload["title"],
            "subtitle": payload.get("subtitle", ""),
            "description": payload.get("description", ""),
            "fields": payload.get("fields", {}) or {},
            "source": source,
            "created_at": now,
            "updated_at": now,
        }
        with self._conn() as con:
            con.execute(
                """
                INSERT INTO cards (id, type, title, subtitle, description, fields_json, source_json, source_path, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    card["id"], card["type"], card["title"], card["subtitle"], card["description"],
                    json.dumps(card["fields"]), json.dumps(card["source"]), source_path,
                    card["created_at"], card["updated_at"],
                ),
            )
            self._insert_revision(con, card_id, "create", card)
        return card

    def upsert_card_by_source(self, payload: Dict[str, Any], reason: str = "ingest_upsert") -> Dict[str, Any]:
        source = payload.get("source", {}) or {}
        source_path = source.get("path")
        if not source_path:
            return self.create_card(payload)

        with self._conn() as con:
            row = con.execute("SELECT * FROM cards WHERE source_path = ?", (source_path,)).fetchone()
            if not row:
                return self.create_card(payload)

            card_id = row["id"]
            now = utcnow_iso()
            con.execute(
                """
                UPDATE cards
                SET type=?, title=?, subtitle=?, description=?, fields_json=?, source_json=?, updated_at=?
                WHERE id=?
                """,
                (
                    payload["type"], payload["title"], payload.get("subtitle", ""), payload.get("description", ""),
                    json.dumps(payload.get("fields", {}) or {}), json.dumps(source), now, card_id,
                ),
            )
            updated = self.get_card(card_id)
            self._insert_revision(con, card_id, reason, updated)
            return updated

    def list_cards(self) -> List[Dict[str, Any]]:
        with self._conn() as con:
            rows = con.execute("SELECT * FROM cards ORDER BY updated_at DESC").fetchall()
        return [self._row_to_card(r) for r in rows]

    def get_card(self, card_id: str) -> Optional[Dict[str, Any]]:
        with self._conn() as con:
            row = con.execute("SELECT * FROM cards WHERE id=?", (card_id,)).fetchone()
        return self._row_to_card(row) if row else None

    def update_card(self, card_id: str, patch: Dict[str, Any], reason: str = "update") -> Optional[Dict[str, Any]]:
        current = self.get_card(card_id)
        if not current:
            return None
        for key in ["type", "title", "subtitle", "description", "fields", "source"]:
            if key in patch and patch[key] is not None:
                current[key] = patch[key]
        current["updated_at"] = utcnow_iso()
        source_path = (current.get("source") or {}).get("path")

        with self._conn() as con:
            con.execute(
                """
                UPDATE cards
                SET type=?, title=?, subtitle=?, description=?, fields_json=?, source_json=?, source_path=?, updated_at=?
                WHERE id=?
                """,
                (
                    current["type"], current["title"], current.get("subtitle", ""), current.get("description", ""),
                    json.dumps(current.get("fields", {}) or {}), json.dumps(current.get("source", {}) or {}), source_path,
                    current["updated_at"], card_id,
                ),
            )
            self._insert_revision(con, card_id, reason, current)
        return current

    def get_revisions(self, card_id: str) -> List[Dict[str, Any]]:
        with self._conn() as con:
            rows = con.execute("SELECT * FROM revisions WHERE card_id=? ORDER BY at DESC", (card_id,)).fetchall()
        return [
            {
                "id": r["id"],
                "card_id": r["card_id"],
                "at": r["at"],
                "reason": r["reason"],
                "snapshot": json.loads(r["snapshot_json"]),
            }
            for r in rows
        ]

    def revert(self, card_id: str, revision_id: str) -> Optional[Dict[str, Any]]:
        with self._conn() as con:
            row = con.execute("SELECT * FROM revisions WHERE id=? AND card_id=?", (revision_id, card_id)).fetchone()
            if not row:
                return None
            snap = json.loads(row["snapshot_json"])
        return self.update_card(card_id, snap, reason=f"revert:{revision_id}")

    def _insert_revision(self, con: sqlite3.Connection, card_id: str, reason: str, snapshot: Dict[str, Any]):
        con.execute(
            "INSERT INTO revisions (id, card_id, at, reason, snapshot_json) VALUES (?, ?, ?, ?, ?)",
            (str(uuid.uuid4()), card_id, utcnow_iso(), reason, json.dumps(snapshot)),
        )
