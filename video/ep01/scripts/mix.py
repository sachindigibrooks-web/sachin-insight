"""Sound design + mix for Ep01.
Layers: processed voice (lead), music bed (Voxel Revolution, Kevin MacLeod, CC BY 4.0) with sidechain ducking
and section automation, and ~150 synthesized SFX cues placed on the same beats the visuals animate on.
Output: out/mix_premaster.wav (mastered to -14 LUFS / -1 dBTP afterwards with ffmpeg loudnorm)."""
import json, subprocess
import numpy as np
import librosa
import pyloudnorm as pyln
import soundfile as sf
from scipy import signal
import sfx
from sfx import SR

tl = json.load(open('src/timeline.json'))
B = tl['beats']
DUR = tl['duration']
N = int(DUR * SR)
meter = pyln.Meter(SR)


def db(x):
    return 10 ** (x / 20)


def load(path, mono=False):
    y, _ = librosa.load(path, sr=SR, mono=mono)
    return y


# ---------------------------------------------------------------- voice
# Cleanup chain: rumble HPF, de-mud, presence lift, gentle de-ess, leveling compression.
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'public/voice.mp3', '-af',
                'highpass=f=85,equalizer=f=280:t=q:w=1.2:g=-2.5,equalizer=f=3400:t=q:w=1.0:g=2.5,'
                'equalizer=f=7200:t=q:w=2:g=-2,equalizer=f=12000:t=h:w=0.7:g=1.5,'
                'acompressor=threshold=-20dB:ratio=3:attack=6:release=90:makeup=3',
                '-ar', str(SR), '-ac', '1', 'audio/voice_proc.wav'], check=True)
v, _ = sf.read('audio/voice_proc.wav')
voice = np.zeros(N)
voice[:min(N, len(v))] = v[:N]
voice *= db(-16 - meter.integrated_loudness(voice))  # lead sits at -16 LUFS before master
voice_st = np.stack([voice, voice], 1)

# Voice activity envelope for ducking (fast attack, slow release)
env = np.sqrt(signal.sosfilt(signal.butter(2, 12, 'low', fs=SR, output='sos'), voice ** 2).clip(0))
active = (env > db(-38)).astype(float)
att, rel = np.exp(-1 / (0.03 * SR)), np.exp(-1 / (0.30 * SR))
duck = np.zeros(N)
g = 0.0
dec = signal.decimate(active, 48)  # compute at 1 kHz for speed
dk = np.zeros_like(dec)
a1, r1 = np.exp(-1 / (0.03 * 1000)), np.exp(-1 / (0.35 * 1000))
for i, x in enumerate(dec):
    g = a1 * g + (1 - a1) * x if x > g else r1 * g + (1 - r1) * x
    dk[i] = g
duck = np.interp(np.arange(N), np.arange(len(dk)) * 48, dk)
duck_gain = db(-7.5 * duck)  # up to 7.5 dB under speech

# ---------------------------------------------------------------- music
m = load('audio/music/Voxel_Revolution.mp3')
m = m.T if m.ndim == 2 else np.stack([m, m], 1)
beats = librosa.beat.beat_track(y=librosa.to_mono(m.T), sr=SR, units='time')[1]
downbeats = beats[::4]


def next_db(pos):
    return float(downbeats[downbeats >= pos][0])


music = np.zeros((N, 2))


def place(start, end, offset, fade_in=0.0, fade_out=0.02):
    s, e = int(start * SR), int(end * SR)
    seg = m[int(offset * SR):int(offset * SR) + (e - s)].copy()
    n = len(seg)
    if fade_in:
        seg[:int(fade_in * SR)] *= np.linspace(0, 1, int(fade_in * SR))[:, None]
    seg[-int(fade_out * SR):] *= np.linspace(1, 0, int(fade_out * SR))[:, None]
    music[s:s + n] += seg


