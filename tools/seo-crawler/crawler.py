"""The crawl engine: fetch every page of a site, record what SEO needs, store it in SQLite.

One crawl = one SQLite file (store.py). Pages are fetched with a few parallel
connections (polite by default: robots.txt is obeyed), redirects are recorded
hop by hop, HTML is parsed for titles, descriptions, headings, canonicals,
directives, links, images and structured data. Linked external pages and images
are checked with a light request so broken ones show up too.
"""

import asyncio
import gzip
import hashlib
import json
import re
import threading
import time
import urllib.robotparser
from dataclasses import asdict, dataclass
from urllib.parse import urldefrag, urljoin, urlsplit, urlunsplit

import httpx
from selectolax.lexbor import LexborHTMLParser

import store

USER_AGENT = "FreeSEOCrawler/1.0 (Made by Sachin Samria)"
AI_BOTS = ["GPTBot", "ChatGPT-User", "ClaudeBot", "PerplexityBot", "Google-Extended", "CCBot"]
MAX_HTML = 5 * 1024 * 1024  # don't parse more than 5 MB of one page


@dataclass
class Settings:
    start_url: str
    max_pages: int = 10000
    concurrency: int = 5
    delay: float = 0.0  # seconds between requests per connection
    respect_robots: bool = True
    check_external: bool = True
    check_images: bool = True
    include_subdomains: bool = False
    use_sitemaps: bool = True
    render_js: bool = False  # also open pages in a headless browser (for React/Vue/Next.js sites)
    timeout: float = 20.0
    user_agent: str = USER_AGENT


# ---------------------------------------------------------------- URLs

def normalize(url, base=None):
    """Absolute URL without #fragment, lower-case host, no default port. None if not http(s)."""
    url = (url or "").strip()
    if not url or url.startswith(("mailto:", "tel:", "javascript:", "data:", "#")):
        return None
    if base:
        url = urljoin(base, url)
    url = urldefrag(url)[0]
    parts = urlsplit(url)
    if parts.scheme not in ("http", "https") or not parts.hostname:
        return None
    host = parts.hostname.lower()
    port = parts.port
    if port and not ((parts.scheme == "http" and port == 80) or (parts.scheme == "https" and port == 443)):
        host = f"{host}:{port}"
    return urlunsplit((parts.scheme, host, parts.path or "/", parts.query, ""))


def site_host(url):
    host = urlsplit(url).hostname or ""
    return host[4:] if host.startswith("www.") else host


# ---------------------------------------------------------------- HTML

def text_of(node):
    return " ".join((node.text(separator=" ") or "").split()) if node else ""


def simhash(words):
    """64-bit SimHash of word 3-grams: near-duplicate pages differ in only a few bits."""
    if len(words) < 3:
        return 0
    v = [0] * 64
    for i in range(len(words) - 2):
        h = int.from_bytes(hashlib.md5(" ".join(words[i:i + 3]).encode()).digest()[:8], "big")
        for b in range(64):
            v[b] += 1 if h >> b & 1 else -1
    out = 0
    for b in range(64):
        if v[b] > 0:
            out |= 1 << b
    return out - (1 << 64) if out >= 1 << 63 else out  # SQLite stores signed 64-bit


