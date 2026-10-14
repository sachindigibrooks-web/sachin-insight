import React from 'react';
import {AbsoluteFill, Easing, Img, staticFile} from 'remotion';
import {
	B, Bg, clamp01, Clip, COLORS, Cut, Crumple, Cursor, DEVA, ease, extrude, HEAVY, KLine, lerp, MARKER, MarkerPath, NumTag, Paper, Pencil,
	Phone, pop, Ripple, SANS, Stamp, TL, TYPE, useT, Word,
} from './lib';

type Dir = 'l' | 'r' | 'u' | 'd' | 'z';
const VEC: Record<Dir, [number, number]> = {l: [1, 0], r: [-1, 0], u: [0, 1], d: [0, -1], z: [0, 0]};

/** Mounts a scene for its window and does a whip-pan (motion-blurred) transition in and out. */
const Scene: React.FC<{id: string; dir?: Dir; tex: string; children: React.ReactNode}> = ({id, dir = 'l', tex, children}) => {
	const t = useT();
	const sc = TL.scenes.find((s) => s.id === id)!;
	const W = 0.14;
	if (t < sc.s - W || t > sc.e + W) return null;
	const enter = ease(t, sc.s - W, W * 2, Easing.out(Easing.cubic));
	const exit = ease(t, sc.e - W, W * 2, Easing.in(Easing.cubic));
	const [vx, vy] = VEC[dir];
	const nextDir = (TL.scenes.findIndex((s) => s.id === id) % 2 ? VEC.u : VEC.l) as [number, number];
	const dx = vx * 1300 * (1 - enter) - nextDir[0] * 1300 * exit;
	const dy = vy * 2200 * (1 - enter) - nextDir[1] * 2200 * exit;
	const blur = (1 - enter) * 28 + exit * 28;
	const zs = dir === 'z' ? lerp(2.2, 1, enter) : 1;
	return (
		<AbsoluteFill style={{transform: `translate(${dx}px,${dy}px) scale(${zs})`, filter: blur > 0.5 ? `blur(${blur}px)` : undefined,
			opacity: dir === 'z' ? clamp01(enter * 2) : 1}}>
			<Bg tex={tex} s={sc.s} e={sc.e} />
			{children}
		</AbsoluteFill>
	);
};

const Abs: React.FC<{x: number; y: number; w?: number; style?: React.CSSProperties; children: React.ReactNode}> = ({x, y, w, style, children}) => (
	<div style={{position: 'absolute', left: x, top: y, width: w, ...style}}>{children}</div>
);

/* 1. HOOK: phone on a desk, typing a search, cursor hovers a result */
const Hook = () => {
	const t = useT();
	const phoneIn = ease(t, 1.45, 0.45, Easing.out(Easing.back(1.2)));
	const query = 'seo tips 2026';
	const typed = query.slice(0, Math.max(0, Math.floor((t - B.typeStart) * 16)));
	const results = ease(t, 4.2, 0.3);
	const cx = lerp(560, 250, ease(t, 4.6, 0.7, Easing.inOut(Easing.cubic)));
	const cy = lerp(1100, 470, ease(t, 4.6, 0.7, Easing.inOut(Easing.cubic)));
	const press = t > B.clickWord && t < B.clickWord + 0.15 ? 1 : 0;
	const headUp = ease(t, 1.35, 0.35);
	return (
		<Scene id="hook" tex="wood" dir="z">
			<Crumple seed="a" style={{left: 820, top: 160}} />
			<Crumple seed="b" size={120} style={{left: 900, top: 330}} />
			<Pencil style={{left: -120, top: 1590, transform: 'rotate(-18deg)'}} />
			<div style={{position: 'absolute', left: 60, top: 1450, width: 230, height: 230, borderRadius: '50%', border: '14px solid rgba(60,30,10,.35)', filter: 'blur(2px)'}} />
			<Abs x={0} y={lerp(640, 120, headUp)} w={1080} style={{transform: `scale(${lerp(1, 0.62, headUp)})`, transformOrigin: '50% 0%'}}>
				<KLine size={150} items={[['Ek', 0.02], ['baat', B.typeStart - 2.6 > 0 ? 0.36 : 0.36], ['batao...', 0.56]]} />
			</Abs>
			<Phone style={{left: 230, top: lerp(2000, 420, phoneIn), transform: `rotate(${lerp(12, -3, phoneIn)}deg)`}}>
				<div style={{position: 'absolute', left: 30, right: 30, top: 110, height: 92, borderRadius: 50, background: '#fff',
					boxShadow: '0 4px 18px rgba(0,0,0,.18)', border: '2px solid #e6e6e6', display: 'flex', alignItems: 'center', padding: '0 30px',
					fontFamily: SANS, fontWeight: 600, fontSize: 38, color: '#222'}}>
					<svg width="40" height="40" viewBox="0 0 24 24" style={{marginRight: 18}}><circle cx="10" cy="10" r="7" stroke="#777" strokeWidth="2.6" fill="none" /><path d="M15 15l6 6" stroke="#777" strokeWidth="2.6" /></svg>
					{typed}
					{Math.floor(t * 3) % 2 === 0 && t < 4.6 && <span style={{width: 3, height: 44, background: '#2f7bff', marginLeft: 4}} />}
				</div>
				{[0, 1, 2, 3].map((i) => (
					<div key={i} style={{position: 'absolute', left: 40, right: 40, top: 250 + i * 200, opacity: clamp01(results * 4 - i),
						transform: `translateY(${(1 - clamp01(results * 4 - i)) * 40}px)`,
						background: i === 0 && t > B.clickWord ? '#e8f0ff' : 'transparent', borderRadius: 18, padding: 14}}>
						<div style={{width: 260, height: 18, borderRadius: 9, background: '#9fc69f', marginBottom: 14}} />
						<div style={{width: 420, height: 30, borderRadius: 10, background: '#1a56db', marginBottom: 14}} />
						<div style={{width: 470, height: 16, borderRadius: 8, background: '#d0d0d0', marginBottom: 10}} />
						<div style={{width: 380, height: 16, borderRadius: 8, background: '#d0d0d0'}} />
					</div>
				))}
				<Ripple x={240} y={330} at={B.clickWord} />
			</Phone>
			{t > 4.55 && <Cursor x={cx + 230} y={cy + 420} press={press} />}
			<Abs x={560} y={560}><Stamp at={B.clickWord} text="click?" rot={10} size={110} color="#ff2a2a" /></Abs>
		</Scene>
	);
};

