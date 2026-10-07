import { Composition } from "remotion";
import { MAIN_FRAMES, Main } from "./Main";
import { FPS } from "./timeline";

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="JCPenneySEO"
      component={Main}
      durationInFrames={MAIN_FRAMES}
      fps={FPS}
      width={1920}
      height={1080}
    />
  );
};
