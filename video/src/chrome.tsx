import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { totalDecisions, totalShelves, MODELS } from "./data";
import { phase2Decisions } from "./phase2";
import { GITHUB_URL } from "./handle";
import { ACCENT, FONT, MUTED } from "./theme";

/** Two slow-drifting glows behind the content scenes. */
export const Glow: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / 30;
  const x1 = 25 + Math.sin(t / 3) * 10;
  const y1 = 20 + Math.cos(t / 4) * 8;
  const x2 = 80 + Math.cos(t / 5) * 8;
  const y2 = 85 + Math.sin(t / 3.5) * 6;
  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(circle at ${x1}% ${y1}%, rgba(57,135,229,0.16) 0%, rgba(14,16,20,0) 45%),
                     radial-gradient(circle at ${x2}% ${y2}%, rgba(230,103,103,0.10) 0%, rgba(14,16,20,0) 40%)`,
      }}
    />
  );
};

/** Thin progress line along the top edge. */
export const Progress: React.FC = () => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const w = interpolate(frame, [0, durationInFrames - 1], [0, 100]);
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <div style={{ position: "absolute", top: 0, left: 0, height: 8, width: `${w}%`, background: ACCENT }} />
    </AbsoluteFill>
  );
};

/** Study name in the bottom corner, hidden on the opening and closing scenes. */
export const Footer: React.FC<{ hideBefore: number; hideAfter: number }> = ({ hideBefore, hideAfter }) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [hideBefore, hideBefore + 10, hideAfter - 10, hideAfter], [0, 1, 1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <AbsoluteFill style={{ pointerEvents: "none", fontFamily: FONT }}>
      <div style={{ position: "absolute", bottom: 34, left: 90, fontSize: 24, color: MUTED, opacity: o, letterSpacing: 0.5, whiteSpace: "nowrap" }}>
        <span style={{ color: "#fff", fontWeight: 700 }}>{GITHUB_URL}</span> · {(totalDecisions + phase2Decisions).toLocaleString("en-US")} AI purchases tested
      </div>
    </AbsoluteFill>
  );
};
