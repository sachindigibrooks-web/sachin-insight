import React from 'react';
import {Composition} from 'remotion';
import {Edit} from './Edit';
import tl from './timeline.json';

const frames = Math.ceil(tl.duration * 30);
export const Root: React.FC = () => (
	<>
		<Composition id="Shorts" component={Edit} durationInFrames={frames} fps={30} width={1080} height={1920} />
		<Composition id="YouTube" component={Edit} durationInFrames={frames} fps={30} width={1920} height={1080} />
	</>
);
