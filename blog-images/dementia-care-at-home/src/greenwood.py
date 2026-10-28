import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

D = sys.argv[1]
G = D + '/g/'
F = D + '/fonts/'
OUT = sys.argv[2]
W, H = 1200, 800  # 3:2, same shape as the site's recent featured images (1024x683)
NAVY = (26, 48, 82)      # #1a3052 hero button / logo wordmark
TEAL = (156, 203, 194)   # #9ccbc2 logo leaves
AMBER = (229, 154, 88)   # #e59a58 hero panel / Get Started button
TEAL_PALE = (232, 243, 240)
BG = (248, 248, 248)     # #f8f8f8 page background
GREY = (84, 98, 118)
WHITE = (255, 255, 255)
fX = lambda s: ImageFont.truetype(F + 'DMSerifDisplay-Regular.ttf', int(s * 1.15))  # serif headings, as on the site
fB = lambda s: ImageFont.truetype(F + 'FiraSans-SemiBold.ttf', s)
fS = lambda s: ImageFont.truetype(F + 'FiraSans-Medium.ttf', s)


def soft(base, shape_fn, col, op=255, blur=0):
    m = Image.new('L', base.size, 0)
    shape_fn(ImageDraw.Draw(m), op)
    if blur:
        m = m.filter(ImageFilter.GaussianBlur(blur))
    lay = Image.new('RGBA', base.size, col + (255,))
    lay.putalpha(m)
    base.alpha_composite(lay)


def wrap(d, text, font, width):
    out, cur = [], ''
    for w in text.split():
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=font) > width and cur:
            out.append(cur); cur = w
        else:
            cur = t
    return out + [cur]


def card(im, box, r=18, fill=WHITE, outline=(222, 234, 231)):
    x0, y0, x1, y1 = box
    soft(im, lambda dd, op: dd.rounded_rectangle((x0, y0 + 6, x1, y1 + 8), r, fill=op), NAVY, 30, 10)
    ImageDraw.Draw(im).rounded_rectangle(box, r, fill=fill, outline=outline, width=1)


