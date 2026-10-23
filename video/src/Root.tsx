import { Composition, Still } from "remotion";
import { Cover } from "./Cover";
import { AIShopper, TOTAL_FRAMES } from "./Video";

export const RemotionRoot: React.FC = () => (
  <>
    <Composition id="AIShopper" component={AIShopper} durationInFrames={TOTAL_FRAMES} fps={30} width={1080} height={1350} />
    <Still id="Cover" component={Cover} width={1080} height={1350} />
  </>
);
