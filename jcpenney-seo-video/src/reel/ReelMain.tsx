import React from "react";
import { Audio } from "@remotion/media";
import { AbsoluteFill, Sequence, interpolate, staticFile, useVideoConfig } from "remotion";
import { TOTAL_FRAMES, f } from "../timeline";
import { LightLeak } from "./Fx";
import { ReelCaptions } from "./ReelCaptions";
import { ReelSpeaker } from "./ReelSpeaker";
import {
  AlgoPop,
  Billion,
  Categories,
  Caught,
  Cctv,
  EndCta,
  GoneTitle,
  KyunPop,
  Lesson,
  PaidLinks,
  Ranking,
  Reveal,
  ShortcutTitle,
  TvCheck,
  TypesOfSeo,
  World,
  WorriedClip,
  Year,
} from "./Scenes";

// Scenes are placed in source-video seconds; f() maps them through the jump cuts.
const span = (s: number, e: number) => ({ from: f(s), durationInFrames: Math.max(1, f(e) - f(s)) });

const Sfx: React.FC<{ readonly at: number; readonly src: string; readonly volume?: number; readonly lead?: number; readonly seconds?: number }> = ({
  at,
  src,
  volume = 0.35,
  lead = 0,
  seconds = 2.5,
}) => {
  const { fps } = useVideoConfig();
  return (
    <Sequence name={`SFX ${src}`} from={Math.max(0, f(at) - Math.round(lead * fps))} durationInFrames={Math.round(seconds * fps)} premountFor={fps}>
      <Audio src={staticFile(`sfx/${src}.mp3`)} volume={volume} />
    </Sequence>
  );
};

