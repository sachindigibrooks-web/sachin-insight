import React from 'react';
import {AbsoluteFill, Img, staticFile} from 'remotion';
import {B, clamp01, ease, FPS, pop, SANS, TL, useT} from './lib';
import {Scenes} from './scenes';

// Camera-shake impacts: [beat time, strength]
const IMPACTS: [number, number][] = [
	[B.clickWord, 10], [B.nahiNa, 14], [B.hindi, 8], [B.rank1 + 0.45, 8], [B.zero, 34], [B.year, 12], [B.cite, 14],
	[B.kaise, 12], [B.realData, 8], [B.realExp, 8], [B.ignore, 18], [B.follow + 0.4, 8],
];
const FLASHES = [B.zero, B.cite, B.ignore];

const shake = (t: number) => {
	let x = 0, y = 0, r = 0;
	for (const [a, s] of IMPACTS) {
		if (t < a || t > a + 0.5) continue;
		const k = s * Math.exp(-(t - a) * 9);
		x += Math.sin((t - a) * 90) * k;
		y += Math.cos((t - a) * 73) * k * 0.8;
		r += Math.sin((t - a) * 60) * k * 0.03;
	}
	return {x, y, r};
};

const Captions = () => {
	const t = useT();
	const page = TL.pages.find((p) => t >= p.s - 0.05 && t < p.e);
	if (!page) return null;
	const p = pop(t, page.s - 0.05, 400, 18);
	return (
		<div style={{position: 'absolute', left: 60, right: 60, top: 1515, display: 'flex', justifyContent: 'center', flexWrap: 'wrap', gap: '0 16px',
			transform: `scale(${0.85 + 0.15 * p})`}}>
			{page.words.map((w, i) => {
				const active = t >= w.s - 0.03 && t < w.e + 0.08;
				return (
					<span key={i} style={{fontFamily: SANS, fontWeight: 900, fontSize: 56, color: active ? '#ffd21f' : '#fff',
						textShadow: '0 0 6px #000, 0 4px 0 #000, 0 0 14px rgba(0,0,0,.8)', WebkitTextStroke: '2px #000', paintOrder: 'stroke fill'}}>{w.t}</span>
				);
			})}
		</div>
	);
};

export const Video: React.FC = () => {
	const t = useT();
	const {x, y, r} = shake(t);
	const flash = Math.max(0, ...FLASHES.map((a) => (t >= a && t < a + 0.2 ? 1 - ease(t, a, 0.2) : 0)));
	const g = Math.floor(t * FPS) % 8;
	return (
		<AbsoluteFill style={{background: '#000'}}>
			<svg width={0} height={0} style={{position: 'absolute'}}>
				<defs>
					<filter id="rough">
						<feTurbulence type="fractalNoise" baseFrequency="0.05" numOctaves={2} seed={3} />
						<feDisplacementMap in="SourceGraphic" scale={5} />
					</filter>
				</defs>
			</svg>
			<AbsoluteFill style={{transform: `translate(${x}px,${y}px) rotate(${r}deg) scale(1.03)`}}>
				<Scenes />
			</AbsoluteFill>
			<Captions />
			<AbsoluteFill style={{background: '#fff', opacity: flash * 0.75, mixBlendMode: 'screen'}} />
			<AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.55) 100%)'}} />
			<AbsoluteFill style={{backgroundImage: `url(${staticFile(`grain/g${g}.png`)})`, backgroundSize: '512px 512px', opacity: 0.09, mixBlendMode: 'overlay'}} />
			<AbsoluteFill style={{opacity: clamp01(1 - t / 0.25), background: '#000'}} />
		</AbsoluteFill>
	);
};
