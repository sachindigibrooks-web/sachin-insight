"""Build the crawler app with PyInstaller.

Output: dist/FreeSEOCrawler/ (Windows / Linux) or dist/FreeSEOCrawler.app (Mac). A folder
build starts instantly. On Windows, pass --installer to also make
dist/FreeSEOCrawler-Setup.exe with Inno Setup.
"""

import glob
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
VERSION = os.environ.get("APP_VERSION", "1.0.0")


def build_app():
    sep = ";" if os.name == "nt" else ":"
    subprocess.run([sys.executable, "-m", "PyInstaller", "--noconfirm", "--windowed", "--onedir",
                    "--name", "FreeSEOCrawler", "--add-data", f"web{sep}web",
                    "--collect-all", "selectolax", "app.py"], cwd=HERE, check=True)


def build_installer():
    candidates = glob.glob(r"C:\Program Files*\Inno Setup 6\ISCC.exe")
    if not candidates:
        sys.exit("Inno Setup 6 is not installed (https://jrsoftware.org/isdl.php) - "
                 "the app folder is ready in dist\\FreeSEOCrawler, but no Setup.exe.")
    subprocess.run([candidates[0], f"/DAppVersion={VERSION}", "installer.iss"], cwd=HERE, check=True)


if __name__ == "__main__":
    build_app()
    if "--installer" in sys.argv:
        build_installer()
