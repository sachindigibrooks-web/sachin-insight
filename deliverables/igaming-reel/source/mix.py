"""Voice + ducked music + timed SFX -> mix.wav (60.1 s, -14 LUFS)."""
import os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
A = lambda *p: os.path.join(HERE, "assets", *p)
TOTAL = 60.1

SFX = [  # (file, time, gain dB)
    *[("whoosh_fast", t, -7) for t in (0.05, 7.10, 11.10, 22.10, 28.05)],
    *[("pop_hard", t + .35, -10) for t in (0.05, 7.10, 11.10, 22.10, 28.05)],
    *[("correct", t, -9) for t in (4.84, 10.10, 25.45)],
    ("riser", 30.30, -9), ("impact", 33.05, -7),
    *[("sweep", t - .1, -11) for t in (4.75, 13.97, 15.70, 39.40, 43.40, 49.70, 52.00)],
    *[("ui_click", t, -9) for t in (20.15, 34.50, 37.25, 43.05, 46.40)],
    ("tech_slide", 50.55, -12), ("tech_slide", 52.90, -12), ("confirm", 57.60, -9),
    ("glitch_hit", 49.70, -14), ("pop_whoosh", 58.70, -6), ("shutter", 58.72, -10),
]


def main():
    cmd = ["ffmpeg", "-v", "error", "-y",
           "-i", os.path.join(HERE, "src", "reel.mp4"),
           "-ss", "8", "-i", A("music", "69.mp3")]
    for f, _, _ in SFX:
        cmd += ["-i", A("sfx", f + ".mp3")]
    fc = [
        # voice: tidy low end, gentle compression, pad to full length
        "[0:a]highpass=f=80,acompressor=threshold=-20dB:ratio=3:attack=5:release=120:makeup=3,apad=whole_dur=%s[vox]" % TOTAL,
        "[vox]asplit=2[voxm][voxsc]",
        # music: bed level, ducked by the voice, swell for the outro
        "[1:a]atrim=0:%s,asetpts=PTS-STARTPTS,volume=-15dB,afade=t=in:d=0.6,afade=t=out:st=%s:d=1.0,"
        "volume='if(gte(t,58.6),2.2,1)':eval=frame[mus0]" % (TOTAL, TOTAL - 1.0),
        "[mus0][voxsc]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=350:makeup=1[mus]",
    ]
    labels = []
    for i, (f, t, g) in enumerate(SFX):
        ms = int(t * 1000)
        fc.append(f"[{i + 2}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={g}dB,adelay={ms}|{ms}[s{i}]")
        labels.append(f"[s{i}]")
    fc.append(f"[voxm][mus]{''.join(labels)}amix=inputs={2 + len(SFX)}:normalize=0:duration=first,"
              f"atrim=0:{TOTAL},loudnorm=I=-14:TP=-1.0:LRA=9[out]")
    cmd += ["-filter_complex", ";".join(fc), "-map", "[out]", "-ar", "48000", "-ac", "2", os.path.join(HERE, "mix.wav")]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        print(r.stderr[-3000:]); raise SystemExit(1)
    print("mix.wav ok")


if __name__ == "__main__":
    main()
