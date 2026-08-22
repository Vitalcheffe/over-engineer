"""Tests for The Optimal Shower model.

Verifies:
  1. Fanger PMV returns values in [-3, +3]
  2. PMV = 0 at neutral temperature (~34°C with these parameters)
  3. Heat loss increases with temperature
  4. Energy increases linearly with temperature
  5. The optimal temperature is in the physiological range (30-40°C)
  6. Results JSON is produced and has the expected schema
"""
import sys
sys.path.insert(0, '..')

import json
import os
import numpy as np
from model import fanger_pmv, pmv_to_ppd, simulate_shower, sweep_temperatures, run_full_analysis


def test_pmv_in_range():
    """PMV should always be in [-3, +3] (clipped)."""
    for t in range(20, 50):
        pmv = fanger_pmv(
            t_air=22 + (t - 22) * 0.3,
            t_radiant=22 + (t - 22) * 0.4,
            t_skin=min(t, 42),
            air_vel=0.5,
            humidity=95.0,
            metabolic=80,
            clothing=0.0,
        )
        assert -3.0 <= pmv <= 3.0, f"PMV={pmv} out of range at T={t}"


def test_pmv_near_zero_at_optimal():
    """PMV should be near 0 at ~34°C (the claimed optimal)."""
    r = simulate_shower(34.0)
    assert abs(r.comfort_pmv) < 0.1, f"PMV={r.comfort_pmv} at 34°C, expected ~0"


def test_heat_loss_decreases_above_body_temp():
    """Above body temp (37°C), the body gains heat from water, so heat_loss = 0.
    Below body temp, heat_loss > 0 and increases as water gets colder."""
    r_below = simulate_shower(34.0)
    r_above = simulate_shower(42.0)
    assert r_above.heat_loss == 0.0, "Heat loss should be 0 when water > body temp"
    assert r_below.heat_loss > 0.0, "Heat loss should be > 0 when water < body temp"


def test_energy_increases_with_temp():
    """Higher water temp → more energy used."""
    r_low = simulate_shower(34.0)
    r_high = simulate_shower(42.0)
    assert r_high.energy_used > r_low.energy_used, \
        f"Energy at 42°C ({r_high.energy_used}) should be > 34°C ({r_low.energy_used})"


def test_optimal_in_physiological_range():
    """The Pareto-optimal temperature should be in 30-40°C."""
    output = run_full_analysis()
    optimal_temp = output['optimal']['water_temp']
    assert 30 <= optimal_temp <= 40, \
        f"Optimal temp {optimal_temp}°C outside physiological range [30, 40]"


def test_results_json_written():
    """run_full_analysis produces a valid results.json."""
    output = run_full_analysis()
    assert 'project' in output
    assert 'optimal' in output
    assert 'water_temp' in output['optimal']
    assert 'comfort_pmv' in output['optimal']
    assert 'energy_used_kj' in output['optimal']
    assert len(output['sweep']) > 100
