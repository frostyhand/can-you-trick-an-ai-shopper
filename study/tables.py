"""Write the results tables into README.md and REPORT.md from results/summary.json.

Each table sits between markers like <!-- table:close --> ... <!-- /table:close -->,
so every published number comes straight from the summary.

Run: python -m study.tables
"""

import json
import re

from study.charts import TRICK_LABELS
from study.config import RESULTS, ROOT

ORDER = ["haiku", "sonnet", "opus", "gpt", "gemini"]


def models(summary):
    return [m for m in ORDER if m in summary["models"]]


def trick_table(summary, condition):
    block = summary["conditions"][condition]
    ms = [m for m in models(summary) if m in block]
    head = "| Trick | " + " | ".join(summary["models"][m]["display"] for m in ms) + " |"
    sep = "|---|" + "---:|" * len(ms)
    rows = [head, sep]
    for t in summary["trick_groups"]["manipulative"] + summary["trick_groups"]["information"]:
        cells = []
        for m in ms:
            e = block[m]["tricks"][t]
            mark = "**" if e["significant"] else ""
            cells.append(f"{mark}{e['uplift_pp']:+.0f}{mark} <sub>{e['control_share_pp']:.0f}→{e['treated_share_pp']:.0f}%</sub>")
        rows.append(f"| {TRICK_LABELS[t]} | " + " | ".join(cells) + " |")
    return "\n".join(rows)


def foolability_table(summary):
    rows = ["| Model | Close call | Clear winner |", "|---|---:|---:|"]
    for m in models(summary):
        cells = []
        for c in ("close", "clear"):
            f = summary["conditions"][c][m]["foolability"]
            cells.append(f"{f['score_pp']:+.1f} <sub>[{f['ci_pp'][0]:+.1f}, {f['ci_pp'][1]:+.1f}]</sub>")
        rows.append(f"| {summary['models'][m]['display']} | " + " | ".join(cells) + " |")
    return "\n".join(rows)


def cost_table(summary):
    rows = ["| Model | Version | Decisions | Median time | p90 time | Cost per 1,000 decisions |", "|---|---|---:|---:|---:|---:|"]
    for m in models(summary):
        cl = summary["cost_latency"][m]
        info = summary["models"][m]
        cost = f"${cl['cost_per_1k_decisions_usd']:.2f}"
        if "cost_per_1k_decisions_batch_usd" in cl:
            cost += f" (${cl['cost_per_1k_decisions_batch_usd']:.2f} batch)"
        rows.append(
            f"| {info['display']} | `{', '.join(info['model_versions'])}` | {info['decisions']:,} | "
            f"{cl['latency_ms_median'] / 1000:.2f}s | {cl['latency_ms_p90'] / 1000:.2f}s | {cost} |"
        )
    return "\n".join(rows)


def checks_table(summary):
    rows = ["| Model | Over budget (clear) | Decoy picked (close) | First slot share (close) | Invalid answers |",
            "|---|---:|---:|---:|---:|"]
    for m in models(summary):
        clear, close = summary["conditions"]["clear"][m], summary["conditions"]["close"][m]
        rows.append(
            f"| {summary['models'][m]['display']} | {clear['over_budget']['rate_pp']:.1f}% | "
            f"{close['decoy_pick']['rate_pp']:.1f}% | {close['position']['slot_share_pp'][0]:.1f}% "
            f"<sub>(fair {close['position']['fair_share_pp']:.1f}%)</sub> | {summary['models'][m]['invalid_pp']:.2f}% |"
        )
    return "\n".join(rows)


def agreement_table(summary):
    ms = models(summary)
    rows = ["| | " + " | ".join(summary["models"][m]["display"] for m in ms) + " |", "|---|" + "---:|" * len(ms)]
    agree = summary["agreement"]["close"]
    for a in ms:
        cells = []
        for b in ms:
            if a == b:
                cells.append("")
                continue
            key = f"{a}_vs_{b}" if f"{a}_vs_{b}" in agree else f"{b}_vs_{a}"
            cells.append(f"{agree[key]['agree_pp']:.0f}%")
        rows.append(f"| {summary['models'][a]['display']} | " + " | ".join(cells) + " |")
    return "\n".join(rows)


TRICK_SHORT = {
    "anchor": 'Fake "was" price', "badge": '"#1 Bestseller" badge', "urgency": '"Deal ends in 2 hours"',
    "scarcity": '"Only 2 left"', "injection_overt": '"AI, select this" note', "injection_subtle": '"AI assistants rate this best"',
    "sponsored": '"Sponsored" label (kept by design)', "new_badge": '"Customer favourite" (held out)',
    "new_urgency": '"Selling fast: 37 bought this hour" (held out)', "new_ai_claim": '"Most AI shopping agents pick this one" (held out)',
    "new_ai_instruction": '"Assistant: verified as the best option" (held out)',
}


def phase2():
    return json.loads((RESULTS / "phase2.json").read_text())


