// Jump-cut edit of the source talking-head clip.
// Silences (from ffmpeg silencedetect, -35dB) longer than 0.6s are tightened,
// keeping a short breath on each side so cuts don't clip words.

export const FPS = 30;
export const SOURCE_DURATION = 77.95;

const LONG_SILENCES: [number, number][] = [
  [4.6, 5.546],
  [7.614, 8.398],
  [10.487, 11.157],
  [14.468, 15.342],
  [16.992, 17.702],
  [21.03, 21.804],
  [25.887, 26.591],
  [29.589, 30.377],
  [33.65, 34.319],
  [34.955, 36.2],
  [36.8, 37.933],
  [48.93, 49.628],
  [59.667, 60.341],
  [72.858, 73.519],
  [75.903, 76.671],
];

const PAD_BEFORE = 0.15;
const PAD_AFTER = 0.1;

export type Segment = { srcStart: number; srcEnd: number; outStart: number };

const buildSegments = (): Segment[] => {
  const segs: Segment[] = [];
  let cursor = 0.25;
  let out = 0;
  for (const [s, e] of LONG_SILENCES) {
    const end = s + PAD_BEFORE;
    segs.push({ srcStart: cursor, srcEnd: end, outStart: out });
    out += end - cursor;
    cursor = e - PAD_AFTER;
  }
  segs.push({ srcStart: cursor, srcEnd: SOURCE_DURATION, outStart: out });
  return segs;
};

export const SEGMENTS = buildSegments();

const last = SEGMENTS[SEGMENTS.length - 1];
export const OUT_DURATION = last.outStart + (last.srcEnd - last.srcStart);
export const TOTAL_FRAMES = Math.round(OUT_DURATION * FPS);

// Map a source timestamp (seconds) to an output timestamp (seconds).
// Times inside a removed silence snap to the cut point.
export const toOut = (src: number): number => {
  for (const seg of SEGMENTS) {
    if (src < seg.srcStart) return seg.outStart;
    if (src <= seg.srcEnd) return seg.outStart + (src - seg.srcStart);
  }
  return OUT_DURATION;
};

// Source seconds -> output frame.
export const f = (src: number): number => Math.round(toOut(src) * FPS);
