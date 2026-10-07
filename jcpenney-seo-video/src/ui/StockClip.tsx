import React from "react";
import { Video } from "@remotion/media";
import { AbsoluteFill, Easing, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { C, SAFE, SAFE_V, body, display, useLayout } from "../theme";
import { PaperTexture, Tape, TornSheet, paperCard } from "./Paper";
import { mix, prog } from "./motion";

type Props = {
  readonly src: string;
  readonly seed: string;
  readonly trimSeconds?: number;
  readonly variant?: "full" | "photo";
  readonly label?: string;
  readonly labelColor?: string;
  readonly children?: React.ReactNode;
};

// Graded stock footage so it sits in the same warm palette as the talking head.
const Footage: React.FC<{ src: string; trimSeconds: number }> = ({ src, trimSeconds }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  return (
    <AbsoluteFill style={{ overflow: "hidden", backgroundColor: C.ink }}>
      <Video
        src={staticFile(src)}
        trimBefore={Math.round(trimSeconds * fps)}
        muted
        premountFor={fps}
        objectFit="cover"
        style={{
          position: "absolute",
          width: "100%",
          height: "100%",
          scale: String(interpolate(frame, [0, durationInFrames], [1.06, 1.14])),
          filter: "sepia(0.22) saturate(1.05) contrast(1.06) brightness(0.96)",
        }}
      />
      <AbsoluteFill style={{ background: "rgba(210,88,74,0.08)", mixBlendMode: "soft-light" }} />
      <AbsoluteFill
        style={{ background: "radial-gradient(110% 90% at 50% 45%, rgba(0,0,0,0) 55%, rgba(25,14,10,0.6) 100%)" }}
      />
    </AbsoluteFill>
  );
};

// Torn-paper label stuck onto the footage.
export const PaperLabel: React.FC<{ readonly text: string; readonly color?: string; readonly delay?: number; readonly style?: React.CSSProperties }> = ({
  text,
  color = C.ink,
  delay = 8,
  style,
}) => {
  const frame = useCurrentFrame();
  const { v } = useLayout();
  const p = prog(frame, delay, 12);
  return (
    <div
      style={{
        position: "absolute",
        left: v ? SAFE_V.x : SAFE.x,
        top: v ? SAFE_V.top + 20 : SAFE.y + 20,
        padding: "18px 34px 14px",
        ...paperCard,
        color,
        fontFamily: display,
        fontSize: v ? 88 : 96,
        lineHeight: 1,
        letterSpacing: "0.01em",
        rotate: `${mix(p, -9, -2)}deg`,
        scale: String(mix(p, 1.25, 1)),
        opacity: p,
        boxShadow: "0 14px 34px rgba(0,0,0,0.35)",
        clipPath:
          "polygon(0 4%, 6% 0, 14% 5%, 25% 1%, 37% 4%, 50% 0, 63% 5%, 76% 1%, 88% 4%, 100% 0, 99% 50%, 100% 100%, 90% 96%, 78% 100%, 64% 95%, 50% 100%, 36% 96%, 22% 100%, 10% 95%, 0 100%, 1% 50%)",
        ...style,
      }}
    >
      {text}
    </div>
  );
};

export const StockClip: React.FC<Props> = ({
  src,
  seed,
  trimSeconds = 0,
  variant = "full",
  label,
  labelColor,
  children,
}) => {
  const frame = useCurrentFrame();
  const { v } = useLayout();

  if (variant === "full") {
    return (
      <TornSheet seed={seed}>
        <Footage src={src} trimSeconds={trimSeconds} />
        <PaperTexture tone="dark" opacity={0.35} />
        {label ? <PaperLabel text={label} color={labelColor} /> : null}
        {children}
      </TornSheet>
    );
  }

  // Photo variant: footage printed on a taped photo card on a paper desk.
  const drop = prog(frame, 2, 18, Easing.bezier(0.16, 1, 0.3, 1));
  return (
    <TornSheet seed={seed}>
      <AbsoluteFill style={{ ...paperCard, backgroundColor: C.sand }} />
      <PaperTexture />
      <div
        style={{
          position: "absolute",
          right: v ? 70 : SAFE.x + 10,
          top: v ? 290 : 110,
          width: v ? 940 : 1040,
          height: v ? 640 : 640,
          padding: 22,
          paddingBottom: 70,
          background: "#FBF8F2",
          boxShadow: "0 30px 60px rgba(31,26,23,0.35)",
          rotate: `${mix(drop, 7, 2.5)}deg`,
          translate: `0px ${mix(drop, -80, 0)}px`,
          scale: String(mix(drop, 1.12, 1)),
        }}
      >
        <div style={{ position: "relative", width: "100%", height: "100%", overflow: "hidden" }}>
          <Footage src={src} trimSeconds={trimSeconds} />
        </div>
        {label ? (
          <div
            style={{
              position: "absolute",
              left: 30,
              bottom: 14,
              fontFamily: body,
              fontWeight: 800,
              fontSize: 30,
              color: C.inkSoft,
              letterSpacing: "0.04em",
            }}
          >
            {label}
          </div>
        ) : null}
        <Tape style={{ left: -50, top: -18, rotate: "-32deg" }} />
        <Tape style={{ right: -50, top: -14, rotate: "28deg" }} />
      </div>
      {children}
    </TornSheet>
  );
};
