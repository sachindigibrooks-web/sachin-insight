import React from 'react';
import {AbsoluteFill, Easing, Img, random, staticFile} from 'remotion';
import {B, C, clamp01, Dust, ease, Eye, Label, Leak, lerp, Line, Nebula, Photo, Ring, soft, Thought, TL, useT, W} from './lib';

/** Soft dissolve between scenes: fade + slight scale + blur, no hard whips (calm format). */
const Scene: React.FC<{id: string; children: React.ReactNode}> = ({id, children}) => {
	const t = useT();
	const sc = TL.scenes.find((s) => s.id === id)!;
	const D = 0.45;
	if (t < sc.s - D || t > sc.e + D) return null;
	const enter = ease(t, sc.s - D, D * 2, Easing.inOut(Easing.cubic));
	const exit = ease(t, sc.e - D * 0.5, D, Easing.in(Easing.cubic));
	return (
		<AbsoluteFill style={{opacity: enter * (1 - exit), transform: `scale(${lerp(1.06, 1, enter) * lerp(1, 0.97, exit)})`,
			filter: enter < 0.99 || exit > 0.01 ? `blur(${(1 - enter) * 14 + exit * 10}px)` : undefined}}>
			{children}
		</AbsoluteFill>
	);
};

const Abs: React.FC<{x?: number; y: number; w?: number; style?: React.CSSProperties; children: React.ReactNode}> = ({x = 0, y, w = 1080, style, children}) => (
	<div style={{position: 'absolute', left: x, top: y, width: w, ...style}}>{children}</div>
);

const THOUGHTS = ['deadline', 'EMI', 'log kya kahenge?', 'kal ki meeting', 'notifications', 'kya main kaafi hoon?', 'past', 'future',
	'what if...', 'comparison', 'career', 'reels', 'exam', 'phone', 'galti', 'kal kya hoga?'];

/* 1. HOOK: overthinking chatter freezes, then the witness-eye opens */
const Hook = () => {
	const t = useT();
	const freeze = Math.min(t, B.abSocho + 0.15);
	const fade = 1 - ease(t, 4.9, 0.6);
	return (
		<Scene id="hook">
			<Photo src="broll/overthink.jpg" s={0} e={6.5} from={1.0} to={1.18} tone="indigo" dim={0.35}
				style={{filter: t > B.abSocho ? `grayscale(${ease(t, B.abSocho, 0.5)})` : undefined}} />
			{THOUGHTS.map((txt, i) => {
				const at = B.kitne + i * 0.13;
				if (t < at) return null;
				const ang = random(`a${i}`) * Math.PI * 2;
				const r0 = 180 + random(`r${i}`) * 300;
				const k = freeze - at;
				const x = 540 + Math.cos(ang + k * 0.5) * (r0 + k * 30);
				const y = 900 + Math.sin(ang + k * 0.5) * (r0 * 1.3 + k * 30) + Math.sin(k * 6 + i) * (t < B.abSocho ? 8 : 0);
				return <Thought key={i} text={txt} x={x} y={y} o={ease(t, at, 0.25) * fade * (t > B.abSocho ? 0.6 : 1)} scale={0.8 + random(`s${i}`) * 0.4} />;
			})}
			<Abs y={230}>
				<Line size={96} items={[['Ek', 0.0], ['second', 0.28], ['ruko...', 0.54, true]]} style={{opacity: 1 - ease(t, 4.7, 0.4)}} />
			</Abs>
			{t > 4.7 && (
				<>
					<Abs y={250}>
						<Line size={104} items={[['Inhe', 4.98], ['dekh', B.dekh, true], ['kaun', B.kaun], ['raha', 5.88], ['hai?', 6.08]]} />
					</Abs>
					<Eye at={B.dekh} cx={540} cy={930} w={560} />
					<Ring cx={540} cy={930} at={B.dekh + 0.6} max={520} />
				</>
			)}
		</Scene>
	);
};

