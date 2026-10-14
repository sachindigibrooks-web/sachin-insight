import React from 'react';
import {AbsoluteFill, Img, staticFile} from 'remotion';
import {B, C, clamp01, Clip, ease, Hotspot, inout, lerp, Logo, Photo, Rule, Title, useT} from './lib';

const In: React.FC<{s: number; e: number; children: React.ReactNode}> = ({s, e, children}) => {
	const t = useT();
	return t >= s && t < e ? <>{children}</> : null;
};
/** Soft cross-dissolve wrapper (luxury cuts: dissolves + occasional hard cut on the beat). */
const Fade: React.FC<{s: number; e: number; d?: number; children: React.ReactNode}> = ({s, e, d = 0.45, children}) => {
	const t = useT();
	if (t < s - d || t > e + d) return null;
	const o = inout(t, s - d, d * 2) * (1 - inout(t, e - d * 0.4, d));
	return <AbsoluteFill style={{opacity: o}}>{children}</AbsoluteFill>;
};
const Abs: React.FC<{y: number; x?: number; w?: number; style?: React.CSSProperties; children: React.ReactNode}> = ({y, x = 0, w = 1080, style, children}) => (
	<div style={{position: 'absolute', left: x, top: y, width: w, ...style}}>{children}</div>
);

/* 1. Your body is not a time slot: a booking grid of identical slots, struck through in gold */
const S1 = () => {
	const t = useT();
	const slots = ['10:00', '10:30', '11:00', '11:30', '12:00', '12:30', '1:00', '1:30', '2:00'];
	return (
		<Fade s={0} e={B.l1 - 0.05} d={0.3}>
			<Photo src="brand/dsc3927.jpg" at={0} until={3} push={[1.15, 1.05]} dim={0.55} grade="grayscale(1) contrast(1.1) brightness(.6)" />
			<div style={{position: 'absolute', left: 140, top: 760, width: 800, display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 22}}>
				{slots.map((s, i) => {
					const p = ease(t, 0.15 + i * 0.07, 0.6);
					return <div key={s} style={{height: 96, border: '1.5px solid rgba(242,239,230,.45)', borderRadius: 6, display: 'flex', alignItems: 'center', justifyContent: 'center',
						fontFamily: 'Body', fontWeight: 500, fontSize: 36, letterSpacing: '0.12em', color: 'rgba(242,239,230,.75)', opacity: p, transform: `translateY(${(1 - p) * 20}px)`}}>{s}</div>;
				})}
				<div style={{position: 'absolute', left: -30, top: 160, height: 4, width: 860 * ease(t, 1.75, 0.5), background: C.gold, boxShadow: `0 0 18px ${C.gold}`, transform: 'rotate(-14deg)', transformOrigin: '0 50%'}} />
			</div>
			<Abs y={360}><Title size={104} lines={[['Your body is not', 0.6], ['a time slot.', 1.5, 'italic']]} /></Abs>
		</Fade>
	);
};

/* 2. Every massage feels the same: the same clip, tiled, in lock-step */
const S2 = () => {
	const t = useT();
	return (
		<Fade s={B.l1 - 0.05} e={B.l2 - 0.1} d={0.25}>
			<AbsoluteFill style={{background: C.black}} />
			<div style={{position: 'absolute', inset: 0, display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gridTemplateRows: 'repeat(3, 1fr)', gap: 6, padding: 6}}>
				{Array.from({length: 9}, (_, i) => (
					<div key={i} style={{position: 'relative', overflow: 'hidden', opacity: ease(t, B.l1 + i * 0.05, 0.4)}}>
						<Clip src="v/massage3.mp4" at={B.l1} until={B.l2} push={[1.0, 1.0]} dim={0.15} grade="grayscale(1) contrast(1.05) brightness(.7)" />
					</div>
				))}
			</div>
			<AbsoluteFill style={{background: 'rgba(20,20,20,.45)'}} />
			<Abs y={720}><Title size={100} lines={[['So why does every massage', B.l1 + 0.1], ['feel the same?', B.same - 0.6, 'italic']]} /></Abs>
		</Fade>
	);
};

