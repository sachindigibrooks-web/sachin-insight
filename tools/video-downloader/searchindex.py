"""Search the words spoken inside downloaded videos.

Every subtitle line (from the site or from the AI) is stored with its start
time in a local SQLite full-text index. The trigram tokenizer matches any
part of a word in any script, so Hindi and English searches both work.
"""

import os
import sqlite3
import threading
import uuid

import appdata

_lock = threading.Lock()


def _db():
    con = sqlite3.connect(os.path.join(appdata.folder(), "search.db"))
    con.execute("CREATE TABLE IF NOT EXISTS videos (id TEXT PRIMARY KEY, path TEXT UNIQUE, title TEXT)")
    con.execute("CREATE VIRTUAL TABLE IF NOT EXISTS lines USING fts5("
                "video_id UNINDEXED, start UNINDEXED, text, tokenize='trigram')")
    return con


def add(path, title, lines):
    """Index a video's subtitle lines [(start, end, text)], replacing any older entry."""
    path = os.path.abspath(path)
    with _lock, _db() as con:
        old = con.execute("SELECT id FROM videos WHERE path = ?", (path,)).fetchone()
        if old:
            con.execute("DELETE FROM lines WHERE video_id = ?", old)
            con.execute("DELETE FROM videos WHERE id = ?", old)
        vid = uuid.uuid4().hex
        con.execute("INSERT INTO videos VALUES (?, ?, ?)", (vid, path, title))
        con.executemany("INSERT INTO lines VALUES (?, ?, ?)",
                        [(vid, float(a), text) for a, _, text in lines if text.strip()])
    return vid


def is_indexed(path):
    with _lock, _db() as con:
        return con.execute("SELECT 1 FROM videos WHERE path = ?",
                           (os.path.abspath(path),)).fetchone() is not None


def video(vid):
    with _lock, _db() as con:
        row = con.execute("SELECT path, title FROM videos WHERE id = ?", (vid,)).fetchone()
    return {"path": row[0], "title": row[1]} if row else None


def search(query, limit=200):
    """[{video_id, title, path, start, text}] for lines containing `query`, newest videos first."""
    q = query.strip()
    if len(q) < 3:  # trigram index: shorter text can't be matched
        return []
    phrase = '"' + q.replace('"', '""') + '"'
    with _lock, _db() as con:
        rows = con.execute(
            "SELECT l.video_id, v.title, v.path, l.start, l.text FROM lines l "
            "JOIN videos v ON v.id = l.video_id WHERE lines MATCH ? "
            "ORDER BY v.rowid DESC, l.start LIMIT ?", (phrase, limit)).fetchall()
    return [{"video_id": r[0], "title": r[1], "path": r[2], "start": r[3], "text": r[4]}
            for r in rows if os.path.isfile(r[2])]


def count():
    with _lock, _db() as con:
        return con.execute("SELECT COUNT(*) FROM videos").fetchone()[0]