/* 2. INTRO: freedom fighter -> yogi; the 1908 photograph */
const Intro = () => {
	const t = useT();
	const ph = soft(t, 6.6);
	return (
		<Scene id="intro">
			<Nebula />
			<Dust n={50} />
			<Abs y={170}>
				<Label at={B.freedom} out={B.yogi - 0.1} style={{fontSize: 44}}>Freedom Fighter</Label>
			</Abs>
			<Abs y={170}>
				<Label at={B.yogi} style={{fontSize: 44}}>Freedom Fighter  →  Yogi</Label>
			</Abs>
			<div style={{position: 'absolute', left: 290, top: 300, width: 500, height: 750, transform: `translateY(${(1 - ph) * 60}px)`, opacity: ph}}>
				<div style={{position: 'absolute', inset: -18, border: `2px solid ${C.gold}`, borderRadius: '250px 250px 14px 14px', opacity: 0.8}} />
				<div style={{position: 'absolute', inset: 0, borderRadius: '240px 240px 8px 8px', overflow: 'hidden', boxShadow: '0 30px 60px rgba(0,0,0,.6)'}}>
					<Img src={staticFile('photo/front.jpg')} style={{width: '100%', height: '100%', objectFit: 'cover', objectPosition: '50% 20%',
						filter: 'grayscale(1) sepia(.5) contrast(1.1) brightness(.95)', transform: `scale(${lerp(1.1, 1.0, ease(t, 6.6, 5, Easing.linear))})`}} />
					<AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(233,180,76,.12), rgba(13,17,48,.45))', mixBlendMode: 'multiply'}} />
				</div>
			</div>
			<Abs y={1110}>
				<Line size={120} items={[['Sri', B.sri], ['Aurobindo', 8.56, true]]} />
				<Label at={9.0} style={{marginTop: 18, fontSize: 34}}>1872 – 1950</Label>
			</Abs>
			{t > B.chaabi - 0.1 && (
				<svg width={140} height={70} viewBox="0 0 140 70" style={{position: 'absolute', left: 470, top: 1360, overflow: 'visible', opacity: ease(t, B.chaabi, 0.4)}}>
					<circle cx={24} cy={35} r={20} fill="none" stroke={C.gold} strokeWidth={5} pathLength={1} strokeDasharray="1 1" strokeDashoffset={1 - ease(t, B.chaabi, 0.6)} />
					<path d="M44 35 H130 M110 35 V55 M124 35 V50" stroke={C.gold} strokeWidth={5} fill="none" pathLength={1} strokeDasharray="1 1" strokeDashoffset={1 - ease(t, B.chaabi + 0.2, 0.6)} />
				</svg>
			)}
			<Leak at={B.yogi} x={50} y={30} />
		</Scene>
	);
};

const STEPS = [
	{k: 'Matter', sub: 'padarth  ·  shareer', at: () => B.matter, y: 1330},
	{k: 'Life', sub: 'praan  ·  energy', at: () => B.life, y: 1090},
	{k: 'Mind', sub: 'vichaar  ·  thoughts', at: () => B.mind, y: 850},
	{k: 'Supermind', sub: 'satya-chetna  ·  direct knowing', at: () => B.supermind, y: 470},
];

