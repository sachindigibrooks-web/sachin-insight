import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { PAGES } from "../captions";
import { C, SAFE_V, body, useLayout } from "../theme";

// Word-by-word animated subtitles, centred inside the bottom safe area.
export const Captions: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const { v } = useLayout();

  const page = PAGES.find((p) => t >= p.start && t < p.end);
  if (!page) return null;

  const pageIn = interpolate(t - page.start, [0, 0.18], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });

  return (
    <AbsoluteFill style={{ justifyContent: "flex-end", alignItems: "center", pointerEvents: "none" }}>
      <div
        style={{
          marginBottom: v ? SAFE_V.bottom + 20 : 104,
          maxWidth: v ? 1080 - 2 * 90 : 1920 - 2 * 240,
          display: "flex",
          flexWrap: "wrap",
          justifyContent: "center",
          gap: "0 18px",
          fontFamily: body,
          fontWeight: 900,
          fontSize: v ? 70 : 66,
          lineHeight: 1.15,
          letterSpacing: "-0.01em",
          opacity: pageIn,
          translate: `0px ${interpolate(pageIn, [0, 1], [18, 0])}px`,
        }}
      >
        {page.words.map((w, i) => {
          const active = t >= w.start && t < w.end + 0.05;
          const spoken = t >= w.start;
          const pop = interpolate(t - w.start, [0, 0.12, 0.24], [0.9, 1.1, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          });
          const color = active ? C.white : w.keyword ? C.amber : C.white;
          return (
            <span
              key={i}
              style={{
                position: "relative",
                display: "inline-block",
                padding: "2px 12px",
                color,
                opacity: spoken ? 1 : 0.55,
                scale: spoken ? String(pop) : "1",
                textShadow: "0 4px 0 rgba(20,14,12,0.55), 0 0 24px rgba(20,14,12,0.55)",
                WebkitTextStroke: "2px rgba(31,26,23,0.9)",
                paintOrder: "stroke fill",
              }}
            >
              {active ? (
                <span
                  style={{
                    position: "absolute",
                    inset: "6px 0 4px 0",
                    borderRadius: 14,
                    background: C.clay,
                    zIndex: -1,
                    boxShadow: "0 8px 22px rgba(142,59,48,0.45)",
                  }}
                />
              ) : null}
              {w.text}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
