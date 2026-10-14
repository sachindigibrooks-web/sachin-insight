import React from 'react';
import {AbsoluteFill, continueRender, delayRender, Easing, Img, random, spring, staticFile, useCurrentFrame} from 'remotion';
import tl from './timeline.json';

/* Palette chosen for the psychology of the topic:
   indigo = introspection/depth, violet = spirituality, saffron-gold = illumination/hope (Indian spiritual cue),
   ivory = clarity, teal = calm, coral = restlessness (used only for overthinking). */
export const C = {
	indigo: '#0d1130',
	indigo2: '#161b45',
	violet: '#2b1f4f',
	gold: '#e9b44c',
	goldSoft: '#f5d48a',
	ivory: '#f4ebdd',
	teal: '#5fb3b3',
	coral: '#e4572e',
};

const FONTS: [string, string, string, string][] = [
	['Serif', 'CormorantGaramond-700-normal', '700', 'normal'],
	['Serif', 'CormorantGaramond-500-normal', '500', 'normal'],
	['Serif', 'CormorantGaramond-500-italic', '500', 'italic'],
	['Caps', 'Cinzel-600-normal', '600', 'normal'],
	['Sans', 'Inter-900-latin', '400 900', 'normal'],
	['Deva', 'Hind-700-devanagari', '700', 'normal'],
];
if (typeof document !== 'undefined') {
	const h = delayRender('fonts');
	Promise.all(FONTS.map(([fam, file, weight, style]) => {
		const f = new FontFace(fam, `url(${staticFile(`fonts/${file}.woff2`)})`, {weight, style});
		document.fonts.add(f);
		return f.load();
	})).then(() => continueRender(h));
}

export const FPS = 30;
export const TL = tl;
export const B = tl.beats as Record<string, number>;
export const useT = () => useCurrentFrame() / FPS;
export const clamp01 = (x: number) => Math.max(0, Math.min(1, x));
export const ease = (t: number, a: number, d: number, fn = Easing.out(Easing.cubic)) => fn(clamp01((t - a) / d));
export const lerp = (a: number, b: number, p: number) => a + (b - a) * p;
export const soft = (t: number, a: number) => (t < a ? 0 : spring({frame: (t - a) * FPS, fps: FPS, config: {damping: 20, stiffness: 90, mass: 0.8}}));

/** Calm word reveal: fades up from a soft blur on its spoken beat. */
export const W: React.FC<{at: number; children: React.ReactNode; gold?: boolean; style?: React.CSSProperties}> = ({at, children, gold, style}) => {
	const t = useT();
	const p = ease(t, at - 0.05, 0.55);
	return (
		<span style={{display: 'inline-block', opacity: p, transform: `translateY(${(1 - p) * 26}px)`, filter: `blur(${(1 - p) * 8}px)`,
			color: gold ? C.gold : undefined, textShadow: gold ? `0 0 ${28 * p}px rgba(233,180,76,.55)` : undefined, ...style}}>
			{children}
		</span>
	);
};

export const Line: React.FC<{items: [string, number, boolean?][]; size?: number; font?: string; style?: React.CSSProperties; color?: string}> = ({
	items, size = 110, font = 'Serif', style, color = C.ivory,
}) => (
	<div style={{display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: `0 ${size * 0.26}px`, fontFamily: font, fontWeight: 700,
		fontSize: size, lineHeight: 1.05, color, textShadow: '0 6px 30px rgba(0,0,0,.55)', ...style}}>
		{items.map(([w, a, g], i) => <W key={i} at={a} gold={g}>{w}</W>)}
	</div>
);

export const Label: React.FC<{at: number; children: React.ReactNode; style?: React.CSSProperties; color?: string; out?: number}> = ({at, children, style, color = C.gold, out}) => {
	const t = useT();
	const p = ease(t, at, 0.6) * (out !== undefined ? 1 - ease(t, out, 0.35) : 1);
	return (
		<div style={{fontFamily: 'Caps', fontWeight: 600, fontSize: 40, letterSpacing: `${0.32 + (1 - p) * 0.4}em`, color, opacity: p, textAlign: 'center',
			textShadow: '0 2px 18px rgba(0,0,0,.6)', ...style}}>{children}</div>
	);
};

