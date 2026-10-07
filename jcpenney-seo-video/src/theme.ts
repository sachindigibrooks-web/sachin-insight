import { loadFont } from "@remotion/fonts";
import { staticFile } from "remotion";

// Palette sampled from the footage: cream brick wall, warm red glow,
// terracotta flowers and olive leaves.
export const C = {
  ink: "#1F1A17",
  inkSoft: "#2C2420",
  cream: "#F3ECE2",
  stone: "#938A7D",
  sand: "#D9CEBF",
  clay: "#D2584A",
  clayDeep: "#8E3B30",
  amber: "#E9B44C",
  olive: "#7C7A45",
  white: "#FFFFFF",
} as const;

// Fonts are bundled in public/fonts so rendering works offline.
export const display = "Bebas Neue";
export const body = "Montserrat";

loadFont({ family: display, url: staticFile("fonts/BebasNeue.woff2"), weight: "400" });
loadFont({ family: body, url: staticFile("fonts/Montserrat.woff2"), weight: "100 900" });

// Safe area for a 1920x1080 frame.
export const SAFE = { x: 120, y: 90 } as const;
