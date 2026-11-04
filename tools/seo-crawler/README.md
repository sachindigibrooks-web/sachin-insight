# Free SEO Crawler

**Made by Sachin Samria**

Screaming Frog jaisa website crawler — poori website crawl karke 80+ SEO gadbadiyan dhundhta
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

## Paid tools ke features — yahan free

| Feature | Kahan | Kya karta hai |
|---|---|---|
| **White-label PDF report** | Report tab · ⚙ Settings me branding | Aapka/agency ka naam, logo, rang, client ka naam, English ya Hindi. Health score, "pehle kya theek karein" (examples ke saath), page speed, Search Console, accessibility. PDF PC ke Edge/Chrome se banta hai. |
| **Scheduled crawl + alerts** | Schedules tab · ⚙ Settings me Telegram / e-mail | Har N din me site apne aap crawl, pichhle crawl se tulna, aur Telegram ya e-mail par message (hamesha, ya sirf jab kuch bigde). App khuli honi chahiye — installer me "Start with Windows" tick karo. |
| **Custom search & extraction** | Settings → Custom search | Har page par text dhundho ("page contains" / "does NOT contain", jaise purana analytics code) ya CSS / XPath / regex se data nikalo (price, author…). Custom tab + Excel/CSV. |
| **Internal link score (PageRank)** | Pages table "Link score" | Har page ko andar ke links se kitni taqat milti hai (0–100). "Sirf ek page se linked" pages bhi dikhte hain. |
| **Site map (graph + folders)** | Site map tab | 150 sabse zaroori pages ka link graph (drag karo, double-click = details) aur folder tree jisme har folder ke errors. |
| **Core Web Vitals** | Speed tab · ⚙ Settings me PageSpeed key | Google PageSpeed Insights se sabse zaroori pages ke LCP, CLS, INP, score (asli users ka data jab Google ke paas ho). Free key: console.cloud.google.com → "PageSpeed Insights API" enable → Credentials. |
| **Search Console data** | Search Console tab | GSC ka Pages export (.zip/.csv) upload karo: traffic wale pages jo ab toote / noindex hain, Google me dikhne wale par site se unlinked pages, high impressions + low CTR. |
| **Log file analysis** | Logs tab | Apache/Nginx access log (.log/.gz) upload karo: Googlebot, Bing, GPTBot, ClaudeBot… asal me kaunse pages dekhte hain, error pages par bots, ?parameter URLs par crawl budget, aur kaunse pages Googlebot ne dekhe hi nahi. |
| **Accessibility audit** | Issues → Accessibility | Bina browser: bina label ke form fields, bina text ke links/buttons, khali / chhoote headings. JavaScript rendering ke saath **axe-core** (WCAG 2.1 A/AA) ka poora audit. |
| **Structured data validation** | Issues → Structured data | Product, Offer, Review, FAQ, Breadcrumb, Article, Event, Recipe, Video, Job, LocalBusiness… Google rich results ke zaroori aur suggested fields check. |

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
37 tarah ki gadbadiyan daali hain, crawl karta hai (raw HTML aur JavaScript rendering dono) aur
check karta hai ki har ek pakdi gayi. `python tests/test_features.py` — custom search, structured
data, accessibility (axe bhi), link score, Search Console, logs, PageSpeed, PDF report aur alerts.
GitHub par har build se pehle dono test chalte hain.

axe-core (`vendor/`, MPL-2.0, Deque Systems) bina badlaav ke use hota hai.
