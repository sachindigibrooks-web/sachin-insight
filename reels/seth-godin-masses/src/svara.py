import sys, os, time, json
import numpy as np, torch, soundfile as sf
from llama_cpp import Llama
from snac import SNAC

S = os.path.dirname(os.path.abspath(__file__))
_llm = None; _snac = None

def models():
    global _llm, _snac
    if _llm is None:
        _llm = Llama(model_path=f"{S}/models/svara-q6.gguf", n_ctx=4096, n_threads=4, verbose=False, logits_all=False)
        _snac = SNAC.from_pretrained("hubertsiuzdak/snac_24khz").eval()
    return _llm, _snac

def tts(text, speaker="Hindi (Male)", style="", temp=0.7, top_p=0.8, rep=1.1, seed=0, max_tokens=2800):
    llm, snac = models()
    prompt = f"{speaker}: {text}" + (f" <{style}>" if style else "")
    ids = [128259] + llm.tokenize(prompt.encode(), add_bos=True, special=True) + [128009, 128260]
    llm.reset(); llm.set_seed(seed) if hasattr(llm, "set_seed") else None
    out = []
    for tok in llm.generate(ids, temp=temp, top_p=top_p, repeat_penalty=rep, reset=True):
        if tok == 128258 or len(out) > max_tokens: break
        out.append(tok)
    if 128257 in out: out = out[len(out) - out[::-1].index(128257):]
    codes = [t - 128266 for t in out if t >= 128266]
    codes = codes[: len(codes) // 7 * 7]
    l1, l2, l3 = [], [], []
    for i in range(len(codes) // 7):
        b = 7 * i
        l1.append(codes[b]); l2.append(codes[b + 1] - 4096)
        l3 += [codes[b + 2] - 2 * 4096, codes[b + 3] - 3 * 4096]
        l2.append(codes[b + 4] - 4 * 4096)
        l3 += [codes[b + 5] - 5 * 4096, codes[b + 6] - 6 * 4096]
    if not l1: return np.zeros(2400, np.float32)
    bad = any(not (0 <= c < 4096) for c in l1 + l2 + l3)
    if bad:
        l1 = [min(max(c, 0), 4095) for c in l1]; l2 = [min(max(c, 0), 4095) for c in l2]; l3 = [min(max(c, 0), 4095) for c in l3]
    with torch.inference_mode():
        audio = snac.decode([torch.tensor(x).unsqueeze(0) for x in (l1, l2, l3)]).squeeze().numpy()
    return audio.astype(np.float32)

if __name__ == "__main__":
    t = time.time()
    a = tts(sys.argv[1], speaker=sys.argv[2] if len(sys.argv) > 2 else "Hindi (Male)", style=sys.argv[3] if len(sys.argv) > 3 else "")
    sf.write(sys.argv[4] if len(sys.argv) > 4 else f"{S}/test.wav", a, 24000)
    print(f"{len(a)/24000:.2f}s audio in {time.time()-t:.1f}s")
