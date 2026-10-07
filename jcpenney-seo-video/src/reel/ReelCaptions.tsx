import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { WORDS, type Word } from "../captions";
import { toOut } from "../timeline";
import { CAPTION_OFF, R, glow, sora } from "./style";

type Page = { start: number; end: number; words: (Word & { i: number })[] };

// Short pages (max 3 words) so each beat lands, like the references.
const PAGES: Page[] = (() => {
  const pages: Page[] = [];
  let cur: (Word & { i: number })[] = [];
  const flush = () => {
    if (cur.length) pages.push({ start: cur[0].start, end: cur[cur.length - 1].end, words: cur });
    cur = [];
  };
  WORDS.forEach((w, i) => {
    const next = WORDS[i + 1];
    if (cur.length >= 3) flush();
    cur.push({ ...w, i });
    if (/[.?!,]$/.test(w.text) || !next || next.start - w.end > 0.25 || (w.keyword && cur.length >= 2)) flush();
  });
  flush();
  return pages.map((p, k) => ({ ...p, end: Math.min(pages[k + 1]?.start ?? p.end + 0.5, p.end + 0.5) }));
})();

const OFF = CAPTION_OFF.map(([s, e]) => [toOut(s), toOut(e)] as const);

// Keyword styles rotate between the three treatments seen in the references.
const keywordStyle = (n: number): React.CSSProperties => {
  switch (n % 3) {
    case 0:
      return { color: R.white, textShadow: glow("rgba(255,255,255,0.55)", 0.7) };
    case 1:
      return { color: R.green, textShadow: glow("rgba(61,255,143,0.6)", 0.7) };
    default:
      return { color: R.white, background: R.redDeep, padding: "0 16px", borderRadius: 6 };
  }
};

export const ReelCaptions: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  if (OFF.some(([s, e]) => t >= s && t < e)) return null;
  const page = PAGES.find((p) => t >= p.start && t < p.end);
  if (!page) return null;

  const small = page.words.filter((w) => !w.keyword);
  const big = page.words.filter((w) => w.keyword);

  const renderWord = (w: Word & { i: number }, isBig: boolean) => {
    const p = interpolate(t - w.start, [-0.02, 0.14], [0, 1], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: Easing.bezier(0.16, 1, 0.3, 1),
    });
    return (
      <span
        key={w.i}
        style={{
          display: "inline-block",
          margin: isBig ? "0 10px" : "0 7px",
          opacity: p,
          scale: String(interpolate(p, [0, 1], [isBig ? 1.35 : 0.8, 1])),
          filter: `blur(${(1 - p) * 8}px)`,
          ...(isBig ? keywordStyle(w.i) : { color: R.white }),
        }}
      >
        {w.text.toLowerCase().replace(/[,]$/, "")}
      </span>
    );
  };

  return (
    <AbsoluteFill style={{ alignItems: "center", pointerEvents: "none" }}>
      <div
        style={{
          position: "absolute",
          top: 1150,
          left: 80,
          right: 80,
          textAlign: "center",
          fontFamily: sora,
          letterSpacing: "-0.03em",
          textShadow: "0 4px 18px rgba(0,0,0,0.65)",
        }}
      >
        {small.length ? (
          <div style={{ fontSize: 54, fontWeight: 600, lineHeight: 1.1 }}>{small.map((w) => renderWord(w, false))}</div>
        ) : null}
        {big.length ? (
          <div style={{ fontSize: 108, fontWeight: 800, lineHeight: 1.05, marginTop: 4 }}>{big.map((w) => renderWord(w, true))}</div>
        ) : null}
      </div>
    </AbsoluteFill>
  );
};
