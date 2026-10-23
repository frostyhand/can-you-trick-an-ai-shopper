import { RowBars } from "../bars";
import { router, routerClear } from "../phase2";
import { INK_2, MUTED } from "../theme";
import { Page, Rise, useOutro } from "../ui";

const GRAY = "#5b5e66";
const BLUE = "#3987e5";
const AMBER = "#c98500";

export const Router: React.FC<{ duration: number }> = ({ duration }) => {
  const out = useOutro(duration);
  const r = routerClear;
  const share = Math.round((100 * r.routed_cost_per_1k_usd) / r.strong_cost_per_1k_usd);
  return (
    <Page padding={80}>
      <div style={{ opacity: out, display: "flex", flexDirection: "column", height: "100%" }}>
        <Rise>
          <div style={{ fontSize: 56, fontWeight: 800, lineHeight: 1.1 }}>Then Jev decides when to call in the expensive AI.</div>
        </Rise>
        <Rise delay={10}>
          <div style={{ fontSize: 30, color: INK_2, marginTop: 14, lineHeight: 1.35 }}>
            Easy choice: the small, cheap AI buys. Hard choice: Jev hands it to the top AI (Claude Opus). It handed over {Math.round(r.escalated_pp)}%.
          </div>
        </Rise>
        <div style={{ fontSize: 32, fontWeight: 800, marginTop: 36 }}>Same choice as the top AI</div>
        <RowBars delay={30} max={100} labelWidth={330} barMax={390} unit="%"
          rows={[
            { label: "Small AI alone", value: r.cheap_agree_pp, color: GRAY },
            { label: "Small AI + Jev", value: r.routed_agree_pp, color: BLUE },
            { label: "Top AI alone", value: 100, color: AMBER },
          ]} />
        <div style={{ fontSize: 32, fontWeight: 800, marginTop: 40 }}>Cost per 1,000 purchases</div>
        <RowBars delay={80} max={r.strong_cost_per_1k_usd} labelWidth={330} barMax={390}
          rows={[
            { label: "Small AI alone", value: router.always_cheap.cost_per_1k_usd, color: GRAY, display: `$${router.always_cheap.cost_per_1k_usd.toFixed(2)}` },
            { label: "Small AI + Jev", value: r.routed_cost_per_1k_usd, color: BLUE, display: `$${r.routed_cost_per_1k_usd.toFixed(2)}` },
            { label: "Top AI alone", value: r.strong_cost_per_1k_usd, color: AMBER, display: `$${r.strong_cost_per_1k_usd.toFixed(2)}` },
          ]} />
        <Rise delay={140} style={{ marginTop: "auto" }}>
          <div style={{ fontSize: 34, fontWeight: 700 }}>
            {Math.round(r.routed_agree_pp)}% of the top AI's choices, at {share}% of the cost.
            <span style={{ fontSize: 26, color: MUTED, fontWeight: 400 }}> (shelves with a clear best product)</span>
          </div>
        </Rise>
      </div>
    </Page>
  );
};
