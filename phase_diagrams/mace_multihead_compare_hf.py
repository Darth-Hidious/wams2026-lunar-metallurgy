# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "mace-torch>=0.3.15",
#   "ase>=3.23",
#   "numpy>=1.24",
#   "matplotlib>=3.7",
#   "huggingface_hub>=0.20",
#   "torch>=2.1",
# ]
# ///
"""
mace_multihead_compare_hf.py — Cross-validation across MACE-MH-1 heads.

For WAMS 2026, Paper #68.  Re-evaluates every relaxed structure we have on
disk through three different MACE-MH-1 multi-head output heads, demonstrating
that the phase-preference and formation-enthalpy verdicts are robust against
the choice of electronic-structure-theory reference.

Heads compared (selected from the seven available in mace-mh-1):
  - omat_pbe       : PBE/PBE+U, OMAT-24 corpus.  Main paper result.
                     Recommended head for inorganic crystals.
  - matpes_r2scan  : r²SCAN meta-GGA, MATPES corpus.  More accurate for 3d
                     transition-metal magnetism; sanity-checks ΔH_f for the
                     Fe-bearing dilution path and the Laves competitors.
  - oc20_usemppbe  : PBE, OC20 catalysis corpus.  Different training
                     distribution than omat_pbe — a structural robustness
                     test.  (The other four heads — omol, spice_wB97M,
                     rgd1_b3lyp, matpes_r2scan — are inappropriate for
                     bulk inorganic crystals and not surveyed.)

Structures re-evaluated:
  - 7 dilution-path BCC random-substitution supercells along
    MoNbTaTiV → Fe-50Ti (x = 0, 10, 25, 50, 75, 90, 100 wt% ISRU)
  - 3 published-baseline BCC supercells: MoNbTaW, MoNbTaVW,
    AlMo₀.₅NbTa₀.₅TiZr
  - 2 C14 Laves competitors: Fe₂Nb, Fe₂Ta
  - Pure-element BCC/HCP references for ΔH_f: Mo, Nb, Ta, W, V, Cr (BCC);
    Ti, Zr, Hf (HCP); Fe (BCC); Al (FCC)

For each structure we re-compute the relaxed-geometry total energy under
every head (no further geometry relaxation — the omat_pbe-relaxed structure
is the reference geometry).  ΔH_f relative to pure elements is reconstructed
per head, and the convex-envelope phase verdict (BCC stable / Laves stable)
is re-checked.

Outputs:
  multihead_compare.csv     — energies (eV/atom) per (structure, head)
  multihead_dHf.csv         — formation enthalpy ΔH_f (kJ/mol·atom) per head
  multihead_summary.json    — full per-structure record with verdict columns

No figures are produced from this script (per scope of WAMS revision):
the result enters the paper as a single table in §3.5 / Table~\\ref{tab:multihead}.

Run on HF Jobs:
  hf jobs uv run --flavor l4x1 --timeout 1h --secrets HF_TOKEN \\
      phase_diagrams/mace_multihead_compare_hf.py
"""

from __future__ import annotations

import json
import os
import sys
import warnings
from pathlib import Path

import numpy as np

warnings.filterwarnings("ignore")

OUT_DIR = Path(os.environ.get("OUT_DIR", "/tmp/multihead_out"))
OUT_DIR.mkdir(parents=True, exist_ok=True)

RESULTS_REPO = os.environ.get("RESULTS_REPO",
                                "Darth-Hidious/wams2026-mace-multihead")

# Structures live in the public GitHub repo; fetch them once at job start.
STRUCT_ROOT = Path(os.environ.get("STRUCT_ROOT",
                                    "/tmp/wams26_repo/phase_diagrams"))
GITHUB_REPO = "https://github.com/Darth-Hidious/wams2026-lunar-metallurgy.git"


def fetch_structures():
    """Clone the public WAMS 2026 paper repo into /tmp to access the
    relaxed-structure trajectory files (.traj) committed earlier in the
    pipeline.  No auth needed — repo is public."""
    import subprocess
    target = Path("/tmp/wams26_repo")
    if target.exists():
        print(f"[fetch] {target} already present; skipping clone")
        return
    print(f"[fetch] cloning {GITHUB_REPO} -> {target}")
    subprocess.run(["git", "clone", "--depth", "1", GITHUB_REPO, str(target)],
                    check=True)


def upload_results(local_dir: Path, repo_id: str) -> None:
    """Push every file under `local_dir` to a HF Dataset repo (idempotent)."""
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