/* 2. "Nahi na? Haan, mujhe bhi yaad nahi." */
const Nahi = () => {
	const t = useT();
	const card = ease(t, B.haan, 0.4, Easing.out(Easing.back(1.4)));
	return (
		<Scene id="nahi" tex="dark" dir="r">
			<Abs x={0} y={330} w={1080}>
				<KLine size={230} color="red" items={[['Nahi', B.nahiNa], ['na?', B.nahiNa + 0.28]]} style={{flexDirection: 'column', alignItems: 'center'}} />
			</Abs>
			<Cut src="man" at={B.nahiNa + 0.08} x={150} y={830} w={780} from="b" out={B.haan - 0.2} outline={0} float={4} />
			<Paper w={760} h={340} seed="tab" style={{left: 160, top: lerp(1900, 900, card), transform: `rotate(${lerp(10, -4, card)}deg)`}}>
				<div style={{position: 'absolute', left: 50, top: 50, fontFamily: TYPE, fontSize: 40, color: '#333'}}>www.aapki-website.in</div>
				<div style={{position: 'absolute', left: 50, top: 120, fontFamily: TYPE, fontSize: 64, color: '#111'}}>Visits today:</div>
				<div style={{position: 'absolute', left: 520, top: 105, fontFamily: HEAVY, fontSize: 110, color: '#e3262b'}}>0</div>
				<MarkerPath w={700} h={300} at={9.0} dur={0.18} d="M40 40 L650 260" style={{left: 30, top: 20}} />
				<MarkerPath w={700} h={300} at={9.2} dur={0.18} d="M650 40 L40 260" style={{left: 30, top: 20}} />
			</Paper>
		</Scene>
	);
};

/* 3. AI answers by itself: rings, AI core, orbiting labels, Hindi sticker */
const Ai = () => {
	const t = useT();
	const core = pop(t, B.answer, 200, 10);
	const ringP = ease(t, 10.0, 0.8);
	const orbit = (t - 12.5) * 0.6;
	const pill = (label: string, at: number, ang: number, r: number) => {
		const p = pop(t, at, 260, 12);
		const a = ang + orbit;
		return (
			<div style={{position: 'absolute', left: 540 + Math.cos(a) * r, top: 1000 + Math.sin(a) * r * 0.9, transform: `translate(-50%,-50%) scale(${p})`,
				fontFamily: HEAVY, fontSize: 52, color: '#fff', background: '#1b1b1b', padding: '14px 30px', borderRadius: 60, whiteSpace: 'nowrap',
				boxShadow: '6px 12px 0 #8a8a8a, 0 20px 30px rgba(0,0,0,.35)'}}>{label}</div>
		);
	};
	const hp = pop(t, B.hindi, 380, 13);
	return (
		<Scene id="ai" tex="grid" dir="u">
			<Abs x={0} y={170} w={1080}>
				<KLine size={118} color="black" items={[['Ab', 10.24], ['Google', 10.36], ['khud', B.answer - 0.38]]} />
				<KLine size={90} color="green" items={[['answer', B.answer], ['deta', 11.74], ['hai', 12.02]]} style={{marginTop: 18}} />
			</Abs>
			{[1, 2, 3].map((k) => (
				<div key={k} style={{position: 'absolute', left: 540 - k * 140, top: 1000 - k * 140, width: k * 280, height: k * 280, borderRadius: '50%',
					border: '5px solid #1b1b1b', opacity: 0.55 * ringP, transform: `scale(${lerp(0.3, 1, ease(t, 10 + k * 0.12, 0.6))})`}} />
			))}
			<div style={{position: 'absolute', left: 430, top: 890, width: 220, height: 220, borderRadius: '50%', background: 'radial-gradient(circle at 35% 30%,#7dff8c,#22b53a 60%,#127a24)',
				border: '12px solid #fff', boxShadow: '0 0 0 6px #1b1b1b, 0 30px 40px rgba(0,0,0,.35)', transform: `scale(${core})`,
				display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: HEAVY, fontSize: 96, color: '#fff', textShadow: extrude(5, '#126b22')}}>AI</div>
			{pill('AI MODE', B.aiMode, -2.4, 330)}
			{pill('AI OVERVIEW', B.aiOverview, 0.5, 300)}
			<Cut src="robot" at={B.answer + 0.05} x={690} y={1060} w={360} from="r" rot={-4} />
			{t > B.hindi && (
				<div style={{position: 'absolute', left: 60, top: 1380, transform: `rotate(-8deg) scale(${lerp(2.4, 1, hp)})`, opacity: clamp01(hp * 2),
					background: '#ff7a00', color: '#fff', fontFamily: DEVA, fontWeight: 700, fontSize: 96, padding: '6px 46px 0', borderRadius: 18,
					boxShadow: '10px 14px 0 #8a3b00, 0 24px 30px rgba(0,0,0,.4)'}}>हिंदी में भी</div>
			)}
		</Scene>
	);
};

