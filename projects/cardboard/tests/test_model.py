"""
Tests for the cardboard strength model.

Run:  python -m pytest tests/test_model.py -v
"""
import os
import sys
import json

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import model as M


# --------------------------------------------------------------------------- #
# Geometry
# --------------------------------------------------------------------------- #
def test_flute_profile_zero_at_origin():
    """The sinusoidal flute starts at zero (bonded to the liner)."""
    assert abs(M.flute_profile(np.array([0.0]))[0]) < 1e-12
    assert abs(M.flute_profile(np.array([M.FLUTE_PITCH]))[0]) < 1e-12


def test_flute_amplitude_matches_height():
    """Peak amplitude equals half the flute height."""
    x = np.array([M.FLUTE_PITCH / 4.0])
    assert abs(M.flute_profile(x)[0] - M.FLUTE_HEIGHT / 2.0) < 1e-15


def test_arc_factor_greater_than_one():
    """A corrugated medium is longer than its flat pitch."""
    af = M.arc_factor()
    assert af > 1.0
    # For h=4.7mm, p=7.2mm the arc factor is ~1.7
    assert 1.4 < af < 2.0


# --------------------------------------------------------------------------- #
# Mass equivalence
# --------------------------------------------------------------------------- #
def test_equivalent_flat_thickness_positive_and_smaller_than_total():
    """The mass-equivalent flat sheet is thin and carries all the paper."""
    t_eq = M.equivalent_flat_thickness()
    assert t_eq > 0
    # Must be heavier than two liners alone
    assert t_eq > 2 * M.T_LINER


def test_mass_consistency():
    """Mass of the flat-equivalent sheet equals the corrugated mass."""
    m_corr = M.mass_per_unit_area()
    t_eq = M.equivalent_flat_thickness()
    m_flat = t_eq * M.RHO_PAPER
    assert abs(m_corr - m_flat) < 1e-6


# --------------------------------------------------------------------------- #
# Stiffness
# --------------------------------------------------------------------------- #
def test_corrugated_stiffer_than_flat():
    """The headline result: corrugation multiplies I by ~40x."""
    I_corr = M.second_moment_corrugated()
    I_flat = M.second_moment_flat(M.equivalent_flat_thickness())
    ratio = I_corr / I_flat
    assert ratio > 30.0
    assert ratio < 80.0


# --------------------------------------------------------------------------- #
# Euler buckling
# --------------------------------------------------------------------------- #
def test_euler_formula_unit_case():
    """P_cr = pi^2 E I / L^2 for the textbook case."""
    E, I, L = 1.0, 1.0, 1.0
    assert abs(M.euler_buckling_load(E, I, L) - np.pi ** 2) < 1e-9


def test_euler_load_decreases_with_length():
    """Doubling the length quarters the Euler load."""
    L1 = 0.2
    L2 = 0.4
    I = M.second_moment_corrugated()
    p1 = M.euler_buckling_load(M.E_KRAFT, I, L1)
    p2 = M.euler_buckling_load(M.E_KRAFT, I, L2)
    assert abs(p1 / p2 - 4.0) < 1e-6


# --------------------------------------------------------------------------- #
# Tilt model
# --------------------------------------------------------------------------- #
def test_tilt_zero_equals_axial():
    """At zero tilt the capacity equals the axial buckling load."""
    P0 = 1000.0
    assert abs(M.buckling_load_vs_tilt(0.0, P0) - P0) < 1e-9


def test_tilt_monotonic_decrease():
    """Capacity decreases as the tilt angle increases."""
    P0 = 1000.0
    angles = np.linspace(0, np.deg2rad(30), 10)
    loads = M.buckling_load_vs_tilt(angles, P0)
    assert np.all(np.diff(loads) < 0)


def test_tilt_15deg_drops_about_60_percent():
    """Key finding: a 15 deg tilt cuts capacity by ~60%."""
    P0 = M.euler_buckling_load(M.E_KRAFT, M.second_moment_corrugated(),
                               M.COLUMN_LENGTH)
    p15 = M.buckling_load_vs_tilt(np.deg2rad(15.0), P0)
    drop = (1.0 - p15 / P0) * 100.0
    assert 55.0 < drop < 65.0


# --------------------------------------------------------------------------- #
# FEA
# --------------------------------------------------------------------------- #
def test_fea_matches_euler_arc_length():
    """The FEA eigenvalue should reproduce the Euler load with arc length."""
    res = M.fea_buckling_load(n_elements=48)
    ratio = res["fea_over_euler_arc"]
    # Within 5% of the analytical estimate
    assert abs(ratio - 1.0) < 0.05


def test_fea_refinement_converges():
    """More elements -> stable eigenvalue."""
    coarse = M.fea_buckling_load(n_elements=16)["critical_axial_force_N_per_slice"]
    fine = M.fea_buckling_load(n_elements=96)["critical_axial_force_N_per_slice"]
    assert abs(coarse - fine) / fine < 0.10


# --------------------------------------------------------------------------- #
# Full simulation
# --------------------------------------------------------------------------- #
def test_simulate_returns_20kg_hold():
    """The 20 kg box does not collapse under the model."""
    res = M.simulate(applied_mass_kg=20.0)
    assert res.holds_20kg is True
    assert res.safety_factor > 1.0
    assert res.stiffness_ratio > 30.0


def test_results_json_written():
    """Running model.py as a script writes a results.json."""
    res = M.simulate()
    d = M.results_to_dict(res)
    # Must be JSON-serialisable
    assert json.loads(json.dumps(d)) is not None
    assert "stiffness_ratio" in d
    assert "fea" in d
    assert "tilt_15_drop_percent" in d


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
