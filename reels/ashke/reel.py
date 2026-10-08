"""Ashke - Karan Aujla | lyric reel renderer (1080x1920, 30fps).
Usage: python3 reel.py [out.mp4] [--frames t1,t2,...] (preview stills)
"""
import sys, os, math, random, subprocess
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance

D = os.path.dirname(os.path.abspath(__file__))
AS = os.path.join(D, "assets")
AUDIO = os.path.join(D, "src.mp4")
W, H, FPS, DUR = 1080, 1920, 30, 45.10

RED = (214, 28, 38)
BLACK = (14, 13, 15)
WHITE = (245, 242, 236)
BLUE = (38, 150, 222)
PAPER_TXT = (28, 26, 26)

BEATS = [0.1, 0.58, 1.09, 1.57, 2.02, 2.46, 2.91, 3.33, 3.78, 4.22, 4.67, 5.12, 5.57, 6.02, 6.46, 6.91, 7.36, 7.81,
         8.26, 8.7, 9.15, 9.6, 10.05, 10.53, 10.98, 11.42, 11.87, 12.29, 12.77, 13.22, 13.7, 14.21, 14.69, 15.14,
         15.65, 16.1, 16.51, 16.99, 17.44, 17.89, 18.34, 18.78, 19.23, 19.68, 20.13, 20.58, 21.02, 21.47, 21.92,
         22.37, 22.82, 23.26, 23.68, 24.16, 24.61, 25.06, 25.5, 25.95, 26.4, 26.82, 27.26, 27.74, 28.19, 28.64,
         29.12, 29.6, 30.05, 30.5, 30.91, 31.33, 31.78, 32.22, 32.67, 33.12, 33.57, 34.02, 34.46, 34.91, 35.36,
         35.81, 36.26, 36.7, 37.15, 37.6, 38.05, 38.5, 38.94, 39.39, 39.84, 40.26, 40.74, 41.18, 41.63, 42.08,
         42.53, 42.98, 43.42, 43.84, 44.29, 44.7]


# ---------------------------------------------------------------- helpers
def c01(x): return max(0.0, min(1.0, x))
def e_out(x): x = c01(x); return 1 - (1 - x) ** 3
def e_back(x, s=2.2): x = c01(x) - 1; return 1 + (s + 1) * x ** 3 + s * x ** 2
def e_in(x): x = c01(x); return x ** 3


FONTS = {
    "anton": "Anton-Regular.ttf", "bebas": "BebasNeue-Regular.ttf", "oswald": "Oswald.ttf",
    "marker": "PermanentMarker.ttf", "archivo": "ArchivoBlack-Regular.ttf",
}


@lru_cache(None)
def font(name, size):
    f = ImageFont.truetype(os.path.join(AS, "fonts", FONTS[name]), size)
    if name == "oswald":
        try: f.set_variation_by_name("Bold")
        except Exception: pass
    return f


@lru_cache(None)
def text_img(txt, fname, size, col, stretch=1.0, maxw=1000, stroke=0, scol=None):
    f = font(fname, size)
    l, t, r, b = f.getbbox(txt, stroke_width=stroke)
    im = Image.new("RGBA", (r - l + 20, b - t + 20), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10 - l, 10 - t), txt, font=f, fill=col + (255,), stroke_width=stroke,
                            stroke_fill=(scol or col) + (255,))
    im = im.crop(im.getbbox())
    w, h = im.size
    h2 = int(h * stretch)
    if w > maxw:
        h2 = int(h2 * maxw / w); w = maxw
    return im.resize((w, max(1, h2)), Image.LANCZOS)


def jag_poly(w, h, seed, amp=10, step=18):
    rnd = random.Random(seed)
    pts = []
    for x in range(0, w + 1, step): pts.append((x, rnd.uniform(0, amp)))
    for y in range(0, h + 1, step): pts.append((w - rnd.uniform(0, amp), y))
    for x in range(w, -1, -step): pts.append((x, h - rnd.uniform(0, amp)))
    for y in range(h, -1, -step): pts.append((rnd.uniform(0, amp), y))
    return pts


@lru_cache(None)
def paper_tex_small():
    return Image.open(os.path.join(AS, "paper3.jpg")).convert("L")


def textured(im, strength=0.35, seed=0):
    """multiply a crumpled paper texture into an RGBA patch"""
    tex = paper_tex_small()
    rnd = random.Random(seed)
    w, h = im.size
    tw, th = tex.size
    sc = max(w / tw, h / th, 0.5)
    t2 = tex.resize((max(w, int(tw * sc)) + 2, max(h, int(th * sc)) + 2))
    x = rnd.randint(0, t2.size[0] - w); y = rnd.randint(0, t2.size[1] - h)
    t2 = np.asarray(t2.crop((x, y, x + w, y + h)), np.float32) / 255.0
    t2 = 1 - strength + strength * (t2 / max(t2.mean(), 1e-3)).clip(0, 1.4)
    a = np.asarray(im, np.float32)
    a[..., :3] = (a[..., :3] * t2[..., None]).clip(0, 255)
    return Image.fromarray(a.astype(np.uint8), "RGBA")


