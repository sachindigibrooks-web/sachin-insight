"""Crawl storage: one SQLite file per crawl, plus a small index of all crawls."""

import json
import os
import sqlite3
import sys
import threading
import time
import uuid

PAGE_COLUMNS = [
    "url", "internal", "depth", "source", "status", "error", "content_type", "size", "time_ms",
    "redirect_to", "title", "titles", "meta_desc", "meta_descs", "h1", "h2s", "canonical",
    "meta_robots", "x_robots", "words", "text_hash", "simhash", "lang", "viewport", "og",
    "jsonld", "jsonld_bad", "hsts", "mixed", "blocked", "resource",
    "rendered", "raw_words", "raw_links", "render_error", "a11y", "link_score",
]
TEXT_COLUMNS = {"url", "source", "error", "content_type", "redirect_to", "title", "meta_desc", "h1",
                "canonical", "meta_robots", "x_robots", "text_hash", "lang", "render_error", "a11y"}


def folder(*parts):
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~\\AppData\\Local")
    elif sys.platform == "darwin":
        base = os.path.expanduser("~/Library/Application Support")
    else:
        base = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
    path = os.path.join(base, "FreeSEOCrawler", *parts)
    os.makedirs(path, exist_ok=True)
    return path


def load_settings():
    """App settings: PageSpeed key, Telegram / e-mail alerts, report branding."""
    try:
        with open(os.path.join(folder(), "settings.json"), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def save_settings(values):
    data = load_settings()
    data.update(values)
    path = os.path.join(folder(), "settings.json")
    with open(path + ".tmp", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    os.replace(path + ".tmp", path)
    return data


def _index():
    con = sqlite3.connect(os.path.join(folder(), "crawls.db"))
    con.execute("CREATE TABLE IF NOT EXISTS crawls (id TEXT PRIMARY KEY, start_url TEXT, "
                "started REAL, finished REAL, pages INTEGER, status TEXT, settings TEXT)")
    return con


def new_crawl(start_url, settings):
    cid = time.strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:6]
    with _index() as con:
        con.execute("INSERT INTO crawls VALUES (?, ?, ?, NULL, 0, 'running', ?)",
                    (cid, start_url, time.time(), json.dumps(settings)))
    return cid


def finish_crawl(cid, pages, status):
    with _index() as con:
        con.execute("UPDATE crawls SET finished = ?, pages = ?, status = ? WHERE id = ?",
                    (time.time(), pages, status, cid))


def crawls():
    with _index() as con:
        rows = con.execute("SELECT id, start_url, started, finished, pages, status FROM crawls "
                           "ORDER BY started DESC").fetchall()
    return [dict(zip(("id", "start_url", "started", "finished", "pages", "status"), r)) for r in rows]


def delete_crawl(cid):
    with _index() as con:
        con.execute("DELETE FROM crawls WHERE id = ?", (cid,))
    try:
        os.remove(db_path(cid))
    except OSError:
        pass


def db_path(cid):
    if not all(c.isalnum() or c == "-" for c in cid):
        raise ValueError("bad crawl id")
    return os.path.join(folder("crawls"), cid + ".db")


def flatten_jsonld(item):
    """Every typed object in a JSON-LD block (top level, @graph lists and nested values)."""
    if isinstance(item, list):
        for x in item:
            yield from flatten_jsonld(x)
    elif isinstance(item, dict):
        if "@type" in item:
            yield item
        for key, value in item.items():
            if key != "@type" and isinstance(value, (dict, list)):
                yield from flatten_jsonld(value)


class CrawlDB:
    """All data of one crawl. Safe to use from several threads (one lock)."""

    def __init__(self, cid):
        self.id = cid
        self.lock = threading.Lock()
        self.con = sqlite3.connect(db_path(cid), check_same_thread=False)
        self.con.execute("PRAGMA journal_mode=WAL")
        cols = ", ".join(f"{c} {'TEXT' if c in TEXT_COLUMNS else 'INTEGER'}" for c in PAGE_COLUMNS)
        self.con.executescript(f"""
            CREATE TABLE IF NOT EXISTS pages (id INTEGER PRIMARY KEY, {cols}, UNIQUE(url));
            CREATE TABLE IF NOT EXISTS links (src TEXT, dst TEXT, anchor TEXT, nofollow INTEGER,
                                              kind TEXT);
            CREATE INDEX IF NOT EXISTS links_dst ON links(dst);
            CREATE INDEX IF NOT EXISTS links_src ON links(src);
            CREATE TABLE IF NOT EXISTS sitemap (url TEXT PRIMARY KEY);
            CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT);
            CREATE TABLE IF NOT EXISTS issues (code TEXT, url TEXT, detail TEXT);
            CREATE INDEX IF NOT EXISTS issues_code ON issues(code);
            CREATE TABLE IF NOT EXISTS structured (url TEXT, type TEXT, json TEXT);
            CREATE TABLE IF NOT EXISTS custom (url TEXT, name TEXT, value TEXT);
            CREATE TABLE IF NOT EXISTS a11y (url TEXT, rule TEXT, impact TEXT, help TEXT,
                                             count INTEGER, help_url TEXT);
            CREATE TABLE IF NOT EXISTS cwv (url TEXT, strategy TEXT, score INTEGER, lcp REAL,
                                            cls REAL, inp REAL, tbt REAL, fcp REAL,
                                            field TEXT, error TEXT, checked REAL);
            CREATE TABLE IF NOT EXISTS gsc (url TEXT PRIMARY KEY, clicks INTEGER,
                                            impressions INTEGER, ctr REAL, position REAL);
            CREATE TABLE IF NOT EXISTS logs (url TEXT, bot TEXT, hits INTEGER, last TEXT,
                                             statuses TEXT);
        """)

    def add_page(self, row, resource=False):
        row = dict(row, resource=int(resource))
        cols = [c for c in PAGE_COLUMNS if c in row]
        with self.lock:
            self.con.execute(f"INSERT OR REPLACE INTO pages ({', '.join(cols)}) VALUES "
                             f"({', '.join('?' * len(cols))})", [row[c] for c in cols])

    def add_links(self, src, links):
        with self.lock:
            self.con.executemany("INSERT INTO links VALUES (?, ?, ?, ?, ?)",
                                 [(src, dst, anchor, nofollow, kind)
                                  for dst, anchor, nofollow, kind in links])

    def add_structured(self, url, items):
        rows = []
        for item in items:
            for node in flatten_jsonld(item):
                types = node.get("@type")
                for t in (types if isinstance(types, list) else [types]):
                    if isinstance(t, str):
                        rows.append((url, t, json.dumps(node, ensure_ascii=False)[:20000]))
        with self.lock:
            self.con.executemany("INSERT INTO structured VALUES (?, ?, ?)", rows)

    def add_custom(self, url, results):
        with self.lock:
            self.con.executemany("INSERT INTO custom VALUES (?, ?, ?)",
                                 [(url, n, v) for n, v in results])

    def add_accessibility(self, url, violations):
        with self.lock:
            self.con.executemany("INSERT INTO a11y VALUES (?, ?, ?, ?, ?, ?)", [
                (url, v["id"], v.get("impact"), v.get("help"), len(v.get("nodes", [])),
                 v.get("helpUrl")) for v in violations])

    def add_sitemap_urls(self, urls):
        with self.lock:
            self.con.executemany("INSERT OR IGNORE INTO sitemap VALUES (?)", [(u,) for u in urls])

    def set_meta(self, key, value):
        with self.lock:
            self.con.execute("INSERT OR REPLACE INTO meta VALUES (?, ?)", (key, value))

    def meta(self, key, default=None):
        with self.lock:
            row = self.con.execute("SELECT value FROM meta WHERE key = ?", (key,)).fetchone()
        return row[0] if row else default

    def query(self, sql, args=()):
        with self.lock:
            cur = self.con.execute(sql, args)
            names = [d[0] for d in cur.description] if cur.description else []
            return [dict(zip(names, r)) for r in cur.fetchall()]

    def execute(self, sql, args=()):
        with self.lock:
            self.con.execute(sql, args)

    def executemany(self, sql, rows):
        with self.lock:
            self.con.executemany(sql, rows)

    def commit(self):
        with self.lock:
            self.con.commit()