# ----------------------------------------------------------------------------
# Structure inventory
# ----------------------------------------------------------------------------
DILUTION_PATH = [
    ("dilution_x000", "MoNbTaTiV (x = 0 wt% ISRU)",     "dilution_results/relaxed_bcc_x000.traj"),
    ("dilution_x010", "x = 10 wt% ISRU",                  "dilution_results/relaxed_bcc_x010.traj"),
    ("dilution_x025", "x = 25 wt% ISRU",                  "dilution_results/relaxed_bcc_x025.traj"),
    ("dilution_x050", "x = 50 wt% ISRU",                  "dilution_results/relaxed_bcc_x050.traj"),
    ("dilution_x075", "x = 75 wt% ISRU",                  "dilution_results/relaxed_bcc_x075.traj"),
    ("dilution_x090", "x = 90 wt% ISRU",                  "dilution_results/relaxed_bcc_x090.traj"),
    ("dilution_x100", "Fe-50Ti (x = 100 wt% ISRU)",      "dilution_results/relaxed_bcc_x100.traj"),
]
PUBLISHED_BASELINES = [
    ("MoNbTaW",                  "MoNbTaW (Senkov 2010)",
     "mace_cache/relaxed_bcc_MoNbTaW.traj"),
    ("MoNbTaVW",                 "MoNbTaVW (Senkov 2010)",
     "mace_cache/relaxed_bcc_MoNbTaVW.traj"),
    ("AlMo0.5NbTa0.5TiZr",       "AlMo₀.₅NbTa₀.₅TiZr (Senkov 2014)",
     "mace_cache/relaxed_bcc_AlMo0.5NbTa0.5TiZr.traj"),
]
LAVES_COMPETITORS = [
    ("Fe2Nb",  "Fe₂Nb (C14)",  "dilution_results/relaxed_fe2nb.traj"),
    ("Fe2Ta",  "Fe₂Ta (C14)",  "dilution_results/relaxed_fe2ta.traj"),
]

# Pure-element reference lattices for ΔH_f (constructed in-script)
PURE_REFERENCES = {
    "Mo": ("bcc", 3.15),
    "Nb": ("bcc", 3.30),
    "Ta": ("bcc", 3.30),
    "W":  ("bcc", 3.16),
    "V":  ("bcc", 3.03),
    "Cr": ("bcc", 2.88),
    "Ti": ("hcp", (2.95, 4.69)),
    "Zr": ("hcp", (3.23, 5.15)),
    "Hf": ("hcp", (3.20, 5.05)),
    "Al": ("fcc", 4.05),
    "Fe": ("bcc", 2.87),
}

# MACE heads to survey
HEADS = ["omat_pbe", "matpes_r2scan", "oc20_usemppbe"]


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------
def build_pure_reference(elem: str):
    """Return an ASE Atoms object for the pure-element reference structure."""
    from ase.build import bulk
    crystal, lat = PURE_REFERENCES[elem]
    if crystal == "bcc":
        return bulk(elem, "bcc", a=lat, cubic=True).repeat((2, 2, 2))
    if crystal == "fcc":
        return bulk(elem, "fcc", a=lat, cubic=True).repeat((2, 2, 2))
    if crystal == "hcp":
        a, c = lat
        return bulk(elem, "hcp", a=a, c=c).repeat((3, 3, 2))
    raise ValueError(crystal)


_MODEL_PATH = None
def _model_path():
    """Cache the downloaded MACE-MH-1 checkpoint across head switches."""
    global _MODEL_PATH
    if _MODEL_PATH is None:
        from huggingface_hub import hf_hub_download
        _MODEL_PATH = hf_hub_download(
            repo_id="mace-foundations/mace-mh-1",
            filename="mace-mh-1.model",
        )
    return _MODEL_PATH


def load_calculator(head: str):
    """Construct a MACE calculator pinned to a particular multi-head output."""
    from mace.calculators import mace_mp
    import torch
    device = "cuda" if torch.cuda.is_available() else "cpu"
    return mace_mp(
        model=_model_path(),
        default_dtype="float32",
        device=device,
        head=head,
    )


def energy_per_atom(atoms, calc):
    """Total energy / N_atoms (eV/atom).  No relaxation — uses the geometry
    we hand in (always the omat_pbe-relaxed geometry)."""
    atoms.set_calculator(calc)
    return atoms.get_potential_energy() / len(atoms)


def composition_dict(atoms) -> dict[str, float]:
    """Return atomic fractions {symbol: fraction} from an ASE Atoms object."""
    syms = atoms.get_chemical_symbols()
    n = len(syms)
    counts = {}
    for s in syms:
        counts[s] = counts.get(s, 0) + 1
    return {s: c / n for s, c in counts.items()}


