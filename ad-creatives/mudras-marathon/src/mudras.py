"""Rebuild the three approved Mudras ad designs 1:1, swapping only the photos.

Every position and text size is measured from the original 642x809 previews and scaled to 1080x1350.
"""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

D = sys.argv[1]
M = D + '/m/'
F = D + '/fonts/'
OUT = sys.argv[2]
W, H = 1080, 1350
K = 1350 / 809         # scale from the reference previews
OX = (W - 642 * K) / 2
OY = 0
GOLD = (228, 184, 104)
GOLD_LINE = (214, 170, 92)
WHITE = (255, 255, 255)
BODY = (240, 236, 228)
DARK = (24, 18, 10)


def X(v):
    return int(OX + v * K)


def Y(v):
    return int(OY + v * K)


def S_(v):
    return int(v * K)


def vf(path, size, weight):
    f = ImageFont.truetype(F + path, size)
    f.set_variation_by_axes([weight])
    return f


serif = lambda s, w=700: vf('PlayfairDisplay.ttf', s, w)
sans = lambda s, w=400: vf('Montserrat.ttf', s, w)

logo = Image.open(M + 'site/18.img').convert('RGBA')
logo = logo.crop(logo.getbbox())
ICONS = {n: Image.open(M + f'icons/{n}.png').convert('RGBA') for n in ('run', 'arm-flex-outline', 'spa-outline')}


def fit(text, maker, target_w, start):
    s = start
    d = ImageDraw.Draw(Image.new('L', (8, 8)))
    while d.textlength(text, font=maker(s)) > target_w and s > 10:
        s -= 1
    while d.textlength(text, font=maker(s + 1)) <= target_w:
        s += 1
    return s


# Original copy, line breaks and positions (reference px). Only the photos are new.
ADS = [
    dict(slug='run-strong', photo='knead.jpg', crop=None, focus=(0.42, 0.40), target=(0.74, 0.56), zoom=1.05,
         logo=(55, 35, 255),
         head=[('RUN STRONG', WHITE, 168, 418), ('IN NYC.', GOLD, 232, 280)],
         rule=307,
         sub=[('Pre-Marathon', 323, 247), ('Sports Massage', 360, 268)],
         body=(412, 25, ['Targeted bodywork to help', 'you feel more mobile, reduce', 'muscle tension and prepare', 'for race day.']),
         icons=dict(cy=557, xs=[118, 252, 376], div=[188, 315], label_y=595,
                    items=[('run', 'Reduce', 'Muscle Tension'), ('arm-flex-outline', 'Improve', 'Mobility'), ('spa-outline', 'Feel', 'Race-Ready')]),
         loc=(62, 655, 683), btn=(58, 717, 313, 773)),
    dict(slug='marathon-ready', photo='forearm.jpg', crop=None, mirror=True, focus=(0.56, 0.72), target=(0.74, 0.62), zoom=1.35,
         logo=(55, 38, 245),
         head=[('NYC', WHITE, 148, 153), ('MARATHON', WHITE, 215, 336), ('READY?', GOLD, 278, 308)],
         rule=361,
         sub=[('Pre-Race', 385, 160), ('Sports Massage', 423, 275)],
         body=(480, 26, ['Personalized, one-on-one', 'sessions to support your', 'body, mobility and race', 'preparation.']),
         icons=None, loc=(64, 636, 663), btn=(60, 705, 322, 763)),
    dict(slug='race-prep', photo='physio.jpg', crop=(560, 620, 2400, 1600), mirror=False, focus=(0.36, 0.30), target=(0.76, 0.42), zoom=1.35, lift=0.8,
         logo=(55, 40, 240),
         head=[('Your', WHITE, 170, 150), ('Race Prep', GOLD, 235, 325), ('Starts Here.', WHITE, 300, 358)],
         rule=378,
         sub=[('Pre-Marathon', 400, 240), ('Sports Massage', 440, 265)],
         body=(493, 26, ['Bespoke treatments for runners', 'to support flexibility, ease muscle', 'tension and help you feel prepared', 'for race day.']),
         icons=None, loc=(66, 630, 657), btn=(60, 692, 338, 750)),
]


