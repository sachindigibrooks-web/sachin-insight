"""Magic Wand Original UK: 'How to Choose a Wand Attachment' featured image + in-article graphics.
Reuses the background, cutout and brush helpers from the earlier G spot post so the series looks consistent."""
import sys

REPO = sys.argv[3]
src = open(REPO + '/blog-images/g-spot-wand-attachments/src/make.py').read()
exec(src.split('# ---------- products')[0])                         # palette, cutout, shadowed, reflect, bg -> img, cor
exec('def brush' + src.split('def brush')[1].split('\nfs = ')[0])  # brushstroke helper
OUT = sys.argv[2]
base = img.copy()
base.alpha_composite(cor)
fX = lambda s: ImageFont.truetype(F + 'Poppins-ExtraBold.ttf', s)
fB = lambda s: ImageFont.truetype(F + 'Poppins-Bold.ttf', s)
fS = lambda s: ImageFont.truetype(F + 'Poppins-SemiBold.ttf', s)
GREY = (70, 84, 110)
GREEN, AMBER = (22, 150, 90), (214, 120, 0)


def fit(o, h=None, w=None):
    sc = min(h / o.height if h else 9e9, w / o.width if w else 9e9)
    return o.resize((int(o.width * sc), int(o.height * sc)), Image.LANCZOS)


def save(im, name):
    im.convert('RGB').save(OUT + f'/{name}.webp', quality=90)
    im.convert('RGB').save(OUT + f'/{name}.png')
    if name.endswith('featured'):
        im.convert('RGB').save(OUT + f'/{name}.jpg', quality=92)


# ---------- featured ----------
wand = cutout(P + 'mw1.jpg', 60).rotate(18, resample=Image.BICUBIC, expand=True)
wand = wand.crop(wand.getbbox())
wand = fit(wand, w=480)
shadowed(img, wand, (W - 500, -10), blur=18, off=(0, 18), op=50)
img.alpha_composite(cor)
items = [fit(cutout(P + f), h=h, w=mw) for f, h, mw in [('lily3.webp', 150, 999), ('rt3.webp', 140, 240), ('eu2.webp', 180, 999)]]
floor, gap = 625, 18
x = W - 40 - (sum(o.width for o in items) + gap * (len(items) - 1))
for o in items:
    pos = (x, floor - o.height)
    reflect(img, o, pos)
    shadowed(img, o, pos, blur=10, off=(0, 8), op=60)
    x += o.width + gap
logo = Image.open(P + 'logo.png').convert('RGBA')
logo = logo.resize((int(logo.width * 46 / logo.height), 46), Image.LANCZOS)
lc = Image.new('RGBA', logo.size, TEAL + (255,))
lc.putalpha(logo.getchannel('A'))
img.alpha_composite(lc, (60, 52))
d = ImageDraw.Draw(img)
y = 132
for line in ['How to Choose a', 'Wand Attachment']:
    d.text((56, y), line, font=fX(60), fill=NAVY)
    y += 74
y += 22
for line in ['5 Checks Before', 'You Buy']:
    bb = d.textbbox((0, 0), line, font=fB(44))
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    img.alpha_composite(brush(tw + 36, th + 26), (40, y - 14))
    d = ImageDraw.Draw(img)
    d.text((76 - bb[0], y + 17 - bb[1]), line, font=fB(44), fill=WHITE if 'WHITE' in globals() else (255, 255, 255))
    y += th + 34
save(img, 'how-to-choose-a-wand-attachment-featured')

# ---------- shared graphic helpers ----------
WHITE = (255, 255, 255)


def card(im, box, r=22, fill=WHITE, outline=(214, 232, 248)):
    x0, y0, x1, y1 = box
    m = Image.new('L', im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((x0, y0 + 8, x1, y1 + 8), r, fill=60)
    lay = Image.new('RGBA', im.size, NAVY + (255,))
    lay.putalpha(m.filter(ImageFilter.GaussianBlur(14)))
    im.alpha_composite(lay)
    ImageDraw.Draw(im).rounded_rectangle(box, r, fill=fill, outline=outline, width=2)


def centered(d, cx, y, text, font, fill):
    d.text((cx - d.textlength(text, font=font) / 2, y), text, font=font, fill=fill)


def canvas(text, sub):
    im = base.copy()
    d = ImageDraw.Draw(im)
    centered(d, W / 2, 30, text, fX(38), NAVY)
    centered(d, W / 2, 84, sub, fS(19), GREY)
    d.rounded_rectangle((W / 2 - 50, 118, W / 2 + 50, 123), 3, fill=BLUE)
    return im


def wrap(d, text, font, width):
    out, cur = [], ''
    for w in text.split():
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=font) > width and cur:
            out.append(cur); cur = w
        else:
            cur = t
    return out + [cur]


