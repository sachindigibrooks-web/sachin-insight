"""Download engine for the video downloader, built on yt-dlp.

Kept free of any GUI code so it can be used from the command line or tested
headlessly. Works with YouTube and the 1000+ other sites yt-dlp supports
(Instagram, Facebook, X/Twitter, TikTok, Vimeo, Dailymotion, Reddit, ...).
"""

import os
import shutil
from dataclasses import dataclass, field

import yt_dlp

# Sites shown in the apps; yt-dlp supports many more.
POPULAR_SITES = ["YouTube", "Instagram", "Facebook", "X / Twitter", "TikTok", "Vimeo",
                 "Dailymotion", "Reddit", "Twitch", "SoundCloud", "Pinterest", "LinkedIn"]

# Browsers whose saved login yt-dlp can reuse (for private / login-only videos).
BROWSERS = ["firefox", "chrome", "edge", "brave", "opera", "vivaldi", "safari"]

# Offered for playlists, where each video can have different qualities.
PLAYLIST_HEIGHTS = [2160, 1440, 1080, 720, 480, 360]
HEIGHT_NAMES = {4320: "8K", 2160: "4K", 1440: "2K"}


@dataclass
class Option:
    label: str
    format: str
    audio_only: bool = False


@dataclass
class Info:
    title: str
    duration: float | None
    thumbnail: str | None
    options: list
    site: str = ""
    is_playlist: bool = False
    entries: list = field(default_factory=list)  # playlist video titles
    has_playlist: bool = False  # a single video whose URL also names a playlist


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


def video_option(h, fps=0, up_to=False):
    name = HEIGHT_NAMES.get(h, "")
    label = ("Up to " if up_to else "") + f"{h}p" + (f"{int(fps)}" if fps > 30 else "")
    if name:
        label += f"  ({name})"
    # The trailing /best keeps sites whose formats lack height info working.
    return Option(label, f"bestvideo[height<={h}]+bestaudio/best[height<={h}]/best")


AUDIO_OPTION = Option("Audio only - MP3 (best quality)", "bestaudio/best", audio_only=True)


def base_opts(browser=None):
    opts = {"quiet": True, "no_warnings": True}
    if browser:
        opts["cookiesfrombrowser"] = (browser,)
    return opts


def fetch_info(url, playlist=False, browser=None):
    """Describe `url`: a single video, or (with `playlist`, or for a playlist-only URL) a playlist.

    `browser` (one of BROWSERS) reuses that browser's login. Options are
    ordered best quality first.
    """
    opts = base_opts(browser) | {"skip_download": True, "noplaylist": not playlist,
                                 "extract_flat": "in_playlist"}
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)
    site = info.get("extractor_key") or ""

    if info.get("_type") == "playlist":
        # Some sites list only URLs in a quick playlist read; show the URL's last part then.
        entries = [e.get("title") or (e.get("url") or "?").rstrip("/").rsplit("/", 1)[-1]
                   for e in info.get("entries") or []]
        if not entries:
            raise ValueError("This playlist is empty or private.")
        thumbs = (info.get("thumbnails") or [{}])
        options = [video_option(h, up_to=True) for h in PLAYLIST_HEIGHTS] + [AUDIO_OPTION]
        return Info(info.get("title") or "playlist", None, thumbs[-1].get("url"), options,
                    site, is_playlist=True, entries=entries)

    heights = {}
    for f in info.get("formats") or []:
        h = f.get("height")
        if not h or f.get("vcodec") in (None, "none"):
            continue
        heights[h] = max(heights.get(h, 0), f.get("fps") or 0)

    options = [video_option(h, heights[h]) for h in sorted(heights, reverse=True)]
    if not options:
        # Site exposed no per-resolution formats; let yt-dlp pick the best it has.
        options.append(Option("Best available", "bestvideo+bestaudio/best"))
    options.append(AUDIO_OPTION)
    return Info(info.get("title") or "video", info.get("duration"), info.get("thumbnail"),
                options, site, has_playlist="list=" in url and not playlist)


