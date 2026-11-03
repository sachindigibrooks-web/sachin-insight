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
    height: int | None = None
    size: int | None = None  # estimated bytes for the whole video, when known


@dataclass
class Extras:
    """Optional features, all off by default."""
    start: float | None = None  # clip: seconds into the video
    end: float | None = None
    sponsorblock: bool = False  # cut sponsors / intros / outros (YouTube)
    budget_mb: float | None = None  # playlists: keep the whole download under this size
    subs_lang: str | None = None  # extras.LANGUAGES code, or extras.ORIGINAL
    subs_mode: str = "embed"  # embed | burn | srt
    ai_model: str = "accurate"  # accurate | fast
    whatsapp_mb: int | None = None  # also make a copy that fits in this many MB

    def needs_processing(self):
        return bool(self.subs_lang or self.whatsapp_mb)


@dataclass
class Result:
    failed: bool  # some playlist videos could not be downloaded
    files: list  # final file paths (videos, subtitles, WhatsApp copies)
    warnings: list


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


def video_option(h, fps=0, up_to=False, size=None):
    name = HEIGHT_NAMES.get(h, "")
    label = ("Up to " if up_to else "") + f"{h}p" + (f"{int(fps)}" if fps > 30 else "")
    if name:
        label += f"  ({name})"
    if size:
        label += f"   ~{human_size(size)}"
    # The trailing /best keeps sites whose formats lack height info working.
    return Option(label, f"bestvideo[height<={h}]+bestaudio/best[height<={h}]/best",
                  height=h, size=size)


AUDIO_LABEL = "Audio only - MP3 (best quality)"
AUDIO_OPTION = Option(AUDIO_LABEL, "bestaudio/best", audio_only=True)


def human_size(n):
    return f"{n / 1e9:.1f} GB" if n >= 1e9 else f"{n / 1e6:.0f} MB"


def format_size(f, duration):
    size = f.get("filesize") or f.get("filesize_approx")
    if not size and f.get("tbr") and duration:
        size = f["tbr"] * 1000 / 8 * duration
    return size


def estimate_sizes(info):
    """Estimated download size per height (and for audio only), mirroring the format choice.

    yt-dlp lists formats worst to best, so the last match is the one it picks.
    """
    fmts, dur = info.get("formats") or [], info.get("duration")
    audio = [f for f in fmts if f.get("vcodec") == "none" and f.get("acodec") not in (None, "none")]
    audio_size = format_size(audio[-1], dur) if audio else None
    sizes = {}
    for h in {f["height"] for f in fmts if f.get("height")}:
        only = [f for f in fmts if f.get("height") and f["height"] <= h and f.get("acodec") == "none"
                and f.get("vcodec") not in (None, "none")]
        both = [f for f in fmts if f.get("height") and f["height"] <= h
                and f.get("acodec") not in (None, "none") and f.get("vcodec") not in (None, "none")]
        if only and audio_size:
            v = format_size(only[-1], dur)
            sizes[h] = v + audio_size if v else None
        elif both:
            sizes[h] = format_size(both[-1], dur)
    return sizes, audio_size


def budget_format(option, per_video_mb):
    """Format for one playlist video that stays under `per_video_mb` (sizes are estimates)."""
    mb = per_video_mb
    if option.audio_only:
        return f"ba[filesize<?{mb:.1f}M][filesize_approx<?{mb:.1f}M]/wa/w"
    h, v, a = option.height or 4320, mb * 0.85, mb * 0.15
    return (f"bv[height<={h}][filesize<?{v:.1f}M][filesize_approx<?{v:.1f}M]"
            f"+ba[filesize<?{a:.1f}M][filesize_approx<?{a:.1f}M]"
            f"/b[height<={h}][filesize<?{mb:.1f}M][filesize_approx<?{mb:.1f}M]/wv+wa/w")


def parse_time(text):
    """'1:20:05', '20:05', '75' or '' -> seconds (None when empty)."""
    text = (text or "").strip()
    if not text:
        return None
    try:
        secs = 0.0
        for part in text.split(":"):
            secs = secs * 60 + float(part)
        return secs
    except ValueError:
        raise ValueError(f"Time should look like 1:20:05 or 20:05, not '{text}'.")


def base_opts(browser=None):
    opts = {"quiet": True, "no_warnings": True}
    if browser:
        opts["cookiesfrombrowser"] = (browser,)
    ff = ffmpeg_location()
    if ff:
        opts["ffmpeg_location"] = ff
        # Some yt-dlp checks (e.g. for clip downloads) ignore the option and read this
        # per-thread default instead; without it the bundled ffmpeg of the .exe isn't found.
        from yt_dlp.postprocessor.ffmpeg import FFmpegPostProcessor
        FFmpegPostProcessor._ffmpeg_location.set(ff)
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

    sizes, audio_size = estimate_sizes(info)
    options = [video_option(h, heights[h], size=sizes.get(h)) for h in sorted(heights, reverse=True)]
    if not options:
        # Site exposed no per-resolution formats; let yt-dlp pick the best it has.
        options.append(Option("Best available", "bestvideo+bestaudio/best"))
    label = AUDIO_LABEL + (f"   ~{human_size(audio_size)}" if audio_size else "")
    options.append(Option(label, AUDIO_OPTION.format, audio_only=True, size=audio_size))
    return Info(info.get("title") or "video", info.get("duration"), info.get("thumbnail"),
                options, site, has_playlist="list=" in url and not playlist)