def parse_html(html, url):
    tree = LexborHTMLParser(html)
    base = url
    b = tree.css_first("base[href]")
    if b:
        base = urljoin(url, b.attributes.get("href") or "")

    metas = {}
    for m in tree.css("meta"):
        a = m.attributes
        key = (a.get("name") or a.get("property") or a.get("http-equiv") or "").lower()
        if key:
            metas.setdefault(key, []).append(a.get("content") or "")

    # Only <head> titles count (an <svg> icon in the body can have its own <title>).
    titles = [text_of(t) for t in (tree.css("head title") or tree.css("title"))]
    canonicals = [urljoin(base, (c.attributes.get("href") or "").strip())
                  for c in tree.css("link[rel]")
                  if "canonical" in (c.attributes.get("rel") or "").lower().split()]
    jsonld_ok = jsonld_bad = 0
    for s in tree.css('script[type="application/ld+json"]'):
        try:
            json.loads(s.text() or "")
            jsonld_ok += 1
        except ValueError:
            jsonld_bad += 1

    links = []
    for a in tree.css("a[href]"):
        dst = normalize(a.attributes.get("href"), base)
        if dst:
            rel = (a.attributes.get("rel") or "").lower()
            links.append((dst, text_of(a)[:200], int("nofollow" in rel), "a"))
    images = []
    for img in tree.css("img"):
        src = img.attributes.get("src") or img.attributes.get("data-src")
        dst = normalize(src, base)
        if dst:
            alt = img.attributes.get("alt")
            images.append((dst, alt))
            links.append((dst, alt if alt is not None else None, 0, "img"))
    for s in tree.css("script[src]"):
        dst = normalize(s.attributes.get("src"), base)
        if dst:
            links.append((dst, None, 0, "script"))
    for c in tree.css("link[href]"):
        if "stylesheet" in (c.attributes.get("rel") or "").lower():
            dst = normalize(c.attributes.get("href"), base)
            if dst:
                links.append((dst, None, 0, "css"))

    for junk in tree.css("script, style, noscript, template"):
        junk.decompose()
    words = (tree.body.text(separator=" ") if tree.body else "").split()
    html_tag = tree.css_first("html")
    return {
        "title": titles[0] if titles else None, "titles": len(titles),
        "meta_desc": (metas.get("description") or [None])[0], "meta_descs": len(metas.get("description", [])),
        "h1": json.dumps([text_of(h)[:300] for h in tree.css("h1")], ensure_ascii=False),
        "h2s": len(tree.css("h2")),
        "canonical": json.dumps(canonicals),
        "meta_robots": ", ".join(metas.get("robots", []) + metas.get("googlebot", [])) or None,
        "words": len(words),
        "text_hash": hashlib.md5(" ".join(words).lower().encode()).hexdigest() if words else None,
        "simhash": simhash([w.lower() for w in words]),
        "lang": (html_tag.attributes.get("lang") if html_tag else None) or None,
        "viewport": int("viewport" in metas),
        "og": int("og:title" in metas),
        "jsonld": jsonld_ok, "jsonld_bad": jsonld_bad,
        "links": links, "images": images,
    }


# ---------------------------------------------------------------- crawl

