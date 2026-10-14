"""v2 mix: real recorded foley/SFX (Mixkit, free licence), "Vastness" (Mixkit) aligned so its swell lands on SUPERMIND,
a quiet synthesized tanpura bed in D, and the narration. Sound-design notes are inline next to each cue."""
import json, os, subprocess
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


def auto(points):
    ts, vs = zip(*points)
    return db(np.interp(t, ts, vs))


# ---------- voice (same take; warm, present, a touch of room)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'public/voice.mp3', '-af',
                'highpass=f=75,equalizer=f=180:t=q:w=1:g=1.5,equalizer=f=320:t=q:w=1.2:g=-2.5,equalizer=f=3000:t=q:w=1.0:g=2.5,'
                'equalizer=f=6800:t=q:w=2:g=-2.5,equalizer=f=11000:t=h:w=0.7:g=2,'
                'acompressor=threshold=-22dB:ratio=3:attack=6:release=110:makeup=3',
                '-ar', str(SR), '-ac', '1', 'audio/voice_proc.wav'], check=True)
v, _ = sf.read('audio/voice_proc.wav')
voice = np.zeros(N)
voice[:min(N, len(v))] = v[:N]
voice *= db(-16 - meter.integrated_loudness(voice))
ir = np.random.default_rng(1).standard_normal(int(0.5 * SR)) * np.exp(-np.arange(int(0.5 * SR)) / (0.1 * SR))
ir = signal.sosfilt(signal.butter(2, [300, 5000], 'bandpass', fs=SR, output='sos'), ir)
ir *= db(-20) / np.sqrt((ir ** 2).sum())
rev = signal.fftconvolve(voice, ir)[:N]
voice_st = np.stack([voice + rev, voice + np.roll(rev, 240)], 1)

env = np.sqrt(np.clip(signal.sosfilt(signal.butter(2, 12, 'low', fs=SR, output='sos'), voice ** 2), 0, None))
act = signal.decimate((env > db(-38)).astype(float), 48)
g, dk = 0.0, np.zeros_like(act)
for i, x in enumerate(act):
    g = (np.exp(-1 / 30) * g + (1 - np.exp(-1 / 30)) * x) if x > g else (np.exp(-1 / 380) * g + (1 - np.exp(-1 / 380)) * x)
    dk[i] = g
duck = np.interp(np.arange(N), np.arange(len(dk)) * 48, dk)

# ---------- music: "Vastness" offset so its build (track 40 s) meets SUPERMIND (24.16 s)
m, _ = librosa.load('audio/mixkit/music/m184.mp3', sr=SR, mono=False)
m = m.T
OFF = 40.0 - B['supermind']
music = np.zeros((N, 2))
seg = m[int(OFF * SR): int(OFF * SR) + N]
music[:len(seg)] = seg
music *= db(-21 - meter.integrated_loudness(music[int(8 * SR):int(40 * SR)]))
lp = np.stack([signal.sosfiltfilt(signal.butter(4, 1100, 'low', fs=SR, output='sos'), music[:, c]) for c in range(2)], 1)
wlp = np.interp(t, [0, 21.3, 21.5, 23.9, 24.16, 31.6, 32.2, 40.8, 42.3, 43.2, 60], [0, 0, 1, 1, 0, 0, 0.75, 0.75, 1, 0, 0])
music = music * (1 - wlp)[:, None] + lp * wlp[:, None]
music *= auto([(0, -80), (6.2, -80), (6.6, -2), (11.5, -2), (12.0, -4), (21.3, -4), (21.5, -10), (24.0, -6), (24.16, 1), (28.5, 0), (31.6, -1),
               (32.2, -4), (40.9, -4), (41.15, -60), (42.25, -60), (44.6, -3), (46.5, -1), (48.4, 0), (48.6, 2), (52.4, 1), (53.4, -60)])[:, None]
music *= db(-6 * duck)[:, None]

# ---------- tanpura bed (Indian texture, very low)
tan = sfx.tanpura(DUR + 1, sa=146.83)[:N]
tan *= db(-34 - meter.integrated_loudness(tan))
tan *= auto([(0, -60), (4.0, -60), (4.6, 0), (41.0, 0), (41.3, 1.5), (42.3, 1.5), (43.5, 0), (52.5, 0), (53.4, -60)])[:, None]

# ---------- real SFX
cache = {}