/* 4. Rank #1 but ZERO clicks */
const Zero = () => {
	const t = useT();
	const sheet = ease(t, 16.4, 0.45, Easing.out(Easing.back(1.1)));
	const z = pop(t, B.zero, 500, 14);
	const red = t > B.zero;
	const counter = t < B.click2 ? '----' : t < B.zero ? String(Math.floor(9999 * (1 - ease(t, B.click2, B.zero - B.click2, Easing.in(Easing.quad))))).padStart(4, '0') : '0';
	return (
		<Scene id="zero" tex={red ? 'red' : 'blue'} dir="l">
			<Pencil style={{left: 600, top: 260, transform: 'rotate(28deg)'}} />
			<Paper w={820} h={1000} seed="report" style={{left: 130, top: lerp(1900, 380, sheet), transform: `rotate(${lerp(-12, -2, sheet)}deg)`,
				filter: red ? 'drop-shadow(10px 18px 22px rgba(0,0,0,.5)) saturate(0.4) brightness(0.8)' : undefined}}>
				<div style={{position: 'absolute', left: 60, top: 60, fontFamily: TYPE, fontSize: 52, color: '#222', borderBottom: '4px solid #222', paddingBottom: 10}}>RANKING REPORT</div>
				<div style={{position: 'absolute', left: 60, top: 180, fontFamily: TYPE, fontSize: 40, color: '#444'}}>Website: aapki-website.in</div>
				<div style={{position: 'absolute', left: 60, top: 300, fontFamily: TYPE, fontSize: 60, color: '#111'}}>Google Rank</div>
				<div style={{position: 'absolute', left: 60, top: 560, fontFamily: TYPE, fontSize: 60, color: '#111'}}>Clicks</div>
				<div style={{position: 'absolute', left: 430, top: 540, fontFamily: HEAVY, fontSize: 110, color: '#1b1b1b', fontVariantNumeric: 'tabular-nums'}}>{counter}</div>
				<Abs x={430} y={250}><Stamp at={B.rank1 + 0.45} text="#1" color="#16a34a" rot={-8} size={150} /></Abs>
				<MarkerPath w={300} h={120} at={19.3} dur={0.25} color="#16a34a" d="M10 60 L90 105 L280 10" style={{left: 470, top: 400}} />
			</Paper>
			<Cut src="trophy" at={B.rank1 + 0.5} x={710} y={1180} w={300} rot={6}
				filter={t > B.zero ? 'grayscale(1) brightness(.55)' : undefined}
				style={t > B.zero ? {transform: `rotate(${lerp(6, 78, ease(t, B.zero, 0.5, Easing.in(Easing.quad)))}deg) translateY(${ease(t, B.zero, 0.5) * 160}px)`} : undefined} />
			{t < B.zero + 0.12 && (
				<Cut src="bomb" at={B.click2} x={40} y={1260} w={330} from="l" rot={-8}
					style={{transform: `translate(${Math.sin(t * 70) * 5 * ease(t, B.click2, 0.6)}px, 0) scale(${t > B.zero ? lerp(1, 2.4, ease(t, B.zero, 0.12)) : 1})`,
						opacity: t > B.zero ? 1 - ease(t, B.zero, 0.12) : 1}} />
			)}
			{t > B.zero && t < B.zero + 0.4 && (
				<div style={{position: 'absolute', left: 205 - 450 * ease(t, B.zero, 0.4), top: 1425 - 450 * ease(t, B.zero, 0.4), width: 900 * ease(t, B.zero, 0.4),
					height: 900 * ease(t, B.zero, 0.4), borderRadius: '50%', background: 'radial-gradient(circle,#fff6c0 0%,#ffb000 35%,#ff3d00 60%,rgba(255,61,0,0) 72%)',
					opacity: 1 - ease(t, B.zero + 0.1, 0.3)}} />
			)}
			{t > B.zero && (
				<div style={{position: 'absolute', left: 0, width: 1080, top: 650, textAlign: 'center', fontFamily: HEAVY, fontSize: 330, color: COLORS.red[0],
					textShadow: extrude(26, '#3d0000', 0.7), transform: `scale(${lerp(3, 1, z)}) rotate(${-4 + (1 - z) * 10}deg)`, letterSpacing: -10}}>ZERO</div>
			)}
		</Scene>
	);
};

