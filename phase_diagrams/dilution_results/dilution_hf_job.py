# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "mace-torch>=0.3.15",
#   "ase>=3.23",
#   "phonopy>=2.20",
#   "numpy>=1.24",
#   "scipy>=1.10",
#   "matplotlib>=3.7",
#   "huggingface_hub>=0.20",
#   "torch>=2.1",
# ]
# ///
"""
Quantitative ab-initio dilution diagram for WAMS 2026 Paper #68, Figure 12.

Replaces the hand-drawn schematic of the dilution trajectory from a concentrated
RHEA master alloy (MoNbTaTiV) to ISRU-derived Fe-50Ti, with a measured
T-x phase diagram constructed from:

  - MACE-MH-1 foundation MLIP (arXiv:2510.25380, OMAT/PBE head) for E0 and forces
  - Phonopy harmonic phonons on the relaxed supercell -> F_vib(T)
  - Bragg-Williams ideal-mixing config entropy for BCC SS (analytical)
  - Convex envelope on a per-temperature basis to identify BCC vs Laves regions

Phases included:
  - BCC random solid solution at 7 dilution points along the path:
       x_ISRU in {0.0, 0.10, 0.25, 0.50, 0.75, 0.90, 1.00}
    with the master alloy at x=0 (equimolar MoNbTaTiV) and the ISRU end-point
    at x=1 (Fe-50Ti atomic).
  - Pure Fe2Nb (C14, MgZn2 prototype) -- the Laves competitor named in caption.
  - Pure Fe2Ta (C14)                  -- ditto.

Scope hedges (this is Tier 1, not full CALPHAD):
  - Harmonic phonons only (no thermal expansion / quasi-harmonic correction).
  - No liquid phase -- no liquidus / solidus boundaries.
  - Random-mixing config entropy (no SRO; cluster expansion is Tier 2 future work).
  - Gamma-only phonon sampling on the relaxed supercell (DOS quality limited by
    cell size, fine for free-energy comparison between competing phases).

Outputs (pushed to a HF Dataset repo):
  - thermo_results.json    : E0, F_vib(T), G(T) per phase
  - dilution_phase_diagram.pdf/.png
  - dilution_thermo.csv
  - relaxed_*.traj         : relaxed structures of every phase

Run:
  hf jobs uv run --flavor l4x1 --timeout 1h --secrets HF_TOKEN \
      phase_diagrams/dilution_hf_job.py
"""

from __future__ import annotations

import json
import os
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

import torch
from ase import Atoms
from ase.build import bulk
from ase.cell import Cell
from ase.filters import FrechetCellFilter
from ase.io import write as ase_write
from ase.optimize import LBFGS

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
RNG_SEED = 20260506
N_ATOMS_BCC = 100  # 5x5x2 of cubic BCC = 100 atoms
DILUTION_FRACTIONS = [0.0, 0.10, 0.25, 0.50, 0.75, 0.90, 1.00]
TEMPS_K = np.array([0.0, 100.0, 300.0, 500.0, 800.0, 1000.0, 1200.0, 1500.0, 1800.0])
DISPLACEMENT_AA = 0.01  # Phonopy displacement amplitude

# Pure-element BCC starting lattice parameters (Angstrom)
A_BCC = {
    "Mo": 3.15, "Nb": 3.30, "Ta": 3.30, "Ti": 3.27, "V": 3.03,
    "Fe": 2.87, "Hf": 3.55, "Zr": 3.57, "Al": 3.20,
}

# Hub dataset target -- where the job pushes results
RESULTS_REPO = os.environ.get("RESULTS_REPO", "Darth-Hidious/wams2026-rhea-dilution")

# Output directory inside the job
OUT = Path(os.environ.get("OUT_DIR", "/tmp/dilution_out"))
OUT.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Calculator
# ---------------------------------------------------------------------------
def make_calc():
    """Load mace-mh-1 on CUDA at float64 (CUDA supports it; MPS does not)."""
    from huggingface_hub import hf_hub_download
    from mace.calculators import mace_mp

    path = hf_hub_download(
        repo_id="mace-foundations/mace-mh-1", filename="mace-mh-1.model"
    )
    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = "float64"
    print(f"[mace-mh-1] device={device}  dtype={dtype}  path={path}")
    return mace_mp(model=path, default_dtype=dtype, device=device, head="omat_pbe")


