#!/usr/bin/env python3
"""
Elastic constants and Pugh's G/B ductility ratio for the cached MACE-MH-1
relaxed structures.

Builds the 6x6 elastic stiffness tensor C_ij from finite-difference
strain-stress fits (6 strain modes, ±0.005 amplitude), then computes
isotropic shear modulus G and bulk modulus B via Voigt-Reuss-Hill averaging
and the Pugh's ratio G/B.

Pugh (1954): G/B < 0.57 -> ductile; G/B > 0.57 -> brittle.

The published JOM 2025 "RHEA-AM Manufacturability Index" cites Pugh's G/B
as the strongest single descriptor of LPBF cracking susceptibility
(r = -0.90 with cumulative crack length).  This script computes the Pugh
component of that index for our reference compositions, the dilution path,
and the named Laves competitors Fe2Nb and Fe2Ta.

Outputs:
  phase_diagrams/elastic_results.csv      raw C_ij + G + B + G/B per phase
  figures/presentation/slide_10_pugh_ductility.pdf
  figures/presentation/slide_11_pugh_dilution_path.pdf
"""

from __future__ import annotations

import csv
import os
import time
import warnings
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from ase import Atoms
from ase.io import read as ase_read

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
CACHE_RHEA = ROOT / "phase_diagrams" / "mace_cache"
CACHE_DIL = ROOT / "phase_diagrams" / "dilution_results"
SLIDES = ROOT / "figures" / "presentation"
CSV_OUT = ROOT / "phase_diagrams" / "elastic_results.csv"

# ---------------------------------------------------------------------------
# Strain modes (Voigt notation: xx, yy, zz, yz, xz, xy)
# ---------------------------------------------------------------------------
STRAIN_AMPLITUDE = 0.005
N_STRAINS = 6


def voigt_strain_tensor(component: int, eps: float) -> np.ndarray:
    """Build a symmetric 3x3 strain tensor for Voigt component (0..5)."""
    s = np.zeros((3, 3))
    if component < 3:
        s[component, component] = eps
    elif component == 3:  # yz
        s[1, 2] = s[2, 1] = eps / 2
    elif component == 4:  # xz
        s[0, 2] = s[2, 0] = eps / 2
    elif component == 5:  # xy
        s[0, 1] = s[1, 0] = eps / 2
    return s


def apply_strain(atoms: Atoms, strain: np.ndarray) -> Atoms:
    """Return a copy of `atoms` with the strain tensor applied to its cell.

    Atoms are scaled with the cell so that fractional coordinates are
    unchanged.  This is the standard convention for elastic-constant fits
    that hold internal coordinates frozen at the reference relaxed state.
    """
    new = atoms.copy()
    deformation = np.eye(3) + strain
    new.set_cell(atoms.cell.array @ deformation, scale_atoms=True)
    return new


def stress_voigt(atoms: Atoms) -> np.ndarray:
    """ASE returns stress in Voigt order (xx, yy, zz, yz, xz, xy) in eV/A^3."""
    return atoms.get_stress()


# ---------------------------------------------------------------------------
# C_ij from 6 strain pairs (central-difference)
# ---------------------------------------------------------------------------
def elastic_tensor(atoms_relaxed: Atoms, calc, label: str = "") -> np.ndarray:
    """Compute the 6x6 stiffness tensor by central differences."""
    base = atoms_relaxed.copy()
    base.calc = calc

    # Reference stress (should be ~0 since cell is relaxed)
    s_ref = stress_voigt(base)
    print(f"  [{label}]  reference |stress|max = "
          f"{np.max(np.abs(s_ref)) * 160.21766208:.3f} GPa")

    C = np.zeros((6, 6))
    for j in range(N_STRAINS):
        sigma_plus = stress_voigt(_strained(atoms_relaxed, calc, j, +STRAIN_AMPLITUDE))
        sigma_minus = stress_voigt(_strained(atoms_relaxed, calc, j, -STRAIN_AMPLITUDE))
        # Central difference: C_ij = (sigma_i(+eps) - sigma_i(-eps)) / (2 eps)
        # Sign correction: for stress definition with positive=tensile, the
        # response of a tensile stress to tensile strain is positive.
        dC = (sigma_plus - sigma_minus) / (2.0 * STRAIN_AMPLITUDE)
        C[:, j] = dC

    # Symmetrize: C should be symmetric
    C = 0.5 * (C + C.T)
    # Convert eV/A^3 to GPa (1 eV/A^3 = 160.21766208 GPa)
    C *= 160.21766208
    return C


