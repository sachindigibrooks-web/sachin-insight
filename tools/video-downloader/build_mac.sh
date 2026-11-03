#!/bin/bash
# Builds dist/FreeVideoDownloader.app (run on a Mac) and zips it as
# dist/FreeVideoDownloader-Mac.zip. The website runs from inside the app
# ("Phone / Website" button).
set -e
cd "$(dirname "$0")"
python3 -m pip install --upgrade -r requirements.txt pyinstaller
python3 build.py
cd dist
rm -rf FreeVideoDownloader FreeVideoDownloader-Mac.zip  # the folder build; the .app holds the same
# ditto keeps the symlinks and permissions the .app needs.
ditto -c -k --keepParent FreeVideoDownloader.app FreeVideoDownloader-Mac.zip
echo "Done: dist/FreeVideoDownloader-Mac.zip"
