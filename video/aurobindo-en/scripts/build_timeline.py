"""Word timings (Whisper on the assembled voice) aligned to the script's own spelling, caption pages, scene windows
and named beats. Beat names match the Hinglish cut so the visuals and the mix keep their structure."""
import difflib, json, re
import numpy as np
import librosa
from faster_whisper import WhisperModel

LINES = json.load(open('audio/takes/lines.json'))
script = ' '.join(l[0] for l in LINES).replace('nineteen oh eight', '1908')
toks = script.split()
key = lambda w: re.sub(r"[^a-z0-9']", '', w.lower())
y, _ = librosa.load('public/voice.wav', sr=16000)
segs, _ = WhisperModel('small.en', device='cpu', compute_type='int8').transcribe(
    y, language='en', word_timestamps=True, beam_size=5, initial_prompt=script)
heard = [w for s in segs for w in s.words]
hk = [key(w.word) for w in heard]
for i, h in enumerate(hk):  # Whisper writes the year as digits or words
    if h in ('nineteen', '1908'): hk[i] = '1908'
words = [None] * len(toks)
sm = difflib.SequenceMatcher(None, [key(t) for t in toks], hk, autojunk=False)
for a, b, n in sm.get_matching_blocks():
    for j in range(n):
        w = heard[b + j]
        words[a + j] = {'t': toks[a + j], 's': round(w.start, 3), 'e': round(w.end, 3)}
# words Whisper merged or dropped: spread them evenly between their known neighbours
i = 0
while i < len(words):
    if words[i] is None:
        j = i
        while j < len(words) and words[j] is None: j += 1
        s = words[i - 1]['e'] if i else 0.0
        e = words[j]['s'] if j < len(words) else s + 0.4 * (j - i)
        for k in range(i, j):
            words[k] = {'t': toks[k], 's': round(s + (e - s) * (k - i) / (j - i), 3), 'e': round(s + (e - s) * (k - i + 1) / (j - i), 3)}
        print('interpolated', toks[i:j])
        i = j
    i += 1
for a, b in zip(words, words[1:]):  # keep starts monotonic
    if b['s'] < a['s']: b['s'] = a['e']


def at(tok, n=1, after=0.0):
    c = 0
    for w in words:
        if key(w['t']) == key(tok) and w['s'] >= after:
            c += 1
            if c == n: return w['s']
    raise KeyError(tok)


DUR = round(words[-1]['e'] + 2.4, 2)
B = {'kitne': at('How'), 'thoughts': at('thoughts'), 'abSocho': at('Now'), 'kaun': at('who'), 'dekh': at('watching'),
     'freedom': at('freedom'), 'yogi': at('yogi'), 'sri': at('Sri'), 'sawaal': at('question'), 'chaabi': at('key'),
     'consciousness': at('consciousness'), 'seedhi': at('ladder'), 'matter': at('Matter'), 'life': at('Life'), 'mind': at('Mind'),
     'atke': at('stuck'), 'overthink': at('Overthinking'), 'par': at('But'), 'aakhri': at('last'), 'upar': at('Above'),
     'supermind': at('Supermind'), 'sochti': at('think'), 'jaanti': at('knows'), 'insaan': at('Humans'), 'transitional': at('transitional'),
     'y1908': at('1908'), 'baitho': at('Sit'), 'soChoMat': at("Don't"), 'dekho': at('watch'), 'thoughts2': at('thoughts', 2),
     'phenk': at('throw'), 'teen': at('three'), 'shaant': at('silent'), 'aaj': at('So', after=at('silent')), 'minute': at('minute'),
     'kyunki': at('Because'), 'joDekh': at('watching', 2), 'wahi': at("that's"), 'aap': at('you'), 'all': at('All'),
     'yoga': at('Yoga'), 'follow': at('Follow'), 'end': words[-1]['e']}
B = {k: round(v, 3) for k, v in B.items()}
cuts = [('hook', 0), ('intro', B['freedom'] - 0.25), ('ladder', at('He') - 0.15), ('super', B['par'] - 0.15),
        ('story', B['y1908'] - 0.3), ('practice', B['aaj'] - 0.15), ('end', B['all'] - 0.15)]
scenes = [{'id': n, 's': round(max(0, s), 2), 'e': round(cuts[i + 1][1] if i + 1 < len(cuts) else DUR, 2)} for i, (n, s) in enumerate(cuts)]
pages, cur = [], []
for i, w in enumerate(words):
    cur.append(w)
    nx = words[i + 1] if i + 1 < len(words) else None
    gap = nx['s'] - w['e'] if nx else 9
    if len(cur) >= 3 or w['t'][-1] in '.,?:' or w['t'].endswith('...') or gap > 0.3 or nx is None:
        pages.append({'s': cur[0]['s'], 'e': round(min(w['e'] + 0.25, nx['s']) if nx else w['e'] + 0.8, 2), 'words': cur}); cur = []
json.dump({'duration': DUR, 'words': words, 'pages': pages, 'scenes': scenes, 'beats': B}, open('src/timeline.json', 'w'), indent=1)
for s in scenes: print(s)
print('duration', DUR)
