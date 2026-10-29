import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

D = sys.argv[1]
M = D + '/m/'
F = D + '/fonts/'
OUT = sys.argv[2]
GOLD = (222, 178, 96)
GOLD_BTN = (226, 186, 106)
WHITE = (255, 255, 255)
BODY = (238, 232, 222)
INK = (18, 15, 10)
serif = lambda s: ImageFont.truetype(F + 'DMSerifDisplay-Regular.ttf', s)
sans = lambda s: ImageFont.truetype(F + 'Poppins-SemiBold.ttf', s)
body = lambda s: ImageFont.truetype(F + 'FiraSans-Regular.ttf', s)
bold = lambda s: ImageFont.truetype(F + 'Poppins-Bold.ttf', s)

logo = Image.open(M + 'site/18.img').convert('RGBA')
logo = logo.crop(logo.getbbox())

# Copy is kept word for word from the approved ad preview.
ADS = [
    dict(slug='run-strong', bg='A4579vLezz8.jpg', bg_focus=(0.42, 0.42), bg_mirror=True,
         inset='knead.jpg', in_focus=(0.47, 0.42), in_zoom=1.15,
         head=[('RUN STRONG', WHITE), ('IN NYC.', GOLD)],
         sub=['Pre-Marathon', 'Sports Massage'],
         copy='Targeted bodywork to help you feel more mobile, reduce muscle tension and prepare for race day.',
         icons=[('tension', 'Reduce\nMuscle Tension'), ('mobility', 'Improve\nMobility'), ('ready', 'Feel\nRace-Ready')]),
    dict(slug='marathon-ready', bg='sK-nciHHnYA.jpg', bg_focus=(0.42, 0.40), bg_mirror=False,
         inset='forearm.jpg', in_focus=(0.46, 0.74), in_zoom=1.0,
         head=[('NYC', WHITE), ('MARATHON', WHITE), ('READY?', GOLD)],
         sub=['Pre-Race', 'Sports Massage'],
         copy='Personalized, one-on-one sessions to support your body, mobility and race preparation.',
         icons=None),
    dict(slug='race-prep', bg='1xx1hq2RJts.jpg', bg_focus=(0.66, 0.62), bg_mirror=False,
         inset='thumbs.jpg', in_focus=(0.84, 0.56), in_zoom=1.35,
         head=[('Your', WHITE), ('Race Prep', GOLD), ('Starts Here.', WHITE)],
         sub=['Pre-Marathon', 'Sports Massage'],
         copy='Bespoke treatments for runners to support flexibility, ease muscle tension and help you feel prepared for race day.',
         icons=None),
]


def grade(im):
    """Warm, low-key grade so every photo sits in the black-and-gold Mudras look."""
    a = np.asarray(im.convert('RGB')).astype(np.float32) / 255
    lum = a @ np.array([0.299, 0.587, 0.114], np.float32)
    a = a * 0.45 + lum[..., None] * 0.55                      # pull saturation down
    a = a * np.array([1.12, 0.97, 0.78], np.float32)          # golden warm
    a = np.clip(a, 0, 1) ** 1.2 * 0.95                         # deeper shadows
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


def photo(ad, W, H, target):
    im = Image.open(M + 'u/full/' + ad['photo']).convert('RGB')
    if ad['mirror']:
        im = ImageOps.mirror(im)
        ad = dict(ad, focus=(1 - ad['focus'][0], ad['focus'][1]))
    sc = max(W / im.width, H / im.height) * ad['zoom']
    im = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)
    fx, fy = ad['focus'][0] * im.width, ad['focus'][1] * im.height
    x0 = int(np.clip(fx - target[0], 0, im.width - W))
    y0 = int(np.clip(fy - target[1], 0, im.height - H))
    return grade(im.crop((x0, y0, x0 + W, y0 + H))).convert('RGBA')


