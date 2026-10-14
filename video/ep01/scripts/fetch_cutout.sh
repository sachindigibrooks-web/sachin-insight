#!/bin/sh
# Usage: fetch_cutout.sh <ideogram_response_id> <name>  -> public/img/<name>.png (RGBA)
set -e
for i in $(seq 1 60); do
  if curl -sf -o /tmp/cut.webp "https://ideogram.ai/assets/image/balanced/response/$1@2k" && head -c 64 /tmp/cut.webp | grep -q ALPH; then
    python3 -c "from PIL import Image; im=Image.open('/tmp/cut.webp').convert('RGBA'); bb=im.getbbox(); im.crop(bb).save('public/img/$2.png'); print('$2', im.crop(bb).size)"
    exit 0
  fi
  sleep 4
done
echo "timeout $2"; exit 1
