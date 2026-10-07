import React from "react";
import { Video } from "@remotion/media";
import { AbsoluteFill, Easing, Img, interpolate, random, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { f } from "../timeline";
import { mix, pop, prog } from "../ui/motion";
import { BracketLabel, Brackets, DarkBg, Emoji, GreyBg, NeonText, RedTag, Streaks, ZoomIn } from "./Fx";
import { R, bebas, glow, sora } from "./style";
import { TvStack } from "./TvStack";

type P = { readonly start: number };

const useAt = (start: number) => {
  const frame = useCurrentFrame();
  return { frame, at: (src: number) => f(src) - f(start) };
};

const Center: React.FC<{ readonly children: React.ReactNode; readonly top?: number; readonly style?: React.CSSProperties }> = ({
  children,
  top,
  style,
}) => (
  <AbsoluteFill
    style={{
      alignItems: "center",
      justifyContent: top === undefined ? "center" : "flex-start",
      paddingTop: top,
      paddingBottom: top === undefined ? 260 : 0,
      ...style,
    }}
  >
    {children}
  </AbsoluteFill>
);

/* Graded full-frame stock clip. */
const Footage: React.FC<{ readonly src: string; readonly trim?: number; readonly tint?: string; readonly focusX?: number }> = ({
  src,
  trim = 0,
  tint,
  focusX = 0.5,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  return (
    <AbsoluteFill style={{ background: "#000", overflow: "hidden" }}>
      <Video
        src={staticFile(src)}
        trimBefore={Math.round(trim * fps)}
        muted
        objectFit="cover"
        style={{
          // 16:9 clip at full height, centred on its subject.
          position: "absolute",
          height: "100%",
          width: 3413,
          left: Math.min(0, Math.max(1080 - 3413, 540 - focusX * 3413)),
          scale: String(interpolate(frame, [0, durationInFrames], [1.05, 1.15])),
          filter: "contrast(1.15) saturate(0.95) brightness(0.8)",
        }}
      />
      {tint ? <AbsoluteFill style={{ background: tint, mixBlendMode: "multiply" }} /> : null}
      <AbsoluteFill style={{ background: "radial-gradient(90% 60% at 50% 45%, transparent 35%, rgba(0,0,0,0.75) 100%)" }} />
    </AbsoluteFill>
  );
};

/* ---- "SHORTCUT?" neon title ---- */
export const ShortcutTitle: React.FC<P> = ({ start }) => {
  const { at } = useAt(start);
  return (
    <ZoomIn flash={R.red}>
      <DarkBg />
      <Streaks />
      <Center>
        <Brackets width={860} height={420} start={at(1.76)} />
        <NeonText size={250} start={at(1.76)}>
          SHORTCUT?
        </NeonText>
      </Center>
    </ZoomIn>
  );
};

/* ---- "bhaari pad gaya" stock beat ---- */
export const WorriedClip: React.FC<P> = ({ start }) => {
  const { at } = useAt(start);
  return (
    <ZoomIn>
      <Footage src="broll/worried-man.mp4" trim={2} tint="rgba(255,90,80,0.35)" focusX={0.68} />
      <Center top={300}>
        <Emoji name="scream" size={240} start={at(3.9)} />
      </Center>
    </ZoomIn>
  );
};

/* ---- 2011 ---- */
export const Year: React.FC<P> = ({ start }) => {
  const { frame, at } = useAt(start);
  const year = Math.round(
    interpolate(frame, [at(8.7), at(9.5)], [1990, 2011], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: Easing.out(Easing.cubic),
    }),
  );
  return (
    <ZoomIn>
      <DarkBg hue="#7A1A10" />
      <Center>
        <div style={{ fontFamily: sora, fontWeight: 600, fontSize: 54, color: R.white, opacity: 0.85 }}>saal</div>
        <NeonText size={360} color={R.gold} filled start={0}>
          {year}
        </NeonText>
        <div style={{ marginTop: 24 }}>
          <BracketLabel start={at(10.04)}>ek company thi</BracketLabel>
        </div>
      </Center>
    </ZoomIn>
  );
};

/* ---- $1 billion brand: money bag + flying notes ---- */
export const Billion: React.FC<P> = ({ start }) => {
  const { frame, at } = useAt(start);
  const n = Math.round(
    interpolate(frame, [at(11.2), at(12.4)], [0, 1000000000], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: Easing.out(Easing.cubic),
    }),
  );
  return (
    <ZoomIn>
      <DarkBg hue="#0F5A33" />
      {new Array(14).fill(0).map((_, i) => {
        const x = random(`bx${i}`) * 1080;
        const speed = 9 + random(`bs${i}`) * 10;
        const y = ((frame * speed + random(`by${i}`) * 2200) % 2300) - 300;
        return (
          <Img
            key={i}
            src={staticFile("emoji/dollar.webp")}
            style={{
              position: "absolute",
              left: x - 90,
              top: y,
              width: 150 + random(`bw${i}`) * 90,
              rotate: `${frame * (random(`br${i}`) - 0.5) * 6}deg`,
              opacity: 0.8,
              filter: `blur(${random(`bb${i}`) > 0.6 ? 4 : 0}px)`,
            }}
          />
        );
      })}
      <Center>
        <Emoji name="money-bag" size={420} start={2} />
        <div style={{ fontFamily: bebas, fontSize: 150, color: R.green, textShadow: glow("rgba(61,255,143,0.55)", 0.8), lineHeight: 1 }}>
          ${n.toLocaleString("en-US")}
        </div>
        <BracketLabel start={at(12.4)}>billion dollar brand</BracketLabel>
      </Center>
    </ZoomIn>
  );
};

