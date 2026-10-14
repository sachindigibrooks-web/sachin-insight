import React from 'react';
import {AbsoluteFill, Easing, Img, random, spring, staticFile, useCurrentFrame} from 'remotion';
import {continueRender, delayRender} from 'remotion';
import tl from './timeline.json';

// Fonts are bundled locally (public/fonts) so rendering does not depend on Google Fonts at render time.
const FONTS: [string, string, string][] = [
	['ArchivoBlack', 'ArchivoBlack-400-latin', '400'],
	['InterLocal', 'Inter-900-latin', '600 900'],
	['SpecialElite', 'SpecialElite-400-latin', '400'],
	['PermanentMarker', 'PermanentMarker-400-latin', '400'],
	['HindLocal', 'Hind-700-devanagari', '700'],
	['HindLocal', 'Hind-700-latin', '700'],
];
if (typeof document !== 'undefined') {
	const handle = delayRender('fonts');
	Promise.all(
		FONTS.map(([fam, file, weight]) => {
			const f = new FontFace(fam, `url(${staticFile(`fonts/${file}.woff2`)})`, {weight});
			document.fonts.add(f);
			return f.load();
		}),
	).then(() => continueRender(handle));
}
export const HEAVY = 'ArchivoBlack';
export const SANS = 'InterLocal';
export const TYPE = 'SpecialElite';
export const MARKER = 'PermanentMarker';
export const DEVA = 'HindLocal';

export const FPS = 30;
export const TL = tl;
export const B = tl.beats as Record<string, number>;
export const useT = () => useCurrentFrame() / FPS;

export const clamp01 = (x: number) => Math.max(0, Math.min(1, x));
export const ease = (t: number, a: number, d: number, fn = Easing.out(Easing.cubic)) => fn(clamp01((t - a) / d));
export const pop = (t: number, a: number, stiff = 230, damping = 11) =>
	t < a ? 0 : spring({frame: (t - a) * FPS, fps: FPS, config: {damping, stiffness: stiff, mass: 0.6}});
export const lerp = (a: number, b: number, p: number) => a + (b - a) * p;

export const extrude = (depth: number, color: string, soft = 0.55) => {
	const s: string[] = [];
	for (let i = 1; i <= depth; i++) s.push(`${(i * 0.55).toFixed(1)}px ${i}px 0 ${color}`);
	s.push(`${depth * 0.55 + 8}px ${depth + 14}px 26px rgba(0,0,0,${soft})`);
	return s.join(',');
};

export const COLORS = {
	white: ['#ffffff', '#9b9b9b'],
	red: ['#ff2a2a', '#7a0b0b'],
	green: ['#3ee05a', '#126b22'],
	yellow: ['#ffd21f', '#8a6500'],
	black: ['#1b1b1b', '#a9a9a9'],
	blue: ['#2f7bff', '#0d2f73'],
} as const;
export type Col = keyof typeof COLORS;

/** Heavy 3D-extruded word that slams in at `at` seconds. */
export const Word: React.FC<{
	at: number; text: string; size?: number; color?: Col; rot?: number; style?: React.CSSProperties; depth?: number; out?: number;
}> = ({at, text, size = 150, color = 'white', rot = 0, style, depth, out}) => {
	const t = useT();
	const p = pop(t, at);
	if (t < at) return <span style={{display: 'inline-block', opacity: 0, fontSize: size, ...style}}>{text}</span>;
	const o = out !== undefined ? 1 - ease(t, out, 0.18) : 1;
	const [fill, side] = COLORS[color];
	return (
		<span
			style={{
				display: 'inline-block',
				fontFamily: HEAVY,
				fontSize: size,
				lineHeight: 0.98,
				color: fill,
				letterSpacing: -size * 0.025,
				textTransform: 'uppercase',
				textShadow: extrude(depth ?? Math.round(size / 14), side),
				transform: `scale(${lerp(1.7, 1, p)}) rotate(${rot + (1 - p) * 6}deg)`,
				opacity: clamp01(p * 3) * o,
				filter: `blur(${(1 - clamp01(p)) * 10}px)`,
				...style,
			}}
		>
			{text}
		</span>
	);
};

/** A line of words, each appearing on its own spoken beat. */
export const KLine: React.FC<{items: [string, number][]; size?: number; color?: Col; gap?: number; style?: React.CSSProperties; colors?: Col[]}> = ({
	items, size = 140, color = 'white', gap = 0.22, style, colors,
}) => (
	<div style={{display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: `0 ${size * gap}px`, ...style}}>
		{items.map(([w, a], i) => (
			<Word key={i} at={a} text={w} size={size} color={colors?.[i] ?? color} />
		))}
	</div>
);

