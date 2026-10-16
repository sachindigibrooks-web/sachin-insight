import React from 'react';
import {AbsoluteFill, Easing, Img, OffthreadVideo, random, staticFile} from 'remotion';
import {B, BRoll, C, Captions, clamp01, DUR, ease, enter, gridBg, In, lerp, paperBg, pop, Still, Tag, Tick, useLayout, useT, Words} from './lib';

/* One edit, two frames. Every cue sits on a spoken word (B = beats from Whisper). A-roll is the speaker; cut-aways carry the
   points he lists, the person he names (Neil Patel), the number, and the cheat-code metaphor. */

// windows where the speaker is on screen
const AROLL: [number, number][] = [[0, 5.64], [B.iknow, B.ek], [B.think, B.black], [B.toh, DUR + 1]];

/** Punch-ins on emphasis (eased, never snapping), plus a slow push so the frame never sits dead. */
const ZOOM: [number, number][] = [[0, 1.16], [0.9, 1.06], [B.but0, 1.12], [B.isme, 1.22], [5.0, 1.12], [B.iknow, 1.0], [B.boring2, 1.05], [B.but, 1.14],
	[B.think, 1.18], [B.toh, 1.02], [B.skill, 1.08], [B.hamesha, 1.12]];
const zoomAt = (t: number) => {
	let i = 0;
	while (i + 1 < ZOOM.length && ZOOM[i + 1][0] <= t) i++;
	const [t0, z] = ZOOM[i];
	const prev = i ? ZOOM[i - 1][1] : z;
	return lerp(prev, z, ease(t, t0, 0.3, Easing.out(Easing.cubic)));
};

const Speaker = () => {
	const t = useT();
	const {v} = useLayout();
	const seg = AROLL.find(([a, b]) => t >= a && t < b);
	const z = v ? 1 + (zoomAt(t) - 1) * 0.55 : zoomAt(t);
	return (
		<AbsoluteFill style={{background: '#000'}}>
			<AbsoluteFill style={{opacity: seg ? 1 : 0, ...(seg && seg[0] > 0 ? enter(t, seg[0]) : {})}}>
				<OffthreadVideo src={staticFile('clip.mp4')} muted
					style={{width: '100%', height: '100%', objectFit: 'cover', objectPosition: v ? '49.5% 50%' : '50% 50%',
						transform: `scale(${z})`, transformOrigin: v ? '50% 32%' : '50% 34%', filter: 'contrast(1.07) saturate(1.06) brightness(1.02)'}} />
				{/* soft vignette to pull the eye to the face */}
				<AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 38%, rgba(0,0,0,0) 45%, rgba(0,0,0,.42) 100%)'}} />
				{v && <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(0,0,0,.35) 0%, rgba(0,0,0,0) 28%, rgba(0,0,0,0) 62%, rgba(0,0,0,.55) 100%)'}} />}
			</AbsoluteFill>
		</AbsoluteFill>
	);
};