/* 3. Brand reveal on the music drop: black, gold logo with light sweep, then real Mudras photography */
const S3 = () => {
	const t = useT();
	const photos = ['brand/dsc3958.jpg', 'brand/trigger.jpg', 'brand/sports.jpg'];
	return (
		<In s={B.l2 - 0.1} e={B.l3 - 0.05}>
			<AbsoluteFill style={{background: `radial-gradient(circle at 50% 45%, #2a2a24 0%, ${C.black} 70%)`}} />
			{t > 6.9 && (
				<div style={{position: 'absolute', left: 90, top: 1090, width: 900, display: 'flex', gap: 14, opacity: ease(t, 6.9, 0.8)}}>
					{photos.map((p, i) => (
						<div key={p} style={{flex: 1, height: 420, overflow: 'hidden', borderRadius: 4, transform: `translateY(${(1 - ease(t, 6.9 + i * 0.12, 0.9)) * 60}px)`}}>
							<Img src={staticFile(p)} style={{width: '100%', height: '100%', objectFit: 'cover', filter: 'contrast(1.08) brightness(.9)'}} />
						</div>
					))}
				</div>
			)}
			<Logo at={B.l2 - 0.05} w={820} y={560} sweep={B.l2 + 0.7} />
			<Rule at={6.6} y={880} w={520} />
			<Abs y={920}><Title size={70} lines={[['No two sessions look alike.', 6.6, 'italic']]} /></Abs>
		</In>
	);
};

/* 4. Signature BodyReset: title card, then a gold body map built in real time */
const BODY = 'M540 470 C 500 470 478 500 478 540 C 478 590 505 618 540 618 C 575 618 602 590 602 540 C 602 500 580 470 540 470 Z ' +
	'M510 615 L505 660 C 430 668 360 690 330 740 C 310 800 300 880 290 980 L270 1150 M570 615 L575 660 C 650 668 720 690 750 740 C 770 800 780 880 790 980 L810 1150 ' +
	'M360 735 C 380 860 390 960 400 1080 C 410 1180 420 1260 430 1330 M720 735 C 700 860 690 960 680 1080 C 670 1180 660 1260 650 1330 M430 1330 C 480 1350 600 1350 650 1330';
const S4 = () => {
	const t = useT();
	const draw = ease(t, B.l4 - 0.2, 1.6);
	return (
		<>
			<Fade s={B.l3 - 0.05} e={B.l4 - 0.2} d={0.35}>
				<Clip src="v/oilmassage.mp4" at={B.l3 - 0.05} until={B.l4} push={[1.05, 1.15]} dim={0.35} />
				<Abs y={600}>
					<Title size={92} lines={[['Every visit begins with', B.l3, 'caps'], ['our signature', B.l3 + 0.35, 'caps']]} />
					<Rule at={B.l3 + 0.6} y={150} w={600} />
					<Title size={190} style={{marginTop: 40}} lines={[['BodyReset', 9.9, 'gold']]} />
				</Abs>
			</Fade>
			<Fade s={B.l4 - 0.2} e={B.l5 - 0.1} d={0.35}>
				<Clip src="v/backmassage.mp4" at={B.l4 - 0.2} until={B.l5} push={[1.1, 1.2]} dim={0.6} />
				<svg width={1080} height={1920} style={{position: 'absolute', left: 0, top: 0, filter: 'drop-shadow(0 0 10px rgba(240,204,117,.4))'}}>
					<path d={BODY} fill="none" stroke={C.gold} strokeWidth={3} pathLength={1} strokeDasharray="1 1" strokeDashoffset={1 - draw} />
					<path d="M540 630 L540 1300" stroke={C.gold} strokeWidth={2} strokeDasharray="6 12" opacity={ease(t, B.l4 + 0.8, 0.6)} />
				</svg>
				<Hotspot at={B.real} x={540} y={650} label="NECK" />
				<Hotspot at={12.6} x={395} y={720} label="SHOULDERS" side="l" />
				<Hotspot at={B.carrying - 0.3} x={540} y={1160} label="LOWER BACK" />
				<Abs y={250}><Title size={84} lines={[['Built in real time,', B.real - 0.4, 'italic'], ['around what your body', 13.0], ['is carrying today.', B.carrying - 0.2, 'gold']]} /></Abs>
			</Fade>
		</>
	);
};