/* ---- the whole world knew it ---- */
export const World: React.FC<P> = ({ start }) => {
  const { frame } = useAt(start);
  return (
    <ZoomIn>
      <DarkBg hue="#123A6B" />
      <Center>
        <Emoji name="globe" size={520} start={1} style={{ rotate: `${frame * 0.6}deg` }} />
        <div style={{ marginTop: 30 }}>
          <BracketLabel start={4}>poori duniya jaanti thi</BracketLabel>
        </div>
      </Center>
    </ZoomIn>
  );
};

/* ---- clothes / electronics / furniture (grey card, ref 2) ---- */
export const Categories: React.FC<P> = ({ start }) => {
  const { at } = useAt(start);
  const tile = (emoji: string, label: string, t: number) => (
    <div
      style={{
        width: 400,
        padding: "30px 0 24px",
        borderRadius: 34,
        background: "#F4F4F4",
        boxShadow: "0 24px 40px rgba(0,0,0,0.18)",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 6,
      }}
    >
      <Emoji name={emoji} size={200} start={at(t)} />
      <div style={{ fontFamily: sora, fontWeight: 700, fontSize: 34, color: R.ink, letterSpacing: "-0.02em" }}>{label}</div>
    </div>
  );
  return (
    <ZoomIn>
      <GreyBg />
      <Center top={330}>
        <div style={{ fontFamily: sora, fontWeight: 600, fontSize: 52, color: "#555", letterSpacing: "-0.03em" }}>har cheez</div>
        <div style={{ fontFamily: sora, fontWeight: 800, fontSize: 110, color: R.ink, letterSpacing: "-0.05em", lineHeight: 1 }}>
          sell ho rahi thi.
        </div>
        <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "center", gap: 30, marginTop: 70, width: 840 }}>
          {tile("tshirt", "clothes", 17.64)}
          {tile("tv", "electronics", 18.32)}
          {tile("couch", "furniture", 19.3)}
          {tile("shopping-bags", "saara kuch", 20.52)}
        </div>
      </Center>
    </ZoomIn>
  );
};

