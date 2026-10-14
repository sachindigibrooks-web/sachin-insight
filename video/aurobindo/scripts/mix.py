"""Sound design + mix for the Sri Aurobindo consciousness short.
Layers: voice (lead), "Ether Vox" (Kevin MacLeod, CC BY 4.0) with ducking + section automation,
a synthesized tanpura drone tuned to the track's key (D), and synthesized SFX on the same beats as the visuals."""
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
t = np.arange(N) / SR
meter = pyln.Meter(SR)
db = lambda x: 10 ** (x / 20)


def ramp(points):
    """Piecewise-linear automation in dB from [(time, dB), ...]."""
    ts, vs = zip(*points)
    return db(np.interp(t, ts, vs))


# ---------------- voice
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'public/voice.mp3', '-af',
                'highpass=f=80,equalizer=f=260:t=q:w=1.2:g=-2,equalizer=f=3200:t=q:w=1.0:g=2,'
                'equalizer=f=7000:t=q:w=2:g=-2,equalizer=f=11000:t=h:w=0.7:g=1.5,'
                'acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=2',
                '-ar', str(SR), '-ac', '1', 'audio/voice_proc.wav'], check=True)
v, _ = sf.read('audio/voice_proc.wav')
voice = np.zeros(N)
voice[:min(N, len(v))] = v[:N]
voice *= db(-16 - meter.integrated_loudness(voice))
# a little room so the narration feels intimate, not dry
ir = np.random.default_rng(1).standard_normal(int(0.6 * SR)) * np.exp(-np.arange(int(0.6 * SR)) / (0.12 * SR))
ir = signal.sosfilt(signal.butter(2, [300, 5000], 'bandpass', fs=SR, output='sos'), ir)
ir *= db(-18) / np.sqrt((ir ** 2).sum())  # wet sits ~18 dB under the dry voice
rev = signal.fftconvolve(voice, ir)[:N]
voice_st = np.stack([voice + rev, voice + np.roll(rev, 240)], 1)

env = np.sqrt(np.clip(signal.sosfilt(signal.butter(2, 12, 'low', fs=SR, output='sos'), voice ** 2), 0, None))
act = signal.decimate((env > db(-38)).astype(float), 48)
g, dk = 0.0, np.zeros_like(act)
a1, r1 = np.exp(-1 / 30), np.exp(-1 / 400)
for i, x in enumerate(act):
    g = a1 * g + (1 - a1) * x if x > g else r1 * g + (1 - r1) * x
    dk[i] = g
duck = np.interp(np.arange(N), np.arange(len(dk)) * 48, dk)

# ---------------- music: Ether Vox enters on "Freedom fighter"
m, _ = librosa.load('audio/music/Ether_Vox.mp3', sr=SR, mono=False)
m = m.T
off = 18.0
music = np.zeros((N, 2))
seg = m[int(off * SR): int(off * SR) + N]
music[:len(seg)] = seg
music *= db(-22 - meter.integrated_loudness(music[int(8 * SR):int(30 * SR)]))
lp = np.stack([signal.sosfiltfilt(signal.butter(4, 900, 'low', fs=SR, output='sos'), music[:, c]) for c in range(2)], 1)
wlp = np.interp(t, [0, 31.4, 32.4, 40.8, 41.2, 42.3, 43.5, 60], [0, 0, 0.8, 0.8, 1, 1, 0, 0])  # filtered during the story, open again for practice
music = music * (1 - wlp)[:, None] + lp * wlp[:, None]
music *= ramp([(0, -80), (6.3, -80), (7.6, 0), (21.5, 0), (22.5, -3), (24.16, 1.5), (31.4, 0), (32.4, -3), (40.9, -3), (41.4, -40),
               (42.6, -40), (44.0, -2), (48.4, 0), (49.0, 1.5), (52.3, 0), (53.4, -60)])[:, None]
music *= db(-6.5 * duck)[:, None]

# ---------------- tanpura drone (whole piece, quieter under the music)
tan = sfx.tanpura(DUR + 1, sa=146.83)[:N]
tan *= db(-30 - meter.integrated_loudness(tan))
tan *= ramp([(0, -6), (0.6, 0), (6.5, 0), (7.6, -5), (31.4, -5), (32.5, -1), (42.3, 0), (44.0, -5), (52.5, -5), (53.4, -60)])[:, None]
tan *= db(-3 * duck)[:, None]

# ---------------- SFX
bus = np.zeros((N, 2))


def put(at, snd, gdb):
    s = int(at * SR)
    if s < 0:
        snd, s = snd[-s:], 0
    e = min(N, s + len(snd))
    bus[s:e] += snd[: e - s] * db(gdb)


D, Fs, A = 293.66, 369.99, 440.0  # D, F#, A (D major, matches the track + tanpura)

# Hook: chatter + ticking build, hard stop on "Ab socho", heartbeat, bowl as the eye opens
build = B['abSocho'] - B['kitne']
ch = sfx.chatter(build + 0.1, 3) * np.linspace(0.3, 1.0, sfx._n(build + 0.1))[:, None]
put(B['kitne'], ch, -20)
tk = 0.0
while B['kitne'] + tk < B['abSocho'] - 0.04:
    put(B['kitne'] + tk, sfx.tick(), -21)
    tk += max(0.07, 0.22 - tk * 0.1)
