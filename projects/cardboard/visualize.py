"""
Generate the 4-panel analysis figure for The Strength of Cardboard.

Light editorial palette - navy on white, muted grays. 150 DPI.
Output: docs/viz/analysis-light.png
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import model as M

# --------------------------------------------------------------------------- #
# Editorial palette
# --------------------------------------------------------------------------- #
NAVY = "#001F3F"
MUTED = "#6B7A8D"
LABEL = "#8FA3B1"
BG = "#FFFFFF"
GRID = "#E3E8EE"

plt.rcParams.update({
    "figure.facecolor": BG,
    "axes.facecolor": BG,
    "savefig.facecolor": BG,
    "axes.edgecolor": MUTED,
    "axes.labelcolor": NAVY,
    "axes.titlecolor": NAVY,
    "xtick.color": NAVY,
    "ytick.color": NAVY,
    "text.color": NAVY,
    "axes.linewidth": 0.8,
    "grid.color": GRID,
    "grid.linewidth": 0.6,
    "font.family": "DejaVu Sans",
    "font.size": 9,
    "axes.titlesize": 11,
    "axes.titleweight": "bold",
    "axes.labelsize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 8,
    "legend.frameon": False,
})


def panel_cross_section(ax):
    """Panel 1: cross-section of the corrugated board (to scale)."""
    pitch = M.FLUTE_PITCH
    n_periods = 3
    x = np.linspace(0, pitch * n_periods, 1200)
    y = M.flute_profile(x)
    t = M.T_LINER
    h = M.FLUTE_HEIGHT

    # Top and bottom liners as filled rectangles
    top_bottom = h / 2 + t / 2
    for sign in (+1, -1):
        yc = sign * top_bottom
        rect = Polygon(
            [[x.min(), yc - t / 2], [x.max(), yc - t / 2],
             [x.max(), yc + t / 2], [x.min(), yc + t / 2]],
            closed=True, facecolor=NAVY, edgecolor=NAVY, alpha=0.85,
        )
        ax.add_patch(rect)

    # Corrugated medium as a thick sinusoidal ribbon
    for sign in (+1, -1):
        ax.fill_between(x, y, y + sign * M.T_MEDIUM,
                        color=MUTED, alpha=0.55, linewidth=0)

    # Neutral axis
    ax.axhline(0, color=LABEL, linewidth=0.6, linestyle=(0, (3, 3)))

    # Dimensions
    ax.annotate("", xy=(0, -h / 2 - t - 0.6e-3),
                xytext=(0, h / 2 + t + 0.6e-3),
                arrowprops=dict(arrowstyle="<->", color=MUTED, lw=0.8))
    ax.text(-0.4e-3, 0, f"h = {h*1e3:.1f} mm", color=MUTED, rotation=90,
            va="center", ha="center", fontsize=8)

    ax.annotate("", xy=(0, h / 2 + t + 1.4e-3),
                xytext=(pitch, h / 2 + t + 1.4e-3),
                arrowprops=dict(arrowstyle="<->", color=MUTED, lw=0.8))
    ax.text(pitch / 2, h / 2 + t + 1.6e-3, f"pitch = {pitch*1e3:.1f} mm",
            color=MUTED, ha="center", va="bottom", fontsize=8)

    ax.set_title("Corrugated board cross-section")
    ax.set_xlabel("x  [mm]")
    ax.set_ylabel("y  [mm]")
    ax.set_aspect("equal")
    ax.set_xlim(-1.5e-3, pitch * n_periods + 0.5e-3)
    ax.set_ylim(-h / 2 - t - 2.2e-3, h / 2 + t + 2.6e-3)
    ax.set_xticks([0, pitch, 2 * pitch, 3 * pitch])
    ax.set_xticklabels([0, 7.2, 14.4, 21.6])
    ax.set_yticks([-4e-3, 0, 4e-3])
    ax.set_yticklabels([-4, 0, 4])
    ax.grid(False)


def panel_stiffness_ratio(ax):
    """Panel 2: second moment of area - flat vs corrugated (same mass)."""
    I_flat = M.second_moment_flat(M.equivalent_flat_thickness())
    I_corr = M.second_moment_corrugated()
    ratio = I_corr / I_flat

    bars = ax.bar(["Flat sheet\n(same mass)", "Corrugated\nboard"],
                  [I_flat, I_corr], color=[MUTED, NAVY], width=0.5,
                  edgecolor=NAVY, linewidth=0.6)
    ax.set_ylabel("I  [m$^4$]")
    ax.set_title("Second moment of area (per panel)")
    ax.set_yscale("log")
    ax.set_ylim(I_flat * 0.3, I_corr * 4)
    ax.grid(True, axis="y", which="both", alpha=0.5)

    for b, v in zip(bars, [I_flat, I_corr]):
        ax.text(b.get_x() + b.get_width() / 2, v * 1.5,
                f"{v:.2e}", ha="center", va="bottom",
                color=NAVY, fontsize=8)
    ax.text(0.5, I_corr * 0.18,
            f"stiffness ratio = {ratio:.1f}$\\times$",
            ha="center", va="top", color=NAVY, fontsize=10,
            bbox=dict(boxstyle="round,pad=0.4", fc=BG, ec=MUTED, lw=0.6))


def panel_euler_curve(ax):
    """Panel 3: Euler buckling load vs column length, corrugated vs flat."""
    L = np.logspace(-2, 0, 200)        # 1 cm to 1 m
    I_corr = M.second_moment_corrugated()
    I_flat = M.second_moment_flat(M.equivalent_flat_thickness())
    P_corr = M.euler_buckling_load(M.E_KRAFT, I_corr, L)
    P_flat = M.euler_buckling_load(M.E_KRAFT, I_flat, L)

    ax.loglog(L * 1e3, P_corr / 9.81, color=NAVY, linewidth=2.0,
              label="corrugated board")
    ax.loglog(L * 1e3, P_flat / 9.81, color=MUTED, linewidth=1.6,
              linestyle=(0, (4, 2)), label="flat sheet (same mass)")

    # Mark the working point (L = 0.4 m, applied 20 kg)
    L_work = M.COLUMN_LENGTH
    P_work = M.euler_buckling_load(M.E_KRAFT, I_corr, L_work) / 9.81
    ax.scatter([L_work * 1e3], [P_work], color=NAVY, s=28, zorder=5,
               edgecolor=BG, linewidth=0.8)
    ax.annotate(f"L = 400 mm\nP$_{{cr}}$ = {P_work:.0f} kg",
                xy=(L_work * 1e3, P_work),
                xytext=(L_work * 1e3 * 1.3, P_work * 0.4),
                color=NAVY, fontsize=8,
                arrowprops=dict(arrowstyle="->", color=MUTED, lw=0.7))

    ax.axhline(20, color=LABEL, linewidth=0.8, linestyle=(0, (1, 2)))
    ax.text(L[0] * 1e3 * 1.1, 21, "applied load = 20 kg",
            color=LABEL, fontsize=7.5, va="bottom")

    ax.set_xlabel("column length L  [mm]")
    ax.set_ylabel("Euler buckling load  [kg]")
    ax.set_title("Buckling load vs length")
    ax.set_xlim(L[0] * 1e3, L[-1] * 1e3)
    ax.grid(True, which="both", alpha=0.45)
    ax.legend(loc="upper right")


def panel_tilt(ax):
    """Panel 4: buckling load vs flute tilt angle."""
    P_cr0 = M.euler_buckling_load(M.E_KRAFT, M.second_moment_corrugated(),
                                  M.COLUMN_LENGTH)
    angles, loads = M.tilt_sweep(P_cr0, max_deg=30.0, n=121)

    ax.plot(angles, loads / P_cr0 * 100, color=NAVY, linewidth=2.0)
    ax.fill_between(angles, loads / P_cr0 * 100, 100, color=NAVY, alpha=0.06)

    # Mark 15 deg point
    p15 = M.buckling_load_vs_tilt(np.deg2rad(15.0), P_cr0) / P_cr0 * 100
    ax.scatter([15], [p15], color=NAVY, s=28, zorder=5,
               edgecolor=BG, linewidth=0.8)
    ax.annotate(f"15$^\\circ$ tilt\n{p15:.0f}% capacity\n(60% drop)",
                xy=(15, p15), xytext=(19, 78),
                color=NAVY, fontsize=8,
                arrowprops=dict(arrowstyle="->", color=MUTED, lw=0.7))

    ax.axvline(0, color=LABEL, linewidth=0.8, linestyle=(0, (1, 2)))
    ax.set_xlabel("load tilt angle  [deg]")
    ax.set_ylabel("buckling load  [% of axial]")
    ax.set_title("Off-axis loading kills the panel")
    ax.set_xlim(0, 30)
    ax.set_ylim(0, 105)
    ax.grid(True, alpha=0.45)


def main():
    fig, axes = plt.subplots(2, 2, figsize=(11, 8.2))
    fig.subplots_adjust(left=0.08, right=0.97, top=0.92, bottom=0.09,
                        wspace=0.28, hspace=0.42)

    panel_cross_section(axes[0, 0])
    panel_stiffness_ratio(axes[0, 1])
    panel_euler_curve(axes[1, 0])
    panel_tilt(axes[1, 1])

    fig.suptitle("The Strength of Cardboard - simplified FEA on a corrugated structure",
                 color=NAVY, fontsize=13, fontweight="bold", y=0.975)

    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "docs", "viz")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "analysis-light.png")
    fig.savefig(out, dpi=150)
    print(f"Saved: {out}")


if __name__ == "__main__":
    main()