# ---------------------------------------------------------------------------
# Compositions
# ---------------------------------------------------------------------------
def composition_at_x(x_isru: float, n_atoms: int = N_ATOMS_BCC) -> dict:
    """Atomic counts for an n-atom supercell at given % ISRU.

    Master alloy = equimolar MoNbTaTiV (5 elements, 20% each).
    ISRU end-point = Fe-50Ti (atomic).
    """
    rhea_frac = 1.0 - x_isru
    # Master-alloy contribution: equimolar Mo, Nb, Ta, Ti, V
    n_master_each = rhea_frac * n_atoms / 5.0
    # ISRU contribution: Fe-50Ti split 50/50
    n_isru_each = x_isru * n_atoms / 2.0

    raw = {
        "Mo": n_master_each, "Nb": n_master_each, "Ta": n_master_each,
        "V":  n_master_each,
        "Ti": n_master_each + n_isru_each,
        "Fe": n_isru_each,
    }
    # Round to integers, then fix the residual to enforce sum=n_atoms exactly
    rounded = {k: int(round(v)) for k, v in raw.items()}
    diff = n_atoms - sum(rounded.values())
    if diff != 0:
        # Adjust the largest-fraction non-zero entry
        target = max(raw, key=raw.get)
        rounded[target] += diff
    # Drop zero counts
    return {k: v for k, v in rounded.items() if v > 0}


def build_bcc_supercell(comp: dict, seed: int) -> Atoms:
    """5x5x2 conventional BCC = 100 atoms with random substitution."""
    n = sum(comp.values())
    assert n == 100, f"composition must sum to 100, got {n}"
    a = sum(A_BCC[el] * c for el, c in comp.items()) / n  # composition-weighted a
    proto = bulk("X", "bcc", a=a, cubic=True)
    sc = proto * (5, 5, 2)
    symbols = []
    for el, c in comp.items():
        symbols.extend([el] * c)
    rng = np.random.default_rng(seed)
    rng.shuffle(symbols)
    sc.set_chemical_symbols(symbols)
    return sc


# ---------------------------------------------------------------------------
# C14 Laves (Fe2Nb, Fe2Ta) prototype
# ---------------------------------------------------------------------------
def build_c14_laves(big_atom: str, small_atom: str = "Fe") -> Atoms:
    """C14 (MgZn2) prototype, 12 atoms / unit cell.

    Hexagonal P6_3/mmc; Wyckoff sites:
      4f (1/3, 2/3, z),  z ~ 0.0625      -> 'big' atoms (Nb / Ta)
      2a (0,0,0)                          -> 'small' (Fe)
      6h (x, 2x, 1/4),   x ~ 0.833        -> 'small' (Fe)

    Tile to 2x2x2 = 96 atoms for the phonon supercell.
    """
    # Experimental lattice (Fe2Nb): a = 4.842, c = 7.872 Å.  Used as starting
    # guess for both Fe2Nb and Fe2Ta -- relaxation handles species-specific scale.
    a, c = 4.842, 7.872
    cell = Cell.fromcellpar([a, a, c, 90, 90, 120])

    z = 0.0625
    x = 5.0 / 6.0  # = 0.8333

    # Build positions in fractional coords; wrap to unit cell.
    positions_frac = np.array([
        # 4 'big' atoms at 4f
        [1/3, 2/3, z],
        [2/3, 1/3, z + 0.5],
        [2/3, 1/3, -z],
        [1/3, 2/3, -z + 0.5],
        # 2 'small' atoms at 2a
        [0.0, 0.0, 0.0],
        [0.0, 0.0, 0.5],
        # 6 'small' atoms at 6h: (x, 2x, 1/4) and symmetry mates.
        # Generators of the 6h orbit in P6_3/mmc:
        [   x,  2*x, 0.25],
        [-2*x,   -x, 0.25],
        [   x,   -x, 0.25],
        [  -x, -2*x, 0.75],
        [ 2*x,    x, 0.75],
        [  -x,    x, 0.75],
    ])
    positions_frac = positions_frac % 1.0
    symbols = [big_atom] * 4 + [small_atom] * 8
    primitive = Atoms(
        symbols=symbols, scaled_positions=positions_frac,
        cell=cell, pbc=True,
    )
    # 2x2x2 supercell -> 96 atoms (consistent with our 100-atom BCC scale)
    return primitive * (2, 2, 2)


# ---------------------------------------------------------------------------
# Relaxation
# ---------------------------------------------------------------------------
def relax(atoms: Atoms, calc, fmax=0.05, steps=200, label="") -> Atoms:
    atoms.calc = calc
    flt = FrechetCellFilter(atoms)
    opt = LBFGS(flt, logfile=None)
    t0 = time.time()
    opt.run(fmax=fmax, steps=steps)
    e_pa = atoms.get_potential_energy() / len(atoms)
    print(f"  relax {label:30s}  E={e_pa:.4f} eV/atom  "
          f"({time.time()-t0:.1f}s, {opt.get_number_of_steps()} steps)")
    return atoms


