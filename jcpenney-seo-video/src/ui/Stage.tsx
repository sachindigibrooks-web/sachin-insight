import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { C } from "../theme";
import { PaperTexture, TornSheet } from "./Paper";

type Props = {
  readonly children: React.ReactNode;
  readonly tone?: "light" | "dark";
  readonly seed?: string;
};

// Full-screen B-roll canvas: a paper sheet that tears in over the speaker
// and tears away again.
export const Stage: React.FC<Props> = ({ children, tone = "light", seed = "stage" }) => {
  const frame = useCurrentFrame();

  const bg =
    tone === "light"
      ? `radial-gradient(90% 80% at 30% 20%, #FBF6EF 0%, ${C.cream} 45%, ${C.sand} 100%)`
      : `radial-gradient(90% 80% at 50% 30%, #3A2C26 0%, ${C.ink} 60%, #0F0B0A 100%)`;

  return (
    <TornSheet seed={seed} rim={tone === "light" ? "#FBF8F2" : "#E9E1D4"}>
      <AbsoluteFill style={{ background: bg }} />
      {/* Ruled lines echoing the brick courses in the footage */}
      <AbsoluteFill
        style={{
          opacity: tone === "light" ? 0.16 : 0.06,
          backgroundImage: `repeating-linear-gradient(0deg, transparent 0 58px, ${
            tone === "light" ? C.stone : C.sand
          } 58px 60px)`,
        }}
      />
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(60% 50% at 95% 100%, rgba(210,88,74,0.24) 0%, rgba(210,88,74,0) 70%)",
        }}
      />
      <PaperTexture tone={tone} />
      <AbsoluteFill
        style={{
          translate: `${interpolate(frame, [4, 20], [70, 0], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.bezier(0.16, 1, 0.3, 1),
          })}px 0px`,
        }}
      >
        {children}
      </AbsoluteFill>
    </TornSheet>
  );
};