/** The ladder of consciousness: steps light up as they are named; an orb climbs. */
const Ladder: React.FC<{shift?: number; superOn?: boolean; lowFade?: number}> = ({shift = 0, superOn, lowFade = 0}) => {
	const t = useT();
	const orbStep = t < B.life ? 0 : t < B.mind ? 1 : 2;
	const orbY = STEPS[orbStep].y - 34;
	const stuck = t > B.atke && t < B.par;
	const jitter = stuck ? Math.sin(t * 40) * 6 : 0;
	return (
		<div style={{position: 'absolute', inset: 0, transform: `translateY(${shift}px)`}}>
			<div style={{position: 'absolute', left: 538, top: STEPS[3].y, width: 3, height: STEPS[0].y - STEPS[3].y, background: `linear-gradient(${C.gold}00, ${C.gold}88)`}} />
			{STEPS.map((s, i) => {
				const isSuper = i === 3;
				const lit = isSuper ? (superOn ? ease(t, B.supermind, 0.6) : 0) : ease(t, s.at(), 0.5);
				const show = (isSuper ? ease(t, 12.9, 0.8) : ease(t, 12.9 + i * 0.15, 0.6)) * (i < 2 ? 1 - lowFade : i === 2 ? 1 - lowFade * 0.6 : 1);
				return (
					<div key={s.k} style={{position: 'absolute', left: 190, top: s.y, width: 700, opacity: show}}>
						<div style={{height: 3, background: lit > 0 ? C.gold : 'rgba(244,235,221,.25)', boxShadow: lit > 0 ? `0 0 ${24 * lit}px ${C.gold}` : undefined,
							borderTop: isSuper && !superOn ? '3px dashed rgba(244,235,221,.35)' : undefined, transform: `scaleX(${lerp(0.6, 1, show)})`}} />
						<div style={{position: 'absolute', left: 0, top: -96, fontFamily: 'Caps', fontWeight: 600, fontSize: isSuper ? 66 : 60, letterSpacing: '0.12em',
							color: lit > 0 ? (isSuper ? C.goldSoft : C.ivory) : 'rgba(244,235,221,.35)', textShadow: lit > 0 ? `0 0 ${30 * lit}px rgba(233,180,76,.6)` : undefined}}>
							{isSuper && !superOn ? 'Supermind ?' : s.k}
						</div>
						<div style={{position: 'absolute', right: 0, top: 14, fontFamily: 'Serif', fontStyle: 'italic', fontWeight: 500, fontSize: 36, color: C.ivory, opacity: 0.6 * Math.max(lit, isSuper ? 0 : 0.3)}}>{s.sub}</div>
						{lit > 0 && !isSuper && <Ring cx={350} cy={0} at={s.at()} max={380} width={2} />}
					</div>
				);
			})}
			{t > B.matter - 0.2 && !superOn && (
				<div style={{position: 'absolute', left: 540 - 34 + jitter, top: orbY - 40 + (t < B.matter ? 40 : 0), width: 68, height: 68, borderRadius: '50%',
					background: `radial-gradient(circle at 40% 35%, #fff, ${stuck ? C.coral : C.goldSoft} 45%, ${stuck ? C.coral : C.gold} 70%)`,
					boxShadow: `0 0 50px ${stuck ? C.coral : C.gold}`, transition: 'none', opacity: ease(t, B.matter - 0.2, 0.3)}} />
			)}
			{t > B.overthink - 0.1 && !superOn && ['kal?', 'kyun?', 'agar...', 'log', 'galti'].map((w, i) => {
				const a = t * 2.4 + i * 1.25;
				return <Thought key={w} text={w} x={540 + Math.cos(a) * 190} y={orbY + Math.sin(a) * 90} o={ease(t, B.overthink + i * 0.1, 0.3) * (1 - ease(t, B.par - 0.3, 0.3))} scale={0.75} />;
			})}
		</div>
	);
};

/* 3. LADDER: Matter -> Life -> Mind (stuck, overthinking) */
const LadderScene = () => (
	<Scene id="ladder">
		<Photo src="broll/stairs_pondy.jpg" s={11.6} e={21.3} from={1.2} to={1.05} tone="indigo" dim={0.62} />
		<Dust n={40} opacity={0.6} />
		<Abs y={140}>
			<Line size={84} items={[['Consciousness', B.consciousness, true]]} />
			<Line size={84} items={[['ek', 13.48], ['seedhi', B.seedhi, true], ['hai', 14.18]]} />
		</Abs>
		<Ladder />
	</Scene>
);