# ---------- 1. pre-purchase checklist ----------
im = canvas('Your Pre-Purchase Checklist', 'Run through these five points before you add to basket')
checks = [
    ('Fit', 'Match the inner diameter to your wand head.'),
    ('Material', 'TPE, silicone or vinyl each feel and clean differently.'),
    ('Shape', 'External, dual, insertable or designed for men.'),
    ('Lube', 'Start with water based, and wash after every use.'),
    ('Seller', 'Buy genuine, with clear compatibility details and a warranty.'),
]
y = 150
for i, (t, body) in enumerate(checks):
    card(im, (110, y, W - 110, y + 82), r=18)
    d = ImageDraw.Draw(im)
    d.ellipse((136, y + 18, 186, y + 68), fill=BLUE)
    centered(d, 161, y + 22, str(i + 1), fX(26), WHITE)
    d.text((212, y + 24), t, font=fX(28), fill=NAVY)
    d.text((390, y + 31), body, font=fS(20), fill=GREY)
    y += 98
save(im, 'wand-attachment-pre-purchase-checklist')

# ---------- 2. standard head or compact ----------
im = canvas('Standard Head or Compact?', 'Most attachments are sized for full-size wand heads')
wands = [
    ('mw1.jpg', 'Rechargeable', '£159.95', True), ('mwp.jpg', 'Plus', '£129.95', True),
    ('mwm5.jpg', 'Mini', '£94.95', False), ('mwu2.jpg', 'Micro', '£64.95', False),
]
cw, gap = 245, 22
x0 = (W - (4 * cw + 3 * gap)) // 2
for i, (f, name, price, std) in enumerate(wands):
    x = x0 + i * (cw + gap)
    card(im, (x, 146, x + cw, 566))
    d = ImageDraw.Draw(im)
    o = cutout(P + f, 60)
    o = o.rotate(90 if o.width > o.height else 0, resample=Image.BICUBIC, expand=True)
    o = fit(o.crop(o.getbbox()), h=210 if std else 145, w=cw - 70)
    im.alpha_composite(o, (x + (cw - o.width) // 2, 375 - o.height))
    d = ImageDraw.Draw(im)
    centered(d, x + cw / 2, 392, 'Magic Wand', fS(17), GREY)
    centered(d, x + cw / 2, 416, name, fX(26), NAVY)
    centered(d, x + cw / 2, 456, price, fB(20), BLUE)
    col = GREEN if std else AMBER
    tag = 'Standard head' if std else 'Smaller head'
    tw = d.textlength(tag, font=fB(17))
    d.rounded_rectangle((x + cw / 2 - tw / 2 - 16, 504, x + cw / 2 + tw / 2 + 16, 542), 19, fill=col)
    centered(d, x + cw / 2, 511, tag, fB(17), WHITE)
d = ImageDraw.Draw(im)
centered(d, W / 2, 590, 'Standard head: still check each attachment listing before ordering.', fS(19), GREY)
centered(d, W / 2, 620, 'Smaller head: contact the team first to confirm a fit.', fB(19), NAVY)
save(im, 'wand-attachment-standard-vs-compact')

# ---------- 3. style finder ----------
im = canvas('Pick a Style That Suits You', 'A few popular options from the range')
styles = [
    ('lily3.webp', 'Lily Pod', 'External, textured', 'TPE', '£39.95'),
    ('rt3.webp', 'Rabbit Tip', 'Dual stimulation', 'TPE', '£49.95'),
    ('eu2.webp', 'Euphoria', 'Dual stimulation', 'Silicone', '£59.95'),
    ('twin.jpg', 'Twin Turbo', 'Designed for men', '2 in 1 stroker', '£49.95'),
    ('assist.jpg', 'Wand Assist', 'Hands-free holder', 'Gooseneck', '£89.95'),
]
cw, gap = 196, 18
x0 = (W - (5 * cw + 4 * gap)) // 2
for i, (f, name, use, mat, price) in enumerate(styles):
    x = x0 + i * (cw + gap)
    card(im, (x, 146, x + cw, 590))
    o = fit(cutout(P + f), h=160, w=cw - 36)
    im.alpha_composite(o, (x + (cw - o.width) // 2, 168 + (160 - o.height)))
    d = ImageDraw.Draw(im)
    centered(d, x + cw / 2, 346, name, fX(23), NAVY)
    y = 384
    for ln in wrap(d, use, fS(18), cw - 30):
        centered(d, x + cw / 2, y, ln, fS(18), GREY); y += 26
    d.line((x + 24, 446, x + cw - 24, 446), fill=(228, 238, 248), width=2)
    centered(d, x + cw / 2, 460, mat, fB(18), NAVY)
    tw = d.textlength(price, font=fB(19))
    d.rounded_rectangle((x + cw / 2 - tw / 2 - 18, 522, x + cw / 2 + tw / 2 + 18, 564), 21, fill=BLUE)
    centered(d, x + cw / 2, 530, price, fB(19), WHITE)
d = ImageDraw.Draw(im)
centered(d, W / 2, 612, 'New to attachments? Start with one style and see how you get on.', fS(18), GREY)
save(im, 'wand-attachment-style-finder')
print('done')
