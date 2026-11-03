"""Follow a channel, playlist or profile: new uploads download automatically.

Each follow keeps an archive of what it already downloaded, so a check only
fetches what is new. Checks look at the newest items only (YouTube channels
and profiles list newest first), which keeps them quick.
"""

import os
import time
import uuid

import appdata
import core
import photos

FILE = "follows.json"
CHECK_LATEST = 10  # how many of the newest items each check looks at
QUALITIES = {"best": None, "1080": 1080, "720": 720, "480": 480, "audio": "audio"}


def entries():
    return appdata.load_json(FILE, [])


def _save(items):
    appdata.save_json(FILE, items)


def archive_path(follow):
    return os.path.join(appdata.folder("archives"), follow["id"] + (
        ".sqlite3" if follow["kind"] == "photos" else ".txt"))


def add(url, out_dir, quality="best", first_n=3, browser=None):
    """Work out what `url` is, save the follow, and return it (not downloaded yet)."""
    try:
        info = core.fetch_info(url, playlist=True, browser=browser)
        if not info.is_playlist:
            raise ValueError("not a channel or playlist")
        kind, title, site = "video", info.title, info.site
    except Exception:
        p = photos.probe(url, browser)  # a profile / board with photos
        kind, title, site = "photos", p.title or url, p.site
    follow = {"id": uuid.uuid4().hex, "url": url, "title": title, "site": site, "kind": kind,
              "quality": quality, "out_dir": out_dir, "first_n": max(0, int(first_n)),
              "added": time.time(), "last_check": 0, "total": 0}
    _save(entries() + [follow])
    return follow


def remove(follow_id):
    _save([f for f in entries() if f["id"] != follow_id])
    for ext in (".txt", ".sqlite3"):
        try:
            os.remove(os.path.join(appdata.folder("archives"), follow_id + ext))
        except OSError:
            pass


def _option(quality):
    q = QUALITIES.get(quality)
    if q == "audio":
        return core.AUDIO_OPTION
    if q:
        return core.video_option(q, up_to=True)
    return core.Option("Best", "bestvideo+bestaudio/best")


def check(follow, progress=lambda p, t: None, browser=None):
    """Download what is new for one follow. Returns the new files."""
    first = follow["last_check"] == 0
    items = f"1-{follow['first_n'] if first else CHECK_LATEST}"
    files = []
    if not first or follow["first_n"] > 0:
        out = os.path.join(follow["out_dir"], "Follows")
        if follow["kind"] == "photos":
            files = photos.download(follow["url"], out, progress, browser, items,
                                    archive=archive_path(follow), allow_empty=True)
        else:
            res = core.download(follow["url"], _option(follow["quality"]), out, progress=progress,
                                playlist=True, items=items, browser=browser,
                                archive=archive_path(follow))
            files = res.files
    if first:
        # Remember everything that exists today, so later checks only fetch new uploads.
        if follow["kind"] == "photos":
            photos.mark_existing(follow["url"], archive_path(follow), browser,
                                 f"1-{CHECK_LATEST}")
        else:
            mark_existing(follow, browser)
    items_all = entries()
    for f in items_all:
        if f["id"] == follow["id"]:
            f["last_check"] = time.time()
            f["total"] = f.get("total", 0) + len(files)
            follow.update(f)
    _save(items_all)
    return files


def mark_existing(follow, browser=None):
    """Write the current newest videos into the archive (yt-dlp's format) without downloading."""
    import yt_dlp
    opts = core.base_opts(browser) | {"extract_flat": "in_playlist",
                                      "playlist_items": f"1-{CHECK_LATEST}"}
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(follow["url"], download=False)
        with open(archive_path(follow), "a", encoding="utf-8") as a:
            for e in info.get("entries") or []:
                key = (e.get("ie_key") or info.get("extractor_key") or "").lower()
                if e.get("id") and key:
                    a.write(f"{key} {e['id']}\n")


def due(every=3600):
    return [f for f in entries() if time.time() - f.get("last_check", 0) >= every]