def shade(img, left_end, top_band, bottom_band):
    W, H = img.size
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    left = np.clip(1 - xx / left_end, 0, 1) ** 0.9 * 238
    top = np.clip(1 - yy / top_band, 0, 1) ** 1.5 * 210
    bot = np.clip((yy - (H - bottom_band)) / bottom_band, 0, 1) ** 1.3 * 225
    vig = (np.hypot((xx - W * 0.7) / W, (yy - H * 0.5) / H) * 120)
    a = np.clip(np.maximum.reduce([left, top, bot]) + vig * 0.6, 0, 245)
    lay = Image.new('RGBA', (W, H), (8, 7, 5, 255))
    lay.putalpha(Image.fromarray(a.astype(np.uint8)))
    img.alpha_composite(lay)


def wrap(d, text, font, width):
    out, cur = [], ''
    for w in text.split():
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=font) > width and cur:
            out.append(cur); cur = w
        else:
            cur = t
    return out + [cur]


def icon(d, kind, cx, cy, r, col=GOLD):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=col, width=3)
    s = r * 0.5
    if kind == 'tension':  # tight zig-zag easing into a smooth line
        pts = [(cx - s, cy), (cx - s * 0.6, cy - s * 0.5), (cx - s * 0.2, cy + s * 0.5), (cx + s * 0.15, cy - s * 0.3),
               (cx + s * 0.4, cy + s * 0.1), (cx + s, cy + s * 0.1)]
        d.line(pts, fill=col, width=4, joint='curve')
    elif kind == 'mobility':  # circular arrows
        d.arc((cx - s, cy - s, cx + s, cy + s), 200, 340, fill=col, width=4)
        d.arc((cx - s, cy - s, cx + s, cy + s), 20, 160, fill=col, width=4)
        d.polygon([(cx + s * 0.95, cy - s * 0.55), (cx + s * 1.15, cy - s * 0.05), (cx + s * 0.55, cy - s * 0.2)], fill=col)
        d.polygon([(cx - s * 0.95, cy + s * 0.55), (cx - s * 1.15, cy + s * 0.05), (cx - s * 0.55, cy + s * 0.2)], fill=col)
    else:  # race-ready: check mark
        d.line((cx - s * 0.75, cy + s * 0.05, cx - s * 0.2, cy + s * 0.6, cx + s * 0.85, cy - s * 0.6), fill=col, width=5, joint='curve')


def pin(d, x, y, h, col=GOLD):
    r = h * 0.36
    d.ellipse((x - r, y, x + r, y + 2 * r), fill=col)
    d.polygon([(x - r * 0.86, y + r * 1.5), (x + r * 0.86, y + r * 1.5), (x, y + h)], fill=col)
    d.ellipse((x - r * 0.4, y + r * 0.6, x + r * 0.4, y + r * 1.4), fill=(8, 7, 5))


def cover(path, W, H, focus, target, mirror=False, zoom=1.0):
    im = Image.open(M + 'u/full/' + path).convert('RGB')
    if mirror:
        im = ImageOps.mirror(im)
        focus = (1 - focus[0], focus[1])
    sc = max(W / im.width, H / im.height) * zoom
    im = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)
    x0 = int(np.clip(focus[0] * im.width - target[0], 0, im.width - W))
    y0 = int(np.clip(focus[1] * im.height - target[1], 0, im.height - H))
    return grade(im.crop((x0, y0, x0 + W, y0 + H)))


def background(ad, W, H):
    img = cover(ad['bg'], W, H, ad['bg_focus'], (W * 0.68, H * 0.42), ad['bg_mirror']).convert('RGBA')
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    left = np.clip(1 - xx / (W * 0.80), 0, 1) ** 0.85 * 235
    top = np.clip(1 - yy / (H * 0.28), 0, 1) ** 1.4 * 170
    bot = np.clip((yy - H * 0.62) / (H * 0.38), 0, 1) ** 1.2 * 225
    a = np.clip(np.maximum.reduce([left, top, bot]), 0, 240)
    lay = Image.new('RGBA', (W, H), (9, 8, 6, 255))
    lay.putalpha(Image.fromarray(a.astype(np.uint8)))
    img.alpha_composite(lay)
    return img


