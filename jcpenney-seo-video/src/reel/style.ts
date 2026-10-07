import { loadFont } from "@remotion/fonts";
import { staticFile } from "remotion";

// Reel look, built from the two references: cinematic black + neon red
// (ref 1) with clean light-grey cards and red accent labels (ref 2).
// The footage already carries a red glow and a white shirt, so it sits in this palette.
export const R = {
  black: "#0A0909",
  night: "#140D0D",
  wine: "#4A0B0E",
  red: "#FF2D2D",
  redDeep: "#C4161C",
  grey: "#DADADA",
  greyDark: "#BDBDBD",
  ink: "#111111",
  white: "#FFFFFF",
  green: "#3DFF8F",
  gold: "#F7C65A",
} as const;

export const sora = "Sora";
export const bebas = "Bebas Neue";
loadFont({ family: sora, url: staticFile("fonts/Sora.woff2"), weight: "400 800" });

export const glow = (color: string, strength = 1) =>
  `0 0 ${8 * strength}px ${color}, 0 0 ${22 * strength}px ${color}, 0 0 ${48 * strength}px ${color}`;

// Moments where an on-screen typography scene already shows the words,
// so the running captions step aside (source seconds).
export const CAPTION_OFF: [number, number][] = [
  [1.7, 2.75],
  [8.5, 14.95],
  [17.3, 21.6],
  [22.2, 26.6],
  [26.55, 29.75],
  [34.3, 35.15],
  [39.6, 41.65],
  [46.75, 49.4],
  [49.55, 55.05],
  [55.1, 60.15],
  [67.0, 76.3],
];
