import { RowBars } from "../bars";
import { wins } from "../data";
import { ACCENT, INK_2, PANEL } from "../theme";
import { Page, Rise, useOutro } from "../ui";

export const Wins: React.FC<{ duration: number }> = ({ duration }) => {
  const out = useOutro(duration);
  return (
    <Page>
      <div style={{ opacity: out }}>
        <Rise>
          <div style={{ fontSize: 60, fontWeight: 800, lineHeight: 1.1 }}>What actually sells to an AI: product data.</div>
        </Rise>
        <Rise delay={8}>
          <div style={{ fontSize: 32, color: INK_2, marginTop: 14 }}>Purchases out of 100, every AI model averaged</div>
        </Rise>
        <div style={{ marginTop: 60 }}>
          <RowBars
            delay={24}
            max={100}
            labelWidth={340}
            barMax={440}
            rows={[
              { label: "5× more customer reviews", value: wins.reviewsMin, color: "#3987e5" },
              { label: "Normal product page", value: wins.reviewsControl, color: "#5b5e66" },
              { label: "No specs or description", value: wins.thinMax, color: "#e66767" },
            ]}
          />
        </div>
        <Rise delay={100}>
          <div style={{ fontSize: 34, color: INK_2, marginTop: 60, lineHeight: 1.4 }}>
            Reviews and complete product details decide the sale. A thin page is invisible.
          </div>
        </Rise>
        <Rise delay={130}>
          <div style={{ background: PANEL, borderRadius: 24, padding: "30px 34px", marginTop: 44 }}>
            <div style={{ fontSize: 76, fontWeight: 800, color: ACCENT, lineHeight: 1 }}>100%</div>
            <div style={{ fontSize: 31, lineHeight: 1.4, marginTop: 10 }}>
              When products were otherwise equal, the four big AIs all bought the same one, every time: the one with the most reviews.
            </div>
          </div>
        </Rise>
      </div>
    </Page>
  );
};
