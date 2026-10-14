import React from 'react';
import {AbsoluteFill, Easing, random} from 'remotion';
import {B, Big, Burn, C, Clip, DUR, ease, Hand, lerp, LowerThird, Mark, Print, rgbSplit, SC, scribble, spr, useT, W} from './lib';

/* English cut. Same structure and footage as the Hinglish v2, but every cue is read from the English voice (W = word start),
   and nothing important sits in TikTok's bottom 470 px (caption/description) or the right-hand icon column. */

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

const NOISE = ['rent', 'what will they think?', 'deadline', 'what if...?', 'that mistake', 'check your phone', 'exams', 'career', 'am I enough?', 'meetings', 'the past', 'the future'];

// scene anchors
const EYE = B.kaun - 0.08; // "who is watching them?"
const STORY = SC.story.s;
const PRACT = SC.practice.s;
const END = SC.end.s;

/* ---------- 1. HOOK ---------- */
const Hook = () => {
	const t = useT();
	const montage = ['v/crowd.mp4', 'v/timer.mp4', 'v/rubeyes.mp4', 'v/rainnight.mp4'];
	const cutLen = (B.abSocho - B.kitne) / montage.length;
	const frozen = t >= B.abSocho && t < EYE;
	const shake = t > B.kitne && t < B.abSocho ? Math.sin(t * 61) * 6 : 0;
	return (
		<>
			<In s={0} e={B.kitne}>
				<Clip src="v/worried.mp4" at={0} until={B.kitne} grade="cool" push={[1.02, 1.12]} />
				<Abs y={260}>
					<Big size={190} items={[['Wait.', W('Wait'), 'gold']]} />
					<Big size={130} items={[['Stop', W('Stop')], ['for', W('for')]]} />
					<Big size={130} items={[['one', W('one')], ['second.', W('second'), 'serif']]} />
				</Abs>
			</In>
			<In s={B.kitne} e={EYE}>
				<AbsoluteFill style={{transform: `translate(${shake}px, ${shake * 0.6}px)`, filter: frozen ? `grayscale(${ease(t, B.abSocho, 0.3)}) contrast(1.2)` : rgbSplit(6)}}>
					{montage.map((m, i) => {
						const s = B.kitne + i * cutLen;
						const e = i === montage.length - 1 ? EYE : s + cutLen;
						return frozen ? (i === montage.length - 1 ? <Clip key={m} src={m} at={s} until={e} rate={0.02} grade="night" push={[1.1, 1.1]} /> : null)
							: t >= s && t < e ? <Punch key={m} at={s} amt={0.1}><Clip src={m} at={s} until={e} grade="night" push={[1.06, 1.12]} /></Punch> : null;
					})}
				</AbsoluteFill>
				{NOISE.map((w, i) => {
					const at = B.kitne + i * ((B.abSocho - B.kitne) / NOISE.length);
					if (t < at) return null;
					const x = 120 + random(`nx${i}`) * 700;
					const y = 560 + random(`ny${i}`) * 800;
					return <Hand key={w} at={at} dur={0.18} size={44 + random(`ns${i}`) * 26} rot={(random(`nr${i}`) - 0.5) * 24} color={i % 3 === 0 ? C.coral : C.ivory}
						style={{left: x - 150, top: y, opacity: frozen ? 0.35 : 1}}>{w}</Hand>;
				})}
				<Abs y={250}><Big size={150} items={[['How many', B.kitne], ['thoughts?', B.thoughts, 'coral']]} /></Abs>
				{frozen && <Abs y={820}><Big size={170} items={[['Now', B.abSocho], ['ask', W('ask'), 'serif'], ['yourself...', W('yourself'), 'serif']]} /></Abs>}
			</In>
			<In s={EYE} e={SC.intro.s}>
				<Clip src="v/eye.mp4" at={EYE} until={SC.intro.s} grade="warm" push={[1.0, 1.25]} dim={0.15} />
				<Mark at={B.dekh + 0.1} dur={0.5} width={10} d={scribble('eye', 520, 980, 330, 230)} />
				<Abs y={240}><Big size={140} items={[['Who', B.kaun, 'gold'], ['is', W('is', B.kaun)], ['watching', B.dekh], ['them?', W('them'), 'serif']]} /></Abs>
			</In>
		</>
	);
};