def pill(d, x, y, text, font, fg, bg, padx=18, h=38):
    tw = d.textlength(text, font=font)
    d.rounded_rectangle((x, y, x + tw + 2 * padx, y + h), h // 2, fill=bg)
    d.text((x + padx, y + (h - font.size) / 2 - 3), text, font=font, fill=fg)
    return tw + 2 * padx


# ---------- featured: mirrors the homepage hero (orange panel with a curved edge over a photo) ----------
img = Image.new('RGBA', (W, H), BG + (255,))
ph = Image.open(G + 'ph/carer2.jpg').convert('RGB')
ph = ph.resize((int(ph.width * 820 / ph.height), 820), Image.LANCZOS)
img.paste(ph, (W - ph.width + 150, -10))
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
edge = 700 * np.sqrt(np.clip(1 - ((H - yy) / 1000) ** 2, 0, 1))  # bulges right towards the bottom
panel = np.clip(edge - xx + 0.5, 0, 1)
lay = Image.new('RGBA', (W, H), AMBER + (255,))
lay.putalpha(Image.fromarray((panel * 255).astype(np.uint8)))
img.alpha_composite(lay)
d = ImageDraw.Draw(img)
logo = Image.open(G + 'site/logo.png').convert('RGBA')
logo = logo.resize((int(logo.width * 50 / logo.height), 50), Image.LANCZOS)
d.rounded_rectangle((52, 44, 52 + logo.width + 40, 44 + 50 + 28), 16, fill=WHITE)
img.alpha_composite(logo, (72, 58))
d = ImageDraw.Draw(img)
y = 196
for ln in ['Dementia Care', 'at Home']:
    d.text((60, y), ln, font=ImageFont.truetype(F + 'DMSerifDisplay-Regular.ttf', 78), fill=WHITE)
    y += 92
y += 18
for ln in ['The Complete UK Guide', 'for Families']:
    d.text((62, y), ln, font=ImageFont.truetype(F + 'FiraSans-Medium.ttf', 34), fill=WHITE)
    y += 44
btn = 'Care options, 2026 costs and funding'
bf = ImageFont.truetype(F + 'FiraSans-SemiBold.ttf', 22)
bw = d.textlength(btn, font=bf)
d.rounded_rectangle((60, 548, 60 + bw + 64, 612), 10, fill=NAVY)
d.text((92, 563), btn, font=bf, fill=WHITE)
img.convert('RGB').save(OUT + '/dementia-care-at-home-featured.webp', quality=90)
img.convert('RGB').save(OUT + '/dementia-care-at-home-featured.jpg', quality=92)
img.convert('RGB').save(OUT + '/dementia-care-at-home-featured.png')


def canvas(title, sub):
    im = Image.new('RGBA', (W, H), BG + (255,))
    soft(im, lambda dd, op: dd.ellipse((900, -300, 1500, 260), fill=op), TEAL_PALE, 255, 2)
    soft(im, lambda dd, op: dd.ellipse((-260, 600, 300, 1100), fill=op), (255, 243, 226), 255, 2)
    d = ImageDraw.Draw(im)
    tw = d.textlength(title, font=fX(38))
    d.text(((W - tw) / 2, 40), title, font=fX(38), fill=NAVY)
    sw = d.textlength(sub, font=fS(18))
    d.text(((W - sw) / 2, 98), sub, font=fS(18), fill=GREY)
    d.rounded_rectangle((W / 2 - 44, 134, W / 2 + 44, 139), 3, fill=AMBER)
    return im


def footnote(im, text, y=752):
    d = ImageDraw.Draw(im)
    tw = d.textlength(text, font=fS(15))
    d.text(((W - tw) / 2, y), text, font=fS(15), fill=GREY)


# ---------- in-article 1: stages ----------
im = canvas('Dementia Stages and the Support Needed', 'Care at home usually moves from occasional visits to daily support, then round the clock care')
stages = [
    ('Early stage', TEAL, NAVY,
     'Memory lapses and some confusion, but most daily tasks are still managed.',
     'Short visits, reminders, shopping, company and planning ahead.'),
    ('Middle stage', (92, 150, 160), WHITE,
     'More help needed with washing, dressing, meals and safety. Mood changes are more common and evenings can be harder.',
     'Daily visits and night care often start here.'),
    ('Late stage', NAVY, WHITE,
     'Constant care is usually needed, including help with mobility, eating and communication.',
     'Live in care, 24 hour care at home or nursing care.'),
]
cw, gap = 340, 30
x0 = (W - (3 * cw + 2 * gap)) // 2
for i, (name, col, fg, notice, support) in enumerate(stages):
    x = x0 + i * (cw + gap)
    card(im, (x, 176, x + cw, 676))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((x, 176, x + cw, 246), 18, fill=col)
    d.rectangle((x, 220, x + cw, 246), fill=col)
    d.text((x + 26, 191), name, font=fX(26), fill=fg)
    d.text((x + 26, 270), 'What you may notice', font=fB(16), fill=(92, 150, 160))
    y = 302
    for ln in wrap(d, notice, fS(18), cw - 52):
        d.text((x + 26, y), ln, font=fS(18), fill=GREY); y += 29
    y = 500
    d.line((x + 26, y - 14, x + cw - 26, y - 14), fill=(228, 238, 235), width=2)
    d.text((x + 26, y), 'Helpful support', font=fB(16), fill=(214, 140, 40))
    y += 30
    for ln in wrap(d, support, fB(20), cw - 52):
        d.text((x + 26, y), ln, font=fB(20), fill=NAVY); y += 31
    if i < 2:
        ax = x + cw + 6
        d.polygon([(ax, 414), (ax + gap - 12, 426), (ax, 438)], fill=AMBER)
footnote(im, 'Stages are only a guide: progression varies with the type of dementia, age and general health.', 716)
im.convert('RGB').save(OUT + '/dementia-stages-support.webp', quality=90)
im.convert('RGB').save(OUT + '/dementia-stages-support.png')

# ---------- in-article 2: types of home care ----------
im = canvas('Types of Dementia Home Care Services', 'Many families combine them as needs change')
types = [
    ('Visiting care', 'From 30 minutes to most of the day', 'Suits early and middle stage dementia, for help with specific tasks or a regular, reassuring check in.'),
    ('Night care', 'Awake or on call overnight', 'Help with the toilet, preventing falls, reassurance and settling restless nights.'),
    ('Respite care', 'A break for the family carer', 'The person stays in their own home. Arranged for an afternoon, a weekend or several weeks.'),
    ('Live in care', '24/7 support at home', 'A trained carer lives in, giving the continuity people with dementia often need most.'),
]
cw, chh = 520, 240
for i, (t, tag, body) in enumerate(types):
    col, row = i % 2, i // 2
    x = 70 + col * (cw + 20)
    y = 190 + row * (chh + 30)
    card(im, (x, y, x + cw, y + chh))
    d = ImageDraw.Draw(im)
    d.ellipse((x + 28, y + 28, x + 84, y + 84), fill=TEAL_PALE)
    n = str(i + 1)
    nw = d.textlength(n, font=fX(26))
    d.text((x + 56 - nw / 2, y + 36), n, font=fX(26), fill=NAVY)
    d.text((x + 104, y + 30), t, font=fX(26), fill=NAVY)
    pill(d, x + 104, y + 76, tag, fS(15), NAVY, (255, 236, 208), 14, 32)
    yy = y + 134
    for ln in wrap(d, body, fS(18), cw - 60):
        d.text((x + 30, yy), ln, font=fS(18), fill=GREY); yy += 30
im.convert('RGB').save(OUT + '/types-of-dementia-home-care.webp', quality=90)
im.convert('RGB').save(OUT + '/types-of-dementia-home-care.png')

# ---------- in-article 3: costs and funding ----------
im = canvas('Dementia Care Costs and Funding at a Glance', 'UK figures for 2026 and 2026/27')
cw = 520
for col, (head, rows) in enumerate([
    ('What it costs in 2026', [
        ('Agency home care', '£26 to £38 an hour'),
        ('Two 1 hour visits a day', 'about £420 to £450 a week'),
        ('Residential dementia care home', '£1,343 a week (self funder average)'),
        ('Nursing dementia care home', '£1,564 a week (self funder average)'),
    ]),
    ('Who can help pay (2026/27)', [
        ('Council funding', 'may contribute if savings are below £23,250'),
        ('Attendance Allowance', '£76.70 or £114.60 a week, not means tested'),
        ("Carer's Allowance", '£86.45 a week for 35+ hours of caring'),
        ('NHS Continuing Healthcare', 'pays in full for a primary health need'),
    ]),
]):
    x = 70 + col * (cw + 20)
    card(im, (x, 176, x + cw, 712))
    d = ImageDraw.Draw(im)
    hc = NAVY if col == 0 else (92, 150, 160)
    d.rounded_rectangle((x, 176, x + cw, 246), 18, fill=hc)
    d.rectangle((x, 220, x + cw, 246), fill=hc)
    d.text((x + 28, 191), head, font=fX(25), fill=WHITE)
    y = 272
    for k, v in rows:
        d.ellipse((x + 28, y + 8, x + 42, y + 22), fill=AMBER)
        d.text((x + 58, y), k, font=fB(19), fill=NAVY)
        for j, ln in enumerate(wrap(d, v, fS(17), cw - 90)):
            d.text((x + 58, y + 32 + j * 26), ln, font=fS(17), fill=GREY)
        y += 108
footnote(im, 'General information, not financial advice. Check your own position with the council, Age UK or an adviser.')
im.convert('RGB').save(OUT + '/dementia-care-costs-funding.webp', quality=90)
im.convert('RGB').save(OUT + '/dementia-care-costs-funding.png')
