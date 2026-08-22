"""
Phantom Traffic Jams
====================

Lighthill-Whitham-Richards (LWR) macroscopic traffic flow on a ring,
a Bando Optimal-Velocity microscopic car-following model, and a
linear-stability analysis that recovers the critical density above
which small perturbations amplify into backward-traveling shockwaves.

References
----------
- Lighthill & Whitham (1955), "On kinematic waves II", Proc. R. Soc. A 229.
- Richards (1956), "Shockwaves on the highway", Oper. Res. 4.
- Bando et al. (1995), "Dynamical model of traffic congestion and
  numerical simulation", Phys. Rev. E 51.
- Daganzo (1994), "The cell transmission model", Transp. Res. B 28.
- Helbing (2001), "Traffic and related self-driven many-particle
  systems", Rev. Mod. Phys. 73.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Iterable

import numpy as np

# ---------------------------------------------------------------------------
# Physical constants and model parameters (SI units unless noted).
# Values are typical of a single freeway lane in uncongested flow.
# ---------------------------------------------------------------------------
V_MAX = 30.0          # free-flow speed [m/s]   (about 108 km/h)
RHO_MAX = 0.143       # jam density [veh/m]     (about 143 veh/km/lane)
RHO_CRIT = 0.030       # critical density [veh/m] (about 30 veh/km/lane)
ROAD_LENGTH = 1000.0   # circular road perimeter [m]
NUM_CARS = 100         # number of vehicles (microsim headline)

# Bando optimal-velocity function (piecewise-linear, Bando 1995):
#   V(dx) = 0            for dx < DX_MIN
#   V(dx) = V_MAX*(dx-DX_MIN)/(DX_MAX-DX_MIN)  for DX_MIN <= dx <= DX_MAX
#   V(dx) = V_MAX        for dx > DX_MAX
# Linear stability criterion:  a < 2 * V'(s)  =>  unstable.
# V'(s) = V_MAX / (DX_MAX - DX_MIN)  in the linear ramp, 0 elsewhere.
# So the critical density (above which instability begins) is exactly
#   rho_crit = 1 / DX_MAX  =  1 / 33  =  0.0303 veh/m  =  30.3 veh/km.
DX_MIN = 7.0           # bumper-to-bumper spacing [m]   (jam density = 143 veh/km)
DX_MAX = 33.0          # free-flow spacing threshold [m] (critical density = 30 veh/km)
SENSITIVITY = 1.0       # OVM relaxation rate a [1/s]  (Bando et al. 1995)
DT = 0.05               # numerical timestep [s]      (microsim)
T_TOTAL = 600.0         # simulated horizon [s]       (microsim)
DX_GRID = 10.0          # cell width [m]              (LWR Godunov)
PERTURBATION_AMP = 4.0  # initial velocity perturbation [m/s] on one car


# ---------------------------------------------------------------------------
# Fundamental diagram (Greenshields) -- used for the LWR PDE and shock speeds
# ---------------------------------------------------------------------------
def v_of_rho(rho: float | np.ndarray) -> float | np.ndarray:
    """Equilibrium speed v(rho) from the Greenshields fundamental diagram.

    v(rho) = v_max * (1 - rho / rho_max)
    """
    return V_MAX * (1.0 - np.maximum(rho, 0.0) / RHO_MAX)


def q_of_rho(rho: float | np.ndarray) -> float | np.ndarray:
    """Flow q(rho) = rho * v(rho).  Maximum at rho_crit = rho_max / 2."""
    return rho * v_of_rho(rho)


def critical_density_greenshields() -> float:
    """Greenshields critical density: rho_max / 2."""
    return RHO_MAX / 2.0


def max_flow() -> float:
    """Capacity q_max = (v_max * rho_max) / 4 (parabola vertex)."""
    return V_MAX * RHO_MAX / 4.0


# ---------------------------------------------------------------------------
# Rankine-Hugoniot shock speed
# ---------------------------------------------------------------------------
def shock_speed(rho_up: float, rho_down: float) -> float:
    """Speed of a kinematic shock between two uniform states.

    w = (q2 - q1) / (rho2 - rho1)   (negative => travels upstream)
    """
    if abs(rho_up - rho_down) < 1e-12:
        return 0.0
    dq = q_of_rho(rho_down) - q_of_rho(rho_up)
    drho = rho_down - rho_up
    return float(dq / drho)


# ---------------------------------------------------------------------------
# Bando optimal-velocity function V(dx) -- piecewise-linear (Bando 1995)
# ---------------------------------------------------------------------------
def v_optimal(dx: float | np.ndarray) -> float | np.ndarray:
    """Piecewise-linear Bando optimal-velocity function.

    V(dx) = 0            if dx <  DX_MIN
          = v_max * (dx - DX_MIN) / (DX_MAX - DX_MIN)   if DX_MIN <= dx <= DX_MAX
          = v_max        if dx >  DX_MAX

    The slope in the ramp is V_MAX / (DX_MAX - DX_MIN).
    The linear-stability criterion for the OVM is a < 2*V'(s); with the
    piecewise-linear V, V' is constant in the ramp and zero outside, so
    instability appears exactly for densities in
    [1/DX_MAX, 1/DX_MIN] = [30, 143] veh/km.
    """
    dx = np.maximum(np.asarray(dx, dtype=np.float64), 0.0)
    slope = V_MAX / (DX_MAX - DX_MIN)
    v = np.where(dx < DX_MIN, 0.0,
                 np.where(dx > DX_MAX, V_MAX,
                          slope * (dx - DX_MIN)))
    return v if v.shape else float(v)


def v_optimal_derivative() -> float:
    """V'(dx) in the linear ramp (constant for piecewise-linear V)."""
    return V_MAX / (DX_MAX - DX_MIN)