/* ---- Google ranking drop (grey card) ---- */
export const Ranking: React.FC<P> = ({ start }) => {
  const { frame, at } = useAt(start);
  const q = "dresses";
  const typed = Math.round(interpolate(frame, [at(22.3), at(23.2)], [0, q.length], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }));
  const fall = prog(frame, at(24.9), 16, Easing.bezier(0.6, 0, 0.9, 0.6));
  const rank = Math.round(mix(fall, 1, 68));
  const row = (title: string, url: string, hot = false) => (
    <div
      style={{
        padding: "18px 24px",
        borderRadius: 20,
        background: hot ? "#FFF" : "rgba(255,255,255,0.55)",
        boxShadow: hot ? `0 0 0 4px ${R.redDeep}, 0 20px 30px rgba(0,0,0,0.15)` : "none",
        marginBottom: 14,
      }}
    >
      <div style={{ fontFamily: sora, fontSize: 24, color: "#777" }}>{url}</div>
      <div style={{ fontFamily: sora, fontWeight: 700, fontSize: 36, color: "#1A3FB8", letterSpacing: "-0.02em" }}>{title}</div>
    </div>
  );
  return (
    <ZoomIn>
      <GreyBg />
      <AbsoluteFill style={{ padding: "260px 80px 0" }}>
        <Img src={staticFile("logos/google.svg")} style={{ width: 360, alignSelf: "center", opacity: prog(frame, 2, 10) }} />
        <div
          style={{
            marginTop: 34,
            padding: "22px 34px",
            borderRadius: 999,
            background: "#FFF",
            boxShadow: "0 14px 30px rgba(0,0,0,0.12)",
            fontFamily: sora,
            fontSize: 40,
            color: R.ink,
          }}
        >
          {q.slice(0, typed)}
          <span style={{ color: R.redDeep, opacity: Math.floor(frame / 8) % 2 ? 0 : 1 }}>|</span>
        </div>
        <div style={{ position: "relative", marginTop: 30, height: 520, overflow: "hidden" }}>
          <div style={{ position: "absolute", left: 0, right: 0, translate: `0px ${fall * 620}px`, rotate: `${fall * 5}deg`, opacity: 1 - fall * 0.8 }}>
            {row("Billion-dollar brand — Official Store", "www.??????.com", true)}
          </div>
          <div style={{ position: "absolute", left: 0, right: 0, top: mix(prog(frame, at(25.2), 12), 140, 0) }}>
            {row("Dresses for Women | Shop", "competitor-one.com")}
            {row("New Arrivals: Dresses", "competitor-two.com")}
            {row("Summer Dresses Sale", "competitor-three.com")}
          </div>
        </div>
        <div style={{ position: "absolute", left: 0, right: 0, top: 1180, display: "flex", alignItems: "center", justifyContent: "center", gap: 20 }}>
          <Emoji name="chart-down" size={150} start={at(24.9)} />
          <div style={{ fontFamily: sora, fontWeight: 600, fontSize: 44, color: "#555", letterSpacing: "-0.03em" }}>google rank</div>
          <div style={{ fontFamily: bebas, fontSize: 210, lineHeight: 1, color: fall > 0.05 ? R.redDeep : R.ink }}>#{rank}</div>
        </div>
      </AbsoluteFill>
    </ZoomIn>
  );
};

/* ---- website / content / products on stacked retro TVs ---- */
export const TvCheck: React.FC<P> = ({ start }) => {
  const { at } = useAt(start);
  const label = (text: string, t: number, top: number) => (
    <div style={{ position: "absolute", right: 70, top, textAlign: "right" }}>
      <div style={{ fontFamily: sora, fontWeight: 800, fontSize: 70, color: R.ink, letterSpacing: "-0.04em", opacity: prog(useCurrentFrame(), at(t), 8) }}>
        {text}
      </div>
      <RedTag start={at(t) + 4} style={{ fontSize: 34 }}>
        ✓ tha
      </RedTag>
    </div>
  );
  return (
    <ZoomIn>
      <GreyBg />
      <TvStack
        screens={[
          { emoji: "shopping-bags" },
          { video: "broll/laptop-typing.mp4", trim: 1 },
          { video: "broll/online-shopping.mp4", trim: 1 },
        ]}
        starts={[at(28.88) - 4, at(27.72) - 4, at(26.75) - 2]}
      />
      {label("website", 26.75, 380)}
      {label("content", 27.72, 740)}
      {label("products", 28.88, 1120)}
    </ZoomIn>
  );
};

