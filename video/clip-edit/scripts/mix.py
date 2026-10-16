"""Mix for the White Hat SEO clip (same audio for the YouTube and Shorts versions).
Voice = the camera mic, cleaned. Music = "Hip Hop 02" (Mixkit), ducked under speech, filtered for the black-hat bit, cut dead on
"But ye cheat code ban hai" so the BANNED hit lands in silence, back on "Toh". SFX are real recordings (Mixkit), placed on words.
Target -14 LUFS integrated (YouTube and Shorts both normalise there)."""
import json, subprocess
import numpy as np
import librosa
import pyloudnorm as pyln
import soundfile as sf
from scipy import signal

SR = 48000
tl = json.load(open('src/timeline.json'))
B = tl['beats']
DUR = tl['duration']
N = int(DUR * SR)
t = np.arange(N) / SR
meter = pyln.Meter(SR)
db = lambda x: 10 ** (x / 20)
auto = lambda pts: db(np.interp(t, *zip(*pts)))

# ---- voice: rumble out, light broadband denoise, a little less boxiness, presence, gentle de-ess and levelling
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'public/clip.mp4', '-vn', '-af',
                'highpass=f=80,afftdn=nr=8:nf=-46:tn=1,equalizer=f=280:t=q:w=1.2:g=-2.5,equalizer=f=3400:t=q:w=1.0:g=2,'
                'equalizer=f=11000:t=h:w=0.7:g=1.5,deesser=i=0.35,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=140:makeup=2',
                '-ar', str(SR), '-ac', '1', 'audio/voice_proc.wav'], check=True)
v, _ = sf.read('audio/voice_proc.wav')
voice = np.zeros(N)
voice[:min(N, len(v))] = v[:N]
voice *= db(-16 - meter.integrated_loudness(voice))
voice_st = np.stack([voice, voice], 1)

env = np.sqrt(np.clip(signal.sosfilt(signal.butter(2, 10, 'low', fs=SR, output='sos'), voice ** 2), 0, None))
act = signal.decimate((env > db(-36)).astype(float), 48)
g, dk = 0.0, np.zeros_like(act)
for i, x in enumerate(act):
    g = (np.exp(-1 / 25) * g + (1 - np.exp(-1 / 25)) * x) if x > g else (np.exp(-1 / 300) * g + (1 - np.exp(-1 / 300)) * x)
    dk[i] = g
duck = np.interp(np.arange(N), np.arange(len(dk)) * 48, dk)

# ---- music
m, _ = librosa.load('audio/music/hiphop02.mp3', sr=SR, mono=False)
m = m.T
music = np.zeros((N, 2))
seg = m[:N]
music[:len(seg)] = seg
music *= db(-20 - meter.integrated_loudness(music[:int(30 * SR)]))
lp = np.stack([signal.sosfiltfilt(signal.butter(4, 700, 'low', fs=SR, output='sos'), music[:, c]) for c in range(2)], 1)
w = np.interp(t, [0, B['black'] - 0.1, B['black'], B['but2'], B['toh'], DUR], [0, 0, 1, 1, 0, 0])  # dark, muffled for the black-hat bit
music = music * (1 - w)[:, None] + lp * w[:, None]
music *= auto([(0, -40), (0.15, 0), (B['but2'] - 0.05, 0), (B['but2'] + 0.25, -60), (B['toh'] - 0.1, -60), (B['toh'] + 0.15, 0),
               (DUR - 0.5, 0), (DUR, -50)])[:, None]
music *= db(-7 * duck)[:, None]

# ---- SFX
cache = {}


def S(name):
    if name not in cache:
        y, _ = librosa.load(f'audio/sfx/{name}.mp3', sr=SR, mono=False)
        y = y.T if y.ndim == 2 else np.stack([y, y], 1)
        a = np.abs(y).mean(1)
        cache[name] = y * db(-18) / (np.sqrt((y[a > a.max() * 0.05] ** 2).mean()) + 1e-9)
    return cache[name]


bus = np.zeros((N, 2))
CUES = []


def put(at, name, gdb, start=0.0, dur=None, fin=0.0, fout=0.05):
    y = S(name)[int(start * SR):]
    if dur is not None: y = y[:int(dur * SR)]
    y = y.copy()
    if fin: k = min(len(y), int(fin * SR)); y[:k] *= np.linspace(0, 1, k)[:, None]
    if fout: k = min(len(y), int(fout * SR)); y[-k:] *= np.linspace(1, 0, k)[:, None]
    s = int(max(0, at) * SR); e = min(N, s + len(y))
    if e > s:
        bus[s:e] += y[:e - s] * db(gdb)
        CUES.append((round(at, 2), name, gdb))


