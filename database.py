"""Durable local storage for Vela's preview and single-server deployment."""

from __future__ import annotations

import json
import os
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

DB_PATH = Path(os.getenv("VELA_DB_PATH", "vela.db"))


@contextmanager
def connection() -> Iterator[sqlite3.Connection]:
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            database = sqlite3.connect(DB_PATH, timeout=15)
            database.row_factory = sqlite3.Row
            database.execute("PRAGMA foreign_keys = ON")
            database.execute("PRAGMA journal_mode = WAL")
            database.execute("PRAGMA busy_timeout = 15000")
            try:
                yield database
                database.commit()
                return
            except Exception:
                database.rollback()
                raise
            finally:
                database.close()
        except sqlite3.OperationalError as error:
            last_error = error
            if attempt == 2:
                raise
            time.sleep(0.25 * (attempt + 1))
    if last_error:
        raise last_error


def initialize(default_chats: list[dict[str, Any]], default_posts: list[dict[str, Any]]) -> None:
    with connection() as database:
        database.executescript(
            """
            CREATE TABLE IF NOT EXISTS chats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                initials TEXT NOT NULL,
                color TEXT NOT NULL,
                preview TEXT NOT NULL,
                status TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL REFERENCES chats(id) ON DELETE CASCADE,
                direction TEXT NOT NULL,
                kind TEXT NOT NULL DEFAULT 'text',
                content BLOB NOT NULL,
                sent_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS feed_posts (
                id REAL PRIMARY KEY,
                author TEXT NOT NULL,
                initials TEXT NOT NULL,
                color TEXT NOT NULL,
                posted_at TEXT NOT NULL,
                text TEXT NOT NULL,
                media_name TEXT,
                media_size INTEGER,
                media_type TEXT,
                likes INTEGER NOT NULL DEFAULT 0,
                liked INTEGER NOT NULL DEFAULT 0,
                comments TEXT NOT NULL DEFAULT '[]'
            );
            """
        )
        for chat in default_chats:
            database.execute(
                "INSERT OR IGNORE INTO chats (name, initials, color, preview, status) VALUES (?, ?, ?, ?, ?)",
                (chat["name"], chat["initials"], chat["color"], chat["preview"], chat["status"]),
            )
        chat_count = database.execute("SELECT COUNT(*) AS count FROM messages").fetchone()["count"]
        if chat_count == 0:
            for chat in default_chats:
                chat_id = database.execute("SELECT id FROM chats WHERE name = ?", (chat["name"],)).fetchone()["id"]
                for direction, content, sent_at in chat["messages"]:
                    add_message(database, chat_id, direction, "text", content, sent_at)
        for post in default_posts:
            database.execute(
                """
                INSERT OR IGNORE INTO feed_posts
                (id, author, initials, color, posted_at, text, likes, liked, comments)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (post["id"], post["author"], post["initials"], post["color"], post["time"], post["text"], post["likes"], int(post["liked"]), json.dumps(post["comments"])),
            )


def add_message(database: sqlite3.Connection, chat_id: int, direction: str, kind: str, content: str | bytes, sent_at: str) -> None:
    value = content if isinstance(content, bytes) else content.encode("utf-8")
    database.execute(
        "INSERT INTO messages (chat_id, direction, kind, content, sent_at) VALUES (?, ?, ?, ?, ?)",
        (chat_id, direction, kind, value, sent_at),
    )


def load_chats() -> list[dict[str, Any]]:
    with connection() as database:
        chats = database.execute("SELECT * FROM chats ORDER BY id").fetchall()
        result = []
        for chat in chats:
            messages = database.execute("SELECT direction, kind, content, sent_at FROM messages WHERE chat_id = ? ORDER BY id", (chat["id"],)).fetchall()
            parsed_messages = []
            for message in messages:
                content = bytes(message["content"])
                value: str | bytes = content if message["kind"] == "voice" else content.decode("utf-8")
                parsed_messages.append((message["direction"] if message["kind"] != "voice" else "voice", value, message["sent_at"]))
            result.append({"name": chat["name"], "initials": chat["initials"], "color": chat["color"], "preview": chat["preview"], "status": chat["status"], "messages": parsed_messages})
        return result


def save_message(chat_name: str, direction: str, content: str | bytes, sent_at: str, kind: str = "text", preview: str | None = None) -> None:
    with connection() as database:
        chat = database.execute("SELECT id FROM chats WHERE name = ?", (chat_name,)).fetchone()
        if chat is None:
            raise ValueError(f"Unknown chat: {chat_name}")
        add_message(database, chat["id"], direction, kind, content, sent_at)
        if preview is not None:
            database.execute("UPDATE chats SET preview = ? WHERE id = ?", (preview, chat["id"]))


def load_posts() -> list[dict[str, Any]]:
    with connection() as database:
        posts = database.execute("SELECT * FROM feed_posts ORDER BY id DESC").fetchall()
        return [{"id": post["id"], "author": post["author"], "initials": post["initials"], "color": post["color"], "time": post["posted_at"], "text": post["text"], "media": None, "media_name": post["media_name"], "media_size": post["media_size"], "media_type": post["media_type"], "likes": post["likes"], "liked": bool(post["liked"]), "comments": json.loads(post["comments"])} for post in posts]


def save_post(post: dict[str, Any]) -> None:
    media = post.get("media")
    with connection() as database:
        database.execute(
            "INSERT OR REPLACE INTO feed_posts (id, author, initials, color, posted_at, text, media_name, media_size, media_type, likes, liked, comments) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (post["id"], post["author"], post["initials"], post["color"], post["time"], post["text"], getattr(media, "name", None), getattr(media, "size", None), getattr(media, "type", None), post["likes"], int(post["liked"]), json.dumps(post["comments"])),
        )


def health_check() -> bool:
    with connection() as database:
        database.execute("SELECT 1").fetchone()
    return True
