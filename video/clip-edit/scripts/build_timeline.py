"""Roman-Hinglish captions on Whisper word timings, caption pages and named beats (shared by visuals and mix)."""
import json
raw = json.load(open('scripts/words.json'))
roman = """White|Hat|SEO.|The|boring|way,|but|the|powerful|way.|Isme|hai|kya?|Jaise|ki|genuine|content|likho,|quality|backlinks|banao,|aur|user|ke|experience|ko|improve|karo.|I|know|yaar,|pata|hai,|boring|lagta|hai.|But,|ek|example|suno.|Ek|blogger|tha,|Neil|Patel.|Usne|White|Hat|SEO|pe|kaam|kiya,|quality|content|likha,|user|ke|experience|ko|improve|kiya,|technical|SEO|kiya.|Aaj|uski|website|pe|millions|of|users|aa|rahe|hain.|Think|of|it|like|this:|Black|Hat|SEO|game|ka|ek|cheat|code|hai.|But|ye|cheat|code|ban|hai.|Toh|White|Hat|SEO|aisi|skill|hai|jo|hamesha|kaam|aayegi.""".split('|')
# Whisper heard "Think of like this" (4 words); the speaker says "Think of it like this" -> split "of" to keep 5 caption words
of = raw[75]
mid = round((of['s'] + raw[76]['s']) / 2, 3)
raw = raw[:75] + [{'w': 'of', 's': of['s'], 'e': mid}, {'w': 'it', 's': mid, 'e': raw[76]['s']}] + raw[76:]
assert len(roman) == len(raw), (len(roman), len(raw))
words = [{'t': r, 's': w['s'], 'e': w['e']} for r, w in zip(roman, raw)]
DUR = 41.04
I = lambda k: words[k]['s']
B = {'hat': I(1), 'seo': I(2), 'boring': I(4), 'but0': I(6), 'powerful': I(8), 'isme': I(10), 'genuine': I(15), 'quality': I(18),
     'backlinks': I(19), 'aur': I(21), 'user': I(22), 'iknow': I(28), 'boring2': I(33), 'but': I(36), 'example': I(38), 'ek': I(40),
     'blogger': I(41), 'neil': I(43), 'usne': I(45), 'wh2': I(46), 'quality2': I(52), 'user2': I(55), 'technical': I(61),
     'aaj': I(64), 'website': I(66), 'million': I(68), 'users': I(70), 'think': I(74), 'black': I(79), 'game': I(82),
     'cheat': I(85), 'but2': I(88), 'cheat2': I(90), 'ban': I(92), 'toh': I(94), 'wh3': I(95), 'skill': I(99),
     'hamesha': I(102), 'end': words[-1]['e']}
pages, cur = [], []
for i, w in enumerate(words):
    cur.append(w)
    nx = words[i + 1] if i + 1 < len(words) else None
    gap = nx['s'] - w['e'] if nx else 9
    if len(cur) >= 3 or w['t'][-1] in '.,?:' or gap > 0.3 or nx is None:
        pages.append({'s': cur[0]['s'], 'e': round(min(w['e'] + 0.2, nx['s']) if nx else DUR, 3), 'words': cur}); cur = []
json.dump({'duration': DUR, 'words': words, 'pages': pages, 'beats': B}, open('src/timeline.json', 'w'), ensure_ascii=False, indent=1)
print(len(words), 'words', len(pages), 'pages')
