import { spring, useCurrentFrame, useVideoConfig } from "remotion";
import { ACCENT, INK_2, PANEL } from "../theme";
import { Page, Rise, useOutro } from "../ui";

const POINTS = [
  { n: "1", title: "Big AIs ignore marketing tricks. Small AIs don't.", body: "Fake badges and fake discounts only fooled the cheapest model." },
  { n: "2", title: "Product data wins the sale.", body: "Reviews and complete specs decide what an AI buys. Thin pages lose." },
  { n: "3", title: "Filter first, escalate when it matters.", body: "A fast filter plus smart routing gave near top-AI choices at under half the cost." },
];

export const Takeaways: React.FC<{ duration: number }> = ({ duration }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const out = useOutro(duration);
  return (
    <Page>
      <div style={{ opacity: out }}>
        <Rise>
          <div style={{ fontSize: 66, fontWeight: 800 }}>What this means</div>
        </Rise>
        {POINTS.map((p, i) => {
          const s = spring({ frame: frame - 18 - i * 34, fps, config: { damping: 200 } });
          return (
            <div key={p.n} style={{ opacity: s, transform: `translateX(${(1 - s) * 40}px)`, display: "flex", gap: 28, background: PANEL, borderRadius: 26, padding: "32px 34px", marginTop: 30 }}>
              <div style={{ fontSize: 64, fontWeight: 800, color: ACCENT, lineHeight: 1 }}>{p.n}</div>
              <div>
                <div style={{ fontSize: 40, fontWeight: 800, lineHeight: 1.15 }}>{p.title}</div>
                <div style={{ fontSize: 30, color: INK_2, marginTop: 10, lineHeight: 1.35 }}>{p.body}</div>
              </div>
            </div>
          );
        })}
      </div>
    </Page>
  );
};
