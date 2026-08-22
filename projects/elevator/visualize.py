"""Elevator visualization"""
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np, sys, os
sys.path.insert(0, '.')
from model import compare
NAVY='#001F3F'; MUTED='#6B7A8D'; LABEL='#8FA3B1'; BG='#FFFFFF'; RULE='#D6DBE0'
fig, axes = plt.subplots(2,2, figsize=(16,10), constrained_layout=True)
fig.patch.set_facecolor(BG)
results = compare()
names = list(results.keys())
means = [results[n]['mean_wait'] for n in names]
stds = [results[n]['std_wait'] for n in names]
# Bar chart
ax=axes[0,0]; ax.set_facecolor(BG)
ax.bar(names, means, color=[NAVY,LABEL,'#8B1A1A'], width=0.5, alpha=0.7)
ax.set_ylabel('Mean Wait Time (s)', fontsize=10, color=MUTED)
ax.set_title('Average Wait Time by Algorithm', fontsize=13, color=NAVY, fontweight='bold', pad=12)
ax.tick_params(colors=MUTED, labelsize=9)
for s in ax.spines.values(): s.set_color(RULE); s.set_linewidth(0.5)
# Std dev
ax=axes[0,1]; ax.set_facecolor(BG)
ax.bar(names, stds, color=[NAVY,LABEL,'#8B1A1A'], width=0.5, alpha=0.7)
ax.set_ylabel('Std Dev (s)', fontsize=10, color=MUTED)
ax.set_title('Wait Time Variance', fontsize=13, color=NAVY, fontweight='bold', pad=12)
ax.tick_params(colors=MUTED, labelsize=9)
for s in ax.spines.values(): s.set_color(RULE); s.set_linewidth(0.5)
# Improvement
ax=axes[1,0]; ax.set_facecolor(BG)
improvements = [(results['Random']['mean_wait']-results[n]['mean_wait'])/results['Random']['mean_wait']*100 for n in names]
ax.bar(names, improvements, color=NAVY, width=0.5, alpha=0.7)
ax.set_ylabel('Improvement vs Random (%)', fontsize=10, color=MUTED)
ax.set_title('Algorithm Improvement', fontsize=13, color=NAVY, fontweight='bold', pad=12)
ax.tick_params(colors=MUTED, labelsize=9)
for s in ax.spines.values(): s.set_color(RULE); s.set_linewidth(0.5)
# Pie
ax=axes[1,1]; ax.set_facecolor(BG)
ax.pie(means, labels=names, colors=[NAVY,LABEL,'#8B1A1A'], autopct='%1.0f%%', textprops={'color':MUTED,'fontsize':9})
ax.set_title('Wait Time Distribution', fontsize=13, color=NAVY, fontweight='bold', pad=12)
fig.suptitle('Elevator Dispatching — Queueing Theory', fontsize=18, color=NAVY, fontweight='bold', y=1.02)
os.makedirs('docs/viz', exist_ok=True)
plt.savefig('docs/viz/analysis-light.png', dpi=150, bbox_inches='tight', facecolor=BG)
plt.close(); print("Saved: docs/viz/analysis-light.png")
