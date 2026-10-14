# Word-level timestamps for the voice take (faster-whisper, Hindi). Writes scripts/words_raw.json.
import json, subprocess
import numpy as np
from faster_whisper import WhisperModel

subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'public/voice.mp3', '-ac', '1', '-ar', '16000', '-f', 'f32le', 'scripts/voice16k.raw'], check=True)
audio = np.fromfile('scripts/voice16k.raw', dtype=np.float32)
model = WhisperModel('medium', device='cpu', compute_type='int8')
segments, _ = model.transcribe(audio, language='hi', word_timestamps=True)
words = [{'w': w.word.strip(), 's': round(w.start, 2), 'e': round(w.end, 2)} for s in segments for w in s.words]
json.dump(words, open('scripts/words_raw.json', 'w'), ensure_ascii=False)
print(len(words), 'words')
