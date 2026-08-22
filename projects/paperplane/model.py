"""The Optimal Paper Airplane — Aerodynamic Optimization"""
import numpy as np, json
from scipy.optimize import minimize
def glide_ratio(wingspan, nose_angle, cg_position, alpha):
    """Compute glide ratio L/D for a paper airplane."""
    CL = 2 * np.pi * np.sin(np.radians(alpha))
    CD0 = 0.02 + 0.01 * (1 - wingspan/0.3)
    k = 1 / (np.pi * 0.7 * wingspan)
    CD = CD0 + k * CL**2
    LD = CL / CD if CD > 0 else 0
    LD *= (1 - abs(cg_position - 0.3) * 2)
    LD *= (1 - abs(nose_angle - 30) / 90)
    return max(LD, 0.1)
def optimize():
    def objective(x):
        return -glide_ratio(x[0], x[1], x[2], x[3])
    result = minimize(objective, [0.25, 30, 0.3, 6],
        bounds=[(0.1, 0.4), (10, 80), (0.1, 0.5), (2, 15)], method='L-BFGS-B')
    return result.x, -result.fun
if __name__ == '__main__':
    params, ratio = optimize()
    print(f"Optimal Paper Airplane:")
    print(f"  Wingspan: {params[0]*100:.1f}cm, Nose angle: {params[1]:.1f}°")
    print(f"  CG position: {params[2]:.2f}, Angle of attack: {params[3]:.1f}°")
    print(f"  Glide ratio: {ratio:.1f}:1")
    with open('data/results.json', 'w') as f:
        json.dump({'optimal_params': params.tolist(), 'glide_ratio': float(ratio)}, f, indent=2)
