"""vigrxplus.uk.com: 'Does an Enlarged Prostate Affect a Man Sexually?' featured image + in-article graphics.
Reuses palette and helpers from the earlier VigRX post so the blog looks consistent."""
import sys

src = open(sys.argv[3] + '/blog-images/how-do-you-make-a-man-hard/src/vigrx.py').read()
exec(src.split('# ---------- featured ----------')[0])
exec(src.split('# ---------- shared bits for in-article graphics ----------')[1].split('# ---------- in-article 1')[0])
OUT = sys.argv[2]
WHITE = (255, 255, 255)
AMBER = (200, 120, 20)


def product(path, **kw):
    o = Image.open(path)
    if o.mode == 'RGBA' and o.getchannel('A').getextrema()[0] < 250:
        o = o.crop(o.getchannel('A').getbbox())
    else:
        o = cutout(path)
    return fit(o, **kw)


def save(im, name):
    im.convert('RGB').save(OUT + f'/{name}.webp', quality=90)
    im.convert('RGB').save(OUT + f'/{name}.png')
    if name.endswith('featured'):
        im.convert('RGB').save(OUT + f'/{name}.jpg', quality=92)


# ---------- featured ----------
img = Image.new('RGBA', (W, H), BG + (255,))
ph = Image.open(V + 'ph/man.jpg').convert('RGB')
pw = 1300
ph = ph.resize((pw, int(ph.height * pw / ph.width)), Image.LANCZOS)
img.paste(ph, (W - pw + 160, (H - ph.height) // 2))
xx = np.arange(W, dtype=np.float32)
fade = np.clip((xx - 500) / 220, 0, 1)
ov = Image.new('RGBA', (W, H), BG + (255,))
ov.putalpha(Image.fromarray(((1 - fade) * 255).astype(np.uint8)[None, :].repeat(H, 0)))
img.alpha_composite(ov)
img.alpha_composite(Image.new('RGBA', (W, H), (255, 250, 246, 36)))
d = ImageDraw.Draw(img)
k = "MEN'S HEALTH GUIDE"
kf = fB(15)
kw = d.textlength(k, font=kf) + 6 * len(k) * 0.12
d.rounded_rectangle((56, 92, 56 + kw + 60, 128), 18, fill=BLUSH, outline=(232, 170, 170), width=1)
d.ellipse((74, 104, 86, 116), fill=RED)
x = 98
for ch in k:
    d.text((x, 99), ch, font=kf, fill=DEEP)
    x += d.textlength(ch, font=kf) + 1.6
y = 150
for line in ['Does an Enlarged', 'Prostate Affect a', 'Man Sexually?']:
    d.text((54, y), line, font=fX(50), fill=INK)
    y += 62
d.text((58, y + 10), 'What UK Men Should Know', font=fS(26), fill=INK)
y += 70
x = 56
for kind, t in [('check', 'Common after 50'), ('plus', 'Treatment effects'), ('heart', 'When to see a GP')]:
    x += chip(img, x, y, kind, t) + 12
d = ImageDraw.Draw(img)
heartbeat(d, 0, 560, 560)
box = product(V + 'prod/prostate.webp', h=210)
bx, by = W - box.width - 36, H - box.height - 34
soft(img, lambda dd, op: dd.rounded_rectangle((bx - 40, by + box.height - 6, W + 20, H + 40), 10, fill=op), WHITE, 235, 1)
soft(img, lambda dd, op: dd.ellipse((bx - 10, by + box.height - 14, bx + box.width + 14, by + box.height + 10), fill=op), INK, 70, 8)
img.alpha_composite(box, (bx, by))
save(img, 'enlarged-prostate-sexual-health-featured')

# ---------- 1. why the two overlap ----------
im = canvas('Why the Two Often Overlap', 'Prostate size is rarely the whole story')
cards = [
    ('Getting older', 'The odds of each climb with every decade past 50.'),
    ('Weight & activity', 'Extra weight can worsen urinary trouble; moving more may ease it.'),
    ('Stress & broken sleep', 'Night-time toilet trips and worry chip away at confidence.'),
    ('Medicines & procedures', 'The clearest link: some treatments change sex, covered below.'),
]
cw, gap = 245, 22
x0 = (W - (4 * cw + 3 * gap)) // 2
for i, (t, body) in enumerate(cards):
    x = x0 + i * (cw + gap)
    card(im, (x, 160, x + cw, 500))
    d = ImageDraw.Draw(im)
    num(d, x + 44, 212, i + 1, 26)
    y = 262
    for ln in wrap(d, t, fX(25), cw - 48):
        d.text((x + 24, y), ln, font=fX(25), fill=INK); y += 33
    y += 16
    for ln in wrap(d, body, fS(21), cw - 44):
        d.text((x + 24, y), ln, font=fS(21), fill=GREY); y += 30
d = ImageDraw.Draw(im)
foot = 'Think of the prostate as one factor among several, not the sole cause.'
d.text(((W - d.textlength(foot, font=fS(19))) / 2, 548), foot, font=fS(19), fill=INK)
save(im, 'enlarged-prostate-ed-shared-factors')

# ---------- 2. treatment side effects ----------
im = canvas('Treatment Side Effects at a Glance', 'How common options may affect your sex life')
rows = [
    ('Alpha blockers', 'e.g. tamsulosin', 'Ejaculation may feel different, with reduced or absent semen.', AMBER),
    ('5 alpha reductase inhibitors', 'finasteride, dutasteride', 'Effects on erections, desire or climax are rare and tend to show in year one.', (120, 150, 60)),
    ('Taking both together', 'combination therapy', 'Raises the odds of bedroom side effects versus a single drug.', RED),
    ('Surgery', 'varies by procedure', 'Possible erection or ejaculation changes. Rezūm steam therapy carries a low risk.', DEEP),
]
y = 150
for t, eg, body, col in rows:
    card(im, (80, y, W - 80, y + 96))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((80, y, 88, y + 96), 4, fill=col)
    d.text((112, y + 18), t, font=fX(23), fill=INK)
    d.text((112, y + 54), eg, font=fS(17), fill=GREY)
    lines = wrap(d, body, fS(19), 520)
    for j, ln in enumerate(lines):
        d.text((560, y + 48 - len(lines) * 14 + j * 28), ln, font=fS(19), fill=INK)
    y += 112
d = ImageDraw.Draw(im)
foot = 'Noticed a change? Check with a doctor before stopping any medicine.'
d.text(((W - d.textlength(foot, font=fB(20))) / 2, 612), foot, font=fB(20), fill=RED)
save(im, 'enlarged-prostate-treatment-side-effects')

# ---------- 3. GP or urgent ----------
im = canvas('GP Appointment or Urgent Help?', 'Know which symptoms can wait for a booking and which cannot')
cols = [
    ('Book a GP visit', INK, ['Struggling to start or keep a flow', 'Needing the toilet more often', 'Erection problems that keep coming back']),
    ('Get help today', RED, ['Any blood when you pee', 'It hurts when you go', 'Unable to pass urine at all']),
]
for i, (head, col, items) in enumerate(cols):
    x = 90 + i * 530
    card(im, (x, 160, x + 490, 560))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((x, 160, x + 490, 236), 16, fill=col)
    d.rectangle((x, 210, x + 490, 236), fill=col)
    d.text((x + 30, 176), head, font=fX(30), fill=WHITE)
    if i == 1:
        tag = 'Urgent GP or NHS 111'
        tw = d.textlength(tag, font=fB(16))
        d.rounded_rectangle((x + 490 - tw - 52, 184, x + 490 - 22, 214), 15, fill=WHITE)
        d.text((x + 490 - tw - 37, 189), tag, font=fB(16), fill=RED)
    y = 270
    for it in items:
        d.ellipse((x + 30, y + 10, x + 44, y + 24), fill=col)
        for ln in wrap(d, it, fS(22), 400):
            d.text((x + 62, y), ln, font=fS(22), fill=INK); y += 32
        y += 36
d = ImageDraw.Draw(im)
foot = 'Several conditions share these signs, so an early check is worth it.'
d.text(((W - d.textlength(foot, font=fS(19))) / 2, 600), foot, font=fS(19), fill=GREY)
save(im, 'enlarged-prostate-when-to-see-gp')
print('done')
