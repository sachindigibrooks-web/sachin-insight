"""Where the apps keep their own files: settings, history, search index, follows, updates."""

import json
import os
import sys
import threading


def folder(*parts):
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~\\AppData\\Local")
    elif sys.platform == "darwin":
        base = os.path.expanduser("~/Library/Application Support")
    else:
        base = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
    path = os.path.join(base, "FreeVideoDownloader", *parts)
    os.makedirs(path, exist_ok=True)
    return path


_lock = threading.Lock()


def load_json(name, default):
    try:
        with open(os.path.join(folder(), name), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def save_json(name, data):
    path = os.path.join(folder(), name)
    with _lock:
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
        os.replace(tmp, path)  # never leave a half-written file behind


def setting(key, default=None):
    return load_json("settings.json", {}).get(key, default)


def set_setting(key, value):
    data = load_json("settings.json", {})
    data[key] = value
    save_json("settings.json", data)
