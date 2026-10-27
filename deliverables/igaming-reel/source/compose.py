"""Final render: base edit + graphics overlay + audio mix, with a 1.5 s blurred outro tail."""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOTAL = 60.1
NAMES = {"v": "iGaming-Real-Talk_Reel_9x16_1080x1920.mp4", "h": "iGaming-Real-Talk_YouTube_16x9_1920x1080.mp4"}


def render(fmt):
    out = os.path.join(HERE, "final", NAMES[fmt]); os.makedirs(os.path.dirname(out), exist_ok=True)
    fc = ("[0:v]tpad=stop_mode=clone:stop_duration=1.6,trim=0:%s,setpts=PTS-STARTPTS,"
          "boxblur=luma_radius=18:luma_power=2:enable='gte(t,58.6)'[b];"
          "[1:v]format=rgba[o];[b][o]overlay=0:0:format=auto:eof_action=repeat,format=yuv420p[v]" % TOTAL)
    cmd = ["ffmpeg", "-v", "error", "-y",
           "-i", os.path.join(HERE, f"base_{fmt}.mp4"),
           "-framerate", "30", "-i", os.path.join(HERE, f"ov_{fmt}", "%05d.png"),
           "-i", os.path.join(HERE, "mix.wav"),
           "-filter_complex", fc, "-map", "[v]", "-map", "2:a",
           "-t", str(TOTAL), "-r", "30",
           "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-profile:v", "high", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        print(r.stderr[-3000:]); raise SystemExit(1)
    print(out)


if __name__ == "__main__":
    for f in (sys.argv[1:] or ["v", "h"]):
        render(f)
