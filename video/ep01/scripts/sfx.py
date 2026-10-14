"""Procedural SFX library. Every sound is synthesized here (no samples), so the mix is royalty-free.
All functions return float32 stereo arrays shaped (n, 2) at SR, peak-normalized to 1.0."""
import numpy as np
from scipy import signal

SR = 48000
rng = np.random.default_rng(11)


def _n(sec):
    return int(sec * SR)


def _norm(x):
    p = np.max(np.abs(x)) + 1e-9
    return (x / p).astype(np.float32)


def _st(mono, pan=0.0):
    """Mono -> stereo with constant-power pan (-1 left .. 1 right); pan may be an array for movement."""
    pan = np.broadcast_to(pan, mono.shape)
    a = (pan + 1) * np.pi / 4
    return np.stack([mono * np.cos(a), mono * np.sin(a)], 1)


def _env(n, attack, release, curve=3.0):
    t = np.linspace(0, 1, n)
    a = max(1e-4, attack)
    e = np.where(t < a, (t / a) ** 1.5, (1 - (t - a) / (1 - a + 1e-9)) ** curve)
    return np.clip(e, 0, 1)


def _sweep_bp(x, f0, f1, q=1.2, block=256):
    """Time-varying band-pass via block-wise biquads (log sweep f0 -> f1)."""
    out = np.zeros_like(x)
    nb = int(np.ceil(len(x) / block))
    zi = None
    for b in range(nb):
        fc = f0 * (f1 / f0) ** (b / max(1, nb - 1))
        fc = np.clip(fc, 30, SR / 2.3)
        bw = fc / q
        sos = signal.butter(2, [max(20, fc - bw / 2), min(SR / 2.1, fc + bw / 2)], 'bandpass', fs=SR, output='sos')
        if zi is None:
            zi = np.zeros((sos.shape[0], 2))
        seg = x[b * block:(b + 1) * block]
        y, zi = signal.sosfilt(sos, seg, zi=zi)
        out[b * block:(b + 1) * block] = y
    return out


def _lp(x, fc, order=2):
    return signal.sosfilt(signal.butter(order, fc, 'low', fs=SR, output='sos'), x)


def _hp(x, fc, order=2):
    return signal.sosfilt(signal.butter(order, fc, 'high', fs=SR, output='sos'), x)


def _bp(x, lo, hi, order=2):
    return signal.sosfilt(signal.butter(order, [lo, hi], 'bandpass', fs=SR, output='sos'), x)


def _sine_sweep(n, f0, f1, curve='exp'):
    t = np.arange(n) / SR
    T = n / SR
    if curve == 'exp':
        k = np.log(f1 / f0) / T
        ph = 2 * np.pi * f0 * (np.exp(k * t) - 1) / k
    else:
        ph = 2 * np.pi * (f0 * t + (f1 - f0) * t * t / (2 * T))
    return np.sin(ph)


def whoosh(dur=0.55, f0=300, f1=4000, peak=0.6, pan_from=-0.8, pan_to=0.8):
    """Air-movement whoosh: swept band-passed noise, swelling into the peak then decaying, panning across."""
    n = _n(dur)
    x = rng.standard_normal(n)
    x = _sweep_bp(x, f0, f1, q=0.9) + 0.35 * _sweep_bp(rng.standard_normal(n), f0 * 2, f1 * 1.5, q=2)
    x *= _env(n, peak, 1, 2.2)
    return _norm(_st(x, np.linspace(pan_from, pan_to, n)))


def swish(dur=0.22):
    return whoosh(dur, 1500, 7000, 0.45, -0.4, 0.4)


def pop(f0=900, f1=260, dur=0.09, click=0.25):
    """Bubbly UI pop: fast pitch-drop sine with a tiny transient."""
    n = _n(dur)
    s = _sine_sweep(n, f0, f1) * _env(n, 0.02, 1, 2.5)
    s[:_n(0.003)] += rng.standard_normal(_n(0.003)) * click
    return _norm(_st(s))


def tone_pop(freq, dur=0.16):
    """Pitched pop (musical) for staggered elements: sine + octave, short decay."""
    n = _n(dur)
    t = np.arange(n) / SR
    s = (np.sin(2 * np.pi * freq * t) + 0.35 * np.sin(4 * np.pi * freq * t)) * np.exp(-t * 28)
    s *= np.minimum(1, t / 0.002)
    s += _sine_sweep(n, freq * 2.2, freq, 'lin') * np.exp(-t * 60) * 0.5
    return _norm(_st(s))


def click(bright=4000, dur=0.012):
    n = _n(dur)
    s = _hp(rng.standard_normal(n), 1500) * np.exp(-np.arange(n) / SR * 600)
    s += np.sin(2 * np.pi * bright * np.arange(n) / SR) * np.exp(-np.arange(n) / SR * 400) * 0.6
    return _norm(_st(s))


