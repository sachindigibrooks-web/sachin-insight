import { Composition } from "remotion";
import { MAIN_FRAMES, Main } from "./Main";
import { FPS } from "./timeline";
import { ReelMain } from "./reel/ReelMain";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="JCPenneySEO"
        component={Main}
        durationInFrames={MAIN_FRAMES}
        fps={FPS}
        width={1920}
        height={1080}
      />
      <Composition
        id="JCPenneySEO-Reels"
        component={Main}
        durationInFrames={MAIN_FRAMES}
        fps={FPS}
        width={1080}
        height={1920}
      />
      <Composition
        id="JCPenneySEO-Short"
        component={ReelMain}
        durationInFrames={MAIN_FRAMES}
        fps={FPS}
        width={1080}
        height={1920}
      />
    </>
  );
};
