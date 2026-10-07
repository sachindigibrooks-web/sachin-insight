import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { C, SAFE, SAFE_V, body, display, useLayout } from "../theme";
import { f } from "../timeline";
import { BookIcon, CheckIcon, CrossIcon, ShirtIcon, SofaIcon, TvIcon } from "../ui/Icons";
import { mix, pop, prog } from "../ui/motion";
import { Tape, TornSheet, paperCard } from "../ui/Paper";

type SceneProps = { readonly start: number };

const useAt = (start: number) => {
  const frame = useCurrentFrame();
  const at = (src: number) => f(src) - f(start);
  return { frame, at };
};

const useExit = (len = 10) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  return interpolate(frame, [durationInFrames - len, durationInFrames], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
};

/* ---------- Hook: "shortcut ... bhaari pad gaya" ---------- */
export const HookText: React.FC<SceneProps> = ({ start }) => {
  const { frame, at } = useAt(start);
  const exit = useExit();
  const a = prog(frame, at(1.76), 12);
  const b = prog(frame, at(3.8), 14);
  const dash = prog(frame, at(1.9), 40, Easing.inOut(Easing.cubic));
  const { v } = useLayout();
  if (v) {
    return (
      <AbsoluteFill style={{ opacity: exit, alignItems: "center" }}>
        <div
          style={{
            position: "absolute",
            top: 1075,
            padding: "10px 36px 4px",
            ...paperCard,
            fontFamily: display,
            fontSize: 120,
            lineHeight: 1,
            color: C.ink,
            opacity: a,
            rotate: `${mix(a, -8, -3)}deg`,
            scale: String(mix(a, 1.2, 1)),
            boxShadow: "0 16px 40px rgba(0,0,0,0.35)",
          }}
        >
          SHORT<span style={{ color: C.clay }}>CUT?</span>
        </div>
        <div
          style={{
            position: "absolute",
            top: 1228,
            padding: "8px 22px",
            background: C.clay,
            color: C.white,
            fontFamily: body,
            fontWeight: 900,
            fontSize: 40,
            borderRadius: 12,
            opacity: b,
            rotate: "2deg",
            translate: `0px ${mix(b, 20, 0)}px`,
            boxShadow: "0 12px 30px rgba(0,0,0,0.3)",
          }}
        >
          BHAARI PAD GAYA
        </div>
      </AbsoluteFill>
    );
  }
  return (
    <AbsoluteFill style={{ opacity: exit }}>
      <div style={{ position: "absolute", left: SAFE.x, top: 150, width: 560 }}>
        <div
          style={{
            fontFamily: display,
            fontSize: 150,
            lineHeight: 0.9,
            color: C.white,
            opacity: a,
            translate: `${mix(a, -40, 0)}px 0px`,
            textShadow: "0 10px 40px rgba(0,0,0,0.45)",
          }}
        >
          SHORT
          <br />
          <span style={{ color: C.amber }}>CUT?</span>
        </div>
        <svg width={520} height={160} viewBox="0 0 520 160" style={{ marginTop: 10, overflow: "visible" }}>
          <path
            d="M10 120 C 140 10, 260 160, 420 50"
            stroke={b > 0 ? C.clay : C.white}
            strokeWidth={8}
            strokeLinecap="round"
            fill="none"
            strokeDasharray="22 18"
            strokeDashoffset={0}
            pathLength={1000}
            style={{ strokeDasharray: `${dash * 1000} 1000` }}
          />
          <g style={{ opacity: b, scale: String(pop(frame, at(3.8))), transformOrigin: "440px 40px" }}>
            <circle cx={450} cy={40} r={34} fill={C.clay} />
            <path d="M436 26l28 28M464 26l-28 28" stroke={C.white} strokeWidth={8} strokeLinecap="round" />
          </g>
        </svg>
        <div
          style={{
            marginTop: 14,
            display: "inline-block",
            padding: "10px 22px",
            background: C.clay,
            color: C.white,
            fontFamily: body,
            fontWeight: 900,
            fontSize: 44,
            borderRadius: 10,
            opacity: b,
            translate: `0px ${mix(b, 20, 0)}px`,
          }}
        >
          BHAARI PAD GAYA
        </div>
      </div>
    </AbsoluteFill>
  );
};

