import pytest, numpy as np, sys
sys.path.insert(0, '..')
from model import build_payoff_matrix, nash_equilibrium, compare_strategies

def test_payoff_matrix():
    m = build_payoff_matrix()
    assert m.shape == (3, 3)
    assert np.all(m >= 0) and np.all(m <= 1)

def test_nash_equilibrium():
    m = build_payoff_matrix()
    strat, val = nash_equilibrium(m)
    assert abs(sum(strat) - 1.0) < 0.01
    assert 0 < val < 1

def test_strategy_comparison():
    results = compare_strategies()
    assert 'nash' in results
    assert results['nash']['min'] >= results['always_left']['min']

def test_reproducibility():
    m1 = build_payoff_matrix()
    m2 = build_payoff_matrix()
    assert np.array_equal(m1, m2)

def test_nash_indifference():
    m = build_payoff_matrix()
    strat, val = nash_equilibrium(m)
    rates = [sum(strat[i]*m[i][j] for i in range(3)) for j in range(3)]
    assert max(rates) - min(rates) < 0.1