@lru_cache(None)
def torn_shape(w, h, col, seed, amp=22):
    im = Image.new("RGBA", (w + 4, h + 4), (0, 0, 0, 0))
    ImageDraw.Draw(im).polygon([(x + 2, y + 2) for x, y in jag_poly(w, h, seed, amp, 14)], fill=col + (255,))
    return textured(im, 0.45, seed)


@lru_cache(None)
def label(txt, fname, size, fg, bg, seed=1, pad=(28, 18), stretch=1.0, maxw=980):
    t = text_img(txt, fname, size, fg, stretch, maxw - 2 * pad[0])
    w, h = t.size[0] + 2 * pad[0], t.size[1] + 2 * pad[1]
    im = Image.new("RGBA", (w + 4, h + 4), (0, 0, 0, 0))
    ImageDraw.Draw(im).polygon([(x + 2, y + 2) for x, y in jag_poly(w, h, seed, 6, 10)], fill=bg + (255,))
    im = textured(im, 0.4, seed)
    im.alpha_composite(t, (pad[0] + 2, pad[1] + 2))
    return im


@lru_cache(None)
def star(r, n, col, inner=0.45):
    im = Image.new("RGBA", (2 * r + 4, 2 * r + 4), (0, 0, 0, 0))
    pts = []
    for i in range(2 * n):
        a = math.pi * i / n - math.pi / 2
        rr = r if i % 2 == 0 else r * inner
        pts.append((r + 2 + rr * math.cos(a), r + 2 + rr * math.sin(a)))
    ImageDraw.Draw(im).polygon(pts, fill=col + (255,))
    return im


# ---------------------------------------------------------------- photo assets
@lru_cache(None)
def cut(name):
    im = Image.open(os.path.join(AS, "cut", name + ".png")).convert("RGBA")
    a = np.asarray(im)[..., 3]
    im.putalpha(Image.fromarray(np.where(a > 40, a, 0).astype(np.uint8)))
    return im.crop(im.getbbox())


def duo(im, c0, c1, c2):
    g = np.asarray(ImageOps.autocontrast(im.convert("L"), cutoff=1), np.float32) / 255.0
    g = np.clip((g - 0.5) * 1.35 + 0.5, 0, 1)
    c0, c1, c2 = (np.array(c, np.float32) for c in (c0, c1, c2))
    lo = g[..., None] * 2
    out = np.where(g[..., None] < 0.5, c0 + (c1 - c0) * lo, c1 + (c2 - c1) * (lo - 1))
    return Image.fromarray(out.clip(0, 255).astype(np.uint8))


