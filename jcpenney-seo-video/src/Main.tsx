import React from "react";
import { Audio } from "@remotion/media";
import { AbsoluteFill, Sequence, interpolate, staticFile, useVideoConfig } from "remotion";
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
import { C } from "./theme";
import { TOTAL_FRAMES, f } from "./timeline";
import { Captions } from "./ui/Captions";
import { Speaker } from "./ui/Speaker";
import { StockClip } from "./ui/StockClip";

// Every scene is placed in source-time seconds; f() maps to output frames
// after the jump cuts.
const span = (s: number, e: number) => ({ from: f(s), durationInFrames: Math.max(1, f(e) - f(s)) });

// `lead` = seconds from the start of the file to its peak, so the peak lands on `at`.
const Sfx: React.FC<{
  readonly at: number;
  readonly src: string;
  readonly volume?: number;
  readonly lead?: number;
  readonly seconds?: number;
}> = ({ at, src, volume = 0.35, lead = 0, seconds = 2.5 }) => {
  const { fps } = useVideoConfig();
  return (
    <Sequence
      name={`SFX ${src}`}
      from={Math.max(0, f(at) - Math.round(lead * fps))}
      durationInFrames={Math.round(seconds * fps)}
      premountFor={fps}
    >
      <Audio src={staticFile(`sfx/${src}.mp3`)} volume={volume} />
    </Sequence>
  );
};

