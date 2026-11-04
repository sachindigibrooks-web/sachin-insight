# Free SEO Crawler

**Made by Sachin Samria**

Screaming Frog jaisa website crawler — poori website crawl karke 50+ SEO gadbadiyan dhundhta
hai, har gadbadi ke saath "kyun zaroori hai aur kaise theek karein" (English + Hindi).
**Koi page limit nahi**, free, data aapke PC par hi rehta hai.

## Kya-kya check karta hai

| Category | Checks |
|---|---|
| Response | 4xx, 5xx, timeout, robots.txt se blocked, slow pages (>1.5 s), http:// URLs on https |
| Redirects | Internal links to redirects, redirect chains (2+ hops), redirect loops |
| Links | Broken internal / external links (kis page par hain), nofollow internal links, dead-end pages, **orphan pages** (sitemap me hain par koi link nahi), deep pages (>3 clicks) |
| Titles | Missing, duplicate, too long (>60), too short (<30), multiple |
| Meta description | Missing, duplicate, too long (>160), too short (<70), multiple |
| Headings | Missing / multiple / duplicate H1, no H2 |
| Content | Thin (<200 words), exact duplicates, **near-duplicates** (SimHash) |
| Indexing | noindex, canonical missing / pointing elsewhere / broken / multiple, sitemap me non-indexable URLs, indexable pages jo sitemap me nahi, sitemap hi nahi |
| Images | Missing alt, broken images, large images (>200 KB) |
| Security & mobile | Mixed content, HSTS, viewport, `<html lang>` |
| Structured data & social | Invalid JSON-LD, no structured data, no Open Graph |
| URLs | Capital letters, underscores, very long, ?parameters |
| **AI search** | robots.txt me GPTBot / ClaudeBot / PerplexityBot / Google-Extended blocked? `llms.txt` hai? |

Dashboard me:
- **Overview** — Site health score, status codes, click depth, top issues
- **Issues** — har gadbadi, affected URLs aur fix ka tarika; CSV download
- **Pages** — saare URLs ki table (search, sort, filter: errors / redirects / external / images / blocked);
  kisi bhi URL par click karke uske inlinks, outlinks aur issues
- **Compare** — ek hi site ke do crawls milao: nayi gadbadiyan, theek hui, naye / hate URLs,
  status aur title ke badlaav
- **Export** — Excel (Pages, Issues, Broken links, Images sheets) ya CSV
- **हिंदी / English** button

## Chalana

**Installer se (Windows):** GitHub Actions → "Build SEO crawler" → Artifacts → `FreeSEOCrawler-Windows`
→ `FreeSEOCrawler-Setup.exe`. Install karo, Start Menu se "Free SEO Crawler" kholo — ek chhoti
window khulegi aur dashboard browser me khul jayega. Window band = app band.

**Python se:** `start.bat` double-click (Windows), ya:

```bash
pip install -r requirements.txt
```

```bash
python app.py
```

**Installer khud banana:** [Inno Setup 6](https://jrsoftware.org/isdl.php) install karo, phir
`build_windows.bat` double-click. Mac: `./build_mac.sh`.

## JavaScript rendering (React, Vue, Next.js, Angular sites)

Settings me **Render JavaScript** tick karo. Har page pehle raw HTML se aur phir asli browser me
khol kar (jaise Google karta hai) check hota hai. PC par pehle se laga **Microsoft Edge** (Windows
me hamesha hota hai) ya **Google Chrome** use hota hai — kuch bada download nahi. Dono na hon to
Chromium ek baar apne aap download hota hai (~150 MB).

Iske saath ek nayi check: **"Content or links appear only after JavaScript"** — jin pages ka text
ya links sirf JavaScript se bante hain. Google unhe der se dekhta hai aur **ChatGPT / Claude /
Perplexity ke crawlers JavaScript chalate hi nahi**, to wo content AI search me nahi aata.
Rendering dheema hai (ek saath max 4 pages), isliye sirf JavaScript wali sites par on karo.

## Settings

- **Max pages** (default 10,000) — isse zyada nahi crawl karega
- **Parallel requests** (default 5) — zyada = tez, par site par zyada load
- robots.txt maanna, external links / images check, XML sitemap use karna, subdomains bhi,
  JavaScript rendering

Normal PC par lagbhag 20–40 pages / second (site ki speed par depend). Ek 1,200 page ki site
~25 second me crawl hui, analysis 1 second se kam.

## Dhyan rakhein

- Sirf apni ya permission wali site crawl karo. Crawler robots.txt maanta hai aur dheere chalta hai.
- Dashboard sirf isi PC par khulta hai (`127.0.0.1`) — crawl data private rehta hai.
- Data yahan rehta hai: Windows `%LOCALAPPDATA%\FreeSEOCrawler`, Mac `~/Library/Application Support/FreeSEOCrawler`.

## Test

`python tests/test_checks.py` — ek nakli website (`tests/test_site.py`) jisme jaan-boojh kar
37 tarah ki gadbadiyan daali hain, crawl karta hai aur check karta hai ki har ek pakdi gayi.
GitHub par har build se pehle ye test chalta hai.
