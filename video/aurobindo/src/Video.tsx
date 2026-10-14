import React from 'react';
import {AbsoluteFill, staticFile} from 'remotion';
import {C, clamp01, FPS, TL, useT} from './lib';
import {Scenes} from './scenes';

const Captions = () => {
	const t = useT();
	const page = TL.pages.find((p) => t >= p.s - 0.05 && t < p.e);
	if (!page) return null;
	return (
		<div style={{position: 'absolute', left: 70, right: 70, top: 1540, display: 'flex', justifyContent: 'center', flexWrap: 'wrap', gap: '0 14px'}}>
			{page.words.map((w, i) => {
				const on = t >= w.s - 0.03 && t < w.e + 0.08;
				return <span key={i} style={{fontFamily: 'Sans', fontWeight: 800, fontSize: 50, color: on ? C.goldSoft : C.ivory,
					textShadow: '0 2px 12px rgba(0,0,0,.85), 0 0 2px rgba(0,0,0,.9)'}}>{w.t}</span>;
			})}
		</div>
	);
};

export const Video: React.FC = () => {
	const t = useT();
	const g = Math.floor(t * FPS) % 8;
	return (
		<AbsoluteFill style={{background: C.indigo}}>
			<Scenes />
			<Captions />
			<AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 55%, rgba(5,6,20,.6) 100%)'}} />
			<AbsoluteFill style={{backgroundImage: `url(${staticFile(`grain/g${g}.png`)})`, backgroundSize: '512px 512px', opacity: 0.07, mixBlendMode: 'overlay'}} />
			<AbsoluteFill style={{background: C.indigo, opacity: clamp01(1 - t / 0.5)}} />
		</AbsoluteFill>
	);
};
