"""
The Optimal Shower — Heat Transfer + Fanger PMV + Sweep
"""
import numpy as np
from dataclasses import dataclass

H_WATER = 200
BODY_SURFACE = 1.8
BODY_TEMP = 37.0
C_WATER = 4186
AMBIENT_TEMP = 22.0
SHOWER_DURATION = 300
FLOW_RATE = 0.12


@dataclass
class ShowerResult:
    water_temp: float
    comfort_pmv: float
    comfort_ppd: float
    heat_loss: float
    energy_used: float
    comfort_energy_ratio: float


def fanger_pmv(t_air, t_radiant, t_skin, air_vel, humidity, metabolic, clothing):
    p_sat = 0.133 * np.exp(20.386 - 5132 / (t_skin + 273.15))
    p_vap = humidity / 100 * 0.133 * np.exp(20.386 - 5132 / (t_air + 273.15))
    f_cl = 1.0 + 0.15 * clothing
    h_c = 8.3 if air_vel < 0.1 else 8.3 * air_vel**0.6
    q_conv = f_cl * h_c * (t_skin - t_air)
    h_r = 4.7
    q_rad = f_cl * h_r * (t_skin - t_radiant)
    q_evap = 0.001 * metabolic * (p_sat - p_vap)
    L = q_conv + q_rad + q_evap - metabolic
    pmv = (0.303 * np.exp(-0.036 * metabolic) + 0.028) * L
    return np.clip(pmv, -3.0, 3.0)


def pmv_to_ppd(pmv):
    return 100 - 95 * np.exp(-0.03353 * pmv**4 - 0.2179 * pmv**2)


def simulate_shower(water_temp, duration=SHOWER_DURATION):
    skin_temp = min(water_temp, 42.0)
    q_body_loss = 0
    if water_temp < BODY_TEMP:
        q_body_loss = H_WATER * BODY_SURFACE * 0.7 * (BODY_TEMP - water_temp)
    mass = FLOW_RATE * duration
    energy = mass * C_WATER * (water_temp - 15.0)
    pmv = fanger_pmv(
        t_air=AMBIENT_TEMP + (water_temp - AMBIENT_TEMP) * 0.3,
        t_radiant=AMBIENT_TEMP + (water_temp - AMBIENT_TEMP) * 0.4,
        t_skin=skin_temp,
        air_vel=0.5,
        humidity=95.0,
        metabolic=80,
        clothing=0.0,
    )
    ppd = pmv_to_ppd(pmv)
    comfort_score = max(0, 1 - abs(pmv) / 3.0)
    energy_score = energy / 1e6
    ratio = comfort_score / max(0.01, energy_score)
    return ShowerResult(water_temp, pmv, ppd, q_body_loss * duration / 1000, energy / 1000, ratio)


def sweep_temperatures():
    temps = np.linspace(30, 45, 151)
    results = [simulate_shower(t) for t in temps]
    return temps, results


if __name__ == '__main__':
    temps, results = sweep_temperatures()
    for t, r in zip(temps[::10], results[::10]):
        print(f"{t:.0f}°C: PMV={r.comfort_pmv:+.2f}, E={r.energy_used:.0f}kJ")

import json

def run_full_analysis():
    """Run the full sweep and return structured results."""
    temps, results = sweep_temperatures()
    output = {
        'project': 'optimal-shower',
        'parameters': {
            'h_water': H_WATER,
            'body_surface': BODY_SURFACE,
            'body_temp': BODY_TEMP,
            'ambient_temp': AMBIENT_TEMP,
            'shower_duration': SHOWER_DURATION,
            'flow_rate': FLOW_RATE,
        },
        'sweep': [
            {
                'water_temp': float(t),
                'comfort_pmv': float(r.comfort_pmv),
                'comfort_ppd': float(r.comfort_ppd),
                'heat_loss_kj': float(r.heat_loss),
                'energy_used_kj': float(r.energy_used),
                'comfort_energy_ratio': float(r.comfort_energy_ratio),
            }
            for t, r in zip(temps, results)
        ],
        'optimal': None,
    }
    # Find the Pareto-optimal temperature (max comfort/energy ratio)
    best_idx = max(range(len(results)), key=lambda i: results[i].comfort_energy_ratio)
    best = results[best_idx]
    output['optimal'] = {
        'water_temp': float(temps[best_idx]),
        'comfort_pmv': float(best.comfort_pmv),
        'comfort_ppd': float(best.comfort_ppd),
        'heat_loss_kj': float(best.heat_loss),
        'energy_used_kj': float(best.energy_used),
        'comfort_energy_ratio': float(best.comfort_energy_ratio),
    }
    return output

if __name__ == '__main__' and not 'sweep_temperatures' in dir():
    pass  # already handled above