def download(url, option, out_dir, container="mp4", progress=None, playlist=False, items=None,
             browser=None, extras=None, playlist_size=None):
    """Download `url` using `option` into `out_dir`, then run the chosen `extras`.

    With `playlist`, every video goes into a sub-folder named after the
    playlist; unavailable videos are skipped. `items` picks videos by
    position, e.g. "1-10" or "1,3,5-7" (all when empty); `playlist_size` is
    the playlist's length, used to split a data budget. `progress(percent, text)`
    is called as the download advances.
    """
    x = extras or Extras()
    items = (items or "").replace(" ", "") if playlist else ""
    picked = count_items(items)
    files = []  # (final path, info) per downloaded video

    def done_hook(d):
        if d["status"] == "finished" and d["postprocessor"] == "MoveFiles":
            files.append((d["info_dict"]["filepath"], d["info_dict"]))

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
    fmt = option.format
    if playlist and x.budget_mb:
        fmt = budget_format(option, x.budget_mb / (picked or playlist_size or 1))
    opts = base_opts(browser) | {
        "format": fmt,
        "outtmpl": os.path.join(out_dir, name),
        "noplaylist": not playlist,
        "ignoreerrors": playlist,  # one private/deleted video shouldn't stop the playlist
        "noprogress": True,
        "progress_hooks": [hook],
        "postprocessor_hooks": [done_hook],
        "concurrent_fragment_downloads": 8,  # parallel chunks, IDM-style
        "windowsfilenames": True,
    }
    if items:
        opts["playlist_items"] = items
    pps = []
    if option.audio_only:
        pps.append({"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "0"})
    else:
        opts["merge_output_format"] = container
    if x.start is not None or x.end is not None:
        from yt_dlp.utils import download_range_func
        start, end = x.start or 0, x.end if x.end is not None else float("inf")
        if end <= start:
            raise ValueError("Clip end must be after the start.")
        opts["download_ranges"] = download_range_func(None, [(start, end)])
        opts["force_keyframes_at_cuts"] = True  # exact cut points (re-encodes the clip edges)
    if x.sponsorblock:
        cats = ["sponsor", "intro", "outro", "selfpromo", "interaction"]
        pps += [{"key": "SponsorBlock", "categories": cats, "when": "after_filter"},
                {"key": "ModifyChapters", "remove_sponsor_segments": cats}]
    if pps:
        opts["postprocessors"] = pps

    with yt_dlp.YoutubeDL(opts) as ydl:
        failed = bool(ydl.download([url]))

    warnings = []
    if x.needs_processing() and files:
        import extras
        warnings = extras.process(files, x, progress or (lambda p, t: None), browser)
    out = []
    for path, _ in files:
        stem = os.path.splitext(path)[0]
        folder = os.path.dirname(path) or "."
        out += [os.path.join(folder, f) for f in os.listdir(folder)
                if os.path.join(folder, f).startswith(stem) and not f.endswith((".part", ".ytdl"))]
    return Result(failed, sorted(set(out)), warnings)


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

    flags = dict(a[2:].partition("=")[::2] for a in sys.argv[1:] if a.startswith("--"))
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit("usage: python core.py <url> [option-number] [output-dir] [--playlist] [--items=1-10]\n"
                 "  [--start=1:20 --end=2:00] [--sponsorblock] [--budget=500] [--subs=hi|en|orig]\n"
                 "  [--burn | --srt-only] [--fast] [--whatsapp=16]")
    x = Extras(start=parse_time(flags.get("start")), end=parse_time(flags.get("end")),
               sponsorblock="sponsorblock" in flags,
               budget_mb=float(flags["budget"]) if flags.get("budget") else None,
               subs_lang=flags.get("subs") or None,
               subs_mode="burn" if "burn" in flags else "srt" if "srt-only" in flags else "embed",
               ai_model="fast" if "fast" in flags else "accurate",
               whatsapp_mb=int(flags["whatsapp"]) if flags.get("whatsapp") else None)
    info = fetch_info(args[0], "playlist" in flags)
    print(f"[{info.site}] {info.title}")
    if info.is_playlist:
        print(f"  Playlist with {len(info.entries)} videos")
    for i, o in enumerate(info.options, 1):
        print(f"  {i}. {o.label}")
    if len(args) > 1:
        choice = info.options[int(args[1]) - 1]
        res = download(args[0], choice, args[2] if len(args) > 2 else ".",
                       progress=lambda p, t: print(f"\r{p:5.1f}% | {t:80.80}", end="", flush=True),
                       playlist=info.is_playlist, items=flags.get("items"), extras=x,
                       playlist_size=len(info.entries))
        print("\nDone" + (" (some videos failed)" if res.failed else ""))
        for f in res.files:
            print("  ", f)
        for w in res.warnings:
            print("  WARNING:", w)
