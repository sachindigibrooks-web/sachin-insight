import React from "react";
import { AbsoluteFill, Easing, interpolate, random, useCurrentFrame } from "remotion";
import { C, SAFE, SAFE_V, body, display, useLayout } from "../theme";
import { f } from "../timeline";
import { CheckIcon, CrossIcon, SearchIcon } from "../ui/Icons";
import { Stage } from "../ui/Stage";
import { StockClip } from "../ui/StockClip";
import { mix, pop, prog } from "../ui/motion";

type SceneProps = { readonly start: number };

const useAt = (start: number) => {
  const frame = useCurrentFrame();
  const at = (src: number) => f(src) - f(start);
  const { v } = useLayout();
  return { frame, at, v };
};

// Content lives in the upper ~75% so it never collides with the captions.
const Content: React.FC<{ readonly children: React.ReactNode; readonly style?: React.CSSProperties }> = ({
  children,
  style,
}) => {
  const { v } = useLayout();
  return (
    <div
      style={{
        position: "absolute",
        left: v ? SAFE_V.x : SAFE.x,
        right: v ? SAFE_V.x : SAFE.x,
        top: v ? SAFE_V.top + 30 : SAFE.y,
        bottom: v ? 560 : 290,
        ...style,
      }}
    >
      {children}
    </div>
  );
};

/* ---------- Saal 2011 ---------- */
export const Year2011: React.FC<SceneProps> = ({ start }) => {
  const { frame, at, v } = useAt(start);
  const year = Math.round(
    interpolate(frame, [at(8.7), at(9.6)], [1995, 2011], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: Easing.out(Easing.cubic),
    }),
  );
  const yearIn = prog(frame, at(8.6), 12);
  const sub = prog(frame, at(10.04), 12);
  return (
    <Stage seed="year">
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", paddingBottom: v ? 560 : 230 }}>
        <div style={{ fontFamily: body, fontWeight: 800, fontSize: 40, letterSpacing: "0.3em", color: C.clayDeep, opacity: yearIn }}>
          SAAL
        </div>
        <div
          style={{
            fontFamily: display,
            fontSize: 380,
            lineHeight: 0.85,
            color: C.ink,
            opacity: yearIn,
            scale: String(mix(yearIn, 1.2, 1)),
          }}
        >
          {year}
        </div>
        <div
          style={{
            marginTop: 16,
            padding: "12px 30px",
            background: C.ink,
            color: C.cream,
            borderRadius: 10,
            fontFamily: body,
            fontWeight: 900,
            fontSize: 42,
            letterSpacing: "0.1em",
            opacity: sub,
            rotate: `${mix(sub, -6, -2)}deg`,
          }}
        >
          EK COMPANY THI...
        </div>
      </AbsoluteFill>
    </Stage>
  );
};

/* ---------- Google search results: rank falls ---------- */
const ResultRow: React.FC<{ readonly title: string; readonly url: string; readonly hot?: boolean }> = ({
  title,
  url,
  hot,
}) => (
  <div
    style={{
      padding: "18px 26px",
      borderRadius: 16,
      background: hot ? "rgba(210,88,74,0.10)" : "transparent",
      border: hot ? `3px solid ${C.clay}` : "3px solid transparent",
    }}
  >
    <div style={{ fontFamily: body, fontWeight: 600, fontSize: 24, color: C.stone }}>{url}</div>
    <div style={{ fontFamily: body, fontWeight: 800, fontSize: 36, color: hot ? C.clayDeep : "#2F4A9E" }}>{title}</div>
  </div>
);