/** Graded photo with slow Ken Burns; tone pulls it into the indigo/gold palette. */
export const Photo: React.FC<{src: string; s: number; e: number; from?: number; to?: number; x?: number; y?: number; tone?: 'indigo' | 'warm' | 'sepia' | 'teal'; dim?: number; style?: React.CSSProperties}> = ({
	src, s, e, from = 1.12, to = 1.0, x = 0, y = 0, tone = 'indigo', dim = 0.35, style,
}) => {
	const t = useT();
	const k = clamp01((t - s) / Math.max(0.1, e - s));
	const filt = {indigo: 'saturate(.65) contrast(1.08) brightness(.9)', warm: 'saturate(.8) contrast(1.05) sepia(.15)', sepia: 'grayscale(1) sepia(.55) contrast(1.15)', teal: 'saturate(.7) hue-rotate(-8deg) contrast(1.05)'}[tone];
	const over = {indigo: 'linear-gradient(180deg, rgba(13,17,48,.35), rgba(43,31,79,.55))', warm: 'linear-gradient(180deg, rgba(233,180,76,.12), rgba(13,17,48,.5))', sepia: 'linear-gradient(180deg, rgba(233,180,76,.15), rgba(13,17,48,.45))', teal: 'linear-gradient(180deg, rgba(95,179,179,.15), rgba(13,17,48,.55))'}[tone];
	return (
		<AbsoluteFill style={{overflow: 'hidden', ...style}}>
			<Img src={staticFile(src)} style={{width: '100%', height: '100%', objectFit: 'cover', filter: filt,
				transform: `scale(${lerp(from, to, Easing.inOut(Easing.quad)(k))}) translate(${x * k}px, ${y * k}px)`}} />
			<AbsoluteFill style={{background: over, mixBlendMode: 'multiply'}} />
			<AbsoluteFill style={{background: `rgba(13,17,48,${dim})`}} />
		</AbsoluteFill>
	);
};

/** Slowly drifting nebula of indigo/violet light: the "inner space" backdrop. */
export const Nebula: React.FC = () => {
	const t = useT();
	const blob = (cx: number, cy: number, r: number, col: string, sp: number, ph: number) =>
		`radial-gradient(circle at ${cx + Math.sin(t * sp + ph) * 8}% ${cy + Math.cos(t * sp * 0.8 + ph) * 6}%, ${col} 0%, rgba(0,0,0,0) ${r}%)`;
	return (
		<AbsoluteFill style={{background: [blob(30, 30, 45, 'rgba(70,52,140,.55)', 0.12, 0), blob(75, 65, 50, 'rgba(36,60,140,.5)', 0.09, 2),
			blob(50, 90, 40, 'rgba(233,180,76,.12)', 0.07, 4), `linear-gradient(180deg, ${C.indigo} 0%, ${C.indigo2} 55%, ${C.violet} 100%)`].join(',')}} />
	);
};

/** Gold dust: deterministic particles rising and twinkling (consciousness motif). */
export const Dust: React.FC<{n?: number; opacity?: number}> = ({n = 70, opacity = 0.8}) => {
	const t = useT();
	return (
		<AbsoluteFill style={{pointerEvents: 'none'}}>
			{Array.from({length: n}, (_, i) => {
				const sp = 18 + random(`s${i}`) * 40;
				const x = random(`x${i}`) * 1080 + Math.sin(t * 0.6 + i) * 18;
				const y = (random(`y${i}`) * 2100 - t * sp) % 2100;
				const yy = y < -60 ? y + 2100 : y;
				const sz = 2 + random(`z${i}`) * 5;
				const tw = 0.35 + 0.65 * Math.abs(Math.sin(t * (0.8 + random(`w${i}`) * 2) + i));
				return <div key={i} style={{position: 'absolute', left: x, top: yy, width: sz, height: sz, borderRadius: '50%', background: C.goldSoft,
					opacity: tw * opacity, boxShadow: `0 0 ${sz * 3}px ${C.gold}`}} />;
			})}
		</AbsoluteFill>
	);
};

