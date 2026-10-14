import React from 'react';
import {AbsoluteFill, Easing, random} from 'remotion';
import {antic, B, Big, Burn, C, clamp01, Clip, ease, Hand, lerp, LowerThird, Mark, Print, rgbSplit, scribble, spr, useT} from './lib';

const In: React.FC<{s: number; e: number; children: React.ReactNode}> = ({s, e, children}) => {
	const t = useT();
	return t >= s && t < e ? <>{children}</> : null;
};
const Abs: React.FC<{y: number; x?: number; w?: number; style?: React.CSSProperties; children: React.ReactNode}> = ({y, x = 0, w = 1080, style, children}) => (
	<div style={{position: 'absolute', left: x, top: y, width: w, ...style}}>{children}</div>
);

/** Punch-in zoom on a cut (camera "push" accent). */
const Punch: React.FC<{at: number; amt?: number; children: React.ReactNode}> = ({at, amt = 0.08, children}) => {
	const t = useT();
	const k = t < at ? 0 : Math.exp(-(t - at) * 7);
	return <AbsoluteFill style={{transform: `scale(${1 + amt * k})`}}>{children}</AbsoluteFill>;
};

const NOISE = ['EMI', 'log kya kahenge?', 'deadline', 'kal ka kya?', 'galti ho gayi', 'phone check karo', 'exam', 'career', 'kya main kaafi hoon?', 'meeting', 'past', 'future'];

/* ---------- 1. HOOK ---------- */
const Hook = () => {
	const t = useT();
	const montage = ['v/crowd.mp4', 'v/timer.mp4', 'v/rubeyes.mp4', 'v/rainnight.mp4'];
	const cutLen = (B.abSocho - B.kitne) / montage.length;
	const frozen = t >= B.abSocho && t < 4.95;
	const shake = t > B.kitne && t < B.abSocho ? Math.sin(t * 61) * 6 : 0;
	return (
		<>
			<In s={0} e={B.kitne}>
				<Clip src="v/worried.mp4" at={0} until={B.kitne} grade="cool" push={[1.02, 1.12]} />
				<Abs y={250}><Big size={170} items={[['Ek', 0.02], ['second', 0.28], ['ruko...', 0.54, 'serif']]} /></Abs>
			</In>
			<In s={B.kitne} e={4.95}>
				<AbsoluteFill style={{transform: `translate(${shake}px, ${shake * 0.6}px)`, filter: frozen ? `grayscale(${ease(t, B.abSocho, 0.3)}) contrast(1.2)` : rgbSplit(6)}}>
					{montage.map((m, i) => {
						const s = B.kitne + i * cutLen;
						const e = i === montage.length - 1 ? 4.95 : s + cutLen;
						// freeze: hold the montage on its last frame by stopping the clip's clock
						return frozen ? (i === montage.length - 1 ? <Clip key={m} src={m} at={s} until={e} rate={0.02} grade="night" push={[1.1, 1.1]} /> : null)
							: t >= s && t < e ? <Punch key={m} at={s} amt={0.1}><Clip src={m} at={s} until={e} grade="night" push={[1.06, 1.12]} /></Punch> : null;
					})}
				</AbsoluteFill>
				{NOISE.map((w, i) => {
					const at = B.kitne + i * 0.11;
					if (t < at) return null;
					const x = 120 + random(`nx${i}`) * 800;
					const y = 330 + random(`ny${i}`) * 1050;
					return <Hand key={w} at={at} dur={0.18} size={44 + random(`ns${i}`) * 30} rot={(random(`nr${i}`) - 0.5) * 24} color={i % 3 === 0 ? C.coral : C.ivory}
						style={{left: x - 150, top: y, opacity: frozen ? 0.35 : 1}}>{w}</Hand>;
				})}
				<Abs y={250}><Big size={150} items={[['Kitne', B.kitne], ['thoughts?', B.thoughts, 'coral']]} /></Abs>
				{frozen && <Abs y={820}><Big size={190} items={[['Ab', B.abSocho], ['socho...', 4.12, 'serif']]} /></Abs>}
			</In>
			<In s={4.95} e={6.62}>
				<Clip src="v/eye.mp4" at={4.95} until={6.6} grade="warm" push={[1.0, 1.25]} dim={0.15} />
				<Mark at={B.dekh + 0.1} dur={0.5} width={10} d={scribble('eye', 520, 980, 330, 230)} />
				<Abs y={240}><Big size={130} items={[['Inhe', 4.98], ['dekh', B.dekh], ['kaun', B.kaun, 'gold'], ['raha', 5.88], ['hai?', 6.08]]} /></Abs>
			</In>
		</>
	);
};

