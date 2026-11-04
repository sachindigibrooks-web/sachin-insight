"""hitachi-magic-wand-massagers.co.uk: 'How to Clean a Wand Vibrator' featured image + in-article graphics.
Reuses the palette, cutout and background helpers from the earlier 'What Is a Wand Vibrator' post."""
import sys

src = open(sys.argv[3] + '/blog-images/what-is-a-wand-vibrator/src/hitachi.py').read()
exec(src.split('# ---------- featured ----------')[0])
exec('def card' + src.split('def card')[1].split('# ---------- in-article: how it works')[0].split('\nim = background()')[0])
OUT = sys.argv[2]


def title(im, text):
    d = ImageDraw.Draw(im)
    centered(d, W / 2, 26, text, fX(38), NAVY)
    d.rounded_rectangle((W / 2 - 50, 94, W / 2 + 50, 99), 3, fill=LINE)


GREEN, RED = (24, 140, 90), (196, 60, 50)
SOAP = 'ToyJoy-Organic-Toy-Cleaner-Spray-150ml-UK-01.png'


def save(im, name):
    im.convert('RGB').save(OUT + f'/{name}.webp', quality=90)
    im.convert('RGB').save(OUT + f'/{name}.png')
    if name.endswith('featured'):
        im.convert('RGB').save(OUT + f'/{name}.jpg', quality=92)


def wrap(d, text, font, width):
    out, cur = [], ''
    for w in text.split():
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=font) > width and cur:
            out.append(cur); cur = w
        else:
            cur = t
    return out + [cur]


def spray():
    o = Image.open(P + SOAP).convert('RGBA')
    if o.getchannel('A').getextrema()[0] == 255:  # no transparency: cut the white background out
        o = cutout(P + SOAP)
    return o.crop(o.getbbox())


# ---------- featured ----------
img = background()
blob(img, lambda d: d.ellipse((600, 520, 1230, 650), fill=255), (250, 251, 253), 2)
blob(img, lambda d: d.ellipse((600, 520, 1230, 650), outline=255, width=2), (226, 232, 242), 1)
wr = fit(cutout(P + 'Magic-Wand-Rechargeable-HV-270-UK-10.jpg'), h=440)
wp = fit(cutout(P + 'Magic-Wand-Waterproof-HV-360-UK-01.jpg'), h=410)
sp = fit(spray(), h=250)
floor = 596
for o, x in ((wr, 740), (wp, 900), (sp, 1040)):
    contact(img, x + o.width / 2, floor, o.width * 1.1)
    drop(img, o, (int(x), floor - o.height), blur=10, off=(8, 6), op=40)
d = ImageDraw.Draw(img)
k = 'Care & Hygiene Guide'
d.text((70, 160), k, font=fS(34), fill=KICK)
kw = d.textlength(k, font=fS(34))
d.rounded_rectangle((72, 214, 72 + kw, 218), 2, fill=LINE)
y = 244
for line in ['How to Clean', 'a Wand Vibrator']:
    d.text((66, y), line, font=fX(62), fill=NAVY)
    y += 80
d.text((70, y + 22), 'Gentle care for each model in the range', font=fS(22), fill=GREY)
save(img, 'how-to-clean-a-wand-vibrator-featured')

# ---------- 1. five-minute routine ----------
im = background()
title(im, 'Your Five-Minute Care Routine')
steps = [
    ('Power down', 'Off, and the cord or charger out.'),
    ('Strip it back', 'Covers and attachments come off.'),
    ('Gentle wipe', 'A soft cloth and a little gentle soap.'),
    ('Rinse the cloth', 'Lift the soap off with plain water.'),
    ('Air dry', 'Towel off, then leave it to air out.'),
]
cw, gap = 196, 20
x0 = (W - (5 * cw + 4 * gap)) // 2
for i, (t, body) in enumerate(steps):
    x = x0 + i * (cw + gap)
    card(im, (x, 140, x + cw, 470))
    d = ImageDraw.Draw(im)
    d.ellipse((x + cw / 2 - 36, 172, x + cw / 2 + 36, 244), fill=KICK)
    centered(d, x + cw / 2, 184, str(i + 1), fX(40), (255, 255, 255))
    y = 272
    for ln in wrap(d, t, fX(25), cw - 30):
        centered(d, x + cw / 2, y, ln, fX(25), NAVY); y += 33
    y += 14
    for ln in wrap(d, body, fS(21), cw - 30):
        centered(d, x + cw / 2, y, ln, fS(21), GREY); y += 30
    if i < 4:
        ax = x + cw + 3
        d.polygon([(ax, 298), (ax + gap - 6, 308), (ax, 318)], fill=ACCENT)
