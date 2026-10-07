import React from "react";
import { Video } from "@remotion/media";
import { Easing, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { mix } from "../ui/motion";
import { R } from "./style";

type Screen = { readonly video?: string; readonly emoji?: string; readonly trim?: number };

// A retro CRT TV drawn in CSS (ref 2's stacked-TV b-roll).
const Tv: React.FC<{
  readonly screen: Screen;
  readonly width: number;
  readonly start: number;
  readonly style?: React.CSSProperties;
}> = ({ screen, width, start, style }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = interpolate(frame - start, [0, 12], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.34, 1.4, 0.64, 1),
  });
  const on = interpolate(frame - start, [6, 12], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const h = width * 0.78;
  return (
    <div
      style={{
        position: "absolute",
        width,
        height: h,
        borderRadius: 26,
        background: "linear-gradient(160deg, #C9C9C6 0%, #A9A9A5 55%, #8E8E8A 100%)",
        boxShadow: "inset 0 4px 0 rgba(255,255,255,0.5), inset 0 -8px 0 rgba(0,0,0,0.18), 0 30px 50px rgba(0,0,0,0.35)",
        translate: `0px ${mix(p, -500, 0)}px`,
        opacity: Math.min(1, p * 3),
        ...style,
      }}
    >
      <div
        style={{
          position: "absolute",
          left: width * 0.06,
          top: h * 0.08,
          width: width * 0.72,
          height: h * 0.8,
          borderRadius: 30,
          overflow: "hidden",
          background: "#111",
          boxShadow: "inset 0 0 30px rgba(0,0,0,0.9), 0 0 0 6px #6E6E6A",
        }}
      >
        <div style={{ position: "absolute", inset: 0, opacity: on }}>
          {screen.video ? (
            <Video
              src={staticFile(screen.video)}
              trimBefore={Math.round((screen.trim ?? 0) * fps)}
              muted
              objectFit="cover"
              style={{ width: "100%", height: "100%", filter: "saturate(1.1) contrast(1.1)" }}
            />
          ) : (
            <div style={{ width: "100%", height: "100%", background: R.redDeep, display: "flex", alignItems: "center", justifyContent: "center" }}>
              <Img src={staticFile(`emoji/${screen.emoji}.webp`)} style={{ width: "62%" }} />
            </div>
          )}
          {/* scanlines + glass glare */}
          <div
            style={{
              position: "absolute",
              inset: 0,
              background: "repeating-linear-gradient(0deg, rgba(0,0,0,0.18) 0 2px, transparent 2px 5px)",
            }}
          />
          <div
            style={{
              position: "absolute",
              inset: 0,
              background: "radial-gradient(120% 90% at 30% 20%, rgba(255,255,255,0.22), transparent 45%)",
            }}
          />
        </div>
      </div>
      {/* knobs + speaker grille */}
      <div style={{ position: "absolute", right: width * 0.06, top: h * 0.14, width: width * 0.1, display: "flex", flexDirection: "column", gap: h * 0.06 }}>
        {[0, 1].map((k) => (
          <div key={k} style={{ width: "100%", aspectRatio: "1", borderRadius: 999, background: "radial-gradient(circle at 35% 35%, #E5E5E2, #7C7C78)" }} />
        ))}
        {[0, 1, 2, 3, 4].map((k) => (
          <div key={`g${k}`} style={{ width: "100%", height: 5, borderRadius: 3, background: "#6E6E6A" }} />
        ))}
      </div>
    </div>
  );
};

export const TvStack: React.FC<{ readonly screens: [Screen, Screen, Screen]; readonly starts: [number, number, number] }> = ({
  screens,
  starts,
}) => (
  <>
    <Tv screen={screens[0]} width={560} start={starts[0]} style={{ left: 90, top: 1010, rotate: "-2deg" }} />
    <Tv screen={screens[1]} width={500} start={starts[1]} style={{ left: 150, top: 620, rotate: "1.5deg" }} />
    <Tv screen={screens[2]} width={440} start={starts[2]} style={{ left: 120, top: 280, rotate: "-1deg" }} />
  </>
);
