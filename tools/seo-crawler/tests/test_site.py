"""A tiny website full of known SEO problems, for testing the crawler.

Served at http://localhost:<port>; "external" links point at http://127.0.0.1:<port>
(a different host, so the crawler treats them as another site).
"""

import time

from flask import Flask, Response, redirect

app = Flask(__name__)
PORT = 8799
WORDS = ("search engines read every page of a website and decide which pages answer a "
         "question best so good pages need clear titles helpful text and working links ").split()


def text(n, swap=None):
    words = [WORDS[i % len(WORDS)] + str(i // len(WORDS)) for i in range(n)]
    if swap:
        words[swap] = "different"
    return " ".join(words)


def page(title="A good page title for testing the crawler", desc=None, h1="Main heading",
         body="", head="", lang=True, viewport=True, h2=True):
    desc = desc if desc is not None else ("A helpful description of this page that is long "
                                          "enough to show nicely in search results snippets.")
    return (f"<!doctype html><html{' lang=en' if lang else ''}><head>"
            + (f"<title>{title}</title>" if title else "")
            + (f'<meta name="description" content="{desc}">' if desc else "")
            + ('<meta name="viewport" content="width=device-width">' if viewport else "")
            + '<meta property="og:title" content="x">'
            + '<script type="application/ld+json">{"@type": "Organization"}</script>'
            + head + "</head><body>"
            + (f"<h1>{h1}</h1>" if h1 else "") + ("<h2>Section</h2>" if h2 else "")
            + body + "</body></html>")


@app.get("/")
def home():
    ext = f"http://127.0.0.1:{PORT}"
    return page(body=f"""<p>{text(300)}</p>
        <a href="/a">A</a> <a href="/b">B</a> <a href="/dup1">D1</a> <a href="/dup2">D2</a>
        <a href="/near1">N1</a> <a href="/near2">N2</a> <a href="/redirect1">R</a>
        <a href="/loop1">L</a> <a href="/missing">gone</a> <a href="/error">err</a>
        <a href="/slow">slow</a> <a href="/deep1">deep</a> <a href="/blocked/page">blocked</a>
        <a href="/Upper_Case">U</a> <a href="/params?x=1">P</a> <a href="/js">JS app</a>
        <a href="{ext}/ext-missing">external broken</a> <a href="{ext}/ext-ok">external ok</a>
        <a href="mailto:x@example.com">mail</a>""",
                head='<link rel="canonical" href="/">')


@app.get("/a")
def a():
    return page(title=None, desc="", h1=None, body="""<p>short page</p>
        <img src="/img/ok.png"><img src="/img/missing.png" alt="gone">
        <img src="/img/big.jpg" alt="big"> <a href="/b" rel="nofollow">B</a> <a href="/">home</a>""")


@app.get("/b")
def b():
    return page(title="T" * 80, desc="too short", h1="One",
                body=f"<h1>Two</h1><p>{text(250)}</p><a href='/'>home</a>",
                head='<title>Second title</title><meta name="robots" content="noindex">'
                     '<link rel="canonical" href="/a">'
                     '<script type="application/ld+json">{broken json</script>')


@app.get("/dup1")
@app.get("/dup2")
def dup():
    return page(title="Duplicate page", body=f"<p>{text(300)} duplicated</p><a href='/'>home</a>")


@app.get("/near1")
def near1():
    return page(title="Near one page title for testing", body=f"<p>{text(400)}</p><a href='/'>h</a>")


@app.get("/near2")
def near2():
    return page(title="Near two page title for testing", body=f"<p>{text(400, swap=200)}</p><a href='/'>h</a>")


@app.get("/redirect1")
def r1():
    return redirect("/redirect2", 301)


@app.get("/redirect2")
def r2():
    return redirect("/a", 301)


@app.get("/loop1")
def l1():
    return redirect("/loop2", 302)


@app.get("/loop2")
def l2():
    return redirect("/loop1", 302)


@app.get("/error")
def error():
    return "boom", 500


@app.get("/slow")
def slow():
    time.sleep(1.7)
    return page(title="Slow page title for the test site", body=f"<p>{text(300)}</p><a href='/'>h</a>")


@app.get("/deep<int:n>")
def deep(n):
    nxt = f'<a href="/deep{n + 1}">next</a>' if n < 5 else ""
    return page(title=f"Deep page number {n} for the crawler test", body=f"<p>{text(300)}</p>{nxt}")


@app.get("/orphan")
def orphan():
    return page(title="Orphan page that nothing links to at all", body=f"<p>{text(300)}</p><a href='/'>h</a>")


@app.get("/Upper_Case")
@app.get("/params")
def misc():
    return page(title="Some other page title for this test", body=f"<p>{text(300)}</p><a href='/'>h</a>")


@app.get("/js")
def js_page():
    """Like a React / Vue app: the raw HTML is an empty shell, JavaScript builds everything."""
    content = text(300)
    return f"""<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width">
        <meta name="description" content="A page built entirely by JavaScript, like a single page app.">
        </head><body><div id="root"></div><script>
        document.title = "Page rendered by JavaScript for testing";
        document.getElementById("root").innerHTML =
          "<h1>Built by JavaScript</h1><h2>Part</h2><p>{content}</p><a href='/js-child'>child</a>";
        </script></body></html>"""


@app.get("/js-child")
def js_child():
    return page(title="Child page only linked from JavaScript", body=f"<p>{text(300)}</p><a href='/'>h</a>")


@app.get("/ext-ok")
def ext_ok():
    return "ok"


@app.get("/img/ok.png")
def img_ok():
    return Response(b"\x89PNG" + b"0" * 100, mimetype="image/png")


@app.get("/img/big.jpg")
def img_big():
    return Response(b"0" * 300 * 1024, mimetype="image/jpeg")


@app.get("/robots.txt")
def robots():
    return Response("User-agent: *\nDisallow: /blocked/\n\nUser-agent: GPTBot\nDisallow: /\n\n"
                    f"Sitemap: http://localhost:{PORT}/sitemap.xml\n", mimetype="text/plain")


@app.get("/sitemap.xml")
def sitemap():
    urls = "".join(f"<url><loc>http://localhost:{PORT}{p}</loc></url>"
                   for p in ("/", "/a", "/orphan", "/missing"))
    return Response(f'<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/'
                    f'sitemap/0.9">{urls}</urlset>', mimetype="application/xml")


if __name__ == "__main__":
    app.run(port=PORT, threaded=True)