def critical_density_ovm() -> float:
    """Critical density of the Bando OVM: 1 / DX_MAX."""
    return 1.0 / DX_MAX


# ---------------------------------------------------------------------------
# Microscopic car-following simulation (Bando OVM) on a ring road
# ---------------------------------------------------------------------------
@dataclass
class MicroResult:
    n_cars: int
    length: float
    t_total: float
    dt: float
    density: float          # veh/m
    mean_speed: float       # m/s
    flow: float             # veh/s
    wave_speed: float       # fitted wave speed [m/s] (negative = upstream)
    perturbation_growth: float  # final speed range / initial speed range
    history: np.ndarray     # (T, N) positions [m]
    speeds: np.ndarray      # (T, N) speed [m/s]
    t_axis: np.ndarray      # (T,) time [s]


def _initial_positions(n: int, length: float) -> np.ndarray:
    """Uniform spacing, sorted, on [0, length)."""
    return np.sort(np.mod(np.linspace(0, length, n, endpoint=False), length))


def _gaps_sorted(positions: np.ndarray, length: float) -> np.ndarray:
    """Forward gap of each car to its leader, given positions are sorted.

    positions must be sorted ascending in [0, length).  The gap of the
    last car wraps around to the first car.  Sum of all gaps == length.
    """
    n = positions.shape[0]
    gaps = np.empty(n, dtype=np.float64)
    gaps[:-1] = np.diff(positions)
    gaps[-1] = positions[0] + length - positions[-1]
    return gaps


def _spacing(positions: np.ndarray, length: float) -> np.ndarray:
    """Forward spacing dx_i = x_{i+1} - x_i (cyclic).

    Deprecated alias kept for any external callers; expects positions
    in sorted cyclic order.  Use ``_gaps_sorted`` in new code.
    """
    return _gaps_sorted(positions, length)