/* ---------- "Ek story sunata hoon" tag ---------- */
export const StoryTag: React.FC<SceneProps> = ({ start }) => {
  const { frame, at } = useAt(start);
  const exit = useExit();
  const a = prog(frame, at(6.98), 14);
  const { v } = useLayout();
  return (
    <AbsoluteFill style={{ opacity: exit }}>
      <div
        style={{
          position: "absolute",
          left: v ? SAFE_V.x : SAFE.x,
          top: v ? 140 : SAFE.y + 20,
          display: "flex",
          alignItems: "center",
          gap: 18,
          padding: "16px 30px 16px 20px",
          background: C.cream,
          borderRadius: 999,
          color: C.ink,
          fontFamily: body,
          fontWeight: 900,
          fontSize: 40,
          letterSpacing: "0.06em",
          boxShadow: "0 12px 40px rgba(0,0,0,0.3)",
          clipPath: `inset(0 ${(1 - a) * 100}% 0 0 round 999px)`,
        }}
      >
        <div
          style={{
            width: 56,
            height: 56,
            borderRadius: 999,
            background: C.clay,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: C.white,
          }}
        >
          <BookIcon size={36} color={C.white} />
        </div>
        STORY TIME
      </div>
    </AbsoluteFill>
  );
};

/* ---------- Website / Content / Products checklist ---------- */
export const Checks: React.FC<SceneProps> = ({ start }) => {
  const { frame, at } = useAt(start);
  const exit = useExit();
  const { v } = useLayout();
  const items: [string, number][] = [
    ["Website", 26.75],
    ["Content", 27.72],
    ["Products", 28.88],
  ];
  return (
    <AbsoluteFill style={{ opacity: exit }}>
      <div style={{ position: "absolute", left: v ? 90 : SAFE.x, top: v ? 990 : 200, display: "flex", flexDirection: "column", gap: 22 }}>
        {items.map(([label, t]) => {
          const p = prog(frame, at(t), 12);
          return (
            <div
              key={label}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 20,
                padding: "14px 34px 14px 16px",
                background: "rgba(243,236,226,0.95)",
                borderRadius: 18,
                color: C.ink,
                fontFamily: body,
                fontWeight: 800,
                fontSize: 50,
                opacity: p,
                translate: `${mix(p, -60, 0)}px 0px`,
                boxShadow: "0 14px 40px rgba(0,0,0,0.28)",
              }}
            >
              <div
                style={{
                  width: 62,
                  height: 62,
                  borderRadius: 14,
                  background: C.olive,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  scale: String(pop(frame, at(t) + 4)),
                }}
              >
                <CheckIcon size={42} color={C.white} />
              </div>
              {label}
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

/* ---------- "Kyun hua ye?" ---------- */
export const Kyun: React.FC<SceneProps> = ({ start }) => {
  const { frame, at } = useAt(start);
  const exit = useExit(6);
  const p = pop(frame, at(36.1), 14);
  const q = pop(frame, at(36.5), 14);
  const { v } = useLayout();
  return (
    <AbsoluteFill style={{ opacity: exit }}>
      <div
        style={{
          position: "absolute",
          ...(v ? { left: 0, right: 0, top: 1060, justifyContent: "center" } : { right: SAFE.x, top: 170 }),
          display: "flex",
          alignItems: "flex-start",
          fontFamily: display,
          color: v ? C.ink : C.white,
          textShadow: v ? "0 6px 30px rgba(255,255,255,0.6)" : "0 10px 40px rgba(0,0,0,0.5)",
        }}
      >
        <span style={{ fontSize: 210, lineHeight: 0.9, scale: String(p) }}>KYUN</span>
        <span
          style={{
            fontSize: 260,
            lineHeight: 0.8,
            color: C.clay,
            scale: String(q),
            rotate: `${mix(q, -30, 8)}deg`,
          }}
        >
          ?
        </span>
      </div>
    </AbsoluteFill>
  );
};

/* ---------- Lesson card ---------- */
export const Lesson: React.FC<SceneProps> = ({ start }) => {
  const { frame, at } = useAt(start);
  const exit = useExit();
  const a = prog(frame, at(55.3), 16);
  const b = prog(frame, at(58.52), 14);
  const { v } = useLayout();
  return (
    <AbsoluteFill style={{ opacity: exit }}>
      <div
        style={{
          position: "absolute",
          left: v ? SAFE_V.x : SAFE.x,
          top: v ? SAFE_V.top + 20 : SAFE.y + 30,
          display: "flex",
          alignItems: "stretch",
          borderRadius: 20,
          overflow: "hidden",
          boxShadow: "0 16px 50px rgba(0,0,0,0.35)",
          clipPath: `inset(0 ${(1 - a) * 100}% 0 0)`,
        }}
      >
        <div style={{ background: C.clay, padding: "0 26px", display: "flex", alignItems: "center" }}>
          <BookIcon size={64} color={C.white} />
        </div>
        <div style={{ ...paperCard, padding: "20px 34px" }}>
          <div style={{ fontFamily: body, fontWeight: 800, fontSize: 28, color: C.clayDeep, letterSpacing: "0.12em" }}>
            SEO INDUSTRY KA
          </div>
          <div style={{ fontFamily: display, fontSize: v ? 76 : 86, lineHeight: 1, color: C.ink }}>
            SABSE BADA{" "}
            <span style={{ color: C.clay, display: "inline-block", scale: String(mix(b, 0.6, 1)), opacity: b }}>
              LESSON
            </span>
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

/* ---------- Ending CTA ---------- */
export const EndCta: React.FC<SceneProps> = ({ start }) => {
  const { frame, at } = useAt(start);
  const { durationInFrames } = useVideoConfig();
  const a = prog(frame, at(77.0), 12);
  const { v } = useLayout();
  const fade = interpolate(frame, [durationInFrames - 12, durationInFrames], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <AbsoluteFill>
      <div
        style={{
          position: "absolute",
          ...(v ? { left: SAFE_V.x, right: SAFE_V.x, top: 1000, justifyContent: "center" } : { right: SAFE.x, top: SAFE.y + 40 }),
          display: "flex",
          alignItems: "center",
          gap: 20,
          padding: "18px 34px",
          background: C.clay,
          color: C.white,
          borderRadius: 16,
          fontFamily: display,
          fontSize: v ? 66 : 80,
          lineHeight: 1,
          clipPath: `inset(0 0 0 ${(1 - a) * 100}% round 16px)`,
          boxShadow: "0 16px 50px rgba(0,0,0,0.35)",
        }}
      >
        CHALIYE SHURU KARTE HAIN
        <svg width={56} height={56} viewBox="0 0 48 48">
          <path d="M8 24h30M26 12l12 12-12 12" stroke={C.white} strokeWidth={6} fill="none" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </div>
      <AbsoluteFill style={{ background: C.ink, opacity: fade }} />
    </AbsoluteFill>
  );
};

/* ---------- Split-screen side panel ---------- */
const Panel: React.FC<{ readonly children: React.ReactNode }> = ({ children }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const enter = prog(frame, 0, 14);
  const exit = interpolate(frame, [durationInFrames - 12, durationInFrames], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.7, 0, 0.84, 0),
  });
  const x = mix(enter, -900, 0) + exit * -900;
  const { v } = useLayout();
  if (v) {
    return (
      <TornSheet seed="panel">
        <AbsoluteFill style={{ ...paperCard }} />
        <Tape style={{ right: 60, top: 150, rotate: "24deg" }} />
        <div style={{ position: "absolute", left: 130, top: 250, width: 650, scale: "1.26", transformOrigin: "top left" }}>
          {children}
        </div>
      </TornSheet>
    );
  }
  return (
    <AbsoluteFill>
      <div
        style={{
          position: "absolute",
          left: 0,
          top: 0,
          bottom: 0,
          width: 860,
          translate: `${x}px 0px`,
          filter: "drop-shadow(18px 0 26px rgba(0,0,0,0.4))",
        }}
      >
        <div
          style={{
            position: "absolute",
            inset: 0,
            ...paperCard,
            clipPath:
              "polygon(0 0, 97% 0, 99% 4%, 96.5% 9%, 99.5% 15%, 97% 22%, 100% 29%, 96.8% 36%, 99% 43%, 97.2% 50%, 99.6% 57%, 96.6% 64%, 99.2% 71%, 97% 78%, 99.8% 85%, 96.9% 92%, 98.5% 100%, 0 100%)",
          }}
        />
        <Tape style={{ right: 10, top: 40, rotate: "38deg" }} />
        <div style={{ position: "absolute", left: SAFE.x, top: 130, right: 90 }}>{children}</div>
      </div>
    </AbsoluteFill>
  );
};

const Eyebrow: React.FC<{ readonly children: React.ReactNode }> = ({ children }) => (
  <div style={{ fontFamily: body, fontWeight: 800, fontSize: 30, letterSpacing: "0.14em", color: C.clayDeep }}>
    {children}
  </div>
);

const Headline: React.FC<{ readonly children: React.ReactNode }> = ({ children }) => (
  <div style={{ fontFamily: display, fontSize: 104, lineHeight: 0.95, color: C.ink, marginTop: 8 }}>{children}</div>
);

/* ---------- Clothes / electronics / furniture ---------- */
export const Categories: React.FC<SceneProps> = ({ start }) => {
  const { frame, at } = useAt(start);
  const items: [string, React.FC<{ size?: number; color?: string }>, number][] = [
    ["Clothes", ShirtIcon, 17.64],
    ["Electronics", TvIcon, 18.32],
    ["Furniture", SofaIcon, 19.3],
  ];
  const chart = prog(frame, at(16.12), 50, Easing.inOut(Easing.cubic));
  return (
    <Panel>
      <Eyebrow>2011 • SALES</Eyebrow>
      <Headline>
        HAR CHEEZ
        <br />
        <span style={{ color: C.clay }}>SELL HO RAHI THI</span>
      </Headline>
      <div style={{ display: "flex", gap: 22, marginTop: 44 }}>
        {items.map(([label, Icon, t]) => {
          const p = pop(frame, at(t), 14);
          return (
            <div
              key={label}
              style={{
                width: 196,
                height: 196,
                borderRadius: 24,
                background: C.white,
                boxShadow: "0 12px 30px rgba(31,26,23,0.12)",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                gap: 10,
                scale: String(p),
                opacity: Math.min(1, p * 2),
                color: C.ink,
              }}
            >
              <Icon size={92} color={C.clay} />
              <div style={{ fontFamily: body, fontWeight: 800, fontSize: 26 }}>{label}</div>
            </div>
          );
        })}
      </div>
      <svg width={630} height={150} viewBox="0 0 630 150" style={{ marginTop: 34 }}>
        <path
          d="M0 140 L90 120 L180 126 L270 92 L360 98 L450 56 L540 40 L630 8"
          stroke={C.olive}
          strokeWidth={8}
          fill="none"
          strokeLinecap="round"
          strokeLinejoin="round"
          pathLength={1}
          strokeDasharray={`${chart} 1`}
        />
      </svg>
    </Panel>
  );
};

/* ---------- Google guidelines vs their tactics ---------- */
export const Algorithm: React.FC<SceneProps> = ({ start }) => {
  const { frame, at } = useAt(start);
  const rules = ["Natural links", "Helpful content", "No paid links", "No link schemes"];
  const x = pop(frame, at(45.62), 16);
  return (
    <Panel>
      <Eyebrow>GOOGLE ALGORITHM</Eyebrow>
      <Headline>
        RULES KE <span style={{ color: C.clay }}>KHILAAF</span>
      </Headline>
      <div
        style={{
          position: "relative",
          marginTop: 40,
          padding: "30px 36px",
          background: C.white,
          borderRadius: 24,
          boxShadow: "0 12px 30px rgba(31,26,23,0.12)",
        }}
      >
        {rules.map((r, i) => {
          const p = prog(frame, at(42.4) + i * 7, 12);
          return (
            <div
              key={r}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 18,
                padding: "12px 0",
                borderBottom: i < rules.length - 1 ? `2px solid ${C.sand}` : "none",
                fontFamily: body,
                fontWeight: 800,
                fontSize: 40,
                color: C.ink,
                opacity: p,
                translate: `${mix(p, 30, 0)}px 0px`,
              }}
            >
              <CheckIcon size={40} color={C.olive} />
              {r}
            </div>
          );
        })}
        <div
          style={{
            position: "absolute",
            right: -30,
            top: -40,
            width: 150,
            height: 150,
            borderRadius: 999,
            background: C.clay,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            scale: String(x),
            boxShadow: "0 14px 40px rgba(142,59,48,0.5)",
          }}
        >
          <CrossIcon size={90} color={C.white} />
        </div>
      </div>
    </Panel>
  );
};

/* ---------- "Most people just define it" ---------- */
export const MostPeople: React.FC<SceneProps> = ({ start }) => {
  const { frame, at } = useAt(start);
  const strike = prog(frame, at(65.6), 14);
  const tag = prog(frame, at(62.38), 14);
  return (
    <Panel>
      <Eyebrow>AAJ KI VIDEO MEIN</Eyebrow>
      <Headline>
        ZYAADATAR LOG
        <br />
        SIRF <span style={{ color: C.clay }}>DEFINE</span>
        <br />
        KARTE HAIN
      </Headline>
      <div
        style={{
          position: "relative",
          marginTop: 44,
          padding: "28px 34px",
          background: C.white,
          borderRadius: 24,
          boxShadow: "0 12px 30px rgba(31,26,23,0.12)",
          fontFamily: body,
          fontWeight: 600,
          fontSize: 34,
          lineHeight: 1.4,
          color: C.stone,
          opacity: tag,
        }}
      >
        <div style={{ fontWeight: 900, color: C.ink }}>SEO (n.)</div>
        “Search Engine Optimization is the process of improving...”
        <div
          style={{
            position: "absolute",
            left: 24,
            right: 24,
            top: "55%",
            height: 10,
            borderRadius: 6,
            background: C.clay,
            transformOrigin: "left center",
            scale: `${strike} 1`,
          }}
        />
      </div>
    </Panel>
  );
};
