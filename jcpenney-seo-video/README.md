# JCPenney SEO story – edited talking-head video

Remotion project that edits `DSC_0053.mp4` (Hinglish talking head about JCPenney's
2011 Google penalty) into a finished 1920×1080 video:

- Jump cuts on long pauses with alternating punch-ins (`src/timeline.ts`, `src/ui/Speaker.tsx`)
- Word-by-word animated Hinglish captions (`src/captions.ts`, `src/ui/Captions.tsx`)
- Motion-graphic B-roll and split-screen panels synced to the words (`src/broll/`)
- Stock B-roll cutaways, paper-tear transitions and taped photo cards (`src/ui/StockClip.tsx`, `src/ui/Paper.tsx`)
- Background music with ducking and sound design (`src/Main.tsx`)
- Palette sampled from the footage (`src/theme.ts`)

## Setup

1. Download the source clip from Google Drive and save it as `public/source.mp4`.
2. `npm i`
3. `./scripts/fetch-assets.sh` downloads the B-roll, music and sound effects from
   [Mixkit](https://mixkit.co/license/) (free license, no attribution required).
   They aren't committed because the license doesn't allow redistributing the raw files.

## Preview / render

```bash
npm run dev                 # Remotion Studio
npx remotion render JCPenneySEO out/JCPenney-SEO-edit.mp4 --crf=20
```

Scene timings are written in **source-video seconds**; `f()` in `src/timeline.ts`
converts them to output frames after the jump cuts.