d = ImageDraw.Draw(im)
centered(d, W / 2, 520, 'Cord or charger attached? Unplug before you start.', fS(22), KICK)
save(im, 'wand-vibrator-five-minute-care-routine')

# ---------- 2. wipe or water by model ----------
im = background()
title(im, 'Wipe or Water? It Depends on the Model')
models = [
    ('Magic-Wand-Original-HV-260-UK-01.jpg', 'Original', 'Wipe only', RED, 'No soaking or rinsing. Take care near the buttons.'),
    ('Magic-Wand-Rechargeable-HV-270-UK-10.jpg', 'Rechargeable', 'Wipe only', RED, 'Unplug first. Charging port must be bone dry after.'),
    ('Magic-Wand-Waterproof-HV-360-UK-01.jpg', 'Waterproof', 'Water friendly', GREEN, 'IPX7. Seal the blue base plug before it goes near water.'),
    ('Magic-Wand-Plus-HV-265-UK-01.jpg', 'Plus, Mini, Micro', 'Check first', (214, 120, 0), 'Check your manual. In doubt? Damp cloth only.'),
]
cw, gap = 250, 18
x0 = (W - (4 * cw + 3 * gap)) // 2
for i, (f, name, tag, col, note) in enumerate(models):
    x = x0 + i * (cw + gap)
    card(im, (x, 122, x + cw, 590))
    o = fit(cutout(P + f), h=200)
    contact(im, x + cw / 2, 326, o.width * 1.2, 45)
    im.alpha_composite(o, (int(x + cw / 2 - o.width / 2), 326 - o.height))
    d = ImageDraw.Draw(im)
    centered(d, x + cw / 2, 344, 'Magic Wand', fS(16), GREY)
    centered(d, x + cw / 2, 366, name, fX(24), NAVY)
    tw = d.textlength(tag, font=fB(18))
    d.rounded_rectangle((x + cw / 2 - tw / 2 - 18, 412, x + cw / 2 + tw / 2 + 18, 452), 20, fill=col)
    centered(d, x + cw / 2, 420, tag, fB(18), (255, 255, 255))
    y = 474
    for ln in wrap(d, note, fS(17), cw - 36):
        centered(d, x + cw / 2, y, ln, fS(17), GREY); y += 25
d = ImageDraw.Draw(im)
centered(d, W / 2, 616, 'Water friendly is not the same as safe to leave underwater.', fS(20), KICK)
save(im, 'wand-vibrator-wipe-or-water-by-model')

# ---------- 3. reach for / steer clear ----------
im = background()
title(im, 'What Belongs in Your Wand Care Kit')
for col_i, (head, col, items) in enumerate([
    ('Reach for', GREEN, ['Gentle, fragrance-free soap', 'Warm water', 'A soft, clean cloth', 'Toy cleaner suited to your wand', 'A dedicated storage bag']),
    ('Steer clear of', RED, ['Bleach or acetone', 'Harsh solvents', 'Scourers and rough sponges', 'Long soaks in cleaning fluid', 'Packing it away while damp']),
]):
    x = 90 + col_i * 560
    card(im, (x, 122, x + 500, 600))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((x, 122, x + 500, 196), 20, fill=col)
    d.rectangle((x, 170, x + 500, 196), fill=col)
    d.text((x + 30, 136), head, font=fX(30), fill=(255, 255, 255))
    y = 226
    for it in items:
        if col_i == 0:
            d.line((x + 34, y + 16, x + 44, y + 26, x + 62, y + 6), fill=col, width=5, joint='curve')
        else:
            d.line((x + 36, y + 4, x + 58, y + 26), fill=col, width=5)
            d.line((x + 58, y + 4, x + 36, y + 26), fill=col, width=5)
        d.text((x + 84, y), it, font=fS(22), fill=NAVY)
        y += 62
sp = fit(spray(), h=130)
im.alpha_composite(sp, (90 + 500 - sp.width - 30, 600 - sp.height - 14))
save(im, 'wand-vibrator-care-kit')
print('done')
