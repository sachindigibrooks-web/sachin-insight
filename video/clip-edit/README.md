# White Hat SEO: creator clip edit (YouTube 16:9 + Shorts 9:16)

The source is a 41 s talking-head clip, 1080p at 23.976 fps, in Hinglish. It is `public/clip.mp4`, taken from the user's Google Drive. It is edited in the style of the two EarnEdits references (`ref/`): cut-aways on every point, the named person on screen, kinetic words, word-by-word captions and real SFX. It is kept deliberately sparse, with one idea on screen at a time.

## Outputs

- `out/WhiteHatSEO_YouTube_16x9.mp4`: 1920x1080, 30 fps.
- `out/WhiteHatSEO_Shorts_9x16.mp4`: 1080x1920, 30 fps. Captions sit inside the Shorts safe zone.

Both share one edit (`src/Edit.tsx`) and one mix. The layout switches on aspect ratio.

## Edit map (all cues are on spoken words, from Whisper timings)

| Time | Line | Picture |
|---|---|---|
| 0–5.6 | White Hat SEO, the boring way but the powerful way, isme hai kya? | Camera, with punch-ins. Title words rise in. "boring" is struck through in red, "powerful" is lime. |
| 5.6–7.6 | genuine content likho | Typing B-roll, with pill "1 Genuine content" |
| 7.6–9.3 | quality backlinks banao | Motion graphic: sites link into YOUR SITE. Pill "2" |
| 9.3–11.8 | user experience improve karo | Phone-browsing B-roll, pill "3", handwritten "fast · easy · useful" |
| 11.8–16.0 | I know yaar, boring lagta hai... But ek example suno | Camera, with "boring lagta hai" and zzz, then a punch-in on "But" |
| 16.0–27.1 | Ek blogger tha, Neil Patel... | Orange grid board. A printed photo of Neil Patel drops in, with a name plate. A checklist ticks on each thing he did. |
| 27.1–30.7 | aaj uski website pe millions of users | Crowd B-roll and a counter to 1,000,000+ |
| 30.7–34.8 | Think of it like this: Black Hat SEO game ka cheat code hai | Camera, then hacker and gamer B-roll. A cheat code (↑↑↓↓←→←→BA) types out. |
| 34.8–37.3 | But ye cheat code ban hai | The music cuts. A freeze frame, a BANNED stamp and "Google penalty = traffic gone". |
| 37.3–41.0 | Toh White Hat SEO aisi skill hai jo hamesha kaam aayegi | Camera, with "White Hat SEO = skill for life" |

## Sound

- **Voice:** the camera mic. The chain is a highpass, light denoise (afftdn), mud cut, presence lift, de-esser and gentle compression.
- **Music:** "Hip Hop 02" (Mixkit), ducked 7 dB under speech. It is low-passed for the black-hat section, cut dead before "ban" so the game-over and impact land in silence, and brought back on "Toh".
- **SFX:** 56 cues from 21 real recordings, all Mixkit:
  - whooshes on cuts,
  - pops on labels,
  - typing under "content",
  - camera shutter on the photo drop,
  - pencil ticks on the checklist,
  - counter ticks and a coin,
  - arcade pops and key hits for the cheat code,
  - game-over plus impact on BANNED.
- **Levels:** -14.3 LUFS integrated. In the speech band, the voice sits a median 20.5 dB above music and SFX.

## Rebuild

```sh
python3 scripts/transcribe.py && python3 scripts/build_timeline.py
python3 scripts/mix.py && sh scripts/master.sh
npx remotion render src/index.ts YouTube out/YouTube_silent.mp4 --codec=h264 --crf=18 --muted
npx remotion render src/index.ts Shorts out/Shorts_silent.mp4 --codec=h264 --crf=18 --muted
# then mux each with out/mix_master.wav (AAC 256k)
```

## Credits (add to the description)

- Photo of Neil Patel: "Neil Patel at Traction" by JD Lasica (flickr.com/photos/jdlasica), licensed under CC BY 2.0.
- Stock video, music ("Hip Hop 02") and sound effects: Mixkit (mixkit.co), Mixkit Free License.
