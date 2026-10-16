# Word timestamps for the talking-head clip (faster-whisper medium, language auto-detected). Writes scripts/words.json.
import json, subprocess
import numpy as np
from faster_whisper import WhisperModel
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', 'public/clip.mp4', '-ac', '1', '-ar', '16000', '-f', 'f32le', '-'], capture_output=True, check=True).stdout
audio = np.frombuffer(raw, dtype=np.float32)
segs, info = WhisperModel('medium', device='cpu', compute_type='int8').transcribe(audio, word_timestamps=True, beam_size=5)
segs = list(segs)
print('language', info.language, round(info.language_probability, 2))
for s in segs: print(f'{s.start:6.2f}-{s.end:6.2f} {s.text}')
json.dump([{'w': w.word.strip(), 's': round(w.start, 3), 'e': round(w.end, 3)} for s in segs for w in s.words], open('scripts/words.json', 'w'), ensure_ascii=False)