def inset_card(img, ad, box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    ph = cover(ad['inset'], w, h, ad['in_focus'], (w / 2, h / 2), zoom=ad['in_zoom']).convert('RGBA')
    mask = Image.new('L', (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w - 1, h - 1), 26, fill=255)
    sh = Image.new('L', img.size, 0)
    ImageDraw.Draw(sh).rounded_rectangle((x0 + 4, y0 + 14, x1 + 4, y1 + 18), 30, fill=170)
    lay = Image.new('RGBA', img.size, (0, 0, 0, 255))
    lay.putalpha(sh.filter(ImageFilter.GaussianBlur(22)))
    img.alpha_composite(lay)
    ph.putalpha(mask)
    img.alpha_composite(ph, (x0, y0))
    ImageDraw.Draw(img).rounded_rectangle((x0, y0, x1, y1), 26, outline=GOLD, width=4)


def render(ad, W, H, story):
    pad = 80
    top0 = 240 if story else 58
    img = background(ad, W, H)
    if story:
        inset_card(img, ad, (W - 80 - 360, 1150, W - 80, 1580))
    else:
        inset_card(img, ad, (W - 64 - 360, 560, W - 64, 1010))
    d = ImageDraw.Draw(img)
    colw = int(W * 0.50)
    lw = 330
    lg = logo.resize((lw, int(logo.height * lw / logo.width)), Image.LANCZOS)
    img.alpha_composite(lg, (pad, top0))
    gap = 1.5 if story else 1.0
    y = top0 + lg.height + int(52 * gap)
    hs = 112 if len(ad['head']) == 2 else 104
    while max(d.textlength(t, font=serif(hs)) for t, _ in ad['head']) > W * 0.62:
        hs -= 2
    for t, c in ad['head']:
        d.text((pad - 4, y), t, font=serif(hs), fill=c)
        y += int(hs * 0.98)
    y += 20
    d.rounded_rectangle((pad, y, pad + 140, y + 5), 2, fill=GOLD)
    y += int(30 * gap)
    for t in ad['sub']:
        d.text((pad, y), t, font=serif(58), fill=WHITE)
        y += 60
    y += int(18 * gap)
    for ln in wrap(d, ad['copy'], body(33), colw):
        d.text((pad, y), ln, font=body(33), fill=BODY)
        y += 44
    if ad['icons']:
        y += int(26 * gap)
        cw = 172
        for i, (k, label) in enumerate(ad['icons']):
            cx = pad + 78 + i * cw
            icon(d, k, cx, y + 40, 38)
            for j, ln in enumerate(label.split('\n')):
                tw = d.textlength(ln, font=sans(22))
                d.text((cx - tw / 2, y + 90 + j * 27), ln, font=sans(22), fill=WHITE)
            if i < 2:
                d.line((cx + cw / 2, y + 4, cx + cw / 2, y + 140), fill=(120, 96, 56), width=2)
        y += 150
    by = H - (330 if story else 70) - 100
    btn = 'BOOK NOW'
    bf = bold(38)
    tw = d.textlength(btn, font=bf)
    bw = tw + 56 + 46 + 36
    d.rounded_rectangle((pad, by, pad + bw, by + 100), 50, fill=GOLD_BTN)
    d.text((pad + 46, by + 24), btn, font=bf, fill=INK)
    ax = pad + 46 + tw + 22
    d.line((ax, by + 50, ax + 30, by + 50), fill=INK, width=5)
    d.line((ax + 17, by + 37, ax + 31, by + 50, ax + 17, by + 63), fill=INK, width=5)
    ly = by - 124
    pin(d, pad + 16, ly + 2, 42)
    d.text((pad + 54, ly - 2), 'Chelsea  |  SoHo  |  Tribeca', font=sans(34), fill=GOLD)
    d.text((pad + 54, ly + 48), 'By Appointment Only', font=sans(26), fill=BODY)
    assert y < ly - 10, (ad['slug'], story, y, ly)
    name = f'mudras-{ad["slug"]}-{"story-1080x1920" if story else "feed-1080x1350"}'
    img.convert('RGB').save(OUT + f'/{name}.jpg', quality=93)
    return name, y, ly


for ad in ADS:
    print(render(ad, 1080, 1350, False))
    print(render(ad, 1080, 1920, True))