/* 5. Techniques: a menu that writes itself, each item cut to its own image */
const TECH: [string, string, string][] = [
	['Deep tissue', 'deep', 'brand/deeptissue.jpg'],
	['Trigger point', 'trigger', 'brand/trigger.jpg'],
	['Assisted stretching', 'assisted', 'brand/sports.jpg'],
	['Cupping', 'cupping', 'brand/dsc3958.jpg'],
	['Gua sha', 'gua', 'v/guasha.mp4'],
];
const ICONS = ['brand/who1.png', 'brand/who2.png', 'brand/who3.png', 'brand/who4.png', 'brand/f81a.png'];
const S5 = () => {
	const t = useT();
	const cur = TECH.reduce((k, x, i) => (t >= B[x[1]] - 0.1 ? i : k), 0);
	const chosen = t >= B.chosen - 0.15;
	return (
		<In s={B.l5 - 0.1} e={B.l7 - 0.05}>
			{TECH.map(([name, key, src], i) => {
				const s = B[key] - 0.1;
				const e = i < 4 ? B[TECH[i + 1][1]] - 0.1 : B.l7;
				if (t < s - 0.3 || t > e + 0.3) return null;
				const o = inout(t, s - 0.25, 0.3) * (1 - inout(t, e - 0.05, 0.3));
				return src.endsWith('.mp4')
					? <AbsoluteFill key={key} style={{opacity: o}}><Clip src={src} at={s} until={e} push={[1.08, 1.18]} dim={0.45} /></AbsoluteFill>
					: <AbsoluteFill key={key} style={{opacity: o}}><Photo src={src} at={s} until={e + 0.6} push={[1.16, 1.04]} dim={0.4} /></AbsoluteFill>;
			})}
			<AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(20,20,20,.75) 0%, rgba(20,20,20,.55) 45%, rgba(20,20,20,0) 70%)', opacity: 1 - inout(t, B.chosen - 0.4, 0.4)}} />
			<div style={{position: 'absolute', left: 120, top: 330, width: 840, opacity: 1 - inout(t, B.chosen - 0.4, 0.4)}}>
				<div style={{fontFamily: 'Caps', fontSize: 30, letterSpacing: '0.4em', color: C.gold, marginBottom: 36, opacity: ease(t, B.l5, 0.8)}}>TECHNIQUES MAY INCLUDE</div>
				{TECH.map(([name, key], i) => {
					const p = ease(t, B[key] - 0.1, 0.8);
					const on = i === cur;
					return (
						<div key={name} style={{display: 'flex', alignItems: 'center', gap: 26, height: 118, borderTop: '1px solid rgba(242,239,230,.25)', opacity: p ? lerp(0, on ? 1 : 0.45, p) : 0,
							transform: `translateX(${(1 - p) * -40}px)`}}>
							<Img src={staticFile(ICONS[i])} style={{width: 76, height: 76, opacity: on ? 1 : 0.6}} />
							<div style={{fontFamily: 'Display', fontWeight: 500, fontSize: 76, color: on ? C.gold : C.cream}}>{name}</div>
						</div>
					);
				})}
			</div>
			{chosen && (
				<Abs y={720}><Title size={130} lines={[['Chosen for you.', B.chosen, 'gold'], ['Not from a script.', 21.4, 'italic']]} /></Abs>
			)}
		</In>
	);
};