/* ---- GONE. ---- */
export const GoneTitle: React.FC<P> = () => {
  const frame = useCurrentFrame();
  const jitter = frame < 8 ? (random(`gj${frame}`) - 0.5) * 50 : 0;
  return (
    <ZoomIn flash={R.red}>
      <DarkBg />
      <Center>
        <NeonText size={360} start={0} style={{ translate: `${jitter}px 0px` }}>
          GONE.
        </NeonText>
        <div style={{ marginTop: 10 }}>
          <Emoji name="skull" size={200} start={3} />
        </div>
      </Center>
    </ZoomIn>
  );
};

/* ---- Kyun? emoji over the speaker ---- */
export const KyunPop: React.FC<P> = ({ start }) => {
  const { at } = useAt(start);
  return (
    <AbsoluteFill>
      <Emoji name="thinking" size={260} start={at(36.15)} style={{ position: "absolute", left: 770, top: 250 }} />
    </AbsoluteFill>
  );
};

/* ---- CCTV: SEO cheating ---- */
export const Cctv: React.FC<P> = () => {
  const frame = useCurrentFrame();
  return (
    <ZoomIn>
      <Footage src="broll/cctv-thieves.mp4" trim={3} />
      <Center>
        <Brackets width={900} height={1200} start={2} />
      </Center>
      <div style={{ position: "absolute", left: 110, top: 300, display: "flex", alignItems: "center", gap: 14 }}>
        <div style={{ width: 26, height: 26, borderRadius: 99, background: R.red, opacity: Math.floor(frame / 10) % 2 ? 0.2 : 1, boxShadow: glow(R.red, 0.6) }} />
        <div style={{ fontFamily: sora, fontWeight: 700, fontSize: 40, color: R.white }}>REC</div>
      </div>
    </ZoomIn>
  );
};

/* ---- paid links network + CHEATING stamp ---- */
export const PaidLinks: React.FC<P> = ({ start }) => {
  const { frame, at } = useAt(start);
  const net = prog(frame, 0, 20, Easing.inOut(Easing.cubic));
  const stamp = pop(frame, at(40.66), 10);
  const cx = 540;
  const cy = 820;
  return (
    <ZoomIn>
      <DarkBg />
      <svg width={1080} height={1920} style={{ position: "absolute" }}>
        {new Array(10).fill(0).map((_, i) => {
          const a = (i / 10) * Math.PI * 2;
          const r = 330 + random(`pr${i}`) * 60;
          const x = cx + Math.cos(a) * r * net;
          const y = cy + Math.sin(a) * r * net;
          return <line key={i} x1={cx} y1={cy} x2={x} y2={y} stroke={R.red} strokeWidth={4} strokeDasharray="14 10" opacity={0.8} />;
        })}
      </svg>
      {new Array(10).fill(0).map((_, i) => {
        const a = (i / 10) * Math.PI * 2;
        const r = 330 + random(`pr${i}`) * 60;
        return (
          <Img
            key={i}
            src={staticFile(`emoji/${i % 2 ? "link" : "dollar"}.webp`)}
            style={{ position: "absolute", left: cx + Math.cos(a) * r * net - 55, top: cy + Math.sin(a) * r * net - 55, width: 110, opacity: net }}
          />
        );
      })}
      <div
        style={{
          position: "absolute",
          left: cx - 120,
          top: cy - 120,
          width: 240,
          height: 240,
          borderRadius: 999,
          background: R.redDeep,
          boxShadow: glow(R.red, 1),
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontFamily: bebas,
          fontSize: 70,
          color: R.white,
        }}
      >
        ??.COM
      </div>
      <Center top={290}>
        <NeonText size={170} color={R.white} filled start={2}>
          PAID LINKS
        </NeonText>
      </Center>
      <div
        style={{
          position: "absolute",
          left: 140,
          top: 1180,
          padding: "10px 40px",
          border: `10px solid ${R.red}`,
          borderRadius: 16,
          fontFamily: bebas,
          fontSize: 170,
          lineHeight: 1,
          color: R.red,
          rotate: "-8deg",
          scale: String(mix(stamp, 2.3, 1)),
          opacity: Math.min(1, stamp * 2),
          textShadow: glow(R.red, 0.6),
          boxShadow: glow(R.red, 0.5),
        }}
      >
        CHEATING
      </div>
    </ZoomIn>
  );
};