export const Main: React.FC = () => {
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill style={{ backgroundColor: "#141010" }}>
      <Speaker />

      {/* Stock B-roll cutaways (Mixkit, free license) */}
      <Sequence name="Stock: worried man" {...span(3.25, 5.45)} premountFor={fps}>
        <StockClip src="broll/worried-man.mp4" seed="worried" trimSeconds={2} />
      </Sequence>
      <Sequence name="Stock: banknotes" {...span(11.15, 13.35)} premountFor={fps}>
        <StockClip src="broll/banknotes.mp4" seed="money" trimSeconds={2} label="$1 BILLION BRAND" labelColor={C.clayDeep} />
      </Sequence>
      <Sequence name="Stock: globe" {...span(13.35, 14.95)} premountFor={fps}>
        <StockClip src="broll/globe.mp4" seed="globe" trimSeconds={1} variant="photo" label="Poori duniya jaanti thi" />
      </Sequence>
      <Sequence name="Stock: online shopping + checks" {...span(26.75, 29.75)} premountFor={fps}>
        <StockClip src="broll/online-shopping.mp4" seed="shop" trimSeconds={1} variant="photo" label="Sab kuch tha...">
          <Checks start={26.75} />
        </StockClip>
      </Sequence>
      <Sequence name="Stock: CCTV" {...span(37.85, 39.6)} premountFor={fps}>
        <StockClip src="broll/cctv-thieves.mp4" seed="cctv" trimSeconds={3} label="SEO CHEATING" labelColor={C.clay} />
      </Sequence>
      <Sequence name="Stock: library + lesson" {...span(55.1, 60.15)} premountFor={fps}>
        <StockClip src="broll/library.mp4" seed="library" trimSeconds={0.5}>
          <Lesson start={55.1} />
        </StockClip>
      </Sequence>

      {/* Overlays on the speaker */}
      <Sequence name="Hook text" {...span(0.25, 5.45)} premountFor={fps}>
        <HookText start={0.25} />
      </Sequence>
      <Sequence name="Story tag" {...span(5.5, 8.3)} premountFor={fps}>
        <StoryTag start={5.5} />
      </Sequence>
      <Sequence name="Kyun?" {...span(36.0, 37.6)} premountFor={fps}>
        <Kyun start={36.0} />
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

      {/* Full-screen paper motion graphics */}
      <Sequence name="Graphic: 2011" {...span(8.5, 11.15)} premountFor={fps}>
        <Year2011 start={8.5} />
      </Sequence>
      <Sequence name="Graphic: Google rank drop" {...span(21.8, 26.75)} premountFor={fps}>
        <Serp start={21.8} />
      </Sequence>
      <Sequence name="Graphic: Gone" {...span(30.25, 35.0)} premountFor={fps}>
        <Gone start={30.25} />
      </Sequence>
      <Sequence name="Graphic: Cheating" {...span(39.6, 41.6)} premountFor={fps}>
        <Cheating start={39.6} />
      </Sequence>
      <Sequence name="Stock + graphic: Caught" {...span(46.75, 49.35)} premountFor={fps}>
        <Caught start={46.75} />
      </Sequence>
      <Sequence name="Graphic: JCPenney reveal" {...span(49.55, 55.05)} premountFor={fps}>
        <Reveal start={49.55} />
      </Sequence>
      <Sequence name="Graphic: Types of SEO" {...span(67.0, 76.3)} premountFor={fps}>
        <TypesOfSeo start={67.0} />
      </Sequence>

      <Captions />

      {/* Background music: "Curiosity" (Mixkit). Ducked under the voice,
          dropped out for the "gone." beat, faded at the end. */}
      <Audio
        name="Music"
        src={staticFile("music/curiosity.mp3")}
        volume={(fr) =>
          interpolate(
            fr,
            [0, 20, f(33.6), f(34.3), f(34.9), f(36.1), TOTAL_FRAMES - 45, TOTAL_FRAMES],
            [0, 0.13, 0.13, 0.0, 0.0, 0.13, 0.13, 0],
            { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
          )
        }
      />

      {/* Sound design (Mixkit) */}
      <Sfx at={1.76} src="whoosh-fast" lead={1.05} volume={0.3} />
      <Sfx at={3.25} src="paper-slide" lead={0.3} volume={0.5} />
      <Sfx at={3.8} src="heartbeat-impact" lead={0.05} volume={0.45} />
      <Sfx at={5.5} src="page-turn" lead={0.2} volume={0.5} />
      <Sfx at={8.5} src="paper-slide" lead={0.3} volume={0.5} />
      <Sfx at={9.6} src="pop" volume={0.25} />
      <Sfx at={11.15} src="paper-move" lead={0.3} volume={0.5} />
      <Sfx at={13.35} src="paper-slide" lead={0.3} volume={0.5} />
      <Sfx at={15.0} src="paper-move" lead={0.3} volume={0.45} />
      <Sfx at={17.64} src="pop" volume={0.22} />
      <Sfx at={18.32} src="pop" volume={0.22} />
      <Sfx at={19.3} src="pop" volume={0.22} />
      <Sfx at={21.8} src="paper-slide" lead={0.3} volume={0.5} />
      <Sfx at={22.0} src="typing" volume={0.3} seconds={0.9} />
      <Sfx at={24.8} src="whoosh-fast" lead={1.05} volume={0.3} />
      <Sfx at={26.75} src="paper-slide" lead={0.3} volume={0.5} />
      <Sfx at={27.0} src="pop" volume={0.22} />
      <Sfx at={27.72} src="pop" volume={0.22} />
      <Sfx at={28.88} src="pop" volume={0.22} />
      <Sfx at={30.25} src="paper-slide" lead={0.3} volume={0.5} />
      <Sfx at={32.9} src="glitch-hit" lead={0.25} volume={0.3} seconds={1.4} />
      <Sfx at={34.36} src="impact-big" lead={2.15} volume={0.55} seconds={5} />
      <Sfx at={36.1} src="heartbeat-impact" lead={0.05} volume={0.45} />
      <Sfx at={37.85} src="paper-move" lead={0.3} volume={0.5} />
      <Sfx at={38.0} src="shutter" lead={0.15} volume={0.4} />
      <Sfx at={39.6} src="paper-slide" lead={0.3} volume={0.5} />
      <Sfx at={40.66} src="impact-trailer" lead={0.95} volume={0.35} />
      <Sfx at={41.6} src="paper-move" lead={0.3} volume={0.45} />
      <Sfx at={45.62} src="pop" volume={0.25} />
      <Sfx at={46.75} src="paper-slide" lead={0.3} volume={0.5} />
      <Sfx at={48.4} src="impact-trailer" lead={0.95} volume={0.45} />
      <Sfx at={49.55} src="paper-slide" lead={0.3} volume={0.5} />
      <Sfx at={50.86} src="impact-big" lead={2.15} volume={0.4} seconds={4} />
      <Sfx at={55.1} src="paper-move" lead={0.3} volume={0.5} />
      <Sfx at={55.3} src="page-turn" lead={0.2} volume={0.4} />
      <Sfx at={60.2} src="paper-move" lead={0.3} volume={0.45} />
      <Sfx at={65.6} src="paper-crumple" lead={0.1} volume={0.3} />
      <Sfx at={67.0} src="paper-slide" lead={0.3} volume={0.5} />
      <Sfx at={69.4} src="pop" volume={0.22} />
      <Sfx at={70.42} src="pop" volume={0.22} />
      <Sfx at={72.3} src="pop" volume={0.18} />
      <Sfx at={74.1} src="pop" volume={0.18} />
      <Sfx at={75.3} src="pop" volume={0.18} />
      <Sfx at={76.9} src="whoosh-fast" lead={1.05} volume={0.3} />
    </AbsoluteFill>
  );
};

export const MAIN_FRAMES = TOTAL_FRAMES;
