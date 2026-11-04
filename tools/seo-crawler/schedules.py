"""Scheduled crawls with alerts on Telegram or e-mail.

A schedule re-crawls a site every N days while the app is running (the installer
can start the app with Windows, quietly). After each crawl it is compared with the
previous crawl of the same site, and a short report is sent - always, or only when
something got worse.
"""

import json
import os
import smtplib
import sqlite3
import threading
import time
import uuid
from email.message import EmailMessage

import httpx

import checks
import store

CHECK_EVERY = 60  # seconds between looks for due schedules


def settings():
    return store.load_settings()


def _db():
    con = sqlite3.connect(os.path.join(store.folder(), "crawls.db"))
    con.execute("CREATE TABLE IF NOT EXISTS schedules (id TEXT PRIMARY KEY, url TEXT, settings TEXT, "
                "every_days REAL, next_run REAL, telegram_chat TEXT, email_to TEXT, "
                "only_changes INTEGER, last_crawl TEXT, last_result TEXT)")
    return con


def add(url, crawl_settings, every_days=7, telegram_chat="", email_to="", only_changes=True):
    sid = uuid.uuid4().hex[:10]
    with _db() as con:
        con.execute("INSERT INTO schedules VALUES (?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL)",
                    (sid, url, json.dumps(crawl_settings), float(every_days), time.time(),
                     telegram_chat.strip(), email_to.strip(), int(bool(only_changes))))
    return sid


def remove(sid):
    with _db() as con:
        con.execute("DELETE FROM schedules WHERE id = ?", (sid,))


def entries():
    with _db() as con:
        cur = con.execute("SELECT * FROM schedules ORDER BY next_run")
        names = [d[0] for d in cur.description]
        return [dict(zip(names, r)) for r in cur.fetchall()]


def _update(sid, **values):
    with _db() as con:
        con.execute(f"UPDATE schedules SET {', '.join(f'{k} = ?' for k in values)} WHERE id = ?",
                    list(values.values()) + [sid])


def compare(old_id, new_id):
    """Numbers for the alert: score before/after and error-level issues that appeared / went away."""
    new = store.CrawlDB(new_id)
    out = {"score": checks.health_score(new), "before": None, "new": {}, "fixed": {},
           "pages": new.query(f"SELECT COUNT(*) AS n FROM pages WHERE {checks.HTML_PAGES}")[0]["n"]}
    now = {(r["code"], r["url"]) for r in new.query("SELECT code, url FROM issues")}
    then = set()
    if old_id:
        old = store.CrawlDB(old_id)
        out["before"] = checks.health_score(old)
        then = {(r["code"], r["url"]) for r in old.query("SELECT code, url FROM issues")}
    for code, _ in now - then:
        out["new"][code] = out["new"].get(code, 0) + 1
    for code, _ in then - now:
        out["fixed"][code] = out["fixed"].get(code, 0) + 1
    return out


def message(url, cmp, lang="en"):
    hi = lang == "hi"
    score = f"{cmp['score']}%" if cmp["score"] is not None else "-"
    lines = [("🕷 SEO रिपोर्ट: " if hi else "🕷 SEO report: ") + url,
             ("साइट हेल्थ: " if hi else "Site health: ") + score
             + (f" ({'पहले' if hi else 'was'} {cmp['before']}%)" if cmp["before"] is not None else ""),
             (f"{cmp['pages']} पेज क्रॉल हुए" if hi else f"{cmp['pages']} pages crawled")]
    worse = {c: n for c, n in cmp["new"].items() if checks.CHECKS[c][0] in ("error", "warning")}
    if worse:
        lines.append("\n" + ("⚠ नई गड़बड़ियाँ:" if hi else "⚠ New problems:"))
        for code, n in sorted(worse.items(), key=lambda x: (checks.SEVERITY_ORDER[checks.CHECKS[x[0]][0]], -x[1]))[:8]:
            lines.append(f"• {checks.CHECKS[code][3 if hi else 2]}: {n}")
    fixed = sum(cmp["fixed"].values())
    if fixed:
        lines.append(("✅ ठीक हुईं: " if hi else "✅ Fixed: ") + str(fixed))
    lines.append("\nFree SEO Crawler - Made by Sachin Samria")
    return "\n".join(lines), bool(worse) or (cmp["before"] is not None and (cmp["score"] or 0) < cmp["before"])


def send_telegram(chat_id, text, token=None):
    token = token or settings().get("telegram_token")
    if not token or not chat_id:
        raise ValueError("Telegram bot token or chat id missing (Settings).")
    r = httpx.post(f"https://api.telegram.org/bot{token}/sendMessage",
                   json={"chat_id": chat_id, "text": text}, timeout=30)
    if r.status_code != 200:
        raise ValueError(f"Telegram said: {r.text[:200]}")


def send_email(to, subject, text):
    cfg = settings()
    host, user = cfg.get("smtp_host"), cfg.get("smtp_user")
    if not host or not user or not to:
        raise ValueError("E-mail (SMTP) settings or address missing (Settings).")
    msg = EmailMessage()
    msg["From"], msg["To"], msg["Subject"] = cfg.get("smtp_from") or user, to, subject
    msg.set_content(text)
    port = int(cfg.get("smtp_port") or 587)
    with smtplib.SMTP(host, port, timeout=30) as s:
        s.starttls()
        s.login(user, cfg.get("smtp_password", ""))
        s.send_message(msg)


def notify(entry, text):
    errors = []
    if entry.get("telegram_chat"):
        try:
            send_telegram(entry["telegram_chat"], text)
        except Exception as e:
            errors.append(f"Telegram: {e}")
    if entry.get("email_to"):
        try:
            send_email(entry["email_to"], "SEO report: " + entry["url"], text)
        except Exception as e:
            errors.append(f"E-mail: {e}")
    return errors


def previous_crawl(url, before_id):
    done = [c for c in store.crawls() if c["start_url"] == url and c["status"] == "finished"
            and c["id"] < before_id]
    return done[0]["id"] if done else None


def run_one(entry, start_crawl):
    """Crawl one scheduled site now, compare, alert. `start_crawl(settings)` returns a Crawl."""
    _update(entry["id"], next_run=time.time() + entry["every_days"] * 86400)
    crawl = start_crawl(json.loads(entry["settings"]))
    while crawl.progress["status"] in ("starting", "starting browser", "running", "analysing"):
        time.sleep(2)
    if crawl.progress["status"] != "finished":
        _update(entry["id"], last_crawl=crawl.id, last_result=f"crawl {crawl.progress['status']}")
        return
    cmp = compare(previous_crawl(crawl.start, crawl.id), crawl.id)
    text, worse = message(entry["url"], cmp, settings().get("alert_lang", "en"))
    result = "no change" if entry["only_changes"] and not worse else "sent"
    if result == "sent":
        errors = notify(entry, text)
        result = "; ".join(errors) if errors else "sent"
    _update(entry["id"], last_crawl=crawl.id, last_result=result)


def start_scheduler(start_crawl):
    def loop():
        while True:
            for entry in entries():
                if entry["next_run"] <= time.time():
                    try:
                        run_one(entry, start_crawl)
                    except Exception as e:
                        _update(entry["id"], last_result=f"error: {e}"[:300])
            time.sleep(CHECK_EVERY)
    threading.Thread(target=loop, daemon=True).start()