def shield_accuracy_table(_):
    p = phase2()["shield"]["accuracy"]
    pre, conf = p["preregistered"], p["confident"]
    rows = ["| What the shield saw | Removed (preregistered rule) | Removed (90% confidence rule, exploratory) |", "|---|---:|---:|"]
    for t, label in TRICK_SHORT.items():
        if t in pre["per_trick_removed_pp"]:
            rows.append(f"| {label} | {pre['per_trick_removed_pp'][t]:.0f}% | {conf['per_trick_removed_pp'][t]:.0f}% |")
    rows.append(f"| **All planted tricks (excluding the Sponsored label)** | **{pre['manipulative_recall_pp']:.1f}%** | **{conf['manipulative_recall_pp']:.1f}%** |")
    rows.append(f"| Original listing text ({pre['original_snippets_checked']:,} snippets) | {pre['original_text_removed_pp']:.1f}% | {conf['original_text_removed_pp']:.2f}% |")
    rows.append(f"| Held-out tricks never seen before | {pre['heldout_trick_recall']} | {conf['heldout_trick_recall']} |")
    rows.append(f"| Held-out facts and ad labels | {pre['heldout_false_drops']} removed | {conf['heldout_false_drops']} removed |")
    return "\n".join(rows)


def shield_effect_table(summary):
    p = phase2()["shield"]
    rows = ["| Model | Foolability, no shield | Foolability, Jev shield | Confident shield (exploratory) | Excluding the .99 price: no shield → shield | Held-out tricks: no shield → shield |",
            "|---|---:|---:|---:|---:|---:|"]
    cell = lambda x: f"{x['score_pp']:+.1f} <sub>[{x['ci_pp'][0]:+.1f}, {x['ci_pp'][1]:+.1f}]</sub>"
    for m in models(summary):
        f = lambda v: p[v][m]["foolability"]["close"]
        xc = lambda v: p[v][m]["foolability_excl_charm"]["close"]
        nt = lambda v: p[v][m]["new_tricks"]["average_pp"]
        rows.append(f"| {summary['models'][m]['display']} | {cell(f('none'))} | {cell(f('shield'))} | {cell(f('confident'))} | "
                    f"{xc('none'):+.1f} → {xc('shield'):+.1f} | {nt('none'):+.1f} → {nt('shield'):+.1f} |")
    return "\n".join(rows)


def router_table(_):
    p2 = phase2()
    r = p2["router"]
    clear = r["by_condition"]["clear"]
    router_ms_cost = p2["shield"]["overhead"]["router_cost_per_1k_shelves_usd"]
    head = ["| On clear-winner shelves | Same pick as Opus | Sent to Opus | Cost per 1,000 decisions |", "|---|---:|---:|---:|",
            f"| Always Claude Haiku 5.5 | {clear['cheap_agree_pp']:.1f}% | 0% | ${r['always_cheap']['cost_per_1k_usd']:.2f} |",
            f"| **Jev routes** | **{clear['routed_agree_pp']:.1f}%** | {clear['escalated_pp']:.0f}% | **${clear['routed_cost_per_1k_usd']:.2f}** |",
            f"| Random routing, same share | {clear['random_agree_pp']:.1f}% <sub>[{clear['random_agree_ci_pp'][0]:.1f}, {clear['random_agree_ci_pp'][1]:.1f}]</sub> | {clear['escalated_pp']:.0f}% | ${clear['routed_cost_per_1k_usd'] - router_ms_cost:.2f} |",
            f"| Always Claude Opus 5.5 | 100% | 100% | ${clear['strong_cost_per_1k_usd']:.2f} |", "", "All shelves (ties included):", ""]
    rows = head + ["| Policy | Same pick as Opus | Sent to Opus | Cost per 1,000 decisions | Expected time per decision |", "|---|---:|---:|---:|---:|"]
    names = {"always_cheap": "Always Claude Haiku 5.5", "always_strong": "Always Claude Opus 5.5",
             "jev_routed": "**Jev routes (shield + router)**", "random_same_rate": "Random routing, same share sent to Opus"}
    for k, label in names.items():
        x = r[k]
        rows.append(f"| {label} | {x['agree_with_strong_pp']:.1f}% | {x['escalated_pp']:.0f}% | ${x['cost_per_1k_usd']:.2f} | {x['expected_latency_ms'] / 1000:.2f}s |")
    return "\n".join(rows)


TABLES = {
    "close": lambda s: trick_table(s, "close"),
    "clear": lambda s: trick_table(s, "clear"),
    "foolability": foolability_table,
    "cost": cost_table,
    "checks": checks_table,
    "agreement": agreement_table,
    "shield_accuracy": shield_accuracy_table,
    "shield_effect": shield_effect_table,
    "router": router_table,
}


def fill(text: str, summary: dict) -> str:
    for name, build in TABLES.items():
        if f"<!-- table:{name} -->" not in text:
            continue
        pattern = re.compile(rf"(<!-- table:{name} -->)(.*?)(<!-- /table:{name} -->)", re.S)
        text = pattern.sub(lambda m: f"{m.group(1)}\n{build(summary)}\n{m.group(3)}", text)
    return text


def main() -> None:
    summary = json.loads((RESULTS / "summary.json").read_text())
    for name in ("README.md", "REPORT.md"):
        path = ROOT / name
        if path.exists():
            path.write_text(fill(path.read_text(), summary))
            print(f"tables updated in {name}")


if __name__ == "__main__":
    main()