/* ---------- A-roll titles ---------- */
const HookTitle = () => {
	const t = useT();
	const {v} = useLayout();
	const strike = ease(t, B.but0, 0.3);
	return (
		<>
			<In s={0} e={1.68}>
				<div style={{position: 'absolute', left: v ? 0 : 110, right: v ? 0 : undefined, top: v ? 230 : 330, width: v ? undefined : 760}}>
					<Words size={v ? 128 : 140} align={v ? 'center' : 'left'} items={[['White', 0.02, 'serif'], ['Hat', B.hat, 'serif'], ['SEO', B.seo, 'lime']]} />
				</div>
			</In>
			<In s={1.68} e={B.isme}>
				<div style={{position: 'absolute', left: v ? 0 : 110, right: v ? 0 : undefined, top: v ? 230 : 300, width: v ? undefined : 820}}>
					<div style={{position: 'relative', display: 'inline-block', width: '100%'}}>
						<Words size={v ? 96 : 92} align={v ? 'center' : 'left'} items={[['The', 1.68], ['boring', B.boring, 'grey'], ['way,', 2.42]]} />
					</div>
					<div style={{height: 8, background: C.red, width: v ? 520 * strike : 470 * strike, margin: v ? '-70px auto 62px' : '-66px 0 58px 0', borderRadius: 4, transform: 'rotate(-2deg)'}} />
					<Words size={v ? 96 : 92} align={v ? 'center' : 'left'} items={[['but', B.but0, 'serif'], ['the', 3.3], ['powerful', B.powerful, 'lime'], ['way.', 3.98]]} />
				</div>
			</In>
			<In s={B.isme} e={5.64}>
				<div style={{position: 'absolute', left: v ? 0 : 110, right: v ? 0 : undefined, top: v ? 260 : 360, width: v ? undefined : 760}}>
					<Words size={v ? 120 : 120} align={v ? 'center' : 'left'} items={[['Isme', B.isme, 'serif'], ['hai', 4.86], ['kya?', 5.1, 'lime']]} />
				</div>
			</In>
		</>
	);
};

/* ---------- the three pillars (cut-aways) ---------- */
const SITES = ['blog', 'news', 'forum', '.edu', 'podcast', 'wiki'];
const LinkMap: React.FC<{at: number}> = ({at}) => {
	const t = useT();
	const {W, H, v} = useLayout();
	const cx = W / 2, cy = v ? 820 : H / 2 + 10;
	const R = v ? 330 : 300;
	const core = pop(t, at + 0.05);
	return (
		<AbsoluteFill style={{...paperBg, ...enter(t, at)}}>
			<svg width={W} height={H} style={{position: 'absolute', inset: 0}}>
				{[0.55, 1, 1.45].map((k) => <circle key={k} cx={cx} cy={cy} r={R * k} fill="none" stroke="rgba(15,15,15,.12)" strokeWidth={2} />)}
				{SITES.map((s, i) => {
					const a = (i / SITES.length) * Math.PI * 2 - Math.PI / 2;
					const p = ease(t, B.backlinks + 0.05 + i * 0.1, 0.35);
					const x = cx + Math.cos(a) * R, y = cy + Math.sin(a) * R;
					return <line key={s} x1={x} y1={y} x2={lerp(x, cx, p)} y2={lerp(y, cy, p)} stroke={C.ink} strokeWidth={4} strokeDasharray="10 8" />;
				})}
			</svg>
			{SITES.map((s, i) => {
				const a = (i / SITES.length) * Math.PI * 2 - Math.PI / 2;
				const p = pop(t, at + 0.15 + i * 0.07);
				return (
					<div key={s} style={{position: 'absolute', left: cx + Math.cos(a) * R - 85, top: cy + Math.sin(a) * R - 38, width: 170, height: 76, borderRadius: 18, background: C.white,
						boxShadow: '0 10px 24px rgba(0,0,0,.18)', display: 'grid', placeItems: 'center', fontFamily: 'Sans', fontWeight: 800, fontSize: 34, color: C.ink, transform: `scale(${p})`}}>{s}</div>
				);
			})}
			<div style={{position: 'absolute', left: cx - 120, top: cy - 120, width: 240, height: 240, borderRadius: '50%', background: C.lime, display: 'grid', placeItems: 'center',
				textAlign: 'center', fontFamily: 'Sans', fontWeight: 900, fontSize: 44, lineHeight: 1.0, color: C.ink, transform: `scale(${core})`,
				boxShadow: `0 0 0 ${12 + 10 * Math.sin(t * 6)}px rgba(200,245,60,.25)`}}>YOUR<br />SITE</div>
		</AbsoluteFill>
	);
};