def grade(im):
    """Warm, rich grade similar to the original golden-hour imagery."""
    a = np.asarray(im.convert('RGB')).astype(np.float32) / 255
    lum = a @ np.array([0.299, 0.587, 0.114], np.float32)
    a = a * 0.75 + lum[..., None] * 0.25
    a = a * np.array([1.08, 0.97, 0.84], np.float32)
    a = np.clip((a - 0.5) * 1.12 + 0.5, 0, 1) ** 1.12
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


def photo(ad):
    im = Image.open(M + 'u/full/' + ad['photo']).convert('RGB')
    if ad['crop']:
        im = im.crop(ad['crop'])  # drop everything above the shoulders so no face is shown
    if ad.get('mirror'):
        im = ImageOps.mirror(im)  # subject on the right, as in the originals
    sc = max(W / im.width, H / im.height) * ad['zoom']
    im = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)
    x0 = int(np.clip(ad['focus'][0] * im.width - ad['target'][0] * W, 0, im.width - W))
    y0 = int(np.clip(ad['focus'][1] * im.height - ad['target'][1] * H, 0, im.height - H))
    img = grade(im.crop((x0, y0, x0 + W, y0 + H)))
    if ad.get('lift'):
        img = Image.fromarray(np.clip(np.asarray(img).astype(np.float32) * ad['lift'], 0, 255).astype(np.uint8))
    img = img.convert('RGBA')
    # left-side darkening like the originals: near black behind the copy, photo fully visible on the right
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    left = np.clip(1 - xx / (W * 0.80), 0, 1) ** 0.95 * 246
    top = np.clip(1 - yy / (H * 0.20), 0, 1) ** 1.6 * 120
    bot = np.clip((yy - H * 0.80) / (H * 0.20), 0, 1) ** 1.6 * 130
    a = np.clip(np.maximum.reduce([left, top, bot]), 0, 242)
    lay = Image.new('RGBA', (W, H), (8, 6, 4, 255))
    lay.putalpha(Image.fromarray(a.astype(np.uint8)))
    img.alpha_composite(lay)
    return img


def gold_rule(img, x0, x1, y):
    w = x1 - x0
    g = np.clip(1.15 - np.linspace(0, 1, w), 0, 1)
    strip = Image.new('RGBA', (w, 4), GOLD_LINE + (255,))
    strip.putalpha(Image.fromarray((np.repeat(g[None, :], 4, 0) * 255).astype(np.uint8)))
    img.alpha_composite(strip, (x0, y))


def pin(d, x, y, h):
    r = h * 0.34
    d.ellipse((x - r, y, x + r, y + 2 * r), fill=GOLD)
    d.polygon([(x - r * 0.88, y + r * 1.45), (x + r * 0.88, y + r * 1.45), (x, y + h)], fill=GOLD)
    d.ellipse((x - r * 0.42, y + r * 0.58, x + r * 0.42, y + r * 1.42), fill=(10, 8, 5))


