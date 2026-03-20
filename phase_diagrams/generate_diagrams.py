#!/usr/bin/env python3
"""
Generate phase diagrams relevant to WAMS 2026 Paper #68:
Lunar ISRU alloy systems and RHEA compositions.

Uses pycalphad with COST507 thermochemical database for light metal alloys.
Systems chosen to match paper's terrane→alloy mapping:
  - Fe-Ti   (Mare basalt: ilmenite reduction products)
  - Al-Fe   (Highlands+Mare blend: FFC-Cambridge + H₂ reduction)
  - Al-Ni   (Ni-superalloy route: Earth Ni + lunar Al)
  - Al-Si   (Highlands: anorthite/plagioclase extraction)

References:
  COST507 database: EU COST Action 507, Round II (Jan 1999)
  pycalphad: Otis & Liu, J. Open Res. Softw. 5(1), 2017
"""

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for PDF/PNG output
import matplotlib.pyplot as plt
from pycalphad import Database, binplot
import pycalphad.variables as v
import os
import warnings
warnings.filterwarnings('ignore')

# Output directory
OUTDIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(OUTDIR, 'COST507.tdb')

# Load the COST507 database
print("Loading COST507 database...")
db = Database(DB_PATH)
print(f"  Elements: {sorted(db.elements - {'/-', 'VA'})}")
print(f"  Phases: {sorted(db.phases.keys())}")

# ============================================================
# 1. Fe-Ti Binary Phase Diagram
#    Relevance: Mare basalt ISRU — ilmenite (FeTiO₃) reduction
#    yields Fe + Ti metal. This diagram shows what phases form
#    in the Fe-Ti system at different compositions and temperatures.
# ============================================================
print("\n[1/4] Calculating Fe-Ti phase diagram...")

# Select phases that exist in the Fe-Ti binary
# From COST507: check which phases include both Fe and Ti
feti_phases = ['LIQUID', 'BCC_A2', 'HCP_A3', 'FCC_A1', 'LAVES_C14', 'FETI_EPSILON']

# Filter to phases that actually exist in database
feti_phases_available = [p for p in feti_phases if p in db.phases]
# Also check for any Fe-Ti specific phases
for phase_name in sorted(db.phases.keys()):
    if 'FE' in phase_name.upper() and 'TI' in phase_name.upper():
        if phase_name not in feti_phases_available:
            feti_phases_available.append(phase_name)
    if 'LAVES' in phase_name.upper():
        if phase_name not in feti_phases_available:
            feti_phases_available.append(phase_name)

# Fallback: use all phases but filter to Fe-Ti relevant ones
if len(feti_phases_available) < 3:
    # Use all phases and let pycalphad figure it out
    feti_phases_available = list(db.phases.keys())

print(f"  Using phases: {feti_phases_available[:15]}...")

fig1, ax1 = plt.subplots(figsize=(8, 6))
try:
    binplot(db, ['FE', 'TI', 'VA'], feti_phases_available,
            {v.X('TI'): (0, 1, 0.01), v.T: (800, 2200, 10), v.P: 101325, v.N: 1},
            plot_kwargs={'ax': ax1})
    ax1.set_title('Fe–Ti Binary Phase Diagram (COST507)', fontsize=14)
    ax1.set_xlabel('Mole fraction Ti', fontsize=12)
    ax1.set_ylabel('Temperature (K)', fontsize=12)
    ax1.set_xlim(0, 1)
    # Add annotation about ISRU relevance
    ax1.annotate('Ilmenite reduction\n(FeTiO₃ → Fe + Ti)',
                 xy=(0.5, 1100), fontsize=9, ha='center',
                 bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.8))
    fig1.tight_layout()
    fig1.savefig(os.path.join(OUTDIR, 'phase_Fe_Ti.pdf'), dpi=300)
    fig1.savefig(os.path.join(OUTDIR, 'phase_Fe_Ti.png'), dpi=300)
    print("  ✓ Saved phase_Fe_Ti.pdf/png")
except Exception as e:
    print(f"  ✗ Fe-Ti failed: {e}")
plt.close(fig1)

# ============================================================
# 2. Al-Fe Binary Phase Diagram
#    Relevance: Highlands Al + Mare Fe — blending ISRU metals
#    from different terranes creates Al-Fe alloys.
# ============================================================
print("\n[2/4] Calculating Al-Fe phase diagram...")

alfe_phases = ['LIQUID', 'BCC_A2', 'FCC_A1', 'HCP_A3', 'AL13FE4', 'AL5FE2', 'AL5FE4', 'AL2FE']
alfe_phases_available = [p for p in alfe_phases if p in db.phases]
# Add any other Al-Fe intermetallics from DB
for phase_name in sorted(db.phases.keys()):
    if ('AL' in phase_name.upper() and 'FE' in phase_name.upper()):
        if phase_name not in alfe_phases_available:
            alfe_phases_available.append(phase_name)
if len(alfe_phases_available) < 3:
    alfe_phases_available = list(db.phases.keys())

print(f"  Using phases: {alfe_phases_available}")

fig2, ax2 = plt.subplots(figsize=(8, 6))
try:
    binplot(db, ['AL', 'FE', 'VA'], alfe_phases_available,
            {v.X('FE'): (0, 1, 0.01), v.T: (400, 2000, 10), v.P: 101325, v.N: 1},
            plot_kwargs={'ax': ax2})
    ax2.set_title('Al–Fe Binary Phase Diagram (COST507)', fontsize=14)
    ax2.set_xlabel('Mole fraction Fe', fontsize=12)
    ax2.set_ylabel('Temperature (K)', fontsize=12)
    ax2.set_xlim(0, 1)
    ax2.annotate('Highlands Al\n+ Mare Fe',
                 xy=(0.3, 800), fontsize=9, ha='center',
                 bbox=dict(boxstyle='round,pad=0.3', facecolor='lightcyan', alpha=0.8))
    fig2.tight_layout()
    fig2.savefig(os.path.join(OUTDIR, 'phase_Al_Fe.pdf'), dpi=300)
    fig2.savefig(os.path.join(OUTDIR, 'phase_Al_Fe.png'), dpi=300)
    print("  ✓ Saved phase_Al_Fe.pdf/png")