/** Rubber stamp that thuds down. */
export const Stamp: React.FC<{at: number; text: string; color?: string; rot?: number; size?: number; style?: React.CSSProperties}> = ({
	at, text, color = '#e3262b', rot = -12, size = 92, style,
}) => {
	const t = useT();
	if (t < at) return null;
	const p = pop(t, at, 420, 16);
	return (
		<div
			style={{
				position: 'absolute', fontFamily: HEAVY, fontSize: size, color, border: `${size * 0.09}px solid ${color}`,
				padding: `${size * 0.08}px ${size * 0.28}px`, borderRadius: size * 0.14, textTransform: 'uppercase', letterSpacing: 2,
				transform: `rotate(${rot}deg) scale(${lerp(2.6, 1, p)})`, opacity: clamp01(p * 2.5) * 0.92, filter: 'url(#rough)',
				whiteSpace: 'nowrap', background: 'rgba(255,255,255,0.04)', ...style,
			}}
		>
			{text}
		</div>
	);
};

/** Torn-edge paper card. */
export const Paper: React.FC<{w: number; h: number; seed: string; style?: React.CSSProperties; tex?: string; children?: React.ReactNode}> = ({
	w, h, seed, style, tex = 'paper', children,
}) => {
	const pts: string[] = [];
	const n = 28;
	const j = (i: number, k: string) => (random(`${seed}${k}${i}`) - 0.5) * 1.4;
	for (let i = 0; i <= n; i++) pts.push(`${(i / n) * 100}% ${0.8 + j(i, 't')}%`);
	for (let i = 0; i <= n; i++) pts.push(`${99.2 + j(i, 'r') * 0.5}% ${(i / n) * 100}%`);
	for (let i = n; i >= 0; i--) pts.push(`${(i / n) * 100}% ${99.2 + j(i, 'b') * 0.5}%`);
	for (let i = n; i >= 0; i--) pts.push(`${0.8 + j(i, 'l') * 0.5}% ${(i / n) * 100}%`);
	return (
		<div style={{position: 'absolute', width: w, height: h, filter: 'drop-shadow(10px 18px 22px rgba(0,0,0,0.5))', ...style}}>
			<div
				style={{
					position: 'absolute', inset: 0, clipPath: `polygon(${pts.join(',')})`,
					backgroundImage: `url(${staticFile(`tex/${tex}.png`)})`, backgroundSize: 'cover',
				}}
			/>
			<div style={{position: 'absolute', inset: 0}}>{children}</div>
		</div>
	);
};

/** Hand-drawn marker stroke that draws itself on. */
export const MarkerPath: React.FC<{d: string; at: number; dur?: number; color?: string; width?: number; w: number; h: number; style?: React.CSSProperties}> = ({
	d, at, dur = 0.35, color = '#e3262b', width = 14, w, h, style,
}) => {
	const t = useT();
	const p = ease(t, at, dur, Easing.inOut(Easing.quad));
	return (
		<svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} style={{position: 'absolute', overflow: 'visible', ...style}}>
			<path d={d} pathLength={1} fill="none" stroke={color} strokeWidth={width} strokeLinecap="round" strokeLinejoin="round"
				strokeDasharray="1 1" strokeDashoffset={1 - p} style={{filter: 'url(#rough)'}} />
		</svg>
	);
};

