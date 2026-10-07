import React from "react";
import { Video } from "@remotion/media";
import { AbsoluteFill, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { SEGMENTS, f } from "../timeline";
import { Grain } from "./Fx";

const ZOOMS = [1, 1.14, 1.04, 1.2, 1, 1.12, 1.06, 1.25, 1, 1.15, 1.05, 1.18, 1, 1.12, 1.2, 1];

// Quick punch-ins on the words that carry the story.
const PUNCHES = [1.76, 3.8, 22.44, 34.36, 36.1, 40.66, 48.4, 50.86, 58.9];

export const ReelSpeaker: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  let punch = 1;
  for (const t of PUNCHES) {
    punch *= interpolate(frame, [f(t), f(t) + 3, f(t) + 14], [1, 1.07, 1], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });
  }

  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      <AbsoluteFill style={{ scale: String(punch), transformOrigin: "50% 35%" }}>
        {SEGMENTS.map((seg, i) => (
          <Video
            key={i}
            name={`Cut ${i + 1}`}
            src={staticFile("source.mp4")}
            from={Math.round(seg.outStart * fps)}
            trimBefore={Math.round(seg.srcStart * fps)}
            durationInFrames={Math.round((seg.outStart + seg.srcEnd - seg.srcStart) * fps) - Math.round(seg.outStart * fps)}
            premountFor={fps}
            objectFit="cover"
            style={{
              position: "absolute",
              width: 3413,
              height: 1920,
              left: -1064,
              scale: String(ZOOMS[i % ZOOMS.length]),
              transformOrigin: "47% 30%",
              // Moody cinematic grade: deeper blacks, warm skin, slightly muted wall.
              filter: "contrast(1.16) saturate(1.04) brightness(0.86) sepia(0.06)",
            }}
          />
        ))}
      </AbsoluteFill>
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(85% 60% at 50% 38%, rgba(0,0,0,0) 40%, rgba(8,4,4,0.55) 75%, rgba(5,2,2,0.85) 100%)",
        }}
      />
      <AbsoluteFill
        style={{
          background: "radial-gradient(60% 40% at 100% 70%, rgba(255,45,45,0.22) 0%, rgba(255,45,45,0) 70%)",
          mixBlendMode: "screen",
        }}
      />
      <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(0,0,0,0) 50%, rgba(0,0,0,0.45) 70%, rgba(0,0,0,0.6) 100%)" }} />
      <Grain opacity={0.18} />
    </AbsoluteFill>
  );
};
