import { AbsoluteFill, Audio, interpolate, Sequence, staticFile, useVideoConfig } from "remotion";
import { ASSETS } from "./assets";
import { Cta } from "./scenes/Cta";
import { Hijack } from "./scenes/Hijack";
import { Hook } from "./scenes/Hook";
import { Tricks } from "./scenes/Tricks";
import { Wins } from "./scenes/Wins";
import { Models } from "./scenes/Models";
import { Setup } from "./scenes/Setup";
import { Footer, Glow, Progress } from "./chrome";
import { BG } from "./theme";

// 40 s at 30 fps, matching the 39-second edit of the music track.
const SCENES = [
  { id: "hook", from: 0, duration: 105 },
  { id: "setup", from: 105, duration: 120 },
  { id: "tricks", from: 225, duration: 240 },
  { id: "hijack", from: 465, duration: 225 },
  { id: "wins", from: 690, duration: 195 },
  { id: "models", from: 885, duration: 165 },
  { id: "cta", from: 1050, duration: 150 },
] as const;
export const TOTAL_FRAMES = 1200;

// Frames (absolute) where a pop accents a number landing.
const POPS = [465 + 95, 690 + 18, 690 + 53];

const Sfx: React.FC<{ file: string | null; at: number; volume: number }> = ({ file, at, volume }) =>
  file ? (
    <Sequence from={Math.max(0, at)} durationInFrames={60}>
      <Audio src={staticFile(`envato/${file}`)} volume={volume} />
    </Sequence>
  ) : null;

export const AIShopper: React.FC = () => {
  const { durationInFrames } = useVideoConfig();
  const [hook, setup, tricks, hijack, wins, models, cta] = SCENES;
  return (
    <AbsoluteFill style={{ backgroundColor: BG }}>
      <Glow />
      {ASSETS.music && (
        <Audio
          src={staticFile(`envato/${ASSETS.music}`)}
          volume={(f) => interpolate(f, [0, 15, durationInFrames - 30, durationInFrames], [0, 0.65, 0.65, 0], { extrapolateRight: "clamp" })}
        />
      )}
      {SCENES.slice(1).map((sc) => (
        <Sfx key={sc.id} file={ASSETS.whoosh} at={sc.from - 8} volume={0.35} />
      ))}
      {POPS.map((f) => (
        <Sfx key={f} file={ASSETS.pop} at={f} volume={0.6} />
      ))}
      <Sequence from={hook.from} durationInFrames={hook.duration}><Hook duration={hook.duration} /></Sequence>
      <Sequence from={setup.from} durationInFrames={setup.duration}><Setup duration={setup.duration} /></Sequence>
      <Sequence from={tricks.from} durationInFrames={tricks.duration}><Tricks duration={tricks.duration} /></Sequence>
      <Sequence from={hijack.from} durationInFrames={hijack.duration}><Hijack duration={hijack.duration} /></Sequence>
      <Sequence from={wins.from} durationInFrames={wins.duration}><Wins duration={wins.duration} /></Sequence>
      <Sequence from={models.from} durationInFrames={models.duration}><Models duration={models.duration} /></Sequence>
      <Sequence from={cta.from} durationInFrames={cta.duration}><Cta /></Sequence>
      <Footer hideBefore={setup.from} hideAfter={cta.from} />
      <Progress />
    </AbsoluteFill>
  );
};