def S(name):
    if name not in cache:
        y, _ = librosa.load(f'audio/mixkit/sfx/{name}.mp3', sr=SR, mono=False)
        y = y.T if y.ndim == 2 else np.stack([y, y], 1)
        a = np.abs(y).mean(1)
        rms = np.sqrt((y[a > a.max() * 0.05] ** 2).mean())  # loudness of the active part
        cache[name] = y * db(-18) / (rms + 1e-9)
    return cache[name]


bus = np.zeros((N, 2))
CUES = []  # every placed sound, for the timeline editor export (scripts/export_editor.py)


def put(at, src, gdb, start=0.0, dur=None, fin=0.0, fout=0.05, rate=1.0, label=None):
    name = src if isinstance(src, str) else label
    y = S(src) if isinstance(src, str) else src
    y = y[int(start * SR):]
    if rate != 1.0:
        idx = np.arange(0, len(y) - 1, rate)
        y = np.stack([np.interp(idx, np.arange(len(y)), y[:, c]) for c in range(2)], 1)
    if dur is not None:
        y = y[:int(dur * SR)]
    y = y.copy()
    if fin:
        k = min(len(y), int(fin * SR)); y[:k] *= np.linspace(0, 1, k)[:, None]
    if fout:
        k = min(len(y), int(fout * SR)); y[-k:] *= np.linspace(1, 0, k)[:, None]
    s = int(at * SR)
    e = min(N, s + len(y))
    if e > s:
        bus[s:e] += y[: e - s] * db(gdb)
        CUES.append(dict(at=round(at, 3), name=name, gain=gdb, start=start, dur=dur, fin=fin, fout=fout, rate=rate, audio=y[: e - s]))


# HOOK: inner noise. A wind bed and slow heart, then the montage explodes into crowd + traffic + racing clock,
# cut dead on "Ab socho" (hard silence is the hook), single heartbeats, and a shimmer as the eye opens.
put(0.0, 'wind_hum', -30, dur=2.6, fin=0.4, fout=0.4)
put(0.0, 'heartbeat_slow', -24, start=2.0, dur=2.4, fin=0.3, fout=0.2)
kd = B['abSocho'] - B['kitne']
put(B['kitne'], 'crowd_talk', -18, start=5, dur=kd, fin=0.15, fout=0.01)
put(B['kitne'], 'city_traffic', -22, start=10, dur=kd, fin=0.1, fout=0.01)
put(B['kitne'], 'clock_close', -17, dur=kd, fout=0.01, rate=1.5)
for i in range(4):
    put(B['kitne'] + i * kd / 4 - 0.12, 'whoosh_fast', -22)
put(B['abSocho'] - 0.02, 'heart_impact', -10)
put(B['abSocho'] + 0.75, 'heartbeat_single', -13)
put(B['abSocho'] + 1.55, 'heartbeat_single', -14)
put(B['dekh'] - 0.1, 'magic_light', -15)

# INTRO: whoosh-impact as the music enters; wind on the flag; the photograph is shot and dropped on the table
put(B['freedom'] - 0.45, 'whoosh_impact', -15, start=0.0, dur=3.0)
put(B['freedom'], 'wind_mountain', -27, dur=1.4, fin=0.3, fout=0.4)
put(B['yogi'] + 0.05, 'swoosh_wind', -20)
put(B['yogi'] + 0.25, 'camera_vintage', -11)
put(B['yogi'] + 0.4, 'paper_slide', -15)
put(B['sri'], 'swoosh_windy', -22)
put(B['chaabi'], 'pencil', -16)

# LADDER: pencil draws the ladder; each level lands with its own texture
put(11.3, 'whoosh_tunnel', -19, dur=2.5, fout=0.6)
put(13.0, 'pencil', -18)
put(13.5, 'pencil', -19)
put(B['matter'] - 0.15, 'whoosh_deep_impact', -15)
put(B['matter'], 'wind_mountain', -25, start=5, dur=1.1, fin=0.2, fout=0.3)
put(B['life'] - 0.1, 'swoosh_windy', -18)
put(B['life'], 'rain_light', -25, dur=1.1, fin=0.2, fout=0.3)
put(B['mind'] - 0.05, 'heart_impact', -14)
put(B['mind'], 'crowd_talk', -27, start=20, dur=B['par'] - B['mind'], fin=1.5, fout=0.05)
put(B['atke'] + 0.05, 'pencil', -15)
put(B['overthink'] - 0.1, 'clock_close', -20, start=1, dur=B['par'] - B['overthink'] + 0.05, fin=0.4, fout=0.02, rate=1.25)

