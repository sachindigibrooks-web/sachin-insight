import React from "react";
import { AbsoluteFill, Easing, Img, interpolate, random, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { mix, pop } from "../ui/motion";
import { R, bebas, glow, sora } from "./style";

/* Scene entry used by the references: punch out of a blur with a quick flash. */
export const ZoomIn: React.FC<{ readonly children: React.ReactNode; readonly flash?: string }> = ({
  children,
  flash = R.white,
}) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame, [0, 9], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{ scale: String(mix(p, 1.18, 1)), filter: `blur(${mix(p, 14, 0)}px)` }}>{children}</AbsoluteFill>
      <AbsoluteFill
        style={{
          background: flash,
          opacity: interpolate(frame, [0, 1, 4], [0.85, 0.6, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
        }}
      />
    </AbsoluteFill>
  );
};

/* Dark background with a breathing red glow (ref 1). */
export const DarkBg: React.FC<{ readonly hue?: string }> = ({ hue = R.redDeep }) => {
  const frame = useCurrentFrame();
  const breathe = 0.75 + Math.sin(frame / 9) * 0.08;
  return (
    <AbsoluteFill style={{ background: R.black }}>
      <AbsoluteFill
        style={{
          background: `radial-gradient(70% 45% at 50% 42%, ${hue} 0%, rgba(74,11,14,0.6) 45%, rgba(10,9,9,0) 80%)`,
          opacity: breathe,
        }}
      />
      <Grain />
    </AbsoluteFill>
  );
};

/* Light-grey card background (ref 2) with a soft window-light shadow. */
export const GreyBg: React.FC = () => (
  <AbsoluteFill style={{ background: `radial-gradient(120% 80% at 40% 30%, #ECECEC 0%, ${R.grey} 55%, ${R.greyDark} 100%)` }}>
    <AbsoluteFill
      style={{
        opacity: 0.18,
        background:
          "linear-gradient(115deg, transparent 0 18%, rgba(255,255,255,0.9) 18% 26%, transparent 26% 34%, rgba(255,255,255,0.9) 34% 42%, transparent 42%)",
        filter: "blur(30px)",
      }}
    />
    <Grain opacity={0.25} />
  </AbsoluteFill>
);

export const Grain: React.FC<{ readonly opacity?: number }> = ({ opacity = 0.35 }) => {
  const frame = useCurrentFrame();
  const x = Math.floor(random(`gx${Math.floor(frame / 2)}`) * 400);
  const y = Math.floor(random(`gy${Math.floor(frame / 2)}`) * 400);
  return (
    <AbsoluteFill
      style={{
        backgroundImage: `url(${staticFile("paper.jpg")})`,
        backgroundSize: "1600px 900px",
        backgroundPosition: `${x}px ${y}px`,
        mixBlendMode: "overlay",
        opacity,
      }}
    />
  );
};

/* Neon outline headline (ref 1: "ADVICE", "FANBASE", "FAKE MONEY"). */
export const NeonText: React.FC<{
  readonly children: React.ReactNode;
  readonly size?: number;
  readonly color?: string;
  readonly start?: number;
  readonly filled?: boolean;
  readonly style?: React.CSSProperties;
}> = ({ children, size = 220, color = R.red, start = 0, filled = false, style }) => {
  const frame = useCurrentFrame();
  const f = frame - start;
  // Neon tube flicker on ignition.
  const flicker = f < 0 ? 0 : f < 10 ? (random(`fl${f}`) > 0.4 ? 1 : 0.25) : 0.92 + Math.sin(frame / 3) * 0.05;
  return (
    <div
      style={{
        fontFamily: bebas,
        fontSize: size,
        lineHeight: 0.9,
        letterSpacing: "0.02em",
        color: filled ? color : "transparent",
        WebkitTextStroke: filled ? undefined : `${Math.max(3, size / 45)}px ${color}`,
        textShadow: glow(color, 1.1),
        opacity: flicker,
        textAlign: "center",
        ...style,
      }}
    >
      {children}
    </div>
  );
};

