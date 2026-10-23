import { AbsoluteFill } from "remotion";
import { trickRow } from "./data";
import { haikuBadge, routerClear } from "./phase2";
import { ACCENT, BG, FONT, INK, INK_2, PANEL, WARN } from "./theme";

const badge = trickRow("badge");

/** LinkedIn cover frame (1080 x 1350). */
export const Cover: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: BG, fontFamily: FONT, color: INK, padding: 90 }}>
    <AbsoluteFill style={{ background: "radial-gradient(circle at 20% 10%, rgba(57,135,229,0.25) 0%, rgba(14,16,20,0) 50%)" }} />
    <div style={{ fontSize: 38, fontWeight: 600, color: ACCENT, letterSpacing: 1 }}>AI SHOPPER EXPERIMENT</div>
    <div style={{ fontSize: 104, fontWeight: 800, lineHeight: 1.02, marginTop: 24 }}>We tried to trick 5 AI shoppers.</div>
    <div style={{ background: PANEL, borderRadius: 32, padding: "44px 50px", marginTop: 56 }}>
      <div style={{ fontSize: 40, fontWeight: 700 }}>A fake "#1 Bestseller" badge</div>
      <div style={{ display: "flex", alignItems: "baseline", gap: 26, marginTop: 14 }}>
        <div style={{ fontSize: 88, fontWeight: 800, color: INK_2 }}>{badge.haiku.control_share_pp.toFixed(0)}%</div>
        <div style={{ fontSize: 70, color: INK_2 }}>→</div>
        <div style={{ fontSize: 150, fontWeight: 800, color: WARN, lineHeight: 1 }}>{badge.haiku.treated_share_pp.toFixed(0)}%</div>
      </div>
      <div style={{ fontSize: 32, color: INK_2, marginTop: 14 }}>
        how often Claude Haiku bought it. The frontier models didn't budge.
      </div>
    </div>
    <div style={{ display: "flex", gap: 28, marginTop: 28 }}>
      <div style={{ flex: 1, background: PANEL, borderRadius: 28, padding: "30px 34px" }}>
        <div style={{ fontSize: 30, fontWeight: 700, lineHeight: 1.25 }}>With Jev's shield</div>
        <div style={{ fontSize: 96, fontWeight: 800, color: ACCENT, marginTop: 6 }}>+{haikuBadge.shield.toFixed(0)} pts</div>
        <div style={{ fontSize: 26, color: INK_2 }}>badge effect, down from +{haikuBadge.none.toFixed(0)}</div>
      </div>
      <div style={{ flex: 1, background: PANEL, borderRadius: 28, padding: "30px 34px" }}>
        <div style={{ fontSize: 30, fontWeight: 700, lineHeight: 1.25 }}>Jev routing</div>
        <div style={{ fontSize: 96, fontWeight: 800, color: ACCENT, marginTop: 6 }}>{routerClear.routed_agree_pp.toFixed(0)}%</div>
        <div style={{ fontSize: 26, color: INK_2 }}>of Opus's picks, at {(100 * routerClear.routed_cost_per_1k_usd / routerClear.strong_cost_per_1k_usd).toFixed(0)}% of the cost</div>
      </div>
    </div>
    <div style={{ marginTop: "auto", fontSize: 32, color: INK_2 }}>Claude · GPT · Gemini · protected by Jev</div>
  </AbsoluteFill>
);
