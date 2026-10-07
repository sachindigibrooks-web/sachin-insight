# JCPenney SEO story – edited talking-head video

Remotion project that edits `DSC_0053.mp4` (Hinglish talking head about JCPenney's
2011 Google penalty) into a finished 1920×1080 video:

- Jump cuts on long pauses with alternating punch-ins (`src/timeline.ts`, `src/ui/Speaker.tsx`)
- Word-by-word animated Hinglish captions (`src/captions.ts`, `src/ui/Captions.tsx`)
- Motion-graphic B-roll and split-screen panels synced to the words (`src/broll/`)
- Palette sampled from the footage (`src/theme.ts`), sound effects in `public/sfx/`

## Setup

1. Download the source clip from Google Drive and save it as `public/source.mp4`.
2. `npm i`

## Preview / render

```bash
npm run dev                 # Remotion Studio
npx remotion render JCPenneySEO out/JCPenney-SEO-edit.mp4 --crf=20
```

Scene timings are written in **source-video seconds**; `f()` in `src/timeline.ts`
converts them to output frames after the jump cuts.
