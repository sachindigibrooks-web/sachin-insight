# Ep01 video: "Rank #1, phir bhi click zero?"

A 1080x1920, 30 fps, 70.6 s vertical Reel/Short, built in code (Remotion + Python) in the style of the EarnEdits reference videos.

## Style taken from the reference videos
- Top-down "desk collage" scenes on a different surface every scene (wood, grid paper, cutting mat, blue felt, charcoal, red curtain), with props (pencil, crumpled paper, paper clip, phone).
- Heavy 3D-extruded kinetic words (Archivo Black) that slam in on the exact spoken word, in white/red/green/yellow.
- Torn paper cards, typewriter text (Special Elite), rubber stamps, hand-drawn marker strokes (circles, strike-throughs, arrows, check marks).
- Radial-ring "AI core" graphic, orbiting labels, number tiles, newspaper headline, UI mockups (search, AI Overview card, Instagram-style grid, Follow button).
- Small word-by-word captions with the active word in yellow (Roman Hinglish, timed from Whisper word timestamps).
- A whip-pan with motion blur between every scene, camera shake on impacts, white flash frames, film grain and vignette.

## Sound design
- **Voice:** ElevenLabs take 2. HPF 85 Hz, -2.5 dB at 280 Hz (mud), +2.5 dB at 3.4 kHz (presence), de-ess dip at 7.2 kHz, air shelf, 3:1 leveling compression.
- **Music:** "Voxel Revolution" (123 BPM), sidechain-ducked up to 7.5 dB under the voice. It's arranged around the story:
  - The hook starts low-passed (muffled) and opens up at 2.9 s.
  - Tape-stop into dead silence on "ZERO" (21.1 s), with a low drone under the sigh.
  - The music drops back in on a downbeat at "Toh bhai" (23.1 s).
  - It filters down again for the "Ab ye hoga kaise?" build, with a riser and reverse swell.
  - A fresh downbeat plus an impact lands on "Ek" (38.0 s). The outro ends on a reverse swell and a final hit.
- **SFX:** about 150 cues, all synthesized in `scripts/sfx.py` (no samples, so they're royalty-free): whooshes on every cut (alternating flavours and pan direction), text slams, stamps, paper slides, marker strokes, keyboard typing on the search queries, mouse clicks, UI blips, a rolling counter, bells and sparkles for AI reveals, an error buzzer for "ignored", a camera shutter for the newspaper, and pitched pops that play C-E-G on the 1-2-3 tiles.
- **Levels:** In the 300 Hz–4 kHz speech band, the voice stays at least 7 dB (typically 14–20 dB) above everything else. The master is -14.3 LUFS integrated with peaks at -1.4 dBFS, matching the reference videos' -14.2 LUFS.

## Music credit (required, CC BY 4.0)
Put this in the post caption or description:

> Music: "Voxel Revolution" by Kevin MacLeod (incompetech.com)
> Licensed under Creative Commons: By Attribution 4.0 License
> http://creativecommons.org/licenses/by/4.0/

## Rebuild
```sh
python3 scripts/build_timeline.py   # captions + scene/beat timing from scripts/words_raw.json
python3 scripts/mix.py && sh scripts/master.sh
npx remotion render src/index.ts Ep01 out/ep01_silent.mp4 --codec=h264 --crf=20 --muted
ffmpeg -i out/ep01_silent.mp4 -i out/mix_master.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k -shortest out/final.mp4
```
`scripts/transcribe.py` (faster-whisper) regenerates `words_raw.json` if the voice take changes. `scripts/textures.py` regenerates the backgrounds.

## Image cutouts (v2)
Each scene has one or two stickers with a white die-cut outline, drop shadow, entrance animation and idle float. Each sticker has its own synthesized SFX.

| Scene | Cutout | Moment | Source |
|---|---|---|---|
| Nahi na? | shocked man (also peeks in at the end) | rises on "Nahi" | AI-generated (Ideogram 4.0) for this project |
| AI answers | chrome robot | on "answer" | AI-generated (Ideogram 4.0) |
| Zero | gold #1 trophy, falls grey on ZERO | on "number one" | AI-generated (Ideogram 4.0) |
| Zero | lit cartoon bomb with fuse hiss, explodes on ZERO | on "click" | rawpixel, CC0 |
| Game change | red megaphone | on "Toh bhai" | rawpixel, CC0 |
| Cite | vintage pointing hand, gold medal | "yahan!", "Cite" | rawpixel, CC0 |
| Kaise? | glowing light bulb with hum | on "kaise" | rawpixel, CC0 |
| AI reads everywhere | magnifying glass sweep | on "wahin" | rawpixel, CC0 |
| Ignored | vintage trash can; the copies fly in with a clang | on "ignore" | rawpixel, CC0 |

- The rawpixel images are CC0 (public domain): free for commercial use, no attribution needed. Details are in `public/img/CREDITS.json`.
- Their baked-in preview checkerboards were removed with BiRefNet (MIT licence, `scripts/cutout.py`) plus `scripts/fill_holes.py`.
- Pinterest and Instagram images were deliberately not used, because they are usually copyrighted and can get a Reel claimed or muted.