# SUPERMIND: dead stop on "Par", a glass hit, the riser climbs into the swell; impact + light on the word
put(B['par'] - 0.05, 'glass_hit', -14)
put(B['supermind'] - 2.6, 'riser', -14)
put(B['supermind'] - 0.05, 'impact_big', -11)
put(B['supermind'], 'magic_light', -14)
put(B['supermind'] + 0.3, 'sparkle_whoosh', -21)
put(26.45, 'pencil', -18)
put(B['jaanti'], 'bell_chime', -15)
put(28.45, 'swoosh_wind', -18)
put(28.6, 'wind_mountain', -28, start=12, dur=3.0, fin=0.5, fout=0.6)
put(30.25, 'pencil', -20)

# STORY 1908: the archive drawer opens; typewriter for the instructions; thoughts blown away like papers; tally marks
put(31.45, 'whoosh_tunnel', -19, dur=2.2, fout=0.5)
put(B['y1908'], 'clock_fast', -21, dur=0.75, fout=0.05)
put(31.9, 'camera_vintage', -12)
put(32.05, 'paper_slide', -15)
put(32.84, 'pencil', -18)
put(B['baitho'], 'type_hit', -11)
put(B['soChoMat'], 'type_hit2', -11)
put(35.64, 'type_hit', -13)
put(B['dekho'] - 0.6, 'type_hit2', -11)
put(B['dekho'] - 0.1, 'type_bell', -17)
put(B['thoughts2'], 'crowd_talk', -24, start=30, dur=B['phenk'] - B['thoughts2'], fin=0.3, fout=0.1)
put(B['phenk'] - 0.15, 'papers_wind', -15, dur=2.0, fout=0.5)
put(B['phenk'] - 0.1, 'whoosh_fast', -17)
for a in [B['teen'], 40.24, 40.44]:
    put(a, 'pencil', -14, start=0.1, dur=0.35, fout=0.05)
put(B['shaant'] - 0.02, sfx.water_drop(), -12, label='water_drop (synth)')
put(B['shaant'], 'rain_light', -27, start=8, dur=1.4, fin=0.4, fout=0.6)
put(B['shaant'] + 0.05, 'bell_chime', -19)

# PRACTICE: a breath in, harp opens the music back up; the eye gets a single heartbeat; "Wahi aap ho" lands with light
put(B['aaj'] - 0.15, 'swoosh_windy', -21)
put(B['aaj'] - 0.1, sfx.breath(1.8, True), -26, label='breath (synth)')
put(B['aaj'] + 0.6, 'harp_sweep', -27)
put(B['kyunki'] - 0.3, 'whoosh_tunnel', -25, dur=1.6, fout=0.4)
put(46.3, 'heartbeat_single', -17)
put(B['wahi'] - 0.2, 'whoosh_deep_impact', -15)
put(B['wahi'] - 0.05, 'magic_light', -16)

# END: morning birds, a chime on "Yoga", a soft pop for Follow
put(B['all'] - 0.2, 'birds_morning', -25, start=20, dur=DUR - B['all'] + 0.2, fin=0.6, fout=0.8)
put(B['all'] - 0.3, 'swoosh_wind', -20)
put(B['yoga'], 'bell_chime', -14)
put(B['yoga'] + 0.1, 'sparkle_whoosh', -22)
put(B['follow'], 'paper_quick', -17)

sfx_gain = db(3) * db(-4 * duck)  # SFX sit +3 dB and duck 4 dB under the voice
bus *= sfx_gain[:, None]
mix = voice_st + music + tan + bus
mix *= np.clip((DUR - t) / 0.4, 0, 1)[:, None]
sf.write('out/mix_premaster.wav', mix.astype(np.float32), SR, subtype='FLOAT')
print('voice', round(meter.integrated_loudness(voice_st), 1), 'music', round(meter.integrated_loudness(music), 1),
      'sfx', round(meter.integrated_loudness(bus), 1), 'mix', round(meter.integrated_loudness(mix), 1), 'OFF', round(OFF, 2))

if os.environ.get('STEMS'):
    # stems + per-cue audio for the timeline editor; summing the stems reproduces mix_premaster.wav
    os.makedirs('out/stems', exist_ok=True)
    fade = np.clip((DUR - t) / 0.4, 0, 1)[:, None]
    for k, y in [('voice', voice_st), ('music', music), ('tanpura', tan), ('sfx', bus)]:
        sf.write(f'out/stems/{k}.wav', (y * fade).astype(np.float32), SR, subtype='FLOAT')
    np.save('out/stems/sfx_gain.npy', sfx_gain[::SR // 100].astype(np.float32))
    import pickle
    pickle.dump(CUES, open('out/stems/cues.pkl', 'wb'))
