"""Build the desktop app (the website is inside it) with PyInstaller.

Output: dist/FreeVideoDownloader/ (Windows / Linux) or dist/FreeVideoDownloader.app (Mac).
A folder build starts in seconds, unlike a single-file .exe that unpacks itself
on every start. On Windows, pass --installer to also make dist/FreeVideoDownloader-Setup.exe
with Inno Setup.
"""

import glob
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
VERSION = os.environ.get("APP_VERSION", "1.0.0")


def build_app():
    sep = ";" if os.name == "nt" else ":"
    cmd = [sys.executable, "-m", "PyInstaller", "--noconfirm", "--windowed", "--onedir",
           "--name", "FreeVideoDownloader", "--add-data", f"web{sep}web",
           # the updater reads the bundled engine versions from their metadata
           "--copy-metadata", "yt-dlp", "--copy-metadata", "gallery-dl"]
    for package in ("imageio_ffmpeg", "faster_whisper", "ctranslate2", "gallery_dl"):
        cmd += ["--collect-all", package]
    subprocess.run(cmd + ["app.py"], cwd=HERE, check=True)


def build_installer():
    candidates = glob.glob(r"C:\Program Files*\Inno Setup 6\ISCC.exe")
    if not candidates:
        sys.exit("Inno Setup 6 is not installed (https://jrsoftware.org/isdl.php) - "
                 "the app folder is ready in dist\\FreeVideoDownloader, but no Setup.exe.")
    subprocess.run([candidates[0], f"/DAppVersion={VERSION}", "installer.iss"], cwd=HERE,
                   check=True)


if __name__ == "__main__":
    build_app()
    if "--installer" in sys.argv:
        build_installer()
