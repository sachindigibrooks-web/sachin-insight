"""Photo downloads (Instagram, Pinterest, X / Twitter, Reddit, Facebook, Tumblr, Flickr, ...).

yt-dlp only fetches videos, so photo posts and galleries go through gallery-dl,
which knows 300+ sites. The apps try a link as a video first and fall back to
this when there is no video in it.
"""

import io
import os
import threading
from dataclasses import dataclass, field

# gallery-dl keeps its settings in one global config, so photo jobs run one at a time.
_lock = threading.Lock()

POPULAR_SITES = ["Instagram", "Pinterest", "X / Twitter", "Reddit", "Facebook", "Tumblr",
                 "Flickr", "Imgur", "DeviantArt", "ArtStation", "Bluesky"]


@dataclass
class PhotoInfo:
    site: str
    count: int
    previews: list = field(default_factory=list)  # first few image URLs
    title: str = ""


def _configure(out_dir=None, browser=None, items=None, archive=None):
    from gallery_dl import config
    config.clear()
    config.set((), "retries", 2)
    config.set(("output",), "mode", "null")  # no console (the .exe has none)
    if out_dir:
        config.set((), "base-directory", out_dir)
        # One folder per site and account / board, e.g. Photos/pinterest/<board>.
        config.set(("extractor",), "directory", ["Photos", "{category}"])
    if browser:
        config.set(("extractor",), "cookies", [browser])
    if items:
        config.set(("extractor",), "image-range", items)
    if archive:  # remembers finished files so a follow only fetches new ones
        config.set(("extractor",), "archive", archive)
    # Videos inside posts go through yt-dlp; give it the bundled ffmpeg too.
    import core
    ff = core.base_opts().get("ffmpeg_location")
    if ff:
        config.set(("downloader", "ytdl"), "raw-options", {"ffmpeg_location": ff})


def supported(url):
    """True when gallery-dl has an extractor for `url` (cheap: regex matching only)."""
    from gallery_dl import extractor
    try:
        return extractor.find(url) is not None
    except Exception:
        return False


def _first_error(job_data):
    for msg in job_data:
        if msg[0] == -1:
            return msg[1].get("message") or msg[1].get("error")
    return None


def probe(url, browser=None):
    """Return PhotoInfo when `url` has photos gallery-dl can fetch, else raise ValueError."""
    from gallery_dl import exception, job
    with _lock:
        _configure(browser=browser)
        try:
            j = job.DataJob(url, file=io.StringIO())
        except exception.NoExtractorError:
            raise ValueError("No photos or videos found at this link.")
        j.run()
    images = [u for u in j.data_urls if not u.startswith("ytdl:")]
    if not j.data_urls:
        raise ValueError(_first_error(j.data) or "No photos found at this link.")
    meta = j.data_meta[0] if j.data_meta else {}
    title = (meta.get("title") or meta.get("description") or meta.get("content") or "")
    title = " ".join(str(title).split())[:120]
    return PhotoInfo(j.extractor.category.title(), len(j.data_urls), images[:12], title)


def download(url, out_dir, progress=None, browser=None, items=None, total=None, archive=None,
             allow_empty=False):
    """Download every photo of `url` into out_dir/Photos/<site>/... Returns the saved files."""
    from gallery_dl import job
    files = []

    class Job(job.DownloadJob):
        def handle_skip(self):  # already downloaded before (archive or file on disk)
            self.skipped = True
            super().handle_skip()

        def handle_url(self, url, kwdict):
            self.skipped = False
            super().handle_url(url, kwdict)
            path = self.pathfmt.realpath
            if not self.skipped and path and os.path.isfile(path) and path not in files:
                files.append(path)
            if progress:
                n = len(files)
                pct = n * 100 / total if total else 0
                progress(min(pct, 99), f"Saved {n}" + (f" of {total}" if total else "") + " files")

    with _lock:
        _configure(out_dir, browser, items, archive)
        j = Job(url)
        j.run()
    if not files and not allow_empty:
        raise ValueError("No photos could be downloaded (the post may need a login).")
    return files


def mark_existing(url, archive, browser=None, items=None):
    """Record the current items in `archive` without downloading them (for follows)."""
    from gallery_dl import config, job
    with _lock:
        _configure(None, browser, items, archive)
        config.set(("extractor",), "archive-event", "file,skip")
        job.SimulationJob(url).run()


def pick_error(video_error, photo_error):
    """The more useful of the two failures, in plain words."""
    import core
    photo = core.friendly_error(photo_error)
    if "login" in photo or "No photos or videos" in photo:
        return photo
    return core.friendly_error(video_error)