def download(url, option, out_dir, container="mp4", progress=None, playlist=False, items=None,
             browser=None):
    """Download `url` using `option` into `out_dir`.

    With `playlist`, every video goes into a sub-folder named after the
    playlist; unavailable videos are skipped. `items` picks videos by
    position, e.g. "1-10" or "1,3,5-7" (all when empty). `progress(percent, text)` is
    called as the download advances. Returns non-zero if any video failed.
    """
    items = (items or "").replace(" ", "") if playlist else ""
    picked = count_items(items)

    def hook(d):
        if not progress:
            return
        info = d.get("info_dict") or {}
        # playlist_autonumber counts only the picked videos, so "Video 2/3" stays right with `items`.
        idx = info.get("playlist_autonumber") or info.get("playlist_index")
        count = picked or info.get("n_entries") or info.get("playlist_count")
        prefix = f"Video {idx}/{count}:  " if playlist and idx and count else ""
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            done = d.get("downloaded_bytes") or 0
            pct = done * 100 / total if total else 0
            speed = d.get("speed") or 0
            eta = d.get("eta")
            text = f"{pct:5.1f}%  {done / 1e6:.1f}/{total / 1e6:.1f} MB  {speed / 1e6:.2f} MB/s"
            if eta is not None:
                text += f"  ETA {int(eta)}s"
            if prefix:
                pct = ((idx - 1) + pct / 100) * 100 / count
            progress(pct, prefix + text)
        elif d["status"] == "finished":
            pct = idx * 100 / count if prefix else 100
            progress(pct, prefix + "Processing (merging audio + video)...")

    name = "%(title)s.%(ext)s" if option.audio_only else "%(title)s [%(height)sp].%(ext)s"
    if playlist:
        name = os.path.join("%(playlist_title,playlist,playlist_id|Playlist)s", "%(playlist_index)03d - " + name)
    opts = base_opts(browser) | {
        "format": option.format,
        "outtmpl": os.path.join(out_dir, name),
        "noplaylist": not playlist,
        "ignoreerrors": playlist,  # one private/deleted video shouldn't stop the playlist
        "noprogress": True,
        "progress_hooks": [hook],
        "concurrent_fragment_downloads": 8,  # parallel chunks, IDM-style
        "windowsfilenames": True,
    }
    if items:
        opts["playlist_items"] = items
    ff = ffmpeg_location()
    if ff:
        opts["ffmpeg_location"] = ff
    if option.audio_only:
        opts["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3",
                                   "preferredquality": "0"}]
    else:
        opts["merge_output_format"] = container

    with yt_dlp.YoutubeDL(opts) as ydl:
        return ydl.download([url])


def friendly_error(e):
    """Turn a yt-dlp error into a short message a non-technical user can act on."""
    msg = str(e).replace("ERROR: ", "")
    low = msg.lower()
    if "not a bot" in low:
        return ("YouTube blocked this internet connection (common on VPN / cloud servers). "
                "Turn off the VPN or try your home internet.")
    if "could not copy" in low and "cookie" in low or "failed to decrypt" in low:
        return ("Could not read the browser's login. Close that browser completely and try "
                "again, or pick Firefox.")
    if any(k in low for k in ("login", "log in", "sign in", "authentication", "cookies",
                              "private", "rate-limit", "age-restricted", "confirm your age")):
        return ("This video needs a login. Log in to the site in your browser, then pick that "
                "browser in 'Use login from' and try again.")
    if "unsupported url" in low:
        return "This website is not supported, or the link is not a video page."
    if "no video" in low:
        return "No video found at this link."
    if "unexpected response" in low or "http error 403" in low:
        return ("The site refused the request. Update the downloader (pip install -U yt-dlp), "
                "or try again later.")
    return msg.split(". See ")[0].split("; please report")[0][:300]


def count_items(items):
    """Number of videos named by a spec like "1-10,15", or None if it can't be counted."""
    if not items:
        return None
    try:
        total = 0
        for part in items.split(","):
            a, _, b = part.partition("-")
            total += int(b) - int(a) + 1 if b else 1
        return total if total > 0 else None
    except ValueError:
        return None


def valid_items(items):
    items = (items or "").replace(" ", "")
    return not items or count_items(items) is not None


if __name__ == "__main__":
    import sys

    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    pl = "--playlist" in sys.argv
    items = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--items=")), None)
    if not args:
        sys.exit("usage: python core.py <url> [option-number] [output-dir] [--playlist] [--items=1-10]")
    info = fetch_info(args[0], pl)
    print(f"[{info.site}] {info.title}")
    if info.is_playlist:
        print(f"  Playlist with {len(info.entries)} videos")
    for i, o in enumerate(info.options, 1):
        print(f"  {i}. {o.label}")
    if len(args) > 1:
        choice = info.options[int(args[1]) - 1]
        failed = download(args[0], choice, args[2] if len(args) > 2 else ".",
                          progress=lambda p, t: print(f"\r{p:5.1f}% | {t}", end="", flush=True),
                          playlist=info.is_playlist, items=items)
        print("\nDone" + (" (some videos failed)" if failed else ""))
