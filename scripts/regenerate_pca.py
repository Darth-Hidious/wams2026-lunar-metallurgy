#!/usr/bin/env python3
"""
Regenerate PCA results matching the paper's exact configuration:
  - 8 features: 6 CLR-transformed oxides + 2 z-scored traces (K, Th)
  - U EXCLUDED from PCA (U = 0.27*Th, linear dependency)
  - 2-degree LP-GRS data (11,306 pixels)
  - 200 sign-aligned bootstrap resamples
  - Geochemical sign convention enforced on loadings

Outputs: PCA biplot, loadings figure, loadings CSV, variance CSV
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score, davies_bouldin_score
from pathlib import Path

plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif', 'serif'],
    'mathtext.fontset': 'dejavuserif',
    'font.size': 9,
    'axes.labelsize': 10,
    'axes.titlesize': 10,
    'xtick.labelsize': 8,
    'ytick.labelsize': 8,
    'axes.linewidth': 0.6,
    'savefig.dpi': 300,
    'figure.dpi': 150,
})

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
FIG  = ROOT / "figures"
TBL  = ROOT / "tables"
FIG.mkdir(exist_ok=True)
TBL.mkdir(exist_ok=True)

TERRANE_COLORS = {'highlands': '#3B7DD8', 'mare': '#D64545', 'kreep': '#E8A630'}

# ── 1. Load data ──────────────────────────────────────────────────────
print("[1/7] Loading LP-GRS 2-degree data...")
df = pd.read_csv(DATA / "lunar_geochem_2deg.csv")
print(f"  {len(df)} rows loaded")

# ── 2. Terrane classification ─────────────────────────────────────────
print("[2/7] Classifying terranes...")
def classify_terrane(row):
    if row['Th'] > 3.5:
        return 'kreep'
    elif row['FeO'] > 8 and row['TiO2'] > 0.5:
        return 'mare'
    else:
        return 'highlands'

df['terrane'] = df.apply(classify_terrane, axis=1)
counts = df['terrane'].value_counts()
print(f"  highlands: {counts.get('highlands', 0)}")
print(f"  mare: {counts.get('mare', 0)}")
print(f"  kreep: {counts.get('kreep', 0)}")
print(f"  total: {len(df)}")

# ── 3. Data cleaning ──────────────────────────────────────────────────
print("[3/7] Cleaning data...")
OXIDE_COLS = ['FeO', 'TiO2', 'Al2O3', 'CaO', 'MgO', 'SiO2']
TRACE_COLS = ['K', 'Th']
BOUNDS = {
    'FeO': (0, 28), 'TiO2': (0, 15), 'Al2O3': (0, 38),
    'CaO': (0, 22), 'MgO': (0, 25), 'SiO2': (35, 55),
}

clipped = 0
for col, (lo, hi) in BOUNDS.items():
    if col not in df.columns:
        continue
    mask = (df[col] < lo) | (df[col] > hi)
    clipped += mask.sum()
    df.loc[mask, col] = np.nan

# Terrane-wise median imputation for NaN and zeros
zeros_replaced = 0
for col in OXIDE_COLS:
    zero_mask = df[col] == 0
    zeros_replaced += zero_mask.sum()
    df.loc[zero_mask, col] = np.nan
    for t in df['terrane'].unique():
        tmask = df['terrane'] == t
        median = df.loc[tmask, col].median()
        df.loc[tmask & df[col].isna(), col] = median

print(f"  {clipped} values clipped, {zeros_replaced} zeros replaced")

# ── 4. CLR transform (oxides only) + z-score traces ──────────────────
print("[4/7] CLR transform + z-score...")

def clr_transform(X, eps=1e-10):
    X = np.clip(X, eps, None)
    log_X = np.log(X)
    geo_mean = log_X.mean(axis=1, keepdims=True)
    return log_X - geo_mean

X_clr = clr_transform(df[OXIDE_COLS].values)
scaler_trace = StandardScaler()
X_trace = scaler_trace.fit_transform(df[TRACE_COLS].values)

# Combine: 6 CLR oxides + 2 z-scored traces = 8 features
X_combined = np.hstack([X_clr, X_trace])
feature_names = OXIDE_COLS + TRACE_COLS

# Standardize the combined matrix
scaler = StandardScaler()
X_std = scaler.fit_transform(X_combined)
print(f"  Feature matrix: {X_std.shape} (8 features, U excluded)")

# ── 5. PCA ────────────────────────────────────────────────────────────
print("[5/7] PCA + bootstrap loadings...")
N_COMPONENTS = 3
pca = PCA(n_components=N_COMPONENTS)
scores = pca.fit_transform(X_std)
df['PC1'] = scores[:, 0]
df['PC2'] = scores[:, 1]
df['PC3'] = scores[:, 2]

var_explained = pca.explained_variance_ratio_
print(f"  Variance: PC1={var_explained[0]*100:.1f}%, PC2={var_explained[1]*100:.1f}%, PC3={var_explained[2]*100:.1f}%")
print(f"  Cumulative: {sum(var_explained)*100:.1f}%")

# Separability
sil = silhouette_score(scores, df['terrane'])
dbi = davies_bouldin_score(scores, df['terrane'])
print(f"  Silhouette: {sil:.3f}  |  Davies-Bouldin: {dbi:.3f}")

# Raw loadings
loadings_raw = pca.components_.T  # (8, 3)

# ── Enforce geochemical sign convention ───────────────────────────────
# PC1: highlands (Al2O3, CaO, SiO2 negative) vs mare/KREEP (FeO, TiO2, K, Th positive)
#   => FeO should be positive on PC1
if loadings_raw[feature_names.index('FeO'), 0] < 0:
    loadings_raw[:, 0] *= -1
    df['PC1'] *= -1
    print("  PC1 sign flipped (FeO convention)")

# PC2: MgO dominant positive
if loadings_raw[feature_names.index('MgO'), 1] < 0:
    loadings_raw[:, 1] *= -1
    df['PC2'] *= -1
    print("  PC2 sign flipped (MgO convention)")

# PC3: TiO2 dominant positive
if loadings_raw[feature_names.index('TiO2'), 2] < 0:
    loadings_raw[:, 2] *= -1
    df['PC3'] *= -1
    print("  PC3 sign flipped (TiO2 convention)")

# ── Bootstrap with same sign convention ───────────────────────────────
N_BOOT = 200
rng = np.random.default_rng(42)
all_loadings = np.zeros((N_BOOT, len(feature_names), N_COMPONENTS))

for b in range(N_BOOT):
    idx = rng.choice(len(X_std), size=len(X_std), replace=True)
    pca_b = PCA(n_components=N_COMPONENTS)
    pca_b.fit(X_std[idx])
    load_b = pca_b.components_.T
    # Align to reference via dot product
    for c in range(N_COMPONENTS):
        if np.dot(load_b[:, c], loadings_raw[:, c]) < 0:
            load_b[:, c] *= -1
    all_loadings[b] = load_b

mean_load = all_loadings.mean(axis=0)
std_load = all_loadings.std(axis=0)
print(f"  Bootstrap: {N_BOOT} iterations, max std = {std_load.max():.4f}")

# Use bootstrap means as final loadings
loadings = pd.DataFrame(mean_load, index=feature_names,
                         columns=['PC1', 'PC2', 'PC3'])

# Print loadings for verification
print("\n  Final loadings (bootstrap mean, sign-convention enforced):")
for feat in feature_names:
    pc1, pc2, pc3 = loadings.loc[feat]
    s1, s2, s3 = std_load[feature_names.index(feat)]
    print(f"    {feat:<8} PC1={pc1:+.2f}±{s1:.3f}  PC2={pc2:+.2f}±{s2:.3f}  PC3={pc3:+.2f}±{s3:.3f}")

# ── 6. Save tables ───────────────────────────────────────────────────
print("\n[6/7] Saving tables...")
load_export = loadings.copy()
for i in range(N_COMPONENTS):
    load_export[f'PC{i+1}_std'] = std_load[:, i]
load_export.to_csv(TBL / 'pca_loadings.csv')
print(f"  -> {TBL}/pca_loadings.csv")

var_df = pd.DataFrame({
    'Component': [f'PC{i+1}' for i in range(N_COMPONENTS)],
    'Explained_variance_pct': [v*100 for v in var_explained],
    'Cumulative_pct': [sum(var_explained[:i+1])*100 for i in range(N_COMPONENTS)],
})
var_df.to_csv(TBL / 'pca_variance.csv', index=False)
print(f"  -> {TBL}/pca_variance.csv")

# ── 7. Figures ────────────────────────────────────────────────────────
print("[7/7] Generating figures...")

# --- Biplot ---
fig, ax = plt.subplots(figsize=(6.5, 5))
for t in ['highlands', 'mare', 'kreep']:
    g = df[df['terrane'] == t]
    ax.scatter(g['PC1'], g['PC2'], s=8, alpha=0.4,
               label=t.capitalize(), color=TERRANE_COLORS[t],
               edgecolors='none', zorder=2)

# Loading vectors with manual nudges to avoid overlaps
scale = 4.0
# Manual label offsets: (dx, dy) nudge from arrow tip
nudge = {
    'FeO':   (+0.25, -0.20),
    'TiO2':  (-0.10, +0.25),
    'Al2O3': (-0.35, +0.15),
    'CaO':   (+0.10, -0.30),
    'MgO':   (+0.20, +0.25),
    'SiO2':  (-0.35, -0.15),
    'K':     (+0.30, +0.20),   # nudge right to avoid Th
    'Th':    (+0.10, -0.25),   # nudge down to avoid K
}
for i, feat in enumerate(feature_names):
    tip_x = loadings.iloc[i, 0] * scale
    tip_y = loadings.iloc[i, 1] * scale
    ax.annotate('', xy=(tip_x, tip_y), xytext=(0, 0),
                arrowprops=dict(arrowstyle='->', color='black', lw=1.0))
    dx, dy = nudge.get(feat, (0.15, 0.15))
    label = feat.replace('2', '$_2$').replace('3', '$_3$')
    ax.text(tip_x + dx, tip_y + dy, label, fontsize=7.5,
            ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.15', fc='white', ec='none', alpha=0.85))

ax.set_xlabel(f'PC1 ({var_explained[0]*100:.1f}%)')
ax.set_ylabel(f'PC2 ({var_explained[1]*100:.1f}%)')
ax.axhline(0, color='grey', lw=0.5, ls='--', alpha=0.5)
ax.axvline(0, color='grey', lw=0.5, ls='--', alpha=0.5)
ax.legend(fontsize=8, loc='upper right', framealpha=0.9)
ax.grid(True, alpha=0.1)
fig.tight_layout()
for ext in ('pdf', 'png'):
    fig.savefig(FIG / f'pca_biplot.{ext}')
print(f"  -> {FIG}/pca_biplot.pdf")
plt.close()

# --- Loadings bar chart ---
fig, ax = plt.subplots(figsize=(7, 4))
x = np.arange(len(feature_names))
width = 0.25
labels_pretty = [f.replace('2', '$_2$').replace('3', '$_3$') for f in feature_names]
colors = ['#2166ac', '#b2182b', '#4dac26']

for i, (pc, col) in enumerate(zip(['PC1','PC2','PC3'], colors)):
    ax.bar(x + i*width, loadings[pc], width, label=f'{pc} ({var_explained[i]*100:.1f}%)',
           color=col, yerr=std_load[:, i], capsize=2, error_kw={'linewidth': 0.6})

ax.set_xticks(x + width)
ax.set_xticklabels(labels_pretty, fontsize=9)
ax.set_ylabel('Loading')
ax.axhline(0, color='grey', lw=0.5)
ax.legend(fontsize=8, loc='upper right')
ax.grid(True, alpha=0.1, axis='y')
fig.tight_layout()
for ext in ('pdf', 'png'):
    fig.savefig(FIG / f'pca_loadings.{ext}')
print(f"  -> {FIG}/pca_loadings.pdf")
plt.close()

# --- UMAP embedding ---
print("  Generating UMAP embedding...")
from umap import UMAP

reducer = UMAP(n_components=2, n_neighbors=30, min_dist=0.3,
               metric='euclidean', random_state=42)
umap_embedding = reducer.fit_transform(X_std)

fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))

# Left panel: UMAP coloured by terrane
ax = axes[0]
for t in ['highlands', 'mare', 'kreep']:
    mask = df['terrane'] == t
    ax.scatter(umap_embedding[mask, 0], umap_embedding[mask, 1],
               s=6, alpha=0.35, label=t.capitalize(),
               color=TERRANE_COLORS[t], edgecolors='none')
ax.set_xlabel('UMAP-1')
ax.set_ylabel('UMAP-2')
ax.set_title('Terrane separation', fontsize=10)
ax.legend(fontsize=8, loc='best', framealpha=0.9)
ax.grid(True, alpha=0.1)

# Right panel: UMAP coloured by I_FeTi (continuous)
# Recompute indices for colouring
from regenerate_figures import compute_indices as ci_func
df_idx = ci_func(df.rename(columns={c: c for c in df.columns}))

ax = axes[1]
sc = ax.scatter(umap_embedding[:, 0], umap_embedding[:, 1],
                s=6, alpha=0.4, c=df_idx['I_FeTi'], cmap='RdYlBu_r',
                edgecolors='none', vmin=0, vmax=0.7)
ax.set_xlabel('UMAP-1')
ax.set_ylabel('UMAP-2')
ax.set_title(r'Coloured by $I_{\mathrm{FeTi}}$', fontsize=10)
cbar = fig.colorbar(sc, ax=ax, shrink=0.85, pad=0.02)
cbar.set_label(r'$I_{\mathrm{FeTi}}$', fontsize=9)
cbar.ax.tick_params(labelsize=7)
ax.grid(True, alpha=0.1)

fig.tight_layout(w_pad=2.0)
for ext in ('pdf', 'png'):
    fig.savefig(FIG / f'umap_embedding.{ext}')
print(f"  -> {FIG}/umap_embedding.pdf")
plt.close()

# Silhouette on UMAP space
sil_umap = silhouette_score(umap_embedding, df['terrane'])
dbi_umap = davies_bouldin_score(umap_embedding, df['terrane'])
print(f"  UMAP separability: Silhouette={sil_umap:.3f}  DBI={dbi_umap:.3f}")

print("\n" + "="*60)
print("PAPER CROSS-CHECK")
print("="*60)
print(f"  Variance: PC1={var_explained[0]*100:.1f}% PC2={var_explained[1]*100:.1f}% PC3={var_explained[2]*100:.1f}%")
print(f"  Cumulative: {sum(var_explained)*100:.1f}% (paper says 83.6%)")
print(f"  Silhouette (PCA): {sil:.3f}")
print(f"  DBI (PCA): {dbi:.3f}")
print(f"  Silhouette (UMAP): {sil_umap:.3f}")
print(f"  DBI (UMAP): {dbi_umap:.3f}")
print(f"  Pixels: {len(df)} (paper says 11,306)")
print(f"  Features: {len(feature_names)} (paper says 8, U excluded)")
