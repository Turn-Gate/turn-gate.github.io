import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import os

# ---------- style ----------
mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Inter", "Arial", "sans-serif"],
    "font.size": 15,
    "axes.labelsize": 17,
    "axes.titlesize": 17,
    "legend.fontsize": 14,
    "xtick.labelsize": 14,
    "ytick.labelsize": 14,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.linewidth": 1.0,
    "lines.linewidth": 2.4,
    "lines.markersize": 9,
})

# ---------- data (from Table 3, FS column only) ----------
iterations = np.array([1, 3, 5])

methods = {
    "No Defense":                   {"fs": [0.824, 0.882, 0.882], "color": "#9E9E9E", "marker": "s", "ls": "--"},
    "Intention Analysis (GPT-5.2)": {"fs": [0.412, 0.706, 0.765], "color": "#E08E45", "marker": "^", "ls": "-"},
    "Qwen Guard (8B)":              {"fs": [0.735, 0.824, 0.824], "color": "#4C8BB8", "marker": "D", "ls": "-"},
    "TurnGate (Ours)":               {"fs": [0.265, 0.647, 0.676], "color": "#B3324A", "marker": "o", "ls": "-"},
}


# ---------- plotting function ----------
def make_plot(save_path=None):
    fig, ax = plt.subplots(figsize=(8, 5))

    for name, spec in methods.items():
        lw = 2.8 if "TurnGate" in name else 2.2
        z = 5 if "TurnGate" in name else 3
        ax.plot(
            iterations, spec["fs"],
            label=name,
            color=spec["color"],
            marker=spec["marker"],
            linestyle=spec["ls"],
            linewidth=lw,
            markerfacecolor=spec["color"],
            markeredgecolor="white",
            markeredgewidth=1.0,
            zorder=z,
        )

    ax.set_xlabel("Attacker iteration budget $i$")
    ax.set_ylabel("Attack Success Rate $\downarrow$", labelpad=6)
    ax.set_xticks(iterations)
    ax.set_xlim(0.7, 5.3)
    ax.set_ylim(0.0, 1.0)
    ax.set_yticks(np.arange(0.0, 1.01, 0.2))
    ax.grid(axis="y", linestyle=":", linewidth=0.6, color="gray", alpha=0.5)

    leg = ax.legend(
        loc="lower right",
        frameon=True,
        framealpha=0.92,
        edgecolor="#CCCCCC",
        handlelength=2.2,
        borderpad=0.5,
    )
    leg.get_frame().set_linewidth(0.6)

    fig.tight_layout()

    if save_path:
        if not os.path.exists(os.path.dirname(save_path)):
            os.makedirs(os.path.dirname(save_path))
        fig.savefig(save_path, bbox_inches="tight", dpi=200)
        print(f"saved: {save_path}")

if __name__ == "__main__":
    make_plot(save_path="figs/fs_vs_iteration.png")