// 9:16 short in the style of the two reference reels.
export const ReelMain: React.FC = () => {
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      <ReelSpeaker />

      <Sequence name="Shortcut title" {...span(1.7, 2.75)} premountFor={fps}>
        <ShortcutTitle start={1.7} />
      </Sequence>
      <Sequence name="Worried b-roll" {...span(3.7, 5.45)} premountFor={fps}>
        <WorriedClip start={3.7} />
      </Sequence>
      <Sequence name="2011" {...span(8.5, 11.15)} premountFor={fps}>
        <Year start={8.5} />
      </Sequence>
      <Sequence name="Billion" {...span(11.15, 13.35)} premountFor={fps}>
        <Billion start={11.15} />
      </Sequence>
      <Sequence name="World" {...span(13.35, 14.95)} premountFor={fps}>
        <World start={13.35} />
      </Sequence>
      <Sequence name="Categories" {...span(17.3, 21.6)} premountFor={fps}>
        <Categories start={17.3} />
      </Sequence>
      <Sequence name="Google ranking" {...span(22.2, 26.6)} premountFor={fps}>
        <Ranking start={22.2} />
      </Sequence>
      <Sequence name="TV stack" {...span(26.6, 29.75)} premountFor={fps}>
        <TvCheck start={26.6} />
      </Sequence>
      <Sequence name="GONE" {...span(34.3, 35.15)} premountFor={fps}>
        <GoneTitle start={34.3} />
      </Sequence>
      <Sequence name="Kyun emoji" {...span(36.0, 37.6)} premountFor={fps}>
        <KyunPop start={36.0} />
      </Sequence>
      <Sequence name="CCTV" {...span(37.85, 39.6)} premountFor={fps}>
        <Cctv start={37.85} />
      </Sequence>
      <Sequence name="Paid links" {...span(39.6, 41.65)} premountFor={fps}>
        <PaidLinks start={39.6} />
      </Sequence>
      <Sequence name="Algorithm pop" {...span(44.3, 46.7)} premountFor={fps}>
        <AlgoPop start={44.3} />
      </Sequence>
      <Sequence name="Caught" {...span(46.75, 49.4)} premountFor={fps}>
        <Caught start={46.75} />
      </Sequence>
      <Sequence name="JCPenney reveal" {...span(49.55, 55.05)} premountFor={fps}>
        <Reveal start={49.55} />
      </Sequence>
      <Sequence name="Lesson" {...span(55.1, 60.15)} premountFor={fps}>
        <Lesson start={55.1} />
      </Sequence>
      <Sequence name="Types of SEO" {...span(67.0, 76.3)} premountFor={fps}>
        <TypesOfSeo start={67.0} />
      </Sequence>
      <Sequence name="End CTA" {...span(76.6, 77.95)} premountFor={fps}>
        <EndCta start={76.6} />
      </Sequence>

      {/* light leaks on the big beats */}
      <Sequence name="Leak 1" {...span(8.3, 8.9)}>
        <LightLeak />
      </Sequence>
      <Sequence name="Leak 2" {...span(49.3, 49.9)}>
        <LightLeak />
      </Sequence>
      <Sequence name="Leak 3" {...span(66.8, 67.4)}>
        <LightLeak color="#FF3B3B" />
      </Sequence>

      <ReelCaptions />

      <Audio
        name="Music"
        src={staticFile("music/curiosity.mp3")}
        volume={(fr) =>
          interpolate(
            fr,
            [0, 15, f(34.0), f(34.3), f(35.0), f(36.0), TOTAL_FRAMES - 40, TOTAL_FRAMES],
            [0, 0.15, 0.15, 0, 0, 0.15, 0.15, 0],
            { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
          )
        }
      />

      <Sfx at={1.7} src="whoosh-fast" lead={1.05} volume={0.35} />
      <Sfx at={1.76} src="glitch-hit" lead={0.25} volume={0.25} seconds={0.8} />
      <Sfx at={3.7} src="whoosh-fast" lead={1.05} volume={0.3} />
      <Sfx at={3.9} src="pop" volume={0.3} />
      <Sfx at={8.5} src="impact-trailer" lead={0.95} volume={0.3} />
      <Sfx at={11.15} src="whoosh-fast" lead={1.05} volume={0.3} />
      <Sfx at={11.3} src="pop" volume={0.3} />
      <Sfx at={13.35} src="whoosh-fast" lead={1.05} volume={0.3} />
      <Sfx at={17.3} src="whoosh-fast" lead={1.05} volume={0.3} />
      <Sfx at={17.64} src="pop" volume={0.28} />
      <Sfx at={18.32} src="pop" volume={0.28} />
      <Sfx at={19.3} src="pop" volume={0.28} />
      <Sfx at={20.52} src="pop" volume={0.28} />
      <Sfx at={22.2} src="whoosh-fast" lead={1.05} volume={0.3} />
      <Sfx at={22.3} src="typing" volume={0.3} seconds={0.9} />
      <Sfx at={24.9} src="glitch-hit" lead={0.25} volume={0.25} seconds={0.9} />
      <Sfx at={26.6} src="whoosh-fast" lead={1.05} volume={0.3} />
      <Sfx at={26.75} src="pop" volume={0.28} />
      <Sfx at={27.72} src="pop" volume={0.28} />
      <Sfx at={28.88} src="pop" volume={0.28} />
      <Sfx at={32.9} src="glitch-hit" lead={0.25} volume={0.3} seconds={1.4} />
      <Sfx at={34.36} src="impact-big" lead={2.15} volume={0.6} seconds={5} />
      <Sfx at={36.1} src="heartbeat-impact" lead={0.05} volume={0.45} />
      <Sfx at={37.85} src="shutter" lead={0.15} volume={0.45} />
      <Sfx at={39.6} src="whoosh-fast" lead={1.05} volume={0.3} />
      <Sfx at={40.66} src="impact-trailer" lead={0.95} volume={0.4} />
      <Sfx at={44.56} src="pop" volume={0.3} />
      <Sfx at={45.62} src="glitch-hit" lead={0.25} volume={0.25} seconds={0.8} />
      <Sfx at={46.75} src="whoosh-fast" lead={1.05} volume={0.3} />
      <Sfx at={48.4} src="impact-trailer" lead={0.95} volume={0.5} />
      <Sfx at={49.55} src="whoosh-fast" lead={1.05} volume={0.3} />
      <Sfx at={50.86} src="impact-big" lead={2.15} volume={0.45} seconds={4} />
      <Sfx at={55.1} src="whoosh-fast" lead={1.05} volume={0.3} />
      <Sfx at={59.24} src="pop" volume={0.3} />
      <Sfx at={67.0} src="impact-trailer" lead={0.95} volume={0.35} />
      <Sfx at={69.4} src="pop" volume={0.28} />
      <Sfx at={70.42} src="pop" volume={0.28} />
      <Sfx at={72.06} src="glitch-hit" lead={0.25} volume={0.18} seconds={0.6} />
      <Sfx at={73.88} src="glitch-hit" lead={0.25} volume={0.18} seconds={0.6} />
      <Sfx at={75.04} src="glitch-hit" lead={0.25} volume={0.18} seconds={0.6} />
      <Sfx at={77.0} src="pop" volume={0.35} />
    </AbsoluteFill>
  );
};
