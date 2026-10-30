import sys

src = open(sys.argv[1] + '/greenwood.py').read()
exec(src.split('# ---------- featured')[0])        # palette, fonts, helpers
exec('def canvas' + src.split('def canvas')[1].split('# ---------- in-article 1')[0])  # canvas + footnote
OUT = sys.argv[2]
serif = lambda s: ImageFont.truetype(F + 'DMSerifDisplay-Regular.ttf', s)

# ---------- featured: homepage hero style ----------
img = Image.new('RGBA', (W, H), BG + (255,))
ph = Image.open(G + 'ph/homecare.jpg').convert('RGB')
ph = ph.resize((int(ph.width * 900 / ph.height), 900), Image.LANCZOS)
img.paste(ph, (264, -40))
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
edge = 640 * np.sqrt(np.clip(1 - ((H - yy) / 1000) ** 2, 0, 1))
lay = Image.new('RGBA', (W, H), AMBER + (255,))
lay.putalpha(Image.fromarray((np.clip(edge - xx + 0.5, 0, 1) * 255).astype(np.uint8)))
img.alpha_composite(lay)
d = ImageDraw.Draw(img)
logo = Image.open(G + 'site/logo.png').convert('RGBA')
logo = logo.resize((int(logo.width * 50 / logo.height), 50), Image.LANCZOS)
d.rounded_rectangle((52, 44, 52 + logo.width + 40, 44 + 50 + 28), 16, fill=WHITE)
img.alpha_composite(logo, (72, 58))
d = ImageDraw.Draw(img)
y = 186
for ln in ['Dementia Home', 'Care Services']:
    d.text((60, y), ln, font=serif(64), fill=WHITE)
    y += 74
y += 16
for ln in ['What They Include and', 'How to Arrange Them']:
    d.text((62, y), ln, font=ImageFont.truetype(F + 'FiraSans-Medium.ttf', 32), fill=WHITE)
    y += 42
btn = 'Support in your own home'
bf = ImageFont.truetype(F + 'FiraSans-SemiBold.ttf', 22)
bw = d.textlength(btn, font=bf)
d.rounded_rectangle((60, 566, 60 + bw + 64, 630), 10, fill=NAVY)
d.text((92, 581), btn, font=bf, fill=WHITE)
for ext, kw in (('webp', dict(quality=90)), ('jpg', dict(quality=92)), ('png', {})):
    img.convert('RGB').save(OUT + f'/dementia-home-care-services-featured.{ext}', **kw)


def save(im, name):
    im.convert('RGB').save(OUT + f'/{name}.webp', quality=90)
    im.convert('RGB').save(OUT + f'/{name}.png')


def badge(d, cx, cy, n, r=24, col=AMBER):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col)
    t = str(n)
    tw = d.textlength(t, font=fX(22))
    d.text((cx - tw / 2, cy - 18), t, font=fX(22), fill=WHITE)


# ---------- in-article 1: what a carer can help with ----------
im = canvas('A Helping Hand Through the Day', 'Everyday support a trained carer can bring into the home')
items = [
    ('Washing & dressing', 'Personal care with dignity'), ('Daily routine', 'Activities that feel meaningful'),
    ('Meals', 'Healthy food and help eating'), ('Around the house', 'Laundry and light tidying'),
    ('Medication', 'Reminders and support'), ('Moving safely', 'Help getting around the home'),
    ('Company', 'Chats, visits and gentle exercise'), ('Pet care', 'Looking after a loved pet'),
    ('Night support', 'For restless evenings and nights'),
]
cw, chh, gx, gy = 330, 152, 26, 22
x0 = (W - (3 * cw + 2 * gx)) // 2
for i, (t, s) in enumerate(items):
    x = x0 + (i % 3) * (cw + gx)
    y = 174 + (i // 3) * (chh + gy)
    card(im, (x, y, x + cw, y + chh))
    d = ImageDraw.Draw(im)
    d.ellipse((x + 24, y + 26, x + 74, y + 76), fill=TEAL_PALE)
    d.line((x + 37, y + 52, x + 46, y + 61, x + 62, y + 41), fill=(70, 140, 128), width=5, joint='curve')
    d.text((x + 92, y + 28), t, font=fX(23), fill=NAVY)
    for j, ln in enumerate(wrap(d, s, fS(18), cw - 116)):
        d.text((x + 92, y + 72 + j * 26), ln, font=fS(18), fill=GREY)
footnote(im, 'Every plan is built around the person, so no two look the same.', 742)
save(im, 'dementia-home-care-what-carers-help-with')

# ---------- in-article 2: levels of support ----------
im = canvas('Finding the Right Level of Support', 'Start small and add more as needs grow')
types = [
    ('Visiting care', 'From 30 minutes up to a full day', 'Help with getting up, meals or medication, or a reassuring check-in.', TEAL, NAVY),
    ('Overnight care', 'Awake or on call through the night', 'Reassurance when evenings bring confusion, so family can sleep.', (92, 150, 160), WHITE),
    ('Live in care', 'Support around the clock', 'One carer who knows their habits, preferences and triggers.', NAVY, WHITE),
    ('Respite care', 'A day, a weekend or longer', 'A proper break for the family carer, with company for their loved one.', AMBER, WHITE),
]
y = 176
for i, (t, when, body, col, fg) in enumerate(types):
    x = 110
    card(im, (x, y, W - 110, y + 118))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((x, y, x + 320, y + 118), 18, fill=col)
    d.rectangle((x + 290, y, x + 320, y + 118), fill=col)
    d.text((x + 24, y + 22), t, font=fX(25), fill=fg)
    d.text((x + 24, y + 70), when, font=fS(16), fill=fg)
    lines = wrap(d, body, fS(20), W - 110 - x - 370)
    for j, ln in enumerate(lines):
        d.text((x + 350, y + 59 - len(lines) * 15 + j * 30), ln, font=fS(20), fill=GREY)
    y += 136
footnote(im, 'Many families combine these and change the mix over time.', 742)
save(im, 'dementia-home-care-levels-of-support')

# ---------- in-article 3: signs ----------
im = canvas('Signs It May Be Time for Extra Support', 'No need to wait for a crisis')
signs = [
    'Skipped meals, too little to drink or weight loss',
    'Medication forgotten or taken twice',
    'Hob, taps or doors left on or open',
    'Getting lost, even in familiar places',
    'Personal hygiene slipping or unsuitable clothing',
    'More anxiety, withdrawal or evening restlessness',
    'A family carer who is exhausted or isolated',
]
y = 172
for i, s in enumerate(signs):
    last = i == len(signs) - 1
    card(im, (180, y, W - 180, y + 64), fill=(255, 246, 236) if last else WHITE, outline=AMBER if last else (222, 234, 231))
    d = ImageDraw.Draw(im)
    badge(d, 222, y + 32, i + 1, 20, NAVY if last else AMBER)
    d.text((262, y + 17), s, font=fB(22) if last else fS(22), fill=NAVY)
    y += 78
footnote(im, 'No diagnosis yet? Start with the GP: a diagnosis usually unlocks wider support.', 742)
save(im, 'dementia-home-care-signs-to-act')
print('done')