put(B['abSocho'] - 0.02, sfx.reverse_swell(0.3) * -1, -30)
put(B['abSocho'] + 0.25, sfx.heartbeat(), -13)
put(B['abSocho'] + 1.05, sfx.heartbeat(), -14)
put(B['dekh'], sfx.bowl(D, 5.0), -15)
put(B['dekh'] + 0.6, sfx.shimmer(1.6, 1174.66), -26)
put(0.0, sfx.sub_swell(1.2, 41), -20)

# Intro
put(B['freedom'] - 0.4, sfx.whoosh(0.7, 200, 2500, 0.65, -0.6, 0.6), -20)
put(B['freedom'], sfx.impact(1.8, 45, 0.3), -19)
put(B['yogi'], sfx.bowl(A, 4.0), -20)
put(B['sri'] + 0.3, sfx.shimmer(1.5, 880), -25)
put(B['chaabi'], sfx.click(2600, 0.02), -22)
put(B['chaabi'] + 0.2, sfx.ding(1760, 0.6), -26)

# Ladder: each step rings a bowl a step higher; the orb gets stuck at Mind
put(B['consciousness'] - 0.5, sfx.whoosh(0.8, 150, 2000, 0.6, 0.6, -0.6), -20)
for k, f in [('matter', D / 2 * 2), ('life', Fs), ('mind', A)]:
    put(B[k], sfx.bowl(f, 3.5), -17)
    put(B[k], sfx.tone_pop(f * 2, 0.2), -27)
stuck_d = B['par'] - B['atke']
put(B['atke'], sfx.chatter(stuck_d, 7) * np.linspace(0.2, 1, sfx._n(stuck_d))[:, None], -23)
tk = 0.0
while B['overthink'] + tk < B['par'] - 0.1:
    put(B['overthink'] + tk, sfx.tick(), -24)
    tk += 0.16

# Supermind
put(B['upar'] - 0.9, sfx.riser(1.5), -21)
put(B['supermind'] - 0.8, sfx.reverse_swell(0.8), -20)
put(B['supermind'], sfx.bowl(D * 2, 6.0), -14)
put(B['supermind'], sfx.shimmer(3.0, 587.33), -18)
put(B['supermind'], sfx.impact(2.4, 40, 0.2), -18)
put(B['sochti'] + 0.3, sfx.whoosh(0.3, 2000, 6000, 0.5, 0, 0), -26)
put(B['jaanti'], sfx.ding(1174.66, 0.9), -22)
put(B['insaan'] - 0.3, sfx.whoosh(0.6, 200, 2500, 0.7, -0.5, 0.5), -21)
for i in range(4):
    put(29.0 + i * 0.25, sfx.tone_pop([D, Fs, A, D * 2][i] * 2, 0.15), -26)
put(B['transitional'], sfx.bowl(Fs, 3.0), -21)

# Story 1908
put(B['y1908'] - 0.3, sfx.whoosh(0.6, 200, 2000, 0.7, 0.5, -0.5), -21)
for i in range(10):
    put(B['y1908'] + i * 0.08, sfx.tick(), -28)
put(B['y1908'] + 0.8, sfx.hit(0.4, 70), -22)
for k, f in [('baitho', D), ('soChoMat', Fs), ('dekho', A)]:
    put(B[k] - (0.6 if k == 'dekho' else 0), sfx.bowl(f, 2.5), -21)
put(B['thoughts2'], sfx.chatter(B['phenk'] - B['thoughts2'], 11), -24)
put(B['phenk'] - 0.1, sfx.whoosh(0.6, 400, 6000, 0.35, -0.9, 0.9), -17)
put(B['phenk'] - 0.05, sfx.whoosh(0.6, 300, 5000, 0.35, 0.9, -0.9), -19)
for i, k in enumerate(['teen', None, None]):
    put([B['teen'], 40.24, 40.44][i], sfx.tone_pop([587.33, 739.99, 880.0][i], 0.25), -19)
put(B['shaant'], sfx.water_drop(), -17)
put(B['shaant'] + 0.05, sfx.bowl(D / 2 * 2, 6.0), -19)

# Practice
put(B['aaj'] - 0.1, sfx.breath(1.8, True), -24)
put(B['aaj'] + 1.9, sfx.breath(2.2, False), -26)
for i in range(4):
    put(B['minute'] + i * 1.0, sfx.tick(), -28)
put(B['kyunki'] - 0.25, sfx.whoosh(0.6, 200, 2200, 0.7, 0, 0), -22)
put(B['wahi'], sfx.bowl(D, 5.0), -15)
put(B['aap'], sfx.shimmer(2.0, 880), -22)

# End
put(B['all'] - 0.6, sfx.reverse_swell(0.6), -22)
put(B['yoga'], sfx.bowl(A, 5.0), -17)
put(B['follow'], sfx.click(2200, 0.02), -22)
put(B['follow'] + 0.03, sfx.pop(700, 300, 0.12), -24)

# Soft air whooshes into each scene
for sc in tl['scenes'][1:]:
    put(sc['s'] - 0.45, sfx.whoosh(0.8, 180, 1800, 0.7, -0.4, 0.4), -27)

bus *= db(-3 * duck)[:, None]
mix = voice_st + music + tan + bus
mix *= np.clip((DUR - t) / 0.4, 0, 1)[:, None]
sf.write('out/mix_premaster.wav', mix.astype(np.float32), SR, subtype='FLOAT')
print('voice', round(meter.integrated_loudness(voice_st), 1), 'music', round(meter.integrated_loudness(music), 1), 'tanpura', round(meter.integrated_loudness(tan), 1),
      'sfx', round(meter.integrated_loudness(bus), 1), 'mix', round(meter.integrated_loudness(mix), 1))
