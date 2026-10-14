import React from 'react';
import {AbsoluteFill, continueRender, delayRender, Easing, Img, OffthreadVideo, random, Sequence, spring, staticFile, useCurrentFrame} from 'remotion';
import tl from './timeline.json';

/* Editorial-documentary look. Colour: warm cinematic grade (teal shadows / amber highlights);
   saffron-gold accent = illumination & hope, ivory text = clarity, coral only for overthinking. */
export const C = {
	ink: '#0b0d14',
	gold: '#f2b84b',
	ivory: '#f6efe3',
	coral: '#ff5a3c',
	marker: '#ffd84a',
	teal: '#2a5d63',
};

const FONTS: [string, string, string, string][] = [
	['Display', 'Anton-400-latin', '400', 'normal'],
	['Serif', 'CormorantGaramond-700-normal', '700', 'normal'],
	['Serif', 'CormorantGaramond-500-italic', '500', 'italic'],
	['Hand', 'Kalam-700-latin', '700', 'normal'],
	['Hand', 'Kalam-700-devanagari', '700', 'normal'],
	['Sans', 'Inter-900-latin', '400 900', 'normal'],
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
export const spr = (t: number, a: number, stiff = 170, damp = 14) =>
	t < a ? 0 : spring({frame: (t - a) * FPS, fps: FPS, config: {damping: damp, stiffness: stiff, mass: 0.7}});
/** Anticipation: dip slightly below 0 before shooting past 1 and settling (classic animation principle). */
export const antic = (t: number, a: number) => {
	if (t < a - 0.12) return 0;
	if (t < a) return -0.06 * Math.sin(((t - (a - 0.12)) / 0.12) * Math.PI);
	return spr(t, a, 210, 12);
};

const GRADE: Record<string, string> = {
	warm: 'contrast(1.08) saturate(.92) sepia(.12) brightness(.92)',
	cool: 'contrast(1.1) saturate(.8) hue-rotate(-6deg) brightness(.85)',
	night: 'contrast(1.12) saturate(.85) brightness(.75)',
	mono: 'grayscale(1) contrast(1.15) brightness(.85)',
	gold: 'contrast(1.05) saturate(1.05) sepia(.2) brightness(.95)',
};

/** Full-bleed stock clip that starts playing at global time `at`, graded and slowly pushed in. */
export const Clip: React.FC<{src: string; at: number; until: number; trim?: number; grade?: string; push?: [number, number]; dim?: number; rate?: number; style?: React.CSSProperties; freezeAt?: number; transparent?: boolean}> = ({
	src, at, until, trim = 0, grade = 'warm', push = [1.04, 1.14], dim = 0.25, rate = 1, style, transparent,
}) => {
	const t = useT();
	if (t < at - 0.6 || t > until + 0.6) return null;
	const k = clamp01((t - at) / Math.max(0.1, until - at));
	return (
		<AbsoluteFill style={{overflow: 'hidden', ...style}}>
			<Sequence from={Math.round((at - 0.6) * FPS)} layout="none">
				<OffthreadVideo src={staticFile(src)} muted transparent={transparent} startFrom={Math.max(0, Math.round((trim - 0.6) * FPS))} playbackRate={rate}
					style={{width: '100%', height: '100%', objectFit: 'cover', filter: GRADE[grade], transform: `scale(${lerp(push[0], push[1], Easing.inOut(Easing.quad)(k))})`}} />
			</Sequence>
			{!transparent && <AbsoluteFill style={{background: `linear-gradient(180deg, rgba(11,13,20,${dim + 0.25}) 0%, rgba(11,13,20,${dim * 0.4}) 38%, rgba(11,13,20,${dim * 0.5}) 62%, rgba(11,13,20,${dim + 0.35}) 100%)`}} />}
		</AbsoluteFill>
	);
};

/** Big condensed display line with a masked slide-up reveal per word. */
export const Big: React.FC<{items: [string, number, ('gold' | 'serif' | 'coral')?][]; size?: number; style?: React.CSSProperties; align?: 'center' | 'left'}> = ({
	items, size = 150, style, align = 'center',
}) => {
	const t = useT();
	return (
		<div style={{display: 'flex', flexWrap: 'wrap', justifyContent: align === 'center' ? 'center' : 'flex-start', gap: `0 ${size * 0.18}px`, ...style}}>
			{items.map(([w, a, kind], i) => {
				const p = antic(t, a);
				const serif = kind === 'serif' || kind === 'gold';
				return (
					<span key={i} style={{display: 'inline-block', overflow: 'hidden', paddingTop: size * 0.06, paddingBottom: size * 0.04}}>
						<span style={{display: 'inline-block', transform: `translateY(${(1 - p) * 110}%) skewY(${(1 - clamp01(p)) * 6}deg)`,
							fontFamily: serif ? 'Serif' : 'Display', fontStyle: serif ? 'italic' : 'normal', fontWeight: serif ? 500 : 400,
							fontSize: serif ? size * 1.08 : size, lineHeight: 1, textTransform: serif ? 'none' : 'uppercase', letterSpacing: serif ? 0 : size * 0.01,
							color: kind === 'gold' ? C.gold : kind === 'coral' ? C.coral : C.ivory,
							textShadow: kind === 'gold' ? `0 0 ${30 * clamp01(p)}px rgba(242,184,75,.55), 0 6px 28px rgba(0,0,0,.6)` : '0 6px 28px rgba(0,0,0,.6)',
							filter: p < 0.98 ? `blur(${(1 - clamp01(p)) * 6}px)` : undefined}}>{w}</span>
					</span>
				);
			})}
		</div>
	);
};

/** Handwritten note (Kalam) that writes itself on with a wipe. */
export const Hand: React.FC<{at: number; children: React.ReactNode; size?: number; color?: string; rot?: number; style?: React.CSSProperties; dur?: number; out?: number}> = ({
	at, children, size = 58, color = C.marker, rot = -4, style, dur = 0.6, out,
}) => {
	const t = useT();
	const p = ease(t, at, dur, Easing.inOut(Easing.quad));
	const o = out !== undefined ? 1 - ease(t, out, 0.3) : 1;
	return (
		<div style={{position: 'absolute', fontFamily: 'Hand', fontWeight: 700, fontSize: size, color, transform: `rotate(${rot}deg)`, whiteSpace: 'nowrap',
			clipPath: `inset(-20% ${100 - p * 100}% -20% -5%)`, opacity: o, textShadow: '0 3px 12px rgba(0,0,0,.6)', ...style}}>{children}</div>
	);
};

/** Marker stroke drawn on, slightly rough like a real pen. */
export const Mark: React.FC<{d: string; at: number; dur?: number; color?: string; width?: number; w?: number; h?: number; style?: React.CSSProperties; out?: number}> = ({
	d, at, dur = 0.45, color = C.marker, width = 9, w = 1080, h = 1920, style, out,
}) => {
	const t = useT();
	const p = ease(t, at, dur, Easing.inOut(Easing.quad));
	const o = out !== undefined ? 1 - ease(t, out, 0.3) : 1;
	if (t < at) return null;
	return (
		<svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} style={{position: 'absolute', left: 0, top: 0, overflow: 'visible', opacity: o, ...style}}>
			<path d={d} pathLength={1} fill="none" stroke={color} strokeWidth={width} strokeLinecap="round" strokeLinejoin="round" strokeDasharray="1 1" strokeDashoffset={1 - p}
				style={{filter: 'url(#rough) drop-shadow(0 3px 6px rgba(0,0,0,.5))'}} />
		</svg>
	);
};

