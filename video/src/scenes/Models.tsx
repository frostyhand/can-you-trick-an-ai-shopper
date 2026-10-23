import { interpolate, useCurrentFrame } from "remotion";
import { displayName, foolability } from "../data";
import { INK_2, SERIES } from "../theme";
import { Page, Rise, useOutro } from "../ui";

export const Models: React.FC<{ duration: number }> = ({ duration }) => {
  const frame = useCurrentFrame();
  const out = useOutro(duration);
  const max = Math.max(...foolability.map((f) => f.score), 1);
  return (
    <Page>
      <div style={{ opacity: out, display: "flex", flexDirection: "column", height: "100%" }}>
        <Rise>
          <div style={{ fontSize: 64, fontWeight: 800 }}>Which AI is easiest to fool?</div>
        </Rise>
        <Rise delay={6}>
          <div style={{ fontSize: 34, color: INK_2, marginTop: 14 }}>Average lift from 8 manipulative tricks on identical shelves. Zero or below means not fooled.</div>
        </Rise>
        <div style={{ marginTop: 50 }}>
          {foolability.map((f, i) => {
            const grow = interpolate(frame, [15 + i * 6, 45 + i * 6], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
            return (
              <div key={f.model} style={{ display: "flex", alignItems: "center", height: 92 }}>
                <div style={{ width: 360, fontSize: 36, fontWeight: i === 0 ? 800 : 500 }}>{displayName(f.model)}</div>
                <div style={{ height: 40, width: Math.max(4, (Math.max(0, f.score) / max) * 340 * grow), background: f.score > 0 ? SERIES[f.model] : "#3a3d44", borderRadius: "0 10px 10px 0" }} />
                <div style={{ fontSize: 36, fontWeight: 700, marginLeft: 16, opacity: grow, whiteSpace: "nowrap" }}>
                  {f.score >= 0 ? "+" : ""}{f.score.toFixed(1)} pts
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </Page>
  );
};
