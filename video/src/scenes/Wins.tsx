import { spring, useCurrentFrame, useVideoConfig } from "remotion";
import { wins } from "../data";
import { ACCENT, INK_2, PANEL, WARN } from "../theme";
import { countUp, Page, Rise, useOutro } from "../ui";

const Stat: React.FC<{ delay: number; title: string; from: number; to: number; color: string; note: string }> = ({ delay, title, from, to, color, note }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = spring({ frame: frame - delay, fps, config: { damping: 14 } });
  const v = countUp(frame, from, to, delay + 8, 30);
  return (
    <div style={{ background: PANEL, borderRadius: 30, padding: "40px 46px", marginTop: 34, transform: `scale(${0.9 + 0.1 * p})`, opacity: p }}>
      <div style={{ fontSize: 40, fontWeight: 700 }}>{title}</div>
      <div style={{ display: "flex", alignItems: "baseline", gap: 24, marginTop: 8 }}>
        <div style={{ fontSize: 150, fontWeight: 800, color, lineHeight: 1 }}>{v.toFixed(0)}%</div>
        <div style={{ fontSize: 30, color: INK_2, lineHeight: 1.3 }}>{note}</div>
      </div>
    </div>
  );
};

export const Wins: React.FC<{ duration: number }> = ({ duration }) => {
  const out = useOutro(duration);
  return (
    <Page>
      <div style={{ opacity: out }}>
        <Rise>
          <div style={{ fontSize: 64, fontWeight: 800, lineHeight: 1.1 }}>What actually wins the sale</div>
        </Rise>
        <Stat delay={10} title="5× more reviews" from={wins.reviewsControl} to={wins.reviewsMin} color={ACCENT} note={"of picks, for every\nLLM we tested"} />
        <Stat delay={45} title="A thin product page" from={wins.thinControl} to={wins.thinMax} color={WARN} note={"no specs, no description:\nthe LLMs skipped it"} />
      </div>
    </Page>
  );
};
