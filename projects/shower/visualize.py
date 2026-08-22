"""Generate shower analysis plots."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import sys
sys.path.insert(0, '.')
from model import simulate_shower, sweep_temperatures

temps, results = sweep_temperatures()
pmvs = [r.comfort_pmv for r in results]
energies = [r.energy_used for r in results]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
ax1.plot(temps, pmvs)
ax1.set_title('PMV vs Temperature')
ax2.plot(temps, energies)
ax2.set_title('Energy vs Temperature')
plt.savefig('shower-analysis.png', dpi=150)
print('Saved: shower-analysis.png')
