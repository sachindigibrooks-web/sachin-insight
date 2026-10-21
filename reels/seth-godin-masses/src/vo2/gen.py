import json, os, sys, time, difflib, re
import numpy as np, soundfile as sf, scipy.signal as ss
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from svara import tts
from faster_whisper import WhisperModel
d = os.path.dirname(os.path.abspath(__file__))
lines = json.load(open(f"{d}/lines.json"))
asr = WhisperModel("medium", device="cpu", compute_type="int8")
def norm(s): return re.sub(r"[^\w]", "", s.lower().replace("़", ""))
def check(a, ref, lang):
    segs, _ = asr.transcribe(ss.resample_poly(a, 2, 3).astype(np.float32), language=lang)
    hyp = " ".join(s.text for s in segs)
    return difflib.SequenceMatcher(None, norm(ref), norm(hyp)).ratio(), hyp
only = sys.argv[1:]
for l in lines:
    if only and l["id"] not in only: continue
    out = f"{d}/{l['id']}.wav"
    if os.path.exists(out) and not only: continue
    best = None
    for seed in range(3):
        t = time.time()
        a = tts(l["tts"], speaker="Hindi (Male)", seed=seed)
        sc, hyp = check(a, l["tts"], l.get("lang", "hi"))
        dur = len(a) / 24000
        # penalise runaway generations (too long for the text)
        if dur > len(l["tts"]) * 0.16 + 2: sc -= 0.3
        print(f"{l['id']} seed{seed} score={sc:.2f} dur={dur:.1f}s ({time.time()-t:.0f}s) :: {hyp}", flush=True)
        if best is None or sc > best[0]: best = (sc, a)
        if sc >= 0.82: break
    sf.write(out, best[1], 24000)
print("ALLDONE", flush=True)
