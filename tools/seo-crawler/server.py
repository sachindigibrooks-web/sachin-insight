"""The dashboard: a local website to start crawls and explore the results.

Run:  python server.py   then open http://localhost:8090  (app.py does this with a small window)
"""

import csv
import io
import json
import os
import sys
import threading
import time

from flask import Flask, Response, abort, jsonify, request

import checks
import crawler
import i18n
import store

HERE = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
app = Flask(__name__, static_folder=os.path.join(HERE, "web"), static_url_path="")
running = {}  # crawl id -> Crawl
PER_PAGE = 100

# Which pages each Pages tab shows (SQL condition).
VIEWS = {
    "html": checks.HTML_PAGES,
    "internal": "internal = 1 AND resource = 0",
    "errors": "internal = 1 AND (status >= 400 OR (error IS NOT NULL AND blocked IS NULL))",
    "redirects": "redirect_to IS NOT NULL",
    "external": "internal = 0 AND content_type NOT LIKE 'image/%'",
    "images": "content_type LIKE 'image/%'",
    "blocked": "blocked = 1",
}
SORTABLE = {"url", "status", "depth", "time_ms", "size", "words", "title"}
PAGE_FIELDS = ["url", "status", "content_type", "depth", "time_ms", "size", "words", "title",
               "meta_desc", "h1", "canonical", "meta_robots", "redirect_to", "error", "source"]


def db_for(cid):
    try:
        return store.CrawlDB(cid) if os.path.exists(store.db_path(cid)) else abort(404)
    except ValueError:
        abort(404)


@app.get("/")
def index():
    return app.send_static_file("index.html")


@app.get("/api/i18n")
def texts():
    return jsonify(ui=i18n.UI, checks={k: [v[2], v[3]] for k, v in checks.CHECKS.items()})


@app.post("/api/crawl")
def start_crawl():
    data = request.get_json(silent=True) or {}
    try:
        s = crawler.Settings(
            start_url=str(data.get("url", "")).strip(),
            max_pages=max(1, min(int(data.get("max_pages") or 10000), 1_000_000)),
            concurrency=max(1, min(int(data.get("concurrency") or 5), 20)),
            respect_robots=bool(data.get("respect_robots", True)),
            check_external=bool(data.get("check_external", True)),
            check_images=bool(data.get("check_images", True)),
            include_subdomains=bool(data.get("include_subdomains", False)),
            use_sitemaps=bool(data.get("use_sitemaps", True)))
        if "://" not in s.start_url:
            s.start_url = "https://" + s.start_url
        c = crawler.Crawl(s)
    except ValueError as e:
        return jsonify(error=str(e)), 400
    running[c.id] = c
    c.start_thread()
    return jsonify(id=c.id)


@app.get("/api/crawls")
def crawl_list():
    return jsonify(store.crawls())


@app.delete("/api/crawl/<cid>")
def delete(cid):
    if cid in running and running[cid].progress["status"] in ("starting", "running", "analysing"):
        return jsonify(error="Stop the crawl first."), 400
    running.pop(cid, None)
    store.delete_crawl(cid)
    return jsonify(ok=True)


@app.get("/api/crawl/<cid>/progress")
def progress(cid):
    c = running.get(cid)
    if c:
        return jsonify(c.progress)
    for row in store.crawls():
        if row["id"] == cid:
            status = row["status"] if row["status"] != "running" else "interrupted"
            return jsonify(status=status, crawled=row["pages"], queued=0)
    abort(404)


@app.post("/api/crawl/<cid>/stop")
def stop(cid):
    if cid in running:
        running[cid].stop()
    return jsonify(ok=True)