/* 4. SUPERMIND: the camera rises; the top step ignites; man is a transitional being */
const Super = () => {
	const t = useT();
	const rise = ease(t, B.upar - 0.2, 0.9, Easing.inOut(Easing.cubic));
	const burst = ease(t, B.supermind, 1.2);
	const part2 = t > B.insaan - 0.3;
	const p2 = ease(t, B.insaan - 0.3, 0.6);
	return (
		<Scene id="super">
			<Photo src="broll/milkyway.jpg" s={21.3} e={31.6} from={1.15} to={1.0} tone="indigo" dim={0.45} />
			<div style={{opacity: 1 - p2}}>
				<Ladder shift={lerp(0, 520, rise)} superOn={t > B.supermind} lowFade={ease(t, B.supermind + 0.4, 0.8)} />
				{t > B.supermind && (
					<div style={{position: 'absolute', left: 540, top: 470 + lerp(0, 520, rise), width: 0, height: 0}}>
						{Array.from({length: 18}, (_, i) => (
							<div key={i} style={{position: 'absolute', left: 0, top: 0, width: 900 * burst, height: 4, transformOrigin: '0 50%',
								transform: `rotate(${i * 20 + t * 6}deg)`, background: `linear-gradient(90deg, ${C.goldSoft}cc, rgba(233,180,76,0))`, opacity: 0.55}} />
						))}
					</div>
				)}
				<Abs y={170}>
					<Line size={78} items={[['Par', B.par], ['Mind', 21.74, true], ['aakhri', B.aakhri], ['step', 22.6], ['nahi', 22.78]]} style={{opacity: 1 - ease(t, B.supermind + 0.6, 0.4)}} />
				</Abs>
				{t > B.sochti - 0.3 && (
					<Abs y={150}>
						<div style={{position: 'relative', display: 'flex', justifyContent: 'center'}}>
							<Line size={80} items={[['chetna', 25.3], ['jo', 26.02], ['sochti', B.sochti], ['nahi...', 26.74]]} />
						</div>
						<div style={{position: 'absolute', left: 452, top: 46, width: 238 * ease(t, 26.5, 0.35), height: 5, background: C.gold, boxShadow: `0 0 14px ${C.gold}`}} />
						<Line size={96} items={[['seedha', 27.38], ['JAANTI', B.jaanti, true], ['hai', 28.28]]} style={{marginTop: 10}} />
					</Abs>
				)}
			</div>
			{part2 && (
				<AbsoluteFill style={{opacity: p2}}>
					<Photo src="broll/cosmos_man.jpg" s={28.5} e={31.6} from={1.08} to={1.0} tone="indigo" dim={0.3} />
					<Abs y={260}>
						<Line size={100} items={[['Insaan', B.insaan], ['final', 29.28], ['nahi', 29.66]]} />
						<Line size={110} items={[['transitional', B.transitional, true], ['being', 30.92, true]]} style={{marginTop: 14}} />
					</Abs>
					<div style={{position: 'absolute', left: 120, top: 1230, width: 840}}>
						<div style={{height: 3, background: 'rgba(244,235,221,.35)'}} />
						<div style={{height: 3, marginTop: -3, width: `${lerp(0, 66, ease(t, 29.0, 1.0))}%`, background: C.gold, boxShadow: `0 0 16px ${C.gold}`}} />
						{['Matter', 'Life', 'Mind', 'Supermind'].map((s, i) => (
							<div key={s} style={{position: 'absolute', left: `${i * 33.3}%`, top: -12, transform: 'translateX(-50%)', textAlign: 'center'}}>
								<div style={{width: 26, height: 26, borderRadius: '50%', margin: '0 auto', background: i < 3 ? C.gold : 'transparent', border: `3px solid ${C.gold}`,
									opacity: ease(t, 29.0 + i * 0.25, 0.3)}} />
								<div style={{fontFamily: 'Caps', fontSize: 30, color: C.ivory, marginTop: 14, letterSpacing: '0.1em', opacity: ease(t, 29.0 + i * 0.25, 0.3)}}>{s}</div>
							</div>
						))}
						<div style={{position: 'absolute', left: `${lerp(58, 72, ease(t, 30.3, 1.2, Easing.inOut(Easing.quad)))}%`, top: -110, transform: 'translateX(-50%)',
							fontFamily: 'Sans', fontWeight: 800, fontSize: 30, color: C.indigo, background: C.goldSoft, padding: '8px 18px', borderRadius: 30,
							opacity: ease(t, 29.7, 0.3), whiteSpace: 'nowrap'}}>aap yahan ho</div>
					</div>
				</AbsoluteFill>
			)}
			<Leak at={B.supermind} x={50} y={45} dur={1.4} />
		</Scene>
	);
};

