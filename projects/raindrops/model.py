"""Raindrop Racing — Fluid Dynamics of Coalescence"""
import numpy as np, json
G = 9.81; GAMMA = 0.072; ETA = 1.8e-5; THETA = 15 * np.pi / 180
def terminal_velocity(radius):
    """Stokes terminal velocity with corrections."""
    if radius < 0.001: return 0
    v = (2/9) * (1000 - 1.2) * G * radius**2 / ETA
    return min(v, 50)
def simulate(n_drops=500, duration=60, dt=0.1):
    drops = [{'x': np.random.rand()*0.3, 'y': np.random.rand(), 'r': 0.0003+np.random.rand()*0.0007,
              'vx': 0, 'vy': 0, 'alive': True} for _ in range(n_drops)]
    history = []
    for step in range(int(duration/dt)):
        for d in drops:
            if not d['alive']: continue
            v = terminal_velocity(d['r']) * np.sin(THETA)
            d['vy'] = v
            d['y'] += d['vy'] * dt
            d['x'] += np.random.randn() * 0.001
            if d['y'] > 1.0 or d['y'] < 0: d['alive'] = False
        for i, a in enumerate(drops):
            if not a['alive']: continue
            for j, b in enumerate(drops):
                if i >= j or not b['alive']: continue
                dist = np.sqrt((a['x']-b['x'])**2 + (a['y']-b['y'])**2)
                if dist < (a['r'] + b['r']) * 1000:
                    a['r'] = (a['r']**3 + b['r']**3)**(1/3)
                    b['alive'] = False
        alive = [d for d in drops if d['alive']]
        history.append({'time': step*dt, 'alive': len(alive), 'max_r': max(d['r'] for d in alive) if alive else 0})
    return {'final_drops': sum(1 for d in drops if d['alive']), 'max_radius': max(d['r'] for d in drops),
            'history': history}
if __name__ == '__main__':
    r = simulate()
    print(f"Raindrop Racing: {r['final_drops']} surviving drops, max radius: {r['max_radius']*1000:.2f}mm")
    with open('data/results.json', 'w') as f: json.dump(r, f, indent=2, default=str)
