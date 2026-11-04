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
    threading.Thread(target=lambda: test_site.app.run(port=test_site.PORT, threaded=True),
                     daemon=True).start()
    time.sleep(1)
    c = crawler.Crawl(crawler.Settings(f"http://localhost:{test_site.PORT}/", concurrency=4))
    t0 = time.time()
    c.run()
    print(f"crawl {c.progress['status']}: {c.progress['crawled']} URLs in {time.time() - t0:.1f}s")
    found = {}
    for r in c.db.query("SELECT code, url, detail FROM issues"):
        found.setdefault(r["code"], []).append(r["url"] + " " + r["detail"])
    failed = 0
    for code, needle in EXPECTED.items():
        hits = [x for x in found.get(code, []) if needle in x.split(" ")[0] or needle in x]
        if not hits:
            failed += 1
            print(f"MISSING  {code}: expected {needle}, got {found.get(code, [])[:3]}")
    for code, needle in NOT_EXPECTED.items():
        bad = [x for x in found.get(code, []) if x.split(" ")[0].endswith(needle)]
        if bad:
            failed += 1
            print(f"WRONG    {code}: should not report {needle}: {bad[:2]}")
    print(f"{len(EXPECTED) - failed}/{len(EXPECTED)} checks OK" if not failed else f"{failed} problem(s)")
    return failed


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
