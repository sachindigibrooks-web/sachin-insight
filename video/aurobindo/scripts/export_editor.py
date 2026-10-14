"""Builds editor/data/ for the timeline editor (editor/index.html).
Run after `STEMS=1 python3 scripts/mix2.py`. Reads src/timeline.json, src/scenes.tsx and out/stems/*,
writes project.json (tracks + waveform peaks), stem mp3s, one mp3 per SFX cue, a filmstrip sprite and a muted proxy video."""
import json, os, pickle, re, subprocess
import numpy as np
import pyloudnorm as pyln
import soundfile as sf

OUT = 'editor/data'
SR = 48000
PPS = 100  # waveform peaks per second
tl = json.load(open('src/timeline.json'))
B = tl['beats']
DUR = tl['duration']
os.makedirs(f'{OUT}/sfx', exist_ok=True)
os.makedirs(f'{OUT}/stems', exist_ok=True)


def ev(expr):
    """Evaluate a time expression from scenes.tsx such as `B.yogi + 0.25`."""
    return round(float(eval(re.sub(r'B\.(\w+)', lambda m: repr(B[m.group(1)]), expr), {})), 3)


def attr(line, name):
    m = re.search(name + r'=\{([^{}]+)\}', line) or re.search(name + r'="([^"]*)"', line)
    return m.group(1) if m else None


def peaks(y):
    y = np.abs(y if y.ndim == 1 else y.max(1))
    hop = SR // PPS
    n = int(np.ceil(len(y) / hop))
    y = np.pad(y, (0, n * hop - len(y)))
    return [round(float(v), 3) for v in y.reshape(n, hop).max(1)]


def mp3(y, path, br='128k'):
    tmp = path + '.wav'
    sf.write(tmp, y.astype(np.float32), SR, subtype='FLOAT')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-c:a', 'libmp3lame', '-b:a', br, path], check=True)
    os.remove(tmp)


# ---------------- visual tracks, read from scenes.tsx (times are the authored ones; <In> ranges give on-screen ends)
src = open('src/scenes.tsx').read().splitlines()
SCENE_OF = lambda t: next((s['id'] for s in tl['scenes'] if s['s'] <= t < s['e']), tl['scenes'][-1]['id'])
items = {'broll': [], 'photo': [], 'title': [], 'note': [], 'gfx': []}
stack = []
for ln, line in enumerate(src, 1):
    m = re.search(r'<In s=\{([^{}]+)\} e=\{([^{}]+)\}>', line)
    if m:
        stack.append((ev(m.group(1)), ev(m.group(2))))
    end_in = stack[-1][1] if stack else DUR
    at = attr(line, 'at')
    if at and re.search(r'\b[a-z]\b', re.sub(r'B\.\w+', '', at)):
        at = None  # loop variable (montage / ladder steps): added explicitly below
    if '<Clip ' in line and at and attr(line, 'src') and '"' in line.split('src=')[1][:2]:
        s, e = ev(at), ev(attr(line, 'until'))
        items['broll'].append(dict(label=attr(line, 'src').split('/')[-1], src=attr(line, 'src'), s=s, e=e,
                                   trim=ev(attr(line, 'trim') or '0'), grade=attr(line, 'grade'), alpha='transparent' in line, line=ln))
    elif '<Print ' in line:
        items['photo'].append(dict(label=attr(line, 'caption') or 'photo', src=attr(line, 'src'), s=ev(at), e=end_in, line=ln))
    elif '<Big ' in line and re.search(r"\['", line):
        words = re.findall(r"\['([^']+)', ([^,\]]+)", line)
        ts = [ev(w[1]) for w in words]
        items['title'].append(dict(label=' '.join(w[0] for w in words), s=min(ts), e=end_in, words=[[w[0], t] for w, t in zip(words, ts)], line=ln))
    elif '<Hand ' in line and at and re.search(r'>([^<{]+)</Hand>', line):
        items['note'].append(dict(label=re.search(r'>([^<{]+)</Hand>', line).group(1).strip(), s=ev(at), e=end_in, line=ln))
    elif '<LowerThird ' in line:
        items['gfx'].append(dict(label='Lower third: ' + attr(line, 'name'), s=ev(at), e=ev(attr(line, 'out')) + 0.5, line=ln))
    elif '<Mark ' in line:
        d = ev(attr(line, 'dur') or '0.4')
        items['gfx'].append(dict(label='Marker stroke', s=ev(at), e=round(ev(at) + d, 3), line=ln))
    elif '<Burn ' in line:
        d = ev(attr(line, 'dur') or '0.7')
        items['gfx'].append(dict(label='Light leak', s=ev(at), e=round(ev(at) + d, 3), line=ln))
    if '</In>' in line:
        stack.pop()

# generated elements that scenes.tsx builds in loops
montage = ['crowd', 'timer', 'rubeyes', 'rainnight']
cut = (B['abSocho'] - B['kitne']) / 4
for i, n in enumerate(montage):
    items['broll'].append(dict(label=f'{n}.mp4', src=f'v/{n}.mp4', s=round(B['kitne'] + i * cut, 3), e=round(B['kitne'] + (i + 1) * cut, 3), trim=0, grade='night', alpha=False, line=37))
