"""Tests for the extra features: custom search / extraction, structured data, accessibility
(static + axe), link score, Search Console import, log analysis, PageSpeed parsing, the
white-label report and scheduled-crawl alerts.

Run:  python tests/test_features.py   (from tools/seo-crawler)
"""

import json
import os
import sys
import tempfile
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
os.environ["XDG_DATA_HOME"] = tempfile.mkdtemp()

import checks  # noqa: E402
import crawler  # noqa: E402
import gsc  # noqa: E402
import logs  # noqa: E402
import pagespeed  # noqa: E402
import report  # noqa: E402
import schedules  # noqa: E402
import store  # noqa: E402
import test_site  # noqa: E402

BASE = f"http://localhost:{test_site.PORT}"
failures = []


def check(name, ok, detail=""):
    print(("OK      " if ok else "FAILED  ") + name + (f" - {detail}" if detail and not ok else ""))
    if not ok:
        failures.append(name)


def issues(db, code):
    return {r["url"].replace(BASE, "") + " " + r["detail"] for r in
            db.query("SELECT url, detail FROM issues WHERE code = ?", (code,))}


def has(db, code, needle):
    found = issues(db, code)
    return any(x.split(" ")[0] == needle or needle in x for x in found), sorted(found)[:4]


def start_site():
    from werkzeug.serving import make_server
    for host in ("127.0.0.1", "::1"):
        try:
            srv = make_server(host, test_site.PORT, test_site.app, threaded=True)
        except OSError:
            continue
        threading.Thread(target=srv.serve_forever, daemon=True).start()
    time.sleep(0.5)


