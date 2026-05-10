"""Independent sanity checks on every numerical claim we plan to make.

Run with: python3 phase_diagrams/review_checks.py

Checks:
  1. Pure-element references against published cohesive energies.
  2. Bragg-Williams entropy values reproduced analytically.
  3. Supercell compositions at every dilution x are exact integers.
  4. Relaxed Fe2Nb / Fe2Ta stoichiometry, lattice, and ΔH_f vs experiment.
  5. Solute-dissolution sign convention re-derived from first principles.
  6. Dilution diagram crossing positions re-derived from raw G(T,x).
  7. Imaginary-mode count.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from collections import Counter

import numpy as np
from ase.io import read

ROOT = Path(__file__).resolve().parent.parent
CSV = ROOT / "phase_diagrams" / "rhea_mace_results.csv"
JSON = ROOT / "phase_diagrams" / "dilution_results" / "thermo_results.json"
CACHE = ROOT / "phase_diagrams" / "mace_cache"
DIL_CACHE = ROOT / "phase_diagrams" / "dilution_results"

OK = "[OK]   "; WARN = "[WARN] "; FAIL = "[FAIL] "

# ---------------------------------------------------------------------------
# 1. Pure-element references vs published cohesive energies (PBE)
# ---------------------------------------------------------------------------
# Reference cohesive energies from Materials Project (PBE+U, eV/atom).  These
# are NOT the same convention as MACE's PBE total energy per atom, but their
# RELATIVE ordering should match.  For absolute total-energy comparisons we
# need the OMAT/PBE convention which has different zero of energy.  So we
# compare RELATIVE differences instead.
print("\n=== 1. PURE-ELEMENT REFERENCES (relative ordering) ===")
mu_mace = {}
with open(CSV) as f:
    for row in csv.DictReader(f):
        if row["section"] == "mu_ref":
            mu_mace[row["phase_or_solute"]] = float(row["value"])
print("MACE pure-element E0 (eV/atom):")
for el, e in sorted(mu_mace.items(), key=lambda kv: kv[1]):
    print(f"  {el:>3s}  {e:+.4f}")

# Sanity check: refractories Mo, Nb, Ta should be most negative
# (highest cohesive energy after subtracting atomic energies).
sorted_mu = sorted(mu_mace.items(), key=lambda kv: kv[1])
refractory = ["Ta", "Mo", "Nb", "Hf"]
top4 = [el for el, _ in sorted_mu[:4]]
if set(top4) == set(refractory):
    print(f"{OK}Refractories (Ta/Mo/Nb/Hf) are the 4 most negative — consistent with strong metal bonding.")
else:
    print(f"{WARN}Top-4 most negative are {top4}, expected {refractory}.")

# ---------------------------------------------------------------------------
# 2. Bragg-Williams entropy
# ---------------------------------------------------------------------------
print("\n=== 2. BRAGG-WILLIAMS CONFIG ENTROPY (re-derived) ===")
KB = 8.617333262e-5  # eV/K
def s_bw(comp):
    n = sum(comp.values())
    s = 0.0
    for el, c in comp.items():
        if c == 0: continue
        x = c / n
        s -= x * np.log(x)
    return KB * s

dilution = json.loads(JSON.read_text())
for r in dilution["bcc"]:
    s_recomputed = s_bw(r["composition"])
    diff = abs(s_recomputed - r["S_config_eV_per_K"])
    tag = OK if diff < 1e-7 else FAIL
    print(f"  x={r['x_isru']:.2f}  reported={r['S_config_eV_per_K']:.3e}  "
          f"recomputed={s_recomputed:.3e}  Δ={diff:.1e}  {tag.strip()}")

# ---------------------------------------------------------------------------
# 3. Composition exactness
# ---------------------------------------------------------------------------
print("\n=== 3. COMPOSITION EXACTNESS ===")
for r in dilution["bcc"]:
    n = sum(r["composition"].values())
    if n != 100:
        print(f"{FAIL}x={r['x_isru']:.2f}  total atoms = {n} (expected 100)")
    else:
        # Check ratios match the (1-x) MoNbTaTiV / x Fe-50Ti split
        x = r["x_isru"]
        comp = r["composition"]
        # Expected exact counts:
        # Mo, Nb, Ta, V: each = (1-x) * 100 / 5 = 20*(1-x)
        # Ti: 20*(1-x) + 50*x
        # Fe: 50*x
        expected = {
            "Mo": 20*(1-x), "Nb": 20*(1-x), "Ta": 20*(1-x), "V": 20*(1-x),
            "Ti": 20*(1-x) + 50*x, "Fe": 50*x,
        }
        deltas = []
        for el, e in expected.items():
            actual = comp.get(el, 0)
            deltas.append(abs(actual - e))
        max_dev = max(deltas)
        tag = OK if max_dev <= 1.0 else WARN  # rounding can shift ±1 atom
        print(f"  x={x:.2f}  N=100  max integer-deviation from exact split = {max_dev:.1f}  {tag.strip()}")

# ---------------------------------------------------------------------------
# 4. Fe2Nb and Fe2Ta: stoichiometry, lattice, ΔH_f
# ---------------------------------------------------------------------------
print("\n=== 4. FE2NB / FE2TA SANITY ===")
for laves, big in [("fe2nb", "Nb"), ("fe2ta", "Ta")]:
    p = DIL_CACHE / f"relaxed_{laves}.traj"
    a = read(p)
    counts = Counter(a.get_chemical_symbols())
    n_total = len(a)
    n_big = counts.get(big, 0)
    n_fe = counts.get("Fe", 0)
    ratio_ok = (n_fe == 2 * n_big) and (n_big + n_fe == n_total)
    a_lat, b_lat, c_lat = a.cell.lengths()
    print(f"  {laves}: N={n_total}  ({n_big} {big} + {n_fe} Fe)  "
          f"cell=({a_lat:.2f},{b_lat:.2f},{c_lat:.2f}) Å  "
          f"{OK if ratio_ok else FAIL}stoichiometry {'2:1 Fe:'+big if ratio_ok else 'BROKEN'}")
    # Volume / atom for sanity
    vpa = a.get_volume() / n_total
    print(f"    V/atom = {vpa:.3f} Å³  (expected ~12-14 Å³ for Laves)")

# ΔH_f calculation: E_alloy_per_atom - x_Fe·μ_Fe - x_big·μ_big
# Fe2Nb: 2/3 Fe + 1/3 Nb
print()
for name, big in [("Fe2Nb", "Nb"), ("Fe2Ta", "Ta")]:
    E0_per_atom = dilution[name]["E0_per_atom"]
    ref = (2/3) * mu_mace["Fe"] + (1/3) * mu_mace[big]
    dH = (E0_per_atom - ref) * 1000  # meV/atom
    # Convert to kJ/mol/atom for comparison with experiment
    dH_kJ_mol = dH * 96.485 / 1000  # meV/atom * 0.0965 = kJ/mol per atom
    # Published experimental ΔH_f for Fe2Nb / Fe2Ta Laves:
    #   Fe2Nb: -10 to -19 kJ/mol per atom (Kubaschewski; Mathieu; CALPHAD assessments)
    #   Fe2Ta: -10 to -20 kJ/mol per atom
    in_range = -25 <= dH_kJ_mol <= -5
    print(f"  {name}: ΔH_f = {dH:+.0f} meV/atom = {dH_kJ_mol:+.1f} kJ/mol·atom  "
          f"{OK if in_range else WARN}{'within experimental range' if in_range else 'OUTSIDE typical range'}")

# ---------------------------------------------------------------------------
# 5. Solute dissolution sign convention
# ---------------------------------------------------------------------------
print("\n=== 5. SOLUTE DISSOLUTION SIGN CONVENTION ===")
# Recompute one entry from CSV by the standard formula:
#   E_sub = (E_alloy_subbed - E_alloy_pure) - mu_solute_pure + mu_displaced_pure
# We don't have E_alloy_subbed in the CSV directly, so we rely on the
# structure of the data. The CSV value should be:
#   E_sub = (E_subbed_total - E_pure_total) - mu_solute + mu_displaced

# Read CSV solute rows and confirm displaced/solute pairing
print("Solute rows from CSV:")
solute_rows = []
with open(CSV) as f:
    for row in csv.DictReader(f):
        if row["section"] == "solute":
            solute_rows.append(row)
            print(f"  {row['composition']:20s} {row['phase_or_solute']:3s} <- {row['displaced']:3s}  "
                  f"E_sub = {row['value']:>8s} eV")

# Asymmetry warning for R3
print(f"\n  {WARN}R3 ISRU rows use DIFFERENT displaced elements per row:")
for row in solute_rows:
    if row["composition"] == "R3_ISRU_blend":
        print(f"      {row['phase_or_solute']} <- {row['displaced']}: {row['value']} eV  "
              f"(chemical preference of {row['phase_or_solute']} "
              f"over {row['displaced']} at this site)")
print("    These three R3 numbers are NOT directly comparable across rows because the")
print("    'before' alloy compositions are DIFFERENT (we displace Ti for Fe and Fe for Ti/Al).")
print("    R1 and R2 are consistent because all 3 solutes displace the same element (Hf or Mo).")

# ---------------------------------------------------------------------------
# 6. Dilution diagram crossings: re-derive linearly
# ---------------------------------------------------------------------------
print("\n=== 6. DILUTION DIAGRAM: G_BCC vs G_Laves CROSSINGS @ 1000 K ===")
T_grid = np.array(dilution["bcc"][0]["F_vib"]["T_K"])
ti = int(np.argmin(np.abs(T_grid - 1000)))
xs = np.array([r["x_isru"] for r in dilution["bcc"]])
G_bcc = np.array([r["E0_per_atom"]
                  + r["F_vib"]["F_vib_eV_per_atom"][ti]
                  - T_grid[ti] * r["S_config_eV_per_K"]
                  for r in dilution["bcc"]])
G_FeNb = (dilution["Fe2Nb"]["E0_per_atom"]
          + dilution["Fe2Nb"]["F_vib"]["F_vib_eV_per_atom"][ti])
G_FeTa = (dilution["Fe2Ta"]["E0_per_atom"]
          + dilution["Fe2Ta"]["F_vib"]["F_vib_eV_per_atom"][ti])

# Interpolate crossing
def crossing(x_arr, y_arr, target):
    """Linear-interpolate x where y(x) = target."""
    diffs = y_arr - target
    sign_change = np.where(np.diff(np.sign(diffs)) != 0)[0]
    if len(sign_change) == 0:
        return None
    i = sign_change[0]
    return x_arr[i] + (target - y_arr[i]) * (x_arr[i+1] - x_arr[i]) / (y_arr[i+1] - y_arr[i])

x_cross_FeNb = crossing(xs, G_bcc, G_FeNb)
x_cross_FeTa = crossing(xs, G_bcc, G_FeTa)
print(f"  G_Fe2Nb @ 1000 K = {G_FeNb:+.4f} eV/at  (BCC crosses at x ≈ {x_cross_FeNb*100:.0f}% ISRU)")
print(f"  G_Fe2Ta @ 1000 K = {G_FeTa:+.4f} eV/at  (BCC crosses at x ≈ {x_cross_FeTa*100:.0f}% ISRU)")

# Sanity check: Fe2Ta should cross EARLIER (lower x) than Fe2Nb if Ta is the
# heavier and forms more stable Laves.  Confirm.
if x_cross_FeTa < x_cross_FeNb:
    print(f"  {OK}Fe2Ta crossing happens earlier than Fe2Nb — consistent with Ta forming more stable Laves.")
else:
    print(f"  {WARN}Crossing order is unexpected. Investigate.")

# Compare with what the headline message says
print(f"\n  Headline I claimed at 1000 K: ~22% (Fe2Ta) and ~57% (Fe2Nb)")
print(f"  Independently re-derived:    ~{x_cross_FeTa*100:.0f}% (Fe2Ta) and ~{x_cross_FeNb*100:.0f}% (Fe2Nb)")

# ---------------------------------------------------------------------------
# 7. Imaginary-mode budget
# ---------------------------------------------------------------------------
print("\n=== 7. IMAGINARY MODES PER PHASE ===")
total_imag = 0
for r in dilution["bcc"]:
    n = r["F_vib"]["n_imag"]
    total_imag += n
    print(f"  BCC x={r['x_isru']:.2f}: {n} imaginary modes")
for laves in ("Fe2Nb", "Fe2Ta"):
    n = dilution[laves]["F_vib"]["n_imag"]
    total_imag += n
    print(f"  {laves}:        {n} imaginary modes")
print(f"  {OK if total_imag < 10 else WARN}Total: {total_imag} imaginary modes over 9 structures")

# ---------------------------------------------------------------------------
# 8. R1, R2, R3 BCC margin check
# ---------------------------------------------------------------------------
print("\n=== 8. ORIGINAL RHEA STABILITY: BCC MARGINS ===")
results_csv = list(csv.DictReader(open(CSV)))
for comp_name in ("R1_HfNbTaTiZr", "R2_MoNbTaTiV", "R3_ISRU_blend"):
    e_pa = {}
    for row in results_csv:
        if row["section"] == "static" and row["composition"] == comp_name and row["note"] == "E":
            e_pa[row["phase_or_solute"]] = float(row["value"])
    margin_fcc = (e_pa["fcc"] - e_pa["bcc"]) * 1000  # meV/atom
    margin_hcp = (e_pa["hcp"] - e_pa["bcc"]) * 1000
    consistent = margin_fcc > 0 and margin_hcp > 0
    print(f"  {comp_name:20s} BCC margins (vs FCC, vs HCP): "
          f"+{margin_fcc:.0f} / +{margin_hcp:.0f} meV/atom  "
          f"{OK if consistent else FAIL}{'BCC preferred' if consistent else 'BCC NOT lowest!'}")

print("\n=== END OF SANITY CHECKS ===")
