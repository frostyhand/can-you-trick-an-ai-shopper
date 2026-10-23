import { AbsoluteFill } from "remotion";
import { trickRow } from "./data";
import { GITHUB_URL } from "./handle";
import { haikuBadge, routerClear } from "./phase2";
import { ACCENT, BG, FONT, INK, INK_2, MUTED, PANEL, WARN } from "./theme";

const badge = trickRow("badge");

/** LinkedIn cover frame (1080 x 1350). */
export const Cover: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: BG, fontFamily: FONT, color: INK, padding: 90 }}>
    <AbsoluteFill style={{ background: "radial-gradient(circle at 20% 10%, rgba(57,135,229,0.25) 0%, rgba(14,16,20,0) 50%)" }} />
    <div style={{ fontSize: 36, fontWeight: 600, color: ACCENT, letterSpacing: 1 }}>AN AI SHOPPING EXPERIMENT</div>
    <div style={{ fontSize: 100, fontWeight: 800, lineHeight: 1.02, marginTop: 22 }}>I tried to trick 5 AI shoppers.</div>
    <div style={{ background: PANEL, borderRadius: 32, padding: "40px 46px", marginTop: 50 }}>
      <div style={{ fontSize: 38, fontWeight: 700 }}>A fake "#1 Bestseller" badge</div>
      <div style={{ display: "flex", alignItems: "baseline", gap: 24, marginTop: 12 }}>
        <div style={{ fontSize: 84, fontWeight: 800, color: INK_2 }}>{badge.haiku.control_share_pp.toFixed(0)}</div>
        <div style={{ fontSize: 64, color: INK_2 }}>→</div>
        <div style={{ fontSize: 140, fontWeight: 800, color: WARN, lineHeight: 1 }}>{badge.haiku.treated_share_pp.toFixed(0)}</div>
        <div style={{ fontSize: 34, color: INK_2 }}>purchases out of 100</div>
      </div>
      <div style={{ fontSize: 30, color: INK_2, marginTop: 12 }}>by the small AI. The big AIs ignored it.</div>
    </div>
    <div style={{ display: "flex", gap: 26, marginTop: 26 }}>
      <div style={{ flex: 1, background: PANEL, borderRadius: 28, padding: "28px 32px" }}>
        <div style={{ fontSize: 30, fontWeight: 700 }}>Add a filter</div>
        <div style={{ fontSize: 88, fontWeight: 800, color: ACCENT, marginTop: 4 }}>{Math.round(haikuBadge.none)} → {Math.round(haikuBadge.shield)}</div>
        <div style={{ fontSize: 25, color: INK_2 }}>extra purchases per 100 from the badge</div>
      </div>
      <div style={{ flex: 1, background: PANEL, borderRadius: 28, padding: "28px 32px" }}>
        <div style={{ fontSize: 30, fontWeight: 700 }}>Route smartly</div>
        <div style={{ fontSize: 88, fontWeight: 800, color: ACCENT, marginTop: 4 }}>{routerClear.routed_agree_pp.toFixed(0)}%</div>
        <div style={{ fontSize: 25, color: INK_2 }}>of the top AI's choices at {(100 * routerClear.routed_cost_per_1k_usd / routerClear.strong_cost_per_1k_usd).toFixed(0)}% of the cost</div>
      </div>
    </div>
    <div style={{ marginTop: "auto", display: "flex", justifyContent: "space-between", fontSize: 32 }}>
      <div style={{ color: "#fff", fontWeight: 700 }}>{GITHUB_URL}</div>
      <div style={{ color: MUTED }}>Claude · GPT · Gemini · Jev</div>
    </div>
  </AbsoluteFill>
);
