#!/bin/bash
# Builds dist/FreeSEOCrawler.app (run on a Mac) and zips it as dist/FreeSEOCrawler-Mac.zip.
set -e
cd "$(dirname "$0")"
python3 -m pip install --upgrade -r requirements.txt pyinstaller
python3 build.py
cd dist
rm -rf FreeSEOCrawler FreeSEOCrawler-Mac.zip
ditto -c -k --keepParent FreeSEOCrawler.app FreeSEOCrawler-Mac.zip
echo "Done: dist/FreeSEOCrawler-Mac.zip"
