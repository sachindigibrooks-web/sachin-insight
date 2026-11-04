"""White-label SEO audit report (HTML, and PDF through the PC's Edge / Chrome).

Branding comes from the app settings: agency name and logo, brand colour,
client name and report language (English / Hindi).
"""

import html
import os
import time

import checks
import store

T = {  # report text: key -> (English, Hindi)
    "title": ("SEO Audit Report", "SEO ऑडिट रिपोर्ट"),
    "prepared_for": ("Prepared for", "किसके लिए"),
    "prepared_by": ("Prepared by", "तैयार किया"),
    "date": ("Date", "तारीख"),
    "health": ("Site health", "साइट हेल्थ"),
    "health_note": ("Share of pages with no serious problems.", "जिन पेजों में कोई गंभीर गड़बड़ी नहीं, उनका हिस्सा।"),
    "summary": ("Summary", "सारांश"),
    "pages": ("Pages checked", "जाँचे गए पेज"),
    "errors": ("Serious problems", "गंभीर गड़बड़ियाँ"),
    "warnings": ("Warnings", "चेतावनियाँ"),
    "notices": ("Notices", "सूचनाएँ"),
    "speed": ("Avg. response", "औसत जवाब समय"),
    "broken": ("Broken pages (4xx/5xx)", "टूटे पेज (4xx/5xx)"),
    "priorities": ("What to fix first", "पहले क्या ठीक करें"),
    "issue": ("Problem", "गड़बड़ी"),
    "count": ("Pages", "पेज"),
    "fix": ("How to fix", "कैसे ठीक करें"),
    "examples": ("Examples", "उदाहरण"),
    "all_issues": ("All findings", "सभी नतीजे"),
    "page_speed": ("Page speed (Core Web Vitals)", "पेज स्पीड (Core Web Vitals)"),
    "gsc": ("Search Console: traffic at risk", "Search Console: ख़तरे में ट्रैफ़िक"),
    "a11y": ("Accessibility", "Accessibility"),
    "severity": ("Severity", "गंभीरता"),
    "error": ("Serious", "गंभीर"), "warning": ("Warning", "चेतावनी"), "notice": ("Notice", "सूचना"),
    "no_issues": ("No problems found - excellent!", "कोई गड़बड़ी नहीं मिली - बहुत बढ़िया!"),
}
SEV_COLOR = {"error": "#d33a2c", "warning": "#d98a00", "notice": "#3b6fd8"}


def branding():
    s = store.load_settings()
    return {"agency": s.get("agency_name") or "Sachin Samria", "logo": s.get("agency_logo") or "",
            "color": s.get("brand_color") or "#1f7a4d", "client": s.get("client_name") or "",
            "lang": s.get("report_lang") or "en", "website": s.get("agency_website") or ""}


def inp_text(inp):
    return f"{inp:.0f} ms" if inp else "-"