/* ---- algorithm: warning -> cross over the speaker ---- */
export const AlgoPop: React.FC<P> = ({ start }) => {
  const { frame, at } = useAt(start);
  const swap = frame >= at(45.62);
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", left: 740, top: 250 }}>
        {swap ? <Emoji name="cross" size={260} start={at(45.62)} /> : <Emoji name="warning" size={260} start={at(44.56)} />}
      </div>
      <div style={{ position: "absolute", left: 90, top: 300 }}>
        <RedTag start={at(44.56)}>google guidelines</RedTag>
      </div>
    </AbsoluteFill>
  );
};

/* ---- CAUGHT ---- */
export const Caught: React.FC<P> = ({ start }) => {
  const { frame, at } = useAt(start);
  const s = pop(frame, at(48.4), 10);
  const strobe = Math.floor(frame / 4) % 2 ? "rgba(255,30,30,0.25)" : "rgba(30,60,255,0.18)";
  return (
    <ZoomIn>
      <Footage src="broll/police-tape.mp4" trim={1} />
      <AbsoluteFill style={{ background: strobe, mixBlendMode: "screen" }} />
      <Center>
        <Emoji name="police-light" size={340} start={2} />
        <div style={{ scale: String(mix(s, 2, 1)), opacity: Math.min(1, s * 2) }}>
          <NeonText size={260} filled color={R.white} start={at(48.4)} style={{ textShadow: glow(R.red, 1.2) }}>
            CAUGHT
          </NeonText>
        </div>
        <BracketLabel start={at(48.4) + 4}>google penalty</BracketLabel>
      </Center>
    </ZoomIn>
  );
};

/* ---- JCPenney reveal (grey card, ref 2 kinetic type) ---- */
export const Reveal: React.FC<P> = ({ start }) => {
  const { frame, at } = useAt(start);
  const name = prog(frame, at(50.86), 12);
  return (
    <ZoomIn>
      <GreyBg />
      <Center>
        <Emoji name="department-store" size={300} start={4} />
        <div style={{ fontFamily: sora, fontWeight: 600, fontSize: 56, color: "#555", letterSpacing: "-0.03em", marginTop: 20 }}>
          woh company thi
        </div>
        <div
          style={{
            fontFamily: sora,
            fontWeight: 800,
            fontSize: 150,
            color: R.ink,
            letterSpacing: "-0.06em",
            lineHeight: 1,
            opacity: name,
            scale: String(mix(name, 1.4, 1)),
            filter: `blur(${(1 - name) * 10}px)`,
          }}
        >
          JCPenney.
        </div>
        <div style={{ marginTop: 26 }}>
          <RedTag start={at(53.06)}>american retail giant</RedTag>
        </div>
      </Center>
    </ZoomIn>
  );
};

