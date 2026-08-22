"""Unit tests for the phantom-traffic-jams model.

Run with:
    pytest tests/test_model.py -v
"""
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model import (
    V_MAX, RHO_MAX, ROAD_LENGTH, NUM_CARS,
    v_of_rho, q_of_rho, v_optimal, v_optimal_derivative,
    critical_density_greenshields, critical_density_ovm,
    max_flow, shock_speed, simulate_micro, solve_lwr,
    stability_sweep, critical_density_empirical, save_results,
)


def test_fundamental_diagram_endpoints():
    """At rho=0 cars travel at v_max; at rho=rho_max everyone is stopped."""
    assert abs(float(v_of_rho(0.0)) - V_MAX) < 1e-9
    assert abs(float(v_of_rho(RHO_MAX))) < 1e-9
    assert abs(float(q_of_rho(0.0))) < 1e-9
    assert abs(float(q_of_rho(RHO_MAX))) < 1e-9


def test_capacity_at_critical_density():
    """Greenshields flow peaks at rho_max/2; q_max = v_max * rho_max / 4."""
    rho_c = critical_density_greenshields()
    assert abs(rho_c - RHO_MAX / 2) < 1e-9
    q_peak = float(q_of_rho(rho_c))
    q_theoretical = max_flow()
    assert abs(q_peak - q_theoretical) < 1e-6
    # Also: q at rho_c must exceed q at neighbouring densities
    assert float(q_of_rho(rho_c)) > float(q_of_rho(rho_c * 0.5))
    assert float(q_of_rho(rho_c)) > float(q_of_rho(rho_c * 1.5))


def test_optimal_velocity_monotone_and_bounded():
    """V(dx) is non-decreasing, 0 below dx_min, v_max above dx_max."""
    dx = np.linspace(0, 60, 200)
    v = v_optimal(dx)
    assert np.all(v >= -1e-9)
    assert np.all(v <= V_MAX + 1e-9)
    # Monotone non-decreasing
    assert np.all(np.diff(v) >= -1e-9)
    # Plateau above DX_MAX
    assert abs(float(v_optimal(50.0)) - V_MAX) < 1e-6
    # Zero below DX_MIN
    assert float(v_optimal(2.0)) < 1e-6


def test_critical_density_matches_ovm_theory():
    """OVM critical density is 1/DX_MAX; V' is constant in the ramp."""
    from model import DX_MAX, DX_MIN
    rho_c = critical_density_ovm()
    assert abs(rho_c - 1.0 / DX_MAX) < 1e-9
    slope = v_optimal_derivative()
    assert abs(slope - V_MAX / (DX_MAX - DX_MIN)) < 1e-9


def test_shock_speed_negative_upstream():
    """Shock from a high-flow state into a deep jam travels upstream.

    Rankine-Hugoniot w = (q2-q1)/(rho2-rho1).  For the shock to move
    upstream (w < 0) we need q2 < q1 with rho2 > rho1 -- i.e. the
    downstream state is deep enough in congestion that its flow is
    lower than the upstream state's.  This is the classic "jamiton"
    configuration that produces phantom-jam propagation.
    """
    rho_up = 0.05    # veh/m: free-flow side, q ~ 0.97 veh/s
    rho_down = 0.13  # veh/m: deep jam,     q ~ 0.36 veh/s
    w = shock_speed(rho_up, rho_down)
    assert w < 0, f"shock should propagate upstream, got w={w}"


def test_microsimulation_runs_and_returns_history():
    """Microsim returns arrays of the expected shape with finite values."""
    res = simulate_micro(n_cars=40, length=400.0, t_total=30.0, perturb=2.0)
    assert res.n_cars == 40
    assert res.length == 400.0
    assert res.history.ndim == 2
    assert res.history.shape[1] == 40
    assert np.all(np.isfinite(res.history))
    assert np.all(np.isfinite(res.speeds))
    assert res.history.shape[0] == res.speeds.shape[0]
    # density and mean speed should be sensible
    assert res.density == pytest.approx(40 / 400.0)
    assert 0.0 <= res.mean_speed <= V_MAX


def test_microsimulation_perturbation_amplifies_above_critical():
    """Above the critical density, the perturbation should grow (>1x)."""
    # 100 cars on 1000 m ring = 100 veh/km, well above ~30 veh/km
    res = simulate_micro(n_cars=100, length=1000.0, t_total=300.0, perturb=4.0)
    assert res.perturbation_growth > 1.0, (
        f"expected amplification above critical density; "
        f"got growth={res.perturbation_growth}"
    )


def test_microsimulation_perturbation_damps_below_critical():
    """Below the critical density, the perturbation should dissipate."""
    # 12 cars on 1000 m ring = 12 veh/km, well below ~30 veh/km
    res = simulate_micro(n_cars=12, length=1000.0, t_total=120.0, perturb=4.0)
    assert res.perturbation_growth <= 1.05, (
        f"expected damping below critical density; "
        f"got growth={res.perturbation_growth}"
    )


def test_lwr_solver_conserves_vehicles():
    """LWR Godunov on a periodic ring conserves total vehicles."""
    lwr = solve_lwr(t_total=30.0)
    total_initial = float(lwr.rho_history[0].sum()) * (lwr.x_axis[1] - lwr.x_axis[0])
    total_final = float(lwr.rho_history[-1].sum()) * (lwr.x_axis[1] - lwr.x_axis[0])
    rel_err = abs(total_final - total_initial) / max(total_initial, 1e-9)
    assert rel_err < 1e-3, f"LWR lost {rel_err:.2%} of vehicles"


def test_stability_sweep_recovers_critical_density():
    """The empirical critical density lies in [15, 60] veh/km."""
    rho_c = critical_density_empirical() * 1000  # veh/km
    assert 15.0 < rho_c < 60.0, f"rho_c={rho_c} veh/km out of expected band"


def test_results_json_serializes(tmp_path):
    """save_results writes a JSON file that parses back cleanly."""
    out = tmp_path / "results.json"
    save_results(str(out))
    import json
    d = json.loads(out.read_text())
    assert d['project'] == 'phantom-traffic-jams'
    assert 'parameters' in d
    assert 'results' in d
    assert 'stability_sweep' in d
    assert len(d['stability_sweep']) >= 10
    # numeric sanity
    r = d['results']
    assert r['max_flow_veh_per_h'] > 0
    assert r['critical_density_ovm_veh_per_km'] == pytest.approx(30.3, abs=0.5)
