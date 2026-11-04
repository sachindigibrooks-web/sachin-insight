"""Crawl the test site and check that every planted problem is found.

Run:  python tests/test_checks.py   (from tools/seo-crawler)
"""

import os
import sys
import tempfile
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
os.environ["XDG_DATA_HOME"] = tempfile.mkdtemp()  # keep test crawls out of the real data

import crawler  # noqa: E402
import test_site  # noqa: E402

EXPECTED = {  # code -> a URL (or part of the detail) that must be reported
    "client_error": "/missing", "server_error": "/error", "slow_page": "/slow",
    "link_to_redirect": "/", "redirect_chain": "/redirect1", "redirect_loop": "/loop1",
    "broken_internal_link": "/", "broken_external_link": "/", "nofollow_internal": "/a",
    "orphan_page": "/orphan", "deep_page": "/deep4", "blocked_robots": "/blocked/page",
    "title_missing": "/a", "title_multiple": "/b", "title_long": "/b", "title_duplicate": "/dup1",
    "desc_missing": "/a", "desc_short": "/b", "h1_missing": "/a", "h1_multiple": "/b",
    "thin_content": "/a", "duplicate_content": "/dup2", "near_duplicate": "/near1",
    "noindex": "/b", "canonicalised": "/b", "jsonld_invalid": "/b", "canonical_missing": "/a",
    "sitemap_bad_url": "/missing", "not_in_sitemap": "/near1",
    "img_alt_missing": "/a", "img_large": "/img/big.jpg", "img_broken": "/a",
    "url_uppercase": "/Upper_Case", "url_underscore": "/Upper_Case", "url_params": "/params",
    "ai_bots_blocked": "/robots.txt", "llms_txt_missing": "/llms.txt",
}
NOT_EXPECTED = {"title_missing": "/near1", "client_error": "/a", "orphan_page": "/a",
                "broken_internal_link": "/near1", "duplicate_content": "/near1"}


def main():
    from werkzeug.serving import make_server
    # Listen on IPv4 and IPv6: "localhost" means ::1 first on some systems (macOS).
    for host in ("127.0.0.1", "::1"):
        try:
            srv = make_server(host, test_site.PORT, test_site.app, threaded=True)
        except OSError:  # no IPv6 here
            continue
        threading.Thread(target=srv.serve_forever, daemon=True).start()
    time.sleep(0.5)
    failed = run_checks(render=False, expected=EXPECTED | {"h1_missing": "/js", "thin_content": "/js"})
    failed += run_checks(render=True, expected={
        "js_content": "/js", "title_missing": "/a", "broken_internal_link": "/"},
        not_expected={"h1_missing": "/js", "thin_content": "/js", "title_missing": "/js"},
        must_crawl="/js-child")
    return failed


def run_checks(render, expected, not_expected=NOT_EXPECTED, must_crawl=None):
    s = crawler.Settings(f"http://localhost:{test_site.PORT}/", concurrency=4, render_js=render)
    c = crawler.Crawl(s)
    t0 = time.time()
    c.run()
    mode = "rendered" if render else "raw HTML"
    print(f"[{mode}] crawl {c.progress['status']}: {c.progress['crawled']} URLs in {time.time() - t0:.1f}s"
          + (f" with {c.db.meta('renderer')}" if render else ""))
    if render and c.db.meta("render_error"):
        print(f"[{mode}] SKIPPED - no browser: {c.db.meta('render_error')[:200]}")
        return 0
    found = {}
    for r in c.db.query("SELECT code, url, detail FROM issues"):
        found.setdefault(r["code"], []).append(r["url"] + " " + r["detail"])
    failed = 0
    for code, needle in expected.items():
        hits = [x for x in found.get(code, []) if x.split(" ")[0].endswith(needle) or needle in x]
        if not hits:
            failed += 1
            print(f"[{mode}] MISSING  {code}: expected {needle}, got {found.get(code, [])[:3]}")
    for code, needle in not_expected.items():
        bad = [x for x in found.get(code, []) if x.split(" ")[0].endswith(needle)]
        if bad:
            failed += 1
            print(f"[{mode}] WRONG    {code}: should not report {needle}: {bad[:2]}")
    if must_crawl and not c.db.query("SELECT 1 FROM pages WHERE url LIKE ? AND status = 200",
                                     ("%" + must_crawl,)):
        failed += 1
        print(f"[{mode}] MISSING  page {must_crawl} was not crawled")
    print(f"[{mode}] {len(expected) - failed}/{len(expected)} checks OK" if not failed
          else f"[{mode}] {failed} problem(s)")
    return failed


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