class Crawl:
    """Runs one crawl in a background thread; read .progress while it runs."""

    def __init__(self, settings, crawl_id=None):
        self.s = settings
        start = normalize(settings.start_url)
        if not start:
            raise ValueError("Please enter a full website address, like https://example.com")
        self.start = start
        self.host = site_host(start)
        self.id = crawl_id or store.new_crawl(start, asdict(settings))
        self.db = store.CrawlDB(self.id)
        self.progress = {"status": "starting", "crawled": 0, "queued": 0, "errors": 0,
                         "current": "", "started": time.time(), "finished": None, "rate": 0.0}
        self.stopping = False
        self.seen = set()
        self.checked_ext = set()
        self.robots = None

    def internal(self, url):
        host = site_host(url)
        return host == self.host or (self.s.include_subdomains and host.endswith("." + self.host))

    def start_thread(self):
        t = threading.Thread(target=self.run, daemon=True)
        t.start()
        return t

    def stop(self):
        self.stopping = True

    def run(self):
        try:
            asyncio.run(self.main())
            self.progress["status"] = "stopped" if self.stopping else "analysing"
            import checks
            checks.analyse(self.db)
            self.progress["status"] = "stopped" if self.stopping else "finished"
        except Exception as e:  # never leave the dashboard waiting forever
            self.progress.update(status="failed", error=str(e))
        finally:
            self.progress["finished"] = time.time()
            store.finish_crawl(self.id, self.progress["crawled"], self.progress["status"])
            self.db.commit()

    async def main(self):
        limits = httpx.Limits(max_connections=self.s.concurrency * 2,
                              max_keepalive_connections=self.s.concurrency)
        async with httpx.AsyncClient(headers={"User-Agent": self.s.user_agent},
                                     timeout=self.s.timeout, limits=limits,
                                     follow_redirects=False, http2=False) as client:
            self.client = client
            self.queue = asyncio.Queue()
            self.renderer = None
            if self.s.render_js:
                await self.start_renderer()
            await self.load_robots()
            self.add(self.start, 0, "start")
            sitemap_urls = await self.load_sitemaps() if self.s.use_sitemaps else []
            self.progress["status"] = "running"
            workers = [asyncio.create_task(self.worker()) for _ in range(self.s.concurrency)]
            await self.queue.join()
            # Sitemap pages no link led to (orphans) are crawled last, so pages reached by
            # links keep their real depth and source.
            for u in sitemap_urls:
                if self.internal(u):
                    self.add(u, None, "sitemap")
            await self.queue.join()
            for w in workers:
                w.cancel()
            await asyncio.gather(*workers, return_exceptions=True)
            if self.renderer:
                await self.renderer.stop()
        self.db.commit()

    async def start_renderer(self):
        import renderer
        self.progress["status"] = "starting browser"
        r = renderer.Renderer(self.s.user_agent, self.s.concurrency, self.s.timeout)
        try:
            await r.start()
            self.renderer = r
            self.db.set_meta("renderer", r.browser_name)
        except Exception as e:  # crawl without rendering rather than not at all
            self.db.set_meta("render_error", str(e)[:500])
            self.progress["note"] = str(e)[:300]

    def add(self, url, depth, source):
        if url in self.seen or len(self.seen) >= self.s.max_pages or self.stopping:
            return
        self.seen.add(url)
        self.queue.put_nowait((url, depth, source))
        self.progress["queued"] = self.queue.qsize()

    async def worker(self):
        while True:
            url, depth, source = await self.queue.get()
            try:
                if not self.stopping:
                    await self.fetch_page(url, depth, source)
            except Exception as e:
                self.db.add_page({"url": url, "internal": 1, "depth": depth, "source": source,
                                  "error": f"{type(e).__name__}: {e}"[:300]})
                self.progress["errors"] += 1
            finally:
                done = self.progress["crawled"] = self.progress["crawled"] + 1
                self.progress["queued"] = self.queue.qsize()
                self.progress["rate"] = done / max(1e-6, time.time() - self.progress["started"])
                if done % 50 == 0:
                    self.db.commit()
                self.queue.task_done()
                if self.s.delay:
                    await asyncio.sleep(self.s.delay)

    def blocked(self, url):
        return bool(self.robots and not self.robots.can_fetch(self.s.user_agent, url))

    async def fetch_page(self, url, depth, source):
        self.progress["current"] = url
        row = {"url": url, "internal": 1, "depth": depth, "source": source}
        if self.s.respect_robots and self.blocked(url):
            row["blocked"] = 1
            self.db.add_page(row)
            return
        t0 = time.monotonic()
        async with self.client.stream("GET", url) as r:
            body = b""
            ctype = r.headers.get("content-type", "").split(";")[0].strip().lower()
            if r.status_code == 200 and ctype in ("text/html", "application/xhtml+xml"):
                async for chunk in r.aiter_bytes():
                    body += chunk
                    if len(body) > MAX_HTML:
                        break
        row.update(status=r.status_code, content_type=ctype or None,
                   time_ms=int((time.monotonic() - t0) * 1000),
                   size=int(r.headers.get("content-length") or len(body) or 0),
                   x_robots=r.headers.get("x-robots-tag"),
                   hsts=int("strict-transport-security" in r.headers))
        if r.is_redirect:
            target = normalize(r.headers.get("location"), url)
            row["redirect_to"] = target
            self.db.add_page(row)
            if target:
                self.db.add_links(url, [(target, None, 0, "redirect")])
                if self.internal(target):
                    self.add(target, depth, "redirect")
                else:
                    await self.check_external(target)
            return
        if not body:
            self.db.add_page(row)
            return
        page = parse_html(body.decode(r.encoding or "utf-8", errors="replace"), url)
        if self.renderer:
            # Keep what the raw HTML had, then check the page as the browser built it.
            row["raw_words"] = page["words"]
            row["raw_links"] = sum(1 for d, _, _, k in page["links"] if k == "a" and self.internal(d))
            try:
                page = parse_html(await self.renderer.render(url), url)
                row["rendered"] = 1
            except Exception as e:
                row["render_error"] = str(e)[:300]
        links, images = page.pop("links"), page.pop("images")
        if url.startswith("https://"):
            row["mixed"] = sum(1 for d, _, _, k in links if k != "a" and d.startswith("http://"))
        row.update(page)
        self.db.add_page(row)
        self.db.add_links(url, links)
        follow = "nofollow" not in (row.get("meta_robots") or "").lower()
        for dst, _, nofollow, kind in links:
            if kind == "a" and self.internal(dst):
                if follow:
                    self.add(dst, None if depth is None else depth + 1, "link")
            elif kind == "a" and self.s.check_external:
                await self.check_external(dst)
            elif kind == "img" and self.s.check_images:
                await self.check_external(dst, image=True)

    async def check_external(self, url, image=False):
        """A light request for an external page or any image: status and size only."""
        if url in self.checked_ext or url in self.seen:
            return
        self.checked_ext.add(url)
        row = {"url": url, "internal": 0 if not self.internal(url) else 1, "source": "check",
               "depth": None}
        try:
            t0 = time.monotonic()
            r = await self.client.head(url, follow_redirects=True)
            if r.status_code in (405, 403, 501):  # some servers refuse HEAD
                async with self.client.stream("GET", url, follow_redirects=True) as r:
                    pass
            row.update(status=r.status_code, time_ms=int((time.monotonic() - t0) * 1000),
                       content_type=r.headers.get("content-type", "").split(";")[0] or None,
                       size=int(r.headers.get("content-length") or 0))
        except httpx.HTTPError as e:
            row["error"] = f"{type(e).__name__}: {e}"[:300]
        self.db.add_page(row, resource=True)

    async def load_robots(self):
        root = f"{urlsplit(self.start).scheme}://{urlsplit(self.start).netloc}"
        text, problem = "", None
        try:
            r = await self.client.get(root + "/robots.txt", follow_redirects=True)
            if r.status_code == 200:
                text = r.text
            elif r.status_code >= 500:
                problem = f"HTTP {r.status_code}"
        except httpx.HTTPError as e:
            problem = f"{type(e).__name__}: {e}"[:200]
        if problem:  # crawl anyway, but say so: the site's rules were not seen
            self.db.set_meta("robots_error", problem)
        rp = urllib.robotparser.RobotFileParser()
        rp.parse(text.splitlines())
        self.robots = rp
        self.sitemap_urls = rp.site_maps() or []
        blocked_ai = [bot for bot in AI_BOTS if text and not rp.can_fetch(bot, self.start)]
        llms = False
        try:
            r = await self.client.get(root + "/llms.txt", follow_redirects=True)
            llms = r.status_code == 200 and "html" not in r.headers.get("content-type", "")
        except httpx.HTTPError:
            pass
        self.db.set_meta("robots_txt", text[:100000])
        self.db.set_meta("ai_bots_blocked", json.dumps(blocked_ai))
        self.db.set_meta("llms_txt", json.dumps(llms))

    async def load_sitemaps(self):
        root = f"{urlsplit(self.start).scheme}://{urlsplit(self.start).netloc}"
        todo = list(self.sitemap_urls) or [root + "/sitemap.xml"]
        seen, urls, found = set(), [], []
        while todo and len(seen) < 50:
            sm = todo.pop(0)
            if sm in seen:
                continue
            seen.add(sm)
            try:
                r = await self.client.get(sm, follow_redirects=True)
            except httpx.HTTPError:
                continue
            if r.status_code != 200:
                continue
            data = r.content
            if data[:2] == b"\x1f\x8b":
                data = gzip.decompress(data)
            text = data.decode("utf-8", errors="replace")
            if "<urlset" not in text and "<sitemapindex" not in text:
                continue
            found.append(sm)
            locs = [normalize(x.strip()) for x in re.findall(r"<loc>\s*(.*?)\s*</loc>", text, re.S)]
            if "<sitemapindex" in text:
                todo += [u for u in locs if u]
            else:
                urls += [u for u in locs if u]
        self.db.set_meta("sitemaps", json.dumps(found))
        self.db.add_sitemap_urls(urls)
        return urls