/* 5. STORY 1908: "sit, don't think, watch the mind" -> thoughts thrown out -> silent in 3 days */
const Story = () => {
	const t = useT();
	const calm = ease(t, B.shaant - 0.2, 0.8);
	const tht = ['kal', 'darr', 'plan', 'yaadein', 'shor', 'chinta'];
	return (
		<Scene id="story">
			<Nebula />
			<Dust n={40} opacity={0.6} />
			<div style={{opacity: 1 - calm}}>
				<div style={{position: 'absolute', left: 80, top: 210, width: 330, height: 490, borderRadius: 10, overflow: 'hidden', boxShadow: '0 24px 50px rgba(0,0,0,.6)',
					border: `2px solid ${C.gold}88`, opacity: ease(t, 31.8, 0.6), transform: `rotate(-3deg) translateY(${(1 - ease(t, 31.8, 0.8)) * 40}px)`}}>
					<Img src={staticFile('photo/profile.jpg')} style={{width: '100%', height: '100%', objectFit: 'cover', filter: 'grayscale(1) sepia(.5) contrast(1.1)'}} />
				</div>
				<div style={{position: 'absolute', left: 470, top: 300, fontFamily: 'Serif', fontWeight: 700, fontSize: 230, color: C.gold,
					textShadow: '0 0 40px rgba(233,180,76,.45)', opacity: ease(t, B.y1908, 0.5)}}>
					{t < B.y1908 + 0.8 ? String(Math.round(lerp(1872, 1908, ease(t, B.y1908, 0.8)))) : '1908'}
				</div>
				<Label at={32.84} style={{position: 'absolute', left: 470, top: 560, textAlign: 'left', fontSize: 32}}>ek yogi ki salaah</Label>
				<div style={{position: 'absolute', left: 0, width: 1080, top: 820, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6,
					fontFamily: 'Serif', fontWeight: 700, fontSize: 110, color: C.ivory, textShadow: '0 6px 30px rgba(0,0,0,.6)'}}>
					<W at={B.baitho}>Baitho.</W>
					<W at={B.soChoMat}>Socho mat.</W>
					<W at={B.dekho - 0.6} gold>Bas dekho.</W>
				</div>
				{t > B.thoughts2 - 0.1 && tht.map((w, i) => {
					const ang = (i / tht.length) * Math.PI * 2 + 0.4;
					const fly = ease(t, B.phenk - 0.1 + i * 0.04, 0.5, Easing.in(Easing.cubic));
					const r = 360 + fly * 900;
					return <Thought key={w} text={w} x={540 + Math.cos(ang) * r} y={1010 + Math.sin(ang) * r * 0.9} o={ease(t, B.thoughts2 + i * 0.08, 0.25) * (1 - fly)} color={C.coral} />;
				})}
				<div style={{position: 'absolute', left: 0, width: 1080, top: 1290, display: 'flex', justifyContent: 'center', gap: 40, opacity: ease(t, B.teen - 0.1, 0.3)}}>
					{[0, 1, 2].map((i) => {
						const on = ease(t, [B.teen, 40.24, 40.44][i], 0.25);
						return <div key={i} style={{width: 120, height: 120, borderRadius: '50%', border: `3px solid ${C.gold}`, background: `rgba(233,180,76,${0.85 * on})`,
							display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'Caps', fontSize: 44, color: on > 0.5 ? C.indigo : C.gold}}>{i + 1}</div>;
					})}
				</div>
			</div>
			{t > B.shaant - 0.3 && (
				<AbsoluteFill style={{opacity: calm}}>
					<Photo src="broll/lake.jpg" s={B.shaant - 0.3} e={42.2} from={1.08} to={1.0} tone="teal" dim={0.25} />
					{[0, 0.5, 1.0].map((d, i) => <Ring key={i} cx={540} cy={1180} at={B.shaant + d} dur={2.2} max={460} color={C.ivory} width={2} />)}
					<Abs y={560}><Line size={150} items={[['Shaant.', B.shaant, true]]} /></Abs>
				</AbsoluteFill>
			)}
		</Scene>
	);
};