const Pillars = () => {
	const t = useT();
	const {v} = useLayout();
	const tagPos: React.CSSProperties = v ? {position: 'absolute', left: 70, top: 250} : {position: 'absolute', left: 110, top: 110};
	return (
		<>
			<In s={5.64} e={B.quality}>
				<BRoll src="v/typing.mp4" at={5.64} until={B.quality} trim={1} />
				<div style={tagPos}><Tag n="1" label="Genuine content" at={B.genuine} size={v ? 50 : 46} /></div>
			</In>
			<In s={B.quality} e={B.aur}>
				<LinkMap at={B.quality} />
				<div style={tagPos}><Tag n="2" label="Quality backlinks" at={B.quality + 0.1} size={v ? 50 : 46} /></div>
			</In>
			<In s={B.aur} e={B.iknow}>
				<BRoll src="v/phone.mp4" at={B.aur} until={B.iknow} trim={2} />
				<div style={tagPos}><Tag n="3" label="User experience" at={B.user} size={v ? 50 : 46} /></div>
				{t > B.user + 0.4 && (
					<div style={{position: 'absolute', left: v ? 70 : 110, top: v ? 380 : 230, fontFamily: 'Hand', fontSize: v ? 56 : 52, color: C.lime, transform: `rotate(-4deg)`, opacity: ease(t, 10.68, 0.25),
						textShadow: '0 3px 14px rgba(0,0,0,.6)'}}>fast · easy · useful</div>
				)}
			</In>
		</>
	);
};

/* ---------- "I know yaar, boring lagta hai" ---------- */
const Boring = () => {
	const t = useT();
	const {v} = useLayout();
	return (
		<>
			<In s={B.boring2 - 0.1} e={B.but}>
				<div style={{position: 'absolute', left: v ? 0 : 110, right: v ? 0 : undefined, top: v ? 260 : 360, width: v ? undefined : 760}}>
					<Words size={v ? 110 : 110} align={v ? 'center' : 'left'} items={[['boring', B.boring2, 'grey'], ['lagta hai', 13.92, 'serif']]} />
				</div>
				{['z', 'z', 'Z'].map((z, i) => {
					const p = ease(t, B.boring2 + 0.3 + i * 0.18, 0.9);
					return <div key={i} style={{position: 'absolute', left: (v ? 700 : 1240) + i * 40 + p * 30, top: (v ? 620 : 300) - i * 46 - p * 50, fontFamily: 'Hand', fontSize: 60 + i * 18,
						color: C.white, opacity: p * (1 - ease(t, B.but - 0.3, 0.3)), textShadow: '0 3px 12px rgba(0,0,0,.6)'}}>{z}</div>;
				})}
			</In>
			<In s={B.but} e={B.ek}>
				<div style={{position: 'absolute', left: v ? 0 : 110, right: v ? 0 : undefined, top: v ? 260 : 360, width: v ? undefined : 820}}>
					<Words size={v ? 120 : 118} align={v ? 'center' : 'left'} items={[['But,', B.but], ['ek', 14.9, 'serif'], ['example', B.example, 'lime'], ['suno.', 15.54]]} />
				</div>
			</In>
		</>
	);
};

