import React from 'react';
import {AbsoluteFill, continueRender, delayRender, Easing, Img, OffthreadVideo, Sequence, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import tl from './timeline.json';

/* Clean creator-edit system (EarnEdits-like, kept sparse): paper + ink, one lime accent, red only for "banned". */
export const C = {
	ink: '#0f0f0f',
	paper: '#efebe3',
	white: '#ffffff',
	lime: '#c8f53c',
	red: '#ff3b30',
	orange: '#e8692e',
	grey: '#8a8a8a',
};

const FONTS: [string, string, string, string][] = [
	['Sans', 'Inter-900-latin', '900', 'normal'],
	['Sans', 'Inter-800-latin', '800', 'normal'],
	['Sans', 'Inter-600-latin', '600', 'normal'],
	['Serif', 'CormorantGaramond-500-italic', '500', 'italic'],
	['Serif', 'CormorantGaramond-700-normal', '700', 'normal'],
	['Display', 'Anton-400-latin', '400', 'normal'],
	['Hand', 'Kalam-700-latin', '700', 'normal'],
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
export const DUR = tl.duration;
export const useT = () => useCurrentFrame() / FPS;
export const clamp01 = (x: number) => Math.max(0, Math.min(1, x));
export const lerp = (a: number, b: number, p: number) => a + (b - a) * p;
export const ease = (t: number, a: number, d: number, fn = Easing.out(Easing.cubic)) => fn(clamp01((t - a) / d));
/** Overshoot pop for UI elements (anticipation-free, settles in ~0.35 s). */
export const pop = (t: number, a: number, d = 0.35) => Easing.out(Easing.back(1.7))(clamp01((t - a) / d));

/** Layout: v = vertical Shorts (1080x1920), else YouTube (1920x1080). Sizes are authored for a 1080 short edge. */
export const useLayout = () => {
	const {width, height} = useVideoConfig();
	return {W: width, H: height, v: height > width};
};

/** Visible only inside [s, e). */
export const In: React.FC<{s: number; e: number; children: React.ReactNode}> = ({s, e, children}) => {
	const t = useT();
	return t >= s && t < e ? <>{children}</> : null;
};

/** Cut-in treatment: the incoming shot settles from a slight zoom + motion blur (reads like a whip, not a template wipe). */
export const enter = (t: number, at: number) => {
	const p = ease(t, at, 0.28);
	return {transform: `scale(${lerp(1.12, 1, p)})`, filter: p < 1 ? `blur(${(1 - p) * 14}px)` : undefined};
};

/** Stock clip that starts at `at`, cover-fit, slow handheld-ish drift. */
export const BRoll: React.FC<{src: string; at: number; until: number; trim?: number; grade?: string; freezeAt?: number; dim?: number}> = ({
	src, at, until, trim = 0, grade = 'contrast(1.06) saturate(1.05)', freezeAt, dim = 0.15,
}) => {
	const t = useT();
	if (t < at - 0.05 || t > until + 0.05) return null;
	const k = t - at;
	const dx = Math.sin(k * 0.9) * 6, dy = Math.cos(k * 0.7) * 5;
	const frozen = freezeAt !== undefined && t >= freezeAt;
	return (
		<AbsoluteFill style={{overflow: 'hidden', ...enter(t, at)}}>
			<Sequence from={Math.round(at * FPS)} layout="none">
				<OffthreadVideo src={staticFile(src)} muted startFrom={Math.round(trim * FPS)} playbackRate={1}
					style={{width: '100%', height: '100%', objectFit: 'cover', filter: frozen ? 'grayscale(1) contrast(1.25) brightness(.7)' : grade,
						transform: `translate(${dx}px, ${dy}px) scale(${1.06 + k * 0.012})`}} />
			</Sequence>
			<AbsoluteFill style={{background: `linear-gradient(180deg, rgba(0,0,0,${dim + 0.25}) 0%, rgba(0,0,0,${dim}) 35%, rgba(0,0,0,${dim}) 60%, rgba(0,0,0,${dim + 0.35}) 100%)`}} />
		</AbsoluteFill>
	);
};

/** A held still frame of a clip (used for the freeze on "ban"). */
export const Still: React.FC<{src: string; style?: React.CSSProperties}> = ({src, style}) => (
	<Img src={staticFile(src)} style={{width: '100%', height: '100%', objectFit: 'cover', ...style}} />
);

/** Words rise out of a mask one after another, each on its own beat. */
export const Words: React.FC<{items: [string, number, ('lime' | 'serif' | 'red' | 'grey' | 'ink')?][]; size: number; align?: 'center' | 'left'; color?: string; style?: React.CSSProperties; weight?: number}> = ({
	items, size, align = 'center', color = C.white, style, weight = 900,
}) => {
	const t = useT();
	return (
		<div style={{display: 'flex', flexWrap: 'wrap', justifyContent: align === 'center' ? 'center' : 'flex-start', columnGap: size * 0.24, rowGap: 0, ...style}}>
			{items.map(([w, at, k], i) => {
				const p = Easing.out(Easing.back(1.4))(clamp01((t - at) / 0.32));
				const serif = k === 'serif';
				return (
					<div key={i} style={{overflow: 'hidden', padding: `0 ${size * 0.03}px ${size * 0.1}px`}}>
						<div style={{transform: `translateY(${(1 - p) * 110}%)`, opacity: t >= at - 0.02 ? 1 : 0,
							fontFamily: serif ? 'Serif' : 'Sans', fontStyle: serif ? 'italic' : 'normal', fontWeight: serif ? 500 : weight,
							fontSize: serif ? size * 1.12 : size, lineHeight: 1.0, letterSpacing: serif ? 0 : '-0.035em',
							color: k === 'lime' ? C.lime : k === 'red' ? C.red : k === 'grey' ? C.grey : k === 'ink' ? C.ink : color,
							textShadow: k === 'ink' ? 'none' : '0 6px 30px rgba(0,0,0,.45)'}}>{w}</div>
					</div>
				);
			})}
		</div>
	);
};

/** Small pill label: "01  Genuine content". */
export const Tag: React.FC<{n: string; label: string; at: number; size?: number; style?: React.CSSProperties}> = ({n, label, at, size = 44, style}) => {
	const t = useT();
	const p = pop(t, at);
	return (
		<div style={{display: 'inline-flex', alignItems: 'center', gap: size * 0.4, background: C.white, borderRadius: size, padding: `${size * 0.28}px ${size * 0.6}px ${size * 0.28}px ${size * 0.3}px`,
			boxShadow: '0 14px 40px rgba(0,0,0,.35)', transform: `scale(${p})`, transformOrigin: 'left center', opacity: clamp01(p * 3), ...style}}>
			<div style={{width: size * 1.25, height: size * 1.25, borderRadius: '50%', background: C.lime, display: 'grid', placeItems: 'center', fontFamily: 'Sans', fontWeight: 900, fontSize: size * 0.55, color: C.ink}}>{n}</div>
			<div style={{fontFamily: 'Sans', fontWeight: 800, fontSize: size, color: C.ink, letterSpacing: '-0.02em', whiteSpace: 'nowrap'}}>{label}</div>
		</div>
	);
};

/** Hand-drawn style tick that draws itself. */
export const Tick: React.FC<{at: number; size: number}> = ({at, size}) => {
	const t = useT();
	const p = ease(t, at, 0.25);
	return (
		<svg width={size} height={size} viewBox="0 0 40 40">
			<rect x={2} y={2} width={36} height={36} rx={9} fill={p > 0 ? C.lime : 'none'} stroke={p > 0 ? C.lime : 'rgba(15,15,15,.35)'} strokeWidth={3} />
			<path d="M10 21 L17 28 L31 12" fill="none" stroke={C.ink} strokeWidth={5} strokeLinecap="round" strokeLinejoin="round" pathLength={1} strokeDasharray="1 1" strokeDashoffset={1 - p} />
		</svg>
	);
};

/** Word-by-word captions; the spoken word lights up in lime. */
export const Captions: React.FC<{hide?: [number, number][]}> = ({hide = []}) => {
	const t = useT();
	const {v} = useLayout();
	if (hide.some(([a, b]) => t >= a && t < b)) return null;
	const page = TL.pages.find((p) => t >= p.s - 0.05 && t < p.e);
	if (!page) return null;
	const size = v ? 60 : 52;
	return (
		<div style={{position: 'absolute', left: v ? 90 : 360, right: v ? 150 : 360, top: v ? 1390 : 905, display: 'flex', justifyContent: 'center'}}>
		<div style={{display: 'flex', justifyContent: 'center', flexWrap: 'wrap', gap: '4px 16px', background: 'rgba(10,10,10,.42)', borderRadius: 16, padding: '6px 20px 10px'}}>
			{page.words.map((w, i) => {
				const on = t >= w.s - 0.03 && t < w.e + 0.1;
				const shown = t >= w.s - 0.06;
				return <span key={i} style={{fontFamily: 'Sans', fontWeight: 800, fontSize: size, letterSpacing: '-0.02em', color: on ? C.lime : C.white,
					display: shown ? 'inline' : 'none', transform: on ? 'translateY(-3px)' : undefined,
					textShadow: '0 3px 0 rgba(0,0,0,.55), 0 0 18px rgba(0,0,0,.6)'}}>{w.t}</span>;
			})}
		</div>
		</div>
	);
};

export const paperBg: React.CSSProperties = {backgroundColor: C.paper, backgroundImage: `url(${staticFile('paper.png')})`, backgroundSize: 'cover', backgroundBlendMode: 'multiply'};
export const gridBg = (base: string, line = 'rgba(0,0,0,.12)'): React.CSSProperties => ({
	backgroundColor: base,
	backgroundImage: `linear-gradient(${line} 2px, transparent 2px), linear-gradient(90deg, ${line} 2px, transparent 2px)`,
	backgroundSize: '72px 72px',
});
