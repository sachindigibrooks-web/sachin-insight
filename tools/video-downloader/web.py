"""Website version: paste a video or playlist URL in the browser, pick a quality, download.

Playlists are delivered as one .zip file. The desktop app can also start this
website in the background (serve_background) for phones on the same Wi-Fi.

Run:  python web.py   then open http://localhost:8000
"""

import updater

updater.apply()  # use newer site engines downloaded earlier - before anything imports them

import os  # noqa: E402
import shutil  # noqa: E402
import socket  # noqa: E402
import sys  # noqa: E402
import tempfile  # noqa: E402
import threading  # noqa: E402
import time  # noqa: E402
import uuid  # noqa: E402
import webbrowser  # noqa: E402
import zipfile  # noqa: E402
from html import escape  # noqa: E402

from flask import Flask, Response, abort, jsonify, request, send_file  # noqa: E402

import core  # noqa: E402
import extras  # noqa: E402
import history  # noqa: E402
import i18n  # noqa: E402
import photos  # noqa: E402
import qr  # noqa: E402
import searchindex  # noqa: E402

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


@app.get("/api/config")
def config():
    return jsonify(languages=[[name, code] for name, code, _ in extras.LANGUAGES],
                   whatsapp=extras.WHATSAPP_SIZES, browsers=core.BROWSERS,
                   ui=i18n.UI, phrases=i18n.PHRASES, language_names_hi=i18n.LANGUAGE_NAMES_HI)


@app.get("/api/version")
def version():
    import yt_dlp
    return jsonify(engines=updater.running_versions(), yt_dlp=yt_dlp.version.__version__)


@app.get("/api/qr.svg")
def qr_svg():
    """QR code of this website's address on the home network, for phones."""
    port = request.host.rsplit(":", 1)[-1] if ":" in request.host else "80"
    url = f"http://{qr.lan_ip()}:{port}"
    return Response(qr.svg(url), mimetype="image/svg+xml", headers={"X-Url": url})


@app.get("/api/history")
def history_list():
    return jsonify([{k: e[k] for k in ("title", "url", "kind", "site", "time")}
                    for e in history.search(request.args.get("q", ""))[:200]])


@app.get("/api/search")
def search():
    return jsonify([{k: r[k] for k in ("video_id", "title", "start", "text")}
                    for r in searchindex.search(request.args.get("q", ""))])


@app.get("/media/<video_id>")
def media(video_id):
    """Stream a searchable video (with seeking) - only files in the search index."""
    v = searchindex.video(video_id)
    if not v or not os.path.isfile(v["path"]):
        abort(404)
    return send_file(v["path"], conditional=True)


@app.get("/watch/<video_id>")
def watch(video_id):
    v = searchindex.video(video_id)
    if not v:
        abort(404)
    t = request.args.get("t", "0")
    t = t if t.isdigit() else "0"
    return (f"<!doctype html><meta charset=utf-8><meta name=viewport content='width=device-width'>"
            f"<title>{escape(v['title'])}</title><body style='margin:0;background:#000;color:#eee;"
            f"font-family:system-ui'><video src='/media/{video_id}#t={t}' controls autoplay "
            f"style='width:100%;max-height:90vh'></video><p style='padding:0 12px'>"
            f"{escape(v['title'])}</p>")


def read_extras(data):
    """Extras from the request; raises ValueError with a user-facing message."""
    lang = data.get("subs_lang") or None
    codes = {code for _, code, _ in extras.LANGUAGES} | {extras.ORIGINAL}
    if lang and lang not in codes:
        raise ValueError("Unknown subtitle language.")
    budget, wa = data.get("budget_mb"), data.get("whatsapp_mb")
    try:
        budget = float(budget) if budget not in (None, "") else None
    except ValueError:
        raise ValueError("Data limit should be a number of MB, like 500.")
    if wa not in (None, "") and int(wa) not in extras.WHATSAPP_SIZES:
        raise ValueError("Unknown WhatsApp size.")
    return core.Extras(
        start=core.parse_time(data.get("start")), end=core.parse_time(data.get("end")),
        sponsorblock=bool(data.get("sponsorblock")), budget_mb=budget, subs_lang=lang,
        subs_mode=data.get("subs_mode") if data.get("subs_mode") in ("embed", "burn", "srt")
        else "embed",
        ai_model="fast" if data.get("ai_model") == "fast" else "accurate",
        whatsapp_mb=int(wa) if wa not in (None, "") else None,
        ringtone_start=core.parse_time(data.get("ringtone")))


@app.post("/api/info")
def info():
    data = request.get_json(silent=True) or {}
    url = data.get("url", "").strip()
    playlist = bool(data.get("playlist"))
    if not url.startswith(("http://", "https://")):
        return jsonify(error="Please paste a valid http(s) link."), 400
    try:
        info = core.fetch_info(url, playlist, login_browser(data))
    except Exception as video_error:
        try:  # no video here - maybe a photo post or gallery
            p = photos.probe(url, login_browser(data))
        except Exception as photo_error:
            return jsonify(error=photos.pick_error(video_error, photo_error)), 400
        info_cache[(url, "photos")] = (p.count, p.title or f"{p.site} photos", p.site)
        return jsonify(mode="photos", title=p.title, site=p.site, count=p.count,
                       previews=p.previews)
    info_cache[(url, info.is_playlist)] = (info.options, len(info.entries), info.title, info.site)
    return jsonify(title=info.title, duration=info.duration, thumbnail=info.thumbnail,
                   site=info.site, options=[o.label for o in info.options],
                   sizes=[o.size for o in info.options],
                   audio_only=[o.audio_only for o in info.options],
                   is_playlist=info.is_playlist, has_playlist=info.has_playlist,
                   count=len(info.entries), entries=info.entries[:200])