@app.get("/api/crawl/<cid>/summary")
def summary(cid):
    db = db_for(cid)
    stats = db.query(f"""SELECT
        SUM({checks.HTML_PAGES}) AS html_pages,
        SUM(internal = 1 AND resource = 0) AS internal_urls,
        SUM(internal = 0) AS external_urls,
        SUM(internal = 1 AND status BETWEEN 300 AND 399) AS redirects,
        SUM(internal = 1 AND status >= 400) AS errors,
        AVG(CASE WHEN {checks.HTML_PAGES} THEN time_ms END) AS avg_ms
        FROM pages""")[0]
    status_codes = db.query("SELECT COALESCE(status, 0) AS status, COUNT(*) AS n FROM pages "
                            "WHERE internal = 1 AND resource = 0 GROUP BY 1 ORDER BY 1")
    depths = db.query(f"SELECT depth, COUNT(*) AS n FROM pages WHERE {checks.HTML_PAGES} "
                      "AND depth IS NOT NULL GROUP BY depth ORDER BY depth")
    issues = checks.summary(db)
    errors = ",".join(f"'{k}'" for k, v in checks.CHECKS.items() if v[0] == "error")
    with_errors = db.query(f"SELECT COUNT(DISTINCT url) AS n FROM issues WHERE code IN ({errors}) "
                           f"AND url IN (SELECT url FROM pages WHERE {checks.HTML_PAGES})")[0]["n"]
    html_pages = stats["html_pages"] or 0
    score = round(100 * (html_pages - with_errors) / html_pages) if html_pages else None
    meta = {k: db.meta(k) for k in ("sitemaps", "ai_bots_blocked", "llms_txt")}
    return jsonify(stats=stats, status_codes=status_codes, depths=depths, issues=issues,
                   score=score, meta=meta)


@app.get("/api/crawl/<cid>/issues/<code>")
def issue_urls(cid, code):
    if code not in checks.CHECKS:
        abort(404)
    rows = db_for(cid).query("SELECT url, detail FROM issues WHERE code = ? ORDER BY url LIMIT 5000",
                             (code,))
    return jsonify(rows)


@app.get("/api/crawl/<cid>/pages")
def pages(cid):
    db = db_for(cid)
    where = [VIEWS.get(request.args.get("view", "internal"), VIEWS["internal"])]
    args = []
    q = request.args.get("q", "").strip()
    if q:
        where.append("(url LIKE ? OR title LIKE ?)")
        args += [f"%{q}%", f"%{q}%"]
    sort = request.args.get("sort", "url")
    sort = sort if sort in SORTABLE else "url"
    order = "DESC" if request.args.get("desc") == "1" else "ASC"
    page = max(0, int(request.args.get("page", 0) or 0))
    cond = " AND ".join(f"({w})" for w in where)
    total = db.query(f"SELECT COUNT(*) AS n FROM pages WHERE {cond}", args)[0]["n"]
    rows = db.query(f"SELECT {', '.join(PAGE_FIELDS)} FROM pages WHERE {cond} "
                    f"ORDER BY {sort} {order} LIMIT {PER_PAGE} OFFSET {page * PER_PAGE}", args)
    return jsonify(total=total, rows=rows, per_page=PER_PAGE)


@app.get("/api/crawl/<cid>/page")
def page_detail(cid):
    db = db_for(cid)
    url = request.args.get("url", "")
    row = db.query("SELECT * FROM pages WHERE url = ?", (url,))
    if not row:
        abort(404)
    return jsonify(
        page=row[0],
        inlinks=db.query("SELECT src, anchor, nofollow, kind FROM links WHERE dst = ? LIMIT 500", (url,)),
        outlinks=db.query("SELECT l.dst, l.anchor, l.kind, p.status FROM links l LEFT JOIN pages p "
                          "ON p.url = l.dst WHERE l.src = ? LIMIT 1000", (url,)),
        issues=[dict(r, title=checks.CHECKS[r["code"]][2], title_hi=checks.CHECKS[r["code"]][3],
                     severity=checks.CHECKS[r["code"]][0])
                for r in db.query("SELECT code, detail FROM issues WHERE url = ?", (url,))])


@app.get("/api/compare")
def compare():
    """What changed between two crawls of a site: URLs, status codes, titles and issues."""
    a, b = db_for(request.args.get("a", "")), db_for(request.args.get("b", ""))
    old = {r["url"]: r for r in a.query("SELECT url, status, title FROM pages WHERE internal = 1 AND resource = 0")}
    new = {r["url"]: r for r in b.query("SELECT url, status, title FROM pages WHERE internal = 1 AND resource = 0")}
    status_changed = [{"url": u, "before": old[u]["status"], "after": new[u]["status"]}
                      for u in new if u in old and old[u]["status"] != new[u]["status"]]
    title_changed = [{"url": u, "before": old[u]["title"], "after": new[u]["title"]}
                     for u in new if u in old and old[u]["title"] != new[u]["title"]
                     and new[u]["status"] == 200]
    ia = {(r["code"], r["url"]) for r in a.query("SELECT code, url FROM issues")}
    ib = {(r["code"], r["url"]) for r in b.query("SELECT code, url FROM issues")}
    per_code = {}
    for code, _ in ia | ib:
        per_code.setdefault(code, {"code": code, "title": checks.CHECKS[code][2],
                                   "title_hi": checks.CHECKS[code][3],
                                   "severity": checks.CHECKS[code][0], "new": 0, "fixed": 0})
    for code, _ in ib - ia:
        per_code[code]["new"] += 1
    for code, _ in ia - ib:
        per_code[code]["fixed"] += 1
    return jsonify(added=sorted(set(new) - set(old))[:2000], removed=sorted(set(old) - set(new))[:2000],
                   status_changed=status_changed[:2000], title_changed=title_changed[:2000],
                   issues=sorted([v for v in per_code.values() if v["new"] or v["fixed"]],
                                 key=lambda v: (checks.SEVERITY_ORDER[v["severity"]], -v["new"])))