/* 5. Newspaper: 2026 SEO ka game badal gaya */
const GameChange = () => {
	const t = useT();
	const np = ease(t, 23.0, 0.5, Easing.out(Easing.back(1.1)));
	return (
		<Scene id="gamechange" tex="wood" dir="u">
			<Crumple seed="c" style={{left: 40, top: 150}} />
			<Cut src="megaphone" at={23.35} x={560} y={1400} w={500} from="r" rot={-18}
				style={t > B.badal && t < B.badal + 0.6 ? {translate: `${Math.sin(t * 80) * 6}px 0`} : undefined} />
			<Clip style={{left: 860, top: 260, transform: 'rotate(20deg)'}} />
			<Paper w={940} h={1180} seed="news" tex="newsprint" style={{left: 70, top: lerp(-1400, 330, np), transform: `rotate(${lerp(-25, 3, np)}deg)`}}>
				<div style={{position: 'absolute', left: 40, right: 40, top: 40, textAlign: 'center', fontFamily: 'serif', fontWeight: 900, fontSize: 92, color: '#151515',
					borderBottom: '6px double #151515', paddingBottom: 12, letterSpacing: -1}}>THE SEO TIMES</div>
				<div style={{position: 'absolute', left: 40, right: 40, top: 175, fontFamily: TYPE, fontSize: 30, color: '#333', textAlign: 'center'}}>Breaking: search ka naya rule</div>
				<div style={{position: 'absolute', left: 0, right: 0, top: 240, textAlign: 'center'}}>
					<Word at={B.year} text="2026" size={260} color="red" />
				</div>
				<div style={{position: 'absolute', left: 0, right: 0, top: 520, textAlign: 'center'}}>
					<KLine size={130} color="black" items={[['SEO', B.seo], ['ka', B.seo + 0.4], ['game', B.seo + 0.62]]} />
					<KLine size={150} color="black" items={[['badal', B.badal], ['gaya', B.badal + 0.32]]} style={{marginTop: 10}} />
				</div>
				<MarkerPath w={760} h={60} at={B.badal + 0.55} dur={0.3} width={16} d="M10 30 C 200 50, 500 10, 750 34" style={{left: 90, top: 860}} />
				{[0, 1, 2, 3].map((i) => <div key={i} style={{position: 'absolute', left: 60 + (i % 2) * 430, top: 950 + Math.floor(i / 2) * 90, width: 380, height: 14, background: '#9a968c', boxShadow: '0 30px 0 #9a968c'}} />)}
			</Paper>
		</Scene>
	);
};

