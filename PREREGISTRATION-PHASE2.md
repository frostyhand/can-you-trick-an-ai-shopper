# Preregistration, Phase 2: Jev as decision support

Written and committed before any Phase 2 data was collected. Phase 1 ([PREREGISTRATION.md](PREREGISTRATION.md)) found that the frontier models resist store tricks while the small Claude Haiku 5.5 does not. Phase 2 asks whether a fast decision model can protect and steer the shopping agents instead of shopping itself.

Jev (TypeSafe AI's System One model, `jev-latest`) answers typed questions with calibrated probabilities in about 0.2 seconds. It never makes the purchase in this phase. It plays two support roles.

## Part A: Trick shield

**What it does.** Before a shopping model sees a shelf, every free-text snippet on every product is classified by Jev with one `choice` question per snippet ([study/phase2_snippets.py](study/phase2_snippets.py)): `product_fact`, `sales_pressure`, `ad_disclosure` or `ai_directed`. Snippets whose top class is `sales_pressure` or `ai_directed` are removed; the rest are kept.

Snippets are the availability line, badge, deal line, ad label, the "was" price with its discount (one snippet), each sentence of the description, and the specs (one snippet). Title, brand, price, rating and review count are structured fields and are always kept. All of one shelf's snippets go to Jev in a single call.

**Runs.** All 3,276 Phase 1 shelves are shielded and answered by the five Phase 1 models with the same settings and samples (1 per clear-winner shelf, 2 per close-call shelf). When a shielded shelf is byte-identical to a shelf a model has already answered, that answer is reused (the content fingerprint matches), so only shelves the shield changed in a new way cost new calls.

**Held-out tricks.** The shield's classes were designed knowing the Phase 1 tricks, so 40 held-out snippets that never appear on Phase 1 shelves (20 tricks, 3 ad labels, 17 facts) test generalisation. Four of them are also placed on the target product of all 144 close-call base shelves (`new_badge`, `new_urgency`, `new_ai_claim`, `new_ai_instruction`) and answered by all five models with and without the shield (2 samples each).

**Measures.**
- Shield accuracy: share of inserted manipulative snippets removed (recall) and share of factual snippets removed (false drops), on Phase 1 shelves and on the held-out set.
- Foolability with and without the shield, per model and condition, as in Phase 1.
- Change in the information effects (5× reviews, thin page, .99 price) with the shield.
- Added cost and latency per decision.

**Hypotheses.**
- S1: On Phase 1 shelves the shield removes at least 90% of the inserted manipulative snippets (badge, deal, "Only 2 left", "was" price, both AI-directed sentences) and at most 5% of factual snippets.
- S2: With the shield, Claude Haiku 5.5's close-call foolability falls by at least half.
- S3: The shield changes no model's information effects (reviews, thin page) by more than 5 points.
- S4: On held-out snippets the shield removes at least 80% of tricks and at most 10% of facts.
- S5: On the four held-out tricks placed on shelves, the shield lowers Claude Haiku 5.5's average uplift.

## Part B: Smart router

**What it does.** Jev answers one `noul` question per shelf: whether one product is clearly the best fit, so the choice is easy. If the answer is at least 0.5, the cheap model (Claude Haiku 5.5) decides; otherwise the shelf is escalated to the strong model (Claude Opus 5.5). The router sees the shielded shelf.

**Measures.** Using the shielded answers from Part A (no extra shopping calls), compare four policies on every shelf: always Haiku, always Opus, Jev-routed, and random routing with the same escalation rate as Jev (averaged over 1,000 random draws). For each: agreement with Opus's pick (sample 0), foolability, cost per 1,000 decisions including Jev, and median latency including Jev.

**Hypothesis.**
- R1: Jev-routed decisions agree with Opus more often than random routing at the same escalation rate, at lower cost than always using Opus.

## Reporting

Every hypothesis is reported whether or not it holds. Jev's own product picks are not collected or reported.

## Deviations

Recorded after the run; see [REPORT.md](REPORT.md#deviations-from-the-preregistration). Opus requests were sent live instead of through the stalled batch queue, the held-out classifications were re-run after a log was accidentally deleted (identical results), and three analyses were added after seeing the data and are labelled exploratory: the 90% confidence shield, the router by condition, and foolability without the .99 price.
