#!/usr/bin/env python3
"""
Pseudo-binary dilution diagram. Textbook style.
No fills except target band. Large figure, generous spacing.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from pathlib import Path

plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif', 'serif'],
    'mathtext.fontset': 'dejavuserif',
    'font.size': 10,
    'axes.labelsize': 11,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'axes.linewidth': 0.8,
    'savefig.dpi': 300,
    'figure.dpi': 150,
})

OUTDIR = Path('/Users/siddharthakovid/Downloads/outputs/figures')
x = np.linspace(0, 100, 1000)

# ── Phase boundaries ─────────────────────────────────────────────────
T_liq = gaussian_filter1d(
    3200 - 1200*(x/100)**0.55 - 250*np.exp(-((x-60)**2)/(2*22**2)), 15)
T_sol = gaussian_filter1d(
    2950 - 1200*(x/100)**0.45 - 400*np.exp(-((x-55)**2)/(2*20**2)), 15)
T_bcc = gaussian_filter1d(
    np.where(x < 15, 2700,
    np.where(x < 75, 2700 - 15*(x-15),
             1800 - 10*(x-75))).astype(float), 25)
T_bcc = np.clip(T_bcc, 500, T_sol - 50)
T_lav = gaussian_filter1d(
    np.where((x > 20) & (x < 88),
             1200 + 400*np.exp(-((x-50)**2)/(2*25**2)), 0.0), 20)

# ── Figure — generous size ────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7.5, 5.5))
ax.set_facecolor('white')

# Target band — only coloured element
ax.axvspan(75, 90, color='#E8F5E9', zorder=0)

# Phase boundary lines
ax.plot(x, T_liq, 'k-',  lw=2.0, zorder=3)
ax.plot(x, T_sol, 'k--', lw=1.5, zorder=3)
ax.plot(x[x < 85], T_bcc[x < 85], '-', color='#1565C0', lw=1.5, zorder=3)
lmask = (x > 24) & (x < 86) & (T_lav > 600)
ax.plot(x[lmask], T_lav[lmask], ':', color='#C62828', lw=1.3, zorder=3)

# ── Phase field labels — placed far from any line ─────────────────────

ax.text(50, 3250, 'LIQUID', fontsize=13, ha='center',
        color='#424242', fontweight='bold', fontstyle='italic')

ax.text(65, 2500, 'L + BCC', fontsize=10, ha='center',
        color='#757575', fontstyle='italic')

ax.text(12, 2100, 'BCC', fontsize=15, ha='center',
        color='#2E7D32', fontweight='bold')

ax.text(50, 750, 'BCC + LAVES', fontsize=11, ha='center',
        color='#C62828', fontweight='bold')
ax.text(50, 580, r'(Fe$_2$Nb, Fe$_2$Ta)', fontsize=9, ha='center',
        color='#C62828', fontstyle='italic')

# ── Endpoint labels — tucked into corners ─────────────────────────────

ax.text(1, 3550, 'RHEA master alloy', fontsize=8.5, ha='left',
        color='#1A237E', fontweight='bold')

ax.text(99, 2050, r'Fe$_{0.6}$Ti$_{0.4}$', fontsize=8.5, ha='right',
        color='#BF360C', fontweight='bold')

# ── Target window label — below the diagram, no overlap possible ──────

ax.text(82.5, 450, 'Target\nwindow', fontsize=9, ha='center', va='bottom',
        color='#2E7D32', fontweight='bold')

# ── Embrittlement annotation — in the Laves field, no arrow needed ────

ax.annotate('embrittlement cliff', xy=(38, 1550),
            xytext=(25, 1300), fontsize=8, ha='center', color='#C62828',
            fontstyle='italic',
            arrowprops=dict(arrowstyle='->', color='#C62828', lw=0.8))

# ── Legend — top-left in the liquid field, lots of room ───────────────

from matplotlib.lines import Line2D
ax.legend(handles=[
    Line2D([0],[0], color='k', lw=2.0, label='Liquidus'),
    Line2D([0],[0], color='k', lw=1.5, ls='--', label='Solidus'),
    Line2D([0],[0], color='#1565C0', lw=1.5, label='BCC solvus'),
    Line2D([0],[0], color='#C62828', lw=1.3, ls=':', label='Laves solvus'),
], loc='upper left', fontsize=8.5, framealpha=1.0, edgecolor='0.7',
   fancybox=False, handlelength=2.2, borderpad=0.6,
   bbox_to_anchor=(0.02, 0.98))

# ── Axes ──────────────────────────────────────────────────────────────

ax.set_xlabel('ISRU metal fraction (wt%)')
ax.set_ylabel('Temperature (K)')
ax.set_xlim(0, 100)
ax.set_ylim(400, 3600)
ax.set_xticks(range(0, 101, 10))

fig.tight_layout(pad=1.2)
for ext in ('pdf', 'png'):
    fig.savefig(OUTDIR / f'dilution_phase_diagram.{ext}')
print(f"Done → {OUTDIR}/dilution_phase_diagram.pdf")
plt.close()
