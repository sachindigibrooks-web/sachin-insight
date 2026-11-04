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
import gsc
import i18n
import logs
import pagespeed
import report
import schedules
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
SORTABLE = {"url", "status", "depth", "time_ms", "size", "words", "title", "link_score"}
PAGE_FIELDS = ["url", "status", "content_type", "depth", "time_ms", "size", "words", "title",
               "meta_desc", "h1", "canonical", "meta_robots", "redirect_to", "error", "source",
               "rendered", "raw_words", "link_score"]
CUSTOM_KINDS = {"contains", "missing", "css", "xpath", "regex"}
SECRET_KEYS = {"smtp_password", "telegram_token", "psi_key"}
jobs = {}  # crawl id -> {"pagespeed": progress text}


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


def make_settings(data):
    """crawler.Settings from a form / schedule (raises ValueError on bad input)."""
    rules = [{"name": str(r.get("name", ""))[:60], "kind": r.get("kind"), "value": str(r.get("value", ""))[:500]}
             for r in (data.get("custom") or []) if r.get("kind") in CUSTOM_KINDS and r.get("value")][:20]
    s = crawler.Settings(
        start_url=str(data.get("url", "")).strip(),
        max_pages=max(1, min(int(data.get("max_pages") or 10000), 1_000_000)),
        concurrency=max(1, min(int(data.get("concurrency") or 5), 20)),
        respect_robots=bool(data.get("respect_robots", True)),
        check_external=bool(data.get("check_external", True)),
        check_images=bool(data.get("check_images", True)),
        include_subdomains=bool(data.get("include_subdomains", False)),
        use_sitemaps=bool(data.get("use_sitemaps", True)),
        render_js=bool(data.get("render_js", False)),
        accessibility=bool(data.get("accessibility", True)),
        custom=rules)
    if "://" not in s.start_url:
        s.start_url = "https://" + s.start_url
    return s


def launch(settings):
    c = crawler.Crawl(settings)
    running[c.id] = c
    c.start_thread()
    return c


@app.post("/api/crawl")
def start_crawl():
    try:
        c = launch(make_settings(request.get_json(silent=True) or {}))
    except ValueError as e:
        return jsonify(error=str(e)), 400
    return jsonify(id=c.id)


# ---------------------------------------------------------------- app settings & schedules

@app.get("/api/settings")
def get_settings():
    s = store.load_settings()
    return jsonify({k: ("••••••" if k in SECRET_KEYS and v else v) for k, v in s.items()})


@app.post("/api/settings")
def set_settings():
    data = request.get_json(silent=True) or {}
    allowed = {"psi_key", "telegram_token", "smtp_host", "smtp_port", "smtp_user", "smtp_password",
               "smtp_from", "alert_lang"}
    clean = {k: str(v).strip() for k, v in data.items()
             if k in allowed and not (k in SECRET_KEYS and v == "••••••")}
    store.save_settings(clean)
    report.save_branding(data)
    return jsonify(ok=True)


@app.get("/api/schedules")
def schedule_list():
    return jsonify(schedules.entries())


@app.post("/api/schedules")
def schedule_add():
    data = request.get_json(silent=True) or {}
    try:
        s = make_settings(data)
    except ValueError as e:
        return jsonify(error=str(e)), 400
    from dataclasses import asdict
    sid = schedules.add(s.start_url, dict(asdict(s), url=s.start_url),
                        max(0.04, float(data.get("every_days") or 7)),
                        data.get("telegram_chat", ""), data.get("email_to", ""),
                        bool(data.get("only_changes", True)))
    return jsonify(id=sid)


@app.delete("/api/schedules/<sid>")
def schedule_delete(sid):
    schedules.remove(sid)
    return jsonify(ok=True)


@app.post("/api/schedules/<sid>/run")
def schedule_run(sid):
    entry = next((e for e in schedules.entries() if e["id"] == sid), None)
    if not entry:
        abort(404)
    threading.Thread(target=schedules.run_one, args=(entry, schedule_crawl), daemon=True).start()
    return jsonify(ok=True)


@app.post("/api/alerts/test")
def alert_test():
    data = request.get_json(silent=True) or {}
    errors = schedules.notify({"telegram_chat": data.get("telegram_chat"), "email_to": data.get("email_to"),
                               "url": "test"}, "✅ Free SEO Crawler: test alert - it works!\n"
                              "Made by Sachin Samria")
    return (jsonify(error="; ".join(errors)), 400) if errors else jsonify(ok=True)


def schedule_crawl(saved):
    return launch(make_settings(saved))


@app.get("/api/crawls")
def crawl_list():
    return jsonify(store.crawls())


@app.delete("/api/crawl/<cid>")
def delete(cid):
    if cid in running and running[cid].progress["status"] in ("starting", "starting browser", "running", "analysing"):
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
    score = checks.health_score(db)
    meta = {k: db.meta(k) for k in ("sitemaps", "ai_bots_blocked", "llms_txt", "renderer",
                                    "render_error")}
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


# ---------------------------------------------------------------- extra data: speed, GSC, logs, custom, graph

