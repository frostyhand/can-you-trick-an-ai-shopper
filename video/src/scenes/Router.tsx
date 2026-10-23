import { spring, useCurrentFrame, useVideoConfig } from "remotion";
import { routerClear } from "../phase2";
import { ACCENT, INK_2, MUTED, PANEL } from "../theme";
import { countUp, Page, Rise, useOutro } from "../ui";

export const Router: React.FC<{ duration: number }> = ({ duration }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const out = useOutro(duration, 20);
  const r = routerClear;
  const pop = spring({ frame: frame - 70, fps, config: { damping: 12 } });
  const agree = countUp(frame, 0, r.routed_agree_pp, 75, 40);
  const share = (100 * r.routed_cost_per_1k_usd) / r.strong_cost_per_1k_usd;
  return (
    <Page>
      <div style={{ opacity: out, display: "flex", flexDirection: "column", height: "100%" }}>
        <Rise>
          <div style={{ fontSize: 62, fontWeight: 800, lineHeight: 1.1 }}>Then Jev decides who should shop.</div>
        </Rise>
        <Rise delay={12}>
          <div style={{ fontSize: 34, color: INK_2, marginTop: 18, lineHeight: 1.35 }}>
            Easy call: the small, cheap model buys. Hard call: Jev hands it to Claude Opus. On shelves with a clear best pick, it handed over{" "}
            <span style={{ color: "#fff", fontWeight: 700 }}>{r.escalated_pp.toFixed(0)}%</span>.
          </div>
        </Rise>
        <div style={{ display: "flex", gap: 26, marginTop: 60, transform: `scale(${pop})`, transformOrigin: "left top" }}>
          <div style={{ flex: 1, background: PANEL, borderRadius: 28, padding: "34px 36px" }}>
            <div style={{ fontSize: 30, color: INK_2 }}>Same pick as Opus</div>
            <div style={{ fontSize: 118, fontWeight: 800, color: ACCENT, lineHeight: 1.05 }}>{agree.toFixed(0)}%</div>
            <div style={{ fontSize: 26, color: MUTED }}>Haiku alone: {r.cheap_agree_pp.toFixed(0)}% · random: {r.random_agree_pp.toFixed(0)}%</div>
          </div>
          <div style={{ flex: 1, background: PANEL, borderRadius: 28, padding: "34px 36px" }}>
            <div style={{ fontSize: 30, color: INK_2 }}>Cost vs Opus alone</div>
            <div style={{ fontSize: 118, fontWeight: 800, lineHeight: 1.05 }}>{share.toFixed(0)}%</div>
            <div style={{ fontSize: 26, color: MUTED }}>${r.routed_cost_per_1k_usd.toFixed(2)} vs ${r.strong_cost_per_1k_usd.toFixed(2)} per 1,000</div>
          </div>
        </div>
      </div>
    </Page>
  );
};