items['broll'].append(dict(label='rainnight.mp4 (freeze)', src='v/rainnight.mp4', s=B['abSocho'], e=4.95, trim=0, grade='night', alpha=False, line=41))
steps = [('MATTER', 'mountain', B['matter'], B['life']), ('LIFE', 'forest', B['life'], B['mind']), ('MIND', 'rainnight', B['mind'], 21.44)]
for name, clip, s, e in steps:
    items['broll'].append(dict(label=f'{clip}.mp4', src=f'v/{clip}.mp4', s=round(s - 0.05, 3), e=round(e - 0.05 if name != 'MIND' else e, 3), trim=0, grade='warm', alpha=False, line=142))
    items['title'].append(dict(label=name, s=round(s, 3), e=round(e - 0.05, 3), words=[[name, s]], line=150))
items['broll'].append(dict(label='pensive.webm (alpha)', src='v/pensive.webm', s=round(B['mind'] - 0.05, 3), e=21.44, trim=0, grade='warm', alpha=True, line=146))
items['note'] += [dict(label='Noise words x12', s=B['kitne'], e=B['abSocho'], line=46),
                  dict(label='Overthink words', s=B['overthink'], e=21.44, line=164),
                  dict(label='Thought words', s=B['thoughts2'], e=B['phenk'], line=247)]
# elements that leave earlier than their <In> range (conditional render / fade-out in scenes.tsx)
EARLY = {72: B['yogi'] + 0.15, 127: B['matter'] - 0.05, 128: B['matter'] - 0.05}
for k in items:
    for x in items[k]:
        x['e'] = round(min(DUR, EARLY.get(x['line'], x['e']) if x['line'] in EARLY and k != 'broll' else x['e']), 3)
    items[k].sort(key=lambda x: x['s'])
    for i, x in enumerate(items[k]):
        x['id'] = f'{k}{i + 1}'
        x['scene'] = SCENE_OF(x['s'])

probe = lambda f: round(float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f],
                                              capture_output=True, text=True).stdout), 3)
for x in items['broll']:
    x['srcDur'] = probe('public/' + x['src'])

# ---------------- audio
meter = pyln.Meter(SR)
stems = {}
pre = 0
for k in ['voice', 'music', 'tanpura']:
    y, _ = sf.read(f'out/stems/{k}.wav')
    pre = pre + y
    mp3(y, f'{OUT}/stems/{k}.mp3')
    stems[k] = peaks(y)
sfx_stem, _ = sf.read('out/stems/sfx.wav')
pre = pre + sfx_stem
master_gain = round(-14.3 - meter.integrated_loudness(pre), 2)
sfx_gain = np.load('out/stems/sfx_gain.npy')  # linear, at 100/s

cues = pickle.load(open('out/stems/cues.pkl', 'rb'))
sfx_items = []
for i, c in enumerate(cues):
    base = re.sub(r'[^a-z0-9_]', '', c['name'].split(' ')[0])
    f = f'sfx/{i + 1:02d}_{base}.mp3'
    mp3(c['audio'], f'{OUT}/{f}', '96k')
    sfx_items.append(dict(id=f'sfx{i + 1}', label=c['name'], file=f, s=c['at'], e=round(c['at'] + len(c['audio']) / SR, 3), gain=c['gain'],
                          len=round(len(c['audio']) / SR, 3), peaks=peaks(c['audio']), scene=SCENE_OF(c['at']),
                          src_start=c['start'], rate=c['rate'], fin=c['fin'], fout=c['fout']))

project = dict(
    title='Sri Aurobindo: Consciousness', fps=30, width=1080, height=1920, duration=DUR,
    render='out/Sri_Aurobindo_Consciousness.mp4', masterGain=master_gain, pps=PPS,
    scenes=tl['scenes'], beats=B, pages=tl['pages'],
    video=[dict(key='broll', name='B-roll', items=items['broll']), dict(key='photo', name='Photos', items=items['photo']),
           dict(key='gfx', name='Graphics', items=items['gfx']), dict(key='title', name='Titles', items=items['title']),
           dict(key='note', name='Hand notes', items=items['note'])],
    audio=[dict(key='voice', name='Voice', file='stems/voice.mp3', peaks=stems['voice']),
           dict(key='music', name='Music', file='stems/music.mp3', peaks=stems['music'], note='Mixkit "Vastness", offset 15.84 s, ducked'),
           dict(key='tanpura', name='Tanpura', file='stems/tanpura.mp3', peaks=stems['tanpura'])],
    sfx=sfx_items, sfxBus=[round(float(v), 4) for v in sfx_gain],
)
json.dump(project, open(f'{OUT}/project.json', 'w'), separators=(',', ':'))

# ---------------- proxy video (muted; audio comes from the stems) and filmstrip
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'out/Sri_Aurobindo_Consciousness.mp4', '-an', '-vf', 'scale=540:960', '-c:v', 'libx264',
                '-crf', '27', '-preset', 'slow', '-g', '15', '-movflags', '+faststart', f'{OUT}/proxy.mp4'], check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'out/Sri_Aurobindo_Consciousness.mp4', '-an', '-vf', 'scale=540:960', '-c:v', 'libvpx-vp9', '-b:v', '0',
                '-crf', '40', '-row-mt', '1', '-deadline', 'good', '-cpu-used', '3', '-g', '15', f'{OUT}/proxy.webm'], check=True)  # for browsers without H.264
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'out/Sri_Aurobindo_Consciousness.mp4', '-vf', 'fps=2,scale=72:128,tile=20x6',
                '-frames:v', '1', '-q:v', '4', f'{OUT}/filmstrip.jpg'], check=True)
print('broll', len(items['broll']), 'photo', len(items['photo']), 'title', len(items['title']), 'note', len(items['note']),
      'gfx', len(items['gfx']), 'sfx', len(sfx_items), 'masterGain', master_gain)
