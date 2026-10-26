import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy import ndimage

D = sys.argv[1]
V = D + '/v/'
F = D + '/fonts/'
OUT = sys.argv[2]
W, H = 1200, 675
INK = (36, 40, 48)
RED = (187, 7, 14)
DEEP = (137, 8, 13)
BLUSH = (246, 211, 210)
PALE = (253, 236, 239)
BG = (241, 240, 236)
GREY = (92, 96, 106)
fB = lambda s: ImageFont.truetype(F + 'Poppins-Bold.ttf', s)
fX = lambda s: ImageFont.truetype(F + 'Poppins-ExtraBold.ttf', s)
fS = lambda s: ImageFont.truetype(F + 'Poppins-SemiBold.ttf', s)


def cutout(path, thr=14, trim=4):
    im = Image.open(path).convert('RGB')
    im = im.crop((trim, trim, im.width - trim, im.height - trim))
    a = np.asarray(im).astype(np.float32)
    dark = (255 - a).max(axis=2)
    m = ndimage.binary_closing(dark > thr, iterations=4)
    m = ndimage.binary_fill_holes(m)
    lab, n = ndimage.label(m)
    sizes = ndimage.sum(m, lab, range(1, n + 1))
    m = np.isin(lab, [i + 1 for i, v in enumerate(sizes) if v > sizes.max() * 0.02])
    alpha = ndimage.gaussian_filter(m.astype(np.float32), 0.8)
    o = Image.fromarray(np.dstack([a, alpha * 255]).astype(np.uint8), 'RGBA')
    return o.crop(o.getbbox())


def fit(o, h=None, w=None):
    sc = min(h / o.height if h else 9e9, w / o.width if w else 9e9)
    return o.resize((int(o.width * sc), int(o.height * sc)), Image.LANCZOS)


def soft(base, shape_fn, col, op=255, blur=0):
    m = Image.new('L', base.size, 0)
    shape_fn(ImageDraw.Draw(m), op)
    if blur:
        m = m.filter(ImageFilter.GaussianBlur(blur))
    lay = Image.new('RGBA', base.size, col + (255,))
    lay.putalpha(m)
    base.alpha_composite(lay)


def heartbeat(d, x0, x1, y, col=(176, 176, 172)):
    pts, x = [], x0
    mid = (x0 + x1) // 2
    for px in [x0, mid - 60, mid - 48, mid - 38, mid - 26, mid - 14, mid, x1]:
        pts.append(px)
    ys = [0, 0, 14, -34, 22, -8, 0, 0]
    d.line([(p, y + dy) for p, dy in zip(pts, ys)], fill=col, width=2, joint='curve')


def icon(d, kind, cx, cy, r=14):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=RED, width=3)
    if kind == 'check':
        d.line((cx - 6, cy, cx - 1, cy + 5, cx + 7, cy - 5), fill=RED, width=3, joint='curve')
    elif kind == 'plus':
        d.line((cx - 6, cy, cx + 6, cy), fill=RED, width=3)
        d.line((cx, cy - 6, cx, cy + 6), fill=RED, width=3)
    elif kind == 'heart':
        d.ellipse((cx - 7, cy - 6, cx, cy + 1), fill=RED)
        d.ellipse((cx, cy - 6, cx + 7, cy + 1), fill=RED)
        d.polygon([(cx - 7, cy - 1), (cx + 7, cy - 1), (cx, cy + 7)], fill=RED)


def chip(im, x, y, kind, text):
    d = ImageDraw.Draw(im)
    tw = d.textlength(text, font=fS(16))
    w = int(tw + 68)
    soft(im, lambda dd, op: dd.rounded_rectangle((x, y + 4, x + w, y + 48), 12, fill=op), INK, 40, 6)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((x, y, x + w, y + 44), 12, fill=(255, 255, 255), outline=(230, 226, 222), width=1)
    icon(d, kind, x + 24, y + 22, 12)
    d.text((x + 46, y + 10), text, font=fS(16), fill=INK)
    return w