@app.post("/api/download")
def start_download():
    data = request.get_json(silent=True) or {}
    url = data.get("url", "").strip()
    if data.get("mode") == "photos":
        return start_photos(url, data)
    playlist = bool(data.get("playlist"))
    cached = info_cache.get((url, playlist))
    if not cached:
        return jsonify(error="Fetch the link first."), 400
    options, count, title, site = cached
    try:
        option = options[int(data.get("option", 0))]
    except (ValueError, IndexError):
        return jsonify(error="Invalid quality."), 400
    container = "mkv" if data.get("container") == "mkv" else "mp4"
    items = (data.get("items") or "") if playlist else ""
    if not core.valid_items(items):
        return jsonify(error="Videos should look like 1-10 or 1,3,5-7."), 400
    try:
        x = read_extras(data)
    except ValueError as e:
        return jsonify(error=str(e)), 400

    job_id = new_job()
    args = (job_id, url, option, container, playlist, items, login_browser(data), x, count,
            title, site)
    threading.Thread(target=run_job, args=args, daemon=True).start()
    return jsonify(job=job_id)


def new_job():
    job_id = uuid.uuid4().hex
    job_dir = os.path.join(WORK_DIR, job_id)
    os.makedirs(job_dir)
    with jobs_lock:
        jobs[job_id] = {"status": "queued", "percent": 0, "text": "Waiting in queue...",
                        "dir": job_dir, "file": None, "created": time.time()}
    return job_id


def start_photos(url, data):
    cached = info_cache.get((url, "photos"))
    if cached is None:
        return jsonify(error="Fetch the link first."), 400
    count, title, site = cached
    items = (data.get("items") or "").replace(" ", "")
    if not core.valid_items(items):
        return jsonify(error="Photos should look like 1-10 or 1,3,5-7."), 400
    job_id = new_job()
    total = core.count_items(items) or count
    args = (job_id, url, items, total, login_browser(data), title, site)
    threading.Thread(target=run_photos, args=args, daemon=True).start()
    return jsonify(job=job_id)


def run_photos(job_id, url, items, total, browser, title, site):
    job = jobs[job_id]

    def progress(pct, text):
        job.update(status="downloading", percent=round(pct, 1), text=text)

    with slots:
        job.update(status="downloading", text="Starting...")
        try:
            files = photos.download(url, job["dir"], progress, browser, items, total)
            history.add(title, url, [], "photos", site)  # the files go to the browser
            if len(files) > 1:
                job.update(text="Packing the photos into one .zip file...")
                path = zip_folder(job["dir"], files)
            else:
                path = files[0]
            job.update(status="done", percent=100, text="Ready!", file=path)
        except Exception as e:
            job.update(status="error", text=core.friendly_error(e))


def run_job(job_id, url, option, container, playlist, items, browser, x, count, title, site):
    job = jobs[job_id]

    def progress(pct, text):
        job.update(status="downloading", percent=round(pct, 1), text=text)

    with slots:
        job.update(status="downloading", text="Starting...")
        try:
            res = core.download(url, option, job["dir"], container, progress, playlist, items,
                                browser, x, count)
            files = [f for f in res.files if os.path.isfile(f)]
            if not files:
                raise RuntimeError("No file was produced.")
            history.add(title, url, [], "playlist" if playlist else "video", site)
            if len(files) > 1:  # a playlist, or a video plus subtitles / WhatsApp copy
                job.update(text="Packing the files into one .zip file...")
                path = zip_folder(job["dir"], files)
            else:
                path = files[0]
            note = " Some videos were skipped (private, deleted or blocked)." if res.failed else ""
            if res.warnings:
                note += " Not done: " + " | ".join(res.warnings[:3])
            job.update(status="done", percent=100, text="Ready!" + note, file=path)
        except Exception as e:
            job.update(status="error", text=core.friendly_error(e))


def zip_folder(job_dir, files):
    """Store the playlist's files in one zip (no compression: video is already compressed)."""
    tops = {os.path.relpath(f, job_dir).split(os.sep)[0] for f in files}
    if len(tops) == 1:  # a playlist folder
        name = tops.pop()
    else:  # one video's files: name the zip after the video
        name = os.path.splitext(os.path.basename(max(files, key=os.path.getsize)))[0]
    path = os.path.join(job_dir, name + ".zip")
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


_server = {}


def prepare():
    shutil.rmtree(WORK_DIR, ignore_errors=True)
    os.makedirs(WORK_DIR, exist_ok=True)
    threading.Thread(target=janitor, daemon=True).start()


def port_free(port):
    with socket.socket() as s:
        return s.connect_ex(("127.0.0.1", port)) != 0


def serve_background(port=8000):
    """Start the website in this process (once) and return its port."""
    if "port" in _server:
        return _server["port"]
    while not port_free(port):
        port += 1
    prepare()
    from waitress import serve
    threading.Thread(target=serve, args=(app,), kwargs={"host": "0.0.0.0", "port": port,
                                                         "threads": 16}, daemon=True).start()
    for _ in range(50):  # wait until it answers
        if not port_free(port):
            break
        time.sleep(0.1)
    _server["port"] = port
    return port


if __name__ == "__main__":
    prepare()
    port = int(os.environ.get("PORT", "8000"))
    print(f"Open http://localhost:{port}  (same Wi-Fi devices: http://<this-PC-IP>:{port})")
    if "--open" in sys.argv or getattr(sys, "frozen", False):
        # Open the browser only once the server is up.
        threading.Timer(1.5, webbrowser.open, args=(f"http://localhost:{port}",)).start()
    from waitress import serve
    serve(app, host="0.0.0.0", port=port, threads=16)
