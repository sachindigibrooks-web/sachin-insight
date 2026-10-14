import React from 'react';
import {AbsoluteFill, random, staticFile} from 'remotion';
import {C, clamp01, FPS, TL, useT} from './lib';
import {Scenes} from './scenes';

const Captions = () => {
	const t = useT();
	const page = TL.pages.find((p) => t >= p.s - 0.05 && t < p.e);
	if (!page) return null;
	return (
		<div style={{position: 'absolute', left: 60, right: 60, top: 1560, display: 'flex', justifyContent: 'center', flexWrap: 'wrap', gap: '6px 8px'}}>
			{page.words.map((w, i) => {
				const on = t >= w.s - 0.03 && t < w.e + 0.08;
				return <span key={i} style={{fontFamily: 'Sans', fontWeight: 800, fontSize: 50, padding: '2px 10px', borderRadius: 8,
					color: on ? C.ink : C.ivory, background: on ? C.marker : 'transparent', transform: on ? 'rotate(-1.5deg)' : undefined,
					textShadow: on ? 'none' : '0 2px 12px rgba(0,0,0,.9), 0 0 2px rgba(0,0,0,.9)'}}>{w.t}</span>;
			})}
		</div>
	);
};

export const Video: React.FC = () => {
	const t = useT();
	const f = Math.floor(t * FPS);
	const g = f % 8;
	// gate weave: tiny per-frame jitter like film running through a projector
	const wx = (random(`wx${f}`) - 0.5) * 2.2;
	const wy = (random(`wy${f}`) - 0.5) * 2.2;
	const flicker = 1 + (random(`fl${f}`) - 0.5) * 0.035;
	return (
		<AbsoluteFill style={{background: C.ink}}>
			<svg width={0} height={0} style={{position: 'absolute'}}>
				<defs>
					<filter id="rough"><feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves={2} seed={4} /><feDisplacementMap in="SourceGraphic" scale={4} /></filter>
				</defs>
			</svg>
			<AbsoluteFill style={{transform: `translate(${wx}px, ${wy}px) scale(1.01)`, filter: `brightness(${flicker})`}}>
				<Scenes />
			</AbsoluteFill>
			<Captions />
			<AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 50%, rgba(0,0,0,.55) 100%)'}} />
			<AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(42,93,99,.10), rgba(242,184,75,.06))', mixBlendMode: 'soft-light'}} />
			<AbsoluteFill style={{backgroundImage: `url(${staticFile(`grain/g${g}.png`)})`, backgroundSize: '420px 420px', opacity: 0.11, mixBlendMode: 'overlay'}} />
			<AbsoluteFill style={{background: C.ink, opacity: clamp01(1 - t / 0.35)}} />
		</AbsoluteFill>
	);
};
