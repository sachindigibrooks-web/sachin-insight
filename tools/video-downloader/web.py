"""Website version: paste a URL in the browser, pick a quality, download.

Run:  python web.py   then open http://localhost:8000
"""

import os
import shutil
import tempfile
import threading
import time
import uuid

from flask import Flask, abort, jsonify, request, send_file

import core

HERE = os.path.dirname(os.path.abspath(__file__))
WORK_DIR = os.path.join(tempfile.gettempdir(), "free-video-downloader")
MAX_PARALLEL = int(os.environ.get("MAX_PARALLEL", "3"))
JOB_TTL = 60 * 60  # unfetched files are deleted after an hour
SERVED_TTL = 10 * 60  # fetched files are kept briefly so the browser can retry

app = Flask(__name__, static_folder=os.path.join(HERE, "web"), static_url_path="")
jobs = {}
jobs_lock = threading.Lock()
slots = threading.Semaphore(MAX_PARALLEL)
# Options from the last /api/info per URL, so the client only sends an index.
info_cache = {}


@app.get("/")
def index():
    return app.send_static_file("index.html")


@app.post("/api/info")
def info():
    url = (request.get_json(silent=True) or {}).get("url", "").strip()
    if not url.startswith(("http://", "https://")):
        return jsonify(error="Please paste a valid http(s) link."), 400
    try:
        title, duration, options = core.fetch_info(url)
    except Exception as e:
        return jsonify(error=clean_error(e)), 400
    info_cache[url] = options
    return jsonify(title=title, duration=duration,
                   options=[o.label for o in options])


@app.post("/api/download")
def start_download():
    data = request.get_json(silent=True) or {}
    url = data.get("url", "").strip()
    options = info_cache.get(url)
    if not options:
        return jsonify(error="Fetch the link first."), 400
    try:
        option = options[int(data.get("option", 0))]
    except (ValueError, IndexError):
        return jsonify(error="Invalid quality."), 400
    container = "mkv" if data.get("container") == "mkv" else "mp4"

    job_id = uuid.uuid4().hex
    job_dir = os.path.join(WORK_DIR, job_id)
    os.makedirs(job_dir)
    with jobs_lock:
        jobs[job_id] = {"status": "queued", "percent": 0, "text": "Waiting in queue...",
                        "dir": job_dir, "file": None, "created": time.time()}
    threading.Thread(target=run_job, args=(job_id, url, option, container),
                     daemon=True).start()
    return jsonify(job=job_id)


def run_job(job_id, url, option, container):
    job = jobs[job_id]

    def progress(pct, text):
        job.update(status="downloading", percent=round(pct, 1), text=text)

    with slots:
        job.update(status="downloading", text="Starting...")
        try:
            core.download(url, option, job["dir"], container, progress)
            files = [f for f in os.listdir(job["dir"]) if not f.endswith((".part", ".ytdl"))]
            if not files:
                raise RuntimeError("No file was produced.")
            job.update(status="done", percent=100, text="Ready!",
                       file=os.path.join(job["dir"], max(files, key=lambda f: os.path.getsize(
                           os.path.join(job["dir"], f)))))
        except Exception as e:
            job.update(status="error", text=clean_error(e))


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


def clean_error(e):
    msg = str(e).replace("ERROR: ", "")
    if "not a bot" in msg:
        return ("YouTube blocked this server's IP (common on cloud/VPS hosting). "
                "Run it on a home PC/internet, or configure cookies.")
    return msg.split(". See ")[0][:300]


if __name__ == "__main__":
    shutil.rmtree(WORK_DIR, ignore_errors=True)
    os.makedirs(WORK_DIR, exist_ok=True)
    threading.Thread(target=janitor, daemon=True).start()
    port = int(os.environ.get("PORT", "8000"))
    print(f"Open http://localhost:{port}  (same Wi-Fi devices: http://<this-PC-IP>:{port})")
    from waitress import serve
    serve(app, host="0.0.0.0", port=port, threads=16)
