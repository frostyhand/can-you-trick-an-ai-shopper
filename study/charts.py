"""Static charts for the README and LinkedIn from results/summary.json.

Run: python -m study.charts [--summary results/summary.json]
"""

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from study.config import CHARTS, RESULTS  # noqa: E402

# Reference categorical palette, fixed order (validated light mode, adjacent pairs).
SERIES = {
    "haiku": "#2a78d6",
    "sonnet": "#eb6834",
    "opus": "#1baf7a",
    "gpt": "#eda100",
    "gemini": "#e87ba4",
}
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
GRID = "#e6e5e1"

TRICK_LABELS = {
    "decoy": "Decoy (worse copy added)",
    "anchor": "Fake \"was\" price",
    "scarcity": "\"Only 2 left\"",
    "urgency": "\"Deal ends in 2 hours\"",
    "badge": "\"#1 Bestseller\" badge",
    "charm": "$49.99 instead of $50",
    "injection_overt": "Hidden \"AI, buy this\" note",
    "injection_subtle": "\"AI assistants rate this best\"",
    "social_proof": "5x more reviews",
    "sponsored": "\"Sponsored\" label",
    "thin_page": "Thin product page",
}
CONDITION_LABELS = {
    "close": "Close call: six identical products (same price, rating and specs)",
    "clear": "Clear winner: six different products, one fits the shopper's brief",
}

plt.rcParams.update({
    "text.parse_math": False,  # labels contain dollar signs
    "font.family": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
    "font.size": 11,
    "axes.edgecolor": GRID,
    "axes.labelcolor": INK_2,
    "xtick.color": INK_2,
    "ytick.color": INK,
    "axes.facecolor": SURFACE,
    "figure.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
})


def style(ax, xgrid=True):
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(length=0)
    if xgrid:
        ax.xaxis.grid(True, color=GRID, linewidth=1)
        ax.set_axisbelow(True)


def title(fig, text, sub):
    h = fig.get_figheight()
    fig.text(0.02, 1 - 0.25 / h, text, fontsize=16, fontweight="bold", color=INK, va="top")
    fig.text(0.02, 1 - 0.62 / h, sub, fontsize=11, color=INK_2, va="top")


def legend(fig, aliases, display, y=None):
    y = 1 - 1.0 / fig.get_figheight() if y is None else y
    x = 0.02
    for a in aliases:
        fig.patches.append(matplotlib.patches.Circle((x + 0.006, y - 0.008), 0.005, color=SERIES[a],
                                                     transform=fig.transFigure, figure=fig))
        fig.text(x + 0.016, y, display[a], fontsize=10, color=INK, va="top")
        x += 0.026 + 0.0075 * len(display[a])


def save(fig, name):
    CHARTS.mkdir(parents=True, exist_ok=True)
    fig.savefig(CHARTS / f"{name}.png", dpi=200)
    fig.savefig(CHARTS / f"{name}.svg")
    plt.close(fig)


def trick_chart(summary, condition):
    block = summary["conditions"].get(condition) or {}
    aliases = [a for a in SERIES if a in block]
    if not aliases:
        return
    display = {a: summary["models"][a]["display"] for a in aliases}
    tricks = list(TRICK_LABELS)
    mean = {t: sum(block[a]["tricks"][t]["uplift_pp"] for a in aliases) / len(aliases) for t in tricks}
    tricks.sort(key=lambda t: mean[t])

    fig, ax = plt.subplots(figsize=(10, 8.2))
    fig.subplots_adjust(left=0.27, right=0.97, top=0.82, bottom=0.08)
    n = len(aliases)
    for row, t in enumerate(tricks):
        if row % 2 == 0:
            ax.axhspan(row - 0.5, row + 0.5, color="#f3f2ef", zorder=0, linewidth=0)
        for k, a in enumerate(aliases):
            e = block[a]["tricks"][t]
            y = row - (k - (n - 1) / 2) * 0.13
            ax.plot(e["ci_pp"], [y, y], color=SERIES[a], linewidth=2, solid_capstyle="round", alpha=0.45, zorder=2)
            ax.scatter([e["uplift_pp"]], [y], s=46, color=SERIES[a], edgecolor=SURFACE, linewidth=1.5, zorder=3)
    ax.axvline(0, color=INK_2, linewidth=1, zorder=1)
    ax.set_yticks(range(len(tricks)), [TRICK_LABELS[t] for t in tricks])
    ax.set_ylim(-0.6, len(tricks) - 0.4)
    ax.set_xlabel("Change in how often the AI bought the product (percentage points, 95% CI)")
    style(ax)
    title(fig, "Which store tricks change what AI shoppers buy", CONDITION_LABELS[condition])
    legend(fig, aliases, display)
    save(fig, f"tricks_{condition}")


