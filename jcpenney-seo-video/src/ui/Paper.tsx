import React from "react";
import { AbsoluteFill, Easing, interpolate, random, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { C, useLayout } from "../theme";

const STEPS = 30;

// Polygon covering everything right of a ragged vertical tear at `edge` px.
const tornPolygon = (edge: number, seed: string, W: number, H: number, inset = 0) => {
  const pts: string[] = [`${W + 200}px -100px`];
  for (let i = 0; i <= STEPS; i++) {
    const y = (i / STEPS) * (H + 200) - 100;
    const j = (random(`${seed}-${i}`) - 0.5) * 46 + (random(`${seed}-b${i}`) - 0.5) * 18;
    // Slight diagonal so the tear doesn't read as a straight wipe.
    const slant = (i / STEPS - 0.5) * (H > W ? 220 : 120);
    pts.push(`${edge + j + slant - inset}px ${y}px`);
  }
  pts.push(`${W + 200}px ${H + 100}px`);
  return `polygon(${pts.join(", ")})`;
};

export const PaperTexture: React.FC<{ readonly tone?: "light" | "dark"; readonly opacity?: number }> = ({
  tone = "light",
  opacity,
}) => (
  <AbsoluteFill
    style={{
      backgroundImage: `url(${staticFile("paper.jpg")})`,
      backgroundSize: "cover",
      mixBlendMode: tone === "light" ? "multiply" : "overlay",
      opacity: opacity ?? (tone === "light" ? 0.45 : 0.4),
      pointerEvents: "none",
    }}
  />
);

type SheetProps = {
  readonly children: React.ReactNode;
  readonly seed: string;
  readonly enterFrames?: number;
  readonly exitFrames?: number;
  readonly rim?: string;
};

// A sheet of paper that tears in from the right and tears away to the left,
// with a white fibrous rim and a soft shadow on the torn edge.
export const TornSheet: React.FC<SheetProps> = ({ children, seed, enterFrames = 14, exitFrames = 12, rim = "#FBF8F2" }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const { W, H } = useLayout();

  const enter = interpolate(frame, [0, enterFrames], [W + 160, -160], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.65, 0, 0.25, 1),
  });
  const exit = interpolate(frame, [durationInFrames - exitFrames, durationInFrames], [-160, W + 160], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.65, 0, 0.35, 1),
  });
  const exiting = frame >= durationInFrames - exitFrames;
  const edge = exiting ? exit : enter;
  const settle = interpolate(frame, [0, enterFrames + 6], [1.6, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });
  // Exit tears from the left side, so mirror the sheet's polygon.
  const s = exiting ? `${seed}-x` : seed;

  return (
    <AbsoluteFill style={{ rotate: `${settle}deg`, filter: "drop-shadow(-14px 0 18px rgba(20,12,8,0.35))" }}>
      <AbsoluteFill style={{ background: rim, clipPath: tornPolygon(edge, `${s}-rim`, W, H, 12) }} />
      <AbsoluteFill style={{ clipPath: tornPolygon(edge, s, W, H) }}>{children}</AbsoluteFill>
    </AbsoluteFill>
  );
};

// Masking-tape strip.
export const Tape: React.FC<{ readonly style?: React.CSSProperties }> = ({ style }) => (
  <div
    style={{
      position: "absolute",
      width: 190,
      height: 52,
      background: "rgba(233,220,190,0.82)",
      boxShadow: "0 2px 6px rgba(0,0,0,0.15)",
      clipPath:
        "polygon(3% 8%, 10% 0%, 20% 6%, 32% 0, 45% 5%, 60% 0, 74% 6%, 88% 0, 97% 7%, 100% 50%, 97% 92%, 86% 100%, 72% 94%, 58% 100%, 44% 95%, 30% 100%, 16% 94%, 4% 100%, 0 50%)",
      ...style,
    }}
  />
);

export const paperCard: React.CSSProperties = {
  backgroundColor: C.cream,
  backgroundImage: `url(${staticFile("paper.jpg")})`,
  backgroundSize: "1920px 1080px",
  backgroundBlendMode: "soft-light",
};
