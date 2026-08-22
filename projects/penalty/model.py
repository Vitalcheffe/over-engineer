"""The Penalty Kick Game — Zero-Sum Game Theory"""
import numpy as np
import json
from scipy.optimize import linprog

GOAL_WIDTH = 7.32
BALL_SPEED = 27.0
KEEPER_DIVE_SPEED = 5.0
KEEPER_REACH = 3.0
ZONES = ['left', 'center', 'right']

def goal_probability(shooter, keeper):
    if shooter == keeper:
        return 0.35 if shooter == 'center' else 0.25
    return 0.85 if shooter == 'center' else 0.92

def build_payoff_matrix():
    m = np.zeros((3, 3))
    for i, s in enumerate(ZONES):
        for j, k in enumerate(ZONES):
            m[i][j] = goal_probability(s, k)
    return m

def nash_equilibrium(matrix):
    n = 3
    c = np.zeros(n + 1); c[-1] = -1
    A_ub = np.zeros((n, n + 1))
    for j in range(n):
        for i in range(n):
            A_ub[j][i] = -matrix[i][j]
        A_ub[j][-1] = 1
    b_ub = np.zeros(n)
    A_eq = np.ones((1, n + 1)); A_eq[0][-1] = 0
    b_eq = [1.0]
    bounds = [(0, 1)] * n + [(0, 1)]
    res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
    if res.success:
        return res.x[:n], res.x[-1]
    return np.ones(n)/n, float(np.mean(matrix))

def compare_strategies():
    matrix = build_payoff_matrix()
    nash, val = nash_equilibrium(matrix)
    strategies = {
        'always_left': [1,0,0], 'always_center': [0,1,0],
        'always_right': [0,0,1], 'random': [1/3,1/3,1/3],
        'nash': nash.tolist(),
    }
    results = {}
    for name, strat in strategies.items():
        rates = [sum(strat[i]*matrix[i][j] for i in range(3)) for j in range(3)]
        results[name] = {'min': float(min(rates)), 'avg': float(np.mean(rates)), 'max': float(max(rates))}
    return results

if __name__ == '__main__':
    matrix = build_payoff_matrix()
    nash, val = nash_equilibrium(matrix)
    print(f"Nash equilibrium goal rate: {val:.1%}")
    print(f"Shooter strategy: L={nash[0]:.3f} C={nash[1]:.3f} R={nash[2]:.3f}")
    results = compare_strategies()
    with open('data/results.json', 'w') as f:
        json.dump({'payoff_matrix': matrix.tolist(), 'nash_shooter': nash.tolist(),
                   'nash_value': float(val), 'strategy_comparison': results}, f, indent=2)
    print("Saved: data/results.json")
