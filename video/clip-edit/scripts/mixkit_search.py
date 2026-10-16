"""List free-licence Mixkit stock videos for a search term (VideoObject entries in the page's JSON-LD @graph)."""
import json, re, sys, urllib.request
q = sys.argv[1]
url = f'https://mixkit.co/free-stock-video/discover/{q}/'
html = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=30).read().decode()
def walk(x):
    if isinstance(x, dict):
        if x.get('@type') == 'VideoObject': yield x
        for v in x.values(): yield from walk(v)
    elif isinstance(x, list):
        for v in x: yield from walk(v)
for block in re.findall(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', html, re.S):
    for v in walk(json.loads(block)):
        m = re.search(r'/videos/(\d+)/', json.dumps(v))
        print(m.group(1) if m else '?', '|', v.get('name'), '|', v.get('duration'), '|', str(v.get('license', ''))[-12:])
