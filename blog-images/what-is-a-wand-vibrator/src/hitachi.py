import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy import ndimage

D = sys.argv[1]
P = D + '/h/prod/'
F = D + '/fonts/'
OUT = sys.argv[2]
W, H = 1200, 675
NAVY = (8, 28, 60)
KICK = (12, 72, 128)
LINE = (128, 192, 228)
SKY = (211, 229, 249)
PINK = (237, 215, 218)
ACCENT = (50, 164, 220)  # site light blue #32a4dc
GREY = (74, 88, 112)
fB = lambda s: ImageFont.truetype(F + 'Poppins-Bold.ttf', s)
fX = lambda s: ImageFont.truetype(F + 'Poppins-ExtraBold.ttf', s)
fS = lambda s: ImageFont.truetype(F + 'Poppins-SemiBold.ttf', s)

WANDS = [  # file, name, power, speeds, rpm, price, relative height
    ('Magic-Wand-Original-HV-260-UK-01.jpg', 'Original HV260', 'Corded', '2', '6,000', '£125.95', 1.0),
    ('Magic-Wand-Plus-HV-265-UK-01.jpg', 'Plus HV265', 'Removable cord', '4', '6,300', '£129.95', 1.0),
    ('Magic-Wand-Rechargeable-HV-270-UK-10.jpg', 'Rechargeable HV270', 'Cordless', '4', '6,300', '£159.95', 1.0),
    ('Magic-Wand-Waterproof-HV-360-UK-01.jpg', 'Waterproof HV360', 'Cordless, submersible', '4', '7,000', '£208.00', 1.0),
    ('Magic-Wand-Rechargeable-Mini-HV-135-UK-01.jpg', 'Mini', 'Cordless, compact', '3', '6,000', '£94.95', 0.68),
    ('Magic-Wand-Micro-HV-60-UK-01.jpg', 'Micro HV60', 'Pocket sized', '3', '6,500', '£64.95', 0.46),
]


def cutout(path, thr=14, trim=10):
    im = Image.open(path).convert('RGB')
    im = im.crop((trim, trim, im.width - trim, im.height - trim))  # drop grey edge lines on some photos
    a = np.asarray(im).astype(np.float32)
    dark = (255 - a).max(axis=2)
    # solid silhouette: product edges, closed and hole-filled, so white bodies stay opaque
    m = ndimage.binary_closing(dark > thr, iterations=4)
    m = ndimage.binary_fill_holes(m)
    lab, n = ndimage.label(m)
    sizes = ndimage.sum(m, lab, range(1, n + 1))
    m = np.isin(lab, [i + 1 for i, v in enumerate(sizes) if v > sizes.max() * 0.02])
    m = ndimage.binary_erosion(m, iterations=1)
    alpha = ndimage.gaussian_filter(m.astype(np.float32), 0.9)
    o = Image.fromarray(np.dstack([a, alpha * 255]).astype(np.uint8), 'RGBA')
    return o.crop(o.getbbox())


def fit(o, h=None, w=None):
    sc = min(h / o.height if h else 9e9, w / o.width if w else 9e9)
    return o.resize((max(1, int(o.width * sc)), max(1, int(o.height * sc))), Image.LANCZOS)