/* 6. Rank is not enough; get CITED in the AI answer */
const Cite = () => {
	const t = useT();
	const up = ease(t, B.aiCard - 0.1, 0.4);
	const card = ease(t, B.aiCard, 0.45, Easing.out(Easing.back(1.2)));
	const lines = ease(t, B.aiCard + 0.3, 1.4, Easing.linear);
	const chip = pop(t, B.naam, 300, 11);
	return (
		<Scene id="cite" tex="grid" dir="l">
			<Abs x={0} y={lerp(420, 140, up)} w={1080} style={{transform: `scale(${lerp(1, 0.6, up)})`, transformOrigin: '50% 0%'}}>
				<div style={{position: 'relative', display: 'inline-block', left: '50%', transform: 'translateX(-50%)'}}>
					<KLine size={150} color="black" items={[['Sirf', 28.02], ['rank', B.rankStrike]]} />
					<MarkerPath w={760} h={80} at={B.kaafiNahi + 0.2} dur={0.25} width={22} d="M10 50 L740 30" style={{left: 0, top: 50}} />
				</div>
				<KLine size={140} color="red" items={[['kaafi', B.kaafiNahi], ['nahi', B.kaafiNahi + 0.24]]} style={{marginTop: 20}} />
			</Abs>
			<div style={{position: 'absolute', left: 110, top: lerp(2000, 600, card), width: 860, height: 780, background: '#fff', borderRadius: 40,
				boxShadow: '0 40px 70px rgba(0,0,0,.35), 0 0 0 3px #e1e1e1', transform: `rotate(${lerp(8, -1.5, card)}deg)`}}>
				<div style={{position: 'absolute', left: 50, top: 46, display: 'flex', alignItems: 'center', fontFamily: SANS, fontWeight: 800, fontSize: 44, color: '#1b1b1b'}}>
					<svg width="56" height="56" viewBox="0 0 24 24" style={{marginRight: 16}}><path d="M12 2 L14 10 L22 12 L14 14 L12 22 L10 14 L2 12 L10 10 Z" fill="#7c4dff" /></svg>
					AI Overview
				</div>
				{[0, 1, 2, 3, 4].map((i) => (
					<div key={i} style={{position: 'absolute', left: 50, top: 150 + i * 60, height: 24, borderRadius: 12, background: '#d9dce3',
						width: Math.max(0, Math.min(1, lines * 5 - i)) * (i === 4 ? 420 : 760)}} />
				))}
				<div style={{position: 'absolute', left: 50, top: 480, fontFamily: SANS, fontWeight: 600, fontSize: 34, color: '#777'}}>Sources</div>
				<div style={{position: 'absolute', left: 50, top: 545, display: 'flex', gap: 20}}>
					<div style={{padding: '18px 30px', borderRadius: 50, background: '#eef1f6', fontFamily: SANS, fontWeight: 700, fontSize: 34, color: '#555'}}>other-site.com</div>
					<div style={{padding: '18px 30px', borderRadius: 50, background: '#ffd21f', fontFamily: SANS, fontWeight: 900, fontSize: 38, color: '#1b1b1b',
						transform: `scale(${chip})`, boxShadow: `0 0 ${40 * chip}px rgba(255,210,31,.9)`}}>aapka-brand.in</div>
				</div>
				{t > 32.3 && <div style={{position: 'absolute', left: 90, top: 650, fontFamily: MARKER, fontSize: 64, color: '#e3262b', transform: `rotate(-6deg) scale(${pop(t, 32.32)})`}}>yahan!</div>}
				<Cut src="hand" at={32.3} x={360} y={700} w={330} rot={-62} from="b" outline={0} float={5} />
				<Cut src="medal" at={B.cite + 0.12} x={640} y={-120} w={230} rot={14} />
				<Abs x={60} y={250}><Stamp at={B.cite} text="Cite hona chahiye" color="#16a34a" rot={-9} size={66} style={{background: 'rgba(255,255,255,.85)'}} /></Abs>
			</div>
		</Scene>
	);
};