/* ---------- 2. INTRO ---------- */
const Intro = () => {
	const t = useT();
	return (
		<In s={6.5} e={11.62}>
			<Clip src="v/flag.mp4" at={6.5} until={8.0} grade="warm" push={[1.05, 1.15]} dim={0.4} />
			{t > 7.5 && <Clip src="v/candle.mp4" at={7.5} until={11.6} grade="gold" push={[1.0, 1.1]} dim={0.15} style={{opacity: ease(t, 7.5, 0.5)}} />}
			<Abs y={220} style={{opacity: 1 - ease(t, B.yogi - 0.1, 0.25)}}><Big size={140} items={[['Freedom', B.freedom], ['fighter', 7.02]]} /></Abs>
			<Abs y={220} style={{opacity: ease(t, B.yogi - 0.05, 0.2)}}>
				<Big size={110} items={[['Freedom fighter', B.yogi - 0.05]]} />
				<Big size={150} items={[['se', B.yogi, 'serif'], ['YOGI', B.yogi + 0.1, 'gold']]} />
			</Abs>
			<Mark at={B.yogi + 0.15} dur={0.3} width={10} d="M260 300 L820 280" style={{opacity: 0.9}} />
			<Print src="photo/front.jpg" at={B.yogi + 0.25} x={300} y={600} w={480} h={560} rot={-4} caption="Alipore, 1908" />
			<LowerThird at={B.sri} out={11.3} name="SRI AUROBINDO" sub="1872 – 1950  ·  Philosopher · Yogi" y={1330} />
			<Hand at={B.chaabi} size={50} rot={7} style={{left: 590, top: 540}}>yahi sawaal = chaabi</Hand>
			<Burn at={B.yogi + 0.1} x={60} />
		</In>
	);
};

const STEPS: [string, string, number, string][] = [
	['MATTER', 'padarth · shareer', 0, 'v/mountain.mp4'],
	['LIFE', 'praan · energy', 1, 'v/forest.mp4'],
	['MIND', 'vichaar · thoughts', 2, 'v/rainnight.mp4'],
];

/** Mini ladder infographic on the left edge: rungs fill as each level is named. */
const MiniLadder: React.FC<{active: number; superLit?: number; show: number}> = ({active, superLit = 0, show}) => {
	const labels = ['MATTER', 'LIFE', 'MIND', 'SUPERMIND'];
	return (
		<div style={{position: 'absolute', left: 60, top: 520, width: 230, height: 760, opacity: show}}>
			<div style={{position: 'absolute', left: 18, top: 0, width: 4, height: 760, background: 'rgba(246,239,227,.5)'}} />
			<div style={{position: 'absolute', left: 120, top: 0, width: 4, height: 760, background: 'rgba(246,239,227,.5)'}} />
			{labels.map((l, i) => {
				const y = 700 - i * 220;
				const on = i === 3 ? superLit : i <= active ? 1 : 0;
				const cur = i === active && i < 3;
				return (
					<div key={l} style={{position: 'absolute', left: 18, top: y, width: 106, height: 6, background: on ? C.gold : 'rgba(246,239,227,.35)',
						boxShadow: on ? `0 0 18px ${C.gold}` : undefined}}>
						<div style={{position: 'absolute', left: 124, top: -22, fontFamily: 'Display', fontSize: i === 3 ? 34 : 38, color: on ? (cur ? C.marker : C.ivory) : 'rgba(246,239,227,.45)',
							letterSpacing: 2, whiteSpace: 'nowrap'}}>{l}</div>
					</div>
				);
			})}
		</div>
	);
};

