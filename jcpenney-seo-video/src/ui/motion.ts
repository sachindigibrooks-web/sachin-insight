import { Easing, interpolate } from "remotion";

const OUT = Easing.bezier(0.16, 1, 0.3, 1);

// Eased 0..1 progress between two local frames.
export const prog = (frame: number, start: number, dur = 14, easing = OUT) =>
  interpolate(frame, [start, start + dur], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing,
  });

// Overshooting pop used for stamps and icons.
export const pop = (frame: number, start: number, dur = 16) =>
  interpolate(frame, [start, start + dur * 0.6, start + dur], [0, 1.12, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.33, 1, 0.68, 1),
  });

export const mix = (p: number, a: number, b: number) => a + (b - a) * p;
