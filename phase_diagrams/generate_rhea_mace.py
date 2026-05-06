#!/usr/bin/env python3
"""
RHEA ab-initio phase / solute-dissolution analysis for WAMS 2026 Paper #68.

Complements generate_rhea.py (COST507 CALPHAD), which the paper itself flags
as indicative-only because COST507 lacks binary interaction parameters for
most refractory pairs. This script provides foundation-MLIP (MACE-MH-1)
energies that do not depend on CALPHAD assessments.

Three deliverables for each of the paper's RHEA compositions:
  1. T = 0 K BCC vs FCC vs HCP phase competition (formation enthalpy / atom)
  2. Dilute Fe / Ti / Al substitution energy in each matrix (ISRU question)
  3. Finite-T NPT MD on the ISRU blend at 1000 / 1500 / 2000 K
     (lattice parameter, energy, RDF — checks BCC stability under regolith
      contamination)

Compositions match phase_diagrams/generate_rhea.py:
  R1: HfNbTaTiZr  equimolar (Senkov 2011 baseline)
  R2: MoNbTaTiV   equimolar (Cao 2019 / SPS route)
  R3: Fe0.3 Ti0.3 Al0.2 Nb0.1 Ta0.1  (ISRU blend)

Model: mace-foundations/mace-mh-1 (arXiv:2510.25380), OMAT/PBE head.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
import warnings
from dataclasses import asdict, dataclass

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from ase import Atoms
from ase.build import bulk
from ase.optimize import LBFGS
from ase.filters import FrechetCellFilter
from ase.md.langevin import Langevin
from ase.md.velocitydistribution import MaxwellBoltzmannDistribution
from ase import units
from ase.io import read as ase_read, write as ase_write
from ase.visualize.plot import plot_atoms

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# Paths and constants
# ---------------------------------------------------------------------------
OUTDIR = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.abspath(os.path.join(OUTDIR, "..", "figures"))
SLIDEDIR = os.path.join(FIGDIR, "presentation")
CACHEDIR = os.path.join(OUTDIR, "mace_cache")
os.makedirs(FIGDIR, exist_ok=True)
os.makedirs(SLIDEDIR, exist_ok=True)
os.makedirs(CACHEDIR, exist_ok=True)

RNG_SEED = 20260506  # fixed for reproducibility

# Reasonable starting lattice parameters (Å)
A_BCC = {"Hf": 3.55, "Nb": 3.30, "Ta": 3.30, "Ti": 3.27, "Zr": 3.57,
         "Mo": 3.15, "V": 3.03, "Fe": 2.87, "Al": 3.20}
A_FCC = {"Hf": 4.50, "Nb": 4.20, "Ta": 4.20, "Ti": 4.13, "Zr": 4.50,
         "Mo": 4.00, "V": 3.83, "Fe": 3.65, "Al": 4.05}
A_HCP = {"Hf": 3.20, "Nb": 2.85, "Ta": 2.85, "Ti": 2.95, "Zr": 3.23,
         "Mo": 2.74, "V": 2.62, "Fe": 2.51, "Al": 2.86}
COA = 1.633  # ideal HCP

PHASES = ("bcc", "fcc", "hcp")

# Composition definitions: dict of element -> integer atom count (sum = N_atoms)
# Using N=100 keeps MD tractable while exact integer composition holds.
COMPOSITIONS = {
    "R1_HfNbTaTiZr": {"Hf": 20, "Nb": 20, "Ta": 20, "Ti": 20, "Zr": 20},
    "R2_MoNbTaTiV":  {"Mo": 20, "Nb": 20, "Ta": 20, "Ti": 20, "V":  20},
    "R3_ISRU_blend": {"Fe": 30, "Ti": 30, "Al": 20, "Nb": 10, "Ta": 10},
}
COMP_TITLES = {
    "R1_HfNbTaTiZr": "HfNbTaTiZr (equimolar)",
    "R2_MoNbTaTiV":  "MoNbTaTiV (equimolar)",
    "R3_ISRU_blend": r"Fe$_{0.3}$Ti$_{0.3}$Al$_{0.2}$Nb$_{0.1}$Ta$_{0.1}$ (ISRU blend)",
}

# ---------------------------------------------------------------------------
# Calculator
# ---------------------------------------------------------------------------
def make_calc():
    from huggingface_hub import hf_hub_download
    from mace.calculators import mace_mp
    path = hf_hub_download(repo_id="mace-foundations/mace-mh-1",
                           filename="mace-mh-1.model")
    return mace_mp(model=path, default_dtype="float64",
                   device="cpu", head="omat_pbe")


# ---------------------------------------------------------------------------
# Supercell builders
# ---------------------------------------------------------------------------
def _avg_a(comp: dict, table: dict) -> float:
    n = sum(comp.values())
    return sum(table[el] * c for el, c in comp.items()) / n


def build_supercell(comp: dict, phase: str, rng: np.random.Generator) -> Atoms:
    """Build a 100-atom supercell of `phase` with composition `comp`.

    Random substitution from a fixed RNG. Lattice parameter = composition-
    weighted average of pure-element values; subsequent cell relaxation
    handles the actual minimum.
    """
    n_atoms = sum(comp.values())
    assert n_atoms == 100, "Composition must sum to 100 atoms"

    # Symbol pool — one entry per atom, then shuffled
    symbols = []
    for el, c in comp.items():
        symbols.extend([el] * c)
    symbols = np.array(symbols, dtype=object)
    rng.shuffle(symbols)

    if phase == "bcc":
        a = _avg_a(comp, A_BCC)
        # 2 atoms / conventional cubic cell -> 5x5x2 = 100 atoms
        proto = bulk("X", "bcc", a=a, cubic=True)
        sc = proto * (5, 5, 2)
    elif phase == "fcc":
        a = _avg_a(comp, A_FCC)
        # 4 atoms / conventional cell -> 5x5x1 = 100 atoms
        proto = bulk("X", "fcc", a=a, cubic=True)
        sc = proto * (5, 5, 1)
    elif phase == "hcp":
        a = _avg_a(comp, A_HCP)
        c = a * COA
        # 2 atoms / primitive HCP -> 5x5x2 = 100 atoms
        proto = bulk("X", "hcp", a=a, c=c)
        sc = proto * (5, 5, 2)
    else:
        raise ValueError(phase)

    assert len(sc) == 100, f"{phase} supercell has {len(sc)} atoms, expected 100"
    sc.set_chemical_symbols(list(symbols))
    return sc


# ---------------------------------------------------------------------------
# Pure-element references (for formation energies)
# ---------------------------------------------------------------------------
def pure_element_energy(symbol: str, calc) -> float:
    """Energy per atom of pure element in its conventional ground state.

    Approximate ground states (good enough as a reference for ΔH_f
    differences between competing phases of the same alloy):
      Fe -> bcc, Al -> fcc, others (refractories) -> bcc, Ti/Zr/Hf -> hcp.
    """
    gs = {"Fe": "bcc", "Al": "fcc", "Mo": "bcc", "Nb": "bcc", "Ta": "bcc",
          "V": "bcc", "Ti": "hcp", "Zr": "hcp", "Hf": "hcp"}[symbol]
    if gs == "bcc":
        a = A_BCC[symbol]
        atoms = bulk(symbol, "bcc", a=a, cubic=True) * (3, 3, 3)
    elif gs == "fcc":
        a = A_FCC[symbol]
        atoms = bulk(symbol, "fcc", a=a, cubic=True) * (3, 3, 3)
    else:
        a = A_HCP[symbol]
        atoms = bulk(symbol, "hcp", a=a, c=a * COA) * (3, 3, 3)
    atoms.calc = calc
    relax(atoms, fmax=0.02, steps=80, label=f"  ref:{symbol}")
    return atoms.get_potential_energy() / len(atoms)


# ---------------------------------------------------------------------------
# Relaxation
# ---------------------------------------------------------------------------
def relax(atoms: Atoms, fmax: float = 0.05, steps: int = 200,
          label: str = "") -> None:
    flt = FrechetCellFilter(atoms)
    opt = LBFGS(flt, logfile=None)
    t0 = time.time()
    opt.run(fmax=fmax, steps=steps)
    if label:
        e = atoms.get_potential_energy() / len(atoms)
        print(f"{label}  E={e:.4f} eV/atom  ({time.time()-t0:.1f}s, "
              f"{opt.get_number_of_steps()} steps)")


# ---------------------------------------------------------------------------
# Phase 1: T=0 phase competition
# ---------------------------------------------------------------------------
@dataclass
class PhaseResult:
    composition: str
    phase: str
    e_per_atom: float
    v_per_atom: float
    a_relaxed: float


def run_static_phase_competition(calc, mu: dict) -> list[PhaseResult]:
    print("\n=== Phase 1: T=0 BCC/FCC/HCP competition ===")
    results: list[PhaseResult] = []

    for comp_name, comp in COMPOSITIONS.items():
        print(f"\n[{comp_name}]")
        for phase in PHASES:
            local_rng = np.random.default_rng(RNG_SEED + hash(comp_name) % 10000)
            atoms = build_supercell(comp, phase, local_rng)
            atoms.calc = calc
            relax(atoms, fmax=0.05, steps=150, label=f"  {phase}")
            e_pa = atoms.get_potential_energy() / len(atoms)
            v_pa = atoms.get_volume() / len(atoms)
            atoms_per_cell = {"bcc": 2, "fcc": 4, "hcp": 2}[phase]
            a_eff = (v_pa * atoms_per_cell) ** (1 / 3)
            results.append(PhaseResult(comp_name, phase, e_pa, v_pa, a_eff))
            # Save the relaxed structure (without calculator state)
            traj = os.path.join(CACHEDIR, f"relaxed_{phase}_{comp_name}.traj")
            atoms_clean = atoms.copy()
            atoms_clean.calc = None
            ase_write(traj, atoms_clean)
    return results


def formation_energy(e_pa: float, comp: dict, mu: dict) -> float:
    """Formation enthalpy per atom relative to pure-element references."""
    n = sum(comp.values())
    e_ref = sum(comp[el] * mu[el] for el in comp) / n
    return e_pa - e_ref


# ---------------------------------------------------------------------------
# Phase 2: Solute dissolution
# ---------------------------------------------------------------------------
@dataclass
class SoluteResult:
    matrix: str
    solute: str
    displaced: str
    e_sub: float  # eV per substitution


def run_solute_dissolution(calc, mu: dict,
                            relaxed_bcc: dict[str, Atoms]) -> list[SoluteResult]:
    """Single-substitution energy: E_sub = E_alloy(X->Y) - E_alloy(X)
                                          - mu_Y_pure + mu_X_pure.

    Negative => Y prefers to be in the alloy over its pure phase
    (relative to displacing element X).
    """
    print("\n=== Phase 2: Solute dissolution (Fe/Ti/Al) ===")
    results: list[SoluteResult] = []

    for matrix_name, atoms_pure in relaxed_bcc.items():
        comp = COMPOSITIONS[matrix_name]
        e_alloy = atoms_pure.get_potential_energy()
        n_atoms = len(atoms_pure)
        print(f"\n[{matrix_name}]  E={e_alloy/n_atoms:.4f} eV/atom")

        for solute in ("Fe", "Ti", "Al"):
            # Pick a displaced element: prefer most-abundant non-solute element
            # so the dilute approximation is reasonable.
            candidates = [el for el in comp if el != solute]
            if not candidates:
                continue
            # Pick the element with the largest count to perturb composition least
            displaced = max(candidates, key=lambda e: comp[e])

            # Find first occurrence of `displaced` and replace
            test = atoms_pure.copy()
            symbols = list(test.get_chemical_symbols())
            try:
                idx = symbols.index(displaced)
            except ValueError:
                continue
            symbols[idx] = solute
            test.set_chemical_symbols(symbols)
            test.calc = calc
            relax(test, fmax=0.05, steps=120,
                  label=f"  {solute}<-{displaced}")
            e_sub_total = test.get_potential_energy()
            e_sub = (e_sub_total - e_alloy) - mu[solute] + mu[displaced]
            results.append(SoluteResult(matrix_name, solute, displaced, e_sub))
            print(f"    E_sub({solute}<-{displaced}) = {e_sub:+.3f} eV")
    return results


# ---------------------------------------------------------------------------
# Phase 3: NPT MD on ISRU blend
# ---------------------------------------------------------------------------
def run_md_isru(calc, atoms_seed: Atoms,
                temps_K=(1000, 1500, 2000),
                n_steps: int = 1000,
                timestep_fs: float = 1.0):
    print("\n=== Phase 3: MD on ISRU blend ===")
    md_data = {}
    for T in temps_K:
        atoms = atoms_seed.copy()
        atoms.calc = calc
        MaxwellBoltzmannDistribution(atoms, temperature_K=T, rng=np.random.default_rng(RNG_SEED + T))
        # Langevin (NVT) — full NPT for MACE+ASE adds complexity; NVT at the
        # already-relaxed cell volume is the standard quick-look protocol.
        dyn = Langevin(atoms, timestep=timestep_fs * units.fs,
                       temperature_K=T, friction=0.01 / units.fs)
        E, T_inst, step_log = [], [], []
        rdf_atoms_final = None

        t0 = time.time()
        sample_every = max(1, n_steps // 50)
        for step in range(n_steps):
            dyn.run(1)
            if step % sample_every == 0:
                ek = atoms.get_kinetic_energy() / len(atoms)
                ep = atoms.get_potential_energy() / len(atoms)
                Tk = atoms.get_temperature()
                E.append(ep)
                T_inst.append(Tk)
                step_log.append(step)
        rdf_atoms_final = atoms.copy()
        elapsed = time.time() - t0
        print(f"  T={T}K  done {n_steps} steps in {elapsed/60:.1f} min "
              f"({elapsed/n_steps*1000:.0f} ms/step)  <T>={np.mean(T_inst[-20:]):.0f}K")
        md_data[T] = dict(steps=step_log, E=E, T_inst=T_inst,
                          atoms=rdf_atoms_final)
    return md_data


def compute_rdf(atoms: Atoms, rmax: float = 6.0, nbins: int = 80):
    """Total RDF (all-pair, normalised by ideal-gas density)."""
    from ase.geometry.analysis import Analysis
    ana = Analysis(atoms)
    # Use simple distance histogram via scipy — Analysis.get_rdf needs newer ase
    pos = atoms.get_positions()
    cell = atoms.cell.array
    n = len(atoms)
    # Minimum-image distances
    dists = []
    inv = np.linalg.inv(cell)
    for i in range(n):
        d = pos - pos[i]
        f = d @ inv
        f -= np.round(f)
        d = f @ cell
        r = np.linalg.norm(d, axis=1)
        r = r[(r > 1e-3) & (r < rmax)]
        dists.append(r)
    dists = np.concatenate(dists)
    edges = np.linspace(0, rmax, nbins + 1)
    hist, edges = np.histogram(dists, bins=edges)
    r_centers = 0.5 * (edges[:-1] + edges[1:])
    dr = edges[1] - edges[0]
    rho = n / atoms.get_volume()
    shell_vol = 4 * np.pi * r_centers**2 * dr
    g = hist / (n * rho * shell_vol)
    return r_centers, g


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------
def plot_results(static_results, solute_results, md_data, mu, isru_atoms_relaxed):
    plt.rcParams.update({
        "font.size": 10, "axes.labelsize": 11, "axes.titlesize": 12,
        "figure.dpi": 300, "savefig.dpi": 300,
    })

    fig = plt.figure(figsize=(14, 10))
    gs = fig.add_gridspec(2, 3, hspace=0.35, wspace=0.30)

    # --- Panel (a): T=0 phase competition ---
    ax = fig.add_subplot(gs[0, 0])
    phase_colors = {"bcc": "#FF5722", "fcc": "#9C27B0", "hcp": "#4CAF50"}
    comps = list(COMPOSITIONS.keys())
    width = 0.25
    x = np.arange(len(comps))
    for i, ph in enumerate(PHASES):
        vals = []
        for c in comps:
            r = next(r for r in static_results if r.composition == c and r.phase == ph)
            dh = formation_energy(r.e_per_atom, COMPOSITIONS[c], mu) * 1000  # meV/atom
            vals.append(dh)
        ax.bar(x + (i - 1) * width, vals, width, label=ph.upper(),
               color=phase_colors[ph], alpha=0.85, edgecolor="black", linewidth=0.5)
    ax.set_xticks(x)
    ax.set_xticklabels(["R1\nHfNbTaTiZr", "R2\nMoNbTaTiV", "R3\nISRU"], fontsize=9)
    ax.set_ylabel(r"$\Delta H_f$ (meV/atom)")
    ax.set_title("(a) T = 0 K phase competition", fontweight="bold")
    ax.axhline(0, color="black", lw=0.5)
    ax.legend(fontsize=9, loc="best")
    ax.grid(axis="y", alpha=0.3)

    # --- Panel (b): ΔE(BCC -> alt phase) — relative phase preference ---
    ax = fig.add_subplot(gs[0, 1])
    for i, c in enumerate(comps):
        e_bcc = next(r.e_per_atom for r in static_results if r.composition == c and r.phase == "bcc")
        for j, ph in enumerate(["fcc", "hcp"]):
            e = next(r.e_per_atom for r in static_results if r.composition == c and r.phase == ph)
            de = (e - e_bcc) * 1000  # meV/atom
            ax.bar(i + (j - 0.5) * 0.4, de, 0.4,
                   color=phase_colors[ph], alpha=0.85,
                   label=f"{ph.upper()} − BCC" if i == 0 else None,
                   edgecolor="black", linewidth=0.5)
    ax.set_xticks(range(len(comps)))
    ax.set_xticklabels(["R1", "R2", "R3"])
    ax.set_ylabel(r"$E_\mathrm{phase} - E_\mathrm{BCC}$ (meV/atom)")
    ax.set_title("(b) BCC preference vs FCC / HCP", fontweight="bold")
    ax.axhline(0, color="black", lw=0.5)
    ax.legend(fontsize=9)
    ax.grid(axis="y", alpha=0.3)

    # --- Panel (c): Solute dissolution heatmap ---
    ax = fig.add_subplot(gs[0, 2])
    matrices = list(COMPOSITIONS.keys())
    solutes = ["Fe", "Ti", "Al"]
    M = np.full((len(matrices), len(solutes)), np.nan)
    for r in solute_results:
        i = matrices.index(r.matrix)
        j = solutes.index(r.solute)
        M[i, j] = r.e_sub
    im = ax.imshow(M, cmap="RdBu_r", aspect="auto",
                   vmin=-max(np.nanmax(np.abs(M)), 1.0),
                   vmax= max(np.nanmax(np.abs(M)), 1.0))
    ax.set_xticks(range(len(solutes))); ax.set_xticklabels(solutes)
    ax.set_yticks(range(len(matrices))); ax.set_yticklabels(["R1", "R2", "R3"])
    for i in range(len(matrices)):
        for j in range(len(solutes)):
            if not np.isnan(M[i, j]):
                ax.text(j, i, f"{M[i,j]:+.2f}", ha="center", va="center",
                        color="white" if abs(M[i, j]) > 0.5 else "black",
                        fontsize=10, fontweight="bold")
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label(r"$E_\mathrm{sub}$ (eV)")
    ax.set_title("(c) Single-solute dissolution\n(neg ⇒ favourable)",
                 fontweight="bold")

    # --- Panel (d): MD energy trace ---
    ax = fig.add_subplot(gs[1, 0])
    cmap = plt.cm.plasma
    for i, (T, d) in enumerate(sorted(md_data.items())):
        c = cmap(i / max(1, len(md_data) - 1))
        # convert step -> ps (1 fs/step)
        ax.plot(np.array(d["steps"]) * 1e-3, d["E"], color=c, lw=1.4,
                label=f"{T} K")
    ax.set_xlabel("time (ps)")
    ax.set_ylabel("E (eV/atom)")
    ax.set_title("(d) ISRU blend NVT MD: energy", fontweight="bold")
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)

    # --- Panel (e): Instantaneous T trace ---
    ax = fig.add_subplot(gs[1, 1])
    for i, (T, d) in enumerate(sorted(md_data.items())):
        c = cmap(i / max(1, len(md_data) - 1))
        ax.plot(np.array(d["steps"]) * 1e-3, d["T_inst"], color=c, lw=1.0,
                label=f"set {T} K", alpha=0.8)
        ax.axhline(T, color=c, lw=0.6, ls="--", alpha=0.5)
    ax.set_xlabel("time (ps)")
    ax.set_ylabel("T (K)")
    ax.set_title("(e) ISRU blend MD: temperature equilibration",
                 fontweight="bold")
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)

    # --- Panel (f): RDF at the highest-T snapshot ---
    ax = fig.add_subplot(gs[1, 2])
    # Pre-MD (relaxed) reference
    r_ref, g_ref = compute_rdf(isru_atoms_relaxed)
    ax.plot(r_ref, g_ref, color="black", lw=1.4, label="T=0 (relaxed)")
    for i, (T, d) in enumerate(sorted(md_data.items())):
        c = cmap(i / max(1, len(md_data) - 1))
        r, g = compute_rdf(d["atoms"])
        ax.plot(r, g, color=c, lw=1.2, label=f"{T} K (final)")
    ax.set_xlabel("r (Å)")
    ax.set_ylabel("g(r)")
    ax.set_title("(f) ISRU blend RDF (final snapshot)", fontweight="bold")
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)

    fig.suptitle("RHEA stability with mace-mh-1 (foundation MLIP, OMAT/PBE head)",
                 fontsize=13, fontweight="bold", y=0.995)
    fig.tight_layout(rect=[0, 0, 1, 0.97])

    out_pdf = os.path.join(FIGDIR, "rhea_mace_stability.pdf")
    out_png = os.path.join(FIGDIR, "rhea_mace_stability.png")
    fig.savefig(out_pdf)
    fig.savefig(out_png)
    print(f"\n✓ wrote {out_pdf}")
    print(f"✓ wrote {out_png}")
    plt.close(fig)


# ---------------------------------------------------------------------------
# CSV dump
# ---------------------------------------------------------------------------
def write_csv(static_results, solute_results, mu):
    out = os.path.join(OUTDIR, "rhea_mace_results.csv")
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["section", "composition", "phase_or_solute",
                    "displaced", "value", "unit", "note"])
        for r in static_results:
            dh = formation_energy(r.e_per_atom, COMPOSITIONS[r.composition], mu)
            w.writerow(["static", r.composition, r.phase, "",
                        f"{r.e_per_atom:.5f}", "eV/atom", "E"])
            w.writerow(["static", r.composition, r.phase, "",
                        f"{dh*1000:.3f}", "meV/atom", "ΔH_f"])
            w.writerow(["static", r.composition, r.phase, "",
                        f"{r.v_per_atom:.4f}", "Å³/atom", "V"])
        for r in solute_results:
            w.writerow(["solute", r.matrix, r.solute, r.displaced,
                        f"{r.e_sub:+.4f}", "eV", "E_sub"])
        for el, m in mu.items():
            w.writerow(["mu_ref", "", el, "", f"{m:.5f}", "eV/atom",
                        "pure-element ground-state E/atom"])
    print(f"✓ wrote {out}")


# ---------------------------------------------------------------------------
# Cache I/O (JSON for scalars, ASE .traj for atoms)
# ---------------------------------------------------------------------------
REFS_PATH = os.path.join(CACHEDIR, "refs.json")
STATIC_PATH = os.path.join(CACHEDIR, "static.json")
SOLUTE_PATH = os.path.join(CACHEDIR, "solute.json")

def md_paths(T):
    return (os.path.join(CACHEDIR, f"md_T{T}.json"),
            os.path.join(CACHEDIR, f"md_T{T}.traj"))


def save_refs(mu):
    with open(REFS_PATH, "w") as f:
        json.dump(mu, f, indent=2)


def load_refs():
    if os.path.exists(REFS_PATH):
        with open(REFS_PATH) as f:
            return json.load(f)
    return None


def save_static(results):
    with open(STATIC_PATH, "w") as f:
        json.dump([asdict(r) for r in results], f, indent=2)


def load_static():
    if os.path.exists(STATIC_PATH):
        with open(STATIC_PATH) as f:
            return [PhaseResult(**d) for d in json.load(f)]
    return None


def save_solute(results):
    with open(SOLUTE_PATH, "w") as f:
        json.dump([asdict(r) for r in results], f, indent=2)


def load_solute():
    if os.path.exists(SOLUTE_PATH):
        with open(SOLUTE_PATH) as f:
            return [SoluteResult(**d) for d in json.load(f)]
    return None


def save_md(md_data):
    for T, d in md_data.items():
        jpath, tpath = md_paths(T)
        scalar = {"steps": list(map(int, d["steps"])),
                  "E": list(map(float, d["E"])),
                  "T_inst": list(map(float, d["T_inst"]))}
        with open(jpath, "w") as f:
            json.dump(scalar, f)
        a = d["atoms"].copy()
        a.calc = None
        ase_write(tpath, a)


def load_md():
    out = {}
    for fname in os.listdir(CACHEDIR):
        if fname.startswith("md_T") and fname.endswith(".json"):
            T = int(fname[len("md_T"):-len(".json")])
            jpath, tpath = md_paths(T)
            with open(jpath) as f:
                scalar = json.load(f)
            atoms = ase_read(tpath)
            out[T] = dict(steps=scalar["steps"], E=scalar["E"],
                          T_inst=scalar["T_inst"], atoms=atoms)
    return out if out else None


def load_relaxed(phase, comp_name):
    p = os.path.join(CACHEDIR, f"relaxed_{phase}_{comp_name}.traj")
    if os.path.exists(p):
        return ase_read(p)
    return None


# ---------------------------------------------------------------------------
# Slide-format figures (16:9, large fonts, one concept per figure)
# ---------------------------------------------------------------------------
SLIDE_RC = {
    "font.size": 16, "axes.labelsize": 18, "axes.titlesize": 20,
    "xtick.labelsize": 15, "ytick.labelsize": 15, "legend.fontsize": 14,
    "axes.linewidth": 1.2, "xtick.major.width": 1.2, "ytick.major.width": 1.2,
    "lines.linewidth": 2.5, "figure.dpi": 300, "savefig.dpi": 300,
    "savefig.bbox": "tight", "axes.spines.top": False, "axes.spines.right": False,
}
PHASE_COLORS = {"bcc": "#FF5722", "fcc": "#9C27B0", "hcp": "#4CAF50"}
COMP_LABELS = {"R1_HfNbTaTiZr": "R1 — HfNbTaTiZr",
               "R2_MoNbTaTiV":  "R2 — MoNbTaTiV",
               "R3_ISRU_blend": "R3 — ISRU blend"}

# Element colors for 3D structure renders (CPK-ish, tuned for visibility)
ELEMENT_COLORS = {
    "Fe": "#E8702A", "Ti": "#BFC2C7", "Al": "#BFA6A0",
    "Nb": "#72C2C9", "Ta": "#4DA6E0", "Mo": "#54B254",
    "V":  "#A6A6A6", "Hf": "#4DB6F1", "Zr": "#94E0E0",
}


def slide_phase_competition(static_results, mu):
    plt.rcParams.update(SLIDE_RC)
    fig, ax = plt.subplots(figsize=(13, 7))
    comps = list(COMPOSITIONS.keys())
    x = np.arange(len(comps))
    width = 0.27
    for i, ph in enumerate(PHASES):
        vals = []
        for c in comps:
            r = next(r for r in static_results if r.composition == c and r.phase == ph)
            dh = formation_energy(r.e_per_atom, COMPOSITIONS[c], mu) * 1000
            vals.append(dh)
        bars = ax.bar(x + (i - 1) * width, vals, width, label=ph.upper(),
                      color=PHASE_COLORS[ph], alpha=0.92,
                      edgecolor="black", linewidth=0.8)
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2,
                    v + (4 if v >= 0 else -10),
                    f"{v:+.0f}", ha="center", va="bottom" if v >= 0 else "top",
                    fontsize=12, fontweight="bold")
    ax.axhline(0, color="black", lw=1)
    ax.set_xticks(x)
    ax.set_xticklabels([COMP_LABELS[c] for c in comps])
    ax.set_ylabel(r"Formation enthalpy  $\Delta H_f$  (meV / atom)")
    ax.set_title("RHEA T = 0 K phase competition (mace-mh-1)", pad=14)
    # Place legend outside the plot area to avoid covering data labels
    ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5),
              frameon=True, framealpha=0.95)
    ax.grid(axis="y", alpha=0.3)
    out = os.path.join(SLIDEDIR, "slide_01_phase_competition")
    fig.savefig(out + ".pdf"); fig.savefig(out + ".png")
    plt.close(fig)
    print(f"  ✓ {os.path.basename(out)}")


def slide_bcc_preference(static_results):
    plt.rcParams.update(SLIDE_RC)
    fig, ax = plt.subplots(figsize=(13, 7))
    comps = list(COMPOSITIONS.keys())
    x = np.arange(len(comps))
    width = 0.36
    for j, ph in enumerate(["fcc", "hcp"]):
        vals = []
        for c in comps:
            e_bcc = next(r.e_per_atom for r in static_results if r.composition == c and r.phase == "bcc")
            e = next(r.e_per_atom for r in static_results if r.composition == c and r.phase == ph)
            vals.append((e - e_bcc) * 1000)
        bars = ax.bar(x + (j - 0.5) * width, vals, width,
                      label=f"{ph.upper()} − BCC", color=PHASE_COLORS[ph],
                      alpha=0.92, edgecolor="black", linewidth=0.8)
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2,
                    v + (4 if v >= 0 else -10),
                    f"{v:+.0f}", ha="center", va="bottom" if v >= 0 else "top",
                    fontsize=12, fontweight="bold")
    ax.axhline(0, color="black", lw=1)
    ax.set_xticks(x); ax.set_xticklabels([COMP_LABELS[c] for c in comps])
    ax.set_ylabel(r"$E_\mathrm{phase} - E_\mathrm{BCC}$  (meV / atom)")
    ax.set_title("BCC stability margin against FCC and HCP", pad=14)
    ax.legend(loc="best", frameon=True, framealpha=0.95)
    ax.grid(axis="y", alpha=0.3)
    out = os.path.join(SLIDEDIR, "slide_02_bcc_preference")
    fig.savefig(out + ".pdf"); fig.savefig(out + ".png")
    plt.close(fig)
    print(f"  ✓ {os.path.basename(out)}")


def slide_solute_heatmap(solute_results):
    plt.rcParams.update(SLIDE_RC)
    fig, ax = plt.subplots(figsize=(11, 7))
    matrices = list(COMPOSITIONS.keys())
    solutes = ["Fe", "Ti", "Al"]
    M = np.full((len(matrices), len(solutes)), np.nan)
    disp = np.full((len(matrices), len(solutes)), "", dtype=object)
    for r in solute_results:
        i = matrices.index(r.matrix); j = solutes.index(r.solute)
        M[i, j] = r.e_sub
        disp[i, j] = r.displaced
    vmax = max(np.nanmax(np.abs(M)), 1.0)
    im = ax.imshow(M, cmap="RdBu_r", aspect="auto", vmin=-vmax, vmax=vmax)
    ax.set_xticks(range(len(solutes))); ax.set_xticklabels(solutes, fontsize=18)
    ax.set_yticks(range(len(matrices)))
    ax.set_yticklabels([COMP_LABELS[m] for m in matrices], fontsize=14)
    for i in range(len(matrices)):
        for j in range(len(solutes)):
            if np.isnan(M[i, j]):
                continue
            ax.text(j, i, f"{M[i,j]:+.2f} eV\n(↩{disp[i,j]})",
                    ha="center", va="center",
                    color="white" if abs(M[i, j]) > 0.5 else "black",
                    fontsize=14, fontweight="bold")
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label(r"$E_\mathrm{sub}$ (eV)  —  negative = solute prefers alloy")
    ax.set_title("Single-atom solute dissolution into BCC RHEAs", pad=14)
    ax.set_xlabel("solute (ISRU-extractable)")
    out = os.path.join(SLIDEDIR, "slide_03_solute_dissolution")
    fig.savefig(out + ".pdf"); fig.savefig(out + ".png")
    plt.close(fig)
    print(f"  ✓ {os.path.basename(out)}")


def slide_md_panels(md_data, isru_atoms_relaxed):
    plt.rcParams.update(SLIDE_RC)
    cmap = plt.cm.plasma

    # (d) energy
    fig, ax = plt.subplots(figsize=(13, 7))
    for i, (T, d) in enumerate(sorted(md_data.items())):
        c = cmap(i / max(1, len(md_data) - 1))
        ax.plot(np.array(d["steps"]) * 1e-3, d["E"],
                color=c, lw=2.5, label=f"{T} K")
    ax.set_xlabel("time (ps)"); ax.set_ylabel("potential energy  (eV / atom)")
    ax.set_title("ISRU blend NVT MD — energy", pad=14)
    ax.legend(); ax.grid(alpha=0.3)
    out = os.path.join(SLIDEDIR, "slide_04_md_energy")
    fig.savefig(out + ".pdf"); fig.savefig(out + ".png"); plt.close(fig)
    print(f"  ✓ {os.path.basename(out)}")

    # (e) temperature
    fig, ax = plt.subplots(figsize=(13, 7))
    for i, (T, d) in enumerate(sorted(md_data.items())):
        c = cmap(i / max(1, len(md_data) - 1))
        ax.plot(np.array(d["steps"]) * 1e-3, d["T_inst"],
                color=c, lw=1.6, label=f"set {T} K")
        ax.axhline(T, color=c, lw=1.0, ls="--", alpha=0.5)
    ax.set_xlabel("time (ps)"); ax.set_ylabel("temperature (K)")
    ax.set_title("ISRU blend NVT MD — Langevin temperature equilibration", pad=14)
    ax.legend(); ax.grid(alpha=0.3)
    out = os.path.join(SLIDEDIR, "slide_05_md_temperature")
    fig.savefig(out + ".pdf"); fig.savefig(out + ".png"); plt.close(fig)
    print(f"  ✓ {os.path.basename(out)}")

    # (f) RDF
    fig, ax = plt.subplots(figsize=(13, 7))
    r_ref, g_ref = compute_rdf(isru_atoms_relaxed)
    ax.plot(r_ref, g_ref, color="black", lw=2.6, label="T = 0 K (relaxed)")
    for i, (T, d) in enumerate(sorted(md_data.items())):
        c = cmap(i / max(1, len(md_data) - 1))
        r, g = compute_rdf(d["atoms"])
        ax.plot(r, g, color=c, lw=2.2, label=f"{T} K (final)")
    ax.set_xlabel(r"interatomic distance  $r$  (Å)")
    ax.set_ylabel(r"radial distribution  $g(r)$")
    ax.set_title("ISRU blend — radial distribution function", pad=14)
    ax.legend(); ax.grid(alpha=0.3); ax.set_xlim(0, 6)
    out = os.path.join(SLIDEDIR, "slide_06_md_rdf")
    fig.savefig(out + ".pdf"); fig.savefig(out + ".png"); plt.close(fig)
    print(f"  ✓ {os.path.basename(out)}")


def slide_structure_renders():
    """Render the 3 relaxed BCC supercells side-by-side."""
    plt.rcParams.update(SLIDE_RC)
    comps = list(COMPOSITIONS.keys())
    fig, axes = plt.subplots(1, 3, figsize=(20, 8))
    for ax, comp_name in zip(axes, comps):
        atoms = load_relaxed("bcc", comp_name)
        if atoms is None:
            ax.text(0.5, 0.5, f"missing: {comp_name}",
                    ha="center", va="center", transform=ax.transAxes)
            continue
        # Tile 1x1x2 along c so BCC supercell looks more cubic / less slab-like
        view = atoms.copy() * (1, 1, 2)
        colors = [ELEMENT_COLORS.get(s, "#888") for s in view.get_chemical_symbols()]
        plot_atoms(view, ax=ax, radii=0.85, colors=colors,
                   rotation=("12x,28y,0z"))
        ax.set_axis_off()
        # legend
        present = sorted(set(view.get_chemical_symbols()),
                         key=lambda s: -COMPOSITIONS[comp_name].get(s, 0))
        handles = [plt.Line2D([0], [0], marker="o", color="w",
                              markerfacecolor=ELEMENT_COLORS.get(s, "#888"),
                              markeredgecolor="black",
                              markersize=14, label=s) for s in present]
        ax.legend(handles=handles, loc="upper center",
                  bbox_to_anchor=(0.5, -0.02), ncol=len(present),
                  fontsize=14, frameon=False)
        ax.set_title(COMP_LABELS[comp_name], fontsize=18, pad=10,
                     fontweight="bold")
    fig.suptitle("Relaxed 100-atom BCC supercells (mace-mh-1)",
                 fontsize=22, fontweight="bold", y=0.99)
    fig.tight_layout(rect=[0, 0.04, 1, 0.95])
    out = os.path.join(SLIDEDIR, "slide_07_structures_bcc")
    fig.savefig(out + ".pdf"); fig.savefig(out + ".png"); plt.close(fig)
    print(f"  ✓ {os.path.basename(out)}")

    # Also render all three phases for the ISRU blend (BCC vs FCC vs HCP)
    fig, axes = plt.subplots(1, 3, figsize=(20, 8))
    # Tile each so the cells look comparably-sized and not slab-like
    tile_factors = {"bcc": (1, 1, 2), "fcc": (1, 1, 3), "hcp": (1, 1, 2)}
    for ax, ph in zip(axes, ("bcc", "fcc", "hcp")):
        atoms = load_relaxed(ph, "R3_ISRU_blend")
        if atoms is None:
            continue
        view = atoms.copy() * tile_factors[ph]
        colors = [ELEMENT_COLORS.get(s, "#888") for s in view.get_chemical_symbols()]
        plot_atoms(view, ax=ax, radii=0.85, colors=colors,
                   rotation=("12x,28y,0z"))
        ax.set_axis_off()
        ax.set_title(f"{ph.upper()}  (ISRU blend)", fontsize=18,
                     pad=10, fontweight="bold",
                     color=PHASE_COLORS[ph])
    # Single legend for the whole figure
    present = sorted(COMPOSITIONS["R3_ISRU_blend"],
                     key=lambda s: -COMPOSITIONS["R3_ISRU_blend"][s])
    handles = [plt.Line2D([0], [0], marker="o", color="w",
                          markerfacecolor=ELEMENT_COLORS.get(s, "#888"),
                          markeredgecolor="black",
                          markersize=16, label=s) for s in present]
    fig.legend(handles=handles, loc="lower center", ncol=len(present),
               fontsize=15, frameon=False, bbox_to_anchor=(0.5, 0.02))
    fig.suptitle("ISRU blend across candidate phases",
                 fontsize=22, fontweight="bold", y=0.99)
    fig.tight_layout(rect=[0, 0.07, 1, 0.95])
    out = os.path.join(SLIDEDIR, "slide_08_structures_isru_phases")
    fig.savefig(out + ".pdf"); fig.savefig(out + ".png"); plt.close(fig)
    print(f"  ✓ {os.path.basename(out)}")


def slide_md_final_snapshot():
    """3D snapshot of ISRU blend at the highest MD temperature, vs T=0."""
    plt.rcParams.update(SLIDE_RC)
    relaxed = load_relaxed("bcc", "R3_ISRU_blend")
    if relaxed is None:
        return
    md_files = sorted(int(f[len("md_T"):-len(".traj")])
                      for f in os.listdir(CACHEDIR)
                      if f.startswith("md_T") and f.endswith(".traj"))
    if not md_files:
        return
    T_hot = md_files[-1]
    hot = ase_read(os.path.join(CACHEDIR, f"md_T{T_hot}.traj"))

    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    for ax, atoms, label in zip(axes, [relaxed, hot],
                                 [r"T = 0 K  (relaxed BCC)",
                                  f"T = {T_hot} K  (final MD snapshot)"]):
        view = atoms.copy() * (1, 1, 2)
        colors = [ELEMENT_COLORS.get(s, "#888") for s in view.get_chemical_symbols()]
        plot_atoms(view, ax=ax, radii=0.85, colors=colors,
                   rotation=("12x,28y,0z"))
        ax.set_axis_off()
        ax.set_title(label, fontsize=18, pad=10, fontweight="bold")
    present = sorted(COMPOSITIONS["R3_ISRU_blend"],
                     key=lambda s: -COMPOSITIONS["R3_ISRU_blend"][s])
    handles = [plt.Line2D([0], [0], marker="o", color="w",
                          markerfacecolor=ELEMENT_COLORS.get(s, "#888"),
                          markeredgecolor="black",
                          markersize=16, label=s) for s in present]
    fig.legend(handles=handles, loc="lower center", ncol=len(present),
               fontsize=15, frameon=False, bbox_to_anchor=(0.5, 0.02))
    fig.suptitle("ISRU blend: structure before and after MD",
                 fontsize=22, fontweight="bold", y=0.99)
    fig.tight_layout(rect=[0, 0.07, 1, 0.95])
    out = os.path.join(SLIDEDIR, "slide_09_md_snapshot")
    fig.savefig(out + ".pdf"); fig.savefig(out + ".png"); plt.close(fig)
    print(f"  ✓ {os.path.basename(out)}")


def emit_all_figures(static_results, solute_results, md_data, mu, isru_relaxed):
    print("\n=== Generating paper figure ===")
    plot_results(static_results, solute_results, md_data, mu, isru_relaxed)
    print("\n=== Generating slide figures ===")
    slide_phase_competition(static_results, mu)
    slide_bcc_preference(static_results)
    slide_solute_heatmap(solute_results)
    slide_md_panels(md_data, isru_relaxed)
    slide_structure_renders()
    slide_md_final_snapshot()


# ---------------------------------------------------------------------------
# Main (cached / resumable)
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--plot-only", action="store_true",
                        help="Skip MACE; load cached results and re-emit figures.")
    parser.add_argument("--force", action="store_true",
                        help="Recompute even if cache exists.")
    args = parser.parse_args()

    t_start = time.time()

    if args.plot_only:
        print("--plot-only: loading cached results...")
        mu = load_refs(); static_results = load_static()
        solute_results = load_solute(); md_data = load_md()
        isru_relaxed = load_relaxed("bcc", "R3_ISRU_blend")
        missing = [n for n, x in [("refs", mu), ("static", static_results),
                                   ("solute", solute_results),
                                   ("md", md_data),
                                   ("relaxed_bcc_R3", isru_relaxed)] if not x]
        if missing:
            sys.exit(f"Cache missing: {missing}")
        emit_all_figures(static_results, solute_results, md_data, mu, isru_relaxed)
        write_csv(static_results, solute_results, mu)
        print(f"\nTotal: {(time.time()-t_start):.1f}s")
        return

    print("Loading mace-mh-1 (CPU, float64, omat_pbe head)...")
    calc = make_calc()

    # Pure-element refs
    mu = None if args.force else load_refs()
    if mu is None:
        print("\n=== Pure-element references ===")
        elements_needed = sorted({el for c in COMPOSITIONS.values() for el in c})
        mu = {el: pure_element_energy(el, calc) for el in elements_needed}
        save_refs(mu)
    else:
        print(f"[cache] refs ({len(mu)} elements)")

    # Phase 1: static + relaxed structure dump
    static_results = None if args.force else load_static()
    if static_results is None:
        static_results = run_static_phase_competition(calc, mu)
        save_static(static_results)
    else:
        print(f"[cache] static ({len(static_results)} entries)")

    # Reuse relaxed BCC structures from Phase 1 for Phases 2 and 3
    relaxed_bcc: dict[str, Atoms] = {}
    for comp_name in COMPOSITIONS:
        a = load_relaxed("bcc", comp_name)
        if a is None:
            sys.exit(f"Missing relaxed BCC for {comp_name}; rerun with --force.")
        a.calc = calc
        relaxed_bcc[comp_name] = a

    # Phase 2: solute
    solute_results = None if args.force else load_solute()
    if solute_results is None:
        solute_results = run_solute_dissolution(calc, mu, relaxed_bcc)
        save_solute(solute_results)
    else:
        print(f"[cache] solute ({len(solute_results)} entries)")

    # Phase 3: MD on ISRU
    md_data = None if args.force else load_md()
    if md_data is None:
        md_data = run_md_isru(calc, relaxed_bcc["R3_ISRU_blend"],
                              temps_K=(1000, 1500, 2000), n_steps=1000)
        save_md(md_data)
    else:
        print(f"[cache] md ({sorted(md_data.keys())} K)")

    # Outputs
    isru_relaxed = load_relaxed("bcc", "R3_ISRU_blend")
    emit_all_figures(static_results, solute_results, md_data, mu, isru_relaxed)
    write_csv(static_results, solute_results, mu)

    print(f"\n=== TOTAL: {(time.time()-t_start)/60:.1f} min ===")


if __name__ == "__main__":
    main()
