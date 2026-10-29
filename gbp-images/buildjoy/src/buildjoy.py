import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

D = sys.argv[1]
B = D + '/b/'
F = D + '/fonts/'
OUT = sys.argv[2]
RED = (158, 27, 42)   # logo roof red
INK = (24, 24, 24)    # logo wordmark
GREY = (90, 90, 90)
fB = lambda s: ImageFont.truetype(F + 'FiraSans-Bold.ttf', s)
fM = lambda s: ImageFont.truetype(F + 'FiraSans-Medium.ttf', s)

# logo: crop the mark from the profile square, keep it at native size (source is low resolution)
logo = Image.open(B + 'dl/prof_full.png').convert('RGB').crop((92, 154, 310, 246))
a = np.asarray(logo).astype(np.float32)
alpha = np.clip(((255 - a).max(axis=2) - 6) / 30, 0, 1)
logo = Image.fromarray(np.dstack([a, alpha * 255]).astype(np.uint8), 'RGBA')


def build(W, H, name):
    ph = Image.open(B + 'ph/ext.jpg').convert('RGB')
    sc = max(W / ph.width, H / ph.height)
    ph = ph.resize((int(ph.width * sc), int(ph.height * sc)), Image.LANCZOS)
    y0 = int((ph.height - H) * 0.35)
    x0 = (ph.width - W) // 2
    img = ph.crop((x0, y0, x0 + W, y0 + H)).convert('RGBA')
    # soft shade at the bottom so the card reads on any crop
    g = np.linspace(0, 1, H)[:, None] ** 3 * 90
    shade = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    shade.putalpha(Image.fromarray(np.repeat(g, W, 1).astype(np.uint8)))
    img.alpha_composite(shade)
    # card centred so it survives Google's 4:3 / square crops
    d = ImageDraw.Draw(img)
    t1, t2 = 'Garden Home Extensions', 'Design & build across London'
    w1, w2 = d.textlength(t1, font=fB(29)), d.textlength(t2, font=fM(18))
    cw = 20 + logo.width + 22 + 2 + 22 + max(w1, w2) + 26
    ch = 116
    cx0 = int((W - cw) // 2)
    cw = int(cw)
    cy0 = H - ch - 32
    m = Image.new('L', (W, H), 0)
    ImageDraw.Draw(m).rounded_rectangle((cx0, cy0 + 6, cx0 + cw, cy0 + ch + 8), 18, fill=90)
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    sh.putalpha(m.filter(ImageFilter.GaussianBlur(10)))
    img.alpha_composite(sh)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((cx0, cy0, cx0 + cw, cy0 + ch), 18, fill=(255, 255, 255))
    img.alpha_composite(logo, (cx0 + 20, cy0 + (ch - logo.height) // 2))
    lx = cx0 + 20 + logo.width + 22
    d.line((lx, cy0 + 22, lx, cy0 + ch - 22), fill=(225, 225, 225), width=2)
    tx = lx + 24
    d.text((tx, cy0 + 26), t1, font=fB(29), fill=INK)
    d.text((tx, cy0 + 68), t2, font=fM(18), fill=RED)
    img.convert('RGB').save(OUT + f'/{name}.jpg', quality=92)
    img.convert('RGB').save(OUT + f'/{name}.png')


build(1200, 520, 'buildjoy-gbp-garden-extension-1200x520')
build(1200, 900, 'buildjoy-gbp-garden-extension-1200x900')