/* ---------- 2. INTRO ---------- */
const Intro = () => {
	const t = useT();
	const s = SC.intro.s, e = SC.ladder.s;
	return (
		<In s={s} e={e}>
			<Clip src="v/flag.mp4" at={s} until={B.yogi + 0.4} grade="warm" push={[1.05, 1.15]} dim={0.4} />
			{t > B.yogi - 0.4 && <Clip src="v/candle.mp4" at={B.yogi - 0.4} until={e} grade="gold" push={[1.0, 1.1]} dim={0.15} style={{opacity: ease(t, B.yogi - 0.4, 0.5)}} />}
			<Abs y={220} style={{opacity: 1 - ease(t, B.yogi - 0.1, 0.25)}}><Big size={140} items={[['Freedom', B.freedom], ['fighter', W('fighter')]]} /></Abs>
			<Abs y={220} style={{opacity: ease(t, B.yogi - 0.05, 0.2)}}>
				<Big size={110} items={[['Freedom fighter', B.yogi - 0.05]]} />
				<Big size={150} items={[['turned', B.yogi, 'serif'], ['YOGI', B.yogi + 0.1, 'gold']]} />
			</Abs>
			<Mark at={B.yogi + 0.15} dur={0.3} width={10} d="M260 300 L820 280" style={{opacity: 0.9}} />
			<Print src="photo/front.jpg" at={B.yogi + 0.25} x={300} y={600} w={480} h={560} rot={-4} caption="Alipore, 1908" />
			<LowerThird at={B.sri} out={e - 0.3} name="SRI AUROBINDO" sub="1872 – 1950  ·  Philosopher · Yogi" y={1190} />
			<Hand at={B.chaabi} size={52} rot={7} style={{left: 560, top: 540}}>this question = the key</Hand>
			<Burn at={B.yogi + 0.1} x={60} />
		</In>
	);
};

const STEPS: [string, string, number, string][] = [
	['MATTER', 'the body · the physical', 0, 'v/mountain.mp4'],
	['LIFE', 'breath · energy', 1, 'v/forest.mp4'],
	['MIND', 'thoughts · emotions', 2, 'v/rainnight.mp4'],
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
	const s0 = SC.ladder.s, e0 = B.par;
	const active = t < B.life ? 0 : t < B.mind ? 1 : 2;
	const lad = ease(t, B.matter - 0.1, 0.6);
	const draw = ease(t, B.consciousness + 0.2, 1.2, Easing.inOut(Easing.cubic));
	return (
		<In s={s0} e={e0}>
			{t < B.matter - 0.05 && (
				<>
					<Clip src="v/stars.mp4" at={s0} until={B.matter} grade="cool" push={[1.1, 1.2]} dim={0.45} />
					<Abs y={300}>
						<Big size={120} items={[['Consciousness', B.consciousness, 'gold']]} />
						<Big size={160} items={[['as a', W('as', B.consciousness)], ['ladder', B.seedhi, 'serif']]} />
					</Abs>
					<svg width={1080} height={1920} style={{position: 'absolute', left: 0, top: 0}}>
						{[0, 1].map((k) => <line key={k} x1={400 + k * 280} y1={1280} x2={400 + k * 280} y2={1280 - 600 * draw} stroke={C.ivory} strokeWidth={6} />)}
						{[0, 1, 2, 3].map((k) => <line key={k} x1={400} x2={400 + 280 * ease(t, B.consciousness + 0.5 + k * 0.18, 0.3)} y1={1220 - k * 150} y2={1220 - k * 150} stroke={C.gold} strokeWidth={8} />)}
					</svg>
				</>
			)}
			{t >= B.matter - 0.05 && STEPS.map(([name, sub, i, src]) => {
				const s = [B.matter, B.life, B.mind][i] - 0.05;
				const e = i < 2 ? [B.life, B.mind][i] - 0.05 : e0;
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
						<Hand at={s + 0.3} size={50} color={C.ivory} rot={-3} style={{left: 340, top: 450}}>({sub})</Hand>
					</Punch>
				);
			})}
			<MiniLadder active={active} show={t >= B.matter - 0.05 ? lad : 0} />
			{t > B.atke && (
				<>
					<Hand at={B.atke} size={66} rot={-8} style={{left: 520, top: 640}}>we get stuck here!</Hand>
					<Mark at={B.atke + 0.3} dur={0.35} d="M760 720 C 760 790, 720 830, 660 850 M660 850 L700 815 M660 850 L705 868" width={8} />
				</>
			)}
			{t > B.overthink - 0.1 && ['what if?', 'why?', 'tomorrow', 'they said', 'regret', 'bills'].map((w, i) => {
				const a = t * 2.2 + i * 1.05;
				return <Hand key={w} at={B.overthink + i * 0.08} dur={0.2} size={48} color={i % 2 ? C.coral : C.ivory} rot={Math.sin(a) * 10}
					style={{left: 560 + Math.cos(a) * 240 - 60, top: 930 + Math.sin(a) * 140}}>{w}</Hand>;
			})}
			<Burn at={B.matter - 0.05} x={30} dur={0.5} />
		</In>
	);
};