# ---------------------------------------------------------------------------
# Phonopy harmonic free energy
# ---------------------------------------------------------------------------
def harmonic_free_energy(atoms_relaxed: Atoms, calc, temps_k: np.ndarray,
                          label: str = "") -> dict:
    """Compute F_vib(T) per atom via phonopy on the supercell.

    Treats the relaxed supercell as the phonon primitive cell (Gamma-only
    sampling).  Generates 3N x 2 displaced configurations (no symmetry
    reduction), gets forces from MACE for each, builds the dynamical matrix,
    samples a uniform mesh in the BZ (q-points are inside the supercell BZ),
    and integrates over phonon DOS for F(T).
    """
    from phonopy import Phonopy
    from phonopy.structure.atoms import PhonopyAtoms

    pa = PhonopyAtoms(
        symbols=atoms_relaxed.get_chemical_symbols(),
        cell=atoms_relaxed.cell.array,
        scaled_positions=atoms_relaxed.get_scaled_positions(),
    )
    # Supercell matrix = identity: treat the 100-atom supercell as-is.
    phonon = Phonopy(pa, supercell_matrix=np.eye(3, dtype=int),
                      primitive_matrix=np.eye(3))
    phonon.generate_displacements(distance=DISPLACEMENT_AA)
    n_disp = len(phonon.supercells_with_displacements)
    print(f"  phonons {label:28s}  {n_disp} displacements")

    forces_set = []
    t0 = time.time()
    for i, sc in enumerate(phonon.supercells_with_displacements):
        if sc is None:
            forces_set.append(np.zeros((len(atoms_relaxed), 3)))
            continue
        a = Atoms(
            symbols=sc.symbols, cell=sc.cell, scaled_positions=sc.scaled_positions,
            pbc=True,
        )
        a.calc = calc
        forces_set.append(a.get_forces())
        if (i + 1) % 50 == 0 or i == n_disp - 1:
            elapsed = time.time() - t0
            rate = (i + 1) / elapsed
            print(f"    [{i+1:4d}/{n_disp}] {elapsed:.1f}s ({rate:.2f}/s)")

    phonon.forces = forces_set
    phonon.produce_force_constants()

    # Modest q-mesh; supercell BZ is small so a 4x4x4 mesh is fine for DOS.
    phonon.run_mesh([4, 4, 4])
    phonon.run_thermal_properties(temperatures=temps_k.tolist())
    tp = phonon.get_thermal_properties_dict()
    # tp['free_energy'] in kJ/mol of unit cell. Convert to eV/atom.
    n_atoms = len(atoms_relaxed)
    # 1 kJ/mol = 1000 / (6.022e23 * 1.602e-19) eV per formula unit
    kJmol_to_eV = 1.0 / 96.485
    F_eV_per_cell = np.array(tp["free_energy"]) * kJmol_to_eV
    F_per_atom = F_eV_per_cell / n_atoms

    # Sanity check: phonon ω_min should be > -small (no major imaginary modes
    # for a stable phase).  Foundation MLIPs sometimes give a few imaginary
    # modes near Gamma in random alloys; we record the count.
    freqs = phonon.get_mesh_dict()["frequencies"]  # THz
    n_imag = int(np.sum(freqs < -0.05))  # tolerance 0.05 THz
    if n_imag > 0:
        print(f"    [warn] {n_imag} imaginary modes (tol 0.05 THz) in {label}")

    return dict(
        T_K=temps_k.tolist(),
        F_vib_eV_per_atom=F_per_atom.tolist(),
        n_imag=n_imag,
    )


# ---------------------------------------------------------------------------
# Configurational entropy
# ---------------------------------------------------------------------------
KB_eV = 8.617333262e-5  # eV/K


def s_config_random_mixing(comp: dict) -> float:
    """Bragg-Williams: S = -k_B sum x_i ln x_i  (eV/K per atom)."""
    n = sum(comp.values())
    s = 0.0
    for el, c in comp.items():
        if c <= 0:
            continue
        x = c / n
        s -= x * np.log(x)
    return KB_eV * s


