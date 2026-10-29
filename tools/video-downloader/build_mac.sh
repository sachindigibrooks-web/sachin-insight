#!/bin/bash
# Builds the Mac versions into dist/ (run on a Mac):
#   FreeVideoDownloader.app  - desktop app
#   FreeVideoDownloaderWeb   - website version (opens in the browser)
# and zips them as dist/FreeVideoDownloader-Mac.zip.
set -e
cd "$(dirname "$0")"
python3 -m pip install --upgrade -r requirements.txt pyinstaller

python3 -m PyInstaller --noconfirm --windowed --name FreeVideoDownloader \
  --collect-all imageio_ffmpeg app.py
python3 -m PyInstaller --noconfirm --onefile --name FreeVideoDownloaderWeb \
  --add-data "web:web" --collect-all imageio_ffmpeg web.py

cd dist
rm -rf FreeVideoDownloader FreeVideoDownloader-Mac FreeVideoDownloader-Mac.zip  # onedir folder; the .app holds the same files
mkdir FreeVideoDownloader-Mac
mv FreeVideoDownloader.app FreeVideoDownloaderWeb FreeVideoDownloader-Mac/
# ditto keeps the symlinks and permissions the .app needs.
ditto -c -k --keepParent FreeVideoDownloader-Mac FreeVideoDownloader-Mac.zip
echo "Done: dist/FreeVideoDownloader-Mac.zip"