@app.post("/api/crawl/<cid>/pagespeed")
def run_pagespeed(cid):
    db = db_for(cid)
    data = request.get_json(silent=True) or {}
    limit = max(1, min(int(data.get("limit") or 20), 500))
    strategy = "desktop" if data.get("strategy") == "desktop" else "mobile"
    urls = [r["url"] for r in db.query(f"SELECT url FROM pages WHERE {checks.HTML_PAGES} "
                                       f"ORDER BY link_score DESC, depth LIMIT {limit}")]
    key = store.load_settings().get("psi_key")
    state = jobs.setdefault(cid, {})
    if state.get("pagespeed", "").startswith("running"):
        return jsonify(error="Already running."), 400

    def work():
        try:
            pagespeed.run(db, urls, key, strategy,
                          lambda d, t: state.update(pagespeed=f"running {d}/{t}"))
            checks.analyse(db)
            state["pagespeed"] = "done"
        except Exception as e:
            state["pagespeed"] = f"error: {e}"
    state["pagespeed"] = f"running 0/{len(urls)}"
    threading.Thread(target=work, daemon=True).start()
    return jsonify(ok=True, urls=len(urls))


@app.get("/api/crawl/<cid>/pagespeed")
def pagespeed_rows(cid):
    rows = db_for(cid).query("SELECT url, strategy, score, lcp, cls, inp, tbt, fcp, field, error "
                             "FROM cwv ORDER BY score IS NULL, score")
    return jsonify(status=jobs.get(cid, {}).get("pagespeed", ""), rows=rows,
                   has_key=bool(store.load_settings().get("psi_key")))


@app.post("/api/crawl/<cid>/gsc")
def upload_gsc(cid):
    db = db_for(cid)
    f = request.files.get("file")
    if not f:
        return jsonify(error="Choose the Search Console export file."), 400
    try:
        n = gsc.import_into(db, f.read(), f.filename or "")
    except Exception as e:
        return jsonify(error=str(e)), 400
    checks.analyse(db)
    return jsonify(rows=n)


@app.get("/api/crawl/<cid>/gsc")
def gsc_rows(cid):
    return jsonify(db_for(cid).query(
        "SELECT g.url, g.clicks, g.impressions, g.ctr, g.position, p.status, p.title FROM gsc g "
        "LEFT JOIN pages p ON p.url = g.url ORDER BY g.clicks DESC LIMIT 2000"))


@app.post("/api/crawl/<cid>/logs")
def upload_logs(cid):
    db = db_for(cid)
    f = request.files.get("file")
    if not f:
        return jsonify(error="Choose a server access log file."), 400
    start = db.query("SELECT url FROM pages WHERE source = 'start'")
    try:
        info = logs.import_into(db, f.read(), start[0]["url"] if start else "")
    except Exception as e:
        return jsonify(error=str(e)), 400
    checks.analyse(db)
    return jsonify(info)


@app.get("/api/crawl/<cid>/logs")
def log_rows(cid):
    db = db_for(cid)
    return jsonify(bots=db.query("SELECT bot, SUM(hits) AS hits, COUNT(*) AS urls FROM logs "
                                 "GROUP BY bot ORDER BY hits DESC"),
                   rows=db.query("SELECT l.url, l.bot, l.hits, l.last, l.statuses, p.status FROM logs l "
                                 "LEFT JOIN pages p ON p.url = l.url ORDER BY l.hits DESC LIMIT 2000"))


@app.get("/api/crawl/<cid>/custom")
def custom_rows(cid):
    return jsonify(db_for(cid).query("SELECT name, url, value FROM custom ORDER BY name, url LIMIT 20000"))


@app.get("/api/crawl/<cid>/graph")
def graph(cid):
    """The most important pages (by link score) and the links between them."""
    db = db_for(cid)
    nodes = db.query(f"SELECT url, link_score, status, depth, title FROM pages WHERE {checks.HTML_PAGES} "
                     "ORDER BY link_score DESC LIMIT 150")
    keep = {n["url"] for n in nodes}
    edges = {(l["src"], l["dst"]) for l in db.query("SELECT src, dst FROM links WHERE kind = 'a'")
             if l["src"] in keep and l["dst"] in keep and l["src"] != l["dst"]}
    tree = db.query(f"SELECT url, status FROM pages WHERE internal = 1 AND resource = 0 LIMIT 50000")
    return jsonify(nodes=nodes, edges=[list(e) for e in edges], tree=tree)


@app.get("/api/branding")
def get_branding():
    return jsonify(report.branding())


@app.get("/api/crawl/<cid>/report.html")
def report_html(cid):
    db_for(cid)
    return Response(report.build_html(cid), mimetype="text/html")


@app.get("/api/crawl/<cid>/report.pdf")
def report_pdf(cid):
    db_for(cid)
    try:
        pdf = report.build_pdf(cid)
    except Exception as e:
        return jsonify(error=str(e)), 400
    return Response(pdf, mimetype="application/pdf",
                    headers={"Content-Disposition": f'attachment; filename="seo-report-{cid}.pdf"'})


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
    custom = db.query("SELECT name, url, value FROM custom ORDER BY name, url")
    return {"Pages": pages, "Issues": issues, "Broken links": links, "Images": images, "Custom": custom}


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
    schedules.start_scheduler(schedule_crawl)
    return port


if __name__ == "__main__":
    from waitress import serve
    port = int(os.environ.get("PORT", "8090"))
    print(f"Open http://localhost:{port}")
    schedules.start_scheduler(schedule_crawl)
    serve(app, host="127.0.0.1", port=port, threads=8)