# hook: a low hit under the first word, a pop as SEO lands
put(0.0, 'heart_impact', -17)
put(B['seo'] - 0.05, 'msg_pop', -22)
put(B['but0'] - 0.05, 'pencil', -19)                 # red strike through "boring"
put(B['powerful'] - 0.05, 'sparkle_whoosh', -24)
put(B['isme'] - 0.12, 'whoosh_fast', -22)             # punch-in
# three pillars
put(5.64 - 0.2, 'whoosh_impact', -20, dur=1.6, fout=0.4)
put(B['genuine'] - 0.05, 'msg_pop', -24)
put(5.7, 'typing_fast', -27, start=1.0, dur=1.85, fin=0.1, fout=0.3)
put(B['quality'] - 0.18, 'swoosh_wind', -21)
for i in range(6):
    put(B['quality'] + 0.15 + i * 0.07, 'arcade_pop', -33 + (i % 2) * 2, dur=0.25, fout=0.05)
put(B['backlinks'] + 0.05, 'clock_fast', -30, dur=0.6, fout=0.1)  # dotted lines "ticking" in
put(B['aur'] - 0.15, 'whoosh_fast', -22)
put(B['user'] - 0.05, 'msg_pop', -24)
put(10.68, 'msg_pop', -28)
put(B['iknow'] - 0.15, 'swoosh_wind', -23)            # back to camera
put(B['but'] - 0.42, 'whoosh_fast', -24, dur=0.4, fout=0.15)  # ends before "But" so the word stays clean
# Neil Patel
put(B['ek'] - 0.15, 'paper_slide', -18)
put(B['neil'] - 0.05, 'whoosh_fast', -24)
put(B['neil'] + 0.25, 'camera_vintage', -15)          # the print drops on the board
put(18.32, 'pencil', -21)
put(B['usne'] - 0.1, 'paper_slide', -21)
for k in ['wh2', 'quality2', 'user2', 'technical']:
    put(B[k] - 0.02, 'pencil', -19, start=0.05, dur=0.4)
    put(B[k] + 0.12, 'msg_pop', -28)
# millions
put(B['aaj'] - 0.2, 'whoosh_impact', -20, dur=1.6, fout=0.4)
put(B['million'] - 0.1, 'clock_fast', -24, dur=1.15, fout=0.1)  # counter rolling
put(B['million'] + 1.0, 'coin_jump', -18)
put(B['million'] + 1.02, 'achievement', -27, dur=1.5, fout=0.5)
# black hat = cheat code, banned
put(B['think'] - 0.12, 'whoosh_fast', -22)
put(B['black'] - 0.2, 'whoosh_deep_impact', -18)
put(B['game'] - 0.1, 'arcade_pop', -22)
for i in range(10):
    put(B['cheat'] + i * 0.09, 'type_hit', -30, dur=0.12, fout=0.03)  # code keys typed
put(B['ban'] - 0.03, 'game_over', -16)
put(B['ban'] - 0.02, 'impact_big', -18, dur=1.6, fout=0.6)
# close
put(B['toh'] - 0.18, 'swoosh_wind', -21)
put(B['skill'] - 0.05, 'magic_light', -25)
put(B['hamesha'], 'achievement', -26, dur=1.2, fout=0.4)

bus *= (db(2) * db(-3 * duck))[:, None]
mix = voice_st + music + bus
mix *= np.clip((DUR - t) / 0.35, 0, 1)[:, None]
sf.write('out/mix_premaster.wav', mix.astype(np.float32), SR, subtype='FLOAT')
print('voice', round(meter.integrated_loudness(voice_st), 1), 'music', round(meter.integrated_loudness(music), 1),
      'sfx', round(meter.integrated_loudness(bus), 1), 'mix', round(meter.integrated_loudness(mix), 1), 'cues', len(CUES))

# clarity: voice vs everything else in the speech band
band = signal.butter(4, [300, 4000], 'bandpass', fs=SR, output='sos')
vv = signal.sosfilt(band, voice); rr = signal.sosfilt(band, (music + bus).mean(1))
n = SR // 10
E = lambda x: 10 * np.log10((x[:len(x) // n * n].reshape(-1, n) ** 2).mean(1) + 1e-12)
ev, er = E(vv), E(rr); mk = ev > ev.max() - 20
print('voice margin median', round(float(np.median(ev[mk] - er[mk])), 1), 'dB, 5th pct', round(float(np.percentile(ev[mk] - er[mk], 5)), 1),
      'dB, worst', [(round(i / 10, 1), round(float(ev[i] - er[i]), 1)) for i in np.where(mk & (ev - er < 5))[0]][:8])