def _strained(atoms_relaxed: Atoms, calc, comp: int, eps: float) -> Atoms:
    a = apply_strain(atoms_relaxed, voigt_strain_tensor(comp, eps))
    a.calc = calc
    a.get_potential_energy()  # ensure stress is computed
    return a


# ---------------------------------------------------------------------------
# Voigt-Reuss-Hill polycrystalline averaging
# ---------------------------------------------------------------------------
def voigt_reuss_hill(C: np.ndarray) -> tuple[float, float, float]:
    """Return (G_VRH, B_VRH, Pugh_G/B) from the 6x6 stiffness tensor.

    Voigt: upper bound (constant strain).
    Reuss: lower bound (constant stress) — needs S = inv(C).
    Hill:  arithmetic mean of Voigt and Reuss.

    Formulas for the Voigt average (general anisotropy, Hill 1952):
        9 K_V = (C11 + C22 + C33) + 2*(C12 + C23 + C13)
        15 G_V = (C11 + C22 + C33) - (C12 + C23 + C13)
                 + 3*(C44 + C55 + C66)

    For Reuss with the compliance S = inv(C):
        1/K_R = (S11 + S22 + S33) + 2*(S12 + S23 + S13)
        15/G_R = 4*(S11 + S22 + S33) - 4*(S12 + S23 + S13)
                  + 3*(S44 + S55 + S66)
    """
    C11, C22, C33 = C[0, 0], C[1, 1], C[2, 2]
    C12, C13, C23 = C[0, 1], C[0, 2], C[1, 2]
    C44, C55, C66 = C[3, 3], C[4, 4], C[5, 5]

    K_V = ((C11 + C22 + C33) + 2 * (C12 + C13 + C23)) / 9.0
    G_V = ((C11 + C22 + C33) - (C12 + C13 + C23) + 3 * (C44 + C55 + C66)) / 15.0

    try:
        S = np.linalg.inv(C)
    except np.linalg.LinAlgError:
        return float("nan"), float("nan"), float("nan")
    S11, S22, S33 = S[0, 0], S[1, 1], S[2, 2]
    S12, S13, S23 = S[0, 1], S[0, 2], S[1, 2]
    S44, S55, S66 = S[3, 3], S[4, 4], S[5, 5]
    K_R_inv = (S11 + S22 + S33) + 2 * (S12 + S13 + S23)
    G_R_inv = (4 * (S11 + S22 + S33) - 4 * (S12 + S13 + S23)
               + 3 * (S44 + S55 + S66)) / 15.0

    K_R = 1.0 / K_R_inv if K_R_inv > 0 else float("nan")
    G_R = 1.0 / G_R_inv if G_R_inv > 0 else float("nan")
    K_VRH = 0.5 * (K_V + K_R)
    G_VRH = 0.5 * (G_V + G_R)
    pugh = G_VRH / K_VRH if K_VRH > 0 else float("nan")
    return G_VRH, K_VRH, pugh


# ---------------------------------------------------------------------------
# Targets — every structure we have
# ---------------------------------------------------------------------------
@dataclass
class Target:
    label: str
    short: str
    path: Path
    group: str  # "rhea" | "dilution" | "laves"