/* ---------- 3. LADDER ---------- */
const Ladder = () => {
	const t = useT();
	const active = t < B.life ? 0 : t < B.mind ? 1 : 2;
	const lad = ease(t, 12.6, 0.6);
	const draw = ease(t, 12.9, 1.2, Easing.inOut(Easing.cubic));
	return (
		<In s={11.6} e={21.44}>
			{t < B.matter - 0.05 && (
				<>
					<Clip src="v/stars.mp4" at={11.6} until={B.matter} grade="cool" push={[1.1, 1.2]} dim={0.45} />
					<Abs y={300}>
						<Big size={120} items={[['Consciousness', B.consciousness, 'gold']]} />
						<Big size={160} items={[['ek', 13.48], ['seedhi', B.seedhi], ['hai', 14.18]]} />
					</Abs>
					<svg width={1080} height={1920} style={{position: 'absolute', left: 0, top: 0}}>
						{[0, 1].map((k) => <line key={k} x1={400 + k * 280} y1={1500} x2={400 + k * 280} y2={1500 - 620 * draw} stroke={C.ivory} strokeWidth={6} />)}
						{[0, 1, 2, 3].map((k) => <line key={k} x1={400} x2={400 + 280 * ease(t, 13.2 + k * 0.18, 0.3)} y1={1440 - k * 160} y2={1440 - k * 160} stroke={C.gold} strokeWidth={8} />)}
					</svg>
				</>
			)}
			{t >= B.matter - 0.05 && STEPS.map(([name, sub, i, src]) => {
				const s = [B.matter, B.life, B.mind][i] - 0.05;
				const e = i < 2 ? [B.life, B.mind][i] - 0.05 : 21.44;
				if (t < s || t >= e) return null;
				return (
					<Punch key={name} at={s} amt={0.06}>
						<Clip src={src} at={s} until={e} grade={i === 2 ? 'night' : 'warm'} push={[1.04, 1.12]} dim={i === 2 ? 0.45 : 0.3}
							style={i === 2 ? {filter: 'blur(6px)'} : undefined} />
						{i === 2 && (
							<AbsoluteFill style={{transform: `translateY(${lerp(80, 0, ease(t, s, 0.6))}px)`}}>
								<Clip src="v/pensive.webm" transparent at={s} until={e} grade="warm" push={[1.0, 1.04]} style={{top: 420, left: 140, width: 900, height: 1500}} />
							</AbsoluteFill>
						)}
						<Abs y={230} x={330} w={700}>
							<Big size={180} align="left" items={[[name, s + 0.05, i === 2 ? 'coral' : undefined]]} />
						</Abs>
						<Hand at={s + 0.3} size={52} color={C.ivory} rot={-3} style={{left: 340, top: 450}}>({sub})</Hand>
					</Punch>
				);
			})}
			<MiniLadder active={active} show={t >= B.matter - 0.05 ? lad : 0} />
			{t > B.atke && (
				<>
					<Hand at={B.atke} size={66} rot={-8} style={{left: 560, top: 640}}>yahin atke hain!</Hand>
					<Mark at={B.atke + 0.3} dur={0.35} d="M760 720 C 760 790, 720 830, 660 850 M660 850 L700 815 M660 850 L705 868" width={8} />
				</>
			)}
			{t > B.overthink - 0.1 && ['kal?', 'kyun?', 'agar...', 'log', 'galti', 'EMI'].map((w, i) => {
				const a = t * 2.2 + i * 1.05;
				return <Hand key={w} at={B.overthink + i * 0.08} dur={0.2} size={48} color={i % 2 ? C.coral : C.ivory} rot={Math.sin(a) * 10}
					style={{left: 600 + Math.cos(a) * 260 - 60, top: 930 + Math.sin(a) * 140}}>{w}</Hand>;
			})}
			<Burn at={B.matter - 0.05} x={30} dur={0.5} />
		</In>
	);
};

