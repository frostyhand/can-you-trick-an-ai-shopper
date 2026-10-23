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


TABLES = {
    "close": lambda s: trick_table(s, "close"),
    "clear": lambda s: trick_table(s, "clear"),
    "foolability": foolability_table,
    "cost": cost_table,
    "checks": checks_table,
    "agreement": agreement_table,
}


def fill(text: str, summary: dict) -> str:
    for name, build in TABLES.items():
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