export const Serp: React.FC<SceneProps> = ({ start }) => {
  const { frame, at, v } = useAt(start);
  const query = "dresses";
  const typed = Math.round(
    interpolate(frame, [at(22.0), at(22.9)], [0, query.length], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    }),
  );
  const fall = prog(frame, at(24.8), 18, Easing.bezier(0.6, 0, 0.9, 0.6));
  const rank = Math.round(mix(fall, 1, 68));
  const shift = prog(frame, at(25.2), 14);

  return (
    <Stage seed="s1">
      <Content style={{ display: "flex", gap: v ? 20 : 60, flexDirection: v ? "column-reverse" : "row" }}>
        <div style={{ flex: 1 }}>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 18,
              padding: "18px 30px",
              background: C.white,
              borderRadius: 999,
              boxShadow: "0 10px 30px rgba(31,26,23,0.12)",
              fontFamily: body,
              fontWeight: 600,
              fontSize: 36,
              color: C.ink,
            }}
          >
            <SearchIcon size={36} color={C.stone} />
            {query.slice(0, typed)}
            <span style={{ opacity: Math.floor(frame / 8) % 2 === 0 ? 1 : 0, color: C.clay }}>|</span>
          </div>
          <div style={{ position: "relative", marginTop: 26, height: 470, overflow: "hidden" }}>
            <div
              style={{
                position: "absolute",
                left: 0,
                right: 0,
                top: 0,
                translate: `0px ${fall * 560}px`,
                opacity: 1 - fall * 0.9,
                rotate: `${fall * 4}deg`,
              }}
            >
              <ResultRow hot title="Billion-dollar brand — Official Store" url="www.??????.com" />
            </div>
            <div style={{ position: "absolute", left: 0, right: 0, top: mix(shift, 120, 0) }}>
              <ResultRow title="Dresses for Women | Shop Online" url="www.competitor-one.com" />
              <ResultRow title="New Arrivals: Dresses & More" url="www.competitor-two.com" />
              <ResultRow title="Summer Dresses Sale" url="www.competitor-three.com" />
            </div>
          </div>
        </div>
        <div
          style={{
            width: v ? "100%" : 440,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <div style={{ fontFamily: body, fontWeight: 800, fontSize: 30, letterSpacing: "0.16em", color: C.clayDeep }}>
            GOOGLE RANK
          </div>
          <div
            style={{
              fontFamily: display,
              fontSize: 260,
              lineHeight: 0.9,
              color: fall > 0.05 ? C.clay : C.ink,
            }}
          >
            #{rank}
          </div>
          <svg width={120} height={120} viewBox="0 0 48 48" style={{ opacity: fall }}>
            <path d="M24 6v32M12 26l12 12 12-12" stroke={C.clay} strokeWidth={6} fill="none" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </div>
      </Content>
    </Stage>
  );
};

