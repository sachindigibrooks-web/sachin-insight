import React from 'react';
import {Composition} from 'remotion';
import {Video} from './Video';
import tl from './timeline.json';

export const Root: React.FC = () => (
	<Composition id="Ep01" component={Video} durationInFrames={Math.ceil(tl.duration * 30)} fps={30} width={1080} height={1920} />
);
