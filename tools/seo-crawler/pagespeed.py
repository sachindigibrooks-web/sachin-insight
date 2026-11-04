"""Core Web Vitals from Google PageSpeed Insights (free API; a free key gives a big quota).

Get a key: https://developers.google.com/speed/docs/insights/v5/get-started  ("Get a Key").
Real-user data (Chrome UX Report) is used when Google has it, otherwise the lab test.
"""

import json
import time
from concurrent.futures import ThreadPoolExecutor

import httpx

API = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"


def parse(data):
    """The numbers we keep from one PageSpeed response."""
    lh = data.get("lighthouseResult", {})
    audits = lh.get("audits", {})

    def num(key):
        v = audits.get(key, {}).get("numericValue")
        return round(v, 3) if isinstance(v, (int, float)) else None

    score = lh.get("categories", {}).get("performance", {}).get("score")
    field = {}
    metrics = (data.get("loadingExperience") or {}).get("metrics") or {}
    if metrics and (data.get("loadingExperience") or {}).get("id"):
        def pct(key):
            return (metrics.get(key) or {}).get("percentile")
        lcp, cls, inp = (pct("LARGEST_CONTENTFUL_PAINT_MS"), pct("CUMULATIVE_LAYOUT_SHIFT_SCORE"),
                         pct("INTERACTION_TO_NEXT_PAINT"))
        field = {k: v for k, v in (("lcp", lcp), ("cls", cls / 100 if cls is not None else None),
                                   ("inp", inp)) if v is not None}
        if field:
            field["overall"] = data["loadingExperience"].get("overall_category")
    return {"score": round(score * 100) if isinstance(score, (int, float)) else None,
            "lcp": num("largest-contentful-paint"), "cls": num("cumulative-layout-shift"),
            "tbt": num("total-blocking-time"), "fcp": num("first-contentful-paint"),
            "inp": field.get("inp"), "field": json.dumps(field) if field else None}


def check_url(url, key=None, strategy="mobile", client=None):
    params = {"url": url, "strategy": strategy, "category": "performance"}
    if key:
        params["key"] = key
    try:
        r = (client or httpx).get(API, params=params, timeout=120)
        if r.status_code == 429:
            return {"error": "Google's free quota without a key is used up - add a free API key."}
        if r.status_code != 200:
            msg = r.json().get("error", {}).get("message", r.text[:200]) if r.text else r.status_code
            return {"error": f"PageSpeed error: {msg}"[:300]}
        return parse(r.json())
    except (httpx.HTTPError, ValueError) as e:
        return {"error": f"{type(e).__name__}: {e}"[:300]}


def run(db, urls, key=None, strategy="mobile", progress=lambda done, total: None):
    """Check `urls` (4 at a time) and store the results in the crawl's cwv table."""
    db.execute("DELETE FROM cwv WHERE strategy = ?", (strategy,))
    done = 0
    with httpx.Client() as client, ThreadPoolExecutor(max_workers=4) as pool:
        for url, res in zip(urls, pool.map(lambda u: check_url(u, key, strategy, client), urls)):
            db.execute("INSERT INTO cwv VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (
                url, strategy, res.get("score"), res.get("lcp"), res.get("cls"), res.get("inp"),
                res.get("tbt"), res.get("fcp"), res.get("field"), res.get("error"), time.time()))
            done += 1
            progress(done, len(urls))
    db.commit()
