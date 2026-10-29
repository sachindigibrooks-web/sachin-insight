import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

D = sys.argv[1]
M = D + '/m/'
F = D + '/fonts/'
OUT = sys.argv[2]
GOLD = (212, 168, 83)      # sampled from the Mudras logo (#c89848 .. #e0b860)
GOLD_HI = (232, 192, 108)
WHITE = (255, 255, 255)
SOFT = (226, 220, 208)
serif = lambda s: ImageFont.truetype(F + 'DMSerifDisplay-Regular.ttf', s)
sans = lambda s: ImageFont.truetype(F + 'Poppins-SemiBold.ttf', s)
bold = lambda s: ImageFont.truetype(F + 'Poppins-Bold.ttf', s)

logo = Image.open(M + 'site/18.img').convert('RGBA')
logo = logo.crop(logo.getbbox())

# (source file, focus point as fractions of the source, headline lines with gold flag, service line)
ADS = [
    ('0.img', (0.74, 0.47), [('RUN STRONG', False), ('IN NYC.', True)], 'Pre-Marathon Sports Massage', 'run-strong'),
    ('6.img', (0.52, 0.66), [('NYC MARATHON', False), ('READY?', True)], 'Pre-Race Sports Massage', 'marathon-ready'),
    ('14.img', (0.62, 0.36), [('YOUR RACE PREP', False), ('STARTS HERE.', True)], 'Pre-Marathon Sports Massage', 'race-prep'),
]


def warm(im):
    """Gentle warm duotone on the black-and-white session photos so they sit with the gold."""
    g = np.asarray(im.convert('L')).astype(np.float32) / 255
    g = np.clip((g - 0.04) * 1.12, 0, 1) ** 0.95
    lo = np.array([10, 9, 7], np.float32)
    hi = np.array([246, 236, 218], np.float32)
    return Image.fromarray((lo + (hi - lo) * g[..., None]).astype(np.uint8))


def band(img, src, focus, y0, y1, fade=130):
    W = img.width
    im = warm(Image.open(M + 'site/' + src))
    bh = y1 - y0
    cw = im.width
    ch = int(cw * bh / W)
    if ch > im.height:  # portrait-ish band: crop width instead
        ch = im.height
        cw = int(ch * W / bh)
    cx = int(np.clip(focus[0] * im.width - cw / 2, 0, im.width - cw))
    cy = int(np.clip(focus[1] * im.height - ch / 2, 0, im.height - ch))
    ph = im.crop((cx, cy, cx + cw, cy + ch)).resize((W, bh), Image.LANCZOS).convert('RGBA')
    y = np.arange(bh, dtype=np.float32)
    a = np.clip(np.minimum(y / fade, (bh - 1 - y) / fade), 0, 1) ** 1.3 * 255
    ph.putalpha(Image.fromarray(np.repeat(a[:, None], W, 1).astype(np.uint8)))
    img.alpha_composite(ph, (0, y0))


def place(src, focus, W, H, target):
    im = warm(Image.open(M + 'site/' + src))
    sc = max(W / im.width, H / im.height) * 1.02
    im = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)
    fx, fy = focus[0] * im.width, focus[1] * im.height
    x0 = int(np.clip(fx - target[0], 0, im.width - W))
    y0 = int(np.clip(fy - target[1], 0, im.height - H))
    return im.crop((x0, y0, x0 + W, y0 + H)).convert('RGBA')


def shade(img, top_end, bot_start, top_a=235, bot_a=245):
    W, H = img.size
    y = np.arange(H, dtype=np.float32)
    a = np.maximum(np.clip(1 - y / top_end, 0, 1) ** 1.4 * top_a,
                   np.clip((y - bot_start) / (H - bot_start), 0, 1) ** 1.2 * bot_a)
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    lay.putalpha(Image.fromarray(np.repeat(a[:, None], W, 1).astype(np.uint8)))
    img.alpha_composite(lay)


def fit_font(d, lines, maxw, start):
    s = start
    while max(d.textlength(t, font=serif(s)) for t, _ in lines) > maxw:
        s -= 2
    return s


def render(src, focus, lines, service, slug, W, H, kind):
    story = kind == 'story'
    # keep text inside Meta's safe zones: stories lose ~14% top and ~20% bottom to UI
    top0 = 250 if story else 64
    bottom_pad = 340 if story else 70
    img = Image.new('RGBA', (W, H), (11, 10, 8, 255))
    if story:
        band(img, src, focus, 600, 1370, 150)
    else:
        band(img, src, focus, 440, 1110, 120)
    d = ImageDraw.Draw(img)
    pad = 72
    lw = 360
    lg = logo.resize((lw, int(logo.height * lw / logo.width)), Image.LANCZOS)
    img.alpha_composite(lg, (pad, top0))
    y = top0 + lg.height + 54
    fs = fit_font(d, lines, W - 2 * pad, 118)
    for t, gold in lines:
        d.text((pad - 4, y), t, font=serif(fs), fill=GOLD_HI if gold else WHITE)
        y += int(fs * 1.02)
    d.rounded_rectangle((pad, y + 22, pad + 120, y + 27), 2, fill=GOLD)
    # bottom block
    by = H - bottom_pad - 98
    btn = 'BOOK NOW'
    bf = bold(38)
    bw = d.textlength(btn, font=bf) + 56 + 46
    d.rounded_rectangle((pad, by, pad + bw, by + 98), 49, fill=GOLD)
    d.text((pad + 46, by + 22), btn, font=bf, fill=(16, 14, 10))
    ax = pad + 46 + d.textlength(btn, font=bf) + 20
    d.line((ax, by + 49, ax + 28, by + 49), fill=(16, 14, 10), width=5)
    d.line((ax + 16, by + 37, ax + 29, by + 49, ax + 16, by + 61), fill=(16, 14, 10), width=5)
    d.text((pad, by - 74), 'Chelsea, NYC  ·  By Appointment Only', font=sans(32), fill=GOLD)
    d.text((pad, by - 146), service, font=sans(48), fill=WHITE)
    name = f'mudras-{slug}-{"story-1080x1920" if story else "feed-1080x1350"}'
    img.convert('RGB').save(OUT + f'/{name}.jpg', quality=92)
    return name


for src, focus, lines, service, slug in ADS:
    print(render(src, focus, lines, service, slug, 1080, 1350, 'feed'))
    print(render(src, focus, lines, service, slug, 1080, 1920, 'story'))