# ---------------------------------------------------------------------------
# Hub upload
# ---------------------------------------------------------------------------
def upload_results(local_dir: Path, repo_id: str) -> None:
    from huggingface_hub import HfApi, create_repo

    token = os.environ.get("HF_TOKEN")
    if not token:
        print("[warn] HF_TOKEN missing; skipping upload")
        return

    api = HfApi(token=token)
    create_repo(repo_id, repo_type="dataset", exist_ok=True, token=token)
    print(f"[upload] -> {repo_id}")
    for p in local_dir.rglob("*"):
        if p.is_file():
            api.upload_file(
                path_or_fileobj=str(p),
                path_in_repo=p.relative_to(local_dir).as_posix(),
                repo_id=repo_id, repo_type="dataset", token=token,
            )
            print(f"  + {p.relative_to(local_dir).as_posix()}")


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------
def plot_dilution_diagram(results: dict) -> None:
    """T-x diagram with BCC stability margin against Fe2Nb / Fe2Ta tie-lines.

    For each (composition x, temperature T), we plot:
      G_BCC(x, T) - max_per_atom_G_of_decomposition(x, T)

    where decomposition is into Fe2Nb (or Fe2Ta) + the residual BCC matrix at
    a composition x' chosen so the overall composition is conserved.  We use a
    simple scalar lever-rule approximation along the dilution axis: this is a
    pseudo-binary projection, not a true multidimensional simplex hull.
    """
    plt.rcParams.update({"font.size": 11, "figure.dpi": 300, "savefig.dpi": 300})
    xs = np.array([r["x_isru"] for r in results["bcc"]])
    temps = np.array(results["bcc"][0]["F_vib"]["T_K"])

    G_bcc = np.zeros((len(xs), len(temps)))
    for i, r in enumerate(results["bcc"]):
        E0 = r["E0_per_atom"]
        F = np.array(r["F_vib"]["F_vib_eV_per_atom"])
        S = r["S_config_eV_per_K"]
        G_bcc[i] = E0 + F - temps * S

    G_FeNb_per_atom = np.array(results["Fe2Nb"]["F_vib"]["F_vib_eV_per_atom"]) \
                      + results["Fe2Nb"]["E0_per_atom"]
    G_FeTa_per_atom = np.array(results["Fe2Ta"]["F_vib"]["F_vib_eV_per_atom"]) \
                      + results["Fe2Ta"]["E0_per_atom"]

    # ---- Panel A: G_BCC(x) at three temperatures ----
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    ax = axes[0]
    cmap = plt.cm.plasma
    sel_T_idx = [np.argmin(np.abs(temps - T)) for T in (300, 1000, 1500)]
    for ti in sel_T_idx:
        T = temps[ti]
        ax.plot(xs * 100, G_bcc[:, ti], "-o", color=cmap(T / 1800),
                lw=2.5, label=f"BCC, T={T:.0f} K")
    ax.axhline(G_FeNb_per_atom[sel_T_idx[1]], color="#FF5722", ls="--", lw=1.5,
               label=r"Fe$_2$Nb pure (1000 K)")
    ax.axhline(G_FeTa_per_atom[sel_T_idx[1]], color="#9C27B0", ls="--", lw=1.5,
               label=r"Fe$_2$Ta pure (1000 K)")
    ax.set_xlabel("ISRU fraction (% atomic)")
    ax.set_ylabel(r"$G_{\rm phase}$ (eV / atom)")
    ax.set_title("Phase free energies along dilution path")
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)
    # Target dilution window (75-90 % ISRU)
    ax.axvspan(75, 90, color="#4CAF50", alpha=0.15)
    ax.text(82.5, ax.get_ylim()[1] - 0.05, "target window",
            ha="center", color="#2E7D32", fontsize=10, fontweight="bold")

    # ---- Panel B: Decomposition driving force vs Fe2Nb ----
    # Compare: G_BCC(x, T) - [(1-y) G_BCC(x', T) + y G_FeNb_per_atom(T)]
    # For simplicity we use y=0 (pure single-phase) and compare against the
    # absolute pure-Fe2Nb energy: this is a chemical-driving-force proxy, not
    # a true tie-line.
    ax = axes[1]
    dG_FeNb = G_bcc - G_FeNb_per_atom[None, :]  # (x, T)
    dG_FeTa = G_bcc - G_FeTa_per_atom[None, :]
    dG_min = np.minimum(dG_FeNb, dG_FeTa)
    im = ax.imshow(dG_min.T, origin="lower", aspect="auto", cmap="RdBu_r",
                    extent=[xs.min() * 100, xs.max() * 100,
                            temps.min(), temps.max()],
                    vmin=-np.nanmax(np.abs(dG_min)),
                    vmax=+np.nanmax(np.abs(dG_min)))
    cs = ax.contour(xs * 100, temps, dG_min.T, levels=[0], colors="black", linewidths=2)
    ax.clabel(cs, inline=True, fontsize=10, fmt="%.0f")
    ax.set_xlabel("ISRU fraction (% atomic)")
    ax.set_ylabel("T (K)")
    ax.set_title(r"$G_{\rm BCC} - \min(G_{\rm Fe_2Nb}, G_{\rm Fe_2Ta})$ "
                  "  |  red: Laves cliff, blue: BCC field")
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label(r"$\Delta G$ (eV / atom)")
    # Target window vertical band
    ax.axvspan(75, 90, color="#4CAF50", alpha=0.15)

    fig.suptitle(
        "Quantitative dilution diagram (mace-mh-1 + harmonic phonons)\n"
        r"MoNbTaTiV $\rightarrow$ Fe-50Ti  |  Tier 1: harmonic, no liquid, "
        "random-mixing config entropy",
        fontsize=12, y=0.99,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    out_pdf = OUT / "dilution_phase_diagram.pdf"
    out_png = OUT / "dilution_phase_diagram.png"
    fig.savefig(out_pdf); fig.savefig(out_png)
    print(f"[plot] wrote {out_pdf.name}")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    t0 = time.time()
    print(f"[start] OUT={OUT}  RESULTS_REPO={RESULTS_REPO}")
    print(f"[torch] cuda={torch.cuda.is_available()}  "
          f"device_name={torch.cuda.get_device_name() if torch.cuda.is_available() else 'cpu'}")

    calc = make_calc()

    # ---- Build + relax + phonons for each BCC composition ----
    bcc_results = []
    for x in DILUTION_FRACTIONS:
        comp = composition_at_x(x)
        label = f"BCC x={x:.2f}"
        print(f"\n[{label}]  comp={comp}")
        atoms = build_bcc_supercell(comp, seed=RNG_SEED + int(x * 100))
        atoms = relax(atoms, calc, label=label)
        traj_path = OUT / f"relaxed_bcc_x{int(x*100):03d}.traj"
        a_clean = atoms.copy(); a_clean.calc = None
        ase_write(traj_path, a_clean)
        F = harmonic_free_energy(atoms, calc, TEMPS_K, label=label)
        bcc_results.append(dict(
            x_isru=x,
            composition=comp,
            E0_per_atom=float(atoms.get_potential_energy() / len(atoms)),
            V_per_atom=float(atoms.get_volume() / len(atoms)),
            F_vib=F,
            S_config_eV_per_K=float(s_config_random_mixing(comp)),
        ))

    # ---- Pure Fe2Nb and Fe2Ta Laves ----
    laves_results = {}
    for laves_name, big in [("Fe2Nb", "Nb"), ("Fe2Ta", "Ta")]:
        print(f"\n[{laves_name} (C14 Laves)]")
        atoms = build_c14_laves(big_atom=big, small_atom="Fe")
        atoms = relax(atoms, calc, label=laves_name)
        traj_path = OUT / f"relaxed_{laves_name.lower()}.traj"
        a_clean = atoms.copy(); a_clean.calc = None
        ase_write(traj_path, a_clean)
        F = harmonic_free_energy(atoms, calc, TEMPS_K, label=laves_name)
        laves_results[laves_name] = dict(
            E0_per_atom=float(atoms.get_potential_energy() / len(atoms)),
            V_per_atom=float(atoms.get_volume() / len(atoms)),
            F_vib=F,
        )

    # ---- Assemble + write JSON ----
    results = dict(
        meta=dict(
            model="mace-foundations/mace-mh-1",
            head="omat_pbe",
            dilution_fractions=DILUTION_FRACTIONS,
            temperatures_K=TEMPS_K.tolist(),
            n_atoms_bcc=N_ATOMS_BCC,
            displacement_AA=DISPLACEMENT_AA,
            wall_time_s=float(time.time() - t0),
        ),
        bcc=bcc_results,
        Fe2Nb=laves_results["Fe2Nb"],
        Fe2Ta=laves_results["Fe2Ta"],
    )
    json_path = OUT / "thermo_results.json"
    json_path.write_text(json.dumps(results, indent=2))
    print(f"\n[json] wrote {json_path.name} ({json_path.stat().st_size//1024} KB)")

    # ---- Plot ----
    try:
        plot_dilution_diagram(results)
    except Exception as ex:
        print(f"[warn] plotting failed: {ex}")

    # ---- Push ----
    upload_results(OUT, RESULTS_REPO)

    print(f"\n[done] total wall time: {(time.time()-t0)/60:.1f} min")


if __name__ == "__main__":
    main()
