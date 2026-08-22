"""The Self-Balancing Tray — Slosh Dynamics + LQR"""
import numpy as np, json
def simulate_lqr(dt=0.01, duration=10):
    # State: [tray_angle, tray_vel, fluid_angle, fluid_vel]
    A = np.array([[0, 1, 0, 0],
                   [-5, -0.1, 1, 0],
                   [0, 0, 0, 1],
                   [3, 0, -3, -0.2]])
    B = np.array([[0], [1], [0], [0.5]])
    Q = np.diag([10, 1, 30, 1])  # Weight fluid stability 3x more
    R = np.array([[1]])
    # Solve discrete LQR
    from scipy.linalg import solve_discrete_are
    n = 4
    Ad = np.eye(n) + A * dt
    Bd = B * dt
    P = solve_discrete_are(Ad, Bd, Q, R)
    K = np.linalg.inv(R + Bd.T @ P @ Bd) @ (Bd.T @ P @ Ad)
    # Simulate
    state = np.array([0.1, 0, 0.2, 0])  # Initial: tray tilted, fluid sloshing
    history = {'tray_angle': [], 'fluid_angle': []}
    for _ in range(int(duration/dt)):
        u = -K @ state
        state = Ad @ state + Bd.flatten() * u
        history['tray_angle'].append(float(state[0]))
        history['fluid_angle'].append(float(state[2]))
    return {'final_tray': float(state[0]), 'final_fluid': float(state[2]),
            'history': history, 'peak_slosh': float(max(abs(f) for f in history['fluid_angle']))}
def simulate_uncontrolled(dt=0.01, duration=10):
    A = np.array([[0, 1, 0, 0],[-5, -0.1, 1, 0],[0, 0, 0, 1],[3, 0, -3, -0.2]])
    state = np.array([0.1, 0, 0.2, 0])
    peak = 0
    for _ in range(int(duration/dt)):
        state = state + A @ state * dt
        peak = max(peak, abs(state[2]))
    return {'peak_slosh': float(peak)}
if __name__ == '__main__':
    lqr = simulate_lqr()
    uncontrolled = simulate_uncontrolled()
    print(f"LQR: peak slosh={lqr['peak_slosh']:.3f}, final tray={lqr['final_tray']:.4f}")
    print(f"Uncontrolled: peak slosh={uncontrolled['peak_slosh']:.3f}")
    print(f"Improvement: {(1-lqr['peak_slosh']/uncontrolled['peak_slosh'])*100:.0f}%")
    with open('data/results.json', 'w') as f:
        json.dump({'lqr': lqr, 'uncontrolled': uncontrolled}, f, indent=2, default=str)
