import { interpolate, useCurrentFrame } from "remotion";
import { acc, haikuBadge, haikuFool } from "../phase2";
import { ACCENT, INK_2, PANEL, WARN } from "../theme";
import { countUp, Page, Rise, useOutro } from "../ui";

const Bar: React.FC<{ label: string; value: number; max: number; color: string; delay: number }> = ({ label, value, max, color, delay }) => {
  const frame = useCurrentFrame();
  const grow = interpolate(frame, [delay, delay + 40], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const v = countUp(frame, 0, value, delay, 40);
  return (
    <div style={{ marginTop: 26 }}>
      <div style={{ fontSize: 32, color: INK_2 }}>{label}</div>
      <div style={{ display: "flex", alignItems: "center", gap: 18, marginTop: 10 }}>
        <div style={{ height: 54, width: Math.max(6, (Math.max(0, value) / max) * 620 * grow), background: color, borderRadius: "0 12px 12px 0" }} />
        <div style={{ fontSize: 54, fontWeight: 800 }}>{v >= 0 ? "+" : ""}{v.toFixed(1)} pts</div>
      </div>
    </div>
  );
};

export const ShieldResult: React.FC<{ duration: number }> = ({ duration }) => {
  const out = useOutro(duration, 20);
  const max = Math.max(haikuBadge.none, 1);
  return (
    <Page>
      <div style={{ opacity: out, display: "flex", flexDirection: "column", height: "100%" }}>
        <Rise>
          <div style={{ fontSize: 62, fontWeight: 800, lineHeight: 1.1 }}>The tricks stopped working.</div>
        </Rise>
        <Rise delay={10}>
          <div style={{ fontSize: 32, color: INK_2, marginTop: 14 }}>How much a fake "#1 Bestseller" badge swayed Claude Haiku (identical shelves)</div>
        </Rise>
        <Bar label="Without a shield" value={haikuBadge.none} max={max} color={WARN} delay={30} />
        <Bar label="With Jev's shield" value={haikuBadge.shield} max={max} color={ACCENT} delay={80} />
        <Rise delay={140} style={{ marginTop: "auto" }}>
          <div style={{ background: PANEL, borderRadius: 24, padding: "28px 34px", fontSize: 32, lineHeight: 1.4 }}>
            Jev caught <b>{acc.manipulative_recall_pp.toFixed(1)}%</b> of the planted tricks and{" "}
            <b>{acc.heldout_trick_recall}</b> tricks worded in ways it had never seen. Across all tricks, Haiku went from{" "}
            <b>+{haikuFool.none.toFixed(1)}</b> to <b>+{haikuFool.shield.toFixed(1)}</b> points.
          </div>
        </Rise>
      </div>
    </Page>
  );
};