# A: hook through ZERO, with a tape-stop into silence
zero = B['zero']
place(0, zero - 0.25, 0.0)
ts_start, ts_len = zero - 0.25, 0.25
src = m[int(ts_start * SR):int((ts_start + 0.6) * SR)]
rate = np.linspace(1, 0.05, int(ts_len * SR))
pos = np.cumsum(rate)
tape = np.stack([np.interp(pos, np.arange(len(src)), src[:, c]) for c in range(2)], 1)
tape *= np.linspace(1, 0, len(tape))[:, None] ** 0.5
music[int(ts_start * SR):int(ts_start * SR) + len(tape)] += tape
# B: comes back on a downbeat at "Toh bhai"
back = B['year'] - 1.14  # "Toh" (23.12)
offB = next_db(zero)
endB = 38.0
place(back, endB, offB, fade_in=0.01, fade_out=0.03)
# C: fresh downbeat lands on the "Ek" impact after the riser
offC = next_db(offB + (endB - back))
place(endB, DUR, offC, fade_out=1.0)

# Section filter automation: muffled intro opening up, filtered build during "Ab ye hoga kaise", open at 38.0
lp_m = np.stack([signal.sosfiltfilt(signal.butter(4, 700, 'low', fs=SR, output='sos'), music[:, c]) for c in range(2)], 1)
w = np.zeros(N)
t = np.arange(N) / SR
w = np.where(t < 2.9, 1.0, w)
w = np.where((t >= 2.9) & (t < 3.6), 1 - (t - 2.9) / 0.7, w)
w = np.where((t >= 34.6) & (t < 36.4), (t - 34.6) / 1.8, w)
w = np.where((t >= 36.4) & (t < 38.0), 1.0, w)
music = music * (1 - w)[:, None] + lp_m * w[:, None]
music *= db(-23 - meter.integrated_loudness(music[: int(20 * SR)]))
music *= duck_gain[:, None]
# end fade
music *= np.clip((DUR - t) / 0.9, 0, 1)[:, None]

# ---------------------------------------------------------------- SFX cues
bus = np.zeros((N, 2))
cache = {}


def put(at, snd, gain_db, key=None):
    if key is not None:
        if key not in cache:
            cache[key] = snd()
        snd = cache[key]
    elif callable(snd):
        snd = snd()
    s = int(at * SR)
    if s < 0:
        snd, s = snd[-s:], 0
    e = min(N, s + len(snd))
    bus[s:e] += snd[: e - s] * db(gain_db)


# Scene transitions: alternate whoosh flavors, landing just before the cut
for i, sc in enumerate(tl['scenes'][1:]):
    f0, f1 = [(250, 3500), (400, 6000), (200, 2500)][i % 3]
    put(sc['s'] - 0.32, lambda: sfx.whoosh(0.5, f0, f1, 0.62, -0.9 if i % 2 else 0.9, 0.9 if i % 2 else -0.9), -11)

# HOOK
put(0.0, sfx.impact(1.4, 70, 0.6), -14)
for a in [0.02, 0.36, 0.56]:
    put(a, sfx.hit(0.25, 140), -15)
put(1.25, sfx.whoosh(0.4, 600, 5000, 0.7, 0, 0), -14)  # phone slides in
query = 'seo tips 2026'
for i in range(len(query)):
    put(B['typeStart'] + i / 16 + np.random.default_rng(i).uniform(-0.01, 0.01), sfx.key(i), -15)
for i in range(4):
    put(4.2 + i * 0.075, sfx.blip(900 + i * 220, 0.05), -24)
put(4.6, sfx.whoosh(0.5, 2000, 6000, 0.5, 0.3, -0.3), -26)
put(B['clickWord'], sfx.mouse_click, -10, 'mclick')
put(B['clickWord'] + 0.02, sfx.stamp, -9, 'stamp')

# NAHI
put(B['nahiNa'], sfx.hit(0.45, 95), -7)
put(B['nahiNa'] + 0.28, sfx.hit(0.45, 120), -8)
put(B['haan'] - 0.05, sfx.paper(0.5, 0.2), -12)
put(9.0, sfx.marker(0.2), -12)
put(9.2, sfx.marker(0.2), -12)

