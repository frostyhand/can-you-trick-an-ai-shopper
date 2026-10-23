import p2 from "./data/phase2.json";

type Fool = { score_pp: number; ci_pp: [number, number] } | null;
type ModelBlock = { foolability: { close: Fool; clear: Fool }; tricks_close: Record<string, number>; new_tricks: Record<string, any> };
type Policy = { agree_with_strong_pp: number; escalated_pp: number; cost_per_1k_usd: number; expected_latency_ms: number };
type P2 = {
  shield: {
    accuracy: { preregistered: any; confident: any };
    overhead: { shield_latency_ms_median: number; shield_cost_per_1k_shelves_usd: number; router_latency_ms_median: number };
    none: Record<string, ModelBlock>;
    shield: Record<string, ModelBlock>;
    confident: Record<string, ModelBlock>;
  };
  router: { always_cheap: Policy; always_strong: Policy; jev_routed: Policy; random_same_rate: Policy; foolability: { close: Fool; clear: Fool };
    by_condition: Record<string, { cheap_agree_pp: number; routed_agree_pp: number; random_agree_pp: number; escalated_pp: number; routed_cost_per_1k_usd: number; strong_cost_per_1k_usd: number }> };
  decisions: { phase2_fresh: number; jev_snippets_labelled: number };
};

const P = p2 as unknown as P2;
export const acc = P.shield.accuracy.preregistered;
export const accConfident = P.shield.accuracy.confident;
export const overhead = P.shield.overhead;
export const haikuFool = {
  none: P.shield.none.haiku.foolability.close?.score_pp ?? 0,
  shield: P.shield.shield.haiku.foolability.close?.score_pp ?? 0,
  confident: P.shield.confident.haiku.foolability.close?.score_pp ?? 0,
};
export const haikuBadge = {
  none: P.shield.none.haiku.tricks_close.badge,
  shield: P.shield.shield.haiku.tricks_close.badge,
};
export const newTricksHaiku = {
  none: P.shield.none.haiku.new_tricks.average_pp as number,
  shield: P.shield.shield.haiku.new_tricks.average_pp as number,
};
export const router = P.router;
export const routerClear = P.router.by_condition.clear;
export const phase2Decisions = P.decisions.phase2_fresh;
export const snippetsLabelled = P.decisions.jev_snippets_labelled;
