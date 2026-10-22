import json, sys, re
from PIL import Image
out = sys.argv[1]; rep = json.load(open(f'{out}/_qa.json'))
def lum(c):
    c = [v/255 for v in c[:3]]; c = [v/12.92 if v <= .03928 else ((v+.055)/1.055)**2.4 for v in c]
    return .2126*c[0] + .7152*c[1] + .0722*c[2]
def rgb(s): return tuple(int(float(v)) for v in re.findall(r'[\d.]+', s)[:3])
ok_all = True
for id, r in rep.items():
    im = Image.open(f'{out}/{id}.png'); bg = Image.open(f'{out}/_bg_{id}.png').convert('RGB')
    print(f'\n== {id}  {im.size[0]}x{im.size[1]} (expected {int(r["W"])}x{int(r["H"])})')
    fails = []
    if im.size != (int(r['W']), int(r['H'])): fails.append('size mismatch')
    if len(r['fonts']) > 2: fails.append(f'fonts {r["fonts"]}')
    ctas = [i for i in r['items'] if i['tag'] == 'cta']
    if len(ctas) > 1: fails.append('more than one CTA')
    for i in r['items']:
        b = i['box']; note = []
        if not i['safe']: fails.append(f'outside safe zone: {i["txt"]!r}')
        if i['tag'] == 'logo': continue
        if i['size'] < 16: fails.append(f'font <16px: {i["txt"]!r}')
        if i['lines'] and max(i['lines']) > 7: fails.append(f'>7 words/line: {i["txt"]!r}')
        if i['tag'] == 'cta':
            if b['h'] < 44: fails.append('CTA <44px')
            if b['x'] + b['w'] < r['W'] * .6: fails.append('CTA not bottom-right')
            cr = (lum(rgb(i['bg'])) + .05) / (lum(rgb(i['color'])) + .05); cr = max(cr, 1/cr)
        else:
            crop = bg.crop((int(b['x']), int(b['y']), int(b['x']+b['w']), int(b['y']+b['h'])))
            ls = sorted(lum(px) for px in crop.getdata()); worst = ls[int(len(ls)*.95)]
            fg = lum(rgb(i['color'])); cr = (max(fg, worst)+.05)/(min(fg, worst)+.05)
        if cr < 4.5: fails.append(f'contrast {cr:.1f} < 4.5: {i["txt"]!r}')
        print(f'  {i["tag"]:4} {i["size"]:5.0f}px contrast {cr:5.1f}  words/line {i["lines"]}  {i["txt"]!r}')
    print(f'  fonts {r["fonts"]}   text area {r["textRatio"]*100:.1f}%')
    if id.startswith('p2') and r['textRatio'] >= .2: fails.append('text >=20% on FB image')
    print('  RESULT:', 'PASS' if not fails else 'FAIL ' + '; '.join(fails)); ok_all &= not fails
print('\nALL PASS' if ok_all else '\nSOME FAILED')
