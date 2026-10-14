"""Pick the cleanest take per line (Whisper transcript vs script), trim silences, and lay the lines out with
hand-set pauses so the read breathes like a person, not a sentence queue. Writes public/voice.wav."""
import difflib, json, re
import numpy as np
import librosa
import soundfile as sf
from faster_whisper import WhisperModel

SR = 48000
LINES = json.load(open('audio/takes/lines.json'))
norm = lambda s: re.sub(r"[^a-z0-9' ]", ' ', s.lower().replace('nineteen oh eight', '1908')).split()
model = WhisperModel('small.en', device='cpu', compute_type='int8')
out, report = [np.zeros(int(0.2 * SR))], []
for i, (txt, gap, ex, cfg) in enumerate(LINES):
    best = None
    for k in range(2):
        y, _ = librosa.load(f'audio/takes/l{i:02d}_t{k}.wav', sr=SR)
        y, _ = librosa.effects.trim(y, top_db=42, frame_length=1024, hop_length=256)
        y16 = librosa.resample(y, orig_sr=SR, target_sr=16000)
        heard = ' '.join(s.text for s in model.transcribe(y16, language='en', beam_size=5)[0])
        score = difflib.SequenceMatcher(None, norm(txt), norm(heard)).ratio()
        # long tails after the last word usually mean a mumble or artefact: small penalty per extra second
        score -= 0.02 * max(0, len(y) / SR - 0.075 * len(txt))
        if best is None or score > best[0]:
            best = (score, k, y, heard)
    score, k, y, heard = best
    fade = int(0.012 * SR)
    y[:fade] *= np.linspace(0, 1, fade); y[-fade:] *= np.linspace(1, 0, fade)
    out += [y, np.zeros(int(gap * SR))]
    report.append(dict(line=i, take=k, score=round(score, 3), dur=round(len(y) / SR, 2), heard=heard.strip()))
    print(i, k, round(score, 3), '|', txt, '|', heard.strip())
v = np.concatenate(out + [np.zeros(int(0.3 * SR))])
v *= 0.89 / np.abs(v).max()
sf.write('public/voice.wav', v.astype(np.float32), SR, subtype='FLOAT')
json.dump(report, open('audio/takes/picked.json', 'w'), indent=1)
print('voice', round(len(v) / SR, 2), 's')