/** Soft gold light leak that blooms across a cut. */
export const Leak: React.FC<{at: number; dur?: number; x?: number; y?: number}> = ({at, dur = 1.0, x = 50, y = 40}) => {
	const t = useT();
	if (t < at - 0.2 || t > at + dur) return null;
	const p = Math.sin(Math.PI * clamp01((t - at + 0.2) / (dur + 0.2)));
	return <AbsoluteFill style={{background: `radial-gradient(ellipse at ${x}% ${y}%, rgba(245,212,138,${0.55 * p}) 0%, rgba(233,180,76,${0.25 * p}) 30%, rgba(0,0,0,0) 65%)`, mixBlendMode: 'screen'}} />;
};

export const Ring: React.FC<{cx: number; cy: number; at: number; dur?: number; max?: number; color?: string; width?: number}> = ({cx, cy, at, dur = 1.6, max = 420, color = C.gold, width = 3}) => {
	const t = useT();
	if (t < at || t > at + dur) return null;
	const p = ease(t, at, dur, Easing.out(Easing.quad));
	return <div style={{position: 'absolute', left: cx - max * p, top: cy - max * p, width: max * 2 * p, height: max * 2 * p, borderRadius: '50%',
		border: `${width}px solid ${color}`, opacity: (1 - p) * 0.9}} />;
};

/** Gold line-art eye that opens (the witness). */
export const Eye: React.FC<{at: number; cx: number; cy: number; w?: number}> = ({at, cx, cy, w = 520}) => {
	const t = useT();
	const draw = ease(t, at, 0.9, Easing.inOut(Easing.cubic));
	const open = ease(t, at + 0.5, 0.6);
	const h = w * 0.42;
	return (
		<svg width={w} height={h * 2} viewBox={`0 0 ${w} ${h * 2}`} style={{position: 'absolute', left: cx - w / 2, top: cy - h, overflow: 'visible',
			filter: `drop-shadow(0 0 ${18 * open}px rgba(233,180,76,.8))`}}>
			<path d={`M10 ${h} Q ${w / 2} ${h - h * 0.95 * (0.15 + 0.85 * open)} ${w - 10} ${h} Q ${w / 2} ${h + h * 0.95 * (0.15 + 0.85 * open)} 10 ${h} Z`}
				fill="none" stroke={C.gold} strokeWidth={5} pathLength={1} strokeDasharray="1 1" strokeDashoffset={1 - draw} />
			<circle cx={w / 2} cy={h} r={h * 0.42 * open} fill="none" stroke={C.gold} strokeWidth={5} />
			<circle cx={w / 2} cy={h} r={h * 0.17 * open} fill={C.gold} />
			<circle cx={w / 2 + h * 0.08} cy={h - h * 0.08} r={h * 0.05 * open} fill={C.ivory} />
		</svg>
	);
};

/** Thought pill (overthinking chatter). */
export const Thought: React.FC<{text: string; x: number; y: number; o: number; scale?: number; color?: string}> = ({text, x, y, o, scale = 1, color = C.coral}) => (
	<div style={{position: 'absolute', left: x, top: y, transform: `translate(-50%,-50%) scale(${scale})`, opacity: o, whiteSpace: 'nowrap',
		fontFamily: 'Sans', fontWeight: 700, fontSize: 36, color: C.ivory, padding: '12px 26px', borderRadius: 40,
		background: 'rgba(13,17,48,.55)', border: `2px solid ${color}`, boxShadow: `0 0 24px ${color}55`, backdropFilter: 'blur(4px)'}}>{text}</div>
);
