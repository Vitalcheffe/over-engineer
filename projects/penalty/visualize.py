"""Penalty Kick visualization"""
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np, json, sys, os
sys.path.insert(0, '.')
from model import build_payoff_matrix, nash_equilibrium, compare_strategies

NAVY='#001F3F'; MUTED='#6B7A8D'; LABEL='#8FA3B1'; BG='#FFFFFF'; RULE='#D6DBE0'
fig, axes = plt.subplots(2,2, figsize=(16,10), constrained_layout=True)
fig.patch.set_facecolor(BG)
matrix = build_payoff_matrix()
nash, val = nash_equilibrium(matrix)

# 1. Payoff matrix heatmap
ax=axes[0,0]; ax.set_facecolor(BG)
im=ax.imshow(matrix, cmap='Blues', vmin=0, vmax=1)
for i in range(3):
    for j in range(3):
        ax.text(j,i,f'{matrix[i][j]:.2f}',ha='center',va='center',fontsize=12,color=NAVY if matrix[i][j]>0.5 else MUTED)
ax.set_xticks([0,1,2]); ax.set_yticks([0,1,2])
ax.set_xticklabels(['Keeper L','Keeper C','Keeper R'],fontsize=9,color=MUTED)
ax.set_yticklabels(['Shoot L','Shoot C','Shoot R'],fontsize=9,color=MUTED)
ax.set_title('Payoff Matrix (P(goal))',fontsize=13,color=NAVY,fontweight='bold',pad=12)
for s in ax.spines.values(): s.set_color(RULE); s.set_linewidth(0.5)

# 2. Nash equilibrium
ax=axes[0,1]; ax.set_facecolor(BG)
zones=['Left','Center','Right']
ax.bar(zones, nash, color=NAVY, width=0.5, alpha=0.7)
ax.set_ylabel('Probability',fontsize=10,color=MUTED)
ax.set_title(f'Nash Equilibrium Strategy (goal rate: {val:.1%})',fontsize=13,color=NAVY,fontweight='bold',pad=12)
ax.tick_params(colors=MUTED,labelsize=9)
for s in ax.spines.values(): s.set_color(RULE); s.set_linewidth(0.5)

# 3. Strategy comparison
ax=axes[1,0]; ax.set_facecolor(BG)
results=compare_strategies()
names=list(results.keys())
mins=[results[n]['min'] for n in names]
avgs=[results[n]['avg'] for n in names]
maxs=[results[n]['max'] for n in names]
x=np.arange(len(names))
ax.bar(x-0.2,mins,0.2,color=MUTED,label='Worst case')
ax.bar(x,avgs,0.2,color=NAVY,label='Average')
ax.bar(x+0.2,maxs,0.2,color=LABEL,label='Best case')
ax.set_xticks(x); ax.set_xticklabels(names,fontsize=8,color=MUTED,rotation=15)
ax.set_ylabel('Goal Rate',fontsize=10,color=MUTED)
ax.set_title('Strategy Comparison',fontsize=13,color=NAVY,fontweight='bold',pad=12)
ax.tick_params(colors=MUTED,labelsize=9); ax.legend(fontsize=8,frameon=False,labelcolor=MUTED)
for s in ax.spines.values(): s.set_color(RULE); s.set_linewidth(0.5)

# 4. Goal zones
ax=axes[1,1]; ax.set_facecolor(BG)
goal_w=7.32; goal_h=2.44
rect=plt.Rectangle((-goal_w/2,0),goal_w,goal_h,fill=False,edgecolor=NAVY,linewidth=2)
ax.add_patch(rect)
ax.plot([-goal_w/6,goal_w/6],[0,0],'k-',linewidth=1)
ax.text(-goal_w/3,goal_h/2,f'{nash[0]:.0%}',ha='center',va='center',fontsize=14,color=NAVY,fontweight='bold')
ax.text(0,goal_h/2,f'{nash[1]:.0%}',ha='center',va='center',fontsize=14,color=NAVY,fontweight='bold')
ax.text(goal_w/3,goal_h/2,f'{nash[2]:.0%}',ha='center',va='center',fontsize=14,color=NAVY,fontweight='bold')
ax.set_xlim(-5,5); ax.set_ylim(-0.5,3.5)
ax.set_title('Optimal Shooting Distribution',fontsize=13,color=NAVY,fontweight='bold',pad=12)
ax.tick_params(colors=MUTED,labelsize=9)
for s in ax.spines.values(): s.set_color(RULE); s.set_linewidth(0.5)
ax.set_aspect('equal')

fig.suptitle('The Penalty Kick Game',fontsize=18,color=NAVY,fontweight='bold',y=1.02)
os.makedirs('docs/viz',exist_ok=True)
plt.savefig('docs/viz/analysis-light.png',dpi=150,bbox_inches='tight',facecolor=BG)
plt.close(); print("Saved: docs/viz/analysis-light.png")
