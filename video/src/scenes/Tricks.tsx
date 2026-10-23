import { interpolate, useCurrentFrame } from "remotion";
import { trickRow } from "../data";
import { INK_2, MUTED, PANEL, SERIES, WARN } from "../theme";
import { countUp, Page, Rise, useOutro } from "../ui";

const ROWS = ["badge", "anchor", "urgency", "scarcity"].map(trickRow);
const COLS: { key: "haiku" | "frontier"; name: string; sub: string; color: string }[] = [
  { key: "haiku", name: "Haiku 5.5", sub: "Claude", color: SERIES.haiku },
  { key: "frontier", name: "Big 4", sub: "Sonnet, Opus, GPT, Gemini", color: SERIES.sonnet },
];

const Cell: React.FC<{ before: number; after: number; delay: number }> = ({ before, after, delay }) => {
  const frame = useCurrentFrame();
  const v = countUp(frame, before, after, delay, 30);
  const up = after - before > 5;
  const down = after - before < -5;
  return (
    <div style={{ width: 230, textAlign: "center" }}>
      <div style={{ fontSize: 26, color: MUTED }}>{before.toFixed(0)}% →</div>
      <div style={{ fontSize: 64, fontWeight: 800, color: up ? WARN : down ? "#7fb8ff" : "#fff", lineHeight: 1.05 }}>{v.toFixed(0)}%</div>
    </div>
  );
};

export const Tricks: React.FC<{ duration: number }> = ({ duration }) => {
  const frame = useCurrentFrame();
  const out = useOutro(duration);
  return (
    <Page padding={70}>
      <div style={{ opacity: out }}>
        <Rise>
          <div style={{ fontSize: 60, fontWeight: 800, lineHeight: 1.1 }}>Store tricks fooled 1 of 5 AIs.</div>
        </Rise>
        <Rise delay={6}>
          <div style={{ fontSize: 32, color: INK_2, marginTop: 14 }}>How often each AI bought the product, before → after the trick (identical shelves)</div>
        </Rise>
        <div style={{ display: "flex", marginTop: 46, marginLeft: 420 }}>
          {COLS.map((c, i) => (
            <Rise key={c.key} delay={10 + i * 4} style={{ width: 260, textAlign: "center" }}>
              <div style={{ height: 8, width: 60, background: c.color, borderRadius: 4, margin: "0 auto 12px" }} />
              <div style={{ fontSize: 32, fontWeight: 800 }}>{c.name}</div>
              <div style={{ fontSize: 20, color: MUTED, marginTop: 4 }}>{c.sub}</div>
            </Rise>
          ))}
        </div>
        {ROWS.map((r, i) => {
          const show = interpolate(frame, [24 + i * 22, 36 + i * 22], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          return (
            <div key={r.trick} style={{ opacity: show, display: "flex", alignItems: "center", background: i % 2 ? "transparent" : PANEL, borderRadius: 22, padding: "18px 0", marginTop: 18 }}>
              <div style={{ width: 420, paddingLeft: 26, fontSize: 32, fontWeight: 700, boxSizing: "border-box" }}>{r.label}</div>
              {COLS.map((c) => (
                <Cell key={c.key} before={r[c.key].control_share_pp} after={r[c.key].treated_share_pp} delay={30 + i * 22} />
              ))}
            </div>
          );
        })}
      </div>
    </Page>
  );
};
