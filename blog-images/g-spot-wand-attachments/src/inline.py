import sys
src = open(sys.argv[1] + '/make.py').read()
exec(src.split('# ---------- products')[0])  # helpers, palette, background -> img, cor
base = img.copy()
base.alpha_composite(cor)
OUT = sys.argv[2]
fB = lambda s: ImageFont.truetype(F + 'Poppins-Bold.ttf', s)
fX = lambda s: ImageFont.truetype(F + 'Poppins-ExtraBold.ttf', s)
fS = lambda s: ImageFont.truetype(F + 'Poppins-SemiBold.ttf', s)
GREY = (70, 84, 110)


def card(im, box, r=22):
    x0, y0, x1, y1 = box
    sh = Image.new('L', im.size, 0)
    ImageDraw.Draw(sh).rounded_rectangle((x0, y0 + 8, x1, y1 + 8), r, fill=60)
    lay = Image.new('RGBA', im.size, NAVY + (255,))
    lay.putalpha(sh.filter(ImageFilter.GaussianBlur(14)))
    im.alpha_composite(lay)
    ImageDraw.Draw(im).rounded_rectangle(box, r, fill=(255, 255, 255, 255), outline=(214, 232, 248), width=2)


def centered(d, cx, y, text, font, fill):
    w = d.textlength(text, font=font)
    d.text((cx - w / 2, y), text, font=font, fill=fill)


def title(im, text):
    d = ImageDraw.Draw(im)
    centered(d, W / 2, 34, text, fX(40), NAVY)
    d.rounded_rectangle((W / 2 - 50, 92, W / 2 + 50, 98), 3, fill=BLUE)


# ---------- 1. range comparison ----------
im = base.copy()
title(im, 'Our G Spot Wand Attachment Range')
prods = [
    ('eu2.webp', 'Euphoria', '£59.95', [('Material', 'Silicone'), ('Insertable', '5 in'), ('Opening', '2.25 in')], 'Internal + clitoral'),
    ('dg3.webp', 'Deep Glider', '£59.95', [('Material', 'TPR'), ('Insertable', '4 in'), ('Opening', '2.25 in')], 'Curved internal tip'),
    ('rt3.webp', 'Rabbit Tip', '£49.95', [('Material', 'TPE'), ('Insertable', '4 in'), ('Inner diameter', '2.3 in')], 'Internal + clitoral'),
]
cw, gap = 340, 40
x = (W - (3 * cw + 2 * gap)) // 2
for f, name, price, rows, tag in prods:
    card(im, (x, 125, x + cw, 645))
    o = cutout(P + f)
    sc = min(170 / o.height, 250 / o.width)
    o = o.resize((int(o.width * sc), int(o.height * sc)), Image.LANCZOS)
    im.alpha_composite(o, (x + (cw - o.width) // 2, 150 + (175 - o.height)))
    d = ImageDraw.Draw(im)
    cx = x + cw / 2
    centered(d, cx, 338, name, fX(30), NAVY)
    centered(d, cx, 380, price, fB(26), BLUE)
    y = 428
    for k, v in rows:
        d.line((x + 28, y - 8, x + cw - 28, y - 8), fill=(228, 238, 248), width=2)
        d.text((x + 30, y), k, font=fS(19), fill=GREY)
        vw = d.textlength(v, font=fB(19))
        d.text((x + cw - 30 - vw, y), v, font=fB(19), fill=NAVY)
        y += 42
    tw = d.textlength(tag, font=fB(18))
    d.rounded_rectangle((cx - tw / 2 - 16, 572, cx + tw / 2 + 16, 610), 19, fill=BLUE)
    centered(d, cx, 579, tag, fB(18), (255, 255, 255))
    x += cw + gap
im.convert('RGB').save(OUT + '/g-spot-attachment-range-comparison.webp', quality=90)
im.convert('RGB').save(OUT + '/g-spot-attachment-range-comparison.png')

# ---------- 2. fit guide ----------
im = base.copy()
title(im, 'Will It Fit Your Wand?')
card(im, (50, 125, 560, 645))
card(im, (600, 125, 1150, 645))
d = ImageDraw.Draw(im)
d.text((80, 150), 'Attachment openings', font=fX(26), fill=NAVY)
y = 205
for f, name, val in [('eu2.webp', 'Euphoria', '2.25 in opening'), ('dg3.webp', 'Deep Glider', '2.25 in opening'), ('rt3.webp', 'Rabbit Tip', '2.3 in inner diameter')]:
    o = cutout(P + f)
    sc = min(110 / o.height, 120 / o.width)
    o = o.resize((int(o.width * sc), int(o.height * sc)), Image.LANCZOS)
    im.alpha_composite(o, (80 + (120 - o.width) // 2, y + (110 - o.height) // 2))
    d = ImageDraw.Draw(im)
    d.text((225, y + 22), name, font=fB(24), fill=NAVY)
    d.text((225, y + 58), val, font=fS(20), fill=BLUE)
    y += 140
d.text((630, 150), 'Our wands', font=fX(26), fill=NAVY)
wand = cutout(P + 'mw1.jpg', 60)
sc = 420 / wand.width
wand = wand.resize((420, int(wand.height * sc)), Image.LANCZOS)
im.alpha_composite(wand, (665, 195))
d = ImageDraw.Draw(im)
y = 195 + wand.height + 20
GREEN, AMBER = (22, 150, 90), (214, 120, 0)
for name, note, ok in [('Magic Wand Rechargeable', 'Standard head', True), ('Magic Wand Plus', 'Standard head', True),
                       ('Magic Wand Mini', 'Smaller - check fit', False), ('Magic Wand Micro', 'Smaller - check fit', False)]:
    col = GREEN if ok else AMBER
    d.ellipse((632, y + 4, 658, y + 30), fill=col)
    if ok:
        d.line((638, y + 17, 643, y + 23, 652, y + 11), fill=(255, 255, 255), width=4, joint='curve')
    else:
        d.text((641, y + 1), '!', font=fX(20), fill=(255, 255, 255))
    d.text((672, y), name, font=fB(21), fill=NAVY)
    nw = d.textlength(note, font=fS(18))
    d.text((1120 - nw, y + 3), note, font=fS(18), fill=col)
    y += 46
d.line((630, 578, 1120, 578), fill=(228, 238, 248), width=2)
d.text((630, 588), 'Listed as fitting standard size wands, including Hitachi.', font=fS(16), fill=GREY)
d.text((630, 611), 'Not sure about your model? Contact our team first.', font=fS(16), fill=GREY)
im.convert('RGB').save(OUT + '/g-spot-attachment-fit-guide.webp', quality=90)
im.convert('RGB').save(OUT + '/g-spot-attachment-fit-guide.png')
