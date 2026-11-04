"""Server log analysis: which pages search and AI bots actually visit, and what they got.

Reads Apache / Nginx access logs in the usual "combined" format (plain or .gz).
Bots are recognised by their user agent.
"""

import gzip
import io
import json
import re
from collections import defaultdict

from crawler import normalize

LINE = re.compile(r'^(?P<ip>\S+) \S+ \S+ \[(?P<time>[^\]]+)\] "(?P<method>[A-Z]+) (?P<path>\S+)[^"]*" '
                  r'(?P<status>\d{3}) \S+(?: "(?P<ref>[^"]*)" "(?P<ua>[^"]*)")?')
BOTS = [("Googlebot", "googlebot"), ("Bingbot", "bingbot"), ("GPTBot", "gptbot"),
        ("ChatGPT-User", "chatgpt-user"), ("ClaudeBot", "claudebot"), ("PerplexityBot", "perplexitybot"),
        ("Applebot", "applebot"), ("YandexBot", "yandexbot"), ("Baiduspider", "baiduspider"),
        ("DuckDuckBot", "duckduckbot")]


def bot_of(ua):
    low = (ua or "").lower()
    return next((name for name, key in BOTS if key in low), None)


def parse(data, site_root):
    """{(url, bot): {"hits", "last", "statuses"}} from log bytes."""
    if data[:2] == b"\x1f\x8b":
        data = gzip.decompress(data)
    agg = defaultdict(lambda: {"hits": 0, "last": "", "statuses": defaultdict(int)})
    lines = bots = 0
    for raw in io.TextIOWrapper(io.BytesIO(data), encoding="utf-8", errors="replace"):
        lines += 1
        m = LINE.match(raw)
        if not m:
            continue
        bot = bot_of(m["ua"])
        if not bot:
            continue
        url = normalize(m["path"], site_root)
        if not url:
            continue
        bots += 1
        a = agg[(url, bot)]
        a["hits"] += 1
        a["last"] = m["time"]  # logs are in time order, so the last one wins
        a["statuses"][m["status"]] += 1
    return agg, lines, bots


def import_into(db, data, site_root):
    agg, lines, bots = parse(data, site_root)
    db.execute("DELETE FROM logs")
    db.executemany("INSERT INTO logs VALUES (?, ?, ?, ?, ?)", [
        (url, bot, a["hits"], a["last"], json.dumps(a["statuses"])) for (url, bot), a in agg.items()])
    db.commit()
    return {"lines": lines, "bot_hits": bots, "urls": len({u for u, _ in agg})}