def collect_targets() -> list[Target]:
    targets: list[Target] = []

    # The three named RHEAs (BCC only)
    for short, name in [("R1", "R1_HfNbTaTiZr"),
                         ("R2", "R2_MoNbTaTiV"),
                         ("R3", "R3_ISRU_blend")]:
        p = CACHE_RHEA / f"relaxed_bcc_{name}.traj"
        if p.exists():
            targets.append(Target(label=name, short=short, path=p, group="rhea"))

    # Dilution path (BCC at 7 ISRU fractions)
    for x_int in (0, 10, 25, 50, 75, 90, 100):
        p = CACHE_DIL / f"relaxed_bcc_x{x_int:03d}.traj"
        if p.exists():
            targets.append(Target(
                label=f"BCC x={x_int}% ISRU",
                short=f"x={x_int}",
                path=p, group="dilution",
            ))

    # Laves competitors
    for laves in ("fe2nb", "fe2ta"):
        p = CACHE_DIL / f"relaxed_{laves}.traj"
        if p.exists():
            targets.append(Target(
                label=laves.replace("fe2", "Fe2").upper().replace("NB", "Nb").replace("TA", "Ta"),
                short=laves.replace("fe2", "Fe$_2$").replace("nb", "Nb").replace("ta", "Ta"),
                path=p, group="laves",
            ))
    return targets


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def make_calc():
    from huggingface_hub import hf_hub_download
    from mace.calculators import mace_mp
    path = hf_hub_download(repo_id="mace-foundations/mace-mh-1",
                           filename="mace-mh-1.model")
    return mace_mp(model=path, default_dtype="float64",
                   device="cpu", head="omat_pbe")


def main() -> None:
    targets = collect_targets()
    print(f"Found {len(targets)} cached structures.")

    calc = make_calc()

    rows = []
    t_total = time.time()
    for t in targets:
        atoms = ase_read(t.path)
        atoms.calc = calc
        t0 = time.time()
        try:
            C = elastic_tensor(atoms, calc, label=t.short)
            G, B, pugh = voigt_reuss_hill(C)
            print(f"  -> G={G:.1f} GPa  B={B:.1f} GPa  G/B={pugh:.3f}  "
                  f"({time.time()-t0:.1f} s)")
            rows.append((t, G, B, pugh, C))
        except Exception as ex:
            print(f"  FAILED: {ex}")
            rows.append((t, float("nan"), float("nan"), float("nan"), None))

    print(f"\nTotal compute: {(time.time()-t_total)/60:.1f} min")

    # ---- Write CSV ----
    with open(CSV_OUT, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["label", "short", "group", "G_VRH_GPa", "B_VRH_GPa",
                    "Pugh_G_over_B", "C11", "C12", "C44"])
        for t, G, B, pugh, C in rows:
            if C is not None:
                w.writerow([t.label, t.short, t.group, f"{G:.2f}", f"{B:.2f}",
                            f"{pugh:.4f}",
                            f"{C[0,0]:.2f}", f"{C[0,1]:.2f}", f"{C[3,3]:.2f}"])
    print(f"wrote {CSV_OUT}")

    # ---- Plot ----
    plot_pugh(rows)


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------
PUGH_THRESHOLD = 0.57  # Pugh 1954: G/B < 0.57 -> ductile

SLIDE_RC = {
    "font.size": 16, "axes.labelsize": 18, "axes.titlesize": 20,
    "xtick.labelsize": 13, "ytick.labelsize": 15, "legend.fontsize": 14,
    "axes.linewidth": 1.2, "xtick.major.width": 1.2, "ytick.major.width": 1.2,
    "lines.linewidth": 2.5, "figure.dpi": 300, "savefig.dpi": 300,
    "savefig.bbox": "tight", "axes.spines.top": False, "axes.spines.right": False,
}


