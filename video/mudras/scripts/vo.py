# Voice-over for the Mudras ad, generated locally with Kokoro-82M (Apache-2.0) via kokoro-onnx.
# Each line is rendered separately and assembled with designed pauses (commercial pacing).
import json, sys
import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

VOICE = sys.argv[1] if len(sys.argv) > 1 else 'af_heart'
LINES = [
    ("Your body is not a time slot.", 0.45),
    ("So why does every massage feel the same?", 0.75),
    ("At Mudras, no two sessions look alike.", 0.5),
    ("Every visit begins with our signature BodyReset,", 0.15),
    ("built in real time, around what your body is carrying today.", 0.7),
    ("Deep tissue. Trigger point. Assisted stretching. Cupping. Gua sha.", 0.35),
    ("Chosen for you. Not from a script.", 0.7),
    ("For pro athletes, and desk warriors alike.", 0.45),
    ("Led by licensed specialists with fifteen to twenty years of experience.", 0.7),
    ("Less tension. Easier movement. Deeper sleep.", 0.8),
    ("Mudras. Bespoke therapeutic massage, in Chelsea, New York.", 0.5),
    ("Book your BodyReset today.", 0.0),
]
k = Kokoro('tts/kokoro-v1.0.onnx', 'tts/voices-v1.0.bin')
out, meta, tcur, sr = [], [], 0.6, 24000
out.append(np.zeros(int(0.6 * sr)))
for text, gap in LINES:
    y, sr = k.create(text, voice=VOICE, speed=0.94, lang='en-us')
    nz = np.nonzero(np.abs(y) > 0.01)[0]
    y = y[max(0, nz[0] - 240): nz[-1] + 1200]
    meta.append({'text': text, 's': round(tcur, 3), 'e': round(tcur + len(y) / sr, 3)})
    out += [y, np.zeros(int(gap * sr))]
    tcur += len(y) / sr + gap
sf.write(f'audio/vo_{VOICE}.wav', np.concatenate(out), sr)
json.dump(meta, open(f'audio/vo_{VOICE}.json', 'w'), indent=1)
print(VOICE, 'total', round(tcur, 2))
