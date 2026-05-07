import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from matplotlib.lines import Line2D
import os

# ---------- style ----------
mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Inter", "Arial", "sans-serif"],
    "font.size": 14,
    "axes.labelsize": 15,
    "legend.fontsize": 13,
    "xtick.labelsize": 13,
    "ytick.labelsize": 13,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.spines.left": False,
    "axes.linewidth": 0.9,
})

# ---------- data ----------
blocks = {
    "a": {
        "title": "Benchmark Distribution Shift",
        "subtitle": "GPT-5.2 target • adaptive tree-search attacker • zero-shot transfer",
        "rows": [
            ("HarmBench",    "Misinformation",             0.765, 0.618),
            ("HarmBench",    "Harmful",                    0.857, 0.429),
            ("HarmBench",    "Harassment",                 0.789, 0.632),
            ("StrongReject", "Illegal Goods & Services",   0.837, 0.388),
            ("StrongReject", "Non-violent Crimes",         0.897, 0.621),
            ("StrongReject", "Violence",                   0.944, 0.778),
            ("JBB",          "Economic Harm",              0.800, 0.800),
            ("JBB",          "Expert Advice",              0.900, 0.500),
            ("JBB",          "Fraud / Deception",          1.000, 0.700),
            ("JBB",          "Government Decision-making", 0.900, 0.600),
            ("JBB",          "Malware / Hacking",          0.500, 0.500),
            ("JBB",          "Physical Harm",              0.800, 0.400),
            ("JBB",          "Privacy",                    0.800, 0.600),
        ],
    },
    "b": {
        "title": "Target-Model Distribution Shift",
        "subtitle": "Gemini-3.1-Pro target (zero-shot) • train on GPT-5.2-generated MTID",
        "rows": [
            ("MTID", "MTID Full Test Set", 0.853, 0.676),
        ],
    },
    "c": {
        "title": "Joint Target + Benchmark Shift",
        "subtitle": "Gemini-3.1-Pro target (zero-shot) • HarmBench • zero-shot transfer",
        "rows": [
            ("HarmBench", "Misinformation", 0.647, 0.529),
            ("HarmBench", "Harmful",        0.667, 0.381),
            ("HarmBench", "Harassment",     0.895, 0.632),
        ],
    },
    "d": {
        "title": "Attacker-Pipeline Distribution Shift",
        "subtitle": "GPT-5.2 target • MAJ attacker • cross-category transfer",
        "rows": [
            ("MAJ", r"Chem $\to$ Cyber", 0.780, 0.631),
            ("MAJ", r"Cyber $\to$ Chem", 0.715, 0.593),
        ],
    },
}

color_nodef   = "#9E9E9E"
color_tg      = "#6366f1" # Using site primary
color_delta   = "#10b981" # Using site success
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

def draw_single_block(block_key, save_filename):
    b = blocks[block_key]
    rows = b["rows"]
    n = len(rows)
    
    row_h = 0.8
    total_h = n * row_h + 2.0 # Increased top space
    fig, ax = plt.subplots(figsize=(12, total_h))

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

    for bench, i0, i1 in bench_spans:
        y_top = y_positions[i0] + 0.5
        y_bot = y_positions[i1] - 0.5
        ax.axhspan(y_bot, y_top, color=bench_row_bg.get(bench, "#F5F5F5"), zorder=0)

    for (b1, i0a, i1a), (b2, i0b, _) in zip(bench_spans, bench_spans[1:]):
        y_div = (y_positions[i1a] + y_positions[i0b]) / 2
        ax.axhline(y_div, color=color_divider, linewidth=0.8, linestyle="-", alpha=0.7, zorder=1)

    for (bench, cat, nd, tg), y in zip(rows, y_positions):
        delta = nd - tg
        improved = delta > 1e-6
        seg_color = color_delta if improved else color_noimp

        ax.plot([tg, nd], [y, y], color=seg_color, linewidth=5, alpha=0.60, zorder=2, solid_capstyle="round")
        ax.scatter(nd, y, s=120, color=color_nodef, marker="s", edgecolor="white", linewidth=1.2, zorder=4)
        ax.scatter(tg, y, s=160, color=color_tg, marker="o", edgecolor="white", linewidth=1.4, zorder=5)

        ax.text(nd + 0.028, y, f"{nd:.3f}", va="center", ha="left", fontsize=12, color="#555555")
        ax.text(tg - 0.028, y, f"{tg:.3f}", va="center", ha="right", fontsize=13, color=color_tg, fontweight="bold")

        mid = (nd + tg) / 2
        if improved:
            ax.text(mid, y + 0.35, f"Δ={delta:.3f}", va="bottom", ha="center", fontsize=12, color=color_delta, fontweight="bold", zorder=6)

    ylabels = [cat for _, cat, _, _ in rows]
    ax.set_yticks(y_positions)
    ax.set_yticklabels(ylabels)
    ax.tick_params(axis="y", length=0, pad=10)

    for bench, i0, i1 in bench_spans:
        y_mid = (y_positions[i0] + y_positions[i1]) / 2
        ax.text(-0.3, y_mid, bench, transform=ax.get_yaxis_transform(), ha="center", va="center",
                fontsize=11, fontweight="bold", color="white",
                bbox=dict(boxstyle="round,pad=0.32", facecolor=bench_color.get(bench, "#555555"), edgecolor="none"),
                zorder=10, clip_on=False)

    ax.set_xlim(0.0, 1.15)
    ax.set_xticks(np.arange(0.0, 1.01, 0.2))
    ax.grid(axis="x", linestyle=":", linewidth=0.6, color="gray", alpha=0.45, zorder=1)
    ax.set_axisbelow(True)
    ax.set_ylim(-0.7, n - 0.2 + 0.6)
    
    # Title and Subtitle with clear separation
    ax.text(0.0, 1.16, b["title"], transform=ax.transAxes, ha="left", va="bottom", fontsize=20, fontweight="bold", color="#222222")
    ax.text(0.0, 1.04, b["subtitle"], transform=ax.transAxes, ha="left", va="bottom", fontsize=14, color="#444444")
    
    ax.set_xlabel(r"Attack Success Rate (ASR) $\downarrow$", fontsize=14, fontweight="bold", labelpad=12)

    plt.tight_layout()
    plt.savefig(save_filename, bbox_inches="tight", dpi=150)
    plt.close()
    print(f"Generated {save_filename}")

# Generate all blocks
if not os.path.exists('figs'):
    os.makedirs('figs')

draw_single_block("a", "figs/ood_benchmark.png")
draw_single_block("b", "figs/ood_model.png")
draw_single_block("c", "figs/ood_joint.png")
draw_single_block("d", "figs/ood_pipeline.png")

# Also generate a shared legend
fig_leg = plt.figure(figsize=(10, 1))
legend_handles = [
    Line2D([0], [0], marker="s", color="w", markerfacecolor=color_nodef, markeredgecolor="white", markersize=12, label="No Defense"),
    Line2D([0], [0], marker="o", color="w", markerfacecolor=color_tg, markeredgecolor="white", markersize=14, label="TurnGate (Ours)"),
    Line2D([0], [0], color=color_delta, lw=5, alpha=0.60, label=r"Δ ASR reduction"),
]
fig_leg.legend(handles=legend_handles, loc="center", ncol=3, frameon=False)
fig_leg.savefig("figs/ood_legend.png", bbox_inches="tight", dpi=150)
plt.close()
print("Generated figs/ood_legend.png")
