#!/usr/bin/env python3
"""
Regenerate publication-quality figures for WAMS 2026 Monte Carlo analysis.
Uses the same computational core as the original script but with fixed visualizations.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.patches import FancyBboxPatch
from scipy import stats
from pathlib import Path
import warnings, sys

warnings.filterwarnings('ignore')

# ── Publication styling ──────────────────────────────────────────────────────
plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif', 'Palatino', 'serif'],
    'mathtext.fontset': 'dejavuserif',
    'font.size': 9,
    'axes.labelsize': 10,
    'axes.titlesize': 10,
    'axes.titleweight': 'bold',
    'xtick.labelsize': 8,
    'ytick.labelsize': 8,
    'legend.fontsize': 8,
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.1,
    'axes.linewidth': 0.6,
    'xtick.major.width': 0.5,
    'ytick.major.width': 0.5,
    'grid.linewidth': 0.3,
    'lines.linewidth': 0.8,
})

OUTDIR = Path('/Users/siddharthakovid/Downloads/outputs/figures')
OUTDIR.mkdir(exist_ok=True)
TBLDIR = Path('/Users/siddharthakovid/Downloads/outputs/tables')
TBLDIR.mkdir(exist_ok=True)

# Terrane colour palette (consistent with existing paper maps)
TC = {
    'Highlands': '#3B7DD8',   # blue
    'Mare':      '#D64545',   # red
    'KREEP':     '#E8A630',   # amber
}

# ═══════════════════════════════════════════════════════════════════════════════
# DATA GENERATION (identical to original)
# ═══════════════════════════════════════════════════════════════════════════════

def generate_synthetic_lpgrs_data(n_pixels=11306, seed=42):
    np.random.seed(seed)
    n_highlands, n_mare, n_kreep = 8472, 1222, 1612
    data_list = []

    for _ in range(n_highlands):
        data_list.append({
            'FeO': np.clip(np.random.normal(4.5, 1.5), 0, 8),
            'TiO2': np.clip(np.random.exponential(0.2), 0, 0.5),
            'Al2O3': np.clip(np.random.normal(28, 3), 20, 36),
            'CaO': np.clip(np.random.normal(16, 2), 12, 20),
            'MgO': np.clip(np.random.normal(5, 2), 1, 12),
            'SiO2': np.clip(np.random.normal(45, 2), 40, 50),
            'K': np.clip(np.random.exponential(300), 50, 1500),
            'Th': np.clip(np.random.exponential(0.8), 0.1, 3.5),
            'lat': np.random.uniform(-90, 90),
            'lon': np.random.uniform(-180, 180),
            'terrane': 'Highlands',
        })
    for _ in range(n_mare):
        Th = np.clip(np.random.normal(2.0, 1.0), 0.3, 3.5)
        data_list.append({
            'FeO': np.clip(np.random.normal(16, 3), 8, 22),
            'TiO2': np.clip(np.random.normal(4, 3), 0.5, 12),
            'Al2O3': np.clip(np.random.normal(12, 3), 6, 18),
            'CaO': np.clip(np.random.normal(11, 2), 7, 15),
            'MgO': np.clip(np.random.normal(9, 3), 3, 18),
            'SiO2': np.clip(np.random.normal(43, 3), 36, 50),
            'K': np.clip(np.random.normal(800, 400), 100, 2500),
            'Th': Th, 'lat': np.random.uniform(-40, 40),
            'lon': np.random.uniform(-100, 50), 'terrane': 'Mare',
        })
    for _ in range(n_kreep):
        Th = np.clip(np.random.normal(6, 2), 3.5, 12)
        data_list.append({
            'FeO': np.clip(np.random.normal(12, 4), 5, 20),
            'TiO2': np.clip(np.random.normal(2.5, 2), 0.3, 10),
            'Al2O3': np.clip(np.random.normal(14, 4), 8, 22),
            'CaO': np.clip(np.random.normal(11, 2), 7, 16),
            'MgO': np.clip(np.random.normal(8, 3), 2, 16),
            'SiO2': np.clip(np.random.normal(46, 3), 38, 54),
            'K': np.clip(np.random.normal(3000, 1500), 500, 8000),
            'Th': Th, 'lat': np.random.uniform(-30, 50),
            'lon': np.random.uniform(-70, 30), 'terrane': 'KREEP',
        })

    for d in data_list:
        d['U'] = 0.27 * d['Th']

    return pd.DataFrame(data_list).sample(frac=1, random_state=seed).reset_index(drop=True)


def minmax_norm(series):
    return (series - series.min()) / (series.max() - series.min() + 1e-10)


def compute_indices(df, weights=None):
    df = df.copy()
    if weights is None:
        weights = {
            'w_FeO': 0.50, 'w_TiO2': 0.40,
            'w_imp_K': 0.06, 'w_imp_Th': 0.04,
            'w_Al2O3': 0.55, 'w_CaO': 0.35, 'w_het': 0.10,
            'w_K_kreep': 0.40, 'w_Th_kreep': 0.40,
            'w_U_kreep': 0.10, 'w_unc': 0.10,
        }

    for col in ['FeO','TiO2','Al2O3','CaO','SiO2','K','Th','U']:
        df[col+'_n'] = minmax_norm(df[col])
    df['lat_n'] = minmax_norm(np.abs(df['lat']))

    tmean = df.groupby('terrane')['SiO2'].transform('mean')
    df['SiO2_dev_n'] = minmax_norm(np.abs(df['SiO2'] - tmean))

    P_imp = minmax_norm(0.6 * df['K_n'] + 0.4 * df['Th_n'])
    df['I_FeTi'] = (weights['w_FeO']*df['FeO_n'] +
                    weights['w_TiO2']*df['TiO2_n'] - 0.10*P_imp).clip(0,1)

    df['I_AlCa'] = (weights['w_Al2O3']*df['Al2O3_n'] +
                    weights['w_CaO']*df['CaO_n'] -
                    weights['w_het']*df['SiO2_dev_n']).clip(0,1)

    df['I_KREEP'] = (weights['w_K_kreep']*df['K_n'] +
                     weights['w_Th_kreep']*df['Th_n'] +
                     weights['w_U_kreep']*df['U_n'] -
                     weights['w_unc']*df['lat_n']).clip(0,1)
    return df


def perturb_weights(nom, sigma=0.2, truncate=0.5):
    p = {}
    for k, v in nom.items():
        eps = np.clip(np.random.normal(0, sigma), -truncate, truncate)
        p[k] = v * (1 + eps)
    # renormalise positive terms within each index
    for group, target in [
        (['w_FeO','w_TiO2'], 0.90),
        (['w_Al2O3','w_CaO'], 0.90),
        (['w_K_kreep','w_Th_kreep','w_U_kreep'], 0.90),
    ]:
        s = sum(p[g] for g in group)
        for g in group:
            p[g] *= target / s
    return p


# ═══════════════════════════════════════════════════════════════════════════════
# MONTE CARLO ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

def run_monte_carlo(df, n_iter=10000, sigma=0.2, seed=42):
    np.random.seed(seed)
    nom = {
        'w_FeO': 0.50, 'w_TiO2': 0.40,
        'w_imp_K': 0.06, 'w_imp_Th': 0.04,
        'w_Al2O3': 0.55, 'w_CaO': 0.35, 'w_het': 0.10,
        'w_K_kreep': 0.40, 'w_Th_kreep': 0.40,
        'w_U_kreep': 0.10, 'w_unc': 0.10,
    }

    dist = {idx: {t: [] for t in ['Highlands','Mare','KREEP']}
            for idx in ['I_FeTi','I_AlCa','I_KREEP']}
    leaders = {idx: [] for idx in ['I_FeTi','I_AlCa','I_KREEP']}

    for i in range(n_iter):
        if i % 2000 == 0:
            print(f"  iteration {i}/{n_iter}...")
        pw = perturb_weights(nom, sigma=sigma)
        di = compute_indices(df, pw)
        tm = di.groupby('terrane')[['I_FeTi','I_AlCa','I_KREEP']].mean()
        for idx in ['I_FeTi','I_AlCa','I_KREEP']:
            for t in ['Highlands','Mare','KREEP']:
                dist[idx][t].append(tm.loc[t, idx])
            leaders[idx].append(tm[idx].idxmax())

    # statistics
    st = {}
    for idx in ['I_FeTi','I_AlCa','I_KREEP']:
        st[idx] = {}
        for t in ['Highlands','Mare','KREEP']:
            v = np.array(dist[idx][t])
            st[idx][t] = {
                'p5': np.percentile(v, 5), 'p50': np.percentile(v, 50),
                'p95': np.percentile(v, 95), 'mean': np.mean(v), 'std': np.std(v),
            }

    rstab = {}
    for idx in ['I_FeTi','I_AlCa','I_KREEP']:
        counts = pd.Series(leaders[idx]).value_counts(normalize=True)
        rstab[idx] = counts.to_dict()

    return {'distributions': dist, 'statistics': st,
            'ranking_stability': rstab, 'n_iterations': n_iter}


# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 1: MONTE CARLO VIOLIN PLOTS
# ═══════════════════════════════════════════════════════════════════════════════

def fig_violins(mc):
    fig, axes = plt.subplots(1, 3, figsize=(7.0, 3.0))  # single-column width ≈ 3.5"

    indices = ['I_FeTi', 'I_AlCa', 'I_KREEP']
    titles = [
        r'$I_{\mathrm{FeTi}}$  (mare potential)',
        r'$I_{\mathrm{AlCa}}$  (highlands potential)',
        r'$I_{\mathrm{KREEP}}$  (trace-element potential)',
    ]
    terranes = ['Highlands', 'Mare', 'KREEP']

    for ax, idx, title in zip(axes, indices, titles):
        data = [mc['distributions'][idx][t] for t in terranes]

        parts = ax.violinplot(data, positions=[0,1,2],
                              showmeans=False, showmedians=False, showextrema=False,
                              widths=0.75)

        for i, (body, t) in enumerate(zip(parts['bodies'], terranes)):
            body.set_facecolor(TC[t])
            body.set_edgecolor('none')
            body.set_alpha(0.55)

        # box-plot internals: IQR box + median + whiskers at p5/p95
        for i, t in enumerate(terranes):
            vals = np.array(mc['distributions'][idx][t])
            q1, med, q3 = np.percentile(vals, [25, 50, 75])
            p5, p95 = np.percentile(vals, [5, 95])

            # IQR box
            ax.add_patch(FancyBboxPatch(
                (i - 0.12, q1), 0.24, q3 - q1,
                boxstyle="round,pad=0.01", linewidth=0.6,
                edgecolor='black', facecolor=TC[t], alpha=0.85, zorder=3))
            # median line
            ax.hlines(med, i - 0.14, i + 0.14, color='white', linewidth=1.5, zorder=4)
            # whiskers
            ax.vlines(i, p5, q1, color='black', linewidth=0.6, zorder=2)
            ax.vlines(i, q3, p95, color='black', linewidth=0.6, zorder=2)
            ax.hlines(p5, i - 0.06, i + 0.06, color='black', linewidth=0.6, zorder=2)
            ax.hlines(p95, i - 0.06, i + 0.06, color='black', linewidth=0.6, zorder=2)

        ax.set_xticks([0, 1, 2])
        ax.set_xticklabels(['Highl.', 'Mare', 'KREEP'], fontsize=7.5)
        ax.set_title(title, fontsize=8.5, pad=4)
        ax.set_ylim(-0.02, max(0.65, max(np.percentile(mc['distributions'][idx][t], 99)
                                          for t in terranes) * 1.15))
        ax.set_ylabel('Index value' if ax == axes[0] else '')
        ax.grid(True, alpha=0.25, axis='y')
        ax.set_axisbelow(True)

    fig.suptitle(
        f'Monte Carlo sensitivity  (n = {mc["n_iterations"]:,},  '
        r'$\sigma_w$ = 20 %,  truncated at $\pm$50 %)',
        fontsize=9, y=1.01)
    fig.tight_layout(w_pad=1.2)

    for ext in ('pdf', 'png'):
        fig.savefig(OUTDIR / f'monte_carlo_indices.{ext}')
    print(f"  -> {OUTDIR}/monte_carlo_indices.pdf")
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 2: BREAK-EVEN CONTOURS
# ═══════════════════════════════════════════════════════════════════════════════

def breakeven_Cop(C_L, C_cap, N, IMLR, M=10.0):
    M_isru = M * (1 - 1.0/IMLR)
    return C_L - C_cap / (N * M_isru + 1e-10)


def fig_breakeven():
    C_L = np.logspace(np.log10(8e3), np.log10(2e6), 200)   # 8k – 2M $/kg
    N   = np.logspace(0, 4, 200)                             # 1 – 10 000 components
    CLg, Ng = np.meshgrid(C_L, N)
    C_cap = 500e6  # $500 M

    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.3), sharey=True)

    for ax, IMLR, label in zip(axes, [2, 5],
                                ['IMLR = 2  (50 % ISRU)', 'IMLR = 5  (80 % ISRU)']):
        Z = breakeven_Cop(CLg, C_cap, Ng, IMLR) / 1e3   # k$/kg

        # Clip for sensible color range
        Zplot = np.clip(Z, -500, 3000)

        # Filled contours
        levels = [-500, -200, 0, 50, 100, 200, 500, 1000, 2000, 3000]
        cs = ax.contourf(CLg/1e3, Ng, Zplot, levels=levels,
                         cmap='RdYlGn', extend='both')
        # Zero contour (break-even boundary) — thick black dashed
        ax.contour(CLg/1e3, Ng, Z, levels=[0],
                   colors='black', linewidths=1.5, linestyles='--')

        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_xlabel(r'Launch cost  $C_L$  (k\$/kg)')
        if ax == axes[0]:
            ax.set_ylabel(r'Production volume  $N$  (components)')
        ax.set_title(label, fontsize=9)

        # Scenario reference lines
        scenarios = [
            ('CLPS',     1000, '#555'),
            ('FH+lander', 200, '#555'),
            ('Starship',   50, '#555'),
            ('Target',     10, '#555'),
        ]
        for name, cost, col in scenarios:
            ax.axvline(cost, color=col, ls=':', lw=0.7, alpha=0.7)
            ax.text(cost * 0.88, 1.3, name, rotation=90, fontsize=6.5,
                    ha='right', va='bottom', color=col, alpha=0.8)

        ax.set_xlim(8, 1500)
        ax.set_ylim(1, 10000)
        ax.grid(True, alpha=0.2, which='both')
        ax.set_axisbelow(True)

    fig.subplots_adjust(left=0.10, right=0.86, wspace=0.25, top=0.82, bottom=0.15)
    cax = fig.add_axes([0.88, 0.15, 0.02, 0.67])
    cbar = fig.colorbar(cs, cax=cax)
    cbar.set_label(r'Max viable $C_{\mathrm{op}}$  (k\$/kg)', fontsize=8)
    cbar.ax.tick_params(labelsize=7)

    fig.suptitle(
        r'Break-even operating cost for ISRU manufacturing'
        '\n'
        r'($C_{\mathrm{cap}}$ = \$500 M,  $M_{\mathrm{comp}}$ = 10 kg)',
        fontsize=9, y=0.97)

    for ext in ('pdf', 'png'):
        fig.savefig(OUTDIR / f'breakeven_contours.{ext}')
    print(f"  -> {OUTDIR}/breakeven_contours.pdf")
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 3: WEIGHT SENSITIVITY HEATMAP
# ═══════════════════════════════════════════════════════════════════════════════

def fig_heatmap(df):
    nom = {
        'w_FeO': 0.50, 'w_TiO2': 0.40,
        'w_imp_K': 0.06, 'w_imp_Th': 0.04,
        'w_Al2O3': 0.55, 'w_CaO': 0.35, 'w_het': 0.10,
        'w_K_kreep': 0.40, 'w_Th_kreep': 0.40,
        'w_U_kreep': 0.10, 'w_unc': 0.10,
    }

    df_base = compute_indices(df, nom)
    base_means = df_base.groupby('terrane')[['I_FeTi','I_AlCa','I_KREEP']].mean()

    weight_groups = {
        'I_FeTi':  ['w_FeO', 'w_TiO2', 'w_imp_K', 'w_imp_Th'],
        'I_AlCa':  ['w_Al2O3', 'w_CaO', 'w_het'],
        'I_KREEP': ['w_K_kreep', 'w_Th_kreep', 'w_U_kreep', 'w_unc'],
    }

    # Nice display labels for weights
    pretty = {
        'w_FeO': r'$w_{\mathrm{FeO}}$',
        'w_TiO2': r'$w_{\mathrm{TiO_2}}$',
        'w_imp_K': r'$P_{\mathrm{imp,K}}$',
        'w_imp_Th': r'$P_{\mathrm{imp,Th}}$',
        'w_Al2O3': r'$w_{\mathrm{Al_2O_3}}$',
        'w_CaO': r'$w_{\mathrm{CaO}}$',
        'w_het': r'$P_{\mathrm{het}}$',
        'w_K_kreep': r'$w_{\mathrm{K}}$',
        'w_Th_kreep': r'$w_{\mathrm{Th}}$',
        'w_U_kreep': r'$w_{\mathrm{U}}$',
        'w_unc': r'$P_{\mathrm{unc}}$',
    }

    factors = np.linspace(0.5, 1.5, 21)

    fig, axes = plt.subplots(1, 3, figsize=(7.5, 3.0),
                             gridspec_kw={'width_ratios': [4, 3, 4]})

    last_im = None
    for ax, idx in zip(axes, ['I_FeTi','I_AlCa','I_KREEP']):
        wl = weight_groups[idx]
        mat = np.zeros((len(wl), len(factors)))

        for i, wname in enumerate(wl):
            for j, f in enumerate(factors):
                pw = nom.copy()
                pw[wname] = nom[wname] * f
                di = compute_indices(df, pw)
                pm = di.groupby('terrane')[idx].mean()
                bspread = base_means[idx].max() - base_means[idx].min()
                pspread = pm.max() - pm.min()
                mat[i, j] = (pspread - bspread) / bspread * 100

        im = ax.imshow(mat, aspect='auto', cmap='RdBu_r',
                       vmin=-30, vmax=30, interpolation='nearest')
        last_im = im

        # x-ticks
        tick_idx = np.arange(0, len(factors), 5)
        ax.set_xticks(tick_idx)
        ax.set_xticklabels([f'{factors[t]:.1f}x' for t in tick_idx], fontsize=7)
        ax.set_xlabel('Weight multiplier', fontsize=8)

        # y-ticks
        ax.set_yticks(range(len(wl)))
        ax.set_yticklabels([pretty[w] for w in wl], fontsize=8)

        # Title using math notation
        idx_label = {'I_FeTi': r'$I_{\mathrm{FeTi}}$',
                     'I_AlCa': r'$I_{\mathrm{AlCa}}$',
                     'I_KREEP': r'$I_{\mathrm{KREEP}}$'}
        ax.set_title(idx_label[idx], fontsize=9, pad=4)

    fig.subplots_adjust(left=0.07, right=0.87, wspace=0.40, top=0.88, bottom=0.18)
    cax = fig.add_axes([0.89, 0.18, 0.015, 0.70])   # [left, bottom, width, height]
    cbar = fig.colorbar(last_im, cax=cax)
    cbar.set_label('Change in terrane separation (%)', fontsize=8)
    cbar.ax.tick_params(labelsize=7)

    fig.suptitle('Index sensitivity to individual weight perturbations',
                 fontsize=9, y=0.97)

    for ext in ('pdf', 'png'):
        fig.savefig(OUTDIR / f'weight_sensitivity_heatmap.{ext}')
    print(f"  -> {OUTDIR}/weight_sensitivity_heatmap.pdf")
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════════════
# TABLES
# ═══════════════════════════════════════════════════════════════════════════════

def save_tables(mc):
    rows = []
    for idx in ['I_FeTi','I_AlCa','I_KREEP']:
        for t in ['Highlands','Mare','KREEP']:
            s = mc['statistics'][idx][t]
            rows.append({
                'Index': idx, 'Terrane': t,
                'p5': f"{s['p5']:.3f}", 'p50': f"{s['p50']:.3f}",
                'p95': f"{s['p95']:.3f}", 'mean': f"{s['mean']:.3f}",
                'std': f"{s['std']:.3f}",
            })
    pd.DataFrame(rows).to_csv(TBLDIR / 'monte_carlo_summary.csv', index=False)

    rows = []
    for idx in ['I_FeTi','I_AlCa','I_KREEP']:
        r = mc['ranking_stability'][idx]
        rows.append({
            'Index': idx,
            'Highlands_leads_%': f"{r.get('Highlands',0)*100:.1f}",
            'Mare_leads_%': f"{r.get('Mare',0)*100:.1f}",
            'KREEP_leads_%': f"{r.get('KREEP',0)*100:.1f}",
        })
    pd.DataFrame(rows).to_csv(TBLDIR / 'ranking_stability.csv', index=False)
    print(f"  -> {TBLDIR}/monte_carlo_summary.csv")
    print(f"  -> {TBLDIR}/ranking_stability.csv")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("="*60)
    print("WAMS 2026 — Regenerating publication figures")
    print("="*60)

    print("\n[1/5] Generating synthetic LP-GRS data ...")
    df = generate_synthetic_lpgrs_data()
    print(f"  {len(df)} pixels  ({df['terrane'].value_counts().to_dict()})")

    print("\n[2/5] Computing nominal indices ...")
    df = compute_indices(df)
    print(df.groupby('terrane')[['I_FeTi','I_AlCa','I_KREEP']].mean().round(3))

    print("\n[3/5] Monte Carlo (10 000 iterations) ...")
    mc = run_monte_carlo(df, n_iter=10000, sigma=0.2, seed=42)

    print("\n[4/5] Figures ...")
    fig_violins(mc)
    fig_breakeven()
    fig_heatmap(df)

    print("\n[5/5] Tables ...")
    save_tables(mc)

    # Print summary
    print("\n" + "="*60)
    print("RANKING STABILITY")
    print("="*60)
    for idx in ['I_FeTi','I_AlCa','I_KREEP']:
        rs = mc['ranking_stability'][idx]
        leader = max(rs, key=rs.get)
        print(f"  {idx}: {leader} leads {rs[leader]*100:.1f}% of iterations")

    print("\nDone. Figures in:", OUTDIR)