/* Corner brackets framing a subject (ref 1). */
export const Brackets: React.FC<{
  readonly width: number;
  readonly height: number;
  readonly color?: string;
  readonly start?: number;
  readonly style?: React.CSSProperties;
}> = ({ width, height, color = R.white, start = 0, style }) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame - start, [0, 10], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });
  const arm = 70;
  const t = 8;
  const corner = (rot: number, pos: React.CSSProperties) => (
    <div style={{ position: "absolute", width: arm, height: arm, rotate: `${rot}deg`, ...pos }}>
      <div style={{ position: "absolute", left: 0, top: 0, width: arm, height: t, background: color, boxShadow: glow(color, 0.5) }} />
      <div style={{ position: "absolute", left: 0, top: 0, width: t, height: arm, background: color, boxShadow: glow(color, 0.5) }} />
    </div>
  );
  const w = mix(p, width * 1.25, width);
  const h = mix(p, height * 1.25, height);
  return (
    <div style={{ position: "absolute", width: w, height: h, opacity: p, ...style }}>
      {corner(0, { left: 0, top: 0 })}
      {corner(90, { right: 0, top: 0 })}
      {corner(180, { right: 0, bottom: 0 })}
      {corner(270, { left: 0, bottom: 0 })}
    </div>
  );
};

/* 3D emoji (Fluent, MIT) that pops in and floats. */
export const Emoji: React.FC<{
  readonly name: string;
  readonly size?: number;
  readonly start?: number;
  readonly float?: boolean;
  readonly style?: React.CSSProperties;
}> = ({ name, size = 300, start = 0, float = true, style }) => {
  const frame = useCurrentFrame();
  const s = pop(frame, start, 14);
  const bob = float ? Math.sin((frame - start) / 10) * 10 : 0;
  return (
    <Img
      src={staticFile(`emoji/${name}.webp`)}
      style={{
        width: size,
        height: size,
        scale: String(s),
        translate: `0px ${bob}px`,
        rotate: `${mix(Math.min(1, s), -18, 0) + Math.sin(frame / 14) * 3}deg`,
        filter: "drop-shadow(0 24px 30px rgba(0,0,0,0.45))",
        ...style,
      }}
    />
  );
};

/* Red bracketed label: "[THE SILVER]" style (ref 1). */
export const BracketLabel: React.FC<{ readonly children: React.ReactNode; readonly start?: number; readonly style?: React.CSSProperties }> = ({
  children,
  start = 0,
  style,
}) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame - start, [0, 8], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <div
      style={{
        fontFamily: sora,
        fontWeight: 700,
        fontSize: 58,
        color: R.white,
        letterSpacing: "-0.01em",
        opacity: p,
        translate: `0px ${mix(p, 20, 0)}px`,
        textAlign: "center",
        ...style,
      }}
    >
      <span style={{ color: R.red, textShadow: glow(R.red, 0.6) }}>[</span>
      {children}
      <span style={{ color: R.red, textShadow: glow(R.red, 0.6) }}>]</span>
    </div>
  );
};

/* Red accent tag (ref 2: "300+ lives"). */
export const RedTag: React.FC<{ readonly children: React.ReactNode; readonly start?: number; readonly style?: React.CSSProperties }> = ({
  children,
  start = 0,
  style,
}) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame - start, [0, 8], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });
  return (
    <div
      style={{
        display: "inline-block",
        padding: "10px 22px",
        background: R.redDeep,
        color: R.white,
        fontFamily: sora,
        fontWeight: 800,
        fontSize: 46,
        letterSpacing: "-0.02em",
        clipPath: `inset(0 ${(1 - p) * 100}% 0 0)`,
        ...style,
      }}
    >
      {children}
    </div>
  );
};

/* Light streaks crossing the frame (ref 1 transitions). */
export const Streaks: React.FC<{ readonly color?: string }> = ({ color = R.red }) => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();
  return (
    <AbsoluteFill style={{ overflow: "hidden", mixBlendMode: "screen" }}>
      {[0, 1, 2].map((i) => {
        const x = ((frame * (38 + i * 14) + i * 500) % (width + 900)) - 450;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: x,
              top: height * (0.2 + i * 0.27),
              width: 520,
              height: 16 - i * 4,
              borderRadius: 20,
              rotate: "-24deg",
              background: `linear-gradient(90deg, transparent, ${color}, white, ${color}, transparent)`,
              filter: "blur(2px)",
              boxShadow: glow(color, 0.8),
              opacity: 0.85,
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};

/* Warm light leak flash used on the big beats. */
export const LightLeak: React.FC<{ readonly color?: string }> = ({ color = "#FF6A2B" }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const p = interpolate(frame, [0, durationInFrames / 2, durationInFrames], [0, 1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <AbsoluteFill
      style={{
        mixBlendMode: "screen",
        opacity: p * 0.85,
        background: `radial-gradient(60% 40% at ${mix(p, 110, 60)}% 30%, ${color} 0%, rgba(255,60,40,0.4) 40%, transparent 75%)`,
      }}
    />
  );
};
