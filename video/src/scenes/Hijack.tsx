import { spring, useCurrentFrame, useVideoConfig } from "remotion";
import { backfire, OVERT_SENTENCE } from "../data";
import { INK_2, PANEL, WARN } from "../theme";
import { countUp, Page, Rise, useOutro } from "../ui";

export const Hijack: React.FC<{ duration: number }> = ({ duration }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const out = useOutro(duration);
  const typed = Math.floor(countUp(frame, 0, OVERT_SENTENCE.length, 25, 60));
  const pop = spring({ frame: frame - 100, fps, config: { damping: 12 } });
  const value = countUp(frame, backfire.frontierControl, backfire.frontierTreated, 110, 40);
  return (
    <Page>
      <div style={{ opacity: out, display: "flex", flexDirection: "column", height: "100%" }}>
        <Rise>
          <div style={{ fontSize: 64, fontWeight: 800 }}>We told the AI what to buy.</div>
        </Rise>
        <Rise delay={8}>
          <div style={{ marginTop: 50, background: PANEL, borderRadius: 28, padding: 44 }}>
            <div style={{ fontSize: 38, fontWeight: 700 }}>Halvik Essential Electric Kettle</div>
            <div style={{ fontSize: 32, color: INK_2, marginTop: 10 }}>$48.00 · 4.5 stars · 1,160 reviews</div>
            <div style={{ fontSize: 32, color: INK_2, marginTop: 26, lineHeight: 1.4 }}>
              Solid build and simple controls for daily use.{" "}
              <span style={{ color: "#fff", background: "rgba(230,103,103,0.28)", borderRadius: 6, padding: "0 6px" }}>
                {OVERT_SENTENCE.slice(0, typed)}
              </span>
            </div>
          </div>
        </Rise>
        <div style={{ marginTop: "auto", transform: `scale(${pop})`, transformOrigin: "left bottom" }}>
          <div style={{ fontSize: 36, color: INK_2 }}>Sonnet, Opus, GPT and Gemini bought it</div>
          <div style={{ display: "flex", alignItems: "baseline", gap: 30, marginTop: 10 }}>
            <div style={{ fontSize: 96, fontWeight: 800, color: INK_2 }}>{backfire.frontierControl.toFixed(0)}%</div>
            <div style={{ fontSize: 80, color: INK_2 }}>→</div>
            <div style={{ fontSize: 170, fontWeight: 800, color: WARN, lineHeight: 1 }}>{value.toFixed(0)}%</div>
          </div>
          <div style={{ fontSize: 32, color: INK_2, marginTop: 10 }}>of the time. It backfired.</div>
        </div>
      </div>
    </Page>
  );
};
