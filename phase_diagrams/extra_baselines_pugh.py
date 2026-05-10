#!/usr/bin/env python3
"""
Pugh's G/B for the three published RHEA baselines from Table 11 / 12 of the
manuscript that were missing from the original elastic-constants run:

  - MoNbTaW         (4-element, 0% ISRU)        Senkov 2011
  - MoNbTaVW        (5-element, 0% ISRU)        Senkov 2018
  - AlMo0.5NbTa0.5TiZr (6-element, 19% ISRU)    Senkov 2018  -- the headline
                                                 "most promising 800-1000C"
                                                 published RHEA cited in the
                                                 paper's Section 4.5

Builds 100-atom random-substitution BCC supercells, relaxes with mace-mh-1,
runs the same 6-strain VRH analysis as elastic_constants.py.

Outputs:
  phase_diagrams/mace_cache/relaxed_bcc_<short>.traj
  phase_diagrams/elastic_results_extra.csv  (appended to main CSV later)
"""
from __future__ import annotations

import csv
import time
import warnings
from pathlib import Path

import numpy as np
from ase import Atoms
from ase.build import bulk
from ase.filters import FrechetCellFilter
from ase.io import write as ase_write
from ase.optimize import LBFGS

# Re-use the elastic-tensor + VRH machinery we already wrote.
import sys
sys.path.insert(0, str(Path(__file__).parent))
from elastic_constants import elastic_tensor, voigt_reuss_hill, make_calc

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "phase_diagrams" / "mace_cache"
CSV_OUT = ROOT / "phase_diagrams" / "elastic_results_extra.csv"

# Pure-element BCC starting lattice parameters (Angstrom)
A_BCC = {
    "Mo": 3.15, "Nb": 3.30, "Ta": 3.30, "Ti": 3.27, "V": 3.03,
    "Fe": 2.87, "Hf": 3.55, "Zr": 3.57, "Al": 3.20, "W": 3.16,
}

# 100-atom compositions
COMPOSITIONS = {
    "MoNbTaW":            {"Mo": 25, "Nb": 25, "Ta": 25, "W": 25},
    "MoNbTaVW":           {"Mo": 20, "Nb": 20, "Ta": 20, "V": 20, "W": 20},
    "AlMo0.5NbTa0.5TiZr": {"Al": 20, "Mo": 10, "Nb": 20, "Ta": 10,
                            "Ti": 20, "Zr": 20},
}

RNG_SEED = 20260506


def build_bcc(comp: dict) -> Atoms:
    n = sum(comp.values())
    assert n == 100, f"comp sums to {n}"
    a = sum(A_BCC[el] * c for el, c in comp.items()) / n
    proto = bulk("X", "bcc", a=a, cubic=True)
    sc = proto * (5, 5, 2)
    syms = [el for el, c in comp.items() for _ in range(c)]
    rng = np.random.default_rng(RNG_SEED)
    rng.shuffle(syms)
    sc.set_chemical_symbols(syms)
    return sc


def main() -> None:
    calc = make_calc()
    rows = []
    for short, comp in COMPOSITIONS.items():
        print(f"\n[{short}]  comp={comp}")
        atoms = build_bcc(comp)
        atoms.calc = calc
        flt = FrechetCellFilter(atoms)
        opt = LBFGS(flt, logfile=None)
        t0 = time.time()
        opt.run(fmax=0.05, steps=200)
        e_pa = atoms.get_potential_energy() / len(atoms)
        print(f"  relax: E={e_pa:.4f} eV/atom  ({time.time()-t0:.1f}s, "
              f"{opt.get_number_of_steps()} steps)")
        # Cache
        a_clean = atoms.copy(); a_clean.calc = None
        ase_write(CACHE / f"relaxed_bcc_{short}.traj", a_clean)
        # Elastic tensor + VRH
        try:
            C = elastic_tensor(atoms, calc, label=short)
            G, B, pugh = voigt_reuss_hill(C)
            print(f"  -> G={G:.1f} GPa  B={B:.1f} GPa  G/B={pugh:.3f}")
            rows.append({
                "label": short, "short": short,
                "G_VRH_GPa": G, "B_VRH_GPa": B, "Pugh_G_over_B": pugh,
                "C11": C[0, 0], "C12": C[0, 1], "C44": C[3, 3],
            })
        except Exception as ex:
            print(f"  FAILED: {ex}")

    with open(CSV_OUT, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["label", "short", "G_VRH_GPa", "B_VRH_GPa",
                    "Pugh_G_over_B", "C11", "C12", "C44"])
        for r in rows:
            w.writerow([r["label"], r["short"],
                        f"{r['G_VRH_GPa']:.2f}",
                        f"{r['B_VRH_GPa']:.2f}",
                        f"{r['Pugh_G_over_B']:.4f}",
                        f"{r['C11']:.2f}",
                        f"{r['C12']:.2f}",
                        f"{r['C44']:.2f}"])
    print(f"\nwrote {CSV_OUT}")


if __name__ == "__main__":
    main()
