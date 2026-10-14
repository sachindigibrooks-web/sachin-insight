import React from 'react';
import {AbsoluteFill, continueRender, delayRender, Easing, Img, OffthreadVideo, Sequence, staticFile, useCurrentFrame} from 'remotion';
import tl from './timeline.json';

/* Mudras brand system (from mudras.com CSS): gold accent hsl(42,80%,70%), near-black, deep forest accent, cream. */
export const C = {
	gold: '#f0cc75',
	goldDeep: '#c9a24e',
	black: '#141414',
	charcoal: '#212121',
	forest: '#1f2c1b',
	cream: '#f2efe6',
	white: '#fffcf2',
};

const FONTS: [string, string, string, string][] = [
	['Display', 'CormorantGaramond-500-normal', '500', 'normal'],
	['Display', 'CormorantGaramond-700-normal', '700', 'normal'],
	['Display', 'CormorantGaramond-500-italic', '500', 'italic'],
	['Caps', 'Cinzel-600-normal', '600', 'normal'],
	['Body', 'Raleway-500', '300 700', 'normal'],
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
export const lerp = (a: number, b: number, p: number) => a + (b - a) * p;
/** Luxury motion: long, soft ease-in-out (quint) for everything; nothing bounces. */
export const ease = (t: number, a: number, d: number, fn = Easing.bezier(0.22, 1, 0.36, 1)) => fn(clamp01((t - a) / d));
export const inout = (t: number, a: number, d: number) => Easing.inOut(Easing.poly(5))(clamp01((t - a) / d));

const GRADE = 'grayscale(.88) sepia(.18) contrast(1.12) brightness(.82)';

export const Clip: React.FC<{src: string; at: number; until: number; trim?: number; push?: [number, number]; grade?: string; style?: React.CSSProperties; dim?: number}> = ({
	src, at, until, trim = 0, push = [1.06, 1.14], grade = GRADE, style, dim = 0.25,
}) => {
	const t = useT();
	if (t < at - 0.7 || t > until + 0.7) return null;
	const k = clamp01((t - at) / Math.max(0.1, until - at));
	return (
		<AbsoluteFill style={{overflow: 'hidden', ...style}}>
			<Sequence from={Math.round((at - 0.7) * FPS)} layout="none">
				<OffthreadVideo src={staticFile(src)} muted startFrom={Math.max(0, Math.round((trim - 0.7) * FPS))}
					style={{width: '100%', height: '100%', objectFit: 'cover', filter: grade, transform: `scale(${lerp(push[0], push[1], k)})`}} />
			</Sequence>
			<AbsoluteFill style={{background: `linear-gradient(180deg, rgba(20,20,20,${dim + 0.3}) 0%, rgba(20,20,20,${dim * 0.3}) 40%, rgba(20,20,20,${dim * 0.5}) 65%, rgba(20,20,20,${dim + 0.45}) 100%)`}} />
		</AbsoluteFill>
	);
};

export const Photo: React.FC<{src: string; at: number; until: number; push?: [number, number]; pos?: string; style?: React.CSSProperties; dim?: number; grade?: string}> = ({
	src, at, until, push = [1.12, 1.0], pos = '50% 50%', style, dim = 0.2, grade = 'contrast(1.08) brightness(.9)',
}) => {
	const t = useT();
	const k = clamp01((t - at) / Math.max(0.1, until - at));
	return (
		<AbsoluteFill style={{overflow: 'hidden', ...style}}>
			<Img src={staticFile(src)} style={{width: '100%', height: '100%', objectFit: 'cover', objectPosition: pos, filter: grade, transform: `scale(${lerp(push[0], push[1], k)})`}} />
			<AbsoluteFill style={{background: `linear-gradient(180deg, rgba(20,20,20,${dim + 0.3}) 0%, rgba(20,20,20,${dim * 0.3}) 40%, rgba(20,20,20,${dim * 0.5}) 65%, rgba(20,20,20,${dim + 0.45}) 100%)`}} />
		</AbsoluteFill>
	);
};

/** Serif headline: each line rises out of a mask with tracking that settles (luxury title treatment). */
export const Title: React.FC<{lines: [string, number, ('gold' | 'italic' | 'caps')?][]; size?: number; style?: React.CSSProperties; out?: number}> = ({lines, size = 120, style, out}) => {
	const t = useT();
	const o = out !== undefined ? 1 - inout(t, out, 0.5) : 1;
	return (
		<div style={{textAlign: 'center', opacity: o, ...style}}>
			{lines.map(([txt, a, kind], i) => {
				const p = ease(t, a, 1.1);
				const caps = kind === 'caps';
				return (
					<div key={i} style={{overflow: 'hidden', paddingBottom: size * 0.08}}>
						<div style={{transform: `translateY(${(1 - p) * 105}%)`, opacity: clamp01(p * 1.6),
							fontFamily: caps ? 'Caps' : 'Display', fontWeight: caps ? 600 : kind === 'italic' ? 500 : 500, fontStyle: kind === 'italic' ? 'italic' : 'normal',
							fontSize: caps ? size * 0.42 : size, lineHeight: 1.02, color: kind === 'gold' || caps ? C.gold : C.cream,
							letterSpacing: caps ? `${lerp(0.6, 0.32, p)}em` : `${lerp(0.04, -0.005, p)}em`, textShadow: '0 4px 30px rgba(0,0,0,.55)'}}>{txt}</div>
					</div>
				);
			})}
		</div>
	);
};

/** Thin gold rule that draws from the centre outward. */
export const Rule: React.FC<{at: number; y: number; w?: number; x?: number}> = ({at, y, w = 420, x}) => {
	const t = useT();
	const p = ease(t, at, 1.0);
	return <div style={{position: 'absolute', left: x ?? 540 - (w * p) / 2, top: y, width: w * p, height: 2, background: `linear-gradient(90deg, rgba(240,204,117,0), ${C.gold}, rgba(240,204,117,0))`}} />;
};

/** Gold logo reveal: fades up from a soft blur, then a specular light sweep crosses the letters. */
export const Logo: React.FC<{at: number; w?: number; y?: number; sweep?: number; out?: number}> = ({at, w = 760, y = 760, sweep, out}) => {
	const t = useT();
	const p = ease(t, at, 1.4);
	const s = clamp01((t - (sweep ?? at + 0.6)) / 1.1);
	const o = out !== undefined ? 1 - inout(t, out, 0.6) : 1;
	const src = staticFile('brand/logo_full.png');
	return (
		<div style={{position: 'absolute', left: 540 - w / 2, top: y, width: w, opacity: p * o, transform: `scale(${lerp(1.08, 1, p)})`, filter: `blur(${(1 - p) * 10}px) drop-shadow(0 0 ${30 * p}px rgba(240,204,117,.25))`}}>
			<Img src={src} style={{width: '100%', display: 'block'}} />
			{s > 0 && s < 1 && (
				<div style={{position: 'absolute', inset: 0, WebkitMaskImage: `url(${src})`, WebkitMaskSize: '100% 100%', maskImage: `url(${src})`, maskSize: '100% 100%',
					background: `linear-gradient(105deg, rgba(255,255,255,0) ${s * 140 - 40}%, rgba(255,250,230,.95) ${s * 140 - 25}%, rgba(255,255,255,0) ${s * 140 - 10}%)`}} />
			)}
		</div>
	);
};

/** Pulsing gold hotspot with a label (body assessment). */
export const Hotspot: React.FC<{at: number; x: number; y: number; label: string; side?: 'l' | 'r'}> = ({at, x, y, label, side = 'r'}) => {
	const t = useT();
	if (t < at) return null;
	const p = ease(t, at, 0.6);
	const ring = ((t - at) % 1.6) / 1.6;
	const lp = ease(t, at + 0.2, 0.7);
	return (
		<>
			<div style={{position: 'absolute', left: x - 14, top: y - 14, width: 28, height: 28, borderRadius: '50%', background: C.gold, opacity: p, boxShadow: `0 0 24px ${C.gold}`, transform: `scale(${p})`}} />
			<div style={{position: 'absolute', left: x - 60, top: y - 60, width: 120, height: 120, borderRadius: '50%', border: `2px solid ${C.gold}`, opacity: (1 - ring) * p, transform: `scale(${0.3 + ring * 0.9})`}} />
			<div style={{position: 'absolute', top: y - 1, left: side === 'r' ? x + 24 : x - 24 - 90 * lp, width: (side === 'r' ? 180 : 90) * lp, height: 2, background: C.gold}} />
			<div style={{position: 'absolute', top: y - 52, left: side === 'r' ? x + 214 : undefined, right: side === 'l' ? 1080 - x + 124 : undefined, fontFamily: 'Caps', fontSize: 34, letterSpacing: '0.2em',
				color: C.cream, opacity: lp, whiteSpace: 'nowrap', textShadow: '0 2px 12px rgba(0,0,0,.7)'}}>{label}</div>
		</>
	);
};
