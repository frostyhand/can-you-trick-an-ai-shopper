import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { FONT, INK } from "./theme";

export const Page: React.FC<{ children: React.ReactNode; padding?: number; transparent?: boolean }> = ({
  children,
  padding = 90,
  transparent = false,
}) => (
  <AbsoluteFill style={{ backgroundColor: transparent ? "transparent" : "rgba(0,0,0,0)", fontFamily: FONT, color: INK, padding }}>
    {children}
  </AbsoluteFill>
);

/** Fade and rise in, starting at `delay` frames. */
export const Rise: React.FC<{ delay?: number; children: React.ReactNode; style?: React.CSSProperties }> = ({ delay = 0, children, style }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = spring({ frame: frame - delay, fps, config: { damping: 200 } });
  return <div style={{ opacity: p, transform: `translateY(${(1 - p) * 40}px)`, ...style }}>{children}</div>;
};

/** Fade the whole scene out over its last frames. */
export const useOutro = (duration: number, length = 12) => {
  const frame = useCurrentFrame();
  return interpolate(frame, [duration - length, duration], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
};

export const countUp = (frame: number, from: number, to: number, start: number, length: number) =>
  interpolate(frame, [start, start + length], [from, to], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

/** Reveal a line word by word. */
export const Words: React.FC<{ text: string; delay?: number; every?: number; style?: React.CSSProperties }> = ({ text, delay = 0, every = 4, style }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <div style={style}>
      {text.split(" ").map((w, i) => {
        const p = spring({ frame: frame - delay - i * every, fps, config: { damping: 200 } });
        return (
          <span key={i} style={{ display: "inline-block", opacity: p, transform: `translateY(${(1 - p) * 30}px)`, marginRight: "0.25em" }}>
            {w}
          </span>
        );
      })}
    </div>
  );
};