def drop(base, obj, xy, blur=12, off=(6, 10), op=55):
    pad = blur * 3
    m = Image.new('L', (obj.width + 2 * pad, obj.height + 2 * pad), 0)
    m.paste(obj.getchannel('A').point(lambda v: v * op // 255), (pad, pad))
    lay = Image.new('RGBA', m.size, NAVY + (255,))
    lay.putalpha(m.filter(ImageFilter.GaussianBlur(blur)))
    base.alpha_composite(lay, (xy[0] - pad + off[0], xy[1] - pad + off[1]))
    base.alpha_composite(obj, xy)


def contact(base, cx, y, w, op=70):
    m = Image.new('L', (W, H), 0)
    ImageDraw.Draw(m).ellipse((cx - w / 2, y - 7, cx + w / 2, y + 7), fill=op)
    lay = Image.new('RGBA', (W, H), NAVY + (255,))
    lay.putalpha(m.filter(ImageFilter.GaussianBlur(6)))
    base.alpha_composite(lay)


def blob(base, draw_fn, col, blur=2):
    m = Image.new('L', (W, H), 0)
    draw_fn(ImageDraw.Draw(m))
    lay = Image.new('RGBA', (W, H), col + (255,))
    lay.putalpha(m.filter(ImageFilter.GaussianBlur(blur)))
    base.alpha_composite(lay)


def background():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    t = np.clip(yy / H * 0.7 + xx / W * 0.3, 0, 1)[..., None]
    bg = np.array([253, 253, 254], np.float32) * (1 - t) + np.array([240, 244, 250], np.float32) * t
    img = Image.fromarray(bg.astype(np.uint8)).convert('RGBA')
    # pastel blue wave top and bottom-left, blush arch right (matches existing post artwork)
    blob(img, lambda d: d.ellipse((380, -520, 1500, 150), fill=255), SKY, 3)
    blob(img, lambda d: d.ellipse((330, -560, 1450, 110), fill=255), (253, 253, 254), 3)
    blob(img, lambda d: d.ellipse((-420, 470, 760, 1100), fill=255), SKY, 3)
    blob(img, lambda d: d.ellipse((-380, 505, 820, 1160), fill=210), (247, 250, 253), 3)
    blob(img, lambda d: d.ellipse((800, 40, 1500, 900), fill=255), PINK, 3)
    blob(img, lambda d: d.ellipse((850, 520, 1600, 1000), fill=255), (234, 208, 211), 3)
    return img


# ---------- featured ----------
img = background()
# pedestal floor
blob(img, lambda d: d.ellipse((560, 545, 1230, 660), fill=255), (250, 251, 253), 2)
blob(img, lambda d: d.ellipse((560, 545, 1230, 660), outline=255, width=2), (226, 232, 242), 1)
tall = 440
items = [fit(cutout(P + f), h=int(tall * r)) for f, *_, r in WANDS]
gap = 10
x = 1195 - sum(o.width for o in items) - gap * 5
floor = 600
for o in items:
    contact(img, x + o.width / 2, floor, o.width * 1.1)
    drop(img, o, (int(x), floor - o.height), blur=10, off=(8, 6), op=40)
    x += o.width + gap

d = ImageDraw.Draw(img)
k = 'What Is a Wand Vibrator?'
d.text((70, 150), k, font=fS(36), fill=KICK)
kw = d.textlength(k, font=fS(36))
d.rounded_rectangle((72, 207, 72 + kw, 211), 2, fill=LINE)
y = 236
for line in ['How It Works', 'and What It Does']:
    d.text((66, y), line, font=fX(60), fill=NAVY)
    y += 78
d.text((70, y + 22), 'Six Magic Wand models compared', font=fS(22), fill=GREY)
img.convert('RGB').save(OUT + '/what-is-a-wand-vibrator-featured.webp', quality=90)
img.convert('RGB').save(OUT + '/what-is-a-wand-vibrator-featured.jpg', quality=92)
img.convert('RGB').save(OUT + '/what-is-a-wand-vibrator-featured.png')


# ---------- in-article: model comparison ----------
def card(im, box, r=20, fill=(255, 255, 255)):
    x0, y0, x1, y1 = box
    m = Image.new('L', im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((x0, y0 + 8, x1, y1 + 8), r, fill=45)
    lay = Image.new('RGBA', im.size, NAVY + (255,))
    lay.putalpha(m.filter(ImageFilter.GaussianBlur(14)))
    im.alpha_composite(lay)
    ImageDraw.Draw(im).rounded_rectangle(box, r, fill=fill + (255,), outline=(220, 232, 246), width=2)


def centered(d, cx, y, text, font, fill):
    d.text((cx - d.textlength(text, font=font) / 2, y), text, font=font, fill=fill)


def title(im, text):
    d = ImageDraw.Draw(im)
    centered(d, W / 2, 28, text, fX(38), NAVY)
    d.rounded_rectangle((W / 2 - 50, 84, W / 2 + 50, 89), 3, fill=LINE)


im = background()
title(im, 'Which Magic Wand Model Should You Choose?')
cw, gap = 176, 14
x0 = (W - (6 * cw + 5 * gap)) // 2
for i, (f, name, power, speeds, rpm, price, r) in enumerate(WANDS):
    x = x0 + i * (cw + gap)
    card(im, (x, 112, x + cw, 648))
    o = fit(items[i], h=int(220 * r))
    cx = x + cw // 2
    contact(im, cx, 348, o.width * 1.1, 50)
    im.alpha_composite(o, (cx - o.width // 2, 348 - o.height))
    d = ImageDraw.Draw(im)
    nm = name.split(' ')
    centered(d, cx, 364, 'Magic Wand', fS(15), GREY)
    centered(d, cx, 383, ' '.join(n for n in nm if not n.startswith('HV')), fX(21), NAVY)
    hv = [n for n in nm if n.startswith('HV')]
    centered(d, cx, 411, hv[0] if hv else 'HV135', fS(14), KICK)
    ry = 446
    for lab, val in [('Power', power), ('Speeds', speeds), ('Up to RPM', rpm)]:
        d.line((x + 16, ry - 6, x + cw - 16, ry - 6), fill=(228, 236, 246), width=2)
        centered(d, cx, ry, lab, fS(13), GREY)
        vf = fB(15) if len(val) < 16 else fB(13)
        centered(d, cx, ry + 19, val, vf, NAVY)
        ry += 50
    pw = d.textlength(price, font=fB(19))
    d.rounded_rectangle((cx - pw / 2 - 16, 598, cx + pw / 2 + 16, 632), 17, fill=KICK)
    centered(d, cx, 602, price, fB(19), (255, 255, 255))
im.convert('RGB').save(OUT + '/magic-wand-models-compared.webp', quality=90)
im.convert('RGB').save(OUT + '/magic-wand-models-compared.png')

# ---------- in-article: how it works (parts diagram) ----------
im = background()
title(im, 'How Does a Wand Vibrator Work?')
w = cutout(P + 'Magic-Wand-Rechargeable-HV-270-UK-10.jpg')
w = w.rotate(90, resample=Image.BICUBIC, expand=True)  # head on the left so the printed text reads correctly
w = fit(w, w=640)
wx, wy = 280, 268
contact(im, wx + w.width / 2, wy + w.height + 18, w.width * 0.95, 45)
drop(im, w, (wx, wy), blur=12, off=(0, 14), op=35)
d = ImageDraw.Draw(im)
bx = lambda frac: wx + int(w.width * frac)
CW, CH = 290, 106
labels = [  # anchor on wand, card top-left, title, body
    ((bx(0.62), wy + 10), (bx(0.62) - 150, 112), 'Speed settings', 'Choose a comfortable level, from gentle to strong.'),
    ((bx(0.12), wy + 8), (bx(0.12) - 160, 112), 'The head', 'Rounded shape covers more area than a small bullet vibrator.'),
    ((bx(0.86), wy + w.height - 8), (bx(0.86) - 150, 468), 'The handle', 'Long reach for shoulders, back and thighs without twisting your wrist.'),
    ((bx(0.30), wy + w.height // 2), (bx(0.30) - 150, 468), 'The motor', 'Creates the vibrations. Many models use a rotating weight for a steady rumble.'),
]
for (ax, ay), (lx, ly), t, body in labels:
    ey = ly + CH if ly < wy else ly
    d.line((ax, ay, ax, ey), fill=KICK, width=2)
    card(im, (lx, ly, lx + CW, ly + CH), r=14)
    d = ImageDraw.Draw(im)
    d.ellipse((ax - 7, ay - 7, ax + 7, ay + 7), fill=ACCENT, outline=(255, 255, 255), width=3)
    d.text((lx + 18, ly + 12), t, font=fX(20), fill=NAVY)
    words, lines, cur = body.split(), [], ''
    for wd in words:
        if d.textlength((cur + ' ' + wd).strip(), font=fS(14)) > CW - 36:
            lines.append(cur); cur = wd
        else:
            cur = (cur + ' ' + wd).strip()
    lines.append(cur)
    for j, ln in enumerate(lines):
        d.text((lx + 18, ly + 44 + j * 19), ln, font=fS(14), fill=GREY)
note = 'RPM alone does not tell you how strong it will feel: motor design, head shape and speed all matter.'
nw = d.textlength(note, font=fS(15))
d.rounded_rectangle((W / 2 - nw / 2 - 20, 604, W / 2 + nw / 2 + 20, 646), 21, fill=(255, 255, 255), outline=LINE, width=2)
d.text((W / 2 - nw / 2, 613), note, font=fS(15), fill=KICK)
im.convert('RGB').save(OUT + '/how-a-wand-vibrator-works.webp', quality=90)
im.convert('RGB').save(OUT + '/how-a-wand-vibrator-works.png')
