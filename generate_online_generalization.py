import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import os
from matplotlib.lines import Line2D

# ---------- style ----------
mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Inter", "Arial", "sans-serif"],
    "font.size": 12,
    "axes.labelsize": 13,
    "legend.fontsize": 11,
    "xtick.labelsize": 11,
    "ytick.labelsize": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.spines.left": False,
    "axes.linewidth": 0.9,
})

# ---------- data ----------
blocks = {
    "a": {
        "title": "(a) Benchmark shift",
        "subtitle": "GPT-5.2 target  •  adaptive tree-search attacker  •  train on MTID (Chemistry + Cybersecurity)",
        "bg": "#FFF2F7",
        "rows": [
            ("HarmBench",    "Chemical & Biological",      0.647, 0.471),
            ("HarmBench",    "Illegal",                    0.833, 0.604),
            ("StrongReject", "Illegal Goods & Services",   0.837, 0.388),
            ("StrongReject", "Non-violent Crimes",         0.897, 0.621),
            ("StrongReject", "Violence",                   0.944, 0.778),
            ("JBB",          "Economic Harm",              0.800, 0.800),
            ("JBB",          "Expert Advice",              1.000, 0.500),
            ("JBB",          "Fraud / Deception",          1.000, 0.700),
            ("JBB",          "Government Decision-making", 0.900, 0.600),
            ("JBB",          "Malware / Hacking",          0.500, 0.500),
            ("JBB",          "Physical Harm",              0.800, 0.400),
            ("JBB",          "Privacy",                    0.800, 0.600),
        ],
    },
    "b": {
        "title": "(b) Target-model shift",
        "subtitle": "Gemini-3.1-Pro target (zero-shot)  •  train on GPT-5.2-generated MTID",
        "bg": "#F3EEFA",
        "rows": [
            ("MTID", "MTID Full Test Set", 0.853, 0.676),
        ],
    },
    "c": {
        "title": "(c) Attacker-pipeline shift",
        "subtitle": "GPT-5.2 target  •  Multi-Agent Jailbreak (MAJ)  •  cross-category transfer",
        "bg": "#ECF4FC",
        "rows": [
            ("MAJ", r"Chem $\to$ Cyber", 0.780, 0.631),
            ("MAJ", r"Cyber $\to$ Chem", 0.715, 0.593),
        ],
    },
}

color_nodef   = "#9E9E9E"
color_tg      = "#B3324A"
color_delta   = "#1C783C"
color_noimp   = "#B0B0B0"
color_divider = "#D6D6D6"

bench_color = {
    "HarmBench":    "#8A3A58",
    "StrongReject": "#3F6EA6",
    "JBB":          "#B07F2A",
    "MTID":         "#5E3F8A",
    "MAJ":          "#2E7F6A",
}

bench_row_bg = {
    "HarmBench":    "#FBEEF3",
    "StrongReject": "#ECF2FA",
    "JBB":          "#FBF3E3",
    "MTID":         "#F1EBF8",
    "MAJ":          "#E8F4EF",
}

# ---------- layout ----------
row_h = 0.55
title_h = 0.9
pad_bottom = 0.35
heights = [len(b["rows"]) * row_h + title_h for b in blocks.values()]
total_h = sum(heights) + pad_bottom

fig = plt.figure(figsize=(10.8, total_h))
gs = fig.add_gridspec(nrows=3, ncols=1, height_ratios=heights, hspace=0.30)
axes = [fig.add_subplot(gs[i, 0]) for i in range(3)]
block_keys = list(blocks.keys())