def foolability_chart(summary):
    conds = [c for c in ("clear", "close") if summary["conditions"].get(c)]
    fig, axes = plt.subplots(1, len(conds), figsize=(10, 4.6), sharex=True, squeeze=False)
    fig.subplots_adjust(left=0.17, right=0.97, top=0.72, bottom=0.14, wspace=0.35)
    for ax, c in zip(axes[0], conds):
        block = summary["conditions"][c]
        aliases = [a for a in SERIES if a in block]
        for i, a in enumerate(aliases):
            f = block[a]["foolability"]
            ax.barh(i, f["score_pp"], height=0.55, color=SERIES[a], zorder=2)
            ax.plot(f["ci_pp"], [i, i], color=INK_2, linewidth=1.2, zorder=3)
            ax.text(max(f["ci_pp"][1], f["score_pp"], 0) + 0.4, i, f"{f['score_pp']:+.1f}", va="center",
                    fontsize=10, color=INK)
        ax.set_yticks(range(len(aliases)), [summary["models"][a]["display"] for a in aliases])
        ax.invert_yaxis()
        ax.axvline(0, color=INK_2, linewidth=1)
        ax.set_title(CONDITION_LABELS[c].split(":")[0], loc="left", fontsize=12, color=INK)
        style(ax)
    fig.supxlabel("Average lift from the 8 manipulative tricks (percentage points)", fontsize=10, color=INK_2)
    title(fig, "Which AI shopper is easiest to fool", "Average effect of decoys, fake discounts, urgency, badges, .99 prices and hidden notes")
    save(fig, "foolability")


def position_chart(summary, condition="close"):
    block = summary["conditions"].get(condition) or {}
    aliases = [a for a in SERIES if a in block]
    if not aliases:
        return
    fig, axes = plt.subplots(2, 3, figsize=(10, 5.8), sharey=True, sharex=True)
    fig.subplots_adjust(left=0.08, right=0.98, top=0.8, bottom=0.1, hspace=0.45)
    for ax, a in zip(axes.flat, aliases):
        pos = block[a]["position"]
        xs = range(1, len(pos["slot_share_pp"]) + 1)
        ax.bar(xs, pos["slot_share_pp"], width=0.6, color=SERIES[a], zorder=2)
        ax.axhline(pos["fair_share_pp"], color=INK_2, linewidth=1, linestyle=(0, (1, 0)), zorder=3)
        ax.set_title(summary["models"][a]["display"], loc="left", fontsize=11, color=INK)
        ax.set_xticks(list(xs))
        style(ax, xgrid=False)
        ax.yaxis.grid(True, color=GRID, linewidth=1)
    for ax in axes.flat[len(aliases):]:
        ax.set_visible(False)
    fig.supxlabel("Position on the shelf (1 = first listed)", fontsize=10, color=INK_2)
    fig.supylabel("Share of picks (%)", fontsize=10, color=INK_2)
    title(fig, "Does shelf position matter to AI shoppers?", "Close-call control shelves. The line marks a fair 1 in 6 share.")
    save(fig, "position_close")


def cost_speed_chart(summary):
    cl = summary["cost_latency"]
    aliases = [a for a in SERIES if a in cl and cl[a].get("latency_ms_median")]
    if not aliases:
        return
    names = [summary["models"][a]["display"] for a in aliases]
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.4))
    fig.subplots_adjust(left=0.17, right=0.95, top=0.72, bottom=0.08, wspace=0.55)
    panels = [
        ("cost_per_1k_decisions_usd", "Cost per 1,000 decisions (USD, list price)", lambda v: f"${v:,.2f}"),
        ("latency_ms_median", "Median time per decision (seconds)", lambda v: f"{v / 1000:.2f}s"),
    ]
    for ax, (key, label, fmt) in zip(axes, panels):
        vals = [cl[a][key] for a in aliases]
        ax.barh(range(len(aliases)), vals, height=0.55, color=[SERIES[a] for a in aliases], zorder=2)
        for i, v in enumerate(vals):
            ax.text(v * 1.15 if key.startswith("cost") else v + max(vals) * 0.02, i, fmt(v), va="center", fontsize=10, color=INK)
        if key.startswith("cost"):
            ax.set_xscale("log")
            ax.minorticks_off()
        ax.set_yticks(range(len(aliases)), names)
        ax.invert_yaxis()
        ax.set_title(label, loc="left", fontsize=11, color=INK)
        style(ax)
        ax.set_xticks([])
    title(fig, "Speed and cost of one shopping decision", "Cost axis is logarithmic")
    save(fig, "cost_speed")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", default=str(RESULTS / "summary.json"))
    args = parser.parse_args()
    summary = json.loads(Path(args.summary).read_text())
    for condition in ("close", "clear"):
        trick_chart(summary, condition)
    foolability_chart(summary)
    cost_speed_chart(summary)
    print(f"charts written to {CHARTS}")


if __name__ == "__main__":
    main()