/** Printed archival photo: paper border, tape strips, slight curl shadow; drops in with a settle. */
export const Print: React.FC<{src: string; at: number; x: number; y: number; w: number; h: number; rot?: number; caption?: string; out?: number; filter?: string}> = ({
	src, at, x, y, w, h, rot = -4, caption, out, filter = 'grayscale(1) sepia(.35) contrast(1.15)',
}) => {
	const t = useT();
	const p = spr(t, at, 120, 13);
	const o = out !== undefined ? 1 - ease(t, out, 0.35) : 1;
	if (t < at - 0.05) return null;
	const tape = (l: number, r: number) => (
		<div style={{position: 'absolute', left: l, top: -26, width: 150, height: 52, transform: `rotate(${r}deg)`, background: 'rgba(240,226,190,.78)',
			boxShadow: '0 2px 6px rgba(0,0,0,.25)', clipPath: 'polygon(3% 0,97% 4%,100% 50%,96% 100%,2% 96%,0 50%)'}} />
	);
	return (
		<div style={{position: 'absolute', left: x, top: y, width: w, transform: `translateY(${(1 - p) * 160}px) rotate(${rot + (1 - p) * 9}deg) scale(${lerp(1.15, 1, clamp01(p))})`,
			opacity: clamp01(p * 2) * o, filter: 'drop-shadow(14px 26px 24px rgba(0,0,0,.55))'}}>
			<div style={{padding: '22px 22px 90px', backgroundImage: `url(${staticFile('paper.png')})`, backgroundSize: 'cover'}}>
				<Img src={staticFile(src)} style={{width: '100%', height: h, objectFit: 'cover', objectPosition: '50% 20%', filter, display: 'block'}} />
			</div>
			{tape(w * 0.12, -8)}{tape(w * 0.62, 6)}
			{caption && <div style={{position: 'absolute', left: 30, bottom: 18, fontFamily: 'Hand', fontWeight: 700, fontSize: 44, color: '#2b2b2b',
				clipPath: `inset(0 ${100 - ease(t, at + 0.5, 0.7) * 100}% 0 0)`}}>{caption}</div>}
		</div>
	);
};