def draw_block(ax, block_key):
    b = blocks[block_key]
    rows = b["rows"]
    n = len(rows)

    y_positions = list(range(n - 1, -1, -1))

    # benchmark groups
    bench_spans = []
    cur = None
    start = None
    for i, (bench, *_) in enumerate(rows):
        if bench != cur:
            if cur is not None:
                bench_spans.append((cur, start, i - 1))
            cur = bench
            start = i
    bench_spans.append((cur, start, len(rows) - 1))

    # Row-level background tint
    for bench, i0, i1 in bench_spans:
        y_top = y_positions[i0] + 0.5
        y_bot = y_positions[i1] - 0.5
        ax.axhspan(y_bot, y_top,
                   color=bench_row_bg.get(bench, "#F5F5F5"),
                   zorder=0)

    # faint dividers between benchmark groups
    for (b1, i0a, i1a), (b2, i0b, _) in zip(bench_spans, bench_spans[1:]):
        y_div = (y_positions[i1a] + y_positions[i0b]) / 2
        ax.axhline(y_div, color=color_divider, linewidth=0.8,
                   linestyle="-", alpha=0.7, zorder=1)

    # dumbbells
    for (bench, cat, nd, tg), y in zip(rows, y_positions):
        delta = nd - tg
        improved = delta > 1e-6
        seg_color = color_delta if improved else color_noimp

        ax.plot([tg, nd], [y, y], color=seg_color, linewidth=3.5,
                alpha=0.60, zorder=2, solid_capstyle="round")

        ax.scatter(nd, y, s=90, color=color_nodef, marker="s",
                   edgecolor="white", linewidth=1.2, zorder=4)
        ax.scatter(tg, y, s=130, color=color_tg, marker="o",
                   edgecolor="white", linewidth=1.4, zorder=5)

        ax.text(nd + 0.012, y, f"{nd:.3f}",
                va="center", ha="left", fontsize=9.5, color="#555555")
        ax.text(tg - 0.012, y, f"{tg:.3f}",
                va="center", ha="right", fontsize=10,
                color=color_tg, fontweight="bold")

        mid = (nd + tg) / 2
        if improved:
            ax.text(mid, y + 0.32, rf"$\Delta$={delta:.3f}",
                    va="bottom", ha="center", fontsize=9.8,
                    color=color_delta, fontweight="bold", zorder=6)
        else:
            ax.text(mid, y + 0.32, r"$\Delta$=0",
                    va="bottom", ha="center", fontsize=9,
                    color="#888888", style="italic", zorder=6)

    # y-axis labels
    ylabels = [cat for _, cat, _, _ in rows]
    ax.set_yticks(y_positions)
    ax.set_yticklabels(ylabels)
    ax.tick_params(axis="y", length=0, pad=10)

    # benchmark badges
    for bench, i0, i1 in bench_spans:
        y_mid = (y_positions[i0] + y_positions[i1]) / 2
        ax.text(
            -0.36, y_mid, bench,
            transform=ax.get_yaxis_transform(),
            ha="center", va="center",
            fontsize=9.5, fontweight="bold",
            color="white",
            bbox=dict(boxstyle="round,pad=0.32",
                      facecolor=bench_color.get(bench, "#555555"),
                      edgecolor="none"),
            zorder=10,
            clip_on=False,
        )

    ax.set_xlim(0.0, 1.15)
    ax.set_xticks(np.arange(0.0, 1.01, 0.2))
    ax.grid(axis="x", linestyle=":", linewidth=0.6,
            color="gray", alpha=0.45, zorder=1)
    ax.set_axisbelow(True)
    ax.set_ylim(-0.7, n - 0.2 + 0.6)

    # title + subtitle
    ax.text(0.0, 1.06, b["title"],
            transform=ax.transAxes,
            ha="left", va="bottom",
            fontsize=13.5, fontweight="bold", color="#222222")
    ax.text(0.0, 1.04, b["subtitle"],
            transform=ax.transAxes,
            ha="left", va="top",
            fontsize=10.5, fontweight="bold", color="#444444")

    ax.spines["left"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_color("#888888")
    ax.spines["bottom"].set_linewidth(0.9)


for ax, key in zip(axes, block_keys):
    draw_block(ax, key)

for ax in axes[:-1]:
    ax.tick_params(axis="x", labelbottom=False)

axes[-1].set_xlabel(r"Attack Success Rate (ASR)  $\downarrow$",
                    fontsize=13, fontweight="bold", labelpad=8)

legend_handles = [
    Line2D([0], [0], marker="s", color="w",
           markerfacecolor=color_nodef, markeredgecolor="white", markersize=10,
           label="No Defense"),
    Line2D([0], [0], marker="o", color="w",
           markerfacecolor=color_tg, markeredgecolor="white", markersize=11,
           label="TurnGate (Ours)"),
    Line2D([0], [0], color=color_delta, lw=3.5, alpha=0.60,
           label=r"$\Delta$ASR reduction"),
]
fig.legend(handles=legend_handles,
           loc="upper right",
           bbox_to_anchor=(0.99, 0.998),
           ncol=3, frameon=True, framealpha=0.96,
           edgecolor="#CCCCCC", borderpad=0.5, handlelength=2.0)

fig.tight_layout(rect=[0, 0, 1, 0.975])
if not os.path.exists('figs'):
    os.makedirs('figs')
fig.savefig("figs/online_generalization.png", bbox_inches="tight", dpi=200)
print("saved: figs/online_generalization.png")
plt.close(fig)
