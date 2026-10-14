"""Mudras ad mix: Kokoro VO (warm female, af_heart) + "Deep Urban" (Mixkit) with its drop on the logo reveal + restrained luxury SFX.
Commercial target: -14 LUFS integrated, VO always clearly on top."""
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

# ---- VO: Kokoro output is clean but a little thin; add body, presence, air, gentle compression and a short plate
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'audio/vo_af_heart.wav', '-af',
                'aresample=48000,highpass=f=70,equalizer=f=170:t=q:w=1:g=2.5,equalizer=f=400:t=q:w=1.4:g=-1.5,'
                'equalizer=f=3200:t=q:w=1.2:g=2,equalizer=f=7500:t=q:w=2:g=-1.5,equalizer=f=12000:t=h:w=0.7:g=2.5,'
                'acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=2',
                '-ac', '1', 'audio/vo_proc.wav'], check=True)
v, _ = sf.read('audio/vo_proc.wav')
vo = np.zeros(N)
vo[:min(N, len(v))] = v[:N]
vo *= db(-16 - meter.integrated_loudness(vo))
ir = np.random.default_rng(2).standard_normal(int(0.9 * SR)) * np.exp(-np.arange(int(0.9 * SR)) / (0.22 * SR))
ir = signal.sosfilt(signal.butter(2, [400, 6000], 'bandpass', fs=SR, output='sos'), ir)
ir *= db(-21) / np.sqrt((ir ** 2).sum())
wet = signal.fftconvolve(vo, ir)[:N]
vo_st = np.stack([vo + wet, vo + np.roll(wet, 360)], 1)

env = np.sqrt(np.clip(signal.sosfilt(signal.butter(2, 10, 'low', fs=SR, output='sos'), vo ** 2), 0, None))
act = signal.decimate((env > db(-38)).astype(float), 48)
g, dk = 0.0, np.zeros_like(act)
for i, x in enumerate(act):
    g = (np.exp(-1 / 25) * g + (1 - np.exp(-1 / 25)) * x) if x > g else (np.exp(-1 / 300) * g + (1 - np.exp(-1 / 300)) * x)
    dk[i] = g
duck = np.interp(np.arange(N), np.arange(len(dk)) * 48, dk)

# ---- Music: start on a beat so the drop (track 15.51 s) lands on "At Mudras"
m, _ = librosa.load('audio/music/m623.mp3', sr=SR, mono=False)
m = m.T
OFF = 15.51 - (B['l2'] - 0.02)
music = np.zeros((N, 2))
seg = m[int(OFF * SR): int(OFF * SR) + N]
music[:len(seg)] = seg
music *= db(-19 - meter.integrated_loudness(music[int(6 * SR):int(30 * SR)]))
# intro filtered (problem statement), opens on the drop; small lift for the CTA; tail fade
lp = np.stack([signal.sosfiltfilt(signal.butter(4, 900, 'low', fs=SR, output='sos'), music[:, c]) for c in range(2)], 1)
w = np.interp(t, [0, B['l2'] - 0.4, B['l2'] - 0.02, 60], [1, 1, 0, 0])
music = music * (1 - w)[:, None] + lp * w[:, None]
music *= auto([(0, -6), (B['l2'] - 0.4, -2), (B['l2'], 0), (38.5, 0), (39.0, 1.5), (43.2, 0), (44.4, -50)])[:, None]
music *= db(-7 * duck)[:, None]

# ---- SFX (Mixkit, restrained: this is luxury, not a trailer)
cache = {}


def S(name):
    if name not in cache:
        y, _ = librosa.load(f'audio/sfx/{name}.mp3', sr=SR, mono=False)
        y = y.T if y.ndim == 2 else np.stack([y, y], 1)
        a = np.abs(y).mean(1)
        cache[name] = y * db(-18) / (np.sqrt((y[a > a.max() * 0.05] ** 2).mean()) + 1e-9)
    return cache[name]


bus = np.zeros((N, 2))


def put(at, name, gdb, start=0.0, dur=None, fin=0.0, fout=0.05):
    y = S(name)[int(start * SR):]
    if dur is not None:
        y = y[:int(dur * SR)]
    y = y.copy()
    if fin:
        k = int(fin * SR); y[:k] *= np.linspace(0, 1, min(k, len(y)))[:, None]
    if fout:
        k = min(len(y), int(fout * SR)); y[-k:] *= np.linspace(1, 0, k)[:, None]
    s = int(at * SR); e = min(N, s + len(y))
    if e > s:
        bus[s:e] += y[:e - s] * db(gdb)


put(0.05, 'clock_close', -24, start=2, dur=2.6, fin=0.4, fout=0.3)          # the "time slot" metronome under line 1
put(1.75, 'pencil', -16)                                                       # gold strike-through
put(B['l1'] - 0.2, 'swoosh_wind', -24)
put(B['l2'] - 1.6, 'reverse_impact', -22, start=8.4, dur=1.6, fout=0.02)      # suck-in before the reveal
put(B['l2'] - 0.03, 'impact_big', -17)                                         # drop + logo
put(B['l2'] + 0.65, 'sparkle_whoosh', -22)                                     # light sweep across the logo
put(B['l3'] - 0.25, 'swoosh_windy', -24)
put(9.85, 'bell_chime', -21)                                                   # "BodyReset" title
put(B['l4'] - 0.25, 'whoosh_tunnel', -26, dur=2.0, fout=0.5)
for a in [B['real'], 12.6, B['carrying'] - 0.3]:
    put(a, 'bell_chime', -27)                                                  # hotspots ping softly
for k in ['deep', 'trigger', 'assisted', 'cupping', 'gua']:
    put(B[k] - 0.12, 'paper_quick', -24)                                       # menu items turn like pages
put(B['chosen'] - 0.2, 'magic_light', -22)
put(B['l7'] - 0.2, 'whoosh_fast', -22)
put(B['desk'] - 0.25, 'whoosh_fast', -23)
put(B['n15'] - 0.3, 'clock_fast', -25, dur=1.3, fout=0.1)                      # counter ticking up
put(B['years'], 'bell_chime', -22)
put(B['l9'] - 0.2, 'harp_sweep', -24)
for k in ['less', 'easier', 'deeper']:
    put(B[k] - 0.1, 'swoosh_wind', -27)
put(B['l10'] - 0.3, 'whoosh_deep_impact', -21)
put(B['l10'] + 0.95, 'sparkle_whoosh', -23)
put(B['l10'], 'city_traffic', -32, start=20, dur=3.8, fin=0.8, fout=1.0)       # a breath of the city under "New York"
put(B['l11'] - 0.3, 'magic_light', -22)
put(B['book'] + 0.2, 'paper_quick', -22)

bus *= (db(3) * db(-4 * duck))[:, None]
mix = vo_st + music + bus
mix *= np.clip((DUR - t) / 0.6, 0, 1)[:, None]
sf.write('out/mix_premaster.wav', mix.astype(np.float32), SR, subtype='FLOAT')
print('vo', round(meter.integrated_loudness(vo_st), 1), 'music', round(meter.integrated_loudness(music), 1), 'sfx', round(meter.integrated_loudness(bus), 1),
      'mix', round(meter.integrated_loudness(mix), 1), 'OFF', round(OFF, 2))
