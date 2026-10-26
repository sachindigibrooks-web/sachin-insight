import random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
from scipy import ndimage

D = sys.argv[1]  # scratchpad dir
P = D + '/prod/'
F = D + '/fonts/'
W, H = 1200, 675
NAVY = (9, 23, 68)
BLUE = (0, 136, 235)
TEAL = (10, 88, 112)
random.seed(7)


def cutout(path, thr=22):
    im = Image.open(path).convert('RGB')
    a = np.asarray(im).astype(np.float32)
    dark = (255 - a).max(axis=2)
    lab, _ = ndimage.label(dark < thr)
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bg = np.isin(lab, list(border))
    alpha = np.where(bg, np.clip((dark - 4) / (thr - 4), 0, 1), 1.0)
    alpha = ndimage.gaussian_filter(alpha, 0.7)
    out = np.dstack([a, alpha * 255]).astype(np.uint8)
    o = Image.fromarray(out, 'RGBA')
    return o.crop(o.getbbox())


def shadowed(base, obj, xy, blur=14, off=(0, 10), op=70):
    sh = Image.new('RGBA', obj.size, (9, 23, 68, 0))
    sh.putalpha(obj.getchannel('A').point(lambda v: v * op // 255))
    pad = blur * 3
    big = Image.new('RGBA', (obj.width + 2 * pad, obj.height + 2 * pad), (0, 0, 0, 0))
    big.paste(sh, (pad, pad))
    big = big.filter(ImageFilter.GaussianBlur(blur))
    base.alpha_composite(big, (xy[0] - pad + off[0], xy[1] - pad + off[1]))
    base.alpha_composite(obj, xy)


def reflect(base, obj, xy, op=0.22, h=0.35):
    r = obj.transpose(Image.FLIP_TOP_BOTTOM)
    rh = int(r.height * h)
    r = r.crop((0, 0, r.width, rh))
    g = np.linspace(op, 0, rh)[:, None]
    al = (np.asarray(r.getchannel('A')).astype(np.float32) * g).astype(np.uint8)
    r.putalpha(Image.fromarray(al))
    base.alpha_composite(r, (xy[0], xy[1] + obj.height + 2))


# ---------- background ----------
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
t = np.clip((xx / W * 0.6 + yy / H * 0.4), 0, 1)[..., None]
top = np.array([255, 255, 255], np.float32)
bot = np.array([232, 243, 252], np.float32)
bg = top * (1 - t) + bot * t
img = Image.fromarray(bg.astype(np.uint8)).convert('RGBA')

# soft swooshes
for (bbox, col, a, w) in [
    ((-500, 170, 1500, 1300), (200, 226, 248), 150, 70),
    ((-300, 280, 1700, 1500), (255, 255, 255), 230, 50),
    ((200, -700, 2100, 500), (210, 232, 250), 140, 90),
    ((350, -600, 2300, 630), (255, 255, 255), 220, 40),
]:
    m = Image.new('L', (W, H), 0)
    ImageDraw.Draw(m).arc(bbox, 0, 360, fill=a, width=w)
    lay = Image.new('RGBA', (W, H), col + (255,))
    lay.putalpha(m.filter(ImageFilter.GaussianBlur(18)))
    img.alpha_composite(lay)

# dot grid, top-left and bottom-right, fading
dots = Image.new('RGBA', (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(dots)
for x in range(12, 420, 18):
    for y in range(12, 260, 18):
        f = max(0, 1 - (x / 420 + y / 260))
        if f > 0:
            d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(150, 195, 235, int(110 * f)))
for x in range(W - 12, W - 330, -18):
    for y in range(H - 12, H - 200, -18):
        f = max(0, 1 - ((W - x) / 330 + (H - y) / 200))
        if f > 0:
            d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(150, 195, 235, int(110 * f)))
img.alpha_composite(dots)

# corner triangles
cor = Image.new('RGBA', (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(cor)
d.polygon([(0, H - 150), (0, H), (380, H)], fill=(1, 81, 154, 255))
d.polygon([(0, H - 95), (0, H), (210, H)], fill=(0, 136, 235, 255))
d.polygon([(W - 260, 0), (W, 0), (W, 150)], fill=(2, 135, 194, 255))
d.polygon([(W - 140, 0), (W, 0), (W, 80)], fill=(1, 81, 154, 255))

# ---------- products ----------
wand = cutout(P + 'mw1.jpg', int(sys.argv[3]) if len(sys.argv) > 3 else 60)
wand = wand.rotate(18, resample=Image.BICUBIC, expand=True)
wand = wand.crop(wand.getbbox())
ws = 560 / wand.width
wand = wand.resize((560, int(wand.height * ws)), Image.LANCZOS)
shadowed(img, wand, (W - 590, -10), blur=18, off=(0, 18), op=50)
img.alpha_composite(cor)  # corners sit above the wand so its cropped handle end is hidden

items = []
for f, h, mw in [('eu2.webp', 185, 999), ('dg3.webp', 160, 999), ('rt3.webp', 150, 250)]:
    o = cutout(P + f)
    sc = min(h / o.height, mw / o.width)
    o = o.resize((int(o.width * sc), int(o.height * sc)), Image.LANCZOS)
    items.append(o)
floor = 625
gap = 18
total = sum(o.width for o in items) + gap * (len(items) - 1)
x = W - 40 - total
for o in items:
    pos = (x, floor - o.height)
    reflect(img, o, pos)
    shadowed(img, o, pos, blur=10, off=(0, 8), op=60)
    x += o.width + gap

# ---------- logo ----------
logo = Image.open(P + 'logo.png').convert('RGBA')
lh = 46
logo = logo.resize((int(logo.width * lh / logo.height), lh), Image.LANCZOS)
lc = Image.new('RGBA', logo.size, TEAL + (255,))
lc.putalpha(logo.getchannel('A'))
img.alpha_composite(lc, (60, 52))

# ---------- headline ----------
d = ImageDraw.Draw(img)
fh = ImageFont.truetype(F + 'Poppins-ExtraBold.ttf', 74)
y = 128
for line in ['G Spot Wand', 'Attachments:']:
    d.text((56, y), line, font=fh, fill=NAVY)
    y += 86


def brush(w, h):
    b = Image.new('L', (w + 40, h + 20), 0)
    bd = ImageDraw.Draw(b)
    for yy_ in range(6, h + 14):
        x0 = 20 + random.randint(-14, 10)
        x1 = w + 20 + random.randint(-12, 14)
        bd.line((x0, yy_, x1, yy_), fill=random.randint(215, 255))
    for _ in range(22):  # dry-brush streaks at the ends
        yy_ = random.randint(8, h + 10)
        side = random.choice([0, 1])
        L = random.randint(10, 34)
        if side:
            bd.line((w + 20, yy_, w + 20 + L, yy_), fill=random.randint(120, 230), width=random.randint(1, 3))
        else:
            bd.line((20 - L, yy_, 20, yy_), fill=random.randint(120, 230), width=random.randint(1, 3))
    b = b.filter(ImageFilter.GaussianBlur(0.8))
    lay = Image.new('RGBA', b.size, BLUE + (255,))
    lay.putalpha(b)
    return lay


fs = ImageFont.truetype(F + 'Poppins-Bold.ttf', 46)
y += 16
for line in ['What They Are and', 'How to Use Them']:
    bb = d.textbbox((0, 0), line, font=fs)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    br = brush(tw + 36, th + 26)
    img.alpha_composite(br, (40, y - 14))
    d = ImageDraw.Draw(img)
    d.text((76 - bb[0], y + 13 - bb[1] + 4), line, font=fs, fill=(255, 255, 255))
    y += th + 34

out = sys.argv[2]
img.convert('RGB').save(out + '.png')
img.convert('RGB').save(out + '.webp', quality=90)
img.convert('RGB').save(out + '.jpg', quality=92)