def mouse_click():
    a = click(3200, 0.015)
    b = click(2600, 0.012) * 0.7
    out = np.zeros((_n(0.09), 2))
    out[:len(a)] += a
    out[_n(0.065):_n(0.065) + len(b)] += b
    return _norm(out)


def key(seed):
    """Single mechanical keystroke with small randomization."""
    r = np.random.default_rng(seed)
    n = _n(0.05)
    t = np.arange(n) / SR
    s = _bp(r.standard_normal(n), 1800 + r.uniform(-300, 600), 6500) * np.exp(-t * 180)
    s += np.sin(2 * np.pi * r.uniform(180, 260) * t) * np.exp(-t * 90) * 0.5  # key-bed thock
    return _norm(_st(s, r.uniform(-0.25, 0.25)))


def impact(dur=1.8, sub=58, punch=1.0):
    """Cinematic boom: pitch-dropping sub, distorted body, noise crack, long tail."""
    n = _n(dur)
    t = np.arange(n) / SR
    body = _sine_sweep(n, sub * 2.2, sub * 0.6) * np.exp(-t * 2.6)
    body = np.tanh(body * 2.5) * 0.8
    crack = _lp(rng.standard_normal(n), 3500) * np.exp(-t * 28) * punch
    tail = _lp(rng.standard_normal(n), 900) * np.exp(-t * 3.2) * 0.25
    s = body + crack + tail
    s *= np.minimum(1, t / 0.001)
    L = s + 0.15 * _lp(np.roll(tail, 300), 700)
    R = s + 0.15 * _lp(np.roll(tail, 520), 700)
    return _norm(np.stack([L, R], 1))


def hit(dur=0.35, freq=110):
    """Lighter thud for text slams: short sub + paper slap."""
    n = _n(dur)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * freq * t * (1 + 0.6 * np.exp(-t * 40))) * np.exp(-t * 14)
    s += _bp(rng.standard_normal(n), 900, 4500) * np.exp(-t * 55) * 0.7
    return _norm(_st(np.tanh(s * 1.6)))


def stamp():
    """Rubber stamp: wooden knock + ink 'chk' + table thud."""
    n = _n(0.4)
    t = np.arange(n) / SR
    knock = np.sin(2 * np.pi * 180 * t) * np.exp(-t * 35)
    chk = _bp(rng.standard_normal(n), 2000, 7000) * np.exp(-t * 90) * 0.9
    thud = np.sin(2 * np.pi * 70 * t) * np.exp(-t * 18) * 0.8
    return _norm(_st(np.tanh((knock + chk + thud) * 1.5)))


def paper(dur=0.45, pan=0.0):
    """Paper sliding across a desk: band-limited noise with grainy amplitude texture."""
    n = _n(dur)
    x = _bp(rng.standard_normal(n), 1500, 9000)
    grain = _lp(np.abs(rng.standard_normal(n)), 40)
    x *= (0.4 + grain / (grain.max() + 1e-9)) * _env(n, 0.15, 1, 1.5)
    return _norm(_st(x, pan))


def marker(dur=0.3):
    """Felt marker stroke: squeaky band noise with fast flutter."""
    n = _n(dur)
    t = np.arange(n) / SR
    x = _bp(rng.standard_normal(n), 2500, 8000)
    flutter = 0.6 + 0.4 * np.sin(2 * np.pi * (35 + 15 * np.sin(2 * np.pi * 3 * t)) * t)
    x *= flutter * _env(n, 0.1, 1, 0.8)
    return _norm(_st(x))


def riser(dur=1.6):
    """Tension riser: rising detuned saws + filtered noise, crescendo to a hard stop."""
    n = _n(dur)
    t = np.arange(n) / SR
    f = 110 * (16 ** (t / (dur)))
    ph = 2 * np.pi * np.cumsum(f) / SR
    saw = sum(signal.sawtooth(ph * k * (1 + d)) for k, d in [(1, 0), (1, 0.008), (2, -0.006)]) / 3
    saw = _lp(saw, 5000)
    nz = _sweep_bp(rng.standard_normal(n), 500, 9000, 1.5)
    e = (t / dur) ** 2.2
    s = (saw * 0.6 + nz) * e
    s[-_n(0.01):] *= np.linspace(1, 0, _n(0.01))
    L = s
    R = np.roll(s, 240)
    return _norm(np.stack([L, R], 1))


def reverse_swell(dur=1.0):
    n = _n(dur)
    t = np.arange(n) / SR
    x = _hp(rng.standard_normal(n), 3000) * (t / dur) ** 3
    x += _lp(rng.standard_normal(n), 600) * (t / dur) ** 4 * 0.5
    x[-_n(0.008):] *= np.linspace(1, 0, _n(0.008))
    return _norm(np.stack([x, np.roll(x, 300)], 1))


