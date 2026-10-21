import json, subprocess, os, math, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1080, 1920, 30
PW, PH = 1188, 2112  # decode size (zoom headroom)
VO = "vo2" if os.path.exists(f"{S}/vo2/timeline.json") else "vo"
TL = json.load(open(f"{S}/{VO}/timeline.json"))
TOTAL = TL["total"] + 0.4
NF = int(TOTAL * FPS)
LINES = {l["id"]: l for l in TL["lines"]}
PREVIEW = "--preview" in sys.argv

def T(i): return LINES[i]["start"]
def Wd(i, word=None, idx=None):
    ws = LINES[i]["words"]
    if idx is not None: return ws[idx][0]
    for w in ws:
        if w[2].strip('".,—?').lower() == word.lower(): return w[0]
    raise KeyError((i, word))
def find_nth(i, word, n):
    c = 0
    for w in LINES[i]["words"]:
        if w[2].strip('".,—?').lower() == word.lower():
            if c == n: return w[0]
            c += 1
    raise KeyError((i, word, n))

F_ANTON = f"{S}/fonts/Anton.ttf"
F_TYPE = f"{S}/fonts/Special+Elite.ttf"
F_SERIF = f"{S}/fonts/Playfair+Display.ttf"
_fc = {}
def font(p, s):
    k = (p, s)
    if k not in _fc: _fc[k] = ImageFont.truetype(p, s)
    return _fc[k]

C = "/".join([S, "clips"])
MASTER = f"{S}/pd/master.mp4"
RED = (235, 30, 40); YEL = (255, 214, 0); WHITE = (255, 255, 255); INK = (34, 26, 20)

GRADES = {
    "color": "eq=contrast=1.08:saturation=0.85:brightness=-0.03,colorbalance=rs=0.04:bs=-0.04:rm=0.03:bh=-0.03",
    "cold": "eq=contrast=1.1:saturation=0.55:brightness=-0.05,colorbalance=bs=0.06:bm=0.03",
    "sepia": "eq=contrast=1.15:brightness=-0.02,colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131",
    "bw": "hue=s=0,eq=contrast=1.25:brightness=-0.04",
}

# ---------- shot list ----------
t_4 = Wd("L08", "4%")
t_mid7 = find_nth("L07", "sabse", 1)
SHOTS = [
    (0, T("L02"), "39854", 1.0, "color"),
    (T("L02"), T("L03"), "18299", 3.0, "color"),
    (T("L03"), T("L04"), "221", 4.0, "cold"),
    (T("L04"), T("L05"), "4761", 0.0, "color"),
    (T("L05"), T("L06"), "4519", 2.0, "color"),
    (T("L06"), T("L07"), "914", 3.0, "cold"),
    (T("L07"), t_mid7, "28897", 0.0, "cold"),
    (t_mid7, T("L08"), "42343", 5.0, "cold"),
    (T("L08"), t_4, "18263", 1.0, "color"),
    (t_4, T("L09"), "@black", 0, None),
    (T("L09"), T("Q1"), "@paper", 0, None),
    (T("Q1"), T("Q2"), "@master", 160.0, "sepia"),
    (T("Q2"), T("L10"), "@master", 344.0, "sepia"),
    (T("L10"), T("L11"), "4701", 2.0, "bw"),
    (T("L11"), Wd("L11", "FACTORY"), "3819", 2.0, "sepia"),
    (Wd("L11", "FACTORY"), T("L14"), "@master", 176.0, "sepia"),
    (T("L14"), Wd("L14", "SKILL"), "41287", 1.0, "color"),
    (Wd("L14", "SKILL"), Wd("L14", "NAAM"), "5339", 3.0, "color"),
    (Wd("L14", "NAAM"), T("L16"), "231", 4.0, "color"),
    (T("L16"), Wd("L16", "BOLA"), "49885", 2.0, "cold"),
    (Wd("L16", "BOLA"), T("L18"), "4832", 1.0, "cold"),
    (T("L18"), Wd("L18", "DOST"), "1623", 3.0, "cold"),
    (Wd("L18", "DOST"), TOTAL, "@black", 0, None),
]