/* ---- biggest lesson: library footage + stacked type ---- */
export const Lesson: React.FC<P> = ({ start }) => {
  const { frame, at } = useAt(start);
  const line = (text: React.ReactNode, t: number, style: React.CSSProperties) => {
    const p = prog(frame, at(t), 10);
    return <div style={{ opacity: p, scale: String(mix(p, 1.3, 1)), filter: `blur(${(1 - p) * 8}px)`, ...style }}>{text}</div>;
  };
  return (
    <ZoomIn>
      <Footage src="broll/library.mp4" trim={0.5} tint="rgba(120,40,30,0.5)" />
      <Center>
        <Emoji name="books" size={240} start={at(55.3)} />
        {line("aaj bhi ye story", 55.84, { fontFamily: sora, fontWeight: 600, fontSize: 56, color: R.white })}
        {line("is industry ka", 57.36, { fontFamily: sora, fontWeight: 600, fontSize: 56, color: R.white })}
        {line("sabse bada", 58.52, { fontFamily: sora, fontWeight: 800, fontSize: 120, color: R.white, letterSpacing: "-0.05em", lineHeight: 1 })}
        {line(
          <span style={{ color: R.green, textShadow: glow("rgba(61,255,143,0.6)", 0.8) }}>lesson.</span>,
          59.24,
          { fontFamily: sora, fontWeight: 800, fontSize: 150, letterSpacing: "-0.05em", lineHeight: 1 },
        )}
      </Center>
    </ZoomIn>
  );
};

/* ---- Types of SEO (neon) ---- */
export const TypesOfSeo: React.FC<P> = ({ start }) => {
  const { frame, at } = useAt(start);
  const row = (emoji: string, text: string, t: number, good: boolean) => {
    const p = prog(frame, at(t), 10);
    return (
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 22,
          padding: "14px 30px 14px 18px",
          borderRadius: 24,
          background: good ? "rgba(61,255,143,0.1)" : "rgba(255,45,45,0.1)",
          border: `2px solid ${good ? "rgba(61,255,143,0.45)" : "rgba(255,45,45,0.45)"}`,
          opacity: p,
          translate: `${mix(p, 80, 0)}px 0px`,
        }}
      >
        <Emoji name={emoji} size={90} start={at(t)} float={false} />
        <div
          style={{
            fontFamily: sora,
            fontWeight: 700,
            fontSize: 50,
            color: good ? R.white : "rgba(255,255,255,0.6)",
            letterSpacing: "-0.03em",
            textDecoration: good ? "none" : "line-through",
            textDecorationColor: R.red,
            textDecorationThickness: 6,
          }}
        >
          {text}
        </div>
      </div>
    );
  };
  return (
    <ZoomIn flash={R.red}>
      <DarkBg />
      <Center top={260}>
        <div style={{ position: "relative", display: "flex", justifyContent: "center", alignItems: "center", width: 900, height: 330 }}>
          <Brackets width={880} height={320} start={4} />
          <NeonText size={190} start={2}>
            TYPES OF SEO
          </NeonText>
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 20, marginTop: 50, width: 860 }}>
          {row("check", "real story", 69.4, true)}
          {row("check", "real example", 70.42, true)}
          {row("cross", "complex sentences", 72.06, false)}
          {row("cross", "definitions", 73.88, false)}
          {row("cross", "ratta maaro theory", 75.04, false)}
        </div>
      </Center>
    </ZoomIn>
  );
};

/* ---- ending CTA over the speaker ---- */
export const EndCta: React.FC<P> = ({ start }) => {
  const { frame, at } = useAt(start);
  const { durationInFrames } = useVideoConfig();
  const p = prog(frame, at(77.0), 10);
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", left: 0, right: 0, top: 330, display: "flex", justifyContent: "center" }}>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 16,
            padding: "16px 34px",
            borderRadius: 999,
            background: R.redDeep,
            boxShadow: glow("rgba(255,45,45,0.6)", 0.8),
            fontFamily: sora,
            fontWeight: 800,
            fontSize: 48,
            color: R.white,
            letterSpacing: "-0.02em",
            opacity: p,
            scale: String(mix(p, 0.6, 1)),
          }}
        >
          follow for part 2
          <Img src={staticFile("emoji/point-right.webp")} style={{ width: 70 }} />
        </div>
      </div>
      <AbsoluteFill
        style={{
          background: "#000",
          opacity: interpolate(frame, [durationInFrames - 10, durationInFrames], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
        }}
      />
    </AbsoluteFill>
  );
};