def ding(freq=1046.5, dur=1.1):
    """Clean bell for 'AI' reveals: inharmonic partials with independent decays."""
    n = _n(dur)
    t = np.arange(n) / SR
    s = sum(a * np.sin(2 * np.pi * freq * r * t) * np.exp(-t * d) for r, a, d in [(1, 1, 4), (2.0, 0.4, 6), (2.76, 0.3, 9), (5.4, 0.15, 14)])
    s *= np.minimum(1, t / 0.002)
    return _norm(np.stack([s, np.roll(s, 400) * 0.9], 1))


def sparkle(dur=0.6):
    out = np.zeros((_n(dur), 2))
    for i, f in enumerate([2093, 2637, 3136, 4186, 3520]):
        d = ding(f, 0.35) * 0.6
        st = _n(i * 0.06)
        seg = d[:len(out) - st]
        out[st:st + len(seg)] += seg * np.array([1 - i * 0.15, 0.4 + i * 0.15])
    return _norm(out)


def blip(freq=1200, dur=0.06):
    n = _n(dur)
    t = np.arange(n) / SR
    s = signal.square(2 * np.pi * freq * t) * np.exp(-t * 50)
    return _norm(_st(_lp(s, 6000)))


def buzz(dur=0.3):
    """Error buzzer for 'ignored'."""
    n = _n(dur)
    t = np.arange(n) / SR
    s = (signal.square(2 * np.pi * 110 * t) + signal.square(2 * np.pi * 116 * t)) * _env(n, 0.02, 1, 0.4)
    return _norm(_st(_lp(s, 2500)))


def shutter():
    a = click(2500, 0.02)
    out = np.zeros((_n(0.16), 2))
    out[:len(a)] += a
    nz = paper(0.08)
    out[_n(0.02):_n(0.02) + len(nz)] += nz * 0.6
    out[_n(0.11):_n(0.11) + len(a)] += a * 0.8
    return _norm(out)


def tick():
    return click(5200, 0.008)


def drone(dur=2.2, freq=55):
    """Low, uneasy room tone that fills the silence after ZERO."""
    n = _n(dur)
    t = np.arange(n) / SR
    s = (np.sin(2 * np.pi * freq * t) + 0.5 * np.sin(2 * np.pi * freq * 1.5 * t + 0.3)) * 0.5
    s += _lp(rng.standard_normal(n), 300) * 0.3
    s *= np.minimum(1, t / 0.3) * np.minimum(1, (dur - t) / 0.6)
    return _norm(np.stack([s, np.roll(s, 800)], 1))


def servo(dur=0.4):
    """Robot servo whir: buzzy pitch glide up then settle."""
    n = _n(dur)
    t = np.arange(n) / SR
    f = 180 + 260 * np.sin(np.pi * t / dur) ** 0.7
    s = signal.sawtooth(2 * np.pi * np.cumsum(f) / SR) * 0.6 + signal.square(2 * np.pi * np.cumsum(f * 2.01) / SR) * 0.2
    s = _bp(s, 300, 4000) * _env(n, 0.1, 1, 1.2)
    return _norm(_st(s, 0.4))


def fuse(dur=0.7):
    """Burning fuse: hissy band noise with random sparks (crackles)."""
    n = _n(dur)
    x = _bp(rng.standard_normal(n), 3000, 11000) * 0.5
    sparks = (rng.random(n) > 0.9993).astype(float)
    x += _hp(np.convolve(sparks, np.exp(-np.arange(200) / 25), 'same') * rng.choice([-1, 1], n), 1500) * 2.5
    x *= np.minimum(1, np.arange(n) / _n(0.05))
    return _norm(_st(x, -0.5))


def clang(dur=0.9):
    """Metal trash-can hit: inharmonic partials with fast-decaying highs."""
    n = _n(dur)
    t = np.arange(n) / SR
    s = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t * d) for f, a, d in [(310, 1, 6), (742, 0.7, 9), (1187, 0.5, 13), (1903, 0.35, 18), (2711, 0.2, 25)])
    s += _bp(rng.standard_normal(n), 1500, 6000) * np.exp(-t * 60) * 0.8
    return _norm(_st(s, 0.5))


def hum(dur=0.8):
    """Light-bulb buzz (mains hum + harmonics) with a switch click in front."""
    n = _n(dur)
    t = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * 50 * k * t) / k for k in (1, 2, 3, 5)) * 0.4 * _env(n, 0.05, 1, 1.5)
    s[:_n(0.012)] += _hp(rng.standard_normal(_n(0.012)), 2000) * 2
    return _norm(_st(s))