# ---------- procedural backgrounds ----------
rng = np.random.default_rng(7)
def vignette(strength=0.75, color=(0, 0, 0)):
    y, x = np.mgrid[0:H, 0:W]
    d = np.sqrt(((x - W / 2) / (W * 0.62)) ** 2 + ((y - H / 2) / (H * 0.6)) ** 2)
    a = np.clip((d - 0.45) / 0.75, 0, 1) ** 1.6 * strength
    return a[..., None].astype(np.float32)
VIG = vignette(0.8)

def paper_bg():
    base = np.ones((H, W, 3), np.float32) * np.array([226, 208, 172], np.float32)
    n = rng.normal(0, 1, (H // 4, W // 4)).astype(np.float32)
    n = np.array(Image.fromarray(((n * 20) + 128).clip(0, 255).astype(np.uint8)).resize((W, H), Image.BICUBIC), np.float32) - 128
    fine = rng.normal(0, 7, (H, W)).astype(np.float32)
    base += (n * 0.7 + fine)[..., None]
    img = Image.fromarray(base.clip(0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img)
    for _ in range(14):  # coffee stains / fibres
        x, y, r = random.randint(0, W), random.randint(0, H), random.randint(60, 220)
        d.ellipse([x - r, y - r, x + r, y + r], outline=(150, 120, 80), width=random.randint(2, 5))
    img = img.filter(ImageFilter.GaussianBlur(0.8))
    a = np.array(img, np.float32)
    a = a * (1 - VIG * 0.9) + np.array([60, 40, 20]) * VIG * 0.9
    return a.clip(0, 255).astype(np.uint8)

def black_bg():
    a = np.ones((H, W, 3), np.float32) * 18
    n = np.array(Image.fromarray(((rng.normal(0, 1, (H // 6, W // 6)) * 25) + 128).clip(0, 255).astype(np.uint8)).resize((W, H), Image.BICUBIC), np.float32) - 128
    a += n[..., None] * 0.35
    y, x = np.mgrid[0:H, 0:W]
    glow = np.exp(-(((x - W / 2) / 600) ** 2 + ((y - H * 0.42) / 700) ** 2))
    a[..., 0] += glow * 70; a[..., 1] += glow * 8; a[..., 2] += glow * 10
    return a.clip(0, 255).astype(np.uint8)

random.seed(3)
PAPER = paper_bg(); BLACK = black_bg()
GRAIN = [rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32) for _ in range(6)]
GRAIN = [(np.array(Image.fromarray(((g * 40) + 128).clip(0, 255).astype(np.uint8)).resize((W, H), Image.NEAREST), np.int16) - 128)[..., None] for g in GRAIN]

# ---------- frame sources ----------
def decode(src, ss, dur, grade):
    path = MASTER if src == "@master" else f"{C}/{src}.mp4"
    vf = f"fps={FPS},scale={PW}:{PH}:force_original_aspect_ratio=increase,crop={PW}:{PH},{GRADES[grade]},format=rgb24"
    n = int(math.ceil(dur * FPS)) + 2
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-stream_loop", "-1", "-ss", str(ss), "-i", path, "-frames:v", str(n),
                          "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    fs = PW * PH * 3
    while True:
        b = p.stdout.read(fs)
        if len(b) < fs: break
        yield np.frombuffer(b, np.uint8).reshape(PH, PW, 3)
    p.wait()

def ease_out_back(x):
    c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2

# ---------- text helpers ----------
_tc = {}
def text_img(txt, fnt, size, fill, stroke=0, stroke_fill=(0, 0, 0), shadow=True, pad=40, spacing=0):
    k = (txt, fnt, size, fill, stroke, shadow)
    if k in _tc: return _tc[k]
    f = font(fnt, size)
    d0 = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    bb = d0.multiline_textbbox((0, 0), txt, font=f, stroke_width=stroke, align="center", spacing=spacing)
    w, h = int(bb[2] - bb[0] + pad * 2), int(bb[3] - bb[1] + pad * 2)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if shadow:
        sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(sh).multiline_text((pad - bb[0] + 6, pad - bb[1] + 10), txt, font=f, fill=(0, 0, 0, 190), stroke_width=stroke, stroke_fill=(0, 0, 0, 190), align="center", spacing=spacing)
        im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(9)))
    ImageDraw.Draw(im).multiline_text((pad - bb[0], pad - bb[1]), txt, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill, align="center", spacing=spacing)
    _tc[k] = im
    return im

def stamp_img(txt, size=150, color=RED, rot=-7):
    k = ("stamp", txt, size, color, rot)
    if k in _tc: return _tc[k]
    f = font(F_ANTON, size)
    bb = ImageDraw.Draw(Image.new("RGBA", (1, 1))).textbbox((0, 0), txt, font=f)
    tw, th = int(bb[2] - bb[0]), int(bb[3] - bb[1])
    w, h = tw + 110, th + 90
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([8, 8, w - 8, h - 8], 18, outline=color + (255,), width=12)
    d.text((55 - bb[0], 45 - bb[1]), txt, font=f, fill=color + (255,))
    a = np.array(im); m = rng.random(a.shape[:2]) < 0.12  # worn ink
    a[..., 3][m] = (a[..., 3][m] * 0.3).astype(np.uint8)
    im = Image.fromarray(a).rotate(rot, expand=True, resample=Image.BICUBIC)
    _tc[k] = im
    return im

def card_img(lines_done):
    k = ("card", lines_done)
    if k in _tc: return _tc[k]
    w, h = 760, 560
    im = Image.new("RGBA", (w + 60, h + 60), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle([40, 44, w + 40, h + 44], fill=(0, 0, 0, 160))
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(14)))
    p = Image.fromarray(PAPER[300:300 + h, 160:160 + w]).convert("RGBA")
    im.paste(p, (24, 24))
    d = ImageDraw.Draw(im)
    d.text((70, 60), "LIFE KA RULEBOOK", font=font(F_TYPE, 46), fill=INK)
    d.line([70, 125, w - 20, 125], fill=INK, width=3)
    items = ["Padhai karo", "Degree lo", "Job pakdo"]
    for i, it in enumerate(items):
        y = 170 + i * 120
        d.rectangle([70, y, 140, y + 70], outline=INK, width=5)
        d.text((175, y + 2), it, font=font(F_TYPE, 60), fill=INK)
        if i < lines_done:
            d.line([(80, y + 35), (102, y + 62), (155, y - 12)], fill=RED + (255,), width=13, joint="curve")
    im = im.rotate(-3, expand=True, resample=Image.BICUBIC)
    _tc[k] = im
    return im

def name_tag():
    k = ("tag",)
    if k in _tc: return _tc[k]
    w, h = 820, 330
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.polygon([(0, 30), (w, 0), (w - 10, h - 20), (12, h)], fill=(245, 236, 214, 255))
    d.text((60, 50), "SETH GODIN", font=font(F_SERIF, 110), fill=INK)
    d.text((66, 210), "Bestselling author · Marketing legend", font=font(F_TYPE, 38), fill=(120, 30, 30))
    im = im.rotate(4, expand=True, resample=Image.BICUBIC)
    _tc[k] = im
    return im

QUOTE = LINES["Q1"]["words"] + LINES["Q2"]["words"]
def quote_img(nwords, t):
    k = ("quote", nwords)
    if k in _tc: return _tc[k]
    w, h = 940, 1040
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    p = Image.fromarray(PAPER[150:150 + h, 70:70 + w]).convert("RGBA")
    mask = Image.new("L", (w, h), 0)
    md = ImageDraw.Draw(mask)
    pts = [(0, 18)] + [(x, random.Random(x).randint(0, 22)) for x in range(40, w, 40)] + [(w, 10), (w, h - 14)] + \
          [(x, h - random.Random(x + 9).randint(0, 22)) for x in range(w - 40, 0, -40)] + [(0, h)]
    md.polygon(pts, fill=255)
    im.paste(p, (0, 0), mask)
    d = ImageDraw.Draw(im)
    d.text((40, -40), "“", font=font(F_SERIF, 240), fill=(150, 30, 30))
    f = font(F_TYPE, 76)
    x, y = 60, 175
    for i, wd in enumerate(QUOTE[:nwords]):
        txt = wd[2].replace('"', '').replace('...', '').replace('…', '')
        if not txt: continue
        if txt == "told": txt = "told,"
        col = RED if txt.lower().startswith("deserve") else INK
        tw = d.textlength(txt + " ", font=f)
        if x + tw > w - 40: x = 60; y += 104
        d.text((x, y), txt, font=f, fill=col)
        x += tw
    if nwords >= len(QUOTE):
        d.text((w - 430, y + 125), "— Seth Godin", font=font(F_TYPE, 54), fill=(120, 30, 30))
    _tc[k] = im
    return im

# ---------- timed overlays ----------
# (t_in, t_out, kind, payload, (cx, cy), sfx)
O = []
def add(t0, t1, kind, payload, pos, anim="pop"):
    O.append(dict(t0=t0, t1=t1, kind=kind, p=payload, pos=pos, anim=anim))

def big(t0, t1, txt, size=170, color=WHITE, y=560, stroke=0):
    add(t0, t1, "img", lambda: text_img(txt, F_ANTON, size, color, stroke=stroke), (W // 2, y))

big(Wd("L01", "10-10"), T("L02"), "10 GHANTE\nROZ.", 190, WHITE, 520)
add(Wd("L02", "20"), T("L03"), "img", lambda: stamp_img("20 TAREEKH", 150), (W // 2, 470))
big(Wd("L02", "salary"), T("L03"), "SALARY = KHATAM", 110, YEL, 700)
big(Wd("L03", "TUMHARE"), T("L04"), "YE TUM HO.", 230, WHITE, 640)
for n, (a, b) in enumerate([(T("L04"), Wd("L04", "ki")), (Wd("L04", "ki"), Wd("L05", "li")), (Wd("L05", "li"), Wd("L06", "pakdi")), (Wd("L06", "pakdi"), T("L07"))]):
    add(a, b, "img", (lambda n=n: card_img(n)), (W // 2, 1000), anim="pop" if n == 0 else "none")
big(T("L07") + 0.2, T("L08"), "SABSE PEHLE AAO", 120, WHITE, 470)
big(t_mid7, T("L08"), "SABSE LAST JAAO", 120, YEL, 640)
big(Wd("L08", "appraisal"), t_4, "APPRAISAL...", 150, WHITE, 560)
big(t_4, T("L09"), "4%", 560, RED, 760)
big(t_4 + 0.35, T("L09"), "BAS ITNA HI?", 90, WHITE, 1130)
add(T("L09") + 0.1, T("Q1"), "img", name_tag, (W // 2, 760))
add(T("Q1"), T("L10"), "quote", None, (W // 2, 880), anim="none")
big(Wd("L10", "MEHNAT"), T("L11"), "GALTI MEHNAT\nKI NAHI HAI", 140, WHITE, 560)
add(Wd("L11", "RULEBOOK"), Wd("L11", "FACTORY"), "img", lambda: stamp_img("RULEBOOK", 170, RED, 6), (W // 2, 560))
add(Wd("L11", "FACTORY"), T("L14"), "img", lambda: stamp_img("FACTORY ERA · 1936", 110, (245, 236, 214), -5), (W // 2, 420))
big(find_nth("L11", "jo", 1), T("L14"), "\"JO BOLA JAAYE,\nWO KARO.\"", 130, YEL, 700)
big(Wd("L14", "SKILL"), T("L16"), "SKILL.", 170, WHITE, 380)
big(Wd("L14", "NAAM"), T("L16"), "NAAM.", 170, WHITE, 580)
big(Wd("L14", "OWN"), T("L16"), "OWN IT.", 200, YEL, 800)
big(Wd("L16", "CHUNA"), T("L18"), "MAINE CHUNA?", 140, WHITE, 470)
big(Wd("L16", "BOLA"), T("L18"), "YA BOLA GAYA?", 150, RED, 680)
big(Wd("L18", "DOST"), TOTAL, "US DOST KO\nSEND KARO", 170, WHITE, 640)
big(Wd("L18", "DOST") + 0.6, TOTAL, "jo kehta hai: \"bas ek promotion aur\"", 52, YEL, 960)
big(LINES["L18"]["end"] + 0.1, TOTAL, "FOLLOW  for more", 70, RED, 1650)

# ---------- captions ----------
CAPS = []
for l in TL["lines"]:
    if l["id"] in ("Q1", "Q2"): continue
    ws = [w for w in l["words"] if w[2].strip() not in ("—", "-")]; chunk = []
    for i, w in enumerate(ws):
        chunk.append(w)
        if len(chunk) == 3 or w[2][-1] in ".,—?" or i == len(ws) - 1:
            CAPS.append(chunk); chunk = []
cap_spans = []
for i, ch in enumerate(CAPS):
    t0 = ch[0][0]
    t1 = min(CAPS[i + 1][0][0], ch[-1][1] + 0.4) if i + 1 < len(CAPS) else ch[-1][1] + 0.5
    cap_spans.append((t0, t1, ch))

def caption_img(ch, cur):
    k = ("cap", tuple(w[2] for w in ch), cur)
    if k in _tc: return _tc[k]
    f = font(F_ANTON, 92)
    parts = []
    for j, w in enumerate(ch):
        raw = w[2].strip('"')
        emph = raw.strip(".,—?").isupper() and len(raw.strip(".,—?")) > 1
        col = YEL if j == cur else (RED if emph else WHITE)
        parts.append((raw.upper(), col))
    d0 = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    sp = 26
    widths = [d0.textlength(p, font=f) for p, _ in parts]
    tw = sum(widths) + sp * (len(parts) - 1)
    scale = min(1, 980 / tw)
    if scale < 1:
        f = font(F_ANTON, int(92 * scale)); widths = [d0.textlength(p, font=f) for p, _ in parts]; tw = sum(widths) + sp * (len(parts) - 1)
    im = Image.new("RGBA", (int(tw) + 60, 170), (0, 0, 0, 0))
    d = ImageDraw.Draw(im); x = 30
    for (p, col), wdt in zip(parts, widths):
        d.text((x, 20), p, font=f, fill=col, stroke_width=7, stroke_fill=(0, 0, 0))
        x += wdt + sp
    _tc[k] = im
    return im

def paste(canvas, im, cx, cy, scale=1.0, alpha=1.0):
    if scale != 1.0:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BILINEAR)
    if alpha < 1.0:
        a = im.getchannel("A").point(lambda v: int(v * alpha)); im = im.copy(); im.putalpha(a)
    canvas.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))

# ---------- main render ----------
out = f"{S}/out/video_noaudio.mp4"
os.makedirs(f"{S}/out", exist_ok=True)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                        "-c:v", "libx264", "-preset", "medium" if not PREVIEW else "ultrafast", "-crf", "19", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
fi = 0
for si, (a, b, src, ss, grade) in enumerate(SHOTS):
    f0, f1 = int(round(a * FPS)), int(round(b * FPS))
    if si == len(SHOTS) - 1: f1 = NF
    n = f1 - f0
    if n <= 0: continue
    gen = None if src.startswith("@") and src != "@master" else decode(src, ss, n / FPS, grade)
    for k in range(n):
        t = (f0 + k) / FPS
        prog = k / max(1, n - 1)
        punch = max(0, 1 - k / 6) * 0.07
        if gen is not None:
            try: fr = next(gen)
            except StopIteration: pass
            z = 1.0 + punch + 0.06 * (1 - prog)  # slow push-in + cut punch
            cw = min(PW, int(W * 1.1 / z)); ch_ = min(PH, int(H * 1.1 / z))
            x0 = (PW - cw) // 2; y0 = (PH - ch_) // 2
            img = Image.fromarray(fr[y0:y0 + ch_, x0:x0 + cw]).resize((W, H), Image.BILINEAR)
            base = np.asarray(img).astype(np.int16)
            if src == "@master": base = base + (GRAIN[(fi + 3) % 6] // 2)
        else:
            bg = BLACK if src == "@black" else PAPER
            if punch > 0:
                z = 1 + punch; img = Image.fromarray(bg).resize((int(W * z), int(H * z)), Image.BILINEAR)
                ox, oy = (img.width - W) // 2, (img.height - H) // 2
                base = np.asarray(img)[oy:oy + H, ox:ox + W].astype(np.int16)
            else:
                base = bg.astype(np.int16)
        # vignette + grain
        base = (base * (1 - VIG * 0.85)).astype(np.int16) + GRAIN[fi % 6] // 5
        canvas = Image.fromarray(base.clip(0, 255).astype(np.uint8)).convert("RGBA")
        # overlays
        for o in O:
            if not (o["t0"] <= t < o["t1"]): continue
            age = t - o["t0"]
            if o["kind"] == "quote":
                nw = sum(1 for w in QUOTE if w[0] <= t)
                im = quote_img(nw, t)
                sc = 0.92 + 0.08 * ease_out_back(min(1, age / 0.25)); paste(canvas, im, o["pos"][0], o["pos"][1], sc)
                continue
            im = o["p"]()
            if o["anim"] == "pop":
                x = min(1, age / 0.22); sc = 1.6 - 0.6 * ease_out_back(x) if x < 1 else 1.0
                sc = max(0.5, sc); al = min(1, age / 0.08)
                jx = random.randint(-6, 6) if age < 0.15 else 0
                paste(canvas, im, o["pos"][0] + jx, o["pos"][1], sc, al)
            else:
                paste(canvas, im, *o["pos"])
        # captions
        for (c0, c1, ch) in cap_spans:
            if c0 <= t < c1:
                cur = max([j for j, w in enumerate(ch) if w[0] <= t] or [0])
                im = caption_img(ch, cur)
                age = t - c0; sc = 1.0 + max(0, 0.12 * (1 - age / 0.12))
                paste(canvas, im, W // 2, 1420, sc)
                break
        enc.stdin.write(canvas.convert("RGB").tobytes())
        fi += 1
    if gen is not None: gen.close()
    print(f"shot {si} {src} done ({fi}/{NF})", flush=True)
enc.stdin.close(); enc.wait()

# ---------- sound design ----------
sfx = []
for (a, b, src, ss, g) in SHOTS[1:]:
    sfx.append(("s1492", a - 0.12, -17))
for t, s, v in [(Wd("L03", "TUMHARE"), "s1143", -8), (t_4, "s788", -7), (Wd("L16", "BOLA"), "s1143", -10),
                (Wd("L18", "DOST"), "s788", -12), (T("L09") - 0.9, "s790", -14), (Wd("L11", "RULEBOOK"), "s498", -9)]:
    sfx.append((s, t, v))
for w in QUOTE: sfx.append(("s1365", w[0], -14))
sfx.append(("s1059", T("L07"), -16))
json.dump({"total": TOTAL, "sfx": sfx}, open(f"{S}/out/sfx.json", "w"))
print("done")