/* 7. Ab ye hoga kaise? Teen simple cheezein */
const Teen = () => {
	const t = useT();
	return (
		<Scene id="teen" tex="dark" dir="z">
			<Abs x={0} y={250} w={1080}>
				<KLine size={110} items={[['Ab', 34.7], ['ye', 35.02], ['hoga', 35.22]]} />
				<div style={{textAlign: 'center', marginTop: 10}}><Word at={B.kaise} text="kaise?" size={220} color="yellow" /></div>
			</Abs>
			<Cut src="bulb" at={B.kaise} x={450} y={620} w={180} rot={8} outline={0}
				filter={`drop-shadow(0 0 ${40 + 25 * Math.abs(Math.sin(t * 9))}px rgba(255,230,80,.9))`} />
			<div style={{position: 'absolute', left: 0, width: 1080, top: 880, display: 'flex', justifyContent: 'center', gap: 40}}>
				{['1', '2', '3'].map((n, i) => {
					const p = pop(t, B.teen + i * 0.2, 300, 11);
					return <div key={n} style={{width: 250, height: 250, borderRadius: 34, background: ['#ff2a2a', '#ffd21f', '#3ee05a'][i], transform: `scale(${p}) rotate(${(i - 1) * 5}deg)`,
						boxShadow: '10px 16px 0 rgba(0,0,0,.55)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: HEAVY, fontSize: 170, color: '#1b1b1b'}}>{n}</div>;
				})}
			</div>
			<Abs x={0} y={1200} w={1080}>
				<KLine size={100} color="white" items={[['simple', B.simple], ['cheezein', B.simple + 0.45]]} />
			</Abs>
		</Scene>
	);
};

/* 8. Ek: seedha sawaal, seedha jawaab */
const One = () => {
	const t = useT();
	const q = ease(t, 39.6, 0.4, Easing.out(Easing.back(1.3)));
	const a = ease(t, 40.6, 0.4, Easing.out(Easing.back(1.3)));
	const bub = pop(t, B.bolte, 260, 11);
	return (
		<Scene id="one" tex="mat" dir="l">
			<NumTag n="01" at={38.1} style={{left: 50, top: 120}} />
			<Abs x={360} y={190} w={680}>
				<div style={{display: 'flex', flexDirection: 'column', alignItems: 'flex-start'}}>
					<KLine size={84} items={[['seedha', 39.66], ['sawaal', B.sawaal]]} />
					<KLine size={84} color="yellow" items={[['seedha', 40.68], ['jawaab', B.jawaab]]} />
				</div>
			</Abs>
			<Paper w={800} h={300} seed="q" style={{left: 140, top: lerp(2000, 560, q), transform: 'rotate(-3deg)'}}>
				<div style={{position: 'absolute', left: 50, top: 50, fontFamily: HEAVY, fontSize: 80, color: '#e3262b'}}>Q.</div>
				<div style={{position: 'absolute', left: 170, top: 66, right: 40, fontFamily: TYPE, fontSize: 50, color: '#1b1b1b'}}>Best SEO tips 2026 kya hain?</div>
			</Paper>
			<Paper w={800} h={300} seed="a" style={{left: 150, top: lerp(2200, 900, a), transform: 'rotate(2deg)'}}>
				<div style={{position: 'absolute', left: 50, top: 50, fontFamily: HEAVY, fontSize: 80, color: '#16a34a'}}>A.</div>
				<div style={{position: 'absolute', left: 170, top: 66, right: 40, fontFamily: TYPE, fontSize: 50, color: '#1b1b1b'}}>Seedha, short answer. Pehli line mein.</div>
				{t > B.likho && <div style={{position: 'absolute', left: 380, top: 200, fontFamily: MARKER, fontSize: 70, color: '#1a56db', transform: `rotate(-5deg) scale(${pop(t, B.likho)})`}}>waise likho!</div>}
			</Paper>
			{t > B.bolte && (
				<div style={{position: 'absolute', left: 520, top: 1230, transform: `scale(${bub}) rotate(4deg)`, transformOrigin: '10% 100%'}}>
					<div style={{background: '#fff', borderRadius: 50, padding: '26px 44px', fontFamily: SANS, fontWeight: 900, fontSize: 54, color: '#1b1b1b',
						boxShadow: '8px 12px 0 rgba(0,0,0,.4)'}}>jaise log BOLTE hain</div>
					<div style={{position: 'absolute', left: 60, bottom: -36, width: 0, height: 0, borderLeft: '30px solid transparent', borderRight: '30px solid transparent', borderTop: '44px solid #fff'}} />
				</div>
			)}
		</Scene>
	);
};

/* 9. Do: apna naam har jagah; AI reads from there */
const Two = () => {
	const t = useT();
	const tiles = [
		{at: B.yt, x: 110, y: 760, label: 'YouTube', bg: '#ff2a2a', icon: <svg width="130" height="130" viewBox="0 0 24 24"><path d="M8 5 L19 12 L8 19 Z" fill="#fff" /></svg>},
		{at: B.ig, x: 400, y: 640, label: 'Instagram', bg: 'linear-gradient(45deg,#f9a825,#e91e63,#7b1fa2)', icon: <svg width="130" height="130" viewBox="0 0 24 24"><rect x="4" y="4" width="16" height="16" rx="5" stroke="#fff" strokeWidth="2" fill="none" /><circle cx="12" cy="12" r="4" stroke="#fff" strokeWidth="2" fill="none" /><circle cx="17" cy="7" r="1.2" fill="#fff" /></svg>},
		{at: B.gbp, x: 690, y: 760, label: 'Business Profile', bg: '#fff', icon: <svg width="130" height="130" viewBox="0 0 24 24"><path d="M12 2 C7.6 2 5 5.2 5 9 C5 14 12 22 12 22 C12 22 19 14 19 9 C19 5.2 16.4 2 12 2Z" fill="#2f7bff" /><circle cx="12" cy="9" r="3" fill="#fff" /></svg>},
	];
	const core = pop(t, B.wahin, 220, 11);
	return (
		<Scene id="two" tex="blue" dir="u">
			<NumTag n="02" at={44.4} style={{left: 50, top: 110}} />
			<Abs x={360} y={170} w={680}>
				<div style={{display: 'flex', flexDirection: 'column', alignItems: 'flex-start'}}>
					<KLine size={96} items={[['apna', 45.28], ['naam', 45.58]]} />
					<KLine size={96} color="yellow" items={[['har', B.har], ['jagah', 46.28]]} />
				</div>
			</Abs>
			{tiles.map((k, i) => {
				const p = pop(t, k.at, 300, 11);
				const lineP = ease(t, B.wahin + 0.1 + i * 0.1, 0.35);
				return (
					<React.Fragment key={i}>
						<svg width={1080} height={1920} style={{position: 'absolute', left: 0, top: 0}}>
							<line x1={k.x + 140} y1={k.y + 140} x2={540} y2={1290} stroke="#ffd21f" strokeWidth="8" strokeDasharray="22 16" strokeDashoffset={-t * 60}
								opacity={lineP} pathLength={1} />
						</svg>
						<div style={{position: 'absolute', left: k.x, top: k.y, width: 280, transform: `scale(${p}) rotate(${(i - 1) * -6}deg)`, textAlign: 'center'}}>
							<div style={{width: 280, height: 280, borderRadius: 64, background: k.bg, display: 'flex', alignItems: 'center', justifyContent: 'center',
								boxShadow: '10px 16px 0 rgba(0,0,0,.4)'}}>{k.icon}</div>
							<div style={{fontFamily: HEAVY, fontSize: 40, color: '#fff', marginTop: 18, textShadow: extrude(4, '#0d2f73')}}>{k.label}</div>
						</div>
					</React.Fragment>
				);
			})}
			<div style={{position: 'absolute', left: 440, top: 1190, width: 200, height: 200, borderRadius: '50%', background: 'radial-gradient(circle at 35% 30%,#7dff8c,#22b53a 60%,#127a24)',
				border: '10px solid #fff', transform: `scale(${core})`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: HEAVY, fontSize: 84, color: '#fff',
				boxShadow: `0 0 ${60 * core}px rgba(62,224,90,.8)`}}>AI</div>
			{t > B.wahin - 0.3 && (
				<Img src={staticFile('img/magnifier.png')} style={{position: 'absolute', width: 380,
					left: lerp(-420, 720, ease(t, B.wahin - 0.3, 1.3, Easing.inOut(Easing.cubic))),
					top: 560 + Math.sin(ease(t, B.wahin - 0.3, 1.3) * Math.PI * 2) * 70, transform: 'rotate(-10deg)',
					filter: 'drop-shadow(16px 26px 18px rgba(0,0,0,.5))'}} />
			)}
			<Abs x={0} y={1420} w={1080}>
				<KLine size={74} items={[['wahin', B.wahin], ['se', 51.52], ['padhta', 51.66], ['hai', 52.04]]} />
			</Abs>
		</Scene>
	);
};

/* 10. Teen: real data + real experience; copy-paste gets ignored */
const Three = () => {
	const t = useT();
	const board = ease(t, 52.5, 0.45, Easing.out(Easing.back(1.1)));
	const copies = ease(t, B.copy + 0.3, 0.5);
	const ignored = t > B.ignore;
	const bars = [0.45, 0.7, 0.55, 0.95];
	return (
		<Scene id="three" tex="wood" dir="l">
			<NumTag n="03" at={52.6} style={{left: 50, top: 110}} />
			<Pencil style={{left: 640, top: 1700, transform: 'rotate(-12deg)'}} />
			<Paper w={760} h={760} seed="data" style={{left: 160, top: lerp(2000, 360, board), transform: `rotate(-2deg) translateX(${-copies * 120}px)`}}>
				<div style={{position: 'absolute', left: 50, top: 40, fontFamily: TYPE, fontSize: 46, color: '#222'}}>Case study: 90 din</div>
				{bars.map((v, i) => (
					<div key={i} style={{position: 'absolute', left: 90 + i * 150, bottom: 90, width: 100, height: 480 * v * ease(t, 53.0 + i * 0.12, 0.5),
						background: i === 3 ? '#16a34a' : '#3d3d3d', borderRadius: 8}} />
				))}
				<Abs x={60} y={130}><Stamp at={B.realData} text="Real data" color="#16a34a" rot={-8} size={80} style={{background: 'rgba(255,255,255,.85)'}} /></Abs>
				<Abs x={50} y={560}><Stamp at={B.realExp} text="Real experience" color="#16a34a" rot={5} size={60} style={{background: 'rgba(255,255,255,.85)'}} /></Abs>
			</Paper>
			{t > B.copy && [0, 1, 2].map((i) => {
				const p = ease(t, B.copy + 0.25 + i * 0.12, 0.3, Easing.out(Easing.back(1.4)));
				return (
					<div key={i} style={{position: 'absolute', left: 560 + i * 60, top: 820 + i * 70, width: 360, height: 460, background: '#f4f4f4', borderRadius: 14,
						transform: `translate(${ease(t, B.ignore + 0.35 + i * 0.08, 0.35, Easing.in(Easing.cubic)) * (330 - i * 60)}px, ${ease(t, B.ignore + 0.35 + i * 0.08, 0.35, Easing.in(Easing.cubic)) * (620 - i * 70)}px) rotate(${4 + i * 5 + ease(t, B.ignore + 0.35, 0.35) * 90}deg) scale(${p * (1 - 0.75 * ease(t, B.ignore + 0.35 + i * 0.08, 0.35))})`, boxShadow: '10px 16px 20px rgba(0,0,0,.45)', filter: ignored ? 'grayscale(1) brightness(.6)' : undefined,
						padding: 30, boxSizing: 'border-box'}}>
						{[0, 1, 2, 3, 4, 5].map((k) => <div key={k} style={{height: 18, borderRadius: 9, background: '#c4c4c4', marginBottom: 26, width: `${90 - (k % 3) * 18}%`}} />)}
						<div style={{position: 'absolute', bottom: 24, right: 26, fontFamily: SANS, fontWeight: 800, fontSize: 28, color: '#999'}}>copy ({i + 1})</div>
					</div>
				);
			})}
			{['CTRL + C', 'CTRL + V'].map((k, i) => {
				const at = B.copy + i * 0.28;
				if (t < at || t > B.ignore) return null;
				const p = pop(t, at, 320, 12);
				return <div key={k} style={{position: 'absolute', left: 120 + i * 430, top: 1250, transform: `scale(${p})`, padding: '22px 40px', background: '#262626', color: '#fff',
					fontFamily: HEAVY, fontSize: 64, borderRadius: 22, boxShadow: '0 12px 0 #000, 0 24px 30px rgba(0,0,0,.5)'}}>{k}</div>;
			})}
			<Cut src="trash" at={B.ignore - 0.45} x={720} y={1340} w={300} from="b" rot={-4} />
			<Abs x={330} y={1020}><Stamp at={B.ignore} text="Ignored" color="#ff2a2a" rot={-14} size={120} style={{background: 'rgba(255,255,255,.85)'}} /></Abs>
		</Scene>
	);
};

/* 11. CTA: next episode teaser + follow */
const Cta = () => {
	const t = useT();
	const phone = ease(t, B.insta2 - 0.2, 0.5, Easing.out(Easing.back(1.1)));
	const ticket = pop(t, B.next, 240, 12);
	const followed = t > B.follow + 0.45;
	const press = t > B.follow + 0.35 && t < B.follow + 0.5 ? 1 : 0;
	const cur = ease(t, B.follow - 0.1, 0.45, Easing.inOut(Easing.cubic));
	const typed = 'seo tips'.slice(0, Math.max(0, Math.floor((t - B.engine) * 14)));
	return (
		<Scene id="cta" tex="mat" dir="u">
			<div style={{position: 'absolute', left: 140, top: 150, transform: `rotate(-5deg) scale(${ticket})`, background: '#ffd21f', padding: '20px 60px', borderRadius: 16,
				fontFamily: HEAVY, fontSize: 88, color: '#1b1b1b', boxShadow: '10px 14px 0 rgba(0,0,0,.45)', border: '6px dashed #1b1b1b'}}>NEXT: EP 02</div>
			<Phone w={560} h={1020} style={{left: 260, top: lerp(2100, 420, phone), transform: `rotate(${lerp(10, 3, phone)}deg)`}}>
				<div style={{position: 'absolute', left: 26, right: 26, top: 96, height: 76, borderRadius: 20, background: '#efefef', fontFamily: SANS, fontWeight: 600,
					fontSize: 34, color: '#333', display: 'flex', alignItems: 'center', padding: '0 24px'}}>{typed || 'Search'}</div>
				<div style={{position: 'absolute', left: 26, right: 26, top: 196, display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 8}}>
					{Array.from({length: 12}, (_, i) => {
						const p = ease(t, B.engine + 0.4 + i * 0.05, 0.25);
						return <div key={i} style={{height: 210, borderRadius: 10, background: `hsl(${(i * 47) % 360},70%,${55 + (i % 3) * 8}%)`, opacity: p, transform: `scale(${0.6 + 0.4 * p})`}} />;
					})}
				</div>
			</Phone>
			<Abs x={0} y={1180} w={1080}>
				{t < B.zyaada - 0.1 && <KLine size={92} colors={['white', 'white', 'yellow', 'yellow']} items={[['Instagram', B.insta2], ['=', B.engine - 0.3], ['search', B.engine], ['engine', B.engine + 0.34]]} />}
			</Abs>
			{t > B.zyaada && t < B.follow - 0.2 && (
				<Abs x={0} y={1200} w={1080}><KLine size={86} color="red" items={[['log', 65.26], ['miss', 65.7], ['kar', 66.02], ['rahe', 66.22], ['hain', 66.42]]} /></Abs>
			)}
			{t > B.follow - 0.15 && (
				<>
					<div style={{position: 'absolute', left: 240, top: 1200, width: 600, height: 150, borderRadius: 40, background: followed ? '#3a3a3a' : '#2f7bff',
						transform: `scale(${pop(t, B.follow - 0.15, 260, 12) * (1 - press * 0.07)})`, display: 'flex', alignItems: 'center', justifyContent: 'center',
						fontFamily: HEAVY, fontSize: 70, color: '#fff', boxShadow: '0 14px 0 rgba(0,0,0,.45)'}}>{followed ? 'FOLLOWING' : 'FOLLOW'}</div>
					<Cursor x={lerp(900, 600, cur)} y={lerp(1700, 1290, cur)} press={press} />
					<Ripple x={620} y={1275} at={B.follow + 0.4} color="#ffd21f" />
				</>
			)}
			{t > B.warna && (
				<Abs x={0} y={1378} w={1080}><KLine size={80} colors={['white', 'red', 'white', 'white']} items={[['warna', B.warna], ['miss', 68.42], ['ho', 68.68], ['jayega', 68.86]]} /></Abs>
			)}
			<Cut src="man" at={B.warna - 0.05} x={660} y={1500} w={430} from="b" rot={-6} outline={0} />
			{t > 69.6 && (
				<div style={{position: 'absolute', inset: 0, background: `rgba(0,0,0,${0.85 * ease(t, 69.6, 0.4)})`, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center'}}>
					<div style={{width: 960, textAlign: 'center'}}><Word at={69.75} text="SEO badal gaya hai" size={92} color="yellow" /></div>
					<div style={{fontFamily: SANS, fontWeight: 800, fontSize: 48, color: '#fff', marginTop: 30, opacity: ease(t, 70.0, 0.3)}}>EP 01 / 06</div>
				</div>
			)}
		</Scene>
	);
};

export const Scenes = () => (
	<>
		<Hook /><Nahi /><Ai /><Zero /><GameChange /><Cite /><Teen /><One /><Two /><Three /><Cta />
	</>
);