/* 6. PRACTICE: one minute of watching; the watcher is you */
const Practice = () => {
	const t = useT();
	const toEye = ease(t, B.kyunki - 0.2, 0.7);
	const ring = ease(t, B.minute, 4.2, Easing.inOut(Easing.quad));
	return (
		<Scene id="practice">
			<Photo src="broll/meditate.jpg" s={42.2} e={46} from={1.12} to={1.0} tone="warm" dim={0.3} />
			<div style={{opacity: 1 - toEye}}>
				<Abs y={230}>
					<Line size={92} items={[['Aaj', B.aaj], ['bas', 42.54], ['ek', 42.94], ['minute', B.minute, true]]} />
					<Line size={84} items={[['apne', 43.9], ['thoughts', 44.22], ['ko', 44.6], ['dekho', 44.7, true]]} style={{marginTop: 8}} />
				</Abs>
				<svg width={420} height={420} viewBox="0 0 420 420" style={{position: 'absolute', left: 330, top: 760, transform: 'rotate(-90deg)', opacity: ease(t, B.minute, 0.4)}}>
					<circle cx={210} cy={210} r={190} fill="none" stroke="rgba(244,235,221,.25)" strokeWidth={6} />
					<circle cx={210} cy={210} r={190} fill="none" stroke={C.gold} strokeWidth={8} strokeLinecap="round" pathLength={1} strokeDasharray="1 1" strokeDashoffset={1 - ring}
						style={{filter: `drop-shadow(0 0 10px ${C.gold})`}} />
				</svg>
				<div style={{position: 'absolute', left: 330, top: 760, width: 420, height: 420, display: 'flex', alignItems: 'center', justifyContent: 'center',
					fontFamily: 'Caps', fontSize: 64, color: C.ivory, opacity: ease(t, B.minute, 0.4), transform: `scale(${1 + Math.sin(t * 1.6) * 0.03})`}}>1:00</div>
			</div>
			{t > B.kyunki - 0.3 && (
				<AbsoluteFill style={{opacity: toEye}}>
					<Photo src="broll/eye.jpg" s={B.kyunki - 0.3} e={48.5} from={1.0} to={1.35} tone="warm" dim={0.2} />
					<AbsoluteFill style={{background: 'radial-gradient(circle at 50% 50%, rgba(0,0,0,0) 30%, rgba(13,17,48,.75) 75%)'}} />
					<Abs y={260}>
						<Line size={86} items={[['Kyunki', B.kyunki], ['jo', 45.68], ['dekh', B.joDekh, true], ['raha', 46.28], ['hai...', 46.56]]} />
					</Abs>
					<Abs y={1150}>
						<Line size={150} items={[['Wahi', B.wahi], ['aap', B.aap, true], ['ho.', 47.84]]} />
					</Abs>
				</AbsoluteFill>
			)}
			<Leak at={B.wahi} x={50} y={60} />
		</Scene>
	);
};

/* 7. END: All life is Yoga */
const End = () => {
	const t = useT();
	const out = ease(t, 52.4, 1.0);
	return (
		<Scene id="end">
			<Photo src="broll/lotus.jpg" s={48.4} e={53.5} from={1.12} to={1.0} tone="indigo" dim={0.35} />
			<Dust n={60} />
			<Abs y={520}>
				<div style={{fontFamily: 'Serif', fontStyle: 'italic', fontWeight: 500, fontSize: 150, color: C.ivory, textAlign: 'center', lineHeight: 1.0, textShadow: '0 6px 34px rgba(0,0,0,.6)'}}>
					<W at={B.all}>All</W> <W at={48.88}>life</W><br /><W at={49.36}>is</W> <W at={B.yoga} gold>Yoga.</W>
				</div>
				<Label at={49.9} style={{marginTop: 40, fontSize: 38}}>— Sri Aurobindo</Label>
			</Abs>
			<div style={{position: 'absolute', left: 340, top: 1190, width: 400, height: 110, borderRadius: 60, border: `3px solid ${C.gold}`, display: 'flex',
				alignItems: 'center', justifyContent: 'center', fontFamily: 'Caps', fontSize: 46, letterSpacing: '0.2em', color: C.gold,
				opacity: ease(t, B.follow, 0.5), transform: `scale(${0.9 + 0.1 * soft(t, B.follow)})`, background: `rgba(13,17,48,${0.4 + 0.3 * Math.abs(Math.sin(t * 2))})`}}>Follow</div>
			<AbsoluteFill style={{background: C.indigo, opacity: out}} />
		</Scene>
	);
};

export const Scenes = () => (
	<>
		<Hook /><Intro /><LadderScene /><Super /><Story /><Practice /><End />
	</>
);