# AI
put(9.75, sfx.reverse_swell(0.4), -20)
for a in [10.24, 10.36, B['answer'] - 0.38, 11.74, 12.02]:
    put(a, sfx.pop, -18, 'pop')
put(B['answer'], sfx.ding(1046.5), -12)
put(B['answer'], sfx.hit(0.3, 160), -14)
put(B['aiMode'], sfx.blip(1400, 0.07), -16)
put(B['aiMode'] + 0.04, sfx.pop, -16, 'pop')
put(B['aiOverview'], sfx.blip(1700, 0.07), -16)
put(B['aiOverview'] + 0.04, sfx.pop, -16, 'pop')
put(B['hindi'], sfx.stamp, -9, 'stamp')
put(B['hindi'] + 0.03, sfx.sparkle(0.5), -18)

# ZERO
put(16.4, sfx.paper(0.55, -0.3), -12)
put(B['rank1'] + 0.45, sfx.stamp, -8, 'stamp')
put(19.3, sfx.marker(0.25), -13)
ticks = []
tt = B['click2']
while tt < zero - 0.03:
    ticks.append(tt)
    tt += max(0.03, 0.09 * (1 - (tt - B['click2']) / (zero - B['click2'])))
for a in ticks:
    put(a, sfx.tick, -17, 'tick')
put(zero - 0.6, sfx.riser(0.6), -14)
put(zero - 0.03, sfx.impact(2.4, 52, 1.2), -6)
put(zero - 0.03, sfx.hit(0.5, 80), -11)
put(zero + 0.25, sfx.drone(2.0, 49), -24)

# GAME CHANGE
put(back, sfx.impact(1.2, 65, 0.8), -9)
put(23.05, sfx.paper(0.6, 0.4), -10)
put(B['year'], sfx.shutter, -10)
put(B['year'] + 0.01, sfx.hit(0.4, 100), -8)
for a in [B['seo'], B['seo'] + 0.4, B['seo'] + 0.62]:
    put(a, sfx.pop, -16, 'pop')
for a in [B['badal'], B['badal'] + 0.32]:
    put(a, sfx.hit(0.3, 120), -11)
put(B['badal'] + 0.55, sfx.marker(0.3), -12)

# CITE
for a in [28.02, B['rankStrike']]:
    put(a, sfx.pop, -16, 'pop')
for a in [B['kaafiNahi'], B['kaafiNahi'] + 0.24]:
    put(a, sfx.hit(0.3, 110), -10)
put(B['kaafiNahi'] + 0.2, sfx.marker(0.25), -11)
put(B['aiCard'] - 0.15, sfx.whoosh(0.45, 300, 4000, 0.7, 0, 0), -13)
for i in range(10):
    put(B['aiCard'] + 0.3 + i * 0.14, sfx.blip(2000 + (i % 3) * 300, 0.03), -28)
put(B['naam'], sfx.sparkle(0.6), -14)
put(32.32, sfx.pop, -15, 'pop')
put(32.4, sfx.marker(0.2), -14)
put(B['cite'], sfx.stamp, -5, 'stamp')
put(B['cite'], sfx.hit(0.4, 90), -10)

# TEEN (build)
for a in [34.7, 35.02, 35.22]:
    put(a, sfx.pop, -17, 'pop')
put(B['kaise'], sfx.hit(0.45, 100), -8)
for i, f in enumerate([523.25, 659.25, 783.99]):  # C E G: the 1-2-3 tiles play a triad
    put(B['teen'] + i * 0.2, sfx.tone_pop(f), -13)
put(B['simple'], sfx.pop, -17, 'pop')
put(B['simple'] + 0.45, sfx.pop, -17, 'pop')
put(38.0 - 1.6, sfx.riser(1.6), -11)
put(38.0 - 1.0, sfx.reverse_swell(1.0), -16)
put(38.0, sfx.impact(1.6, 60, 1.0), -10)

# ONE
put(38.1, sfx.swish, -14)
put(39.55, sfx.paper(0.5, -0.4), -12)
put(40.55, sfx.paper(0.5, 0.4), -12)
for a in [39.66, B['sawaal'], 40.68, B['jawaab']]:
    put(a, sfx.pop, -17, 'pop')