/* ---------- 4. SUPERMIND ---------- */
const Super = () => {
	const t = useT();
	const burst = ease(t, B.supermind, 0.9);
	const hum = B.insaan - 0.2;
	const think = W('think', B.supermind);
	return (
		<In s={B.par} e={STORY}>
			<In s={B.par} e={B.supermind}>
				<Clip src="v/nebula.mp4" at={B.par} until={B.supermind} grade="cool" push={[1.0, 1.5]} dim={0.4} />
				<Abs y={360}><Big size={130} items={[['But', B.par], ['MIND', W('Mind', B.par), 'coral'], ['is not', W('not', B.par)], ['the last', W('the', B.par)], ['step', W('step')]]} /></Abs>
				<Mark at={W('step') + 0.1} dur={0.3} d="M180 650 L900 610" width={12} color={C.coral} />
				<Hand at={B.upar} size={80} rot={-4} style={{left: 340, top: 980}}>look up ↑</Hand>
			</In>
			<In s={B.supermind} e={hum}>
				<Punch at={B.supermind} amt={0.12}>
					<Clip src="v/sunclouds.mp4" at={B.supermind} until={hum} grade="gold" push={[1.15, 1.0]} dim={0.15} />
				</Punch>
				<AbsoluteFill style={{background: `radial-gradient(circle at 50% 42%, rgba(255,240,200,${0.7 * (1 - burst)}) 0%, rgba(0,0,0,0) 60%)`, mixBlendMode: 'screen'}} />
				<Abs y={360}><Big size={140} items={[['SUPERMIND', B.supermind, 'gold']]} /></Abs>
				<Abs y={660}>
					<Big size={84} items={[['a consciousness', W('consciousness', B.supermind)]]} />
					<Big size={100} items={[['that doesn\'t', W("doesn't")], ['think...', think]]} />
				</Abs>
				<Mark at={think + 0.3} dur={0.3} d="M600 880 L940 872" width={10} color={C.coral} />
				<Abs y={920}><Big size={150} items={[['it simply', W('simply'), 'serif'], ['KNOWS', B.jaanti, 'gold']]} /></Abs>
			</In>
			<In s={hum} e={STORY}>
				<Clip src="v/dusk.mp4" at={hum} until={STORY} grade="warm" push={[1.05, 1.15]} dim={0.3} />
				<Abs y={250}>
					<Big size={130} items={[['Humans', B.insaan], ['are not', W('not', B.insaan)], ['final', W('final'), 'coral']]} />
					<Big size={110} items={[['transitional', B.transitional, 'gold']]} />
					<Big size={110} items={[['beings', W('beings'), 'serif']]} />
				</Abs>
				<div style={{position: 'absolute', left: 110, top: 1180, width: 860, opacity: ease(t, B.insaan + 0.2, 0.4)}}>
					<div style={{height: 5, background: 'rgba(246,239,227,.4)'}} />
					<div style={{height: 5, marginTop: -5, width: `${lerp(0, 67, ease(t, B.insaan + 0.2, 1.0))}%`, background: C.gold}} />
					{['MATTER', 'LIFE', 'MIND', 'SUPERMIND'].map((s, i) => (
						<div key={s} style={{position: 'absolute', left: `${i * 33.3}%`, top: -13, transform: 'translateX(-50%)', textAlign: 'center'}}>
							<div style={{width: 30, height: 30, borderRadius: '50%', margin: '0 auto', background: i < 3 ? C.gold : C.ink, border: `4px solid ${C.gold}`}} />
							<div style={{fontFamily: 'Display', fontSize: 34, color: C.ivory, marginTop: 12, letterSpacing: 2}}>{s}</div>
						</div>
					))}
				</div>
				<Hand at={B.transitional - 0.3} size={58} rot={-6} style={{left: 500, top: 1040}}>you are here</Hand>
				<Mark at={B.transitional + 0.1} dur={0.35} d="M640 1110 C 650 1140, 660 1150, 672 1162 M672 1162 L640 1150 M672 1162 L668 1128" width={7} />
			</In>
			<Burn at={B.supermind} x={50} dur={1.0} />
		</In>
	);
};