export const Bg: React.FC<{tex: string; s: number; e: number; push?: number}> = ({tex, s, e, push = 0.07}) => {
	const t = useT();
	const k = clamp01((t - s) / Math.max(0.1, e - s));
	return (
		<AbsoluteFill style={{overflow: 'hidden'}}>
			<Img src={staticFile(`tex/${tex}.png`)} style={{width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${1 + push - push * k})`}} />
		</AbsoluteFill>
	);
};

export const Phone: React.FC<{w?: number; h?: number; style?: React.CSSProperties; children?: React.ReactNode; screenBg?: string}> = ({
	w = 620, h = 1180, style, children, screenBg = '#fff',
}) => (
	<div style={{position: 'absolute', width: w, height: h, borderRadius: 86, background: 'linear-gradient(145deg,#2b2b2e,#0c0c0d)',
		boxShadow: '24px 40px 60px rgba(0,0,0,0.6), inset 0 0 0 3px #45454a', ...style}}>
		<div style={{position: 'absolute', inset: 22, borderRadius: 66, background: screenBg, overflow: 'hidden'}}>
			{children}
			<div style={{position: 'absolute', top: 18, left: '50%', width: 150, height: 42, marginLeft: -75, borderRadius: 30, background: '#0c0c0d'}} />
		</div>
	</div>
);

export const Cursor: React.FC<{x: number; y: number; press?: number; style?: React.CSSProperties}> = ({x, y, press = 0, style}) => (
	<svg width={90} height={110} viewBox="0 0 24 30" style={{position: 'absolute', left: x, top: y, transform: `scale(${1 - press * 0.18})`,
		transformOrigin: '10% 10%', filter: 'drop-shadow(4px 8px 6px rgba(0,0,0,.45))', ...style}}>
		<path d="M2 1 L2 24 L8 18.5 L12 28 L16 26.3 L12 17 L20 17 Z" fill="#fff" stroke="#111" strokeWidth="1.6" strokeLinejoin="round" />
	</svg>
);

export const Ripple: React.FC<{x: number; y: number; at: number; color?: string}> = ({x, y, at, color = '#2f7bff'}) => {
	const t = useT();
	if (t < at || t > at + 0.6) return null;
	const p = ease(t, at, 0.55);
	return <div style={{position: 'absolute', left: x - 90, top: y - 90, width: 180, height: 180, borderRadius: '50%',
		border: `8px solid ${color}`, transform: `scale(${0.2 + p})`, opacity: 1 - p}} />;
};

export const Pencil: React.FC<{style?: React.CSSProperties}> = ({style}) => (
	<svg width={560} height={60} viewBox="0 0 560 60" style={{position: 'absolute', filter: 'drop-shadow(10px 14px 10px rgba(0,0,0,.5))', ...style}}>
		<rect x="70" y="8" width="420" height="44" fill="#f2b705" />
		<rect x="70" y="8" width="420" height="14" fill="#ffd34d" />
		<rect x="70" y="38" width="420" height="14" fill="#c98f00" />
		<rect x="490" y="6" width="34" height="48" fill="#b9b9c0" />
		<rect x="524" y="6" width="34" height="48" rx="8" fill="#ef7f9a" />
		<polygon points="70,8 70,52 8,30" fill="#e8c39e" />
		<polygon points="26,24 26,36 8,30" fill="#2a2a2a" />
	</svg>
);

export const Crumple: React.FC<{seed: string; size?: number; style?: React.CSSProperties}> = ({seed, size = 170, style}) => {
	const pts = Array.from({length: 14}, (_, i) => {
		const a = (i / 14) * Math.PI * 2;
		const r = 0.38 + random(seed + i) * 0.12;
		return `${50 + Math.cos(a) * r * 100}% ${50 + Math.sin(a) * r * 100}%`;
	});
	return (
		<div style={{position: 'absolute', width: size, height: size, filter: 'drop-shadow(8px 14px 10px rgba(0,0,0,.45))', ...style}}>
			<div style={{position: 'absolute', inset: 0, clipPath: `polygon(${pts.join(',')})`,
				background: 'radial-gradient(circle at 35% 30%, #ffffff, #d9d6cf 45%, #a7a39a 80%)'}} />
		</div>
	);
};

export const Clip: React.FC<{style?: React.CSSProperties}> = ({style}) => (
	<svg width={60} height={150} viewBox="0 0 60 150" style={{position: 'absolute', filter: 'drop-shadow(4px 6px 4px rgba(0,0,0,.4))', ...style}}>
		<path d="M18 40 V120 a12 12 0 0 0 24 0 V25 a18 18 0 0 0 -36 0 V115" fill="none" stroke="#c9ced6" strokeWidth="7" strokeLinecap="round" />
	</svg>
);

/** Small label tag like "01" episode chapter markers. */
export const NumTag: React.FC<{n: string; at: number; color?: string; style?: React.CSSProperties}> = ({n, at, color = '#ffd21f', style}) => {
	const t = useT();
	const p = pop(t, at, 260, 12);
	return (
		<div style={{position: 'absolute', fontFamily: HEAVY, fontSize: 210, color: 'transparent', WebkitTextStroke: `7px ${color}`,
			transform: `translateX(${(1 - p) * -500}px) rotate(-6deg)`, opacity: clamp01(p * 2), textShadow: '10px 16px 0 rgba(0,0,0,.35)', ...style}}>
			{n}
		</div>
	);
};