put(B['bolte'], sfx.pop(700, 240, 0.12), -12)
put(B['likho'], sfx.marker(0.4), -11)

# TWO
put(44.4, sfx.swish, -14)
for a in [45.28, 45.58, 46.28]:
    put(a, sfx.pop, -17, 'pop')
put(B['har'], sfx.hit(0.3, 120), -12)
for i, k in enumerate(['yt', 'ig', 'gbp']):
    put(B[k], sfx.tone_pop([587.33, 739.99, 880.0][i]), -12)
put(B['wahin'], sfx.ding(1318.5), -12)
for i in range(3):
    put(B['wahin'] + 0.1 + i * 0.1, sfx.whoosh(0.25, 2500, 8000, 0.3, -0.5 + i * 0.5, 0), -22)
for a in [51.52, 51.66, 52.04]:
    put(a, sfx.pop, -20, 'pop')

# THREE
put(52.5, sfx.paper(0.55, -0.2), -12)
put(52.6, sfx.swish, -14)
for i in range(4):
    put(53.0 + i * 0.12, sfx.tone_pop([392.0, 440.0, 493.88, 587.33][i], 0.12), -18)
put(B['realData'], sfx.stamp, -7, 'stamp')
put(B['realExp'], sfx.stamp, -7, 'stamp')
for i in range(2):
    a = B['copy'] + i * 0.28
    put(a - 0.06, sfx.key(100 + i), -10)
    put(a, sfx.key(200 + i), -9)
for i in range(3):
    put(B['copy'] + 0.25 + i * 0.12, sfx.paper(0.25, 0.3 + i * 0.2), -15)
put(B['ignore'], sfx.stamp, -5, 'stamp')
put(B['ignore'] + 0.02, sfx.buzz(0.32), -14)
put(B['ignore'], sfx.hit(0.4, 85), -10)

# CTA
put(B['next'], sfx.pop, -13, 'pop')
put(B['next'] + 0.02, sfx.swish, -15)
put(B['insta2'] - 0.25, sfx.whoosh(0.5, 400, 5000, 0.7, 0, 0), -13)
for i in range(8):
    put(B['engine'] + i / 14, sfx.key(300 + i), -17)
for i in range(12):
    put(B['engine'] + 0.4 + i * 0.05, sfx.blip(1500 + (i % 4) * 250, 0.03), -27)
for a in [B['insta2'], B['engine'] - 0.3, B['engine'], B['engine'] + 0.34]:
    put(a, sfx.pop, -16, 'pop')
for a in [65.26, 65.7, 66.02, 66.22, 66.42]:
    put(a, sfx.pop, -19, 'pop')
put(B['follow'] - 0.15, sfx.pop(800, 300, 0.12), -12)
put(B['follow'] + 0.35, sfx.mouse_click, -9, 'mclick')
put(B['follow'] + 0.42, sfx.sparkle(0.6), -13)
for a in [B['warna'], 68.68, 68.86]:
    put(a, sfx.pop, -18, 'pop')
put(68.42, sfx.hit(0.35, 110), -11)
put(69.75 - 0.8, sfx.reverse_swell(0.8), -16)
put(69.75, sfx.impact(1.0, 62, 0.9), -9)

# ---------------------------------------------------------------- sum
# SFX get a touch of ducking too so consonants stay clear
bus *= (db(-5 * duck))[:, None]
mixd = voice_st + music + bus
sf.write('out/mix_premaster.wav', mixd.astype(np.float32), SR, subtype='FLOAT')
print('voice LUFS', round(meter.integrated_loudness(voice_st), 1), 'music LUFS', round(meter.integrated_loudness(music), 1),
      'sfx LUFS', round(meter.integrated_loudness(bus), 1), 'mix LUFS', round(meter.integrated_loudness(mixd), 1),
      'peak', round(20 * np.log10(np.abs(mixd).max()), 1), 'offB', offB, 'offC', offC)
