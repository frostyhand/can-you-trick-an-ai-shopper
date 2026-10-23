import { ColumnGroups } from "../bars";
import { backfire, OVERT_SENTENCE } from "../data";
import { INK_2, PANEL } from "../theme";
import { countUp, Page, Rise, useOutro } from "../ui";
import { useCurrentFrame } from "remotion";

export const Hijack: React.FC<{ duration: number }> = ({ duration }) => {
  const frame = useCurrentFrame();
  const out = useOutro(duration);
  const typed = Math.floor(countUp(frame, 0, OVERT_SENTENCE.length, 20, 50));
  return (
    <Page>
      <div style={{ opacity: out, display: "flex", flexDirection: "column", height: "100%" }}>
        <Rise>
          <div style={{ fontSize: 60, fontWeight: 800, lineHeight: 1.1 }}>I hid a message telling the AI what to buy. It backfired.</div>
        </Rise>
        <Rise delay={8}>
          <div style={{ marginTop: 36, background: PANEL, borderRadius: 24, padding: "28px 34px" }}>
            <div style={{ fontSize: 30, fontWeight: 700 }}>Electric kettle · $48.00 · 4.5 stars</div>
            <div style={{ fontSize: 28, color: INK_2, marginTop: 14, lineHeight: 1.4 }}>
              Solid build and simple controls for daily use.{" "}
              <span style={{ color: "#fff", background: "rgba(230,103,103,0.28)", borderRadius: 6, padding: "0 6px" }}>
                {OVERT_SENTENCE.slice(0, typed)}
              </span>
            </div>
          </div>
        </Rise>
        <div style={{ marginTop: 56 }}>
          <ColumnGroups
            delay={90}
            max={30}
            height={460}
            barWidth={190}
            groups={[
              { title: "Big AIs: purchases out of 100", subtitle: "Claude Sonnet & Opus, GPT, Gemini", bars: [
                { label: "Normal page", value: backfire.frontierControl, color: "#5b5e66" },
                { label: "With hidden message", value: backfire.frontierTreated, color: "#3987e5" },
              ] },
            ]}
          />
        </div>
      </div>
    </Page>
  );
};
