"""Keep the site engines (yt-dlp, gallery-dl) fresh without a new .exe.

Sites change often and old engines stop working. Once a day the apps look up
the newest release on PyPI, download its pure-Python wheel, check its SHA-256
and unpack it into the app data folder. apply() - called before anything
imports the engines - puts the newest unpacked copy first on sys.path, and
falls back to the bundled copy if it does not import.
"""

import hashlib
import importlib
import importlib.metadata
import io
import json
import os
import re
import shutil
import sys
import time
import urllib.request
import zipfile

import appdata

PACKAGES = {"yt-dlp": "yt_dlp", "gallery-dl": "gallery_dl"}  # PyPI name -> module
CHECK_EVERY = 24 * 3600


def parse_version(v):
    return tuple(int(n) for n in re.findall(r"\d+", v or ""))


def installed_version(dist):
    try:
        return importlib.metadata.version(dist)
    except importlib.metadata.PackageNotFoundError:
        return "0"


def updates_dir(dist):
    return appdata.folder("updates", dist)


def newest_update(dist):
    """(version, folder) of the newest good unpacked update, or None."""
    best = None
    for name in os.listdir(updates_dir(dist)):
        path = os.path.join(updates_dir(dist), name)
        if os.path.isdir(path) and not name.endswith((".tmp", ".bad")):
            if best is None or parse_version(name) > parse_version(best[0]):
                best = (name, path)
    return best


def apply():
    """Use downloaded engine updates. Call before importing yt_dlp / gallery_dl."""
    for dist, module in PACKAGES.items():
        try:
            found = newest_update(dist)
        except OSError:
            continue
        if not found:
            continue
        version, path = found
        if parse_version(version) <= parse_version(installed_version(dist)):
            continue  # the app itself already ships this or newer
        sys.path.insert(0, path)
        importlib.invalidate_caches()
        try:
            importlib.import_module(module)
        except Exception:
            # A broken update must never break the app: drop it and use the bundled copy.
            sys.path.remove(path)
            for name in [m for m in sys.modules if m == module or m.startswith(module + ".")]:
                del sys.modules[name]
            os.replace(path, path + ".bad")


def running_versions():
    return {dist: installed_version(dist) for dist in PACKAGES}


def check(force=False, log=lambda msg: None):
    """Download newer engines if there are any. Returns the list of updated names.

    Updates take effect the next time the app starts.
    """
    if not force and time.time() - appdata.setting("last_update_check", 0) < CHECK_EVERY:
        return []
    updated = []
    for dist in PACKAGES:
        try:
            if install_latest(dist, log):
                updated.append(dist)
        except Exception as e:  # offline, PyPI down, ... try again next time
            log(f"Update check for {dist} failed: {e}")
    appdata.set_setting("last_update_check", time.time())
    return updated


def install_latest(dist, log):
    with urllib.request.urlopen(f"https://pypi.org/pypi/{dist}/json", timeout=20) as r:
        meta = json.load(r)
    latest = meta["info"]["version"]
    have = max(parse_version(installed_version(dist)),
               parse_version((newest_update(dist) or ("0",))[0]))
    if parse_version(latest) <= have:
        return False
    wheel = next((u for u in meta["urls"]
                  if u["packagetype"] == "bdist_wheel" and u["filename"].endswith("-py3-none-any.whl")),
                 None)
    if not wheel:
        return False
    log(f"Updating {dist} to {latest}...")
    with urllib.request.urlopen(wheel["url"], timeout=120) as r:
        data = r.read()
    if hashlib.sha256(data).hexdigest() != wheel["digests"]["sha256"]:
        raise ValueError("download was corrupted (checksum mismatch)")
    target = os.path.join(updates_dir(dist), latest)
    tmp = target + ".tmp"
    shutil.rmtree(tmp, ignore_errors=True)
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        z.extractall(tmp)
    if not os.path.isdir(os.path.join(tmp, PACKAGES[dist])):
        shutil.rmtree(tmp, ignore_errors=True)
        raise ValueError("unexpected package layout")
    shutil.rmtree(target, ignore_errors=True)
    os.replace(tmp, target)
    # Keep only the newest update.
    for name in os.listdir(updates_dir(dist)):
        if name != latest:
            shutil.rmtree(os.path.join(updates_dir(dist), name), ignore_errors=True)
    log(f"{dist} {latest} downloaded - restart the app to use it.")
    return True
