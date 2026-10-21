import json, subprocess, os
S = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(f"{S}/out/sfx.json"))
total = d["total"]
inputs = ["-i", f"{S}/vo/vo.wav", "-stream_loop", "-1", "-i", f"{S}/sfx/m614.mp3"]
filt = [
    # voice: light warmth + presence, compression
    "[0]highpass=f=70,equalizer=f=180:t=q:w=1:g=2,equalizer=f=3500:t=q:w=1.2:g=2.5,acompressor=threshold=-20dB:ratio=3:attack=5:release=120,volume=1.6,asplit=2[vo][vosc]",
    f"[1]atrim=0:{total},volume=-17dB,afade=t=in:d=1.5,afade=t=out:st={total-2.5}:d=2.5[mus]",
    "[mus][vosc]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=350[duck]",
]
labels = ["[vo]", "[duck]"]
for i, (name, t, vol) in enumerate(d["sfx"]):
    inputs += ["-i", f"{S}/sfx/{name}.mp3"]
    k = i + 2
    dur = "atrim=0:1.2," if name == "s1059" else ""
    if name == "s1059": dur = "atrim=0:3.2,"
    filt.append(f"[{k}]{dur}volume={vol}dB,adelay={max(0,int(t*1000))}:all=1[s{i}]")
    labels.append(f"[s{i}]")
filt.append("".join(labels) + f"amix=inputs={len(labels)}:normalize=0,atrim=0:{total},alimiter=limit=0.95,loudnorm=I=-14:TP=-1.5:LRA=11[out]")
subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(filt), "-map", "[out]", "-ar", "48000", f"{S}/out/mix.wav"], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{S}/out/video_noaudio.mp4", "-i", f"{S}/out/mix.wav", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", f"{S}/out/seth_godin_reel.mp4"], check=True)
print("ok")