# ---------- featured ----------
img = Image.new('RGBA', (W, H), BG + (255,))
ph = Image.open(V + 'ph/couple.jpg').convert('RGB')
pw = 1420
ph = ph.resize((pw, int(ph.height * pw / ph.width)), Image.LANCZOS)
img.paste(ph, (W - pw + 200, (H - ph.height) // 2))
# warm wash over the photo so it sits in the brand palette, then fade to solid on the left
xx = np.arange(W, dtype=np.float32)
fade = np.clip((xx - 470) / 230, 0, 1)
alpha = ((1 - fade) * 255).astype(np.uint8)[None, :].repeat(H, 0)
ov = Image.new('RGBA', (W, H), BG + (255,))
ov.putalpha(Image.fromarray(alpha))
img.alpha_composite(ov)
wash = Image.new('RGBA', (W, H), (255, 250, 246, 40))
img.alpha_composite(wash)

d = ImageDraw.Draw(img)
k = "MEN'S HEALTH GUIDE"
kf = fB(15)
kw = d.textlength(k, font=kf) + 6 * len(k) * 0.12
d.rounded_rectangle((56, 108, 56 + kw + 60, 144), 18, fill=BLUSH, outline=(232, 170, 170), width=1)
d.ellipse((74, 120, 86, 132), fill=RED)
x = 98
for ch in k:  # letter-spaced label
    d.text((x, 115), ch, font=kf, fill=DEEP)
    x += d.textlength(ch, font=kf) + 1.6
y = 170
for line in ['How Do You Make', 'a Man Hard?']:
    d.text((54, y), line, font=fX(56), fill=INK)
    y += 70
d.text((58, y + 10), 'What Really Helps (UK Guide)', font=fS(26), fill=INK)
y += 76
x = 56
for kind, t in [('heart', 'Arousal first'), ('check', 'Daily habits'), ('plus', 'When to see a GP')]:
    x += chip(img, x, y, kind, t) + 12
d = ImageDraw.Draw(img)
heartbeat(d, 0, 600, 500)

box = fit(cutout(V + 'prod/vp1.jpg'), w=250)
bx, by = W - box.width - 40, H - box.height - 46
soft(img, lambda dd, op: dd.rounded_rectangle((bx - 30, by + box.height - 6, W + 20, H + 40), 10, fill=op), (255, 255, 255), 235, 1)
soft(img, lambda dd, op: dd.ellipse((bx - 10, by + box.height - 14, bx + box.width + 14, by + box.height + 10), fill=op), INK, 70, 8)
img.alpha_composite(box, (bx, by))
img.convert('RGB').save(OUT + '/how-do-you-make-a-man-hard-featured.webp', quality=90)
img.convert('RGB').save(OUT + '/how-do-you-make-a-man-hard-featured.jpg', quality=92)
img.convert('RGB').save(OUT + '/how-do-you-make-a-man-hard-featured.png')


# ---------- shared bits for in-article graphics ----------
def canvas(title, sub):
    im = Image.new('RGBA', (W, H), BG + (255,))
    soft(im, lambda dd, op: dd.ellipse((850, -260, 1500, 330), fill=op), PALE, 255, 2)
    soft(im, lambda dd, op: dd.ellipse((-250, 470, 330, 1000), fill=op), PALE, 255, 2)
    d = ImageDraw.Draw(im)
    tw = d.textlength(title, font=fX(36))
    d.text(((W - tw) / 2, 34), title, font=fX(36), fill=INK)
    sw = d.textlength(sub, font=fS(17))
    d.text(((W - sw) / 2, 88), sub, font=fS(17), fill=GREY)
    d.rounded_rectangle((W / 2 - 40, 122, W / 2 + 40, 126), 2, fill=RED)
    return im


def card(im, box, r=16):
    x0, y0, x1, y1 = box
    soft(im, lambda dd, op: dd.rounded_rectangle((x0, y0 + 6, x1, y1 + 8), r, fill=op), INK, 34, 10)
    ImageDraw.Draw(im).rounded_rectangle(box, r, fill=(255, 255, 255), outline=(232, 228, 224), width=1)


def wrap(d, text, font, width):
    out, cur = [], ''
    for w in text.split():
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=font) > width:
            out.append(cur); cur = w
        else:
            cur = t
    return out + [cur]


def num(d, cx, cy, n, r=20):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=RED)
    t = str(n)
    tw = d.textlength(t, font=fX(19))
    d.text((cx - tw / 2, cy - 14), t, font=fX(19), fill=(255, 255, 255))


