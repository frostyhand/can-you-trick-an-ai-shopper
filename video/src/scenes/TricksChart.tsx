import { ColumnGroups } from "../bars";
import { trickRow } from "../data";
import { INK_2, MUTED, PANEL, WARN } from "../theme";
import { Page, Rise, useOutro } from "../ui";

const badge = trickRow("badge");
const anchor = trickRow("anchor");
const GRAY = "#5b5e66";

export const TricksChart: React.FC<{ duration: number }> = ({ duration }) => {
  const out = useOutro(duration);
  return (
    <Page>
      <div style={{ opacity: out, display: "flex", flexDirection: "column", height: "100%" }}>
        <Rise>
          <div style={{ fontSize: 58, fontWeight: 800, lineHeight: 1.1 }}>A fake "#1 Bestseller" badge fooled the small AI. Not the big ones.</div>
        </Rise>
        <Rise delay={10}>
          <div style={{ fontSize: 32, color: INK_2, marginTop: 14 }}>Purchases out of 100, when the products were equally good</div>
        </Rise>
        <div style={{ marginTop: 50 }}>
          <ColumnGroups
            delay={30}
            max={100}
            height={470}
            groups={[
              { title: "Small AI", subtitle: "Claude Haiku", bars: [
                { label: "No badge", value: badge.haiku.control_share_pp, color: GRAY },
                { label: "With badge", value: badge.haiku.treated_share_pp, color: WARN },
              ] },
              { title: "Big AIs", subtitle: "Claude Sonnet & Opus, GPT, Gemini", bars: [
                { label: "No badge", value: badge.frontier.control_share_pp, color: GRAY },
                { label: "With badge", value: badge.frontier.treated_share_pp, color: "#3987e5" },
              ] },
            ]}
          />
        </div>
        <Rise delay={150} style={{ marginTop: "auto" }}>
          <div style={{ background: PANEL, borderRadius: 22, padding: "24px 30px", fontSize: 30, lineHeight: 1.4 }}>
            A fake "was $70, now $48" price did the same: small AI{" "}
            <b>{Math.round(anchor.haiku.control_share_pp)} → {Math.round(anchor.haiku.treated_share_pp)}</b>, big AIs{" "}
            <b>{Math.round(anchor.frontier.control_share_pp)} → {Math.round(anchor.frontier.treated_share_pp)}</b>.
            <span style={{ color: MUTED }}> (out of 100)</span>
          </div>
        </Rise>
      </div>
    </Page>
  );
};