def plot_pugh(rows):
    plt.rcParams.update(SLIDE_RC)
    SLIDES.mkdir(parents=True, exist_ok=True)

    # ---- Slide 10: Pugh map across all 12 structures ----
    fig, ax = plt.subplots(figsize=(15, 8))

    # Order: RHEAs, dilution path (sorted by x), Laves
    rheas = [r for r in rows if r[0].group == "rhea"]
    dilution = sorted(
        [r for r in rows if r[0].group == "dilution"],
        key=lambda r: int(r[0].short.split("=")[1].rstrip("%")),
    )
    laves = [r for r in rows if r[0].group == "laves"]

    ordered = rheas + dilution + laves
    labels = [r[0].short for r in ordered]
    pugh = np.array([r[3] for r in ordered])

    colors = []
    for r in ordered:
        if r[0].group == "rhea":
            colors.append("#1f77b4")
        elif r[0].group == "dilution":
            colors.append("#2ca02c")
        else:
            colors.append("#d62728")

    bars = ax.bar(range(len(ordered)), pugh, color=colors, alpha=0.85,
                   edgecolor="black", linewidth=0.8)
    for b, v in zip(bars, pugh):
        if not np.isnan(v):
            ax.text(b.get_x() + b.get_width() / 2,
                    v + 0.015, f"{v:.2f}", ha="center", va="bottom",
                    fontsize=12, fontweight="bold")

    ax.axhline(PUGH_THRESHOLD, color="black", lw=1.5, ls="--",
                label=f"Pugh threshold (G/B = {PUGH_THRESHOLD})")
    ax.fill_between([-0.5, len(ordered) - 0.5], 0, PUGH_THRESHOLD,
                     color="#4CAF50", alpha=0.10, label="ductile region")
    ax.fill_between([-0.5, len(ordered) - 0.5], PUGH_THRESHOLD,
                     max(np.nanmax(pugh) * 1.10, PUGH_THRESHOLD * 1.5),
                     color="#FF5722", alpha=0.10, label="brittle region")

    ax.set_xticks(range(len(ordered)))
    ax.set_xticklabels(labels, rotation=30, ha="right")
    ax.set_ylabel("Pugh's ratio  G / B")
    ax.set_xlim(-0.5, len(ordered) - 0.5)
    ax.set_title("Ductility prediction (mace-mh-1 elastic constants, "
                  "Voigt-Reuss-Hill)", pad=14)
    ax.legend(loc="upper left", framealpha=0.95)
    ax.grid(axis="y", alpha=0.3)

    # Group separators
    for x in (len(rheas) - 0.5, len(rheas) + len(dilution) - 0.5):
        ax.axvline(x, color="grey", lw=0.8, ls=":")
    ax.text(len(rheas) / 2 - 0.5, ax.get_ylim()[1] * 0.97, "Reference RHEAs",
             ha="center", fontsize=12, fontweight="bold", color="#1f77b4")
    ax.text(len(rheas) + len(dilution) / 2 - 0.5, ax.get_ylim()[1] * 0.97,
             "Dilution path: MoNbTaTiV → Fe-50Ti",
             ha="center", fontsize=12, fontweight="bold", color="#2ca02c")
    ax.text(len(rheas) + len(dilution) + len(laves) / 2 - 0.5,
             ax.get_ylim()[1] * 0.97, "Laves competitors",
             ha="center", fontsize=12, fontweight="bold", color="#d62728")

    out = SLIDES / "slide_10_pugh_ductility"
    fig.savefig(out.with_suffix(".pdf")); fig.savefig(out.with_suffix(".png"))
    print(f"  ✓ {out.name}")
    plt.close(fig)

    # ---- Slide 11: Pugh along the dilution path only (single panel) ----
    if dilution:
        fig, ax = plt.subplots(figsize=(13, 7))
        xs = np.array([int(r[0].short.split("=")[1].rstrip("%")) for r in dilution])
        ys = np.array([r[3] for r in dilution])
        ax.plot(xs, ys, "-o", color="#2ca02c", lw=3, markersize=10,
                  markeredgecolor="black", label="BCC solid solution")

        # Add Laves end-members as horizontal lines for context
        for r, color, ls in zip(laves, ["#d62728", "#9467bd"], ["--", ":"]):
            if not np.isnan(r[3]):
                ax.axhline(r[3], color=color, lw=2, ls=ls,
                            label=f"{r[0].short} (pure Laves)")

        ax.axhline(PUGH_THRESHOLD, color="black", lw=1.5, ls="--",
                    label=f"Pugh threshold (G/B = {PUGH_THRESHOLD})")

        ax.set_xlabel("ISRU fraction (% atomic)")
        ax.set_ylabel("Pugh's ratio  G / B")
        ax.set_title("Ductility along the dilution path "
                     "(MoNbTaTiV → Fe-50Ti)", pad=14)
        ax.legend(loc="best", framealpha=0.95)
        ax.grid(alpha=0.3)
        out = SLIDES / "slide_11_pugh_dilution_path"
        fig.savefig(out.with_suffix(".pdf"))
        fig.savefig(out.with_suffix(".png"))
        print(f"  ✓ {out.name}")
        plt.close(fig)


if __name__ == "__main__":
    main()