def button(img, box):
    x0, y0, x1, y1 = [X(box[0]), Y(box[1]), X(box[2]), Y(box[3])]
    w, h = x1 - x0, y1 - y0
    gx = np.linspace(0, 1, w)[None, :]
    gy = np.linspace(0, 1, h)[:, None]
    t = np.clip(gx * 0.7 + gy * 0.3, 0, 1)[..., None]
    c0, c1 = np.array([242, 206, 138]), np.array([214, 166, 86])
    grad = (c0 * (1 - t) + c1 * t).astype(np.uint8)
    b = Image.fromarray(grad, 'RGB').convert('RGBA')
    m = Image.new('L', (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), h // 2, fill=255)
    b.putalpha(m)
    img.alpha_composite(b, (x0, y0))
    d = ImageDraw.Draw(img)
    f = sans(S_(21.5), 600)
    text = 'BOOK NOW'
    sp = 2.2
    tw = sum(d.textlength(c, font=f) + sp for c in text) - sp
    arrow = S_(24)
    total = tw + S_(14) + arrow
    tx = x0 + (w - total) / 2
    ty = y0 + (h - f.size) / 2 - S_(2.5)
    for c in text:
        d.text((tx, ty), c, font=f, fill=DARK)
        tx += d.textlength(c, font=f) + sp
    ax = tx + S_(14) - sp
    cy = y0 + h / 2
    d.line((ax, cy, ax + arrow, cy), fill=DARK, width=4)
    d.line((ax + arrow - S_(8), cy - S_(8), ax + arrow + 1, cy, ax + arrow - S_(8), cy + S_(8)), fill=DARK, width=4)


def render(ad):
    img = photo(ad)
    d = ImageDraw.Draw(img)
    lx, ly, lw = ad['logo']
    lg = logo.resize((X(lx + lw) - X(lx), int(logo.height * (X(lx + lw) - X(lx)) / logo.width)), Image.LANCZOS)
    img.alpha_composite(lg, (X(lx), Y(ly)))
    ImageDraw.Draw(img).text((X(lx) + lg.width + 6, Y(ly) - 4), '\u00ae', font=sans(S_(15), 500), fill=GOLD)
    for text, col, top, width in ad['head']:
        s = fit(text, serif, width * K, 60)
        f = serif(s)
        bb = d.textbbox((0, 0), text, font=f)
        d.text((X(58) - bb[0], Y(top) - bb[1]), text, font=f, fill=col)
    gold_rule(img, X(60), X(207), Y(ad['rule']))
    d = ImageDraw.Draw(img)
    for text, top, width in ad['sub']:
        s = fit(text, lambda z: serif(z, 600), width * K, 40)
        f = serif(s, 600)
        bb = d.textbbox((0, 0), text, font=f)
        d.text((X(60) - bb[0], Y(top) - bb[1]), text, font=f, fill=WHITE)
    top, lh, lines = ad['body']
    bf = sans(S_(18.6), 400)
    for i, ln in enumerate(lines):
        bb = d.textbbox((0, 0), 'Tg', font=bf)
        d.text((X(60), Y(top + i * lh) - bb[1]), ln, font=bf, fill=BODY)
    if ad['icons']:
        ic = ad['icons']
        r = S_(30)
        for (name, l1, l2), cx in zip(ic['items'], ic['xs']):
            cx, cy = X(cx), Y(ic['cy'])
            d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=GOLD, width=3)
            g = ICONS[name].resize((int(r * 1.15), int(r * 1.15)), Image.LANCZOS)
            img.alpha_composite(g, (cx - g.width // 2, cy - g.height // 2))
            d = ImageDraw.Draw(img)
            lf = sans(S_(13.6), 500)
            for j, t in enumerate((l1, l2)):
                tw = d.textlength(t, font=lf)
                d.text((cx - tw / 2, Y(ic['label_y'] + j * 17)), t, font=lf, fill=WHITE)
        for dx in ic['div']:
            d.line((X(dx), Y(ic['cy'] - 25), X(dx), Y(ic['cy'] + 70)), fill=(150, 120, 70), width=2)
    px, ty1, ty2 = ad['loc']
    pin(d, X(px + 8), Y(ty1 - 5), S_(28))
    lf = sans(S_(19.5), 500)
    x = X(px + 35)
    parts = ['Chelsea', 'SoHo', 'Tribeca']
    for i, p in enumerate(parts):
        d.text((x, Y(ty1) - 4), p, font=lf, fill=GOLD)
        x += d.textlength(p, font=lf)
        if i < 2:
            x += S_(9)
            d.line((x, Y(ty1) + 2, x, Y(ty1) + S_(19)), fill=GOLD, width=2)
            x += S_(11)
    d.text((X(px + 36), Y(ty2) - 2), 'By Appointment Only', font=sans(S_(14.8), 400), fill=BODY)
    button(img, ad['btn'])
    return img


def run(ad, story):
    global H, OY
    H = 1920 if story else 1350
    OY = (1920 - 1350) // 2 if story else 0
    img = render(ad)
    name = f'mudras-{ad["slug"]}-{"story-1080x1920" if story else "feed-1080x1350"}'
    img.convert('RGB').save(OUT + f'/{name}.jpg', quality=93)


for ad in ADS:
    run(ad, False)
    run(ad, True)
    print('ok', ad['slug'])
