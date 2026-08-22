"""Generate the 4-panel analysis figure for phantom-traffic-jams.

Layout (1600x1000 @ 150 DPI):
  - Panel 1 (top-left):  Fundamental diagram q(rho) and v(rho)
  - Panel 2 (top-right): Stability sweep -- growth ratio vs density,
                         with critical density annotated
  - Panel 3 (bot-left):  LWR Godunov space-time density map (x-t)
  - Panel 4 (bot-right): Microsim ring -- speed at each car over time
"""
from __future__ import annotations

import os
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from model import (
    V_MAX, RHO_MAX, RHO_CRIT, ROAD_LENGTH, NUM_CARS, T_TOTAL,
    v_of_rho, q_of_rho, critical_density_greenshields,
    critical_density_ovm, critical_density_empirical, max_flow,
    shock_speed, simulate_micro, solve_lwr, stability_sweep,
)

# --- Over Engineer editorial palette ---------------------------------------
NAVY = '#001F3F'
MUTED = '#6B7A8D'
LABEL = '#8FA3B1'
RULE = '#D6DBE0'
ACCENT = '#9CB3C9'   # secondary line color, derived from navy/light
BG = '#FFFFFF'

plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'axes.unicode_minus': False,
    'axes.edgecolor': RULE,
    'axes.linewidth': 0.6,
    'axes.labelcolor': MUTED,
    'axes.titlecolor': NAVY,
    'axes.titleweight': 'bold',
    'xtick.color': MUTED,
    'ytick.color': MUTED,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'axes.labelsize': 10,
    'axes.titlesize': 12,
    'figure.facecolor': BG,
    'savefig.facecolor': BG,
})


def _style(ax):
    ax.set_facecolor(BG)
    ax.tick_params(colors=MUTED, labelsize=9, length=3, width=0.6)
    for s in ax.spines.values():
        s.set_color(RULE)
        s.set_linewidth(0.6)
    ax.grid(False)


