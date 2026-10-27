"""Build the 1080x1920 base edit (no graphics): split-screen questions, speaker punch-ins, b-roll cutaways."""
import os, subprocess, json, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src", "reel.mp4")
BR = os.path.join(HERE, "assets", "broll")
FMT = sys.argv[1] if len(sys.argv) > 1 else "v"   # v = 1080x1920 reel, h = 1920x1080 YouTube
SEG = os.path.join(HERE, "seg_" + FMT); os.makedirs(SEG, exist_ok=True)
FPS = 30
END = 58.5667

# face centres in the 1920x1080 source (constant across shots)
HOST_X, GUEST_X = 600, 1380
# (start, end, kind, extra)
TIMELINE = [
    (0.00, 2.83, "stack", {}),
    (2.83, 4.75, "guest", {"z0": 1.00, "z1": 1.06}),
    (4.75, 7.03, "broll", {"clip": "b2569.mp4", "cx": 640, "ss": 1.0}),
    (7.03, 10.05, "stack", {}),
    (10.05, 11.07, "guest", {"z0": 1.14, "z1": 1.18}),
    (11.07, 13.97, "stack", {}),
    (13.97, 15.70, "broll", {"clip": "b4163.mp4", "cx": 960, "ss": 2.0}),
    (15.70, 17.90, "broll", {"clip": "b43524.mp4", "cx": 560, "ss": 1.0}),
    (17.90, 22.03, "guest", {"z0": 1.00, "z1": 1.10}),
    (22.03, 25.45, "stack", {}),
    (25.45, 28.00, "guest", {"z0": 1.04, "z1": 1.12}),
    (28.00, 32.90, "stack", {}),
    (32.90, 34.07, "guest", {"z0": 1.18, "z1": 1.24}),
    (34.07, 36.87, "host", {"z0": 1.00, "z1": 1.08}),
    (36.87, 39.40, "guest", {"z0": 1.00, "z1": 1.06}),
    (39.40, 41.40, "broll", {"clip": "b2561.mp4", "cx": 1400, "ss": 3.0}),
    (41.40, 43.40, "guest", {"z0": 1.08, "z1": 1.12}),
    (43.40, 45.80, "broll", {"clip": "b49723.mp4", "cx": 520, "ss": 0.3}),
    (45.80, 49.70, "host", {"z0": 1.00, "z1": 1.10}),
    (49.70, 52.00, "broll", {"clip": "b51214.mp4", "cx": 720, "ss": 2.0}),
    (52.00, 54.23, "broll", {"clip": "b50109.mp4", "cx": 940, "ss": 1.0}),
    (54.23, END, "guest", {"z0": 1.00, "z1": 1.12}),
]

GRADE = "eq=contrast=1.06:saturation=1.10:gamma=0.98,unsharp=5:5:0.6"


def single(cx, z0, z1, dur):
    """9:16 crop around cx with a slow push-in from z0 to z1."""
    n = dur * FPS
    return (f"crop=608:1080:{cx - 304}:0,scale=1080:1920:flags=lanczos,"
            f"zoompan=z='{z0}+({z1}-{z0})*on/{n:.1f}':x='iw/2-(iw/zoom/2)':y='(ih-ih/zoom)*0.42':d=1:s=1080x1920:fps={FPS},{GRADE}")


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        print(r.stderr[-2000:]); raise SystemExit(1)


def wide(cx, z0, z1, dur, cy=420):
    """16:9 punch-in around (cx, cy) from z0 to z1."""
    n = dur * FPS
    return (f"scale=1920:1080,zoompan=z='{z0}+({z1}-{z0})*on/{n:.1f}':"
            f"x='max(0,min(iw-iw/zoom,{cx}-iw/zoom/2))':y='max(0,min(ih-ih/zoom,{cy}-ih/zoom/2))':d=1:s=1920x1080:fps={FPS},{GRADE}")


def build():
    files = []
    for i, (a, b, kind, ex) in enumerate(TIMELINE):
        d = b - a
        out = os.path.join(SEG, f"s{i:02d}.mp4"); files.append(out)
        nf = round(b * FPS) - round(a * FPS)
        enc = ["-frames:v", str(nf), "-r", str(FPS), "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", out]
        if FMT == "h":
            if kind == "stack":
                vf = wide(960, 1.0, 1.04, d, cy=540)
            elif kind in ("guest", "host"):
                cx = GUEST_X if kind == "guest" else HOST_X
                vf = wide(cx, 1.35 + (ex["z0"] - 1), 1.35 + (ex["z1"] - 1), d)
            else:
                vf = None
            if vf:
                run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a}", "-t", f"{d + 0.5}", "-i", SRC, "-vf", vf] + enc)
            else:
                clip = os.path.join(BR, ex["clip"])
                vf = (f"setpts=PTS-STARTPTS,fps={FPS},scale=1920:1080:flags=lanczos,"
                      f"zoompan=z='1.0+0.0007*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1920x1080:fps={FPS},{GRADE}")
                run(["ffmpeg", "-v", "error", "-y", "-ss", f"{ex['ss']}", "-t", f"{d + 0.5}", "-i", clip, "-vf", vf] + enc)
        elif kind == "stack":
            # host on top, guest below, each 1080x960 from a 960x853 window
            fc = (f"[0:v]split[a][b];"
                  f"[a]crop=960:853:{HOST_X-480}:170,scale=1080:960:flags=lanczos,{GRADE}[t];"
                  f"[b]crop=960:853:{GUEST_X-480}:170,scale=1080:960:flags=lanczos,{GRADE}[u];"
                  f"[t][u]vstack[v]")
            run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a}", "-t", f"{d + 0.5}", "-i", SRC, "-filter_complex", fc, "-map", "[v]"] + enc)
        elif kind in ("guest", "host"):
            cx = GUEST_X if kind == "guest" else HOST_X
            run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a}", "-t", f"{d + 0.5}", "-i", SRC, "-vf", single(cx, ex["z0"], ex["z1"], d)] + enc)
        else:
            clip = os.path.join(BR, ex["clip"])
            vf = (f"setpts=PTS-STARTPTS,fps={FPS},crop=607:1080:{ex['cx']}-303:0,scale=1080:1920:flags=lanczos,"
                  f"zoompan=z='1.0+0.0009*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps={FPS},{GRADE}")
            run(["ffmpeg", "-v", "error", "-y", "-ss", f"{ex['ss']}", "-t", f"{d + 0.5}", "-i", clip, "-vf", vf] + enc)
        print(i, kind, round(d, 2))
    lst = os.path.join(SEG, "list.txt")
    open(lst, "w").write("".join(f"file '{f}'\n" for f in files))
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", os.path.join(HERE, f"base_{FMT}.mp4")])
    json.dump(TIMELINE, open(os.path.join(HERE, "timeline.json"), "w"))


if __name__ == "__main__":
    build()
