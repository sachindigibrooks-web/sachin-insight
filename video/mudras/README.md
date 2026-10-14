# Mudras: "Your body is not a time slot" (branded social ad)

A 1080x1920, 30 fps, 44.5 s commercial for **Mudras**, a bespoke massage therapy studio in Chelsea, NYC (mudras.com). It is in English and built for Instagram Reels, TikTok and YouTube Shorts.

## Brand inputs (pulled from mudras.com)
- **Positioning:** a bespoke massage therapy studio where no two sessions look the same. The signature session is the **Mudras BodyReset**, built in real time.
- **Proof points used** (all taken from the site's own copy):
  - Techniques: deep tissue, trigger point, assisted stretching, cupping, gua sha.
  - Clients: pro athletes and desk warriors.
  - Specialists: licensed, with 15–20 years of experience (About page).
  - What clients often notice: less tension, easier movement, deeper sleep. Shown on screen with "Results vary by person and by session", the same caveat the site uses.
- **Contact details on the end card:** 37 W 20th St, Suite 607, Chelsea, NYC · (212) 837-8382 · Mon–Sat 11 AM – 9 PM · mudras.com.
- **Brand system:** gold `#f0cc75`, near-black `#212121`, forest `#1f2c1b` and cream `#f2efe6`, taken from the site's CSS variables. The ad uses the official gold "MUDRAS · Bespoke Therapeutic Massage" logo, Mudras' own black-and-white studio photography, and their gold line icons.

## Structure (VO-timed)
| Time | Line | Visual |
|---|---|---|
| 0–2.8 | Your body is not a time slot. | Booking grid of identical time slots, struck through in gold |
| 2.8–5.8 | So why does every massage feel the same? | The same massage clip tiled 3x3 in lock-step |
| 5.8–8.5 | At Mudras, no two sessions look alike. | Music drop, gold logo with specular light sweep, then three different Mudras photos |
| 8.5–15.8 | Signature BodyReset, built in real time | Title card, then a gold line-art body map with live hotspots (neck, shoulders, lower back) |
| 15.8–22.4 | Techniques / Chosen for you | A menu that writes itself with Mudras icons; each item cuts to its own image |
| 23–25.6 | Pro athletes & desk warriors | Wipe-revealed split screen |
| 26–30.3 | Licensed specialists, 15–20 years | Counter animation over B&W hands |
| 31–33.9 | Less tension · Easier movement · Deeper sleep | Three cards, with the results-vary fine print |
| 34.7–38.5 | Mudras. Chelsea, New York. | Logo over a NYC aerial |
| 39–44.5 | Book your BodyReset today. | CTA end card: Book now, website, phone, address, hours |

## Audio
- **VO:** Kokoro-82M ("af_heart", warm US female), generated locally (Apache-2.0, free for commercial use), line by line with designed pauses. Whisper intelligibility check: 95.7 %. Line 1 was rephrased to "is not", because "isn't" was being heard as "is in".
- **Music:** "Deep Urban" (Mixkit), offset by 9.71 s so its drop lands on "At Mudras". The intro is low-passed under the problem statement and opens on the reveal.
- **SFX:** restrained Mixkit foley: a ticking clock under the time-slot line, a pencil strike, a reverse-impact into the logo drop, a sparkle on the light sweep, soft chimes on the hotspots, page flicks for the technique menu, a counter tick, and a whisper of city ambience under "New York".
- **Master:** -14.3 LUFS integrated, peaks at -1.5 dBFS. While the VO is speaking it sits about 13.5 dB (median) above everything else.

## Licences
- Logo, studio photos and icons are Mudras' own brand assets (from mudras.com). Use them only with the brand's approval.
- Stock video, music ("Deep Urban") and SFX are from Mixkit under its free licence: OK for social and commercial use, no attribution required.
- VO model: Kokoro-82M, Apache-2.0.

## Rebuild
```sh
python3 scripts/vo.py af_heart          # VO (needs tts/kokoro-v1.0.onnx + voices-v1.0.bin from HF fastrtc/kokoro-onnx)
python3 scripts/mix.py && sh scripts/master.sh
npx remotion render src/index.ts Mudras out/silent.mp4 --codec=h264 --crf=18 --muted
```
