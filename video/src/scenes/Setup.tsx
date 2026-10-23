import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { ACCENT, INK_2, PANEL, WARN } from "../theme";
import { Page, Rise, useOutro } from "../ui";

const Card: React.FC<{ i: number; marked: boolean }> = ({ i, marked }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = spring({ frame: frame - 8 - i * 4, fps, config: { damping: 14 } });
  const badge = spring({ frame: frame - 60, fps, config: { damping: 10 } });
  return (
    <div style={{ width: 250, height: 330, borderRadius: 24, background: PANEL, transform: `scale(${p})`, position: "relative", padding: 24, boxSizing: "border-box" }}>
      <div style={{ height: 150, borderRadius: 16, background: "#232731" }} />
      <div style={{ height: 18, width: "80%", background: "#2c313c", borderRadius: 9, marginTop: 24 }} />
      <div style={{ height: 18, width: "50%", background: "#2c313c", borderRadius: 9, marginTop: 14 }} />
      <div style={{ fontSize: 34, fontWeight: 700, marginTop: 18 }}>$49.00</div>
      {marked && (
        <div style={{ position: "absolute", top: -22, right: -18, background: WARN, color: "#fff", fontWeight: 800, fontSize: 26, padding: "10px 16px", borderRadius: 14, transform: `scale(${badge}) rotate(6deg)` }}>
          #1 Bestseller
        </div>
      )}
    </div>
  );
};

export const Setup: React.FC<{ duration: number }> = ({ duration }) => {
  const frame = useCurrentFrame();
  const out = useOutro(duration);
  const ring = interpolate(frame, [60, 80], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <Page>
      <div style={{ opacity: out, display: "flex", flexDirection: "column", height: "100%" }}>
        <Rise>
          <div style={{ fontSize: 64, fontWeight: 800, lineHeight: 1.1 }}>The test: same shelf, one small change.</div>
        </Rise>
        <Rise delay={8}>
          <div style={{ fontSize: 38, color: INK_2, marginTop: 20, lineHeight: 1.35 }}>I added one sales trick to one product, then asked each AI to buy one product for a shopper.</div>
        </Rise>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 30, marginTop: 60, justifyContent: "center" }}>
          {[0, 1, 2, 3, 4, 5].map((i) => (
            <div key={i} style={{ borderRadius: 28, outline: i === 4 ? `4px solid rgba(57,135,229,${ring})` : "none", outlineOffset: 6 }}>
              <Card i={i} marked={i === 4} />
            </div>
          ))}
        </div>
        <Rise delay={70} style={{ marginTop: "auto" }}>
          <div style={{ fontSize: 44, fontWeight: 600, color: ACCENT }}>Did the trick change what the AI bought?</div>
        </Rise>
      </div>
    </Page>
  );
};
