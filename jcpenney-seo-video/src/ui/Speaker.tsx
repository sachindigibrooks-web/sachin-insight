import React from "react";
import { Video } from "@remotion/media";
import { AbsoluteFill, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { SEGMENTS, f } from "../timeline";

// Punch-in level per jump cut. Alternating framing hides the cuts.
const ZOOMS = [1, 1.12, 1, 1.08, 1.16, 1, 1.12, 1, 1.22, 1, 1.1, 1, 1.08, 1, 1.14, 1];

// Split-screen moments: the speaker slides right to make room for a panel.
// [srcStart, srcEnd] in source seconds.
export const SPLITS: [number, number][] = [
  [15.0, 21.6],
  [41.6, 46.7],
  [60.2, 66.9],
];

export const Speaker: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  let shift = 0;
  for (const [s, e] of SPLITS) {
    shift += interpolate(frame, [f(s), f(s) + 12, f(e) - 12, f(e)], [0, 1, 1, 0], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });
  }

  // Slow push-in across the whole piece for energy.
  const drift = interpolate(frame, [0, 60 * fps], [1, 1.04], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ backgroundColor: "#141010" }}>
      <AbsoluteFill
        style={{
          translate: `${shift * 430}px 0px`,
          scale: String(drift * (1 + shift * 0.04)),
          transformOrigin: "47% 35%",
        }}
      >
        {SEGMENTS.map((seg, i) => (
          <Video
            key={i}
            name={`Cut ${i + 1}`}
            src={staticFile("source.mp4")}
            from={Math.round(seg.outStart * fps)}
            trimBefore={Math.round(seg.srcStart * fps)}
            durationInFrames={
              Math.round((seg.outStart + seg.srcEnd - seg.srcStart) * fps) -
              Math.round(seg.outStart * fps)
            }
            premountFor={fps}
            objectFit="cover"
            style={{
              position: "absolute",
              width: "100%",
              height: "100%",
              scale: String(ZOOMS[i % ZOOMS.length]),
              transformOrigin: "47% 32%",
              filter: "contrast(1.08) saturate(1.1) brightness(1.02)",
            }}
          />
        ))}
      </AbsoluteFill>
      {/* Warm grade + vignette */}
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(120% 90% at 50% 40%, rgba(0,0,0,0) 55%, rgba(25,14,10,0.55) 100%)",
        }}
      />
      <AbsoluteFill style={{ background: "rgba(210,88,74,0.05)", mixBlendMode: "soft-light" }} />
    </AbsoluteFill>
  );
};
