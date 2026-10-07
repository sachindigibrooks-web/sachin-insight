import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { C } from "../theme";

type Props = {
  readonly children: React.ReactNode;
  readonly tone?: "light" | "dark";
};

// Full-screen B-roll canvas: wipes in over the speaker and wipes out again.
export const Stage: React.FC<Props> = ({ children, tone = "light" }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  const enter = interpolate(frame, [0, 12], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.7, 0, 0.2, 1),
  });
  const exit = interpolate(frame, [durationInFrames - 10, durationInFrames], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.7, 0, 0.2, 1),
  });

  const bg =
    tone === "light"
      ? `radial-gradient(90% 80% at 30% 20%, #FBF6EF 0%, ${C.cream} 45%, ${C.sand} 100%)`
      : `radial-gradient(90% 80% at 50% 30%, #3A2C26 0%, ${C.ink} 60%, #0F0B0A 100%)`;

  return (
    <AbsoluteFill
      style={{
        clipPath: `inset(0% ${exit * 100}% 0% ${(1 - enter) * 100}%)`,
      }}
    >
      <AbsoluteFill style={{ background: bg }} />
      {/* Brick-course lines echoing the wall in the footage */}
      <AbsoluteFill
        style={{
          opacity: tone === "light" ? 0.22 : 0.08,
          backgroundImage: `repeating-linear-gradient(0deg, transparent 0 58px, ${
            tone === "light" ? C.stone : C.sand
          } 58px 60px)`,
        }}
      />
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(60% 50% at 95% 100%, rgba(210,88,74,0.28) 0%, rgba(210,88,74,0) 70%)",
        }}
      />
      <AbsoluteFill
        style={{
          translate: `${interpolate(frame, [0, 14], [60, 0], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.bezier(0.16, 1, 0.3, 1),
          })}px 0px`,
        }}
      >
        {children}
      </AbsoluteFill>
      {/* Leading edge accent bar on the wipe */}
      <AbsoluteFill
        style={{
          left: `${(1 - enter) * 100}%`,
          width: 14,
          background: C.clay,
          opacity: enter < 1 ? 1 : 0,
        }}
      />
    </AbsoluteFill>
  );
};