/* 6. Pro athletes & desk warriors: split screen */
const S6 = () => {
	const t = useT();
	const top = ease(t, B.l7 - 0.1, 0.9);
	const bot = ease(t, B.desk - 0.2, 0.9);
	return (
		<Fade s={B.l7 - 0.05} e={B.l8 - 0.05} d={0.3}>
			<AbsoluteFill style={{background: C.black}} />
			<div style={{position: 'absolute', left: 0, top: 0, width: 1080, height: 955, overflow: 'hidden', clipPath: `inset(0 ${100 - top * 100}% 0 0)`}}>
				<Clip src="v/lifter.mp4" at={B.l7 - 0.1} until={B.l8} push={[1.1, 1.2]} dim={0.05} style={{bottom: 'auto', height: 955}} />
			</div>
			<div style={{position: 'absolute', left: 0, top: 965, width: 1080, height: 955, overflow: 'hidden', clipPath: `inset(0 0 0 ${100 - bot * 100}%)`}}>
				<Clip src="v/wfhpain.mp4" at={B.desk - 0.2} until={B.l8} push={[1.1, 1.2]} dim={0.05} style={{bottom: 'auto', height: 955}} />
			</div>
			<div style={{position: 'absolute', left: 0, top: 955, width: 1080 * ease(t, B.l7, 0.8), height: 10, background: C.gold}} />
			<Abs y={720}><Title size={92} lines={[['Pro athletes', B.athletes - 0.2, 'gold']]} /></Abs>
			<Abs y={1010}><Title size={92} lines={[['& desk warriors', B.desk - 0.1, 'italic']]} /></Abs>
		</Fade>
	);
};

/* 7. Experience: specialists, an animated counter */
const S7 = () => {
	const t = useT();
	const n = Math.round(lerp(0, 20, ease(t, B.n15 - 0.3, 1.3)));
	return (
		<Fade s={B.l8 - 0.05} e={B.l9 - 0.1} d={0.35}>
			<Photo src="brand/deeptissue2.jpg" at={B.l8} until={B.l9} push={[1.25, 1.08]} dim={0.6} />
			<Abs y={330}><Title size={92} lines={[['Led by licensed', B.licensed - 0.4, 'caps'], ['specialists', B.licensed - 0.1, 'caps']]} /></Abs>
			<Abs y={600}>
				<div style={{textAlign: 'center', fontFamily: 'Display', fontWeight: 500, fontSize: 330, lineHeight: 1, color: C.gold, opacity: ease(t, B.n15 - 0.3, 0.6),
					textShadow: '0 0 40px rgba(240,204,117,.25)'}}>
					{t < B.n15 + 0.6 ? Math.min(n, 15) : 15}<span style={{fontSize: 200, color: C.cream}}>–</span>{n}
				</div>
			</Abs>
			<Abs y={980}><Title size={90} lines={[['years of experience', B.years - 0.1, 'italic']]} /></Abs>
			<Rule at={B.years} y={1130} w={520} />
		</Fade>
	);
};

/* 8. What clients often notice */
const BEN: [string, string][] = [['Less tension', 'less'], ['Easier movement', 'easier'], ['Deeper sleep', 'deeper']];
const S8 = () => {
	const t = useT();
	return (
		<Fade s={B.l9 - 0.1} e={B.l10 - 0.1} d={0.35}>
			<Clip src="v/candles.mp4" at={B.l9 - 0.1} until={B.l10} push={[1.05, 1.15]} dim={0.4} grade="sepia(.35) saturate(.7) contrast(1.1) brightness(.8)" />
			<Abs y={330}><Title size={88} lines={[['What clients', B.l9 - 0.2, 'caps'], ['often notice', B.l9 + 0.1, 'caps']]} /></Abs>
			{BEN.map(([b, k], i) => {
				const p = ease(t, B[k] - 0.1, 0.9);
				return (
					<div key={b} style={{position: 'absolute', left: 150, top: 560 + i * 230, width: 780, height: 180, border: `1.5px solid rgba(240,204,117,${0.7 * p})`, borderRadius: 8,
						background: `rgba(20,20,20,${0.45 * p})`, display: 'flex', alignItems: 'center', gap: 34, padding: '0 48px', boxSizing: 'border-box', opacity: p,
						transform: `translateY(${(1 - p) * 40}px)`}}>
						<div style={{fontFamily: 'Caps', fontSize: 40, color: C.gold}}>0{i + 1}</div>
						<div style={{fontFamily: 'Display', fontSize: 84, color: C.cream}}>{b}</div>
					</div>
				);
			})}
			<div style={{position: 'absolute', left: 0, width: 1080, top: 1300, textAlign: 'center', fontFamily: 'Body', fontSize: 26, letterSpacing: '0.08em',
				color: 'rgba(242,239,230,.6)', opacity: ease(t, B.deeper, 0.6)}}>Results vary by person and by session.</div>
		</Fade>
	);
};

