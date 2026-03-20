"""Publication-ready figures for WAMS 2026 Paper #68."""
import os
import logging

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

log = logging.getLogger(__name__)

# Publication defaults
TERRANE_COLORS = {"mare": "#2166ac", "highlands": "#b2182b", "kreep": "#1b7837"}
TERRANE_MARKERS = {"mare": "o", "highlands": "s", "kreep": "D"}
FIG_DPI = 300
FONT_SIZE = 10


def _setup_style():
    mpl.rcParams.update({
        "figure.dpi": 140,
        "savefig.dpi": FIG_DPI,
        "font.size": FONT_SIZE,
        "font.family": "serif",
        "axes.linewidth": 0.8,
        "xtick.direction": "in",
        "ytick.direction": "in",
    })


def save_fig(fig, out_dir: str, name: str):
    """Save as both PNG and PDF."""
    _setup_style()
    for ext in ("png", "pdf"):
        path = os.path.join(out_dir, f"{name}.{ext}")
        fig.savefig(path, bbox_inches="tight")
    log.info("Saved figure: %s (.png + .pdf)", name)


def fig_pca_scatter(df: pd.DataFrame, explained_var: np.ndarray,
                    separability: dict, out_dir: str):
    """Fig 1: PC1-PC2 projection with terrane classes."""
    _setup_style()
    fig, ax = plt.subplots(figsize=(6.5, 5))
    for t in ["mare", "highlands", "kreep"]:
        g = df[df["terrane"] == t]
        if g.empty:
            continue
        ax.scatter(g["PC1"], g["PC2"], s=12, alpha=0.55, label=t.capitalize(),
                   color=TERRANE_COLORS.get(t, "gray"), marker=TERRANE_MARKERS.get(t, "o"),
                   edgecolors="none")

    ax.set_xlabel(f"PC1 ({explained_var[0]*100:.1f}%)")
    ax.set_ylabel(f"PC2 ({explained_var[1]*100:.1f}%)")
    ax.set_title("PCA: Terrane Separation in Geochemical Space")
    ax.legend(markerscale=2, fontsize=9, framealpha=0.8)

    # Annotate separability metrics
    sil = separability.get("silhouette", float("nan"))
    dbi = separability.get("davies_bouldin", float("nan"))
    ax.text(0.02, 0.02, f"Silhouette = {sil:.3f}  |  DBI = {dbi:.2f}",
            transform=ax.transAxes, fontsize=8, va="bottom",
            bbox=dict(boxstyle="round,pad=0.3", fc="wheat", alpha=0.7))

    fig.tight_layout()
    save_fig(fig, out_dir, "pca_biplot")
    return fig


def fig_pca_loadings(loadings: pd.DataFrame, loading_std: np.ndarray | None,
                     out_dir: str):
    """Fig 2: PCA loadings bar chart with optional error bars."""
    _setup_style()
    fig, ax = plt.subplots(figsize=(7, 4.5))
    x = np.arange(len(loadings))
    width = 0.35
    pc1_err = loading_std[:, 0] if loading_std is not None else None
    pc2_err = loading_std[:, 1] if loading_std is not None else None

    ax.bar(x - width/2, loadings["PC1"], width, label="PC1", color="#2166ac",
           yerr=pc1_err, capsize=3, error_kw={"linewidth": 0.8})
    ax.bar(x + width/2, loadings["PC2"], width, label="PC2", color="#b2182b",
           yerr=pc2_err, capsize=3, error_kw={"linewidth": 0.8})

    ax.set_xticks(x)
    ax.set_xticklabels(loadings.index, rotation=45, ha="right")
    ax.set_ylabel("Loading")
    ax.set_title("PCA Loadings: Dominant Geochemical Drivers")
    ax.legend(fontsize=9)
    ax.axhline(0, color="gray", lw=0.5, ls="--")
    fig.tight_layout()
    save_fig(fig, out_dir, "pca_loadings")
    return fig


def fig_index_map(df: pd.DataFrame, index_col: str, title: str,
                  cmap: str, out_dir: str, fname: str):
    """Generic lat/lon scatter map for a metallurgical index."""
    _setup_style()
    fig, ax = plt.subplots(figsize=(8, 4.2))
    sc = ax.scatter(df["lon"], df["lat"], c=df[index_col], s=8,
                    cmap=cmap, alpha=0.8, edgecolors="none")
    ax.set_xlabel("Longitude (deg)")
    ax.set_ylabel("Latitude (deg)")
    ax.set_title(title)
    cbar = plt.colorbar(sc, ax=ax, shrink=0.85)
    cbar.set_label(index_col + " [0-1]")
    ax.set_xlim(-180, 180)
    ax.set_ylim(-90, 90)
    fig.tight_layout()
    save_fig(fig, out_dir, fname)
    return fig


def fig_feti_map(df: pd.DataFrame, out_dir: str):
    """Fig 3: Fe-Ti metallurgical potential map."""
    return fig_index_map(df, "I_FeTi", "Fe\u2013Ti Metallurgical Potential",
                         "inferno", out_dir, "map_feti_index")


def fig_alca_map(df: pd.DataFrame, out_dir: str):
    """Fig 4: Al-Ca metallurgical potential map."""
    return fig_index_map(df, "I_AlCa", "Al\u2013Ca Metallurgical Potential",
                         "cividis", out_dir, "map_alca_index")


def fig_kreep_map(df: pd.DataFrame, out_dir: str):
    """Fig 5: KREEP functional potential map."""
    return fig_index_map(df, "I_KREEP", "KREEP Functional Potential",
                         "magma", out_dir, "map_kreep_index")


def table_compatibility_latex(compat_df: pd.DataFrame, out_dir: str) -> str:
    """Export Table 1 as LaTeX."""
    latex = compat_df.to_latex(index=False, escape=True, column_format="llllll")
    path = os.path.join(out_dir, "compatibility_matrix.tex")
    with open(path, "w") as f:
        f.write(latex)
    log.info("LaTeX table saved: %s", path)
    return latex
