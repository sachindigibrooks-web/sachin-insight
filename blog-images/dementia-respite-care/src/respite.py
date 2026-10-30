import sys
from PIL import ImageOps

src = open(sys.argv[1] + '/greenwood.py').read()
exec(src.split('# ---------- featured')[0])        # palette, fonts, helpers
exec('def canvas' + src.split('def canvas')[1].split('# ---------- in-article 1')[0])  # canvas + footnote
OUT = sys.argv[2]
serif = lambda s: ImageFont.truetype(F + 'DMSerifDisplay-Regular.ttf', s)

# ---------- featured: homepage hero style ----------
img = Image.new('RGBA', (W, H), BG + (255,))
ph = Image.open(G + 'ph/respite.jpg').convert('RGB')
ph = ph.resize((int(ph.width * 830 / ph.height), 830), Image.LANCZOS)
img.paste(ph, (W - ph.width + 60, -15))
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
edge = 680 * np.sqrt(np.clip(1 - ((H - yy) / 1000) ** 2, 0, 1))
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
for ln in ['Dementia', 'Respite Care']:
    d.text((60, y), ln, font=serif(80), fill=WHITE)
    y += 88
y += 16
for ln in ['Options, 2026 Costs and', 'How to Arrange It']:
    d.text((62, y), ln, font=ImageFont.truetype(F + 'FiraSans-Medium.ttf', 33), fill=WHITE)
    y += 43
btn = 'A UK guide for family carers'
bf = ImageFont.truetype(F + 'FiraSans-SemiBold.ttf', 22)
bw = d.textlength(btn, font=bf)
d.rounded_rectangle((60, 572, 60 + bw + 64, 636), 10, fill=NAVY)
d.text((92, 587), btn, font=bf, fill=WHITE)
for ext, kw in (('webp', dict(quality=90)), ('jpg', dict(quality=92)), ('png', {})):
    img.convert('RGB').save(OUT + f'/dementia-respite-care-featured.{ext}', **kw)


def save(im, name):
    im.convert('RGB').save(OUT + f'/{name}.webp', quality=90)
    im.convert('RGB').save(OUT + f'/{name}.png')


# ---------- in-article 1: respite options compared ----------
im = canvas('Where Can a Respite Break Happen?', 'Four ways to get time off while your loved one is looked after')
opts = [
    ('In their own home', NAVY, WHITE, 'Best for familiar routine',
     ['Carer visits or stays in the house', 'Meals, bedtime and habits stay the same', 'From 30 minutes to several weeks']),
    ('At a day centre', (92, 150, 160), WHITE, 'Best for company',
     ['Structured activities at set times', 'Suits people who enjoy groups', 'Crowds or travel can be hard for some']),
    ('A short care home stay', AMBER, WHITE, 'Best for nursing needs',
     ['Staff on site day and night', 'Helps with longer breaks', 'New surroundings can unsettle']),
    ('Friends and relatives', TEAL, NAVY, 'Best for short gaps',
     ['Useful for an hour or two', 'Hard to rely on for nights', 'Or for personal care']),
]
cw, gap = 255, 20
x0 = (W - (4 * cw + 3 * gap)) // 2
for i, (t, col, fg, tag, pts) in enumerate(opts):
    x = x0 + i * (cw + gap)
    card(im, (x, 180, x + cw, 700))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((x, 180, x + cw, 290), 18, fill=col)
    d.rectangle((x, 260, x + cw, 290), fill=col)
    yy0 = 196
    for ln in wrap(d, t, fX(23), cw - 40):
        d.text((x + 22, yy0), ln, font=fX(23), fill=fg); yy0 += 34
    pill(d, x + 20, 312, tag, fB(15), NAVY, (255, 236, 214), 12, 32)
    y = 372
    for p in pts:
        d.ellipse((x + 22, y + 11, x + 33, y + 22), fill=AMBER)
        for ln in wrap(d, p, fS(21), cw - 66):
            d.text((x + 44, y), ln, font=fS(21), fill=GREY); y += 31
        y += 30
footnote(im, 'Source: NHS guidance on carer breaks and respite care.', 742)
save(im, 'dementia-respite-options-compared')

# ---------- in-article 2: 2026 costs ----------
im = canvas('Respite Prices at a Glance', 'What UK families typically pay this year')
rows = [
    ('Carer visits at home', '£26 to £38 an hour', 'Many families pay around £30 to £32. Specialist dementia support can reach £40+.'),
    ('A four hour afternoon off', '£120 to £128', 'Based on £30 to £32 an hour.'),
    ('A week in a care home', '£700 to £800 a week', 'Average cited by the NHS. Varies by home and care needed.'),
    ('Nights or a carer living in', 'Ask for a quote', 'Live in can be better value than many separate visits.'),
]
y = 178
for t, price, note in rows:
    card(im, (90, y, W - 90, y + 112))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((90, y, 98, y + 112), 4, fill=AMBER)
    d.text((126, y + 20), t, font=fX(25), fill=NAVY)
    d.text((126, y + 64), note, font=fS(17), fill=GREY)
    pw = d.textlength(price, font=fB(30))
    d.text((W - 126 - pw, y + 34), price, font=fB(30), fill=AMBER if price[0] == '£' else NAVY)
    y += 132
card(im, (90, y + 6, W - 90, y + 74), fill=TEAL_PALE, outline=TEAL)
d = ImageDraw.Draw(im)
msg = "Reality check: the Homecare Association's 2026/27 minimum price benchmark is £34.42 an hour."
tw = d.textlength(msg, font=fB(19))
d.text(((W - tw) / 2, y + 28), msg, font=fB(19), fill=NAVY)
save(im, 'dementia-respite-care-costs-2026')

# ---------- in-article 3: how to arrange ----------
im = canvas('Your Respite Plan in 5 Steps', 'Plan the break before you need it')
steps = [
    ('Get assessed', 'Ask the council to assess your relative’s needs, and yours as a carer.'),
    ('Pick the type of break', 'Regular afternoons, a run of nights, a holiday or a backup plan.'),
    ('Free home visit', 'Greenwood meets your relative and gets to know their routine.'),
    ('Start small', 'Short visits first, so the carer becomes a familiar face.'),
    ('Check in and adjust', 'Share what worked and fine-tune the plan for next time.'),
]
y = 176
for i, (t, body) in enumerate(steps):
    card(im, (150, y, W - 150, y + 98))
    d = ImageDraw.Draw(im)
    d.ellipse((176, y + 21, 232, y + 77), fill=AMBER)
    n = str(i + 1)
    nw = d.textlength(n, font=fX(28))
    d.text((204 - nw / 2, y + 22), n, font=fX(28), fill=WHITE)
    d.text((262, y + 16), t, font=fX(25), fill=NAVY)
    d.text((262, y + 58), body, font=fS(18), fill=GREY)
    if i < 4:
        d.line((204, y + 98, 204, y + 116), fill=TEAL, width=3)
    y += 116
save(im, 'how-to-arrange-dementia-respite-care')
print('done')
