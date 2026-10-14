# Roman-Hinglish captions aligned to Whisper timings + scene windows + named beats (shared by visuals and mix).
import json
raw = json.load(open('scripts/words_raw.json'))
roman = """Ek|second|ruko...|abhi|dimaag|mein|kitne|thoughts|chal|rahe|hain?|Ab|socho...|inhe|dekh|kaun|raha|hai?|Freedom|fighter|se|yogi|bane|Sri|Aurobindo|ki|philosophy|ki|chaabi|yahi|sawaal|hai.|Unke|hisaab|se|consciousness|ek|seedhi|hai.|Neeche|Matter...|phir|Life...|phir|Mind,|jahan|hum|atke|hain,|overthink|karte|hue.|Par|Mind|aakhri|step|nahi.|Upar|hai|Supermind,|_|chetna|jo|sochti|nahi...|seedha|jaanti|hai.|Insaan|final|nahi,|transitional|being|hai.|1908|_|mein|ek|yogi|ne|unse|kaha,|baitho,|socho|mat,|bas|mind|ko|dekho.|Thoughts|aayein,|toh|bahar|phenk|do.|Teen|din|mein|mind|shaant|ho|gaya.|Aaj|bas|ek|minute,|apne|thoughts|ko|dekho.|Kyunki|jo|dekh|raha|hai...|wahi|aap|ho.|All|life|is|Yoga.|_|_|_|Follow|karo.""".split('|')
assert len(roman) == len(raw), (len(roman), len(raw))
words = []
for r, w in zip(roman, raw):
    if r == '_':
        words[-1]['e'] = w['e']; continue
    words.append({'t': r, 's': w['s'], 'e': w['e']})
idx = {}
def at(tok, n=1):
    c = 0
    for w in words:
        if w['t'].strip('.,?!').lower() == tok.lower():
            c += 1
            if c == n: return w['s']
    raise KeyError(tok)
DUR = 53.5
cuts = [('hook', 0), ('intro', at('Freedom')), ('ladder', at('Unke')), ('super', at('Par')), ('story', at('1908')),
        ('practice', at('Aaj')), ('end', at('All'))]
scenes = [{'id': n, 's': round(max(0, s - 0.15), 2), 'e': round((cuts[i + 1][1] - 0.15) if i + 1 < len(cuts) else DUR, 2)} for i, (n, s) in enumerate(cuts)]
B = {k: round(v, 3) for k, v in {
    'kitne': at('kitne'), 'thoughts': at('thoughts'), 'abSocho': at('Ab'), 'dekh': at('dekh'), 'kaun': at('kaun'),
    'freedom': at('Freedom'), 'yogi': at('yogi'), 'sri': at('Sri'), 'chaabi': at('chaabi'), 'sawaal': at('sawaal'),
    'consciousness': at('consciousness'), 'seedhi': at('seedhi'), 'matter': at('Matter'), 'life': at('Life'),
    'mind': at('Mind'), 'atke': at('atke'), 'overthink': at('overthink'), 'par': at('Par'), 'aakhri': at('aakhri'),
    'upar': at('Upar'), 'supermind': at('Supermind'), 'sochti': at('sochti'), 'jaanti': at('jaanti'),
    'insaan': at('Insaan'), 'transitional': at('transitional'), 'y1908': at('1908'), 'baitho': at('baitho'),
    'soChoMat': at('socho', 2), 'dekho': at('dekho'), 'thoughts2': at('Thoughts', 2), 'phenk': at('phenk'),
    'teen': at('Teen'), 'shaant': at('shaant'), 'aaj': at('Aaj'), 'minute': at('minute'), 'kyunki': at('Kyunki'),
    'joDekh': at('dekh', 2), 'wahi': at('wahi'), 'aap': at('aap'), 'all': at('All'), 'yoga': at('Yoga'),
    'follow': at('Follow'), 'end': words[-1]['e']}.items()}
pages, cur = [], []
for i, w in enumerate(words):
    cur.append(w)
    nx = words[i + 1] if i + 1 < len(words) else None
    gap = nx['s'] - w['e'] if nx else 9
    if len(cur) >= 3 or w['t'][-1] in '.,?' or gap > 0.35 or nx is None:
        pages.append({'s': cur[0]['s'], 'e': round(min(w['e'] + 0.25, nx['s']) if nx else w['e'] + 0.8, 2), 'words': cur}); cur = []
json.dump({'duration': DUR, 'words': words, 'pages': pages, 'scenes': scenes, 'beats': B}, open('src/timeline.json', 'w'), ensure_ascii=False, indent=1)
for s in scenes: print(s)
