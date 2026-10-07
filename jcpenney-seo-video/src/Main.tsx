import React from "react";
import { Audio } from "@remotion/media";
import { AbsoluteFill, Sequence, staticFile, useVideoConfig } from "remotion";
import {
  Algorithm,
  Categories,
  Checks,
  EndCta,
  HookText,
  Kyun,
  Lesson,
  MostPeople,
  StoryTag,
} from "./broll/Overlays";
import { Caught, Cheating, Gone, Reveal, Serp, TypesOfSeo, Year2011 } from "./broll/Stages";
import { TOTAL_FRAMES, f } from "./timeline";
import { Captions } from "./ui/Captions";
import { Speaker } from "./ui/Speaker";

// Every scene is placed in source-time seconds; f() maps to output frames
// after the jump cuts.
const span = (s: number, e: number) => ({ from: f(s), durationInFrames: Math.max(1, f(e) - f(s)) });

const Sfx: React.FC<{ readonly at: number; readonly src: string; readonly volume?: number }> = ({
  at,
  src,
  volume = 0.35,
}) => {
  const { fps } = useVideoConfig();
  return (
    <Sequence name={`SFX ${src}`} from={Math.max(0, f(at) - 2)} durationInFrames={2 * fps} premountFor={fps}>
      <Audio src={staticFile(`sfx/${src}.wav`)} volume={volume} />
    </Sequence>
  );
};

export const Main: React.FC = () => {
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill style={{ backgroundColor: "#141010" }}>
      <Speaker />

      {/* Overlays on the speaker */}
      <Sequence name="Hook text" {...span(0.25, 5.45)} premountFor={fps}>
        <HookText start={0.25} />
      </Sequence>
      <Sequence name="Story tag" {...span(5.5, 8.3)} premountFor={fps}>
        <StoryTag start={5.5} />
      </Sequence>
      <Sequence name="Website / content / products" {...span(26.75, 29.75)} premountFor={fps}>
        <Checks start={26.75} />
      </Sequence>
      <Sequence name="Kyun?" {...span(36.0, 37.6)} premountFor={fps}>
        <Kyun start={36.0} />
      </Sequence>
      <Sequence name="Lesson card" {...span(55.1, 60.15)} premountFor={fps}>
        <Lesson start={55.1} />
      </Sequence>
      <Sequence name="End CTA" {...span(76.6, 77.95)} premountFor={fps}>
        <EndCta start={76.6} />
      </Sequence>

      {/* Split-screen panels (speaker slides right, see SPLITS) */}
      <Sequence name="Categories panel" {...span(15.0, 21.6)} premountFor={fps}>
        <Categories start={15.0} />
      </Sequence>
      <Sequence name="Algorithm panel" {...span(41.6, 46.7)} premountFor={fps}>
        <Algorithm start={41.6} />
      </Sequence>
      <Sequence name="Most people panel" {...span(60.2, 66.9)} premountFor={fps}>
        <MostPeople start={60.2} />
      </Sequence>

      {/* Full-screen motion-graphic B-roll */}
      <Sequence name="B-roll: 2011 billion dollar brand" {...span(8.5, 14.8)} premountFor={fps}>
        <Year2011 start={8.5} />
      </Sequence>
      <Sequence name="B-roll: Google rank drop" {...span(21.8, 26.75)} premountFor={fps}>
        <Serp start={21.8} />
      </Sequence>
      <Sequence name="B-roll: Gone" {...span(30.25, 35.0)} premountFor={fps}>
        <Gone start={30.25} />
      </Sequence>
      <Sequence name="B-roll: Cheating" {...span(37.85, 41.6)} premountFor={fps}>
        <Cheating start={37.85} />
      </Sequence>
      <Sequence name="B-roll: Caught" {...span(46.75, 49.35)} premountFor={fps}>
        <Caught start={46.75} />
      </Sequence>
      <Sequence name="B-roll: JCPenney reveal" {...span(49.55, 55.05)} premountFor={fps}>
        <Reveal start={49.55} />
      </Sequence>
      <Sequence name="B-roll: Types of SEO" {...span(67.0, 76.3)} premountFor={fps}>
        <TypesOfSeo start={67.0} />
      </Sequence>

      <Captions />

      {/* Sound design */}
      <Sfx at={1.76} src="whoosh" />
      <Sfx at={3.8} src="record-scratch" volume={0.22} />
      <Sfx at={8.5} src="whoosh" />
      <Sfx at={11.2} src="switch" volume={0.3} />
      <Sfx at={15.0} src="whip" volume={0.3} />
      <Sfx at={17.64} src="mouse-click" volume={0.4} />
      <Sfx at={18.32} src="mouse-click" volume={0.4} />
      <Sfx at={19.3} src="mouse-click" volume={0.4} />
      <Sfx at={21.8} src="whoosh" />
      <Sfx at={24.8} src="whip" volume={0.3} />
      <Sfx at={26.75} src="ding" volume={0.15} />
      <Sfx at={27.72} src="ding" volume={0.15} />
      <Sfx at={28.88} src="ding" volume={0.15} />
      <Sfx at={30.25} src="whoosh" />
      <Sfx at={34.36} src="dramatic-boomer" volume={0.4} />
      <Sfx at={37.85} src="whoosh" />
      <Sfx at={40.66} src="shutter-modern" volume={0.4} />
      <Sfx at={41.6} src="whip" volume={0.3} />
      <Sfx at={45.62} src="mouse-click" volume={0.4} />
      <Sfx at={46.75} src="whoosh" />
      <Sfx at={48.4} src="shutter-modern" volume={0.45} />
      <Sfx at={50.86} src="dramatic-boomer" volume={0.35} />
      <Sfx at={55.3} src="whoosh" volume={0.25} />
      <Sfx at={60.2} src="whip" volume={0.3} />
      <Sfx at={67.0} src="whoosh" />
      <Sfx at={77.0} src="whoosh" volume={0.3} />
    </AbsoluteFill>
  );
};

export const MAIN_FRAMES = TOTAL_FRAMES;