/* ---------- Neil Patel ---------- */
const STEPS: [string, number][] = [['White Hat SEO', B.wh2], ['Quality content', B.quality2], ['User experience', B.user2], ['Technical SEO', B.technical]];
const Neil = () => {
	const t = useT();
	const {W, v} = useLayout();
	const drop = Easing.out(Easing.back(1.2))(clamp01((t - B.neil) / 0.45));
	const pw = v ? 470 : 560, ph = pw * 0.86;
	const px = v ? (W - pw) / 2 : 260, py = v ? 170 : 150;
	const nameP = ease(t, 18.32, 0.35);
	const listX = v ? 120 : 960, listY = v ? 860 : 250;
	return (
		<In s={B.ek} e={B.aaj}>
			<AbsoluteFill style={{...gridBg(C.orange), ...enter(t, B.ek)}}>
				<AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 40%, rgba(255,255,255,.12), rgba(0,0,0,.28))'}} />
			</AbsoluteFill>
			{/* "Ek blogger tha..." before the photo lands */}
			<div style={{position: 'absolute', left: v ? 0 : 150, right: v ? 0 : undefined, top: v ? 520 : 380, width: v ? undefined : 700, opacity: 1 - ease(t, B.neil - 0.15, 0.2)}}>
				<Words size={v ? 120 : 110} align={v ? 'center' : 'left'} items={[['Ek', B.ek, 'serif'], ['blogger', B.blogger], ['tha...', 17.26, 'serif']]} />
			</div>
			{/* printed photo drops onto the board */}
			<div style={{position: 'absolute', left: px, top: py, width: pw, padding: 18, paddingBottom: 70, background: '#fbfaf6', boxShadow: '0 30px 60px rgba(0,0,0,.35)',
				transform: `translateY(${(1 - drop) * -900}px) rotate(${lerp(-14, -3, drop)}deg)`, opacity: t >= B.neil - 0.02 ? 1 : 0}}>
				<Img src={staticFile('img/neil_photo.jpg')} style={{width: '100%', height: ph, objectFit: 'cover', objectPosition: '45% 30%', display: 'block', filter: 'contrast(1.05) saturate(1.05)'}} />
				<div style={{position: 'absolute', left: 0, right: 0, bottom: 14, textAlign: 'center', fontFamily: 'Hand', fontSize: 40, color: C.ink}}>the blogger</div>
				<div style={{position: 'absolute', left: pw / 2 - 70, top: -22, width: 140, height: 44, background: 'rgba(240,230,200,.85)', transform: 'rotate(3deg)'}} />
			</div>
			{/* name plate */}
			<div style={{position: 'absolute', left: v ? 0 : px, right: v ? 0 : undefined, top: py + ph + (v ? 108 : 120), width: v ? undefined : pw, textAlign: 'center', opacity: nameP, transform: `translateY(${(1 - nameP) * 20}px)`}}>
				<div style={{display: 'inline-block', background: C.ink, color: C.white, fontFamily: 'Sans', fontWeight: 900, fontSize: v ? 64 : 58, letterSpacing: '-0.02em', padding: '10px 28px', borderRadius: 10}}>NEIL PATEL</div>
				<div style={{fontFamily: 'Sans', fontWeight: 600, fontSize: v ? 34 : 30, color: C.white, marginTop: 10, opacity: 0.92}}>Co-founder, NP Digital</div>
			</div>
			{/* what he did: ticks land on each phrase */}
			{t > B.usne - 0.1 && (
				<div style={{position: 'absolute', left: listX, top: listY, width: v ? W - 240 : 780, background: C.paper, borderRadius: 26, padding: v ? '34px 40px' : '40px 46px',
					boxShadow: '0 24px 60px rgba(0,0,0,.3)', transform: `scale(${pop(t, B.usne - 0.1, 0.4)})`, transformOrigin: v ? '50% 0%' : '0% 50%'}}>
					<div style={{fontFamily: 'Serif', fontStyle: 'italic', fontSize: v ? 46 : 48, color: C.ink, marginBottom: 14}}>Usne kya kiya?</div>
					{STEPS.map(([s, at], i) => {
						const p = ease(t, at - 0.08, 0.25);
						return (
							<div key={s} style={{display: 'flex', alignItems: 'center', gap: 22, padding: '12px 0', borderTop: i ? '2px dashed rgba(15,15,15,.15)' : 'none',
								opacity: lerp(0.35, 1, p)}}>
								<Tick at={at} size={v ? 54 : 56} />
								<div style={{fontFamily: 'Sans', fontWeight: 800, fontSize: v ? 50 : 52, color: C.ink, letterSpacing: '-0.02em'}}>{s}</div>
							</div>
						);
					})}
				</div>
			)}
		</In>
	);
};

