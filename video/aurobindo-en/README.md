# Sri Aurobindo: "Who is watching your thoughts?" (English cut, TikTok)

This is the English version of `video/aurobindo` (v2). It uses the same footage, design and sound palette, re-timed to an English narration and laid out for TikTok's safe zones.

- **Output:** `out/Sri_Aurobindo_Consciousness_EN.mp4`. It is 1080x1920 at 30 fps and about 58 s long, mastered to -14.3 LUFS with peaks at -1.4 dBFS.
- **Post copy:** the caption, hashtags, cover text and posting notes are in `TIKTOK.md`.
- **Shared assets:** `public/v`, `public/photo`, `public/fonts`, `public/grain`, `audio/mixkit` and `node_modules` are symlinks into `../aurobindo`. Single-file symlinks are not served by the Remotion dev server, so `paper.png` is copied in instead.

## Voice

ElevenLabs refused the generation because the account's free tier is disabled, and Higgsfield had no credits. The narration is therefore made locally with **Chatterbox TTS** (Resemble AI, MIT licence) using its built-in male voice.

The script (`scripts/vo.py`) is read **line by line**, so each phrase gets its own energy and pace:

- Hook and reveals are brighter, with exaggeration 0.55–0.7.
- Instructions and the payoff are slower and softer, with cfg 0.3.

Each line gets two takes. `scripts/assemble_vo.py` transcribes every take with Whisper and keeps the one that matches the script word for word. It then trims the silences and lays the lines out with hand-set pauses (0.25–0.9 s), so the read breathes instead of running sentence into sentence.

- All 23 lines matched the script.
- The pitch range is 16.9 semitones (5th–95th percentile). The ElevenLabs Hinglish take was 22, and flat or robotic TTS usually sits under 8.

## Timing

`scripts/build_timeline.py` aligns Whisper word timestamps to the script's own spelling and writes:

- caption pages (3 words maximum),
- the scene windows,
- the named beats, which reuse the Hinglish beat names.

`src/scenes.tsx` and `scripts/mix_en.py` place every visual and sound cue on a spoken word, through `W('word', after)` and the beats. Nothing uses hard-coded seconds, so a new voice take only needs the three scripts re-run.

## TikTok layout

- **Burned captions:** y 1330–1460, x 70–930. That is above the description and sound bar, and clear of the like/comment/share column.
- **Graphics moved up out of the bottom UI zone:** the lower third, progress bar, tally, the "you are here" note and the ladder drawing.

## Sound design (English cut)

- **Opening hit:** a soft heart-impact under "Wait." gives the first frame weight before the swipe decision.
- **Hook montage:** crowd, traffic and a racing clock, cut dead on "Now ask yourself...". Heartbeats follow, then a shimmer as the eye opens on "who is watching them?".
- **Music:** "Vastness" (Mixkit) is offset 13.34 s so its build lands on SUPERMIND. After the swell it settles 2 dB lower so "doesn't think... it simply knows" stays clear. It is filtered for the 1908 story and fully muted after "silent.".
- **"Silent.":** the water drop and bell fall into the silence right after the word, never on top of it.
- **Impacts:** tails are trimmed so they never sit under the next line.
- **Clarity:** in the 300–4000 Hz speech band, the voice sits a median 18.6 dB above music + SFX + tanpura, and is at least 8.3 dB above for 95% of speech.

## Rebuild

```sh
/tmp/claude-0/cbenv/bin/python scripts/vo.py audio/takes   # Chatterbox, Python 3.12 venv with torch 2.6 CPU + chatterbox-tts
python3 scripts/assemble_vo.py && python3 scripts/build_timeline.py
STEMS=1 python3 scripts/mix_en.py && sh scripts/master.sh
npx remotion render src/index.ts AurobindoEN out/silent.mp4 --codec=h264 --crf=18 --muted
ffmpeg -i out/silent.mp4 -i out/mix_master.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k -shortest -movflags +faststart out/Sri_Aurobindo_Consciousness_EN.mp4
```

## Credits

- Video clips, music ("Vastness") and SFX: Mixkit, free licence.
- 1908 photograph of Sri Aurobindo: public domain.
- Voice: Chatterbox TTS by Resemble AI (MIT).