def build_html(cid):
    db = store.CrawlDB(cid)
    b = branding()
    hi = b["lang"] == "hi"
    t = lambda k: T[k][1 if hi else 0]  # noqa: E731
    e = html.escape
    start = (db.query("SELECT url FROM pages WHERE source = 'start'") or [{"url": ""}])[0]["url"]
    issues = checks.summary(db)
    score = checks.health_score(db)
    stats = db.query(f"""SELECT SUM({checks.HTML_PAGES}) AS pages,
        SUM(internal = 1 AND resource = 0 AND status >= 400) AS broken,
        AVG(CASE WHEN {checks.HTML_PAGES} THEN time_ms END) AS ms FROM pages""")[0]
    by_sev = {s: sum(i["count"] for i in issues if i["severity"] == s) for s in ("error", "warning", "notice")}
    color = b["color"]
    ring = "#2fae6e" if (score or 0) >= 90 else "#d98a00" if (score or 0) >= 70 else "#d33a2c"

    def examples(code, n=8):
        rows = db.query("SELECT url, detail FROM issues WHERE code = ? LIMIT ?", (code, n))
        return "".join(f"<li>{e(r['url'])}<small>{e(r['detail'])}</small></li>" for r in rows)

    top = [i for i in issues if i["severity"] in ("error", "warning")][:10]
    prio = "".join(f"""<div class="prio"><div class="prio-h"><span class="dot" style="background:{SEV_COLOR[i['severity']]}"></span>
        <b>{n}. {e(i['title_hi'] if hi else i['title'])}</b><em>{i['count']} {t('count').lower()}</em></div>
        <p>{e(i['fix_hi'] if hi else i['fix'])}</p><ul class="ex">{examples(i['code'])}</ul></div>"""
                   for n, i in enumerate(top, 1)) or f"<p>{t('no_issues')}</p>"
    table = "".join(f"""<tr><td><span class="dot" style="background:{SEV_COLOR[i['severity']]}"></span>{t(i['severity'])}</td>
        <td>{e(i['title_hi'] if hi else i['title'])}</td><td class="n">{i['count']}</td></tr>""" for i in issues)

    speed = db.query("SELECT url, strategy, score, lcp, cls, inp FROM cwv WHERE error IS NULL "
                     "ORDER BY score LIMIT 15")
    speed_html = "" if not speed else f"""<h2>{t('page_speed')}</h2><table><tr><th>URL</th><th>Score</th>
        <th>LCP</th><th>CLS</th><th>INP</th></tr>""" + "".join(
        f"<tr><td>{e(r['url'])}</td><td class='n'>{r['score'] if r['score'] is not None else '-'}</td>"
        f"<td class='n'>{(r['lcp'] or 0) / 1000:.1f} s</td><td class='n'>{(r['cls'] or 0):.2f}</td>"
        f"<td class='n'>{inp_text(r['inp'])}</td></tr>" for r in speed) + "</table>"
    gsc_rows = db.query("SELECT url, detail FROM issues WHERE code = 'gsc_traffic_problem' LIMIT 15")
    gsc_html = "" if not gsc_rows else f"<h2>{t('gsc')}</h2><ul class='ex'>" + "".join(
        f"<li>{e(r['url'])}<small>{e(r['detail'])}</small></li>" for r in gsc_rows) + "</ul>"
    a11y = [i for i in issues if i["category"] == "Accessibility"]
    a11y_html = "" if not a11y else f"<h2>{t('a11y')}</h2><table>" + "".join(
        f"<tr><td>{e(i['title_hi'] if hi else i['title'])}</td><td class='n'>{i['count']}</td></tr>"
        for i in a11y) + "</table>"
    logo = f'<img src="{e(b["logo"])}" class="logo">' if b["logo"].startswith("data:image/") else ""

    return f"""<!doctype html><html lang="{b['lang']}"><head><meta charset="utf-8">
<title>{t('title')} - {e(start)}</title><style>
@page {{ size: A4; margin: 16mm 14mm 18mm; }}
body {{ font: 11pt/1.5 "Segoe UI", "Nirmala UI", system-ui, sans-serif; color: #1a1d29; margin: 0; }}
.cover {{ height: 255mm; display: flex; flex-direction: column; justify-content: center; page-break-after: always;
         border-left: 10px solid {color}; padding-left: 14mm; }}
.cover h1 {{ font-size: 32pt; margin: 8mm 0 2mm; color: {color}; }}
.cover .site {{ font-size: 16pt; font-weight: 600; word-break: break-all; }}
.cover dl {{ margin-top: 14mm; display: grid; grid-template-columns: 40mm 1fr; gap: 2mm; }}
.cover dt {{ color: #687085; }} .cover dd {{ margin: 0; font-weight: 600; }}
.logo {{ max-height: 22mm; max-width: 70mm; object-fit: contain; }}
h2 {{ color: {color}; border-bottom: 2px solid {color}; padding-bottom: 1mm; margin-top: 9mm; page-break-after: avoid; }}
.score {{ display: flex; gap: 8mm; align-items: center; }}
.ring {{ width: 34mm; height: 34mm; border-radius: 50%; background: conic-gradient({ring} {(score or 0) * 3.6}deg, #eef1f6 0);
        display: grid; place-items: center; }}
.ring b {{ background: #fff; width: 25mm; height: 25mm; border-radius: 50%; display: grid; place-items: center; font-size: 18pt; }}
.tiles {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 4mm; margin-top: 6mm; }}
.tile {{ background: #f3f5f9; border-radius: 3mm; padding: 4mm; }} .tile b {{ font-size: 18pt; display: block; }}
.tile small {{ color: #687085; }}
.prio {{ border: 1px solid #e3e6ee; border-radius: 3mm; padding: 3mm 4mm; margin: 3mm 0; page-break-inside: avoid; }}
.prio-h {{ display: flex; align-items: center; gap: 2mm; }} .prio-h em {{ margin-left: auto; color: #687085; font-style: normal; }}
.prio p {{ margin: 1.5mm 0; }}
.ex {{ margin: 0; padding-left: 5mm; font-size: 9pt; color: #3a4052; }} .ex li {{ word-break: break-all; }}
.ex small {{ display: block; color: #8a90a2; }}
.dot {{ display: inline-block; width: 3mm; height: 3mm; border-radius: 50%; margin-right: 1.5mm; vertical-align: middle; }}
table {{ width: 100%; border-collapse: collapse; font-size: 9.5pt; }}
th, td {{ text-align: left; border-bottom: 1px solid #e3e6ee; padding: 1.6mm 2mm; word-break: break-all; }}
th {{ color: #687085; }} td.n {{ text-align: right; white-space: nowrap; }}
.brand {{ margin-top: 10mm; color: #687085; font-size: 9pt; }}
</style></head><body>
<section class="cover">{logo}<h1>{t('title')}</h1><div class="site">{e(start)}</div>
<dl>{f"<dt>{t('prepared_for')}</dt><dd>{e(b['client'])}</dd>" if b['client'] else ""}
<dt>{t('prepared_by')}</dt><dd>{e(b['agency'])}{f" · {e(b['website'])}" if b['website'] else ""}</dd>
<dt>{t('date')}</dt><dd>{time.strftime('%d %b %Y')}</dd></dl></section>

<h2>{t('summary')}</h2>
<div class="score"><div class="ring"><b>{score if score is not None else '-'}%</b></div>
<div><b style="font-size:14pt">{t('health')}</b><br><span style="color:#687085">{t('health_note')}</span></div></div>
<div class="tiles">
<div class="tile"><b>{stats['pages'] or 0}</b><small>{t('pages')}</small></div>
<div class="tile"><b style="color:#d33a2c">{by_sev['error']}</b><small>{t('errors')}</small></div>
<div class="tile"><b style="color:#d98a00">{by_sev['warning']}</b><small>{t('warnings')}</small></div>
<div class="tile"><b>{by_sev['notice']}</b><small>{t('notices')}</small></div>
<div class="tile"><b>{stats['broken'] or 0}</b><small>{t('broken')}</small></div>
<div class="tile"><b>{f"{round(stats['ms'])} ms" if stats['ms'] else '-'}</b><small>{t('speed')}</small></div>
</div>

<h2>{t('priorities')}</h2>{prio}
{speed_html}{gsc_html}{a11y_html}
<h2>{t('all_issues')}</h2><table><tr><th>{t('severity')}</th><th>{t('issue')}</th><th>{t('count')}</th></tr>{table}</table>
<p class="brand">{t('prepared_by')} {e(b['agency'])} · {time.strftime('%d %b %Y')}</p>
</body></html>"""


