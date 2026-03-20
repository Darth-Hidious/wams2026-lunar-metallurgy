#!/usr/bin/env python3
"""
Generate dual-purpose mass break-even comparison (2×2):
  Top row:    Original model (C_op < C_L - C_cap/(N·M_ISRU))
  Bottom row: Dual-Purpose Mass (C_op < C_L·IMLR/(IMLR-1) - C_cap/(N·M_ISRU))
  Left col:   IMLR = 2
  Right col:  IMLR = 5
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm
from pathlib import Path

plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif', 'serif'],
    'mathtext.fontset': 'dejavuserif',
    'font.size': 9, 'axes.labelsize': 9, 'axes.titlesize': 10,
    'xtick.labelsize': 8, 'ytick.labelsize': 8,
    'figure.dpi': 150, 'savefig.dpi': 300,
    'axes.linewidth': 0.6, 'grid.linewidth': 0.3,
})

OUTDIR = Path('/Users/siddharthakovid/Downloads/outputs/figures')
OUTDIR.mkdir(exist_ok=True)

M_comp = 10.0
C_cap_k = 500e3  # k$ (= $500M)
levels = [-500, -200, 0, 50, 100, 200, 500, 1000, 2000, 3000]

CL = np.logspace(np.log10(8), np.log10(2000), 300)
N  = np.logspace(0, 4, 300)
CLg, Ng = np.meshgrid(CL, N)

def M_isru(IMLR):
    return M_comp * (1 - 1.0/IMLR)

def cop_original(CL, N, IMLR):
    m = M_isru(IMLR)
    return CL - C_cap_k / (N * m + 1e-10)

def cop_dual(CL, N, IMLR):
    m = M_isru(IMLR)
    return CL * (IMLR / (IMLR - 1)) - C_cap_k / (N * m + 1e-10)

cmap = plt.cm.RdYlGn
norm = BoundaryNorm(levels, ncolors=cmap.N, clip=True)

scenarios = [('CLPS', 1000), ('FH+lander', 200), ('Starship', 50), ('Target', 10)]

panels = [
    (0, 0, r'Dead-weight cargo — IMLR = 2  (50 % ISRU)',  cop_original(CLg, Ng, 2)),
    (0, 1, r'Dead-weight cargo — IMLR = 5  (80 % ISRU)',  cop_original(CLg, Ng, 5)),
    (1, 0, r'Dual-purpose mass — IMLR = 2  (50 % ISRU)',  cop_dual(CLg, Ng, 2)),
    (1, 1, r'Dual-purpose mass — IMLR = 5  (80 % ISRU)',  cop_dual(CLg, Ng, 5)),
]

fig, axes = plt.subplots(2, 2, figsize=(7.5, 6.0))

for r, c, title, Z in panels:
    ax = axes[r, c]
    Zk = np.clip(Z, -600, 3500)
    cs = ax.contourf(CLg, Ng, Zk, levels=levels, cmap=cmap, norm=norm, extend='both')
    ax.contour(CLg, Ng, Z, levels=[0], colors='black', linewidths=1.5, linestyles='--')

    for name, cost in scenarios:
        ax.axvline(cost, color='0.4', ls=':', lw=0.7, alpha=0.7)
        ax.text(cost * 0.85, 1.3, name, rotation=90, fontsize=6, ha='right',
                va='bottom', color='0.3', alpha=0.85)

    ax.set_xscale('log'); ax.set_yscale('log')
    ax.set_xlim(8, 1500); ax.set_ylim(1, 10000)
    ax.set_title(title, fontsize=8.5, pad=4)
    ax.grid(True, alpha=0.15, which='both')
    ax.set_axisbelow(True)

    if r == 1:
        ax.set_xlabel(r'Launch cost $C_L$ (k\$/kg)')
    if c == 0:
        ax.set_ylabel(r'Production volume $N$')

fig.subplots_adjust(left=0.09, right=0.86, bottom=0.08, top=0.93, wspace=0.25, hspace=0.32)
cax = fig.add_axes([0.88, 0.08, 0.02, 0.85])
cbar = fig.colorbar(cs, cax=cax, ticks=levels)
cbar.set_label(r'Max viable $C_{\mathrm{op}}$  (k\$/kg)', fontsize=8)
cbar.ax.tick_params(labelsize=7)

fig.suptitle(
    'Break-even comparison: dead-weight cargo vs. dual-purpose mass',
    fontsize=10, y=0.98)

for ext in ('pdf', 'png'):
    fig.savefig(OUTDIR / f'dual_purpose_breakeven.{ext}')
print(f"  -> {OUTDIR}/dual_purpose_breakeven.pdf")
plt.close(fig)

# ── Also compute key thresholds for the text ──
print("\n=== Key thresholds ===")
for IMLR in [2, 5]:
    m = M_isru(IMLR)
    mult = IMLR / (IMLR - 1)
    print(f"\nIMLR = {IMLR} (mult = {mult:.2f}, M_ISRU = {m:.1f} kg):")
    for scenario, cl in [('CLPS 1M/kg', 1000), ('Starship 50k/kg', 50)]:
        # Original
        N_break_orig = C_cap_k / (cl * m)
        # Dual-purpose
        N_break_dual = C_cap_k / (cl * mult * m)
        print(f"  {scenario}:")
        print(f"    Original:     break-even at N > {N_break_orig:.0f}")
        print(f"    Dual-purpose: break-even at N > {N_break_dual:.0f}")
        # At N=1000
        cop_o = cop_original(cl, 1000, IMLR)
        cop_d = cop_dual(cl, 1000, IMLR)
        print(f"    At N=1000: orig C_op_max = {cop_o:.0f} k$/kg, dual = {cop_d:.0f} k$/kg")