def main(out_path: str = 'docs/viz/analysis-light.png') -> None:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    fig, axes = plt.subplots(2, 2, figsize=(16, 10), constrained_layout=True)
    fig.patch.set_facecolor(BG)
    axes = axes.flatten()  # axes[0]=TL, axes[1]=TR, axes[2]=BL, axes[3]=BR

    # =====================================================================
    # Panel 1: Fundamental diagram (Greenshields)
    # =====================================================================
    ax = axes[0]
    rho_km = np.linspace(0, RHO_MAX * 1000, 400)
    rho = rho_km / 1000.0
    q_vph = q_of_rho(rho) * 3600.0
    v_kmh = v_of_rho(rho) * 3.6

    ax.plot(rho_km, q_vph, color=NAVY, linewidth=2.0, label='Flow  q(ρ)')
    ax2 = ax.twinx()
    ax2.plot(rho_km, v_kmh, color=MUTED, linewidth=1.5, linestyle='--',
             label='Speed v(ρ)')
    ax2.set_ylabel('Speed  v  [km/h]', color=MUTED, fontsize=10)
    ax2.tick_params(colors=MUTED, labelsize=9, length=3, width=0.6)
    for s in ax2.spines.values():
        s.set_color(RULE)
        s.set_linewidth(0.6)
    ax2.set_ylim(0, V_MAX * 3.6 * 1.05)
    ax2.grid(False)

    rho_c = critical_density_greenshields() * 1000
    q_max = max_flow() * 3600
    ax.plot([rho_c, rho_c], [0, q_max], color=LABEL, linewidth=0.8,
            linestyle=':')
    ax.plot(rho_c, q_max, 'o', color=NAVY, markersize=6, zorder=5)
    ax.annotate(f'capacity\nρ_c = {rho_c:.0f} veh/km\nq_max = {q_max:.0f} veh/h',
                xy=(rho_c, q_max), xytext=(rho_c + 25, q_max * 0.65),
                color=NAVY, fontsize=9, ha='left',
                arrowprops=dict(arrowstyle='-', color=LABEL, lw=0.7))

    ax.set_xlabel('Density  ρ  [veh/km]', color=MUTED, fontsize=10)
    ax.set_ylabel('Flow  q  [veh/h]', color=NAVY, fontsize=10)
    ax.set_title('Fundamental diagram (Greenshields)', color=NAVY, pad=10)
    ax.set_xlim(0, RHO_MAX * 1000)
    ax.set_ylim(0, q_max * 1.15)
    _style(ax)

    # =====================================================================
    # Panel 2: Stability sweep -- growth ratio vs density
    # =====================================================================
    ax = axes[1]
    pts = stability_sweep()
    rho_pts = np.array([p.density * 1000 for p in pts])
    growth = np.array([p.growth_ratio for p in pts])

    stable_mask = growth < 1.0
    ax.plot(rho_pts[stable_mask], growth[stable_mask], 'o',
            color=ACCENT, markersize=7, label='stable (damps)')
    ax.plot(rho_pts[~stable_mask], growth[~stable_mask], 'o',
            color=NAVY, markersize=7, label='unstable (amplifies)')
    ax.plot(rho_pts, growth, color=MUTED, linewidth=0.8, alpha=0.5)
    ax.axhline(1.0, color=LABEL, linewidth=0.8, linestyle=':')

    # Empirical critical density
    rho_crit_emp = critical_density_empirical() * 1000
    ax.axvline(rho_crit_emp, color=NAVY, linewidth=0.8, linestyle='--')
    ax.annotate(f'critical density\nρ* ≈ {rho_crit_emp:.0f} veh/km',
                xy=(rho_crit_emp, 1.0), xytext=(rho_crit_emp + 8, 6),
                color=NAVY, fontsize=9, ha='left',
                arrowprops=dict(arrowstyle='-', color=LABEL, lw=0.7))

    # Theoretical OVM threshold
    rho_ovm = critical_density_ovm() * 1000
    ax.axvline(rho_ovm, color=MUTED, linewidth=0.6, linestyle=':')
    ax.text(rho_ovm + 1, ax.get_ylim()[1] * 0.92 if ax.get_ylim()[1] > 0 else 20,
            f'OVM theory: {rho_ovm:.0f} veh/km',
            color=MUTED, fontsize=8)

    ax.set_xlabel('Density  ρ  [veh/km]', color=MUTED, fontsize=10)
    ax.set_ylabel('Perturbation growth ratio', color=NAVY, fontsize=10)
    ax.set_title('Linear stability of Bando OVM on the ring', color=NAVY, pad=10)
    ax.set_xlim(0, 140)
    ax.set_ylim(0, max(growth.max() * 1.1, 25))
    _style(ax)
    ax.legend(loc='upper left', frameon=False, fontsize=8, labelcolor=NAVY)

    # =====================================================================
    # Panel 3: LWR Godunov space-time density map
    # =====================================================================
    ax = axes[3]  # axes[1, 1] == axes[3]
    lwr = solve_lwr(t_total=120.0)
    # x-t image; time increases downward so upstream propagation
    # (wave moving to the left, against traffic) is visually obvious.
    im = ax.pcolormesh(lwr.x_axis, lwr.t_axis, lwr.rho_history,
                       cmap='Blues', shading='auto', vmin=0.0,
                       vmax=RHO_MAX)
    cb = fig.colorbar(im, ax=ax, pad=0.02, fraction=0.04)
    cb.set_label('density  ρ  [veh/m]', color=MUTED, fontsize=9)
    cb.ax.tick_params(colors=MUTED, labelsize=8)
    cb.outline.set_edgecolor(RULE)
    cb.outline.set_linewidth(0.5)

    # Annotate the shock trajectory: fit a line through the maximum-density
    # ridge at each time and overlay.
    ridge_x = lwr.x_axis[np.argmax(lwr.rho_history, axis=1)]
    # Take early-time ridge and extrapolate upstream (decreasing x).
    ax.plot(ridge_x[:len(ridge_x) // 2], lwr.t_axis[:len(ridge_x) // 2],
            color=NAVY, linewidth=1.5, linestyle='--', alpha=0.9,
            label='shock trajectory')
    w_shock = shock_speed(RHO_CRIT * 1.1, RHO_MAX * 0.85)
    ax.text(0.02, 0.98, f'shock speed w ≈ {w_shock:+.2f} m/s\n'
                        f'(negative ⇒ upstream)',
            transform=ax.transAxes, va='top', ha='left',
            color=NAVY, fontsize=9,
            bbox=dict(facecolor=BG, edgecolor=RULE, boxstyle='round,pad=0.3',
                      linewidth=0.5))

    ax.set_xlabel('Position  x  [m]', color=MUTED, fontsize=10)
    ax.set_ylabel('Time  t  [s]', color=MUTED, fontsize=10)
    ax.set_title('LWR Godunov: density evolution on the ring',
                 color=NAVY, pad=10)
    ax.invert_yaxis()
    _style(ax)

    # =====================================================================
    # Panel 4: Microsim ring -- speed over time, car index on x axis
    # =====================================================================
    ax = axes[2]  # axes[1, 0] == axes[2]
    res = simulate_micro(t_total=T_TOTAL)
    # Downsample time for readability
    take = np.linspace(0, res.speeds.shape[0] - 1, 400).astype(int)
    speeds_ds = res.speeds[take]
    t_ds = res.t_axis[take]

    im2 = ax.pcolormesh(np.arange(res.n_cars), t_ds, speeds_ds,
                        cmap='Blues', shading='auto', vmin=0.0, vmax=V_MAX)
    cb2 = fig.colorbar(im2, ax=ax, pad=0.02, fraction=0.04)
    cb2.set_label('speed  v  [m/s]', color=MUTED, fontsize=9)
    cb2.ax.tick_params(colors=MUTED, labelsize=8)
    cb2.outline.set_edgecolor(RULE)
    cb2.outline.set_linewidth(0.5)

    ax.set_xlabel('Car index  (sorted by position)', color=MUTED, fontsize=10)
    ax.set_ylabel('Time  t  [s]', color=MUTED, fontsize=10)
    ax.set_title(f'Microsim: 100-car ring @ {res.density * 1000:.0f} veh/km, '
                 f'1 car braked', color=NAVY, pad=10)
    ax.invert_yaxis()
    _style(ax)
    ax.text(0.02, 0.02, f'growth ratio = {res.perturbation_growth:.1f}×\n'
                        f'wave speed   = {res.wave_speed:+.2f} m/s'
                        if res.wave_speed == res.wave_speed else
                        f'growth ratio = {res.perturbation_growth:.1f}×',
            transform=ax.transAxes, va='bottom', ha='left',
            color=NAVY, fontsize=9,
            bbox=dict(facecolor=BG, edgecolor=RULE, boxstyle='round,pad=0.3',
                      linewidth=0.5))

    plt.savefig(out_path, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close(fig)
    print(f'Saved: {out_path}')


if __name__ == '__main__':
    main()
