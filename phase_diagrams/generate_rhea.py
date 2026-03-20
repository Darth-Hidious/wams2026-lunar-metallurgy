#!/usr/bin/env python3
"""
RHEA property diagrams for WAMS 2026 Paper #68.

Computes phase fraction vs temperature for key RHEA compositions:
  1. Equimolar HfNbTaTiZr (Senkov 2011 — literature baseline)
  2. Equimolar MoNbTaTiV (Cao 2019 — SPS-processed, paper Table 7)
  3. ISRU-blended concept: Fe₀.₃Ti₀.₃Al₀.₂Nb₀.₁Ta₀.₁
     (hypothetical ISRU-heavy + Earth-shipped refractories)

NOTE: COST507 binary extrapolations to 5-component space.
These are indicative, not TCHEA-grade. SPARK project data
should be preferred where available.

Data source: COST507 EU database (Round II, Jan 1999)
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pycalphad import Database, equilibrium
import pycalphad.variables as v
import numpy as np
import os
import warnings
warnings.filterwarnings('ignore')

OUTDIR = os.path.dirname(os.path.abspath(__file__))
db = Database(os.path.join(OUTDIR, 'COST507.tdb'))

plt.rcParams.update({
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'figure.dpi': 300,
    'savefig.dpi': 300,
})

# Solution phases relevant to RHEAs
solution_phases = ['LIQUID', 'BCC_A2', 'HCP_A3', 'FCC_A1']

# Temperature range
temps = np.arange(500, 2501, 25)  # 500K to 2500K in 25K steps

def compute_phase_fractions(db, comps, phases, conditions_base, temps):
    """Compute phase fractions vs temperature."""
    results = {phase: [] for phase in phases}
    results['T'] = []

    for T in temps:
        conds = dict(conditions_base)
        conds[v.T] = float(T)
        conds[v.P] = 101325
        conds[v.N] = 1

        try:
            eq = equilibrium(db, comps, phases, conds)
            phase_names = eq.Phase.values.flatten()
            phase_fracs = eq.NP.values.flatten()

            results['T'].append(T)
            for phase in phases:
                frac = 0.0
                for pn, pf in zip(phase_names, phase_fracs):
                    if pn == phase and not np.isnan(pf):
                        frac += pf
                results[phase].append(frac)
        except Exception:
            results['T'].append(T)
            for phase in phases:
                results[phase].append(np.nan)

    return results


# ============================================================
# 1. Equimolar HfNbTaTiZr
# ============================================================
print("[1/3] Computing HfNbTaTiZr phase stability...")
comps1 = ['HF', 'NB', 'TA', 'TI', 'ZR', 'VA']
conds1 = {v.X('NB'): 0.2, v.X('TA'): 0.2, v.X('TI'): 0.2, v.X('ZR'): 0.2}

res1 = compute_phase_fractions(db, comps1, solution_phases, conds1, temps)

# ============================================================
# 2. Equimolar MoNbTaTiV
# ============================================================
print("[2/3] Computing MoNbTaTiV phase stability...")
comps2 = ['MO', 'NB', 'TA', 'TI', 'V', 'VA']
conds2 = {v.X('NB'): 0.2, v.X('TA'): 0.2, v.X('TI'): 0.2, v.X('V'): 0.2}

res2 = compute_phase_fractions(db, comps2, solution_phases, conds2, temps)

# ============================================================
# 3. ISRU-blended concept
# ============================================================
print("[3/3] Computing ISRU-blend (Fe₀.₃Ti₀.₃Al₀.₂Nb₀.₁Ta₀.₁)...")
comps3 = ['AL', 'FE', 'NB', 'TA', 'TI', 'VA']
conds3 = {v.X('FE'): 0.3, v.X('TI'): 0.3, v.X('NB'): 0.1, v.X('TA'): 0.1}
# AL = 1 - 0.3 - 0.3 - 0.1 - 0.1 = 0.2

res3 = compute_phase_fractions(db, comps3, solution_phases, conds3, temps)

# ============================================================
# Plot
# ============================================================
print("Plotting...")

phase_colors = {
    'LIQUID': '#2196F3',    # blue
    'BCC_A2': '#FF5722',    # deep orange
    'HCP_A3': '#4CAF50',    # green
    'FCC_A1': '#9C27B0',    # purple
}

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

datasets = [
    (res1, 'Equimolar HfNbTaTiZr\n(Senkov 2011 baseline)', '(a)'),
    (res2, 'Equimolar MoNbTaTiV\n(Cao 2019 / SPS route)', '(b)'),
    (res3, 'Fe₀.₃Ti₀.₃Al₀.₂Nb₀.₁Ta₀.₁\n(ISRU-blend concept)', '(c)'),
]

for ax, (res, title, label) in zip(axes, datasets):
    T = np.array(res['T'])
    # Stack areas
    bottom = np.zeros_like(T, dtype=float)
    for phase in solution_phases:
        fracs = np.array(res[phase], dtype=float)
        fracs = np.nan_to_num(fracs, nan=0.0)
        if np.any(fracs > 0.001):
            ax.fill_between(T, bottom, bottom + fracs,
                           label=phase, color=phase_colors[phase], alpha=0.7)
            bottom = bottom + fracs

    ax.set_xlim(500, 2500)
    ax.set_ylim(0, 1.05)
    ax.set_xlabel('Temperature (K)')
    ax.set_ylabel('Phase fraction')
    ax.set_title(f'{label} {title}', fontsize=10, fontweight='bold')
    ax.legend(loc='center right', fontsize=8)
    ax.axhline(y=1.0, color='gray', linestyle='--', linewidth=0.5)

fig.suptitle('RHEA Phase Stability vs Temperature (COST507 extrapolation)',
             fontsize=13, fontweight='bold')
fig.tight_layout(rect=[0, 0, 1, 0.94])
fig.savefig(os.path.join(OUTDIR, 'rhea_phase_stability.pdf'))
fig.savefig(os.path.join(OUTDIR, 'rhea_phase_stability.png'))
print("✓ Saved rhea_phase_stability.pdf/png")
plt.close(fig)

# Also generate individual refractory binary subsystem diagrams
# These are the building blocks of the RHEA
print("\n[Bonus] Computing key refractory binary subsystems...")

fig2, axes2 = plt.subplots(2, 3, figsize=(15, 10))
from pycalphad import binplot

subsystems = [
    (['NB', 'TI', 'VA'], 'TI', 'Nb–Ti', '(a)'),
    (['MO', 'NB', 'VA'], 'NB', 'Mo–Nb', '(b)'),
    (['TA', 'TI', 'VA'], 'TI', 'Ta–Ti', '(c)'),
    (['HF', 'ZR', 'VA'], 'ZR', 'Hf–Zr', '(d)'),
    (['MO', 'TI', 'VA'], 'TI', 'Mo–Ti', '(e)'),
    (['NB', 'ZR', 'VA'], 'ZR', 'Nb–Zr', '(f)'),
]

for ax, (comps, x_elem, title, label) in zip(axes2.flat, subsystems):
    try:
        binplot(db, comps, solution_phases + ['BCC_B2', 'LAVES_C14', 'LAVES_C15', 'OMEGA', 'SIGMA'],
                {v.X(x_elem): (0, 1, 0.01), v.T: (500, 2800, 10), v.P: 101325, v.N: 1},
                plot_kwargs={'ax': ax})
        ax.set_title(f'{label} {title}', fontweight='bold', fontsize=11)
        ax.set_xlabel(f'Mole fraction {x_elem}')
        ax.set_ylabel('Temperature (K)')
        ax.set_xlim(0, 1)
    except Exception as e:
        ax.text(0.5, 0.5, f'Failed:\n{str(e)[:50]}', ha='center', va='center', transform=ax.transAxes)
        ax.set_title(f'{label} {title} (FAILED)', fontweight='bold')

fig2.suptitle('Refractory Binary Subsystems — Building Blocks of RHEAs (COST507)',
              fontsize=13, fontweight='bold')
fig2.tight_layout(rect=[0, 0, 1, 0.95])
fig2.savefig(os.path.join(OUTDIR, 'rhea_binary_subsystems.pdf'))
fig2.savefig(os.path.join(OUTDIR, 'rhea_binary_subsystems.png'))
print("✓ Saved rhea_binary_subsystems.pdf/png")
plt.close(fig2)

print("\n=== Done ===")
for f in sorted(os.listdir(OUTDIR)):
    if f.endswith('.pdf') and 'rhea' in f:
        size_kb = os.path.getsize(os.path.join(OUTDIR, f)) / 1024
        print(f"  {f} ({size_kb:.0f} KB)")