# ---------- in-article 1: how an erection works ----------
im = canvas('How an Erection Actually Works', 'Arousal sends the signal, then blood flow does the rest')
steps = [
    ('Arousal', 'Something turns you on and the brain sends the signal.'),
    ('Nitric oxide', 'Nerve endings in the penis release nitric oxide.'),
    ('Muscle relaxes', 'The smooth muscle there relaxes.'),
    ('Vessels widen', 'Blood vessels open up to let more blood in.'),
    ('Firm erection', 'More blood flows in than out, so the penis firms up.'),
]
cw, gap = 196, 30
x0 = (W - (5 * cw + 4 * gap)) // 2
d = ImageDraw.Draw(im)
for i, (t, body) in enumerate(steps):
    x = x0 + i * (cw + gap)
    card(im, (x, 170, x + cw, 440))
    d = ImageDraw.Draw(im)
    num(d, x + cw // 2, 222, i + 1, 26)
    tw = d.textlength(t, font=fX(21))
    d.text((x + (cw - tw) / 2, 268), t, font=fX(21), fill=INK)
    for j, ln in enumerate(wrap(d, body, fS(16), cw - 34)):
        lw = d.textlength(ln, font=fS(16))
        d.text((x + (cw - lw) / 2, 314 + j * 25), ln, font=fS(16), fill=GREY)
    if i < 4:
        ax = x + cw + 4
        d.polygon([(ax + 4, 295), (ax + gap - 6, 305), (ax + 4, 315)], fill=RED)
card(im, (x0, 478, W - x0, 610))
d = ImageDraw.Draw(im)
d.rounded_rectangle((x0, 478, x0 + 8, 610), 4, fill=RED)
d.text((x0 + 32, 498), 'Why there is no single switch', font=fX(22), fill=INK)
msg = 'Mood, nerves, hormones and circulation all have to play along. If one drops out, the whole thing can stall.'
for j, ln in enumerate(wrap(d, msg, fS(18), W - 2 * x0 - 64)):
    d.text((x0 + 32, 540 + j * 28), ln, font=fS(18), fill=GREY)
im.convert('RGB').save(OUT + '/how-an-erection-works.webp', quality=90)
im.convert('RGB').save(OUT + '/how-an-erection-works.png')

# ---------- in-article 2: NHS habits ----------
im = canvas('Everyday Habits That Support Erections', 'Lifestyle changes the NHS says can sometimes help with erectile dysfunction')
habits = [
    ('Lose weight', "if you're overweight"),
    ('Stop smoking', ''),
    ('Eat a healthy diet', ''),
    ('Exercise daily', ''),
    ('Reduce stress', 'and anxiety'),
    ('Limit alcohol', 'no more than 14 units a week'),
    ('Pause long rides', 'if you cycle more than 3 hours a week'),
]
colw, rowh = 520, 86
lx, rx = 70, 70 + colw + 40
for i, (t, s) in enumerate(habits):
    col, row = (0, i) if i < 4 else (1, i - 4)
    x = lx if col == 0 else rx
    y = 158 + row * (rowh + 14)
    card(im, (x, y, x + colw, y + rowh), 14)
    d = ImageDraw.Draw(im)
    num(d, x + 44, y + rowh // 2, i + 1)
    if s:
        d.text((x + 82, y + 14), t, font=fX(21), fill=INK)
        d.text((x + 82, y + 48), s, font=fS(15), fill=GREY)
    else:
        d.text((x + 82, y + rowh // 2 - 17), t, font=fX(21), fill=INK)
y = 158 + 3 * (rowh + 14)
card(im, (rx, y, rx + colw, y + rowh), 14)
d = ImageDraw.Draw(im)
d.rounded_rectangle((rx, y, rx + 8, y + rowh), 4, fill=RED)
d.text((rx + 30, y + 14), 'Problems keep happening?', font=fX(20), fill=RED)
d.text((rx + 30, y + 48), 'See a GP or visit a sexual health clinic.', font=fS(15), fill=GREY)
foot = 'Not glamorous, but these habits look after the circulation erections depend on.'
fw = d.textlength(foot, font=fS(17))
d.text(((W - fw) / 2, 588), foot, font=fS(17), fill=INK)
im.convert('RGB').save(OUT + '/habits-that-support-erections.webp', quality=90)
im.convert('RGB').save(OUT + '/habits-that-support-erections.png')