/* ---------- 4. SUPERMIND ---------- */
const Super = () => {
	const t = useT();
	const burst = ease(t, B.supermind, 0.9);
	return (
		<In s={21.44} e={31.7}>
			<In s={21.44} e={B.supermind}>
				<Clip src="v/nebula.mp4" at={21.44} until={B.supermind} grade="cool" push={[1.0, 1.5]} dim={0.4} />
				<Abs y={360}><Big size={130} items={[['Par', B.par], ['MIND', 21.74, 'coral'], ['aakhri', B.aakhri], ['step', 22.6], ['nahi', 22.78]]} /></Abs>
				<Mark at={22.85} dur={0.3} d="M180 650 L900 610" width={12} color={C.coral} />
				<Hand at={B.upar} size={80} rot={-4} style={{left: 360, top: 980}}>upar dekho ↑</Hand>
			</In>
			<In s={B.supermind} e={28.6}>
				<Punch at={B.supermind} amt={0.12}>
					<Clip src="v/sunclouds.mp4" at={B.supermind} until={28.6} grade="gold" push={[1.15, 1.0]} dim={0.15} />
				</Punch>
				<AbsoluteFill style={{background: `radial-gradient(circle at 50% 42%, rgba(255,240,200,${0.7 * (1 - burst)}) 0%, rgba(0,0,0,0) 60%)`, mixBlendMode: 'screen'}} />
				<Abs y={360}><Big size={140} items={[['SUPERMIND', B.supermind, 'gold']]} /></Abs>
				<Abs y={660}>
					<Big size={96} items={[['chetna', 25.3], ['jo', 26.02], ['sochti', B.sochti], ['nahi...', 26.74]]} />
				</Abs>
				<Mark at={26.5} dur={0.3} d="M505 740 L845 732" width={10} color={C.coral} />
				<Abs y={830}><Big size={150} items={[['seedha', 27.38, 'serif'], ['JAANTI', B.jaanti, 'gold'], ['hai', 28.28]]} /></Abs>
			</In>
			<In s={28.6} e={31.7}>
				<Clip src="v/dusk.mp4" at={28.6} until={31.7} grade="warm" push={[1.05, 1.15]} dim={0.3} />
				<Abs y={250}>
					<Big size={140} items={[['Insaan', B.insaan], ['final', 29.28], ['nahi', 29.66, 'coral']]} />
					<Big size={120} items={[['transitional', B.transitional, 'gold'], ['being', 30.92, 'serif']]} />
				</Abs>
				<div style={{position: 'absolute', left: 110, top: 1240, width: 860, opacity: ease(t, 29.0, 0.4)}}>
					<div style={{height: 5, background: 'rgba(246,239,227,.4)'}} />
					<div style={{height: 5, marginTop: -5, width: `${lerp(0, 67, ease(t, 29.0, 1.0))}%`, background: C.gold}} />
					{['MATTER', 'LIFE', 'MIND', 'SUPERMIND'].map((s, i) => (
						<div key={s} style={{position: 'absolute', left: `${i * 33.3}%`, top: -13, transform: 'translateX(-50%)', textAlign: 'center'}}>
							<div style={{width: 30, height: 30, borderRadius: '50%', margin: '0 auto', background: i < 3 ? C.gold : C.ink, border: `4px solid ${C.gold}`}} />
							<div style={{fontFamily: 'Display', fontSize: 34, color: C.ivory, marginTop: 12, letterSpacing: 2}}>{s}</div>
						</div>
					))}
				</div>
				<Hand at={29.9} size={58} rot={-6} style={{left: 520, top: 1100}}>aap yahan ho</Hand>
				<Mark at={30.3} dur={0.35} d="M640 1170 C 650 1200, 660 1210, 672 1222 M672 1222 L640 1210 M672 1222 L668 1188" width={7} />
			</In>
			<Burn at={B.supermind} x={50} dur={1.0} />
		</In>
	);
};