def build_pdf(cid):
    """PDF bytes of the report, printed by the PC's Edge / Chrome (headless)."""
    from playwright.sync_api import sync_playwright
    page_html = build_html(cid)
    agency = html.escape(branding()["agency"])
    footer = (f'<div style="font-size:8px;color:#888;width:100%;padding:0 14mm;display:flex;'
              f'justify-content:space-between"><span>{agency}</span>'
              f'<span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>')
    with sync_playwright() as pw:
        browser, errors = None, []
        exe = os.environ.get("SEO_CHROMIUM")
        for kw in ([{"executable_path": exe}] if exe else []) + [
                {"channel": "msedge"}, {"channel": "chrome"}, {}]:
            try:
                browser = pw.chromium.launch(headless=True, **kw)
                break
            except Exception as e:
                errors.append(str(e).splitlines()[0][:100])
        if not browser:
            raise RuntimeError("No Edge / Chrome found to make the PDF - use 'Open report' and "
                               "print it to PDF instead.")
        page = browser.new_page()
        page.set_content(page_html, wait_until="load")
        pdf = page.pdf(format="A4", print_background=True, display_header_footer=True,
                       header_template="<div></div>", footer_template=footer,
                       margin={"top": "16mm", "bottom": "18mm", "left": "14mm", "right": "14mm"})
        browser.close()
    return pdf


def save_branding(values):
    allowed = {"agency_name", "agency_logo", "brand_color", "client_name", "report_lang",
               "agency_website"}
    clean = {k: str(v)[:400000] for k, v in values.items() if k in allowed}
    if "brand_color" in clean and not (clean["brand_color"].startswith("#") and len(clean["brand_color"]) in (4, 7)):
        clean.pop("brand_color")
    return store.save_settings(clean)