/* 9. Brand line over New York */
const S9 = () => {
	const t = useT();
	return (
		<Fade s={B.l10 - 0.1} e={B.l11 - 0.15} d={0.4}>
			<Clip src="v/citynight.mp4" at={B.l10 - 0.1} until={B.l11} push={[1.05, 1.18]} dim={0.4} grade="grayscale(.7) sepia(.25) contrast(1.15) brightness(.75)" />
			<Logo at={B.l10} w={780} y={640} sweep={B.l10 + 1.0} />
			<Rule at={B.l10 + 1.2} y={950} w={520} />
			<Abs y={990}><Title size={64} lines={[['Chelsea · New York', B.chelsea - 0.3, 'caps']]} /></Abs>
		</Fade>
	);
};

/* 10. CTA end card */
const S10 = () => {
	const t = useT();
	const btn = ease(t, B.book, 0.9);
	return (
		<Fade s={B.l11 - 0.15} e={44.5} d={0.4}>
			<AbsoluteFill style={{background: `radial-gradient(circle at 50% 40%, #26302200 0%, ${C.black} 75%), ${C.forest}`}} />
			<AbsoluteFill style={{background: `radial-gradient(circle at 50% 38%, rgba(240,204,117,.12) 0%, rgba(0,0,0,0) 55%)`}} />
			<Logo at={B.l11 - 0.1} w={640} y={380} sweep={B.l11 + 0.8} />
			<Abs y={720}><Title size={110} lines={[['Book your', B.book - 0.05, 'italic'], ['BodyReset', 39.4, 'gold']]} /></Abs>
			<div style={{position: 'absolute', left: 300, top: 1060, width: 480, height: 110, borderRadius: 60, background: C.gold, display: 'flex', alignItems: 'center', justifyContent: 'center',
				fontFamily: 'Caps', fontSize: 38, letterSpacing: '0.25em', color: C.black, opacity: btn, transform: `scale(${lerp(0.9, 1, btn) * (1 + 0.02 * Math.sin(t * 4) * clamp01(t - 40.5))})`,
				boxShadow: '0 12px 40px rgba(240,204,117,.25)'}}>BOOK NOW</div>
			<div style={{position: 'absolute', left: 0, width: 1080, top: 1240, textAlign: 'center', fontFamily: 'Body', fontWeight: 500, color: C.cream, opacity: ease(t, 40.4, 0.9)}}>
				<div style={{fontSize: 44, letterSpacing: '0.12em', color: C.gold}}>mudras.com</div>
				<div style={{fontSize: 34, marginTop: 18, letterSpacing: '0.06em'}}>(212) 837-8382</div>
				<div style={{fontSize: 28, marginTop: 14, opacity: 0.75, letterSpacing: '0.04em'}}>37 W 20th St, Suite 607 · Chelsea, NYC</div>
				<div style={{fontSize: 26, marginTop: 10, opacity: 0.6, letterSpacing: '0.04em'}}>Mon–Sat · 11 AM – 9 PM</div>
			</div>
		</Fade>
	);
};

export const Scenes = () => (
	<>
		<S1 /><S2 /><S3 /><S4 /><S5 /><S6 /><S7 /><S8 /><S9 /><S10 />
	</>
);