# ---------------------------------------------------------------- export

def export_tables(db):
    pages = db.query(f"SELECT {', '.join(PAGE_FIELDS)} FROM pages WHERE internal = 1 AND resource = 0 "
                     "ORDER BY url")
    issues = [dict(severity=checks.CHECKS[r["code"]][0], issue=checks.CHECKS[r["code"]][2], **r)
              for r in db.query("SELECT code, url, detail FROM issues ORDER BY code, url")]
    links = db.query("SELECT l.src AS on_page, l.dst AS link, l.anchor, p.status, p.error FROM links l "
                     "JOIN pages p ON p.url = l.dst WHERE l.kind IN ('a', 'img') AND "
                     "(p.status >= 400 OR p.error IS NOT NULL) ORDER BY l.src")
    images = db.query("SELECT l.src AS on_page, l.dst AS image, l.anchor AS alt, p.status, p.size "
                      "FROM links l LEFT JOIN pages p ON p.url = l.dst WHERE l.kind = 'img' ORDER BY l.src")
    return {"Pages": pages, "Issues": issues, "Broken links": links, "Images": images}


@app.get("/api/crawl/<cid>/export.xlsx")
def export_xlsx(cid):
    from openpyxl import Workbook
    from openpyxl.styles import Font
    wb = Workbook(write_only=True)
    for name, rows in export_tables(db_for(cid)).items():
        ws = wb.create_sheet(name)
        if rows:
            ws.append(list(rows[0]))
            for r in rows:
                ws.append([v for v in r.values()])
    summary_ws = wb.create_sheet("About", 0)
    summary_ws.append(["Free SEO Crawler - Made by Sachin Samria"])
    summary_ws.append(["Crawl", cid])
    summary_ws.append(["Exported", time.strftime("%Y-%m-%d %H:%M")])
    buf = io.BytesIO()
    wb.save(buf)
    return Response(buf.getvalue(), mimetype="application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet",
                    headers={"Content-Disposition": f'attachment; filename="seo-crawl-{cid}.xlsx"'})


@app.get("/api/crawl/<cid>/export/<table>.csv")
def export_csv(cid, table):
    db = db_for(cid)
    code = request.args.get("code")
    if table == "issue" and code in checks.CHECKS:
        rows = db.query("SELECT url, detail FROM issues WHERE code = ? ORDER BY url", (code,))
        name = code
    else:
        tables = {k.lower().replace(" ", "-"): v for k, v in export_tables(db).items()}
        if table not in tables:
            abort(404)
        rows, name = tables[table], table
    buf = io.StringIO()
    if rows:
        w = csv.DictWriter(buf, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    # BOM so Excel opens Hindi / other scripts correctly
    return Response("﻿" + buf.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": f'attachment; filename="{name}-{cid}.csv"'})


def serve_background(port=8090):
    """Start the dashboard in this process and return its port (used by app.py)."""
    import socket
    from waitress import serve

    def free(p):
        with socket.socket() as s:
            return s.connect_ex(("127.0.0.1", p)) != 0
    while not free(port):
        port += 1
    # Only this PC can open the dashboard (crawl data stays private).
    threading.Thread(target=serve, args=(app,), kwargs={"host": "127.0.0.1", "port": port,
                                                         "threads": 8}, daemon=True).start()
    for _ in range(50):
        if not free(port):
            break
        time.sleep(0.1)
    return port


if __name__ == "__main__":
    from waitress import serve
    port = int(os.environ.get("PORT", "8090"))
    print(f"Open http://localhost:{port}")
    serve(app, host="127.0.0.1", port=port, threads=8)