/** Broadcast-style lower third. */
export const LowerThird: React.FC<{at: number; out: number; name: string; sub: string; y?: number}> = ({at, out, name, sub, y = 1250}) => {
	const t = useT();
	const bar = ease(t, at, 0.45, Easing.out(Easing.exp));
	const txt = ease(t, at + 0.2, 0.5);
	const o = 1 - ease(t, out, 0.35);
	if (t < at) return null;
	return (
		<div style={{position: 'absolute', left: 70, top: y, opacity: o}}>
			<div style={{width: 10, height: 150 * bar, background: C.gold, position: 'absolute', left: 0, top: 0}} />
			<div style={{marginLeft: 34, overflow: 'hidden'}}>
				<div style={{fontFamily: 'Display', fontSize: 92, color: C.ivory, letterSpacing: 2, transform: `translateX(${(1 - txt) * -60}px)`, opacity: txt, lineHeight: 1.05}}>{name}</div>
				<div style={{fontFamily: 'Sans', fontWeight: 700, fontSize: 30, color: C.gold, letterSpacing: '0.18em', textTransform: 'uppercase', marginTop: 6,
					transform: `translateX(${(1 - ease(t, at + 0.35, 0.5)) * -60}px)`, opacity: ease(t, at + 0.35, 0.5)}}>{sub}</div>
			</div>
		</div>
	);
};

/** Film-burn light leak across a cut. */
export const Burn: React.FC<{at: number; dur?: number; x?: number}> = ({at, dur = 0.7, x = 70}) => {
	const t = useT();
	if (t < at - 0.25 || t > at + dur) return null;
	const p = Math.sin(Math.PI * clamp01((t - at + 0.25) / (dur + 0.25)));
	return <AbsoluteFill style={{mixBlendMode: 'screen', background: `radial-gradient(ellipse at ${x + Math.sin(t * 9) * 10}% 30%, rgba(255,214,140,${0.85 * p}) 0%, rgba(255,120,40,${0.55 * p}) 28%, rgba(120,20,0,${0.25 * p}) 50%, rgba(0,0,0,0) 72%)`}} />;
};

/** RGB split for a glitchy, anxious beat. */
export const rgbSplit = (amt: number) => (amt > 0.2 ? `drop-shadow(${amt}px 0 0 rgba(255,0,60,.7)) drop-shadow(${-amt}px 0 0 rgba(0,220,255,.7))` : undefined);

export const scribble = (seed: string, cx: number, cy: number, rx: number, ry: number) => {
	// hand-drawn ellipse: slightly over-rotated with wobble so it never looks machine-perfect
	const pts: string[] = [];
	const n = 40;
	for (let i = 0; i <= n * 1.12; i++) {
		const a = (i / n) * Math.PI * 2 - 0.6;
		const j = 1 + (random(`${seed}${i}`) - 0.5) * 0.06;
		pts.push(`${(cx + Math.cos(a) * rx * j).toFixed(1)} ${(cy + Math.sin(a) * ry * j).toFixed(1)}`);
	}
	return `M ${pts.join(' L ')}`;
};
