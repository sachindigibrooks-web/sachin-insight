"""Website version: paste a video or playlist URL in the browser, pick a quality, download.

Playlists are delivered as one .zip file.

Run:  python web.py   then open http://localhost:8000
"""

import os
import shutil
import sys
import tempfile
import threading
import time
import uuid
import webbrowser
import zipfile

from flask import Flask, abort, jsonify, request, send_file

import core

# Inside a PyInstaller .exe the bundled files live in sys._MEIPASS.
HERE = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
WORK_DIR = os.path.join(tempfile.gettempdir(), "free-video-downloader")
MAX_PARALLEL = int(os.environ.get("MAX_PARALLEL", "3"))
JOB_TTL = 60 * 60  # unfetched files are deleted after an hour
SERVED_TTL = 10 * 60  # fetched files are kept briefly so the browser can retry

app = Flask(__name__, static_folder=os.path.join(HERE, "web"), static_url_path="")
jobs = {}
jobs_lock = threading.Lock()
slots = threading.Semaphore(MAX_PARALLEL)
# Options from the last /api/info per (URL, playlist), so the client only sends an index.
info_cache = {}


def login_browser(data):
    b = (data.get("browser") or "").lower()
    return b if b in core.BROWSERS else None


@app.get("/")
def index():
    return app.send_static_file("index.html")


@app.post("/api/info")
def info():
    data = request.get_json(silent=True) or {}
    url = data.get("url", "").strip()
    playlist = bool(data.get("playlist"))
    if not url.startswith(("http://", "https://")):
        return jsonify(error="Please paste a valid http(s) link."), 400
    try:
        info = core.fetch_info(url, playlist, login_browser(data))
    except Exception as e:
        return jsonify(error=core.friendly_error(e)), 400
    info_cache[(url, info.is_playlist)] = info.options
    return jsonify(title=info.title, duration=info.duration, thumbnail=info.thumbnail,
                   site=info.site, options=[o.label for o in info.options],
                   is_playlist=info.is_playlist, has_playlist=info.has_playlist,
                   count=len(info.entries), entries=info.entries[:200])


@app.post("/api/download")
def start_download():
    data = request.get_json(silent=True) or {}
    url = data.get("url", "").strip()
    playlist = bool(data.get("playlist"))
    options = info_cache.get((url, playlist))
    if not options:
        return jsonify(error="Fetch the link first."), 400
    try:
        option = options[int(data.get("option", 0))]
    except (ValueError, IndexError):
        return jsonify(error="Invalid quality."), 400
    container = "mkv" if data.get("container") == "mkv" else "mp4"
    items = (data.get("items") or "") if playlist else ""
    if not core.valid_items(items):
        return jsonify(error="Videos should look like 1-10 or 1,3,5-7."), 400

    job_id = uuid.uuid4().hex
    job_dir = os.path.join(WORK_DIR, job_id)
    os.makedirs(job_dir)
    with jobs_lock:
        jobs[job_id] = {"status": "queued", "percent": 0, "text": "Waiting in queue...",
                        "dir": job_dir, "file": None, "created": time.time()}
    args = (job_id, url, option, container, playlist, items, login_browser(data))
    threading.Thread(target=run_job, args=args, daemon=True).start()
    return jsonify(job=job_id)


def run_job(job_id, url, option, container, playlist, items, browser):
    job = jobs[job_id]

    def progress(pct, text):
        job.update(status="downloading", percent=round(pct, 1), text=text)

    with slots:
        job.update(status="downloading", text="Starting...")
        try:
            failed = core.download(url, option, job["dir"], container, progress, playlist, items,
                                   browser)
            files = [os.path.join(root, f) for root, _, names in os.walk(job["dir"])
                     for f in names if not f.endswith((".part", ".ytdl"))]
            if not files:
                raise RuntimeError("No file was produced.")
            if playlist:
                job.update(text="Packing the videos into one .zip file...")
                path = zip_folder(job["dir"], files)
            else:
                path = max(files, key=os.path.getsize)
            note = " Some videos were skipped (private, deleted or blocked)." if failed else ""
            job.update(status="done", percent=100, text="Ready!" + note, file=path)
        except Exception as e:
            job.update(status="error", text=core.friendly_error(e))


def zip_folder(job_dir, files):
    """Store the playlist's files in one zip (no compression: video is already compressed)."""
    folders = {os.path.relpath(f, job_dir).split(os.sep)[0] for f in files}
    name = (folders.pop() if len(folders) == 1 else "playlist") + ".zip"
    path = os.path.join(job_dir, name)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_STORED, allowZip64=True) as z:
        for f in files:
            z.write(f, os.path.relpath(f, job_dir))
            os.remove(f)  # keep disk use to about one copy
    return path


@app.get("/api/progress/<job_id>")
def progress(job_id):
    job = jobs.get(job_id)
    if not job:
        abort(404)
    return jsonify({k: job[k] for k in ("status", "percent", "text")})


@app.get("/api/file/<job_id>")
def file(job_id):
    job = jobs.get(job_id)
    if not job or job["status"] != "done":
        abort(404)
    job["served"] = time.time()
    return send_file(job["file"], as_attachment=True,
                     download_name=os.path.basename(job["file"]))


def janitor():
    while True:
        time.sleep(60)
        now = time.time()
        for job_id, job in list(jobs.items()):
            expired = (now - job.get("served", now) > SERVED_TTL
                       or (job["status"] in ("done", "error") and now - job["created"] > JOB_TTL))
            if expired:
                shutil.rmtree(job["dir"], ignore_errors=True)
                if not os.path.exists(job["dir"]):  # on Windows a file still being sent stays locked
                    with jobs_lock:
                        jobs.pop(job_id, None)


if __name__ == "__main__":
    shutil.rmtree(WORK_DIR, ignore_errors=True)
    os.makedirs(WORK_DIR, exist_ok=True)
    threading.Thread(target=janitor, daemon=True).start()
    port = int(os.environ.get("PORT", "8000"))
    print(f"Open http://localhost:{port}  (same Wi-Fi devices: http://<this-PC-IP>:{port})")
    if "--open" in sys.argv or getattr(sys, "frozen", False):
        # Open the browser only once the server is up.
        threading.Timer(1.5, webbrowser.open, args=(f"http://localhost:{port}",)).start()
    from waitress import serve
    serve(app, host="0.0.0.0", port=port, threads=16)