/* ---------- 5. STORY 1908 ---------- */
const Story = () => {
	const t = useT();
	const tally = [B.teen, 40.24, 40.44];
	return (
		<In s={31.7} e={42.25}>
			<In s={31.7} e={B.baitho - 0.1}>
				<Clip src="v/smoke.mp4" at={31.7} until={B.baitho} grade="mono" push={[1.0, 1.1]} dim={0.3} />
				<Print src="photo/profile.jpg" at={31.9} x={80} y={420} w={430} h={540} rot={-5} caption="1908" />
				<Abs y={470} x={540} w={500}>
					<div style={{fontFamily: 'Display', fontSize: 210, color: C.gold, lineHeight: 1, transform: `scale(${0.9 + 0.1 * spr(t, B.y1908)})`, opacity: ease(t, B.y1908, 0.3)}}>
						{t < B.y1908 + 0.7 ? String(Math.round(lerp(1872, 1908, ease(t, B.y1908, 0.7)))) : '1908'}
					</div>
				</Abs>
				<Hand at={32.84} size={56} color={C.ivory} rot={-3} style={{left: 560, top: 730}}>ek yogi ne kaha...</Hand>
			</In>
			<In s={B.baitho - 0.1} e={B.shaant - 0.1}>
				<Clip src="v/candle.mp4" at={B.baitho - 0.1} until={B.shaant} trim={2} grade="gold" push={[1.08, 1.2]} dim={0.25} />
				<div style={{position: 'absolute', left: 0, width: 1080, top: 300}}>
					<Big size={170} items={[['Baitho.', B.baitho]]} />
					<Big size={170} items={[['Socho', B.soChoMat], ['mat.', 35.64, 'coral']]} />
					<Big size={170} items={[['Bas', B.dekho - 0.6, 'serif'], ['dekho.', B.dekho - 0.35, 'gold']]} />
				</div>
				{t > B.thoughts2 - 0.1 && ['kal', 'darr', 'plan', 'yaadein', 'shor', 'chinta', 'EMI'].map((w, i) => {
					const ang = (i / 7) * Math.PI * 2 + 0.3;
					const fly = ease(t, B.phenk - 0.1 + i * 0.03, 0.55, Easing.in(Easing.cubic));
					const r = 300 + fly * 1100;
					return <Hand key={w} at={B.thoughts2 + i * 0.07} dur={0.2} size={56} color={i % 2 ? C.coral : C.ivory} rot={(random(`st${i}`) - 0.5) * 20}
						style={{left: 470 + Math.cos(ang) * r, top: 1080 + Math.sin(ang) * r * 0.6, opacity: 1 - fly, filter: fly > 0.05 ? `blur(${fly * 12}px)` : undefined}}>{w}</Hand>;
				})}
				{t > B.teen - 0.1 && (
					<div style={{position: 'absolute', left: 300, top: 1180, width: 480, opacity: ease(t, B.teen - 0.1, 0.2)}}>
						<div style={{fontFamily: 'Display', fontSize: 64, color: C.ivory, letterSpacing: 3}}>TEEN DIN</div>
						<svg width={480} height={140} viewBox="0 0 480 140">
							{tally.map((a, i) => (
								<path key={i} d={`M${40 + i * 70} 20 L${46 + i * 70} 125`} stroke={C.marker} strokeWidth={12} strokeLinecap="round" pathLength={1}
									strokeDasharray="1 1" strokeDashoffset={1 - ease(t, a, 0.18)} style={{filter: 'url(#rough)'}} />
							))}
						</svg>
					</div>
				)}
			</In>
			<In s={B.shaant - 0.1} e={42.25}>
				<Clip src="v/ripples.mp4" at={B.shaant - 0.1} until={42.3} trim={4} grade="night" push={[1.0, 1.06]} dim={0.3} />
				<Abs y={520}><Big size={200} items={[['Shaant.', B.shaant, 'serif']]} /></Abs>
			</In>
		</In>
	);
};

