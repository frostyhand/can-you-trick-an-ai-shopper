import { AbsoluteFill, Audio, interpolate, Sequence, staticFile, useVideoConfig } from "remotion";
import { ASSETS } from "./assets";
import { Footer, Glow, Progress } from "./chrome";
import { Cta } from "./scenes/Cta";
import { Hijack } from "./scenes/Hijack";
import { Hook } from "./scenes/Hook";
import { Router } from "./scenes/Router";
import { Setup } from "./scenes/Setup";
import { ShieldIntro } from "./scenes/ShieldIntro";
import { ShieldResult } from "./scenes/ShieldResult";
import { Takeaways } from "./scenes/Takeaways";
import { TricksChart } from "./scenes/TricksChart";
import { Wins } from "./scenes/Wins";
import { BG } from "./theme";

// 68 s at 30 fps, matching the 68-second edit of the music track. Scenes hold 6 to 10 s.
const SCENES = [
  { id: "hook", from: 0, duration: 150 },
  { id: "setup", from: 150, duration: 150 },
  { id: "tricks", from: 300, duration: 270 },
  { id: "backfire", from: 570, duration: 195 },
  { id: "wins", from: 765, duration: 195 },
  { id: "shieldIntro", from: 960, duration: 240 },
  { id: "shieldResult", from: 1200, duration: 210 },
  { id: "router", from: 1410, duration: 240 },
  { id: "takeaways", from: 1650, duration: 210 },
  { id: "cta", from: 1860, duration: 180 },
] as const;
export const TOTAL_FRAMES = 2040;

// Frames (absolute) where a pop accents a number landing.
const POPS = [300 + 60, 570 + 100, 765 + 30, 1200 + 40, 1410 + 40];

const Sfx: React.FC<{ file: string | null; at: number; volume: number }> = ({ file, at, volume }) =>
  file ? (
    <Sequence from={Math.max(0, at)} durationInFrames={60}>
      <Audio src={staticFile(`envato/${file}`)} volume={volume} />
    </Sequence>
  ) : null;

const SCENE_COMPONENTS: Record<string, React.FC<{ duration: number }>> = {
  hook: Hook,
  setup: Setup,
  tricks: TricksChart,
  takeaways: Takeaways,
  backfire: Hijack,
  wins: Wins,
  shieldIntro: ShieldIntro,
  shieldResult: ShieldResult,
  router: Router,
  cta: () => <Cta />,
};

export const AIShopper: React.FC = () => {
  const { durationInFrames } = useVideoConfig();
  const cta = SCENES[SCENES.length - 1];
  return (
    <AbsoluteFill style={{ backgroundColor: BG }}>
      <Glow />
      {ASSETS.music && (
        <Audio
          src={staticFile(`envato/${ASSETS.music}`)}
          volume={(f) => interpolate(f, [0, 15, durationInFrames - 45, durationInFrames], [0, 0.65, 0.65, 0], { extrapolateRight: "clamp" })}
        />
      )}
      {SCENES.slice(1).map((sc) => (
        <Sfx key={sc.id} file={ASSETS.whoosh} at={sc.from - 10} volume={0.3} />
      ))}
      {POPS.map((f) => (
        <Sfx key={f} file={ASSETS.pop} at={f} volume={0.55} />
      ))}
      {SCENES.map((sc) => {
        const C = SCENE_COMPONENTS[sc.id];
        return (
          <Sequence key={sc.id} from={sc.from} durationInFrames={sc.duration}>
            <C duration={sc.duration} />
          </Sequence>
        );
      })}
      <Footer hideBefore={SCENES[1].from} hideAfter={cta.from} />
      <Progress />
    </AbsoluteFill>
  );
};
