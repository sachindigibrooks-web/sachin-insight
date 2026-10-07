#!/usr/bin/env bash
# Downloads stock B-roll, music and sound effects from Mixkit (free license,
# no attribution required: https://mixkit.co/license/). They're not committed
# because the Mixkit license doesn't allow redistributing the raw files.
set -euo pipefail
cd "$(dirname "$0")/../public"
mkdir -p broll music sfx

get() { [ -s "$2" ] || curl -sSfL -o "$2" "$1"; echo "ok $2"; }

# B-roll (Mixkit Stock Video Free License)
get https://assets.mixkit.co/videos/4701/4701-720.mp4   broll/worried-man.mp4
get https://assets.mixkit.co/videos/18305/18305-720.mp4 broll/banknotes.mp4
get https://assets.mixkit.co/videos/21607/21607-720.mp4 broll/globe.mp4
get https://assets.mixkit.co/videos/42121/42121-720.mp4 broll/online-shopping.mp4
get https://assets.mixkit.co/videos/31372/31372-720.mp4 broll/cctv-thieves.mp4
get https://assets.mixkit.co/videos/32790/32790-720.mp4 broll/police-tape.mp4
get https://assets.mixkit.co/videos/50726/50726-720.mp4 broll/library.mp4
get https://assets.mixkit.co/videos/1781/1781-720.mp4   broll/laptop-typing.mp4

# Music: "Curiosity" (Mixkit Stock Music Free License)
get https://assets.mixkit.co/music/480/480.mp3 music/curiosity.mp3

# Sound effects (Mixkit Sound Effects Free License)
S=https://assets.mixkit.co/active_storage/sfx
get $S/1530/1530-preview.mp3 sfx/paper-slide.mp3
get $S/2380/2380-preview.mp3 sfx/paper-move.mp3
get $S/2996/2996-preview.mp3 sfx/paper-crumple.mp3
get $S/1104/1104-preview.mp3 sfx/page-turn.mp3
get $S/1492/1492-preview.mp3 sfx/whoosh-fast.mp3
get $S/788/788-preview.mp3   sfx/impact-big.mp3
get $S/2908/2908-preview.mp3 sfx/impact-trailer.mp3
get $S/679/679-preview.mp3   sfx/glitch-hit.mp3
get $S/2364/2364-preview.mp3 sfx/pop.mp3
get $S/1133/1133-preview.mp3 sfx/shutter.mp3
get $S/2531/2531-preview.mp3 sfx/typing.mp3
get $S/498/498-preview.mp3   sfx/heartbeat-impact.mp3
get $S/1150/1150-preview.mp3 sfx/bell.mp3