/* ---------- 5. STORY 1908 ---------- */
const Story = () => {
	const t = useT();
	const tally = [B.teen, B.teen + 0.2, B.teen + 0.4];
	const just = W('Just', B.baitho);
	return (
		<In s={STORY} e={PRACT}>
			<In s={STORY} e={B.baitho - 0.1}>
				<Clip src="v/smoke.mp4" at={STORY} until={B.baitho} grade="mono" push={[1.0, 1.1]} dim={0.3} />
				<Print src="photo/profile.jpg" at={STORY + 0.2} x={80} y={420} w={430} h={540} rot={-5} caption="1908" />
				<Abs y={470} x={540} w={500}>
					<div style={{fontFamily: 'Display', fontSize: 210, color: C.gold, lineHeight: 1, transform: `scale(${0.9 + 0.1 * spr(t, B.y1908)})`, opacity: ease(t, B.y1908, 0.3)}}>
						{t < B.y1908 + 0.7 ? String(Math.round(lerp(1872, 1908, ease(t, B.y1908, 0.7)))) : '1908'}
					</div>
				</Abs>
				<Hand at={W('yogi', B.y1908)} size={56} color={C.ivory} rot={-3} style={{left: 150, top: 1150}}>a yogi told him...</Hand>
			</In>
			<In s={B.baitho - 0.1} e={B.shaant - 0.1}>
				<Clip src="v/candle.mp4" at={B.baitho - 0.1} until={B.shaant} trim={2} grade="gold" push={[1.08, 1.2]} dim={0.25} />
				<div style={{position: 'absolute', left: 0, width: 1080, top: 300}}>
					<Big size={170} items={[['Sit.', B.baitho]]} />
					<Big size={170} items={[["Don't", B.soChoMat], ['think.', W('think', B.soChoMat), 'coral']]} />
					<Big size={170} items={[['Just', just, 'serif'], ['watch.', B.dekho, 'gold']]} />
				</div>
				{t > B.thoughts2 - 0.1 && ['tomorrow', 'fear', 'plans', 'memories', 'noise', 'worry', 'bills'].map((w, i) => {
					const ang = (i / 7) * Math.PI * 2 + 0.3;
					const fly = ease(t, B.phenk - 0.1 + i * 0.03, 0.55, Easing.in(Easing.cubic));
					const r = 260 + fly * 1100;
					return <Hand key={w} at={B.thoughts2 + i * 0.07} dur={0.2} size={56} color={i % 2 ? C.coral : C.ivory} rot={(random(`st${i}`) - 0.5) * 20}
						style={{left: 440 + Math.cos(ang) * r, top: 1000 + Math.sin(ang) * r * 0.55, opacity: 1 - fly, filter: fly > 0.05 ? `blur(${fly * 12}px)` : undefined}}>{w}</Hand>;
				})}
				{t > B.teen - 0.1 && (
					<div style={{position: 'absolute', left: 300, top: 1060, width: 480, opacity: ease(t, B.teen - 0.1, 0.2)}}>
						<div style={{fontFamily: 'Display', fontSize: 64, color: C.ivory, letterSpacing: 3}}>THREE DAYS</div>
						<svg width={480} height={140} viewBox="0 0 480 140">
							{tally.map((a, i) => (
								<path key={i} d={`M${40 + i * 70} 20 L${46 + i * 70} 125`} stroke={C.marker} strokeWidth={12} strokeLinecap="round" pathLength={1}
									strokeDasharray="1 1" strokeDashoffset={1 - ease(t, a, 0.18)} style={{filter: 'url(#rough)'}} />
							))}
						</svg>
					</div>
				)}
			</In>
			<In s={B.shaant - 0.1} e={PRACT}>
				<Clip src="v/ripples.mp4" at={B.shaant - 0.1} until={PRACT + 0.05} trim={4} grade="night" push={[1.0, 1.06]} dim={0.3} />
				<Abs y={520}><Big size={200} items={[['Silent.', B.shaant, 'serif']]} /></Abs>
			</In>
		</In>
	);
};

