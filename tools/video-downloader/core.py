"""Download engine for the video downloader, built on yt-dlp.

Kept free of any GUI code so it can be used from the command line or tested
headlessly.
"""

import shutil
from dataclasses import dataclass

import yt_dlp


@dataclass
class Option:
    label: str
    format: str
    audio_only: bool = False


def ffmpeg_location():
    """Return an ffmpeg binary: the one on PATH, else the bundled imageio-ffmpeg one."""
    found = shutil.which("ffmpeg")
    if found:
        return found
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None


def fetch_info(url):
    """Return (title, duration_seconds, options) for a video URL, best quality first."""
    opts = {"quiet": True, "no_warnings": True, "noplaylist": True, "skip_download": True}
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)

    heights = {}
    for f in info.get("formats") or []:
        h = f.get("height")
        if not h or f.get("vcodec") in (None, "none"):
            continue
        fps = f.get("fps") or 0
        heights[h] = max(heights.get(h, 0), fps)

    options = []
    for h in sorted(heights, reverse=True):
        fps = heights[h]
        name = {4320: "8K", 2160: "4K", 1440: "2K"}.get(h, "")
        label = f"{h}p" + (f"{int(fps)}" if fps > 30 else "") + (f"  ({name})" if name else "")
        options.append(Option(label, f"bestvideo[height<={h}]+bestaudio/best[height<={h}]"))
    options.append(Option("Audio only - MP3 (best quality)", "bestaudio/best", audio_only=True))
    if len(options) == 1:
        # Site exposed no per-resolution formats; let yt-dlp pick the best it has.
        options.insert(0, Option("Best available", "bestvideo+bestaudio/best"))
    return info.get("title", "video"), info.get("duration"), options


def download(url, option, out_dir, container="mp4", progress=None):
    """Download `url` using `option` into `out_dir`.

    `progress(percent, text)` is called as the download advances.
    """
    def hook(d):
        if not progress:
            return
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            done = d.get("downloaded_bytes") or 0
            pct = done * 100 / total if total else 0
            speed = d.get("speed") or 0
            eta = d.get("eta")
            text = f"{pct:5.1f}%  {done / 1e6:.1f}/{total / 1e6:.1f} MB  {speed / 1e6:.2f} MB/s"
            if eta is not None:
                text += f"  ETA {int(eta)}s"
            progress(pct, text)
        elif d["status"] == "finished":
            progress(100, "Processing (merging audio + video)...")

    opts = {
        "format": option.format,
        "outtmpl": f"{out_dir}/%(title)s [%(height)sp].%(ext)s" if not option.audio_only
        else f"{out_dir}/%(title)s.%(ext)s",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
        "progress_hooks": [hook],
        "concurrent_fragment_downloads": 8,  # parallel chunks, IDM-style
        "windowsfilenames": True,
    }
    ff = ffmpeg_location()
    if ff:
        opts["ffmpeg_location"] = ff
    if option.audio_only:
        opts["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3",
                                   "preferredquality": "0"}]
    else:
        opts["merge_output_format"] = container

    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        sys.exit("usage: python core.py <url> [option-number] [output-dir]")
    title, _, options = fetch_info(sys.argv[1])
    print(title)
    for i, o in enumerate(options, 1):
        print(f"  {i}. {o.label}")
    if len(sys.argv) > 2:
        choice = options[int(sys.argv[2]) - 1]
        download(sys.argv[1], choice, sys.argv[3] if len(sys.argv) > 3 else ".",
                 progress=lambda p, t: print("\r" + t, end="", flush=True))
        print("\nDone")