@lru_cache(None)
def photo(name, var, h, stk=0):
    """cutout photo, variant + optional sticker border, resized to height h"""
    im = cut(name)
    sc = h / im.size[1]
    im = im.resize((max(1, int(im.size[0] * sc)), h), Image.LANCZOS)
    a = im.split()[3]
    rgb = im.convert("RGB")
    if var == "bw":
        g = ImageOps.autocontrast(rgb.convert("L"), cutoff=1)
        rgb = ImageEnhance.Contrast(g).enhance(1.35).convert("RGB")
    elif var == "red":
        rgb = duo(rgb, (12, 10, 12), RED, (250, 238, 228))
    elif var == "dark":
        rgb = ImageEnhance.Contrast(ImageEnhance.Brightness(rgb).enhance(0.8)).enhance(1.2)
        rgb = ImageEnhance.Color(rgb).enhance(0.75)
    elif var == "color":
        rgb = ImageEnhance.Contrast(rgb).enhance(1.12)
        rgb = ImageEnhance.Color(rgb).enhance(0.9)
    out = rgb.convert("RGBA"); out.putalpha(a)
    if stk:
        pad = stk + 4
        big = Image.new("RGBA", (out.size[0] + 2 * pad, out.size[1] + 2 * pad), (0, 0, 0, 0))
        aa = Image.new("L", big.size, 0); aa.paste(a, (pad, pad))
        small = aa.resize((aa.size[0] // 4, aa.size[1] // 4))
        dil = small.filter(ImageFilter.MaxFilter(2 * (stk // 4) + 1)).resize(aa.size, Image.BILINEAR)
        dil = dil.point(lambda v: 255 if v > 90 else 0).filter(ImageFilter.GaussianBlur(1))
        white = Image.new("RGBA", big.size, WHITE + (255,)); white.putalpha(dil)
        big.alpha_composite(textured(white, 0.3, hash(name) % 99))
        big.alpha_composite(out, (pad, pad))
        out = big
    return out


@lru_cache(None)
def shadowed(key_img_id, blur=14):
    return None


def put(canvas, im, cx, cy, scale=1.0, rot=0.0, alpha=1.0, shadow=0):
    if scale <= 0.01 or alpha <= 0.01: return
    if abs(scale - 1) > 0.002:
        im = im.resize((max(1, int(im.size[0] * scale)), max(1, int(im.size[1] * scale))), Image.BILINEAR)
    if abs(rot) > 0.05:
        im = im.rotate(rot, Image.BICUBIC, expand=True)
    if alpha < 0.999:
        im = im.copy(); im.putalpha(im.split()[3].point(lambda v: int(v * alpha)))
    x, y = int(cx - im.size[0] / 2), int(cy - im.size[1] / 2)
    if shadow:
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
        sh.putalpha(im.split()[3].point(lambda v: int(v * 0.45)).filter(ImageFilter.BoxBlur(shadow)))
        paste_clip(canvas, sh, x + shadow, y + shadow + 6)
    paste_clip(canvas, im, x, y)


def paste_clip(canvas, im, x, y):
    cw, ch = canvas.size
    l, t = max(0, -x), max(0, -y)
    r, b = min(im.size[0], cw - x), min(im.size[1], ch - y)
    if r <= l or b <= t: return
    canvas.alpha_composite(im.crop((l, t, r, b)) if (l or t or r < im.size[0] or b < im.size[1]) else im,
                           (x + l, y + t))


# ---------------------------------------------------------------- backgrounds
@lru_cache(None)
def paper_bg(v):
    src = Image.open(os.path.join(AS, ["paper1.jpg", "paper3.jpg", "paper2.jpg"][v % 3])).convert("L")
    src = src.rotate(90, expand=True)
    sc = max(W / src.size[0], H / src.size[1]) * (1.0 + 0.15 * (v // 3))
    src = src.resize((int(src.size[0] * sc) + 1, int(src.size[1] * sc) + 1), Image.LANCZOS)
    src = src.crop((0, 0, W, H))
    g = np.asarray(src, np.float32)
    g = (g - g.mean()) * 0.55 + 205
    tint = np.array([1.0, 0.975, 0.93], np.float32)
    rgb = (g[..., None] * tint).clip(0, 255).astype(np.uint8)
    im = Image.fromarray(rgb).convert("RGBA")
    d = ImageDraw.Draw(im)
    rnd = random.Random(v)
    gx, gy = rnd.randint(80, 300), rnd.randint(300, 700)
    for i in range(-2, 9):
        d.line([(gx + i * 130, gy - 220), (gx + i * 130 + 6, gy + 760)], fill=(60, 60, 60, 70), width=2)
    for j in range(-2, 7):
        d.line([(gx - 300, gy + j * 130), (gx + 1100, gy + j * 130 - 8)], fill=(60, 60, 60, 70), width=2)
    return im


@lru_cache(None)
def blinds():
    im = Image.new("L", (W * 2, H * 2), 255)
    d = ImageDraw.Draw(im)
    for i in range(-10, 30):
        y = i * 170
        d.polygon([(0, y), (W * 2, y - 900), (W * 2, y - 830), (0, y + 70)], fill=150)
    return im.filter(ImageFilter.GaussianBlur(28))


def apply_blinds(canvas, t):
    b = blinds()
    ox = int(200 + 60 * math.sin(t * 0.35)); oy = int(400 + t * 9) % 340 + 300
    m = np.asarray(b.crop((ox, oy, ox + W, oy + H)), np.float32) / 255.0
    a = np.asarray(canvas, np.float32)
    a[..., :3] *= m[..., None]
    return Image.fromarray(a.astype(np.uint8), "RGBA")


@lru_cache(None)
def dark_bg(v):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    cx, cy = W * (0.5 + 0.15 * ((v % 3) - 1)), H * 0.42
    r = np.sqrt(((xx - cx) / W) ** 2 + ((yy - cy) / H * 0.6) ** 2)
    g = np.clip(1 - r * 1.6, 0, 1) ** 2
    base = np.array(BLACK, np.float32)
    glow = np.array([58, 30, 34] if v % 2 else [44, 42, 48], np.float32)
    rgb = base + g[..., None] * glow
    return Image.fromarray(rgb.clip(0, 255).astype(np.uint8)).convert("RGBA")


@lru_cache(None)
def red_bg():
    return textured(Image.new("RGBA", (W, H), RED + (255,)), 0.5, 3)


@lru_cache(None)
def grain(i):
    rng = np.random.default_rng(i)
    n = rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32)
    return np.asarray(Image.fromarray(((n * 40) + 128).clip(0, 255).astype(np.uint8)).resize((W, H), Image.BILINEAR),
                      np.float32) - 128


@lru_cache(None)
def vignette():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    return (1 - 0.38 * np.clip(r - 0.55, 0, 1) ** 1.5)[..., None]


@lru_cache(None)
def torn_overlay():
    """white torn-paper strips (internet texture) -> RGBA overlay, portrait"""
    t = Image.open(os.path.join(AS, "torn.jpg")).convert("L").rotate(90, expand=True)
    sc = W * 1.25 / t.size[0]
    t = t.resize((int(t.size[0] * sc), int(t.size[1] * sc)), Image.LANCZOS)
    a = t.point(lambda v: 255 if v > 110 else 0).filter(ImageFilter.GaussianBlur(1.2))
    rgb = ImageOps.colorize(t, (120, 115, 110), (250, 247, 240)).convert("RGBA")
    rgb.putalpha(a)
    return rgb


# ---------------------------------------------------------------- scribble
def scribble(canvas, cx, cy, rx, ry, prog, col=BLUE, width=9, seed=0, turns=1.18):
    if prog <= 0: return
    rnd = random.Random(seed)
    ph = rnd.uniform(0, 6.28)
    n = 90
    k = max(2, int(n * c01(prog)))
    pts = []
    for i in range(k):
        u = i / n
        a = ph + u * turns * 2 * math.pi
        rr = 1 + 0.06 * math.sin(u * 9 + ph) + 0.05 * u
        pts.append((cx + rx * rr * math.cos(a), cy + ry * rr * math.sin(a) * (1 - 0.08 * u)))
    ImageDraw.Draw(canvas).line(pts, fill=col + (235,), width=width, joint="curve")


# ================================================================ TIMELINE
# Lyrics were auto-transcribed (Punjabi, romanised). Edit text here if needed.
# (t0, t1, text, style dict)
T = []


def txt(t0, t1, s, **k): T.append(dict(t0=t0, t1=t1, s=s, **k))


# dark intro - tall condensed kinetic type (panda ref)
txt(0.00, 2.00, "JITTAN DE", f="anton", sz=120, x=300, y=300, col=WHITE, an="pop", st=1.3)
txt(1.36, 2.00, "SHAUNKI", f="anton", sz=330, x=540, y=620, col=WHITE, an="slam", st=1.45)
txt(2.00, 2.76, "SOHNIYE", f="anton", sz=300, x=540, y=1560, col=WHITE, an="slam", st=1.4)
txt(2.76, 4.30, "HARAUN", f="anton", sz=250, x=540, y=360, col=WHITE, an="pop", st=1.4)
txt(3.32, 4.30, "VAIRI", f="anton", sz=130, x=840, y=620, col=RED, an="pop", st=1.3)
txt(3.66, 4.30, "HASS KE", f="anton", sz=280, x=540, y=1600, col=WHITE, an="slam", st=1.4)
# title
txt(4.30, 5.62, "KARAN AUJLA", f="oswald", sz=70, x=540, y=560, col=WHITE, bg=BLACK, an="pop", rot=-3)
txt(4.42, 5.62, "ASHKE", f="anton", sz=380, x=540, y=980, col=RED, an="slam", st=1.15, stroke=6, scol=BLACK)
txt(4.67, 5.62, "AUJLA SZN 1", f="oswald", sz=60, x=640, y=1320, col=BLACK, bg=WHITE, an="pop", rot=4)
# paper collage verse (youmotion ref)
txt(5.62, 7.96, "YAARI", f="oswald", sz=170, x=330, y=330, col=WHITE, bg=BLACK, an="pop", rot=-4)
txt(6.18, 7.96, "AAPAN MOOHON", f="oswald", sz=92, x=600, y=1370, col=BLACK, bg=WHITE, an="pop", rot=2)
txt(6.90, 7.96, "MAIN KI DASS KE", f="oswald", sz=100, x=520, y=1530, col=WHITE, bg=RED, an="pop", rot=-2, scrib=1)
txt(7.96, 9.74, "BABE DI", f="oswald", sz=110, x=330, y=300, col=BLACK, bg=WHITE, an="pop", rot=-3)
txt(8.64, 9.74, "SAANU BAKHSHI", f="oswald", sz=112, x=560, y=1520, col=WHITE, bg=BLACK, an="pop", rot=2)
txt(9.74, 11.50, "KARDI AA GAANI", f="oswald", sz=100, x=540, y=300, col=WHITE, bg=BLACK, an="pop", rot=-2)
txt(10.86, 11.50, "LASHKE", f="anton", sz=300, x=560, y=1520, col=RED, an="slam", st=1.1, scrib=1)
txt(11.50, 12.72, "NI MODE", f="oswald", sz=150, x=380, y=330, col=WHITE, bg=RED, an="pop", rot=-3)
txt(11.88, 12.72, "PAUNDI", f="oswald", sz=130, x=640, y=1540, col=BLACK, bg=WHITE, an="pop", rot=3)
txt(12.72, 13.98, "CHUMM KE", f="anton", sz=230, x=540, y=360, col=BLACK, an="slam", st=1.1, bg=WHITE)
txt(13.56, 14.48, "DENDI AA", f="oswald", sz=100, x=540, y=1540, col=WHITE, bg=BLACK, an="pop", rot=-2)
txt(13.98, 14.48, "KEH KE", f="anton", sz=200, x=540, y=360, col=RED, an="slam", st=1.2)
txt(14.48, 15.18, "ASHKE", f="anton", sz=420, x=540, y=960, col=WHITE, an="slam", st=1.5, echo=3)
# drop
txt(15.18, 16.12, "MERA ZOR BADA", f="anton", sz=170, x=540, y=380, col=WHITE, an="pop", st=1.4)
txt(16.12, 16.94, "PUNJAB CHE", f="anton", sz=260, x=540, y=1560, col=RED, an="slam", st=1.5)
txt(16.94, 18.70, "NI JAADU", f="oswald", sz=150, x=380, y=330, col=WHITE, bg=BLACK, an="pop", rot=-4)
txt(17.60, 18.70, "SAADE HATH CHE", f="oswald", sz=112, x=560, y=1530, col=BLACK, bg=WHITE, an="pop", rot=2, scrib=1)
txt(18.70, 20.48, "TU JIGRA", f="anton", sz=240, x=540, y=400, col=WHITE, an="slam", st=1.5)
txt(19.46, 20.48, "DEKHI JATT DA", f="anton", sz=170, x=540, y=1580, col=RED, an="pop", st=1.4)
txt(20.48, 22.34, "KHAD JANDA", f="oswald", sz=130, x=420, y=330, col=WHITE, bg=RED, an="pop", rot=-3)
txt(21.26, 22.34, "KALLA", f="anton", sz=360, x=540, y=1520, col=RED, stroke=6, scol=BLACK, an="slam", st=1.2, scrib=1)
txt(22.34, 23.90, "MAIN CHALDA", f="anton", sz=200, x=540, y=400, col=WHITE, an="slam", st=1.45, stroke=7, scol=BLACK)
txt(23.90, 24.80, "RAMMING", f="anton", sz=280, x=540, y=1560, col=RED, an="slam", st=1.4, stroke=6, scol=BLACK)
txt(24.80, 25.86, "SAADE MATTHE CHE", f="oswald", sz=100, x=540, y=380, col=BLACK, bg=WHITE, an="pop", rot=-2)
txt(25.86, 27.10, "LATTA KOI KHICHDA", f="anton", sz=150, x=540, y=400, col=WHITE, an="pop", st=1.45)
txt(27.10, 27.86, "KHICH LE", f="anton", sz=300, x=540, y=1560, col=RED, an="slam", st=1.4)
txt(27.86, 29.68, "NI TRUSTY", f="oswald", sz=140, x=400, y=330, col=WHITE, bg=BLACK, an="pop", rot=-3)
txt(28.68, 29.68, "NEELI SHAAN CHE", f="oswald", sz=96, x=560, y=1540, col=BLACK, bg=WHITE, an="pop", rot=2)
txt(29.68, 30.54, "SAADE KAM KAALE", f="oswald", sz=110, x=540, y=1540, col=RED, bg=BLACK, an="pop", rot=-2, scrib=1)
# breakdown
txt(30.54, 33.20, "TERIYAN GALLAN", f="anton", sz=170, x=540, y=380, col=WHITE, an="pop", st=1.4)
txt(31.60, 33.20, "DIYAN LAALIYAN", f="anton", sz=170, x=540, y=1600, col=RED, an="pop", st=1.4)
txt(33.20, 36.80, "NI SUTTIYAN SI", f="oswald", sz=110, x=450, y=320, col=WHITE, bg=BLACK, an="pop", rot=-3)
txt(34.36, 36.80, "SOHNIYE", f="oswald", sz=170, x=560, y=1500, col=BLACK, bg=WHITE, an="pop", rot=2, echo=2)
txt(36.80, 38.26, "PIND DIYAN", f="anton", sz=230, x=540, y=380, col=WHITE, an="slam", st=1.4, stroke=7, scol=BLACK)
txt(37.26, 38.26, "YAARIYAN", f="anton", sz=280, x=540, y=1580, col=RED, an="slam", st=1.4, stroke=6, scol=BLACK)
txt(38.26, 39.30, "SAANU TAARIYAN", f="oswald", sz=110, x=540, y=330, col=WHITE, bg=RED, an="pop", rot=-2)
txt(39.30, 40.48, "PIND DIYAN YAARIYAN", f="oswald", sz=100, x=540, y=1550, col=BLACK, bg=WHITE, an="pop", rot=2, scrib=1)
# outro
txt(40.48, 44.06, "KARAN AUJLA", f="anton", sz=200, x=540, y=330, col=BLACK, an="pop", st=1.45)
txt(41.18, 44.06, "AUJLA SZN 1", f="oswald", sz=80, x=540, y=1450, col=BLACK, bg=WHITE, an="pop", rot=-2)
txt(41.63, 44.06, "PROD. MXRCI", f="oswald", sz=60, x=560, y=1580, col=WHITE, bg=RED, an="pop", rot=3)
txt(44.06, 45.10, "MAIN YAAR", f="anton", sz=260, x=540, y=700, col=WHITE, an="slam", st=1.45)
txt(44.30, 45.10, "YAARAN DA", f="anton", sz=260, x=540, y=1150, col=RED, an="slam", st=1.45)

# ---- scenes: (t0, t1, bg, layers)   layers: photo/shape/star dicts
S = []


def sc(t0, t1, bg, *layers, blinds_=None, ghost=False):
    S.append(dict(t0=t0, t1=t1, bg=bg, L=list(layers), blinds=(bg[0] == "p") if blinds_ is None else blinds_,
                  ghost=ghost))


def P(name, var="bw", x=540, y=1050, h=1250, rot=0, zoom=0.04, dx=0, stk=0, ent="pop", ghost=0, delay=0):
    return dict(k="p", name=name, var=var, x=x, y=y, h=h, rot=rot, zoom=zoom, dx=dx, stk=stk, ent=ent, ghost=ghost,
                delay=delay)


def SH(col, w, h, x, y, rot=0, seed=1, ent="pop", delay=0):
    return dict(k="s", col=col, w=w, h=h, x=x, y=y, rot=rot, seed=seed, ent=ent, delay=delay)


def ST(r, col, x, y, n=5, spin=40, delay=0):
    return dict(k="star", r=r, col=col, x=x, y=y, n=n, spin=spin, delay=delay, ent="pop")


# intro (dark)
sc(0.00, 2.00, "d0", P("k3", "dark", 540, 1180, 1500, zoom=0.05, ent="fade"))
sc(2.00, 2.76, "d1", P("w39", "dark", 560, 1150, 1500, zoom=0.06, ent="none"))
sc(2.76, 4.30, "d0", P("w37", "dark", 540, 1100, 1450, zoom=0.05, ent="none", ghost=1))
# title
sc(4.30, 5.62, "p0", SH(RED, 900, 1100, 560, 980, -3, 4), P("w2", "red", 540, 1000, 1150, rot=2, ent="pop", zoom=0.03),
   ST(70, BLACK, 880, 470, 8), ST(45, RED, 170, 1450, 5, -60))
# verse collage
sc(5.62, 7.96, "p1", SH(RED, 720, 980, 600, 1000, 4, 5), P("w10", "bw", 520, 1020, 1150, rot=-2, stk=18),
   ST(60, BLACK, 900, 1250, 5, 50, 0.3))
sc(7.96, 9.74, "p2", SH(BLACK, 760, 1000, 480, 960, -5, 6), P("w18", "bw", 560, 1000, 1150, rot=2, stk=18),
   ST(50, RED, 160, 640, 8, 50, 0.4))
sc(9.74, 11.50, "p0", SH(RED, 980, 900, 540, 900, 3, 7), P("w38", "bw", 540, 980, 1200, rot=-1, stk=18),
   ST(46, BLACK, 900, 520, 4, 90, 0.2), ST(36, BLACK, 180, 1200, 4, -90, 1.1))
sc(11.50, 12.72, "p1", SH(BLACK, 800, 1000, 520, 980, 4, 8), P("w14", "red", 540, 1000, 1150, rot=-2, stk=16))
for i, (t0, t1, nm, v, bg) in enumerate([(12.72, 13.22, "w32", "bw", "p2"), (13.22, 13.70, "w25", "red", "p0"),
                                         (13.70, 14.21, "w37", "bw", "p1"), (14.21, 14.48, "w2", "red", "p2")]):
    sc(t0, t1, bg, SH([RED, BLACK][i % 2], 820, 980, 540, 1000, [-4, 3][i % 2], 20 + i),
       P(nm, v, 540, 1000, 1150, rot=[2, -2][i % 2], stk=16, ent="none", zoom=0.12))
sc(14.48, 15.18, "red", P("w42", "red", 540, 1150, 1500, ent="none", zoom=0.25, ghost=1))
# drop: alternate dark / paper
sc(15.18, 16.94, "d1", P("w31", "dark", 540, 1100, 1500, zoom=0.06, ent="none"))
sc(16.94, 18.70, "p0", SH(RED, 900, 1000, 540, 960, -3, 9), P("w1", "bw", 540, 980, 1150, stk=18, rot=1),
   ST(60, BLACK, 880, 560, 8, 60, 0.3))
sc(18.70, 20.48, "d0", P("w37", "dark", 540, 1100, 1450, zoom=0.05, ent="none", ghost=1))
sc(20.48, 22.34, "p2", SH(BLACK, 760, 1080, 560, 980, 4, 10), P("w57", "red", 520, 1000, 1200, stk=18, rot=-2),
   ST(50, RED, 180, 1250, 5, 50, 0.6))
mont = ["w34", "w55", "w59", "w12", "w16", "w48", "w38", "w31"]
bt = [b for b in BEATS if 22.34 <= b < 25.86]
cuts = [22.34] + bt[1:] + [25.86]
for i in range(len(cuts) - 1):
    dark = i % 2 == 0
    nm = mont[i % len(mont)]
    if dark:
        sc(cuts[i], cuts[i + 1], "d%d" % (i % 2), P(nm, "dark", 540, 1100, 1450, zoom=0.15, ent="none"))
    else:
        sc(cuts[i], cuts[i + 1], "p%d" % (i % 3), SH(RED, 820, 980, 540, 980, [-3, 4][i % 2], 30 + i),
           P(nm, "bw", 540, 1000, 1150, stk=16, ent="none", zoom=0.15, rot=[2, -2][i % 2]))
sc(25.86, 27.86, "d1", P("w50", "dark", 540, 1080, 1350, zoom=0.07, ent="none", ghost=1))
sc(27.86, 30.54, "p1", SH(RED, 820, 1060, 520, 960, 3, 11), P("w25", "bw", 560, 980, 1180, stk=18, rot=-2),
   ST(54, BLACK, 870, 560, 5, 50, 0.4), ST(40, RED, 170, 1300, 8, -50, 1.4))
# breakdown
sc(30.54, 33.20, "d0", P("w2", "dark", 540, 1060, 1350, zoom=0.035, ent="fade"))
sc(33.20, 36.80, "p2", SH(BLACK, 700, 900, 400, 900, -6, 12), SH(RED, 600, 760, 690, 1000, 5, 13, delay=0.2),
   P("w10", "bw", 380, 960, 950, stk=16, rot=-4), P("w32", "red", 720, 1040, 950, stk=16, rot=4, delay=1.16),
   ST(46, RED, 900, 520, 8, 50, 0.5))
mont2 = [("w20", "dark", "d0"), ("w48", "bw", "p0"), ("w16", "red", "p1"), ("w34", "dark", "d1"), ("w59", "bw", "p2"),
         ("w55", "red", "p0"), ("w1", "dark", "d0"), ("w18", "bw", "p1")]
bt = [b for b in BEATS if 36.8 <= b < 40.48]
cuts = [36.80] + bt[1::1] + [40.48]
for i in range(len(cuts) - 1):
    nm, v, bg = mont2[i % len(mont2)]
    if bg[0] == "d":
        sc(cuts[i], cuts[i + 1], bg, P(nm, v, 540, 1100, 1400, zoom=0.15, ent="none"))
    else:
        sc(cuts[i], cuts[i + 1], bg, SH([RED, BLACK][i % 2], 820, 980, 540, 980, [-3, 4][i % 2], 40 + i),
           P(nm, v, 540, 1000, 1150, stk=16, ent="none", zoom=0.15, rot=[2, -2][i % 2]))
# outro
sc(40.48, 44.06, "p0", SH(RED, 960, 1080, 540, 950, -2, 14), P("w39", "bw", 540, 960, 1180, stk=18, zoom=0.03),
   ST(60, BLACK, 880, 1180, 8, 40, 0.7), ST(44, BLACK, 190, 640, 5, -40, 1.15))
sc(44.06, 45.10, "d0", P("k3", "dark", 540, 1300, 1300, zoom=0.05, ent="none"))

# ---- global FX
FLASH = [(4.30, 0.18), (14.48, 0.22), (15.18, 0.18), (16.12, 0.12), (21.26, 0.1), (27.10, 0.12), (30.54, 0.35),
         (36.80, 0.15), (40.48, 0.25), (44.06, 0.15)]
SHAKE = [(1.36, 0.25, 14), (4.42, 0.3, 18), (14.48, 0.5, 30), (15.18, 0.3, 18), (16.12, 0.35, 22), (18.70, 0.3, 16),
         (21.26, 0.3, 20), (23.90, 0.25, 16), (27.10, 0.35, 22), (36.80, 0.25, 16), (44.06, 0.3, 16)]
TORN = [4.30, 30.54 - 0.0, 40.48]
CUTS = sorted(set(round(s["t0"], 3) for s in S))


def punch_amt(t):
    if not (15.18 <= t < 30.5 or 36.8 <= t < 40.48 or 12.72 <= t < 15.18): return 0.0
    b = max([x for x in BEATS if x <= t], default=-9)
    return 0.045 * math.exp(-(t - b) / 0.11)


# ================================================================ RENDER
def ent_factor(ent, lt):
    if ent == "pop": return e_back(lt / 0.22), c01(lt / 0.08)
    if ent == "fade": return 1.0, c01(lt / 0.6)
    return 1.0, 1.0


def draw_scene(s, t):
    lt = t - s["t0"]
    bg = s["bg"]
    if bg == "red": cv = red_bg().copy()
    elif bg[0] == "p": cv = paper_bg(int(bg[1:])).copy()
    else: cv = dark_bg(int(bg[1:])).copy()
    for L in s["L"]:
        l2 = lt - L["delay"]
        if l2 < 0: continue
        sfac, afac = ent_factor(L["ent"], l2)
        if L["k"] == "s":
            im = torn_shape(L["w"], L["h"], L["col"], L["seed"])
            put(cv, im, L["x"], L["y"], 0.6 + 0.4 * sfac if L["ent"] == "pop" else 1, L["rot"], afac, shadow=8)
        elif L["k"] == "star":
            im = star(L["r"], L["n"], L["col"])
            put(cv, im, L["x"], L["y"], sfac, L["spin"] * l2, afac)
        else:
            dark = L["var"] == "dark"
            im = photo(L["name"], L["var"], L["h"], L["stk"])
            zs = 1 + L["zoom"] * lt
            s2 = (0.85 + 0.15 * sfac) if L["ent"] == "pop" else 1.0
            x = L["x"] + L["dx"] * lt
            if L["ghost"]:
                ga = 0.28 * c01((lt - 0.05) / 0.2)
                off = 150 * e_out(lt / 0.5)
                put(cv, im, x - off, L["y"] - 20, zs * 0.96, L["rot"], ga * afac)
                put(cv, im, x + off, L["y"] - 20, zs * 0.96, L["rot"], ga * afac)
            put(cv, im, x, L["y"], zs * s2, L["rot"], afac, shadow=0 if dark else 10)
            if dark:  # bottom fade into bg so cut-outs sit in the darkness
                pass
    if s["blinds"]:
        cv = apply_blinds(cv, t)
    if s["bg"][0] == "d":
        a = np.asarray(cv, np.float32)
        yy = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
        fade = np.clip((yy - 0.72) / 0.28, 0, 1) ** 1.4
        a[..., :3] = a[..., :3] * (1 - fade) + np.array(BLACK, np.float32) * fade
        cv = Image.fromarray(a.astype(np.uint8), "RGBA")
    return cv


def draw_text(cv, t):
    for it in T:
        if not (it["t0"] <= t < it["t1"]): continue
        lt = t - it["t0"]
        col = it["col"]
        if it.get("bg"):
            im = label(it["s"], it["f"], it["sz"], col, it["bg"], seed=hash(it["s"]) % 97,
                       stretch=it.get("st", 1.0))
        else:
            im = text_img(it["s"], it["f"], it["sz"], col, it.get("st", 1.0), 1000, it.get("stroke", 0),
                          it.get("scol"))
        an = it["an"]
        rot = it.get("rot", 0)
        if an == "slam":
            k = e_out(lt / 0.13); scale = 1.9 - 0.9 * k; a = c01(lt / 0.05)
        else:
            scale = e_back(lt / 0.2); a = c01(lt / 0.06)
            rot = rot + (1 - e_out(lt / 0.25)) * 8
        # exit
        rem = it["t1"] - t
        if rem < 0.07 and it["t1"] < DUR - 0.1:
            scale *= 1 + (0.07 - rem) * 3; a *= rem / 0.07
        if it.get("echo"):
            for e in range(it["echo"], 0, -1):
                de = c01((lt - 0.12 * e) / 0.15)
                if de > 0:
                    put(cv, im, it["x"], it["y"] + e * im.size[1] * 0.92 * de, scale * (1 - 0.08 * e), rot,
                        a * (0.55 - 0.13 * e) * de)
                    put(cv, im, it["x"], it["y"] - e * im.size[1] * 0.92 * de, scale * (1 - 0.08 * e), rot,
                        a * (0.55 - 0.13 * e) * de)
        put(cv, im, it["x"], it["y"], scale, rot, a, shadow=0 if not it.get("bg") else 6)
        if it.get("scrib"):
            p = e_out((lt - 0.12) / 0.35)
            scribble(cv, it["x"], it["y"], im.size[0] * 0.62 * scale, im.size[1] * 0.85 * scale, p,
                     seed=hash(it["s"]) % 31)


def frame(t):
    s = next((x for x in S if x["t0"] <= t < x["t1"]), S[-1])
    cv = draw_scene(s, t)
    draw_text(cv, t)
    # torn paper wipe transitions (internet texture)
    for tt in TORN:
        d = t - (tt - 0.18)
        if 0 <= d < 0.4:
            ov = torn_overlay()
            y = int(H - (H + ov.size[1]) * e_out(d / 0.4))
            put(cv, ov, W // 2, y + ov.size[1] // 2, 1.0, 0, 1.0)
    img = cv.convert("RGB")
    # camera: punch zoom + shake
    z = 1 + punch_amt(t)
    sx = sy = 0.0
    for t0, d, amp in SHAKE:
        if t0 <= t < t0 + d:
            k = amp * (1 - (t - t0) / d)
            r = random.Random(int(t * 1000))
            sx, sy = r.uniform(-k, k), r.uniform(-k, k)
            z = max(z, 1.03)
    if z > 1.001 or sx or sy:
        cw, ch = W / z, H / z
        x0, y0 = (W - cw) / 2 + sx, (H - ch) / 2 + sy
        img = img.transform((W, H), Image.EXTENT, (x0, y0, x0 + cw, y0 + ch), Image.BILINEAR)
    a = np.asarray(img, np.float32)
    # whip blur + rgb split right after cuts in fast sections
    near = [c for c in CUTS if 0 <= t - c < 2.5 / FPS]
    if near and (12.7 <= t < 30.6 or 36.7 <= t < 40.6 or t < 4.4):
        sh = 14
        a = (a + np.roll(a, sh, 1) + np.roll(a, -sh, 1) + np.roll(a, 2 * sh, 1)) / 4
        a[..., 0] = np.roll(a[..., 0], 10, 1); a[..., 2] = np.roll(a[..., 2], -10, 1)
    # flash
    for t0, d in FLASH:
        if t0 <= t < t0 + d:
            f = (1 - (t - t0) / d) ** 1.5 * 0.85
            a = a * (1 - f) + 255 * f
    # global fade in/out
    if t < 0.35: a *= t / 0.35
    if t > DUR - 0.4: a *= max(0, (DUR - t) / 0.4)
    a = a * vignette() + grain(int(t * FPS) % 6)[..., None] * 0.45
    return a.clip(0, 255).astype(np.uint8)


def main():
    args = sys.argv[1:]
    if "--frames" in args:
        ts = [float(x) for x in args[args.index("--frames") + 1].split(",")]
        out = args[0]
        tiles = [Image.fromarray(frame(t)).resize((270, 480)) for t in ts]
        cols = min(6, len(tiles)); rows = (len(tiles) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * 270, rows * 480))
        for i, tl in enumerate(tiles):
            ImageDraw.Draw(tl).text((6, 6), "%.2f" % ts[i], fill=(255, 255, 0))
            sheet.paste(tl, ((i % cols) * 270, (i // cols) * 480))
        sheet.save(out, quality=88)
        return
    out = args[0] if args else os.path.join(D, "ashke_reel.mp4")
    n = int(DUR * FPS)
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-i", AUDIO, "-map", "0:v", "-map", "1:a", "-c:v", "libx264",
                          "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k",
                          "-shortest", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    for i in range(n):
        p.stdin.write(frame(i / FPS).tobytes())
        if i % 150 == 0: print(f"{i}/{n}", flush=True)
    p.stdin.close(); p.wait()
    print("done", out)


if __name__ == "__main__":
    main()