/* ---------- 6. PRACTICE ---------- */
const Practice = () => {
	const t = useT();
	const ring = ease(t, B.minute, 2.4, Easing.inOut(Easing.quad));
	const watch2 = W('watch', B.minute);
	return (
		<In s={PRACT} e={END}>
			<In s={PRACT} e={B.kyunki - 0.05}>
				<Clip src="v/meditate.mp4" at={PRACT} until={B.kyunki} grade="gold" push={[1.04, 1.14]} dim={0.25} />
				<Abs y={260}>
					<Big size={130} items={[['Today,', B.aaj + 0.1], ['just', W('just', B.aaj)], ['one', W('one', B.aaj)], ['MINUTE', B.minute, 'gold']]} />
					<Big size={110} items={[['watch', watch2, 'serif'], ['your', W('your', watch2)], ['thoughts', W('thoughts', watch2), 'gold']]} />
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
				<Abs y={260}>
					<Big size={120} items={[['Because', B.kyunki], ['the one', W('the', B.kyunki)]]} />
					<Big size={130} items={[['who is', W('who', B.kyunki), 'serif'], ['WATCHING', B.joDekh, 'gold']]} />
				</Abs>
			</In>
			<In s={B.wahi - 0.1} e={END}>
				<Punch at={B.wahi - 0.1} amt={0.1}><Clip src="v/sunrise.mp4" at={B.wahi - 0.1} until={END} grade="gold" push={[1.05, 1.15]} dim={0.15} /></Punch>
				<Abs y={600}><Big size={220} items={[["That's", B.wahi, 'serif'], ['YOU.', B.aap, 'gold']]} /></Abs>
			</In>
			<Burn at={B.wahi - 0.1} x={45} dur={0.8} />
		</In>
	);
};

/* ---------- 7. END ---------- */
const End = () => {
	const t = useT();
	const out = ease(t, DUR - 0.9, 0.9);
	return (
		<In s={END} e={DUR + 0.1}>
			<Clip src="v/lotus.mp4" at={END} until={DUR} grade="warm" push={[1.05, 1.15]} dim={0.3} />
			<Abs y={480}>
				<Big size={170} items={[['All', B.all, 'serif'], ['life', W('life', B.all), 'serif']]} />
				<Big size={170} items={[['is', W('is', B.all), 'serif'], ['Yoga.', B.yoga, 'gold']]} />
			</Abs>
			<Hand at={B.yoga + 0.45} size={56} color={C.ivory} rot={-3} style={{left: 540, top: 880}}>— Sri Aurobindo</Hand>
			<div style={{position: 'absolute', left: 360, top: 1120, width: 360, height: 104, borderRadius: 52, background: C.gold, display: 'flex', alignItems: 'center',
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
