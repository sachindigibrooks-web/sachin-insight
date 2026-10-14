import React from 'react';
import {AbsoluteFill, staticFile} from 'remotion';
import {C, clamp01, FPS, TL, useT} from './lib';
import {Scenes} from './scenes';

/** Understated subtitles (most social viewers watch muted): Raleway, cream, current word in gold. */
const Subs = () => {
	const t = useT();
	const page = TL.pages.find((p) => t >= p.s - 0.05 && t < p.e);
	if (!page || t > 38.9) return null;
	return (
		<div style={{position: 'absolute', left: 80, right: 80, top: 1600, display: 'flex', justifyContent: 'center', flexWrap: 'wrap', gap: '0 12px'}}>
			{page.words.map((w, i) => {
				const on = t >= w.s - 0.03 && t < w.e + 0.08;
				return <span key={i} style={{fontFamily: 'Body', fontWeight: 600, fontSize: 44, letterSpacing: '0.02em', color: on ? C.gold : C.cream,
					textShadow: '0 2px 14px rgba(0,0,0,.85)'}}>{w.t}</span>;
			})}
		</div>
	);
};

export const Video: React.FC = () => {
	const t = useT();
	const g = Math.floor(t * FPS) % 8;
	return (
		<AbsoluteFill style={{background: C.black}}>
			<Scenes />
			<Subs />
			<AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 55%, rgba(0,0,0,.5) 100%)'}} />
			<AbsoluteFill style={{backgroundImage: `url(${staticFile(`grain/g${g}.png`)})`, backgroundSize: '400px 400px', opacity: 0.06, mixBlendMode: 'overlay'}} />
			<AbsoluteFill style={{background: C.black, opacity: clamp01(1 - t / 0.4) + clamp01((t - 44.0) / 0.5)}} />
		</AbsoluteFill>
	);
};