def main():
    start_site()
    rules = [{"name": "Old analytics", "kind": "contains", "value": "UA-12345"},
             {"name": "GA4 tag", "kind": "missing", "value": "gtag("},
             {"name": "Price", "kind": "css", "value": ".price"},
             {"name": "Price number", "kind": "regex", "value": r"Rs\. (\d+)"},
             {"name": "Title", "kind": "xpath", "value": "//title/text()"}]
    c = crawler.Crawl(crawler.Settings(BASE + "/", concurrency=4, custom=rules))
    c.run()
    db = c.db
    check("crawl finished", c.progress["status"] == "finished", c.progress)

    # custom search / extraction
    custom = {(r["name"], r["url"].replace(BASE, "")): r["value"] for r in db.query("SELECT * FROM custom")}
    check("custom contains", custom.get(("Old analytics", "/shop")) == "found 1 time(s)", custom)
    check("custom missing", custom.get(("GA4 tag", "/a")) == "missing")
    check("custom css extract", custom.get(("Price", "/shop")) == "Rs. 499")
    check("custom regex extract", custom.get(("Price number", "/shop")) == "499")
    check("custom xpath extract", custom.get(("Title", "/shop")) == "Shop page with products for the crawler test")
    check("custom issues", has(db, "custom_missing", "/a")[0] and has(db, "custom_found", "/shop")[0])

    # structured data
    ok, got = has(db, "sd_required", "Product: missing offers or review or aggregateRating")
    check("structured data required", ok, got)
    ok, got = has(db, "sd_recommended", "Article: add image")
    check("structured data recommended", ok, got)

    # static accessibility
    for code in ("a11y_form_label", "a11y_link_text", "a11y_button_name", "a11y_empty_heading",
                 "a11y_heading_skip"):
        ok, got = has(db, code, "/shop")
        check(f"accessibility {code}", ok, got)
    ok, got = has(db, "a11y_form_label", "/")
    check("labelled field not reported", not any(x.startswith("/ ") for x in issues(db, "a11y_form_label")), got)

    # link score (internal PageRank)
    scores = {r["url"].replace(BASE, ""): r["link_score"] for r in
              db.query(f"SELECT url, link_score FROM pages WHERE {checks.HTML_PAGES}")}
    check("home has the top link score", scores.get("/") == 100, scores)
    check("unlinked orphan page scores lowest", scores.get("/orphan") == 0, scores)
    check("page linked from many outranks one linked from one page",
          scores.get("/a", 0) > scores.get("/js-child", -1) if "/js-child" in scores else scores.get("/a", 0) > 0,
          scores)
    check("few inlinks", has(db, "few_inlinks", "/deep2")[0], sorted(issues(db, "few_inlinks"))[:4])

    # Search Console import
    csv_text = ("Top pages,Clicks,Impressions,CTR,Position\n"
                f"{BASE}/missing,25,900,2.8%,4.1\n"
                f"{BASE}/never-linked,3,120,2.5%,8\n"
                f"{BASE}/near1,1,400,0.25%,6.2\n")
    n = gsc.import_into(db, csv_text.encode(), "Pages.csv")
    checks.analyse(db)
    check("gsc import", n == 3, n)
    check("gsc traffic page broken", has(db, "gsc_traffic_problem", "/missing")[0], issues(db, "gsc_traffic_problem"))
    check("gsc not linked", has(db, "gsc_not_linked", "/never-linked")[0])
    check("gsc low ctr", has(db, "gsc_low_ctr", "/near1")[0], issues(db, "gsc_low_ctr"))
    import io
    import zipfile
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("Queries.csv", "x")
        z.writestr("Pages.csv", csv_text)
    check("gsc zip import", gsc.import_into(db, buf.getvalue(), "export.zip") == 3)

    # server logs
    g = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
    lines = [f'66.249.66.1 - - [04/Nov/2026:10:00:0{i} +0000] "GET {path} HTTP/1.1" {st} 512 "-" "{ua}"'
             for i, (path, st, ua) in enumerate([("/", 200, g), ("/missing", 404, g), ("/missing", 404, g),
                                                 ("/params?x=1", 200, g), ("/a", 200, "GPTBot/1.1"),
                                                 ("/a", 200, "Mozilla/5.0 Chrome")])]
    info = logs.import_into(db, "\n".join(lines).encode(), BASE + "/")
    checks.analyse(db)
    check("logs parsed", info == {"lines": 6, "bot_hits": 5, "urls": 4}, info)
    check("logs bot errors", has(db, "log_bot_errors", "/missing")[0], issues(db, "log_bot_errors"))
    check("logs parameter waste", has(db, "log_param_waste", "/params?x=1")[0])
    not_seen = {x.split(" ")[0] for x in issues(db, "log_not_seen")}
    check("logs not seen by Googlebot", "/near1" in not_seen and "/" not in not_seen, sorted(not_seen)[:5])

    # PageSpeed parsing + checks
    sample = {"lighthouseResult": {"categories": {"performance": {"score": 0.42}}, "audits": {
        "largest-contentful-paint": {"numericValue": 5200.0}, "cumulative-layout-shift": {"numericValue": 0.05},
        "total-blocking-time": {"numericValue": 640.0}, "first-contentful-paint": {"numericValue": 2100.0}}},
        "loadingExperience": {"id": BASE, "overall_category": "SLOW", "metrics": {
            "LARGEST_CONTENTFUL_PAINT_MS": {"percentile": 4300}, "CUMULATIVE_LAYOUT_SHIFT_SCORE": {"percentile": 8},
            "INTERACTION_TO_NEXT_PAINT": {"percentile": 180}}}}
    res = pagespeed.parse(sample)
    check("pagespeed parse", res["score"] == 42 and res["lcp"] == 5200.0 and
          json.loads(res["field"]) == {"lcp": 4300, "cls": 0.08, "inp": 180, "overall": "SLOW"}, res)
    db.execute("INSERT INTO cwv VALUES (?, 'mobile', ?, ?, ?, ?, ?, ?, ?, NULL, 0)",
               (BASE + "/slow", res["score"], res["lcp"], res["cls"], res["inp"], res["tbt"], res["fcp"], res["field"]))
    checks.analyse(db)
    check("cwv poor + low score", has(db, "cwv_poor", "/slow")[0] and has(db, "speed_low", "/slow")[0],
          issues(db, "cwv_poor"))

    # white-label report
    store.save_settings({"agency_name": "DigiBrooks", "client_name": "Test Client", "brand_color": "#123456"})
    page = report.build_html(c.id)
    check("report html branded", "DigiBrooks" in page and "Test Client" in page and "#123456" in page
          and "SEO Audit Report" in page)
    store.save_settings({"report_lang": "hi"})
    check("report in Hindi", "SEO ऑडिट रिपोर्ट" in report.build_html(c.id))
    store.save_settings({"report_lang": "en"})
    try:
        pdf = report.build_pdf(c.id)
        check("report pdf", pdf[:5] == b"%PDF-" and len(pdf) > 10000, len(pdf))
    except RuntimeError as e:
        print(f"SKIPPED report pdf - {e}")

    # scheduled crawl + alert (Telegram call captured instead of sent)
    sent = []
    schedules.send_telegram = lambda chat, text, token=None: sent.append((chat, text))
    sid = schedules.add(BASE + "/", {"url": BASE + "/", "concurrency": 4}, 7, telegram_chat="123",
                        only_changes=False)
    entry = next(e for e in schedules.entries() if e["id"] == sid)

    def start_crawl(saved):
        cr = crawler.Crawl(crawler.Settings(saved["url"], concurrency=4))
        cr.start_thread()
        return cr
    schedules.run_one(entry, start_crawl)
    after = next(e for e in schedules.entries() if e["id"] == sid)
    check("schedule alert sent", after["last_result"] == "sent" and sent and sent[0][0] == "123"
          and "Site health" in sent[0][1] and "Made by Sachin Samria" in sent[0][1], (after, sent[:1]))
    check("schedule next run moved", after["next_run"] > time.time() + 6 * 86400)
    text, worse = schedules.message("x", {"score": 70, "before": 90, "new": {"client_error": 2},
                                          "fixed": {}, "pages": 10})
    check("alert says what got worse", worse and "Pages returning 4xx" in text and "was 90%" in text, text)

    # axe-core in rendering mode (needs a browser)
    r = crawler.Crawl(crawler.Settings(BASE + "/", concurrency=4, render_js=True, max_pages=40))
    r.run()
    if r.db.meta("render_error"):
        print("SKIPPED axe - no browser:", r.db.meta("render_error")[:120])
    else:
        ok, got = has(r.db, "axe_serious", "/shop")
        check(f"axe finds serious problems (with {r.db.meta('renderer')})", ok, sorted(issues(r.db, "axe_serious"))[:3])

    print(f"\n{len(failures)} failure(s)" if failures else "\nall feature checks OK")
    return len(failures)


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
