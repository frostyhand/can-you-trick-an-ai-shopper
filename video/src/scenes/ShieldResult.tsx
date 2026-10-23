import { ColumnGroups } from "../bars";
import { acc, haikuBadge, newTricksHaiku } from "../phase2";
import { INK_2, PANEL, WARN } from "../theme";
import { Page, Rise, useOutro } from "../ui";

export const ShieldResult: React.FC<{ duration: number }> = ({ duration }) => {
  const out = useOutro(duration);
  return (
    <Page>
      <div style={{ opacity: out, display: "flex", flexDirection: "column", height: "100%" }}>
        <Rise>
          <div style={{ fontSize: 62, fontWeight: 800, lineHeight: 1.1 }}>With the filter, the tricks stopped working.</div>
        </Rise>
        <Rise delay={10}>
          <div style={{ fontSize: 32, color: INK_2, marginTop: 14 }}>Extra purchases out of 100 caused by the fake badge (small AI)</div>
        </Rise>
        <div style={{ marginTop: 44 }}>
          <ColumnGroups
            delay={30}
            max={50}
            height={420}
            groups={[
              { title: "", bars: [
                { label: "No filter", value: Math.max(0, haikuBadge.none), color: WARN },
                { label: "With Jev's filter", value: Math.max(0, haikuBadge.shield), color: "#3987e5" },
              ] },
            ]}
          />
        </div>
        <Rise delay={130} style={{ marginTop: "auto" }}>
          <div style={{ background: PANEL, borderRadius: 22, padding: "26px 32px", fontSize: 31, lineHeight: 1.45 }}>
            Caught <b>{acc.manipulative_recall_pp.toFixed(1)}%</b> of the tricks, and <b>{acc.heldout_trick_recall}</b> tricks worded in ways it had
            never seen. New tricks moved the small AI by {Math.round(newTricksHaiku.none)} extra purchases per 100 without the filter, {Math.round(newTricksHaiku.shield)} with it.
          </div>
        </Rise>
      </div>
    </Page>
  );
};