except Exception as e:
    print(f"  ✗ Al-Fe failed: {e}")
plt.close(fig2)

# ============================================================
# 3. Al-Ni Binary Phase Diagram
#    Relevance: Ni-superalloy pathway — Earth-supplied Ni +
#    lunar Al for high-temperature structural alloys.
# ============================================================
print("\n[3/4] Calculating Al-Ni phase diagram...")

# Use the dedicated Ni-Al TDB for better accuracy
nial_db_path = os.path.join(OUTDIR, 'nial_dupin.tdb')
if os.path.exists(nial_db_path):
    nial_db = Database(nial_db_path)
    nial_phases = list(nial_db.phases.keys())
    nial_comps = ['AL', 'NI', 'VA']
    print(f"  Using dedicated Ni-Al database (Dupin 2001)")
    print(f"  Phases: {nial_phases}")
else:
    nial_db = db
    nial_phases = ['LIQUID', 'FCC_A1', 'BCC_A2', 'FCC_L12', 'BCC_B2']
    nial_phases = [p for p in nial_phases if p in db.phases]
    nial_comps = ['AL', 'NI', 'VA']

fig3, ax3 = plt.subplots(figsize=(8, 6))
try:
    binplot(nial_db, nial_comps, nial_phases,
            {v.X('NI'): (0, 1, 0.01), v.T: (400, 2000, 10), v.P: 101325, v.N: 1},
            plot_kwargs={'ax': ax3})
    ax3.set_title('Al–Ni Binary Phase Diagram (Dupin et al. 2001)', fontsize=14)
    ax3.set_xlabel('Mole fraction Ni', fontsize=12)
    ax3.set_ylabel('Temperature (K)', fontsize=12)
    ax3.set_xlim(0, 1)
    ax3.annotate('Ni-superalloy region\n(Earth Ni + Lunar Al)',
                 xy=(0.75, 900), fontsize=9, ha='center',
                 bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.8))
    fig3.tight_layout()
    fig3.savefig(os.path.join(OUTDIR, 'phase_Al_Ni.pdf'), dpi=300)
    fig3.savefig(os.path.join(OUTDIR, 'phase_Al_Ni.png'), dpi=300)
    print("  ✓ Saved phase_Al_Ni.pdf/png")
except Exception as e:
    print(f"  ✗ Al-Ni failed: {e}")
plt.close(fig3)

# ============================================================
# 4. Al-Ti Binary Phase Diagram
#    Relevance: TiAl intermetallics — key lightweight high-temp
#    alloys accessible from ISRU Al + Ti feedstock.
#    Used in aerospace (gamma-TiAl turbine blades).
# ============================================================
print("\n[4/4] Calculating Al-Ti phase diagram...")

alti_phases = ['LIQUID', 'BCC_A2', 'HCP_A3', 'FCC_A1']
alti_phases_available = [p for p in alti_phases if p in db.phases]
# Add Ti-Al intermetallics
for phase_name in sorted(db.phases.keys()):
    if ('AL' in phase_name.upper() and 'TI' in phase_name.upper()):
        if phase_name not in alti_phases_available:
            alti_phases_available.append(phase_name)
    # Also check for known TiAl phases
    if phase_name in ['ALTI', 'ALTI3', 'AL3TI', 'AL2TI', 'ALTI_L10', 'TI3AL']:
        if phase_name not in alti_phases_available:
            alti_phases_available.append(phase_name)

if len(alti_phases_available) < 3:
    alti_phases_available = list(db.phases.keys())

print(f"  Using phases: {alti_phases_available}")

fig4, ax4 = plt.subplots(figsize=(8, 6))
try:
    binplot(db, ['AL', 'TI', 'VA'], alti_phases_available,
            {v.X('TI'): (0, 1, 0.01), v.T: (400, 2200, 10), v.P: 101325, v.N: 1},
            plot_kwargs={'ax': ax4})
    ax4.set_title('Al–Ti Binary Phase Diagram (COST507)', fontsize=14)
    ax4.set_xlabel('Mole fraction Ti', fontsize=12)
    ax4.set_ylabel('Temperature (K)', fontsize=12)
    ax4.set_xlim(0, 1)
    ax4.annotate('γ-TiAl region\n(aerospace intermetallics)',
                 xy=(0.5, 1000), fontsize=9, ha='center',
                 bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgreen', alpha=0.8))
    fig4.tight_layout()
    fig4.savefig(os.path.join(OUTDIR, 'phase_Al_Ti.pdf'), dpi=300)
    fig4.savefig(os.path.join(OUTDIR, 'phase_Al_Ti.png'), dpi=300)
    print("  ✓ Saved phase_Al_Ti.pdf/png")
except Exception as e:
    print(f"  ✗ Al-Ti failed: {e}")
plt.close(fig4)

print("\n=== Done ===")
print(f"Output directory: {OUTDIR}")
for f in sorted(os.listdir(OUTDIR)):
    if f.endswith(('.pdf', '.png')):
        fpath = os.path.join(OUTDIR, f)
        size_kb = os.path.getsize(fpath) / 1024
        print(f"  {f} ({size_kb:.0f} KB)")
