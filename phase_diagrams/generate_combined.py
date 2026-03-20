#!/usr/bin/env python3
"""
Generate a publication-quality 2x2 combined phase diagram figure
for WAMS 2026 Paper #68.

Systems:
  (a) Fe-Ti  — Mare basalt ISRU (ilmenite reduction)
  (b) Al-Ti  — Highlands+Mare ISRU (TiAl intermetallics for aerospace)
  (c) Al-Fe  — Cross-terrane blend (highlands Al + mare Fe)
  (d) Al-Ni  — Ni-superalloy route (Earth Ni + lunar Al)

Data sources:
  COST507: EU COST Action 507 database, Round II (Jan 1999)
  Dupin 2001: N. Dupin et al., Phil. Mag. 81(5), 2001, pp. 547-578
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pycalphad import Database, binplot
import pycalphad.variables as v
import os
import warnings
warnings.filterwarnings('ignore')

OUTDIR = os.path.dirname(os.path.abspath(__file__))
db = Database(os.path.join(OUTDIR, 'COST507.tdb'))
nial_db = Database(os.path.join(OUTDIR, 'nial_dupin.tdb'))

# Publication styling
plt.rcParams.update({
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'legend.fontsize': 7,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'axes.linewidth': 0.8,
})

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# (a) Fe-Ti
print("Calculating Fe-Ti...")
binplot(db, ['FE', 'TI', 'VA'],
        ['LIQUID', 'BCC_A2', 'HCP_A3', 'FCC_A1', 'LAVES_C14', 'FETI'],
        {v.X('TI'): (0, 1, 0.01), v.T: (800, 2200, 10), v.P: 101325, v.N: 1},
        plot_kwargs={'ax': axes[0, 0]})
axes[0, 0].set_title('(a) Fe–Ti', fontweight='bold')
axes[0, 0].set_xlabel('Mole fraction Ti')
axes[0, 0].set_ylabel('Temperature (K)')
axes[0, 0].set_xlim(0, 1)
axes[0, 0].annotate('Mare ISRU:\nilmenite → Fe + Ti',
                     xy=(0.5, 900), fontsize=8, ha='center', style='italic',
                     bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                               edgecolor='gray', alpha=0.9))

# (b) Al-Ti
print("Calculating Al-Ti...")
binplot(db, ['AL', 'TI', 'VA'],
        ['LIQUID', 'BCC_A2', 'HCP_A3', 'FCC_A1', 'AL11TI5', 'AL2TI', 'ALTI'],
        {v.X('TI'): (0, 1, 0.01), v.T: (400, 2000, 10), v.P: 101325, v.N: 1},
        plot_kwargs={'ax': axes[0, 1]})
axes[0, 1].set_title('(b) Al–Ti', fontweight='bold')
axes[0, 1].set_xlabel('Mole fraction Ti')
axes[0, 1].set_ylabel('Temperature (K)')
axes[0, 1].set_xlim(0, 1)
axes[0, 1].annotate('γ-TiAl: aerospace\nintermetallics',
                     xy=(0.55, 550), fontsize=8, ha='center', style='italic',
                     bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                               edgecolor='gray', alpha=0.9))

# (c) Al-Fe
print("Calculating Al-Fe...")
binplot(db, ['AL', 'FE', 'VA'],
        ['LIQUID', 'BCC_A2', 'FCC_A1', 'AL13FE4', 'AL5FE2', 'AL5FE4', 'AL2FE'],
        {v.X('FE'): (0, 1, 0.01), v.T: (400, 1900, 10), v.P: 101325, v.N: 1},
        plot_kwargs={'ax': axes[1, 0]})
axes[1, 0].set_title('(c) Al–Fe', fontweight='bold')
axes[1, 0].set_xlabel('Mole fraction Fe')
axes[1, 0].set_ylabel('Temperature (K)')
axes[1, 0].set_xlim(0, 1)
axes[1, 0].annotate('Highlands Al\n+ Mare Fe blend',
                     xy=(0.3, 550), fontsize=8, ha='center', style='italic',
                     bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                               edgecolor='gray', alpha=0.9))

# (d) Al-Ni
print("Calculating Al-Ni...")
binplot(nial_db, ['AL', 'NI', 'VA'],
        ['LIQUID', 'AL3NI1', 'AL3NI2', 'AL3NI5', 'BCC_B2', 'FCC_L12', 'FCC_A1'],
        {v.X('NI'): (0, 1, 0.01), v.T: (400, 2000, 10), v.P: 101325, v.N: 1},
        plot_kwargs={'ax': axes[1, 1]})
axes[1, 1].set_title('(d) Al–Ni', fontweight='bold')
axes[1, 1].set_xlabel('Mole fraction Ni')
axes[1, 1].set_ylabel('Temperature (K)')
axes[1, 1].set_xlim(0, 1)
axes[1, 1].annotate('Ni-superalloy:\nEarth Ni + Lunar Al',
                     xy=(0.75, 550), fontsize=8, ha='center', style='italic',
                     bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                               edgecolor='gray', alpha=0.9))

fig.suptitle('Binary Phase Diagrams for Lunar ISRU Alloy Systems',
             fontsize=14, fontweight='bold', y=0.98)

fig.tight_layout(rect=[0, 0, 1, 0.96])
fig.savefig(os.path.join(OUTDIR, 'phase_diagrams_combined.pdf'))
fig.savefig(os.path.join(OUTDIR, 'phase_diagrams_combined.png'))
print("✓ Saved phase_diagrams_combined.pdf/png")
plt.close(fig)