def simulate_micro(n_cars: int = NUM_CARS,
                   length: float = ROAD_LENGTH,
                   t_total: float = T_TOTAL,
                   dt: float = DT,
                   perturb: float = PERTURBATION_AMP,
                   seed: int | None = 0) -> MicroResult:
    """Run the Bando OVM microsimulation on a ring road.

    Cars start uniformly spaced at the equilibrium velocity for that
    spacing. Car 0 receives a single velocity perturbation.  We record
    positions and speeds with a stride so the returned arrays stay
    tractable (~1.2k frames).

    Implementation note
    -------------------
    The OVM is a car-following model: each car's update uses the gap to
    its leader.  We therefore keep the position array SORTED at every
    step (positions are monotonically increasing in [0, length)).  This
    is preserved by a no-overtake clamp that prevents a car from
    advancing more than (gap - 0.5 m) in one timestep.
    """
    n = int(n_cars)
    eq_spacing = length / n
    eq_speed = float(np.squeeze(v_optimal(eq_spacing)))

    positions = _initial_positions(n, length).astype(np.float64)
    speeds = np.full(n, eq_speed, dtype=np.float64)
    speeds[0] = max(0.0, eq_speed - perturb)

    n_steps = int(t_total / dt)
    stride = max(1, n_steps // 1200)
    n_frames = n_steps // stride + 1

    history = np.empty((n_frames, n), dtype=np.float32)
    vhist = np.empty((n_frames, n), dtype=np.float32)
    t_axis = np.empty(n_frames, dtype=np.float32)
    history[0] = positions
    vhist[0] = speeds
    t_axis[0] = 0.0
    fi = 1

    for k in range(n_steps):
        # Keep the position array sorted.  The dynamics preserve order
        # (see the no-overtake clamp below), so a stable argsort is
        # essentially a no-op except when wraparound shifts the cyclic
        # origin.  Sorting ensures the gap calc stays correct.
        order = np.argsort(positions, kind='stable')
        positions = positions[order]
        speeds = speeds[order]

        gaps = _gaps_sorted(positions, length)
        v_target = v_optimal(gaps)

        # Forward-Euler velocity-relaxation step (Bando OVM)
        new_speeds = np.maximum(0.0, speeds + dt * SENSITIVITY * (v_target - speeds))
        # No-overtake clamp: a car cannot advance more than (gap - 0.5 m).
        max_step = np.maximum(gaps - 0.5, 0.0)
        new_speeds = np.minimum(new_speeds, max_step / dt)

        positions = np.mod(positions + new_speeds * dt, length)
        speeds = new_speeds

        if (k + 1) % stride == 0 and fi < n_frames:
            # Record in sorted order so the array stays meaningful.
            o2 = np.argsort(positions, kind='stable')
            history[fi] = positions[o2]
            vhist[fi] = speeds[o2]
            t_axis[fi] = (k + 1) * dt
            fi += 1

    history = history[:fi]
    vhist = vhist[:fi]
    t_axis = t_axis[:fi]

    # Perturbation amplification: track the speed range across all cars.
    # Stable => range stays small / decays; unstable => range grows and
    # saturates into a stop-and-go wave (max range ~ v_max).  We report
    # the MAX range over the second half of the run (so transients die out)
    # relative to the initial range (which equals the perturbation).
    speed_range = np.ptp(vhist, axis=1)
    n2 = max(1, len(speed_range) // 2)
    late_max_range = float(np.max(speed_range[n2:]))
    init_range = max(float(speed_range[0]), 1e-9)
    growth = late_max_range / init_range

    # Estimate wave speed via the physical position of the slowest car.
    # In a stop-and-go wave, the jam (slow region) drifts backward in
    # physical space (upstream, against the direction of traffic flow).
    # We track argmin(speeds) at each time -- the position of the most-
    # jammed car -- unwrap the ring coordinate, and fit a line.  The
    # slope of that line is the wave's velocity in the ground frame
    # (negative => upstream propagation, the physically expected case).
    wave_speed = float('nan')
    if late_max_range > 1.0 and vhist.shape[0] > 30:
        slow_idx = np.argmin(vhist, axis=1)
        slow_pos = history[np.arange(vhist.shape[0]), slow_idx].astype(np.float64)
        # Unwrap the ring coordinate so slow_pos is continuous in time.
        diffs = np.diff(slow_pos)
        slow_pos_u = slow_pos.copy()
        corr = 0.0
        for i in range(1, len(slow_pos_u)):
            if diffs[i - 1] > length / 2:
                corr -= length
            elif diffs[i - 1] < -length / 2:
                corr += length
            slow_pos_u[i] = slow_pos[i] + corr
        # Use the middle 70% of the time window to avoid transients.
        a = max(3, int(0.15 * len(slow_pos_u)))
        b = min(len(slow_pos_u) - 1, int(0.85 * len(slow_pos_u)))
        if b - a > 4:
            slope, _ = np.polyfit(t_axis[a:b], slow_pos_u[a:b], 1)
            if abs(slope) < V_MAX * 2:  # sanity bound
                wave_speed = float(slope)

    mean_speed = float(np.mean(vhist))
    density = n / length
    flow = density * mean_speed

    return MicroResult(
        n_cars=n, length=length, t_total=t_total, dt=dt,
        density=density, mean_speed=mean_speed, flow=flow,
        wave_speed=wave_speed, perturbation_growth=growth,
        history=history, speeds=vhist, t_axis=t_axis,
    )


# ---------------------------------------------------------------------------
# Stability sweep: for each density, run microsim and quantify whether the
# initial perturbation grows or decays.
# ---------------------------------------------------------------------------
@dataclass
class StabilityPoint:
    density: float           # veh/m
    n_cars: int
    growth_ratio: float      # final range / initial range
    wave_speed: float        # m/s (negative = upstream; nan if no wave)
    mean_speed: float        # m/s
    stable: bool             # growth_ratio < 1.0


def stability_sweep(densities: Iterable[float] | None = None,
                    perturb: float = PERTURBATION_AMP,
                    t_total: float = T_TOTAL) -> list[StabilityPoint]:
    """For each density, run a perturbed ring and record growth + wave speed."""
    if densities is None:
        # 18 points from 5 to 130 veh/km
        rhos_km = np.linspace(5.0, 130.0, 18)
        densities = rhos_km / 1000.0

    out = []
    for rho in densities:
        n_cars = max(5, int(round(rho * ROAD_LENGTH)))
        if n_cars < 4 or n_cars > 1500:
            continue
        res = simulate_micro(n_cars=n_cars, length=ROAD_LENGTH,
                             t_total=t_total, perturb=perturb, seed=0)
        out.append(StabilityPoint(
            density=rho,
            n_cars=n_cars,
            growth_ratio=res.perturbation_growth,
            wave_speed=res.wave_speed,
            mean_speed=res.mean_speed,
            stable=res.perturbation_growth < 1.0,
        ))
    return out


def critical_density_empirical() -> float:
    """Linear-interp the density where growth_ratio crosses 1.0."""
    pts = stability_sweep()
    g = np.array([p.growth_ratio for p in pts])
    r = np.array([p.density for p in pts])
    for i in range(len(g) - 1):
        if g[i] < 1.0 <= g[i + 1]:
            t = (1.0 - g[i]) / max(g[i + 1] - g[i], 1e-9)
            return float(r[i] + t * (r[i + 1] - r[i]))
    return float(r[int(np.argmax(g))])


# ---------------------------------------------------------------------------
# Macroscopic LWR PDE: Godunov finite volume with the triangular (CTM) flux.
# ---------------------------------------------------------------------------
@dataclass
class LWRResult:
    rho_history: np.ndarray   # (T, X) density
    t_axis: np.ndarray        # time [s]
    x_axis: np.ndarray        # space [m]
    length: float
    initial_perturbation: float


def _triangular_flux(rho: np.ndarray, rho_crit: float = RHO_CRIT,
                    v_max: float = V_MAX, rho_max: float = RHO_MAX) -> np.ndarray:
    """Triangular fundamental diagram q(rho) = min(v_max*rho, w*(rho_max-rho))."""
    w = v_max * rho_crit / max(rho_max - rho_crit, 1e-9)  # shock speed [m/s]
    free = v_max * rho
    cong = w * (rho_max - rho)
    return np.minimum(free, cong)


def solve_lwr(rho0: np.ndarray | None = None,
              length: float = ROAD_LENGTH,
              t_total: float = 60.0,
              dx: float = DX_GRID,
              dt: float | None = None) -> LWRResult:
    """Godunov finite-volume solver for the LWR PDE on a periodic ring.

    Uses the triangular fundamental diagram (Daganzo cell transmission
    model).  CFL-stable dt = 0.5 * dx / v_max.
    """
    nx = int(length / dx)
    if rho0 is None:
        # base density just above critical, with a Gaussian perturbation
        x = np.arange(nx) * dx
        rho0 = RHO_CRIT * 1.10 * np.ones(nx)
        rho0 += 0.015 * np.exp(-((x - length / 4.0) ** 2) / (2 * 25.0 ** 2))
    rho = np.asarray(rho0, dtype=np.float64).copy()

    if dt is None:
        dt = 0.5 * dx / V_MAX
    n_steps = int(t_total / dt)
    stride = max(1, n_steps // 200)
    n_frames = n_steps // stride + 1

    rho_hist = np.empty((n_frames, nx), dtype=np.float32)
    rho_hist[0] = rho
    t_axis = np.zeros(n_frames, dtype=np.float32)
    fi = 1

    for k in range(n_steps):
        # Godunov CTM flux: demand from upstream cell, supply from downstream.
        rho_left = np.roll(rho, 1)          # upstream neighbour (i-1)
        send = np.minimum(rho_left, np.full_like(rho, RHO_CRIT))
        recv = np.minimum(rho, np.full_like(rho, RHO_CRIT))
        q_send = _triangular_flux(send)
        q_recv = _triangular_flux(recv)
        flux = np.minimum(q_send, q_recv)
        rho = rho + (dt / dx) * (np.roll(flux, 1) - flux)

        if (k + 1) % stride == 0 and fi < n_frames:
            rho_hist[fi] = rho
            t_axis[fi] = (k + 1) * dt
            fi += 1

    rho_hist = rho_hist[:fi]
    t_axis = t_axis[:fi]
    x_axis = np.arange(nx) * dx
    return LWRResult(rho_history=rho_hist, t_axis=t_axis, x_axis=x_axis,
                    length=length, initial_perturbation=float(rho0.max() - rho0.min()))


# ---------------------------------------------------------------------------
# Aggregate run + results export
# ---------------------------------------------------------------------------
def run_all() -> dict:
    """Run the macro model, micro model, and stability sweep.

    Returns a dict suitable for JSON serialization.  We downsample the
    micro history so the JSON stays small.
    """
    micro = simulate_micro()
    lwr = solve_lwr()

    T, N = micro.history.shape
    take_t = np.linspace(0, T - 1, 64).astype(int)
    history_ds = micro.history[take_t].tolist()

    sweep = stability_sweep()
    sweep_list = [
        {'density_veh_per_m': p.density,
         'density_veh_per_km': round(p.density * 1000.0, 2),
         'n_cars': p.n_cars,
         'growth_ratio': round(p.growth_ratio, 4),
         'wave_speed_mps': (None if (p.wave_speed != p.wave_speed)
                            else round(p.wave_speed, 3)),
         'mean_speed_mps': round(p.mean_speed, 3),
         'stable': bool(p.stable)}
        for p in sweep
    ]

    try:
        rho_crit_emp = critical_density_empirical()
    except Exception:
        rho_crit_emp = float('nan')

    rho_up = RHO_CRIT * 1.1
    rho_down = RHO_MAX * 0.85
    w = shock_speed(rho_up, rho_down)

    return {
        'project': 'phantom-traffic-jams',
        'date': '2026-04-20',
        'parameters': {
            'road_length_m': ROAD_LENGTH,
            'num_cars': NUM_CARS,
            'v_max_mps': V_MAX,
            'rho_max_veh_per_m': RHO_MAX,
            'rho_crit_veh_per_m': RHO_CRIT,
            'ovm_sensitivity_a_per_s': SENSITIVITY,
            'ovm_dx_min_m': DX_MIN,
            'ovm_dx_max_m': DX_MAX,
            'dt_micro_s': DT,
            't_total_s': T_TOTAL,
            'perturbation_mps': PERTURBATION_AMP,
        },
        'results': {
            'max_flow_veh_per_s': round(max_flow(), 4),
            'max_flow_veh_per_h': round(max_flow() * 3600, 1),
            'critical_density_greenshields_veh_per_m': critical_density_greenshields(),
            'critical_density_greenshields_veh_per_km': round(critical_density_greenshields() * 1000, 1),
            'critical_density_ovm_veh_per_m': critical_density_ovm(),
            'critical_density_ovm_veh_per_km': round(critical_density_ovm() * 1000, 1),
            'critical_density_empirical_veh_per_m': rho_crit_emp,
            'critical_density_empirical_veh_per_km': round(rho_crit_emp * 1000, 1),
            'shockwave_speed_mps': round(w, 3),
            'shockwave_speed_kmh': round(w * 3.6, 1),
            'micro_mean_speed_mps': round(micro.mean_speed, 3),
            'micro_flow_veh_per_h': round(micro.flow * 3600, 1),
            'perturbation_growth_ratio': round(micro.perturbation_growth, 3),
            'lwr_perturbation_amplitude': round(lwr.initial_perturbation, 4),
        },
        'stability_sweep': sweep_list,
        'micro_history_downsampled': {
            't_frames': take_t.tolist(),
            'positions_m': history_ds,
        },
    }


def save_results(path: str = 'data/results.json') -> None:
    """Persist aggregate results as JSON."""
    import os
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(run_all(), f, indent=2)


if __name__ == '__main__':
    print('Greenshields fundamental diagram:')
    print(f'  v_max     = {V_MAX:.1f} m/s  ({V_MAX * 3.6:.0f} km/h)')
    print(f'  rho_max   = {RHO_MAX:.3f} veh/m  ({RHO_MAX * 1000:.0f} veh/km)')
    print(f'  rho_crit  = {critical_density_greenshields():.4f} veh/m  '
          f'({critical_density_greenshields() * 1000:.0f} veh/km)')
    print(f'  q_max     = {max_flow():.2f} veh/s  ({max_flow() * 3600:.0f} veh/h)')

    print('\nBando OVM (piecewise-linear optimal velocity):')
    print(f'  V\'(dx)    = {v_optimal_derivative():.3f} 1/s')
    print(f'  rho_crit = {critical_density_ovm() * 1000:.1f} veh/km '
          f'(linear stability threshold)')

    print('\nMicrosimulation (Bando OVM, ring road):')
    res = simulate_micro()
    print(f'  density       = {res.density * 1000:.1f} veh/km')
    print(f'  mean speed    = {res.mean_speed:.2f} m/s')
    print(f'  flow          = {res.flow * 3600:.0f} veh/h')
    print(f'  growth ratio  = {res.perturbation_growth:.2f}x  '
          f'({"unstable" if res.perturbation_growth > 1 else "stable"})')
    if res.wave_speed == res.wave_speed:  # not NaN
        direction = 'upstream (against flow)' if res.wave_speed < 0 else 'downstream (with flow)'
        print(f'  wave speed    = {res.wave_speed:.2f} m/s  ({direction})')

    print('\nLWR Godunov:')
    lwr = solve_lwr()
    print(f'  grid          = {len(lwr.x_axis)} cells x {len(lwr.t_axis)} frames')
    print(f'  rho range     = [{lwr.rho_history.min():.3f}, '
          f'{lwr.rho_history.max():.3f}] veh/m')

    print('\nShock speed rho_up -> rho_down (jam):')
    w = shock_speed(RHO_CRIT * 1.1, RHO_MAX * 0.85)
    print(f'  w = {w:.2f} m/s  (negative => upstream)')

    print('\nStability sweep (every other density):')
    for p in stability_sweep()[::2]:
        ws = '   --   ' if p.wave_speed != p.wave_speed else f'{p.wave_speed:+6.2f}'
        print(f'  rho={p.density*1000:6.1f} veh/km  '
              f'growth={p.growth_ratio:5.2f}  wave={ws} m/s  '
              f'{"stable" if p.stable else "unstable"}')
