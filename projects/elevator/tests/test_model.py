"""Tests for Elevator Dispatching model.

Verifies:
  1. generate_passengers produces correct count
  2. compare() returns all three algorithms
  3. LOOK is faster than Random
  4. SCAN is faster than Random
  5. Results are reproducible (same seed = same output)
"""
import sys
sys.path.insert(0, '..')

from model import compare, generate_passengers, simulate_scan, simulate_look, simulate_random


def test_generate():
    p = generate_passengers(10)
    assert len(p) == 10
    assert all('origin' in x and 'dest' in x and 'time' in x for x in p)


def test_compare_returns_all_three():
    r = compare()
    assert 'SCAN' in r and 'LOOK' in r and 'Random' in r
    assert 'mean_wait' in r['SCAN']
    assert 'std_wait' in r['SCAN']


def test_look_better_than_random():
    r = compare()
    assert r['LOOK']['mean_wait'] < r['Random']['mean_wait'], \
        f"LOOK ({r['LOOK']['mean_wait']:.1f}) should be < Random ({r['Random']['mean_wait']:.1f})"


def test_scan_better_than_random():
    r = compare()
    assert r['SCAN']['mean_wait'] < r['Random']['mean_wait'], \
        f"SCAN ({r['SCAN']['mean_wait']:.1f}) should be < Random ({r['Random']['mean_wait']:.1f})"


def test_reproducible():
    r1 = compare()
    r2 = compare()
    assert r1['SCAN']['mean_wait'] == r2['SCAN']['mean_wait'], \
        "Same seed should produce same results"