/* ---------- Front page ... GONE ---------- */
export const Gone: React.FC<SceneProps> = ({ start }) => {
  const { frame, at, v } = useAt(start);
  const glitch = interpolate(frame, [at(32.9), at(33.8)], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const gone = pop(frame, at(34.36), 12);
  const jitter = glitch > 0 && glitch < 1 ? (random(`g${frame}`) - 0.5) * 40 : 0;
  const shake = gone > 0 && gone < 1.05 ? (random(`s${frame}`) - 0.5) * 16 : 0;

  return (
    <Stage seed="s2" tone="dark">
      <Content style={{ translate: `${shake}px ${shake / 2}px` }}>
        <div
          style={{
            fontFamily: body,
            fontWeight: 800,
            fontSize: 32,
            letterSpacing: "0.16em",
            color: C.sand,
            opacity: 1 - gone,
          }}
        >
          GOOGLE • FRONT PAGE
        </div>
        <div style={{ marginTop: 26, display: "flex", flexDirection: "column", gap: 18, opacity: 1 - gone * 0.85 }}>
          {[0, 1, 2, 3].map((i) => {
            const hot = i === 0;
            return (
              <div
                key={i}
                style={{
                  height: 92,
                  borderRadius: 16,
                  background: hot ? "rgba(210,88,74,0.22)" : "rgba(243,236,226,0.08)",
                  border: hot ? `3px solid ${C.clay}` : "3px solid rgba(243,236,226,0.12)",
                  display: "flex",
                  alignItems: "center",
                  padding: "0 30px",
                  fontFamily: body,
                  fontWeight: 800,
                  fontSize: 34,
                  color: hot ? C.cream : "rgba(243,236,226,0.5)",
                  translate: hot ? `${jitter}px 0px` : "0px 0px",
                  opacity: hot ? 1 - glitch : 1,
                  clipPath: hot && glitch > 0 ? `inset(${random(`c${frame}`) * 40}% 0 0 0)` : "none",
                }}
              >
                {hot ? "#1  Billion-dollar brand — Official Store" : `#${i + 1}  ${["", "competitor-one.com", "competitor-two.com", "competitor-three.com"][i]}`}
              </div>
            );
          })}
        </div>
      </Content>
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", paddingBottom: v ? 560 : 160 }}>
        <div
          style={{
            fontFamily: display,
            fontSize: v ? 300 : 420,
            lineHeight: 1,
            color: C.clay,
            scale: String(gone),
            opacity: Math.min(1, gone * 3),
            textShadow: "0 20px 80px rgba(210,88,74,0.45)",
          }}
        >
          GONE.
        </div>
      </AbsoluteFill>
    </Stage>
  );
};

/* ---------- SEO cheating: link scheme network ---------- */
export const Cheating: React.FC<SceneProps> = ({ start }) => {
  const { frame, at, v } = useAt(start);
  const net = prog(frame, at(39.6), 24, Easing.inOut(Easing.cubic));
  const stamp = pop(frame, at(40.66), 12);
  const cx = v ? 470 : 1180 - SAFE.x;
  const cy = v ? 720 : 330;
  const nodes = new Array(14).fill(0).map((_, i) => {
    const ang = (i / 14) * Math.PI * 2 + 0.3;
    const r = 230 + random(`r${i}`) * 90;
    return { x: cx + Math.cos(ang) * r * (v ? 0.95 : 1.3), y: cy + Math.sin(ang) * r * (v ? 0.9 : 0.8), d: i / 14 };
  });
  return (
    <Stage seed="s3" tone="dark">
      <Content>
        <svg width={v ? 940 : 1680} height={v ? 1110 : 700} style={{ position: "absolute", left: 0, top: 0 }}>
          {nodes.map((n, i) => {
            const p = Math.max(0, Math.min(1, (net - n.d * 0.6) / 0.4));
            return (
              <g key={i} opacity={p}>
                <line x1={cx} y1={cy} x2={mix(p, cx, n.x)} y2={mix(p, cy, n.y)} stroke={C.clay} strokeWidth={3} strokeDasharray="10 8" />
                <circle cx={mix(p, cx, n.x)} cy={mix(p, cy, n.y)} r={16} fill={C.inkSoft} stroke={C.sand} strokeWidth={3} />
                <text x={mix(p, cx, n.x)} y={mix(p, cy, n.y) + 6} textAnchor="middle" fontFamily={body} fontWeight={800} fontSize={14} fill={C.sand}>
                  $
                </text>
              </g>
            );
          })}
          <circle cx={cx} cy={cy} r={70} fill={C.clay} />
          <text x={cx} y={cy + 12} textAnchor="middle" fontFamily={display} fontSize={44} fill={C.white}>
            ??.COM
          </text>
        </svg>
        <div style={{ position: "absolute", left: 0, top: 40, width: 560 }}>
          <div style={{ fontFamily: body, fontWeight: 800, fontSize: 32, letterSpacing: "0.16em", color: C.sand }}>
            BLACK-HAT SEO
          </div>
          <div style={{ fontFamily: display, fontSize: 130, lineHeight: 0.9, color: C.cream, marginTop: 10 }}>
            PAID
            <br />
            LINKS
          </div>
          <div style={{ fontFamily: body, fontWeight: 600, fontSize: 32, color: C.stone, marginTop: 18, lineHeight: 1.35 }}>
            Hazaaron unrelated sites se
            <br />
            backlinks khareede gaye
          </div>
        </div>
        <div
          style={{
            position: "absolute",
            ...(v ? { left: 150, top: 660 } : { left: 0, bottom: 0 }),
            padding: "12px 34px",
            border: `8px solid ${C.clay}`,
            borderRadius: 14,
            fontFamily: display,
            fontSize: 120,
            lineHeight: 1,
            color: C.clay,
            rotate: "-8deg",
            scale: String(mix(stamp, 2.2, 1)),
            opacity: Math.min(1, stamp * 2),
          }}
        >
          CHEATING
        </div>
      </Content>
    </Stage>
  );
};

/* ---------- Caught: penalty stamp over crime-scene tape ---------- */
export const Caught: React.FC<SceneProps> = ({ start }) => {
  const { frame, at, v } = useAt(start);
  const stamp = pop(frame, at(48.4), 10);
  return (
    <StockClip src="broll/police-tape.mp4" seed="caught" trimSeconds={1}>
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", paddingBottom: v ? 560 : 200 }}>
        <div
          style={{
            padding: "24px 60px",
            border: `12px solid ${C.clay}`,
            borderRadius: 24,
            background: "rgba(31,26,23,0.55)",
            rotate: "-6deg",
            scale: String(mix(stamp, 2.4, 1)),
            opacity: Math.min(1, stamp * 2),
            textAlign: "center",
          }}
        >
          <div style={{ fontFamily: display, fontSize: 260, lineHeight: 0.9, color: C.clay }}>CAUGHT</div>
          <div style={{ fontFamily: body, fontWeight: 900, fontSize: 40, letterSpacing: "0.2em", color: C.cream }}>
            GOOGLE PENALTY
          </div>
        </div>
      </AbsoluteFill>
    </StockClip>
  );
};

/* ---------- Reveal: JCPenney ---------- */
export const Reveal: React.FC<SceneProps> = ({ start }) => {
  const { frame, at, v } = useAt(start);
  const mystery = prog(frame, 6, 12);
  const flip = prog(frame, at(50.86), 16, Easing.bezier(0.65, 0, 0.35, 1));
  const sub = prog(frame, at(53.06), 14);
  const showName = flip > 0.5;
  return (
    <Stage seed="s5">
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", paddingBottom: v ? 560 : 220 }}>
        <div style={{ fontFamily: body, fontWeight: 800, fontSize: 34, letterSpacing: "0.2em", color: C.clayDeep, opacity: mystery }}>
          WOH COMPANY THI...
        </div>
        <div
          style={{
            marginTop: 24,
            padding: "30px 80px",
            borderRadius: 28,
            background: showName ? C.clay : C.ink,
            boxShadow: "0 30px 80px rgba(31,26,23,0.3)",
            rotate: `0deg`,
            scale: `1 ${Math.abs(Math.cos(flip * Math.PI))}`,
            opacity: mystery,
          }}
        >
          <div style={{ fontFamily: display, fontSize: v ? 170 : 230, lineHeight: 1, color: C.white, letterSpacing: "0.02em" }}>
            {showName ? "JCPENNEY" : "? ? ? ? ?"}
          </div>
        </div>
        <div
          style={{
            marginTop: 30,
            display: "flex",
            gap: 18,
            opacity: sub,
            translate: `0px ${mix(sub, 24, 0)}px`,
          }}
        >
          {["AMERICAN", "RETAIL GIANT", "2011"].map((t, i) => (
            <div
              key={t}
              style={{
                padding: "12px 26px",
                borderRadius: 999,
                background: i === 1 ? C.ink : C.white,
                color: i === 1 ? C.cream : C.ink,
                fontFamily: body,
                fontWeight: 900,
                fontSize: 36,
                letterSpacing: "0.08em",
              }}
            >
              {t}
            </div>
          ))}
        </div>
      </AbsoluteFill>
    </Stage>
  );
};

/* ---------- Types of SEO: what this video is (and isn't) ---------- */
export const TypesOfSeo: React.FC<SceneProps> = ({ start }) => {
  const { frame, at, v } = useAt(start);
  const title = prog(frame, at(67.1), 16);
  const yes: [string, number][] = [
    ["Real story", 69.4],
    ["Real example", 70.42],
  ];
  const no: [string, number][] = [
    ["Complex sentences", 72.06],
    ["Definitions", 73.88],
    ["Ratta maaro theory", 75.04],
  ];
  const Row: React.FC<{ label: string; t: number; good: boolean }> = ({ label, t, good }) => {
    const p = prog(frame, at(t), 12);
    const strike = good ? 0 : prog(frame, at(t) + 8, 10);
    return (
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 18,
          padding: "14px 26px 14px 14px",
          borderRadius: 18,
          background: C.white,
          boxShadow: "0 10px 26px rgba(31,26,23,0.10)",
          opacity: p,
          translate: `0px ${mix(p, 24, 0)}px`,
        }}
      >
        <div
          style={{
            width: 58,
            height: 58,
            borderRadius: 14,
            background: good ? C.olive : C.clay,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            scale: String(pop(frame, at(t) + 3)),
          }}
        >
          {good ? <CheckIcon size={40} color={C.white} /> : <CrossIcon size={38} color={C.white} />}
        </div>
        <div style={{ position: "relative", fontFamily: body, fontWeight: 800, fontSize: 42, color: good ? C.ink : C.stone }}>
          {label}
          {good ? null : (
            <div
              style={{
                position: "absolute",
                left: -4,
                right: -4,
                top: "52%",
                height: 6,
                borderRadius: 4,
                background: C.clay,
                transformOrigin: "left center",
                scale: `${strike} 1`,
              }}
            />
          )}
        </div>
      </div>
    );
  };
  return (
    <Stage seed="s6">
      <Content>
        <div style={{ display: "flex", alignItems: "flex-end", gap: 30, opacity: title, translate: `0px ${mix(title, 30, 0)}px` }}>
          <div style={{ fontFamily: display, fontSize: v ? 160 : 210, lineHeight: 0.85, color: C.ink }}>
            TYPES OF <span style={{ color: C.clay }}>SEO</span>
          </div>
        </div>
        <div style={{ display: "flex", gap: v ? 18 : 40, marginTop: 50, flexDirection: v ? "column" : "row" }}>
          <div style={{ display: "flex", flexDirection: "column", gap: 18, width: v ? "100%" : 600 }}>
            {yes.map(([l, t]) => (
              <Row key={l} label={l} t={t} good />
            ))}
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 18, width: v ? "100%" : 640 }}>
            {no.map(([l, t]) => (
              <Row key={l} label={l} t={t} good={false} />
            ))}
          </div>
        </div>
      </Content>
    </Stage>
  );
};
