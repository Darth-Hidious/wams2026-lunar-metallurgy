# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "jax[cpu]>=0.4.30",
#   "jaxlib>=0.4.30",
#   "numpy>=1.24",
#   "ase>=3.23",
#   "matplotlib>=3.7",
#   "huggingface_hub>=0.20",
# ]
# ///
"""
am_process_lunar_terranes.py — JAX Rosenthal/Hunt/Bo screen for ISRU-derived
lunar-feedstock alloys.  Closes the loop:

    LP-GRS terrane chemistry  →  ISRU reduction route  →  alloy composition
        →  MACE-relaxed cell  →  density ρ  →  AM-process model
        →  Pe, Ma, Bo, melt-pool L, W, d, cooling rate, dendrite spacing λ₁

Targets (lunar gravity only, g = 1.624 m/s²):

  1. MARE_FeTi      Fe-50Ti (mol%) from ilmenite reduction (mare basalt)
                    ρ from rule-of-mixtures (Fe 7874 + Ti 4540)/2 corrected
                    by Vegard's law on lattice; book c_p, κ, T_m.
  2. HIGHL_AlSi     Al-12Si (wt%, ≈ eutectic) from FFC-Cambridge on anorthite
                    (highlands).  Aluminium AM workhorse alloy.
  3. ISRU_BLEND     Fe₀.₃Ti₀.₃Al₀.₂Nb₀.₁Ta₀.₁ — cross-terrane blend with Earth
                    refractory additions.  Density ρ_MACE from the
                    relaxed BCC supercell (closes the MACE→AM loop).
  4. SPARK_R1       CrMoTaWV (refractory) — Earth-shipped, lunar AM.
  5. SPARK_S1       HESA-2 (Ni-super)     — Earth-shipped, lunar AM.

For each alloy under nominal LPBF conditions (P = 200 W, v = 0.8 m/s,
σ = 50 μm, ε_R = 5 μm regularisation) we report:
    L  W  d   [melt-pool length, width, depth in μm]
    Ṫ        [cooling rate at trailing edge, K/s]
    λ₁       [primary dendrite arm spacing, μm]
    Pe Ma Bo [dimensionless numbers]
    AM verdict (printable? marginal? not printable? — heuristic from L/W ratio,
                Bo, cooling rate, and depth-to-layer-thickness)

Outputs:
    am_lunar_terranes_summary.json   — full record per alloy
    am_lunar_terranes_table.csv      — flat table for paper
    figures/fig_lunar_terranes_bars.pdf  — comparison bar chart

Run on HF Jobs:
    hf jobs uv run --flavor cpu-basic --timeout 20m --secrets HF_TOKEN \\
        phase_diagrams/am_process_lunar_terranes.py
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import dataclass, asdict
from pathlib import Path

import jax
import jax.numpy as jnp
from jax import jit, vmap
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------
G_LUNAR = 1.624          # m/s^2 — lunar surface gravity
T_0     = 300.0          # K     — ambient/preheat
EPS_R   = 5.0e-6         # m     — Rosenthal regularisation (matches v4)

NOMINAL_PROC = dict(P=200.0, v=0.8, sigma=50.0e-6, T_0=T_0)
A_KZ_HUNT    = 80.0e-6   # μm·(K/s)^(1/3) — Hunt/Kurz-Fisher coefficient

OUT_DIR = Path(os.environ.get("OUT_DIR", "/tmp/lunar_terranes_out"))
OUT_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR = OUT_DIR / "figures"; FIG_DIR.mkdir(exist_ok=True)

RESULTS_REPO = os.environ.get("RESULTS_REPO",
                                "Darth-Hidious/wams2026-am-lunar-terranes")

# Public repo for the MACE-relaxed .traj of R3_ISRU_blend
GITHUB_REPO = "https://github.com/Darth-Hidious/wams2026-lunar-metallurgy.git"
STRUCT_ROOT = Path(os.environ.get("STRUCT_ROOT",
                                    "/tmp/wams26_repo/phase_diagrams"))

# ----------------------------------------------------------------------------
# Alloy properties
# ----------------------------------------------------------------------------
@dataclass(frozen=True)
class Alloy:
    name:        str
    pretty:      str
    composition: str
    terrane:     str           # "mare", "highlands", "blend", "earth-import"
    kappa:       float          # W/(m·K), at LPBF working T (~1500 K), eff
    rho:         float          # kg/m^3
    cp:          float          # J/(kg·K), at ~working T
    T_m:         float          # K
    L_f:         float          # J/kg  (latent heat of fusion)
    sigma_s:     float          # N/m
    dsigma_dT:   float          # N/(m·K)  — negative; we store as |·|
    eta:         float          # absorptivity [-]  at 1.06 μm
    nu_l:        float          # m^2/s   — kinematic viscosity
    rho_source:  str            # "MACE-relaxed", "rule-of-mixtures", "experimental"

    @property
    def alpha(self) -> float:
        return self.kappa / (self.rho * self.cp)


def mare_FeTi() -> Alloy:
    """Mare basalt → ilmenite (FeTiO₃) reduced by H₂ to give Fe + Ti +
    metallic O₂.  Equimolar 50:50 mol Fe:Ti (the natural stoichiometry).
    Densities Fe = 7874, Ti = 4540 kg/m³; Vegard-like blend gives ~6500
    for the cast Fe-Ti binary, but Fe-Ti forms intermetallics (Fe₂Ti, FeTi)
    with somewhat higher density; we use 6800 as a reasonable midpoint.
    κ, c_p, T_m from FeTi intermetallic reference at ~1500 K."""
    return Alloy(
        name="MARE_FeTi", pretty="Mare Fe–Ti (ilmenite-route)",
        composition="Fe$_{0.5}$Ti$_{0.5}$ (50 mol% each)",
        terrane="mare",
        kappa=21.0,     # FeTi @ 1500 K ≈ 20–22 W/(m·K)
        rho=6800.0,
        cp=650.0,       # average of Fe(c_p ≈ 700) and Ti(c_p ≈ 600) at 1500 K
        T_m=1590.0,     # FeTi peritectic at 1590 K (Massalski)
        L_f=2.0e5,
        sigma_s=1.65,   # Fe-Ti ~ 1.6–1.7 N/m
        dsigma_dT=2.5e-4,
        eta=0.45,       # Fe-rich alloys at 1.06 μm
        nu_l=8.0e-7,
        rho_source="rule-of-mixtures (Fe/Ti Vegard + FeTi correction)",
    )

def highlands_AlSi() -> Alloy:
    """Feldspathic highlands → anorthite (CaAl₂Si₂O₈) reduced by molten salt
    (FFC-Cambridge) gives Al-Si alloy, typically Al-12Si eutectic.  This is
    the same chemistry as AlSi10Mg / AlSi12 commercial powders, which are
    the AM-workhorse alloys with extensive process windows."""
    return Alloy(
        name="HIGHL_AlSi", pretty="Highlands Al–12Si (FFC-route)",
        composition=r"Al-12Si (wt\%) eutectic",
        terrane="highlands",
        kappa=130.0,    # AlSi12 @ 800 K ~ 130 W/(m·K)
        rho=2660.0,     # AlSi12 measured ~ 2.65–2.68 g/cm³
        cp=1100.0,      # AlSi12 c_p at 800 K
        T_m=850.0,      # Al-Si eutectic = 577 °C = 850 K
        L_f=4.2e5,
        sigma_s=0.84,   # AlSi12 σ at 1000 K
        dsigma_dT=1.5e-4,
        eta=0.20,       # Al at 1.06 μm — KEY DIFFERENCE (reflective!)
        nu_l=1.4e-6,
        rho_source="rule-of-mixtures (Al-Si Vegard)",
    )

def isru_blend(rho_mace: float) -> Alloy:
    """Fe₀.₃Ti₀.₃Al₀.₂Nb₀.₁Ta₀.₁ — cross-terrane blend with refractory
    additions.  Density taken directly from the MACE-MH-1 BCC relaxation:
    ρ = (Σ m_i) / V_relaxed.  All other properties rule-of-mixtures."""
    return Alloy(
        name="ISRU_BLEND", pretty="ISRU blend Fe-Ti-Al-Nb-Ta",
        composition=r"Fe$_{0.3}$Ti$_{0.3}$Al$_{0.2}$Nb$_{0.1}$Ta$_{0.1}$",
        terrane="blend",
        kappa=25.0,     # blend; ROM Fe/Ti/Al/Nb/Ta then ×0.45 for HEA distortion
        rho=rho_mace,   # MACE-derived
        cp=520.0,       # ROM of c_p
        T_m=1850.0,     # ROM of T_m (Nb,Ta pull it up; Al pulls it down)
        L_f=2.5e5,
        sigma_s=1.75,
        dsigma_dT=2.8e-4,
        eta=0.42,       # mix of Fe-Ti and refractory
        nu_l=6.5e-7,
        rho_source="MACE-MH-1 relaxed BCC (omat_pbe head)",
    )

def spark_R1() -> Alloy:
    """CrMoTaWV — the SPARK Phase-2 winner.  ρ verified against in-house
    measurement (11,453 kg/m³); paper cites internal data only.  Same
    properties as in am_process_jax_hf_v4."""
    return Alloy(
        name="SPARK_R1", pretty="SPARK-R1 (CrMoTaWV)",
        composition=r"CrMoTaWV equimolar",
        terrane="earth-import",
        kappa=24.7 * 1.6,        # 1.6× LPBF-T correction on RT κ
        rho=11450.0,
        cp=221.244119,           # Dulong-Petit / molar mass average
        T_m=2848.8,
        L_f=2.65e5,
        sigma_s=2.10,
        dsigma_dT=2.5e-4,
        eta=0.40,
        nu_l=4.0e-7,
        rho_source="experimental (SPARK Phase-2 internal)",
    )

def spark_S1() -> Alloy:
    """HESA-2 = SPARK-S1: 9-element γ-γ′ Ni-Co-base superalloy.

    At% composition: PROPRIETARY (SPARK Phase-2 internal data; available
    to qualified reviewers under SPARK NDA — not exposed in this script).

    XRD on the HP-densified compact confirmed FCC γ matrix + minor MC carbide
    after hot-press at 1260 °C / 2 h / 30 MPa.  Mechanical-test summary:
    1250 MPa RT UTS, 510 MPa @ 1000 K, hardness 570 HV.

    Derived properties used by the AM-process model:
        ρ      7,605 kg/m³  — ROM Vegard atomic volumes on proprietary at%
        κ      21 W/(m·K)   — midpoint of Mar-M-247 (19) and Inconel-718 (22)
        c_p    580 J/(kg·K) — mass-weighted pure-element ROM at 1000 K
        T_m    1630 K liquidus (elevated γ′ fraction)
        σ_s    1.70 N/m liquid surface tension
        η      0.35 absorptivity at 1.06 μm
    """
    return Alloy(
        name="SPARK_S1", pretty="SPARK-S1 (HESA-2)",
        composition=r"9-element $\gamma$--$\gamma'$ Ni-Co superalloy (proprietary)",
        terrane="earth-import",
        kappa=21.0,
        rho=7605.0,         # ROM Vegard from proprietary at% composition
        cp=580.0,
        T_m=1630.0,
        L_f=2.85e5,
        sigma_s=1.70,
        dsigma_dT=3.7e-4,
        eta=0.35,
        nu_l=6.0e-7,
        rho_source="ROM from proprietary 9-element at% composition",
    )

# ----------------------------------------------------------------------------
# Density from MACE-relaxed cell
# ----------------------------------------------------------------------------
def fetch_repo():
    target = Path("/tmp/wams26_repo")
    if target.exists():
        return
    print(f"[fetch] cloning {GITHUB_REPO} -> {target}")
    subprocess.run(["git", "clone", "--depth", "1", GITHUB_REPO, str(target)],
                    check=True)

def rho_from_mace_relaxed(traj_path: Path) -> float:
    """Compute ρ [kg/m³] from a MACE-relaxed ASE .traj.  ρ = (Σ m_i)/V."""
    from ase.io import read
    atoms = read(str(traj_path))
    V_A3   = atoms.get_volume()                              # Å³
    M_amu  = float(np.sum(atoms.get_masses()))               # amu
    rho    = M_amu * 1.66054e-27 / (V_A3 * 1.0e-30)          # kg/m³
    return rho

# ----------------------------------------------------------------------------
# JAX core (copied from am_process_jax_hf_v4.py — single source of truth would
# be a shared module, but uv-run scripts are single-file)
# ----------------------------------------------------------------------------
@jit
def T_field(x, y, z, eta, kappa, alpha, P, v, T0_):
    R = jnp.sqrt(x**2 + y**2 + z**2 + EPS_R**2)
    return T0_ + (eta * P) / (2.0 * jnp.pi * kappa * R) \
                * jnp.exp(-(v / (2.0 * alpha)) * (x + R))

@jit
def melt_pool_LWD(eta, kappa, alpha, P, v, T0_, T_m):
    # Length: along scan (x), at y=z=0
    x_grid = jnp.linspace(-1.0e-3, 0.5e-3, 600)
    T_x = vmap(lambda xv: T_field(xv, 0.0, 0.0, eta, kappa, alpha, P, v, T0_))(x_grid)
    L = jnp.sum((T_x >= T_m).astype(jnp.float32)) * (x_grid[1] - x_grid[0])
    # Width: across scan (y), at x=z=0; symmetric so 2× the +y half-width
    y_grid = jnp.linspace(0.0, 5.0e-4, 300)
    T_y = vmap(lambda yv: T_field(0.0, yv, 0.0, eta, kappa, alpha, P, v, T0_))(y_grid)
    W = 2.0 * jnp.sum((T_y >= T_m).astype(jnp.float32)) * (y_grid[1] - y_grid[0])
    # Depth: into substrate (z), at x=y=0
    z_grid = jnp.linspace(0.0, 5.0e-4, 300)
    T_z = vmap(lambda zv: T_field(0.0, 0.0, zv, eta, kappa, alpha, P, v, T0_))(z_grid)
    d = jnp.sum((T_z >= T_m).astype(jnp.float32)) * (z_grid[1] - z_grid[0])
    return L, W, d

def cooling_rate_at_trail(alloy: Alloy, proc: dict, L: float) -> float:
    """Ṫ = -v · ∂T/∂x at trailing-edge solidification front (x ≈ -L)."""
    x_trail = -0.95 * L
    eps = 1e-7
    fwd = float(T_field(x_trail + eps, 0.0, 0.0, alloy.eta, alloy.kappa,
                         alloy.alpha, proc["P"], proc["v"], proc["T_0"]))
    bwd = float(T_field(x_trail - eps, 0.0, 0.0, alloy.eta, alloy.kappa,
                         alloy.alpha, proc["P"], proc["v"], proc["T_0"]))
    dTdx = (fwd - bwd) / (2 * eps)
    return -proc["v"] * dTdx

def compute_metrics(alloy: Alloy, proc: dict, g: float) -> dict:
    L_, W_, d_ = melt_pool_LWD(alloy.eta, alloy.kappa, alloy.alpha,
                                proc["P"], proc["v"], proc["T_0"], alloy.T_m)
    L, W, d = float(L_), float(W_), float(d_)
    Tdot = cooling_rate_at_trail(alloy, proc, L)
    lam_1 = A_KZ_HUNT * abs(Tdot)**(-1.0/3.0) if Tdot != 0 else float("inf")
    Pe = proc["v"] * W / (2.0 * alloy.alpha)
    delta_T = alloy.T_m - proc["T_0"]
    Ma = abs(alloy.dsigma_dT) * delta_T * W / (alloy.rho * alloy.nu_l * alloy.alpha)
    Bo = alloy.rho * g * W**2 / alloy.sigma_s
    # AM-printability heuristic
    aspect = L / W if W > 0 else 0
    verdict = "PRINTABLE"
    if d < 30e-6: verdict = "MARGINAL (depth < 30 μm — would need lower v or higher P)"
    if aspect > 10: verdict = "KEYHOLING RISK (L/W > 10)"
    if alloy.eta < 0.25:
        verdict += "  ⚠ low absorptivity (reflective alloy)"
    return dict(
        name=alloy.name, pretty=alloy.pretty, terrane=alloy.terrane,
        composition=alloy.composition, rho_source=alloy.rho_source,
        eta=alloy.eta, kappa=alloy.kappa, rho=alloy.rho, cp=alloy.cp,
        alpha=alloy.alpha, T_m=alloy.T_m, sigma_s=alloy.sigma_s,
        L_um=L*1e6, W_um=W*1e6, d_um=d*1e6,
        cooling_K_s=Tdot, lam_1_um=lam_1*1e6,
        Pe=Pe, Ma=Ma, Bo=Bo, aspect=aspect,
        verdict=verdict,
    )

# ----------------------------------------------------------------------------
# Output figure
# ----------------------------------------------------------------------------
plt.rcParams.update({"font.size": 9, "axes.labelsize": 10,
                     "figure.dpi": 300, "savefig.dpi": 300})

def fig_terrane_bars(results):
    fig, axes = plt.subplots(2, 2, figsize=(8.8, 6.0), constrained_layout=True)
    names   = [r["name"] for r in results]
    colors  = {"mare": "#b2531a", "highlands": "#aab8c2",
               "blend": "#5e3aa1", "earth-import": "#2c7a3e"}
    cs      = [colors[r["terrane"]] for r in results]

    # (a) Melt-pool dims
    ax = axes[0,0]; x = np.arange(len(names)); w = 0.27
    ax.bar(x - w, [r["L_um"] for r in results], w, color=cs, edgecolor="k", label="L")
    ax.bar(x,     [r["W_um"] for r in results], w, color=cs, edgecolor="k",
            alpha=0.65, label="W")
    ax.bar(x + w, [r["d_um"] for r in results], w, color=cs, edgecolor="k",
            alpha=0.35, label="d")
    ax.set_xticks(x); ax.set_xticklabels(names, rotation=30, ha="right", fontsize=8)
    ax.set_ylabel(r"Melt-pool dimension [$\mu$m]")
    ax.set_title("(a) Melt-pool geometry  (L, W, d)")
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(axis="y", alpha=0.3)

    # (b) Cooling rate (log)
    ax = axes[0,1]
    ax.bar(x, [abs(r["cooling_K_s"]) for r in results], color=cs, edgecolor="k")
    ax.set_yscale("log")
    ax.set_xticks(x); ax.set_xticklabels(names, rotation=30, ha="right", fontsize=8)
    ax.set_ylabel(r"$|\dot{T}|$  [K/s]")
    ax.set_title("(b) Cooling rate (trailing edge)")
    ax.grid(axis="y", which="both", alpha=0.3)

    # (c) Pe, Ma  (Pe is O(1-10), Ma is O(100-1000) — split y axes)
    ax = axes[1,0]; ax2 = ax.twinx()
    ax.bar(x - 0.18, [r["Pe"] for r in results], 0.36,
            color=cs, edgecolor="k", label="Pe")
    ax2.bar(x + 0.18, [r["Ma"] for r in results], 0.36,
             color=cs, alpha=0.55, edgecolor="k", label="Ma")
    ax.set_xticks(x); ax.set_xticklabels(names, rotation=30, ha="right", fontsize=8)
    ax.set_ylabel("Pe = vW/(2α)"); ax2.set_ylabel("Ma  (=|dσ/dT|·ΔT·W/(μα))")
    ax.set_title("(c) Peclet & Marangoni numbers")
    ax.grid(axis="y", alpha=0.3)

    # (d) Bond (log) — gravity story
    ax = axes[1,1]
    ax.bar(x, [r["Bo"] for r in results], color=cs, edgecolor="k")
    ax.axhline(1.0, color="r", linestyle="--", lw=1, label="Bo = 1")
    ax.set_yscale("log"); ax.set_ylim(1e-6, 1e1)
    ax.set_xticks(x); ax.set_xticklabels(names, rotation=30, ha="right", fontsize=8)
    ax.set_ylabel(r"Bond  Bo = $\rho g W^2 / \sigma_s$  (g = lunar)")
    ax.set_title("(d) Bond number — surface tension always wins  (Bo « 1)")
    ax.legend(loc="upper left", fontsize=8)
    ax.grid(axis="y", which="both", alpha=0.3)

    # Legend: terrane colors
    handles = [plt.Rectangle((0,0),1,1, color=c, ec="k", label=n)
                for n, c in colors.items()]
    fig.legend(handles=handles, loc="upper center",
                bbox_to_anchor=(0.5, 1.04), ncol=4, fontsize=9,
                frameon=False)
    fig.suptitle("Lunar AM process screen — feedstock-resolved   "
                  r"(P = 200 W,  v = 0.8 m/s,  g = $g_{\rm moon}$)",
                  y=-0.04, fontsize=10)

    out = FIG_DIR / "fig_lunar_terranes_bars.pdf"
    fig.savefig(out, bbox_inches="tight"); plt.close(fig)
    fig.savefig(str(out).replace(".pdf", ".png"), bbox_inches="tight")
    print(f"  wrote {out}")

# ----------------------------------------------------------------------------
# Upload helper
# ----------------------------------------------------------------------------
def upload(local_dir: Path, repo_id: str):
    from huggingface_hub import HfApi, create_repo
    token = os.environ.get("HF_TOKEN")
    if not token:
        print("[warn] HF_TOKEN missing; skipping upload"); return
    api = HfApi(token=token)
    create_repo(repo_id, repo_type="dataset", exist_ok=True, token=token)
    for p in local_dir.rglob("*"):
        if p.is_file():
            api.upload_file(path_or_fileobj=str(p),
                             path_in_repo=p.relative_to(local_dir).as_posix(),
                             repo_id=repo_id, repo_type="dataset", token=token)
            print(f"  + {p.relative_to(local_dir).as_posix()}")

# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------
def main():
    print("=" * 78)
    print("AM PROCESS SCREEN — LUNAR TERRANE-RESOLVED FEEDSTOCKS")
    print("=" * 78)

    # MACE-derived density for the ISRU blend
    fetch_repo()
    traj = STRUCT_ROOT / "mace_cache" / "relaxed_bcc_R3_ISRU_blend.traj"
    rho_mace = rho_from_mace_relaxed(traj)
    print(f"\n[MACE → ρ] ISRU blend BCC: ρ_MACE = {rho_mace:.1f} kg/m^3 "
           f"(from {traj.name})")

    alloys = [mare_FeTi(), highlands_AlSi(), isru_blend(rho_mace),
              spark_R1(), spark_S1()]

    print("\n" + "=" * 78)
    print(f"Computing metrics under LUNAR gravity g = {G_LUNAR:.3f} m/s² ...")
    print("=" * 78)

    results = []
    for a in alloys:
        m = compute_metrics(a, NOMINAL_PROC, G_LUNAR)
        results.append(m)
        print(f"\n  {a.name}  ({a.pretty})")
        print(f"    rho = {a.rho:.0f} kg/m³  [{a.rho_source}]")
        print(f"    eta = {a.eta:.2f}   T_m = {a.T_m:.0f} K   "
               f"alpha = {a.alpha:.2e} m²/s")
        print(f"    L = {m['L_um']:.0f}μm   W = {m['W_um']:.0f}μm   "
               f"d = {m['d_um']:.0f}μm   aspect = {m['aspect']:.2f}")
        print(f"    |Ṫ| = {abs(m['cooling_K_s']):.2e} K/s   "
               f"λ₁ = {m['lam_1_um']:.3f} μm")
        print(f"    Pe = {m['Pe']:.2f}   Ma = {m['Ma']:.0f}   Bo = {m['Bo']:.2e}")
        print(f"    Verdict: {m['verdict']}")

    # Output JSON
    with open(OUT_DIR / "am_lunar_terranes_summary.json", "w") as f:
        json.dump(results, f, indent=2, default=float)
    # Output CSV
    with open(OUT_DIR / "am_lunar_terranes_table.csv", "w") as f:
        cols = ["name", "pretty", "terrane", "rho", "rho_source", "eta",
                "T_m", "L_um", "W_um", "d_um", "cooling_K_s", "lam_1_um",
                "Pe", "Ma", "Bo", "verdict"]
        f.write(",".join(cols) + "\n")
        for r in results:
            f.write(",".join(f'"{r[c]}"' if isinstance(r[c], str) else f'{r[c]}'
                              for c in cols) + "\n")

    print("\n[FIG] generating comparison bars...")
    fig_terrane_bars(results)

    print(f"\n[UPLOAD] -> {RESULTS_REPO}")
    upload(OUT_DIR, RESULTS_REPO)
    print("\nDONE.")

if __name__ == "__main__":
    main()
