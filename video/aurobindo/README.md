# Sri Aurobindo: "Thoughts ko dekh kaun raha hai?" (consciousness short)

A 1080x1920, 30 fps, 53.5 s Hinglish Reel/Short. The narration is ElevenLabs "Yash – Motivational Reel Creator" (eleven_v4); visuals are built in Remotion, and the sound design is synthesized.

## Story (script)
1. **Hook:** "Ek second ruko... kitne thoughts? Inhe dekh kaun raha hai?" Chatter freezes, and a witness-eye opens.
2. **Intro:** Freedom fighter turned yogi, shown with the 1908 Alipore photograph.
3. **Ladder of consciousness:** Matter, then Life, then Mind. An orb climbs and gets stuck at Mind while overthinking.
4. **Supermind:** "chetna jo sochti nahi, seedha jaanti hai". Then: man is a transitional being, with an "aap yahan ho" marker.
5. **1908:** a yogi (Vishnu Bhaskar Lele) told him: sit, don't think, watch the mind, throw the thoughts out. His mind fell silent in 3 days.
6. **Practice:** one minute of watching your thoughts. "Jo dekh raha hai, wahi aap ho."
7. **End:** "All life is Yoga." — Sri Aurobindo.

## Colour palette (psychology)
| Colour | Use | Why |
|---|---|---|
| Deep indigo `#0d1130` | base | introspection, depth, trust |
| Midnight violet `#2b1f4f` | gradients | spirituality, imagination |
| Saffron-gold `#e9b44c` | highlights, ladder, eye | illumination, warmth, hope; a classic Indian spiritual cue |
| Ivory `#f4ebdd` | text | clarity, calm |
| Teal `#5fb3b3` | the "Shaant" lake | calm, balance |
| Coral `#e4572e` | thought pills, stuck orb | restlessness; used only for overthinking |

Typography is Cormorant Garamond (serif, which reads as wisdom) for statements, Cinzel for labels, and Inter for captions. Transitions are soft blur-dissolves rather than whips, to keep the calm format.

## Sound design
- **Voice:** gentle EQ and compression, plus a subtle room reverb about 18 dB under the dry voice.
- **Music:** "Ether Vox", Kevin MacLeod (80 BPM, D), sidechain-ducked. It enters on "Freedom fighter", is filtered during the 1908 story, and goes fully silent on "Shaant" before returning for the practice section.
- **Tanpura drone:** synthesized and tuned to D (Pa-Sa-Sa-Sa), running under everything.
- **Synthesized SFX:**
  - Hook: mental chatter plus accelerating clock ticks that stop dead on "Ab socho", then heartbeats.
  - Singing bowls rising D, F#, A as the ladder steps light up; a riser, shimmer and sub on Supermind.
  - The thoughts get whooshed away; three pitched pops for the "3 din" counter; a water drop on "Shaant"; inhale and exhale for the practice.
- **Levels:** in the speech band the voice stays 7–15 dB above everything else. The master is -14.3 LUFS with peaks at -1.4 dBFS.

## Credits (put this in the caption)
Music: "Ether Vox" by Kevin MacLeod (incompetech.com), licensed under Creative Commons: By Attribution 4.0, http://creativecommons.org/licenses/by/4.0/

Images:
- Sri Aurobindo, 1908 Alipore photograph: public domain (PD-India), via Wikimedia Commons (File:Aurobindo_jail_picture.JPG).
- B-roll photos from Unsplash (Unsplash License, free to use; credit appreciated). Photographers: Makeen M.Alaa (overthinking), Faris Mohammed (Pondicherry lighthouse staircase), Ivana Cajina (Milky Way), Klemen Vrankar (man under the stars), Emmanuel Sabuni (misty lake), Yannic Läderach (yoga silhouette), Vitaly Gariev (eye), Zoltan Tasi (lotus).

## Rebuild
```sh
python3 scripts/transcribe.py && python3 scripts/build_timeline.py
python3 scripts/mix.py && sh scripts/master.sh
npx remotion render src/index.ts Aurobindo out/silent.mp4 --codec=h264 --crf=20 --muted
ffmpeg -i out/silent.mp4 -i out/mix_master.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k -shortest out/final.mp4
```


## v2: documentary / editorial redesign (human touch)
After feedback that v1 looked AI-generated, the video was rebuilt around real footage and hand-made touches.

- **Footage:** 21 real stock clips (Mixkit, free licence), cropped to 9:16 and graded warm/cool per scene, with slow push-ins and punch-in zooms on cuts.
- **Chroma key:** the "Mind" scene uses a green-screen actor, keyed (ffmpeg chromakey + despill) to an alpha WebM and composited over a blurred rainy night street.
- **Typography:**
  - Anton (condensed editorial) paired with Cormorant italic accent words, using a masked slide-up reveal. The easing has anticipation and overshoot, following the 12 principles of animation.
  - Hand-written notes in Kalam ("yahin atke hain!", "aap yahan ho", "Alipore, 1908") and rough marker strokes: circles, arrows, strike-throughs, tally marks.
- **Archive:** the 1908 photograph is a printed photo with paper border and tape that drops onto the frame, plus a broadcast lower third for the name.
- **Infographic:** a ladder of consciousness drawn on screen, then a mini-ladder HUD that fills level by level, and a Matter → Supermind progress line.
- **Overthinking montage:**
  - Four hard cuts in 1.5 s with RGB split, shake and scribbled worries.
  - A freeze-frame and desaturation on "Ab socho".
- **Film finish:** grain, gate weave, light flicker, vignette, a soft teal/amber grade, and film-burn light leaks on key cuts.
- **Captions:** a yellow highlighter box on the active word.
- **Audio:**
  - Real recorded SFX (Mixkit, free licence): crowd chatter, city traffic, racing clocks, heartbeats, whoosh-impacts, a riser, a big impact, a vintage camera shutter, paper slides, pencil, typewriter, papers blown in wind, rain, morning birds, bell chimes and magic shimmer.
  - Music is "Vastness" (Mixkit), offset by 15.84 s so its build lands exactly on SUPERMIND. It is filtered during the 1908 story, muted on "Shaant", and returns with the practice section.
  - The tanpura stays as a quiet Indian bed.
  - Voice-to-everything margin: median 13.5 dB. Master: -14.3 LUFS / -1.4 dBFS.

### v2 credits
- Video clips, music ("Vastness") and SFX: Mixkit (mixkit.co), Mixkit Free License. Free for social media and commercial use; no attribution required.
- The Ether Vox credit above applies only to v1.
