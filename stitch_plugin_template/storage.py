"""SQLite storage for this service plugin.

The plugin owns its own SQLite database at ``db_path`` (received in the
``plugin.init`` handshake).  Tables are created on ``_migrate_db``.
Replace this with your own schema as needed.
"""

# _generated_by: stitch_plugin_tools scaffold v3

from __future__ import annotations

import sqlite3
import uuid
from pathlib import Path
from typing import Any


def _connect(db_path: str) -> sqlite3.Connection:
    """Open a SQLite connection with WAL mode for concurrent reads."""
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def migrate(db_path: str) -> None:
    """Create tables if they do not exist (raw_sql migration).

    Replace with your own schema.  This example creates a simple
    ``items`` table.
    """
    conn = _connect(db_path)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS items (
                id TEXT PRIMARY KEY,
                text TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def list_items(db_path: str) -> list[dict[str, Any]]:
    """Return all items from local storage."""
    conn = _connect(db_path)
    try:
        rows = conn.execute(
            "SELECT id, text FROM items ORDER BY created_at DESC"
        ).fetchall()
        return [{"id": r["id"], "text": r["text"]} for r in rows]
    finally:
        conn.close()


def create_item(db_path: str, text: str) -> dict[str, Any]:
    """Insert an item record and return it."""
    item_id = uuid.uuid4().hex[:12]
    conn = _connect(db_path)
    try:
        conn.execute(
            "INSERT INTO items (id, text) VALUES (?, ?)",
            (item_id, text),
        )
        conn.commit()
    finally:
        conn.close()
    return {"id": item_id, "text": text}
