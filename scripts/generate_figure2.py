"""
Figure 2 — Modelled Travel Time: Distance-Only vs Crowd-Aware Routing
Generates figure2_travel_time.png for the IEEE research paper (PMPML Pulse).
Run from the project root:
    python scripts/generate_figure2.py
Output: docs/figures/figure2_travel_time.png
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# ------------------------------------------------------------------
# Data — Monday 08:30, Heavy Monsoon, Swargate + Univ Chowk surge
# ------------------------------------------------------------------
routes = [
    "Swargate\n→ Hinjewadi",
    "Hadapsar\n→ Pune Univ.",
    "Kothrud\n→ Phoenix Mall",
    "Nigdi\n→ Swargate",
    "Lohegaon\n→ Deccan",
]

standard_times  = [68.0, 52.0, 48.0, 60.0, 55.0]
optimized_times = [45.0, 36.0, 34.0, 42.0, 40.0]
savings_pct     = [33.8, 30.8, 29.2, 30.0, 27.3]

x       = np.arange(len(routes))
width   = 0.35

# ------------------------------------------------------------------
# Figure
# ------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9, 5))
fig.patch.set_facecolor('#FFFFFF')
ax.set_facecolor('#F8FAFC')

bars_std = ax.bar(x - width/2, standard_times,  width,
                  label='Distance-only Dijkstra',
                  color='#94A3B8', edgecolor='#64748B', linewidth=0.7, zorder=3)

bars_opt = ax.bar(x + width/2, optimized_times, width,
                  label='Crowd-aware routing',
                  color='#3B82F6', edgecolor='#1D4ED8', linewidth=0.7, zorder=3)

# Value labels on bars
for bar in bars_std:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.8,
            f'{bar.get_height():.0f}', ha='center', va='bottom',
            fontsize=8.5, color='#475569', fontweight='bold')

for bar, pct in zip(bars_opt, savings_pct):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.8,
            f'{bar.get_height():.0f}', ha='center', va='bottom',
            fontsize=8.5, color='#1D4ED8', fontweight='bold')
    # Saving annotation
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5.5,
            f'−{pct}%', ha='center', va='bottom',
            fontsize=7.5, color='#16A34A', fontstyle='italic', fontweight='bold')

# Grid and spines
ax.yaxis.grid(True, linestyle='--', linewidth=0.6, alpha=0.7, color='#CBD5E1', zorder=0)
ax.set_axisbelow(True)
for spine in ['top', 'right']:
    ax.spines[spine].set_visible(False)
ax.spines['left'].set_color('#CBD5E1')
ax.spines['bottom'].set_color('#CBD5E1')

# Labels
ax.set_xlabel('Route Corridor', fontsize=10, labelpad=8, color='#334155')
ax.set_ylabel('Modelled Travel Time (minutes)', fontsize=10, labelpad=8, color='#334155')
ax.set_title(
    'Fig. 2.  Modelled travel time under distance-only and crowd-aware routing\n'
    '(Monday 08:30, heavy monsoon, Swargate and University Chowk surge nodes)',
    fontsize=9.5, color='#1E293B', pad=12
)
ax.set_xticks(x)
ax.set_xticklabels(routes, fontsize=9, color='#334155')
ax.set_yticks(range(0, 85, 10))
ax.set_ylim(0, 82)
ax.tick_params(axis='y', labelcolor='#64748B', labelsize=8.5)

# Legend
legend = ax.legend(
    handles=[
        mpatches.Patch(color='#94A3B8', label='Distance-only Dijkstra'),
        mpatches.Patch(color='#3B82F6', label='Crowd-aware routing'),
    ],
    loc='upper right', fontsize=9,
    framealpha=0.95, edgecolor='#E2E8F0'
)

# Average line
avg_std = sum(standard_times) / len(standard_times)
avg_opt = sum(optimized_times) / len(optimized_times)
ax.axhline(avg_std, color='#94A3B8', linestyle=':', linewidth=1.2, alpha=0.7)
ax.axhline(avg_opt, color='#3B82F6', linestyle=':', linewidth=1.2, alpha=0.7)
ax.text(len(routes) - 0.05, avg_std + 0.8, f'avg {avg_std:.1f}',
        ha='right', fontsize=7.5, color='#64748B')
ax.text(len(routes) - 0.05, avg_opt + 0.8, f'avg {avg_opt:.1f}',
        ha='right', fontsize=7.5, color='#2563EB')

plt.tight_layout()

# ------------------------------------------------------------------
# Save
# ------------------------------------------------------------------
out_dir = os.path.join(os.path.dirname(__file__), '..', 'docs', 'figures')
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, 'figure2_travel_time.png')
plt.savefig(out_path, dpi=200, bbox_inches='tight', facecolor='white')
print(f"Saved → {os.path.abspath(out_path)}")
plt.close()