/* ---------- Millions of users ---------- */
const Millions = () => {
	const t = useT();
	const {v} = useLayout();
	const p = ease(t, B.million - 0.1, 1.1, Easing.out(Easing.quad));
	const n = Math.round(Math.pow(p, 2.2) * 1000000);
	return (
		<In s={B.aaj} e={B.think}>
			<BRoll src="v/crowd.mp4" at={B.aaj} until={B.think} trim={3} dim={0.35} />
			<div style={{position: 'absolute', left: 0, right: 0, top: v ? 520 : 300, textAlign: 'center'}}>
				<div style={{fontFamily: 'Display', fontSize: v ? 190 : 210, color: C.white, lineHeight: 1, letterSpacing: '0.01em', opacity: ease(t, B.million - 0.15, 0.15),
					fontVariantNumeric: 'tabular-nums', textShadow: '0 10px 40px rgba(0,0,0,.5)', transform: `scale(${1 + 0.06 * (1 - ease(t, B.million + 1.0, 0.3)) * (t > B.million + 1.0 ? 1 : 0)})`}}>
					{n.toLocaleString('en-US')}{p >= 1 ? '+' : ''}
				</div>
				<div style={{marginTop: 14}}><Words size={v ? 84 : 80} items={[['users', B.users, 'lime'], ['aa rahe hain', 29.68, 'serif']]} /></div>
			</div>
			<div style={{position: 'absolute', left: 0, right: 0, top: v ? 300 : 130, display: 'flex', justifyContent: 'center', opacity: ease(t, B.website - 0.1, 0.3)}}>
				<div style={{background: C.white, borderRadius: 14, padding: '12px 26px', fontFamily: 'Sans', fontWeight: 800, fontSize: v ? 40 : 38, color: C.ink, boxShadow: '0 12px 30px rgba(0,0,0,.35)'}}>
					uski website
				</div>
			</div>
		</In>
	);
};