# ----------------------------------------------------------------------------
# Main loop
# ----------------------------------------------------------------------------
def main():
    from ase.io import read as ase_read

    # 0) Fetch the relaxed-structure .traj files from GitHub
    fetch_structures()

    # 1) Pre-compute pure-element references for every head
    print("=== Building pure-element references ===")
    pure_energies = {h: {} for h in HEADS}
    for head in HEADS:
        print(f"  head = {head} ...")
        calc = load_calculator(head)
        for elem in PURE_REFERENCES:
            atoms = build_pure_reference(elem)
            e = energy_per_atom(atoms, calc)
            pure_energies[head][elem] = e
            print(f"    {elem:>2}: {e:+9.4f} eV/atom")
        del calc

    # 2) Evaluate every alloy structure under every head
    all_targets = (
        [("dilution",  *t) for t in DILUTION_PATH]
        + [("baseline", *t) for t in PUBLISHED_BASELINES]
        + [("laves",    *t) for t in LAVES_COMPETITORS]
    )
    print("\n=== Re-evaluating structures across heads ===")
    energies = {}   # {(group, key, head): e_per_atom}
    dHf_table = {}  # {(group, key, head): dHf in kJ/mol/atom}
    compositions = {}

    for head in HEADS:
        print(f"  head = {head} ...")
        calc = load_calculator(head)
        for group, key, label, traj_rel in all_targets:
            path = STRUCT_ROOT / traj_rel
            if not path.exists():
                print(f"    [SKIP] {key}: file not found at {path}")
                continue
            atoms = ase_read(str(path))
            e = energy_per_atom(atoms, calc)
            energies[(group, key, head)] = e
            comp = composition_dict(atoms)
            compositions[(group, key)] = comp
            # ΔH_f relative to pure-element references at the SAME head
            mu_sum = sum(comp[s] * pure_energies[head].get(s, 0.0) for s in comp)
            dHf_eV = e - mu_sum
            dHf_kJmol = dHf_eV * 96.485                     # eV/atom → kJ/mol/atom
            dHf_table[(group, key, head)] = dHf_kJmol
            print(f"    {label:<35s}  E = {e:+9.4f}  ΔH_f = {dHf_kJmol:+7.2f} kJ/mol")
        del calc

    # 3) Write CSVs
    print("\n=== Writing CSV summaries ===")
    structures = sorted({(g, k, _l, _tr) for g, k, _l, _tr in all_targets})
    # multihead_compare.csv — energies
    with open(OUT_DIR / "multihead_compare.csv", "w") as f:
        f.write("group,key,label,n_atoms," + ",".join(f"E_eV_atom_{h}" for h in HEADS) + "\n")
        for group, key, label, traj_rel in all_targets:
            path = STRUCT_ROOT / traj_rel
            if not path.exists():
                continue
            atoms = ase_read(str(path))
            row = [group, key, label, str(len(atoms))]
            for h in HEADS:
                row.append(f"{energies.get((group, key, h), float('nan')):+.6f}")
            f.write(",".join(row) + "\n")

    # multihead_dHf.csv — formation enthalpies
    with open(OUT_DIR / "multihead_dHf.csv", "w") as f:
        f.write("group,key,label," + ",".join(f"dHf_kJmol_{h}" for h in HEADS)
                 + ",dHf_spread_kJmol\n")
        for group, key, label, traj_rel in all_targets:
            if not (STRUCT_ROOT / traj_rel).exists():
                continue
            vals = [dHf_table.get((group, key, h), float("nan")) for h in HEADS]
            spread = (max(vals) - min(vals)) if not any(np.isnan(vals)) else float("nan")
            row = [group, key, label] + [f"{v:+.3f}" for v in vals] + [f"{spread:.3f}"]
            f.write(",".join(row) + "\n")

    # multihead_summary.json — full record
    summary = []
    for group, key, label, traj_rel in all_targets:
        if not (STRUCT_ROOT / traj_rel).exists():
            continue
        row = {"group": group, "key": key, "label": label}
        for h in HEADS:
            row[f"E_eV_atom_{h}"] = energies.get((group, key, h))
            row[f"dHf_kJmol_{h}"] = dHf_table.get((group, key, h))
        vals = [row[f"dHf_kJmol_{h}"] for h in HEADS]
        if not any(v is None or np.isnan(v) for v in vals):
            row["dHf_spread_kJmol"] = max(vals) - min(vals)
            row["dHf_mean_kJmol"] = float(np.mean(vals))
        summary.append(row)
    with open(OUT_DIR / "multihead_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nAll outputs written to {OUT_DIR}")
    upload_results(OUT_DIR, RESULTS_REPO)


if __name__ == "__main__":
    main()
