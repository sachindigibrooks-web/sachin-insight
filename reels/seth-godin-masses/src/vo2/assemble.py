import json, subprocess, os
import numpy as np, soundfile as sf, scipy.signal as ss
d = os.path.dirname(os.path.abspath(__file__))
lines = json.load(open(f"{d}/lines.json"))
SR = 48000; HOP = 0.02
def voiced(a):
    f = int(SR * HOP)
    e = np.array([np.sqrt((a[i:i + f] ** 2).mean()) for i in range(0, len(a) - f, f)])
    thr = max(0.012, np.percentile(e, 90) * 0.12)
    v = e > thr
    # close short gaps (<140ms) and drop blips (<60ms)
    segs = []; i = 0
    while i < len(v):
        if v[i]:
            j = i
            while j < len(v) and v[j]: j += 1
            segs.append([i * HOP, j * HOP]); i = j
        else: i += 1
    m = []
    for s in segs:
        if m and s[0] - m[-1][1] < 0.14: m[-1][1] = s[1]
        else: m.append(s)
    return [s for s in m if s[1] - s[0] >= 0.06]
t = 0.25; tl = []; track = np.zeros(int(SR * 200), np.float32)
for l in lines:
    a, sr = sf.read(f"{d}/{l['id']}.wav", dtype="float32")
    a = ss.resample_poly(a, 2, 1).astype(np.float32)
    seg = voiced(a)
    st, en = max(0, seg[0][0] - 0.04), min(len(a) / SR, seg[-1][1] + 0.12)
    a = a[int(st * SR):int(en * SR)]
    seg = [[x - st, y - st] for x, y in seg]
    caps = l["cap"].split()
    wts = [max(1, len(c.strip('".,—?…'))) + 1.5 for c in caps]
    tot_v = sum(y - x for x, y in seg); tot_w = sum(wts)
    def vt(frac):  # fraction of voiced time -> absolute time in clip
        rem = frac * tot_v
        for x, y in seg:
            if rem <= y - x: return x + rem
            rem -= y - x
        return seg[-1][1]
    acc = 0; cw = []
    for c, w in zip(caps, wts):
        s0 = vt(acc / tot_w); acc += w; s1 = vt(acc / tot_w)
        cw.append([t + s0, t + s1, c])
    n = len(a); i0 = int(t * SR)
    track[i0:i0 + n] += a
    tl.append({"id": l["id"], "start": t, "end": t + n / SR, "words": cw, "cap": l["cap"]})
    t += n / SR + l["gap"]
total = t + 0.3
track = track[:int(total * SR)]
sf.write(f"{d}/vo.wav", track, SR)
json.dump({"total": total, "lines": tl}, open(f"{d}/timeline.json", "w"), ensure_ascii=False, indent=1)
for x in tl: print(f"{x['id']:4} {x['start']:6.2f}-{x['end']:6.2f}  {x['cap']}")
print("TOTAL", total)