/* ---------- Black hat = cheat code, and it's banned ---------- */
const CODE = '↑ ↑ ↓ ↓ ← → ← → B A';
const BlackHat = () => {
	const t = useT();
	const {v} = useLayout();
	const typed = Math.floor(clamp01((t - B.cheat) / 0.9) * CODE.length);
	const ban = pop(t, B.ban - 0.03, 0.22);
	const shake = t > B.ban && t < B.ban + 0.35 ? Math.sin(t * 90) * 14 * (1 - (t - B.ban) / 0.35) : 0;
	return (
		<In s={B.black} e={B.toh}>
			<AbsoluteFill style={{transform: `translate(${shake}px, ${shake * 0.4}px)`}}>
				<In s={B.black} e={B.game}><BRoll src="v/hacker.mp4" at={B.black} until={B.game} trim={1} dim={0.3} grade="contrast(1.15) saturate(.8) hue-rotate(-10deg)" /></In>
				<In s={B.game} e={B.ban}><BRoll src="v/gamer.mp4" at={B.game} until={B.ban} trim={0} dim={0.3} grade="contrast(1.1) saturate(1.1)" /></In>
				{t >= B.ban && (
					<AbsoluteFill style={{overflow: 'hidden'}}>
						<Still src="img/gamer_freeze.jpg" style={{filter: 'grayscale(1) contrast(1.3) brightness(.55)', transform: `scale(${1.1 + (t - B.ban) * 0.02})`}} />
						<AbsoluteFill style={{background: 'rgba(255,40,30,.12)', mixBlendMode: 'multiply'}} />
					</AbsoluteFill>
				)}
				<div style={{position: 'absolute', left: v ? 0 : 110, right: v ? 0 : undefined, top: v ? 250 : 170, width: v ? undefined : 900}}>
					<Words size={v ? 130 : 120} align={v ? 'center' : 'left'} items={[['Black', B.black], ['Hat', 32.22], ['SEO', 32.72, 'red']]} />
					{t > B.game && (
						<div style={{marginTop: 10}}>
							<Words size={v ? 84 : 80} align={v ? 'center' : 'left'} items={[['=', B.game, 'grey'], ['game ka', 33.0, 'serif'], ['cheat code', B.cheat - 0.05, 'lime']]} />
						</div>
					)}
				</div>
				{t > B.cheat && (
					<div style={{position: 'absolute', left: 0, right: 0, top: v ? 900 : 640, textAlign: 'center'}}>
						<span style={{display: 'inline-block', fontFamily: 'Sans', fontWeight: 900, fontSize: v ? 64 : 60, letterSpacing: '0.06em', color: C.lime, background: 'rgba(0,0,0,.6)',
							padding: '14px 30px', borderRadius: 12, textShadow: `0 0 18px ${C.lime}`, opacity: t >= B.ban ? 0.35 : 1}}>
							{CODE.slice(0, typed)}<span style={{opacity: Math.floor(t * 4) % 2 ? 1 : 0}}>_</span>
						</span>
					</div>
				)}
				{t >= B.ban - 0.03 && (
					<div style={{position: 'absolute', left: 0, right: 0, top: v ? 660 : 380, display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
						<div style={{border: `12px solid ${C.red}`, borderRadius: 18, padding: '10px 46px', fontFamily: 'Sans', fontWeight: 900, fontSize: v ? 170 : 170, letterSpacing: '0.02em',
							color: C.red, transform: `rotate(-8deg) scale(${lerp(2.2, 1, ban)})`, opacity: clamp01(ban * 2), background: 'rgba(255,255,255,.06)',
							textShadow: '0 0 1px rgba(0,0,0,.3)'}}>BANNED</div>
						<div style={{marginTop: 36, fontFamily: 'Sans', fontWeight: 800, fontSize: v ? 44 : 40, color: C.white, opacity: ease(t, B.ban + 0.35, 0.3),
							background: 'rgba(0,0,0,.55)', padding: '8px 22px', borderRadius: 10}}>Google penalty = traffic gone</div>
					</div>
				)}
			</AbsoluteFill>
		</In>
	);
};

/* ---------- "Think of it like this" + close ---------- */
const Close = () => {
	const t = useT();
	const {v} = useLayout();
	return (
		<>
			<In s={B.think} e={B.black}>
				<div style={{position: 'absolute', left: v ? 0 : 110, right: v ? 0 : undefined, top: v ? 260 : 360, width: v ? undefined : 760}}>
					<Words size={v ? 110 : 110} align={v ? 'center' : 'left'} items={[['Think', B.think, 'serif'], ['of it', 31.02], ['like this', 31.28, 'lime']]} />
				</div>
			</In>
			<In s={B.toh} e={DUR + 1}>
				<div style={{position: 'absolute', left: v ? 0 : 110, right: v ? 0 : undefined, top: v ? 230 : 300, width: v ? undefined : 820}}>
					<Words size={v ? 130 : 130} align={v ? 'center' : 'left'} items={[['White', B.wh3, 'serif'], ['Hat', 38.32, 'serif'], ['SEO', 38.66, 'lime']]} />
					{t > B.skill - 0.1 && (
						<div style={{marginTop: 6}}>
							<Words size={v ? 86 : 84} align={v ? 'center' : 'left'} items={[['=', B.skill - 0.1, 'grey'], ['skill', B.skill], ['for life', B.hamesha, 'serif']]} />
						</div>
					)}
				</div>
			</In>
		</>
	);
};

export const Edit: React.FC = () => {
	const t = useT();
	const f = Math.floor(t * 30);
	return (
		<AbsoluteFill style={{background: '#000'}}>
			<Speaker />
			<HookTitle />
			<Pillars />
			<Boring />
			<Neil />
			<Millions />
			<BlackHat />
			<Close />
			<Captions />
			{/* light film grain so stock, graphics and camera footage sit in one image */}
			<AbsoluteFill style={{backgroundImage: `url(${staticFile(`grain/g${f % 8}.png`)})`, backgroundSize: '420px 420px', opacity: 0.06, mixBlendMode: 'overlay', pointerEvents: 'none'}} />
			<AbsoluteFill style={{background: '#000', opacity: clamp01(1 - t / 0.2) + ease(t, DUR - 0.35, 0.35)}} />
		</AbsoluteFill>
	);
};
