"""Download history: what was downloaded, when, and where it was saved."""

import os
import time
import uuid

import appdata

FILE = "history.json"
LIMIT = 2000


def entries():
    return appdata.load_json(FILE, [])


def add(title, url, files, kind="video", site=""):
    items = entries()
    items.insert(0, {"id": uuid.uuid4().hex, "time": time.time(), "title": title or url,
                     "url": url, "files": [os.path.abspath(f) for f in files],
                     "kind": kind, "site": site})
    appdata.save_json(FILE, items[:LIMIT])


def search(query=""):
    q = query.strip().lower()
    return [e for e in entries()
            if not q or q in e["title"].lower() or q in e["url"].lower()
            or any(q in os.path.basename(f).lower() for f in e["files"])]


def remove(entry_id):
    appdata.save_json(FILE, [e for e in entries() if e["id"] != entry_id])


def main_file(entry):
    """The biggest file that still exists (the video itself, not its subtitles)."""
    files = [f for f in entry["files"] if os.path.isfile(f)]
    return max(files, key=os.path.getsize) if files else None