/* ---------- 6. PRACTICE ---------- */
const Practice = () => {
	const t = useT();
	const ring = ease(t, B.minute, 2.4, Easing.inOut(Easing.quad));
	return (
		<In s={42.25} e={48.5}>
			<In s={42.25} e={B.kyunki - 0.05}>
				<Clip src="v/meditate.mp4" at={42.25} until={B.kyunki} grade="gold" push={[1.04, 1.14]} dim={0.25} />
				<Abs y={260}>
					<Big size={130} items={[['Aaj', B.aaj], ['bas', 42.54], ['ek', 42.94], ['minute', B.minute, 'gold']]} />
					<Big size={100} items={[['apne', 43.9, 'serif'], ['thoughts', 44.22], ['ko', 44.6, 'serif'], ['dekho', 44.7, 'gold']]} />
				</Abs>
				<svg width={300} height={300} viewBox="0 0 300 300" style={{position: 'absolute', left: 390, top: 900, transform: 'rotate(-90deg)', opacity: ease(t, B.minute, 0.3)}}>
					<circle cx={150} cy={150} r={130} fill="none" stroke="rgba(246,239,227,.3)" strokeWidth={6} />
					<circle cx={150} cy={150} r={130} fill="none" stroke={C.gold} strokeWidth={8} strokeLinecap="round" pathLength={1} strokeDasharray="1 1" strokeDashoffset={1 - ring} />
				</svg>
				<div style={{position: 'absolute', left: 390, top: 900, width: 300, height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center',
					fontFamily: 'Display', fontSize: 72, color: C.ivory, opacity: ease(t, B.minute, 0.3)}}>1:00</div>
			</In>
			<In s={B.kyunki - 0.05} e={B.wahi - 0.1}>
				<Clip src="v/eye.mp4" at={B.kyunki - 0.05} until={B.wahi} trim={6} grade="warm" push={[1.1, 1.6]} dim={0.15} />
				<Abs y={260}><Big size={120} items={[['Kyunki', B.kyunki], ['jo', 45.68], ['dekh', B.joDekh, 'gold'], ['raha', 46.28], ['hai...', 46.56, 'serif']]} /></Abs>
			</In>
			<In s={B.wahi - 0.1} e={48.5}>
				<Punch at={B.wahi - 0.1} amt={0.1}><Clip src="v/sunrise.mp4" at={B.wahi - 0.1} until={48.5} grade="gold" push={[1.05, 1.15]} dim={0.15} /></Punch>
				<Abs y={640}><Big size={210} items={[['Wahi', B.wahi], ['aap', B.aap, 'gold'], ['ho.', 47.84, 'serif']]} /></Abs>
			</In>
			<Burn at={B.wahi - 0.1} x={45} dur={0.8} />
		</In>
	);
};

/* ---------- 7. END ---------- */
const End = () => {
	const t = useT();
	const out = ease(t, 52.5, 0.9);
	return (
		<In s={48.5} e={53.6}>
			<Clip src="v/lotus.mp4" at={48.5} until={53.5} grade="warm" push={[1.05, 1.15]} dim={0.3} />
			<Abs y={480}>
				<Big size={170} items={[['All', B.all, 'serif'], ['life', 48.88, 'serif']]} />
				<Big size={170} items={[['is', 49.36, 'serif'], ['Yoga.', B.yoga, 'gold']]} />
			</Abs>
			<Hand at={50.0} size={56} color={C.ivory} rot={-3} style={{left: 560, top: 880}}>— Sri Aurobindo</Hand>
			<div style={{position: 'absolute', left: 360, top: 1150, width: 360, height: 104, borderRadius: 52, background: C.gold, display: 'flex', alignItems: 'center',
				justifyContent: 'center', fontFamily: 'Display', fontSize: 52, color: C.ink, letterSpacing: 3, transform: `scale(${spr(t, B.follow)})`,
				boxShadow: '0 12px 30px rgba(0,0,0,.4)'}}>FOLLOW</div>
			<AbsoluteFill style={{background: C.ink, opacity: out}} />
		</In>
	);
};

export const Scenes = () => (
	<>
		<Hook /><Intro /><Ladder /><Super /><Story /><Practice /><End />
	</>
);
