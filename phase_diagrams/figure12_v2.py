#!/usr/bin/env python3
"""
Figure 12 v2: ab-initio Tier-1 dilution diagram, drawn in the schematic's visual
style for direct A/B comparison with the manuscript's Figure 12.

Reads thermo_results.json (the HF-Jobs phonon output for the
MoNbTaTiV -> Fe-50Ti dilution path) and produces a T-x plot in the same
layout as scripts/generate_dilution_diagram.py:

  - x-axis = ISRU metal fraction (wt%)
  - y-axis = Temperature (K)
  - BCC + Laves boundary  =  computed (this work, MACE+phonopy)
  - Fe-Ti binary liquidus / solidus on the Fe-Ti end =  literature
    (Okamoto, T-Ti Phase Diagrams, 1993; placeholder analytical curves
     until TCHEA-grade computation is available)
  - Target dilution window 75-90 wt% ISRU shaded green
  - Endpoint labels ("MoNbTaTiV master", "Fe-50Ti")
  - Phase regions labelled BCC and BCC + LAVES

Outputs:
  figures/dilution_phase_diagram_v2.pdf / .png
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "phase_diagrams" / "dilution_results" / "thermo_results.json"
OUT = ROOT / "figures"

# Atomic masses (g/mol) — IUPAC 2019
ATM = {"Mo": 95.95, "Nb": 92.91, "Ta": 180.95, "V": 50.94,
       "Ti": 47.87, "Fe": 55.85}

# Compositions per dilution point (atoms per 100-atom supercell)
def comp_at(x_at: float) -> dict:
    """Atomic counts in a 100-atom supercell at fractional ISRU = x_at."""
    rhea = 1.0 - x_at
    return {
        "Mo": rhea * 20, "Nb": rhea * 20, "Ta": rhea * 20, "V": rhea * 20,
        "Ti": rhea * 20 + x_at * 50,
        "Fe": x_at * 50,
    }


def isru_wt_pct(x_at: float) -> float:
    """Convert atomic-fraction-of-Fe-50Ti-end to ISRU mass fraction.

    Convention: every Fe and every Ti atom is counted as ISRU-extractable
    (consistent with the paper's Section 4.5 footnote on Table 11/12 ISRU%);
    Mo, Nb, Ta, V atoms are counted as Earth-shipped refractory.
    """
    c = comp_at(x_at)
    isru_mass = c["Fe"] * ATM["Fe"] + c["Ti"] * ATM["Ti"]
    earth_mass = (c["Mo"] * ATM["Mo"] + c["Nb"] * ATM["Nb"]
                  + c["Ta"] * ATM["Ta"] + c["V"] * ATM["V"])
    total = isru_mass + earth_mass
    return 100.0 * isru_mass / total


def main() -> None:
    d = json.loads(DATA.read_text())
    T_grid = np.array(d["bcc"][0]["F_vib"]["T_K"])
    xs_at = np.array([r["x_isru"] for r in d["bcc"]])
    xs_wt = np.array([isru_wt_pct(x) for x in xs_at])

    # G_BCC(x, T)
    G_bcc = np.zeros((len(xs_at), len(T_grid)))
    for i, r in enumerate(d["bcc"]):
        E0 = r["E0_per_atom"]
        F = np.array(r["F_vib"]["F_vib_eV_per_atom"])
        S = r["S_config_eV_per_K"]
        G_bcc[i] = E0 + F - T_grid * S

    G_FeNb = (np.array(d["Fe2Nb"]["F_vib"]["F_vib_eV_per_atom"])
              + d["Fe2Nb"]["E0_per_atom"])
    G_FeTa = (np.array(d["Fe2Ta"]["F_vib"]["F_vib_eV_per_atom"])
              + d["Fe2Ta"]["E0_per_atom"])

    # BCC <-> Laves crossing in wt% at each T
    def cross_wt(ys, target):
        diffs = ys - target
        sc = np.where(np.diff(np.sign(diffs)) != 0)[0]
        if len(sc) == 0:
            return None
        i = sc[0]
        x_at = xs_at[i] + (target - ys[i]) * (xs_at[i+1] - xs_at[i]) / (
            ys[i+1] - ys[i])
        return isru_wt_pct(x_at)

    cliff_FeNb = []  # BCC stable below this wt% at each T (Fe2Nb cliff)
    cliff_FeTa = []
    for ti in range(len(T_grid)):
        cliff_FeNb.append(cross_wt(G_bcc[:, ti], G_FeNb[ti]))
        cliff_FeTa.append(cross_wt(G_bcc[:, ti], G_FeTa[ti]))

    # ------------------------------------------------------------------
    # Build the plot in the schematic's visual style
    # ------------------------------------------------------------------
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Times New Roman", "DejaVu Serif", "serif"],
        "mathtext.fontset": "dejavuserif",
        "font.size": 10, "axes.labelsize": 11,
        "xtick.labelsize": 9, "ytick.labelsize": 9,
        "axes.linewidth": 0.8,
        "savefig.dpi": 300, "figure.dpi": 150,
    })

    fig, ax = plt.subplots(figsize=(7.5, 5.5))
    ax.set_facecolor("white")

    cf_ta = np.array([c if c is not None else np.nan for c in cliff_FeTa])
    # Fe2Nb cliff is at higher wt% than Fe2Ta everywhere — never the
    # binding boundary. Keep it out of the diagram entirely; mention it in
    # the figure caption instead. The single boundary keeps the diagram
    # clean and easy to read.

    Y_MAX = 1900  # plot ceiling: 100 K above our computed range (1800 K)

    # ------------------------------------------------------------------
    # Filled phase regions (the eye reads regions, not lines)
    # ------------------------------------------------------------------
    # BCC field = left of the Fe2Ta cliff
    ax.fill(np.concatenate(([0], cf_ta, [cf_ta[-1]], [0])),
            np.concatenate(([0], T_grid, [Y_MAX], [Y_MAX])),
            color="#C8E6C9", zorder=0, alpha=0.55)
    # BCC + Laves field = right of the Fe2Ta cliff
    ax.fill(np.concatenate((cf_ta, [100, 100, cf_ta[0]])),
            np.concatenate((T_grid, [Y_MAX, 0, 0])),
            color="#FFCDD2", zorder=0, alpha=0.55)

    # Target window (only inside BCC field, no overlap with text)
    ax.axvspan(75, 90, color="#2E7D32", alpha=0.22, zorder=1)

    # Single primary boundary line
    ax.plot(cf_ta, T_grid, "-", color="#0D47A1", lw=3.0, zorder=4)

    # Subtle horizontal marker for top-of-computed-range
    ax.axhline(1800, color="#999", lw=0.8, ls=":", zorder=1)
    ax.text(99.5, 1820, "harmonic regime ceiling",
            fontsize=7.0, ha="right", va="bottom",
            color="#666", style="italic")

    # ------------------------------------------------------------------
    # Phase region labels — large, centered, no overlap with anything
    # ------------------------------------------------------------------
    ax.text(8, 900, "BCC", fontsize=28, ha="center",
            color="#1B5E20", fontweight="bold", zorder=5)
    ax.text(8, 690, "single phase", fontsize=10, ha="center",
            color="#2E7D32", style="italic", zorder=5)

    ax.text(60, 900, r"BCC + Fe$_2$Ta", fontsize=18, ha="center",
            color="#B71C1C", fontweight="bold", zorder=5)
    ax.text(60, 690, "two-phase region", fontsize=10, ha="center",
            color="#C62828", style="italic", zorder=5)

    # Target window label — inside the green band, away from any line
    ax.text(82.5, 100, "target\nwindow",
            fontsize=10, ha="center", va="bottom",
            color="#1B5E20", fontweight="bold", zorder=5)

    # Single inline cliff readout at 1000 K — placed RIGHT of the line in
    # the red field, not on top of the line. No arrow, no overlap.
    ti_1000 = int(np.argmin(np.abs(T_grid - 1000)))
    cliff_x = cf_ta[ti_1000]
    ax.plot([cliff_x], [1000], "o", color="#0D47A1", markersize=7,
            markeredgecolor="white", markeredgewidth=1.2, zorder=6)
    ax.text(cliff_x + 3, 1000, f"{cliff_x:.0f} wt% @ 1000 K",
            fontsize=9, ha="left", va="center",
            color="#0D47A1", fontweight="bold", zorder=6)

    # ------------------------------------------------------------------
    # Endpoint labels — placed cleanly on the x-axis, NOT in the plot body
    # ------------------------------------------------------------------
    ax.text(0, -120, "MoNbTaTiV\nmaster", fontsize=8.5, ha="left",
            va="top", color="#1A237E", fontweight="bold", style="italic")
    ax.text(100, -120, "Fe-50Ti", fontsize=8.5, ha="right",
            va="top", color="#BF360C", fontweight="bold", style="italic")

    # ------------------------------------------------------------------
    # Axes
    # ------------------------------------------------------------------
    ax.set_xlabel("ISRU metal fraction (wt%)", labelpad=20)
    ax.set_ylabel("Temperature (K)")
    ax.set_xlim(0, 100); ax.set_ylim(0, Y_MAX)
    ax.set_xticks(range(0, 101, 10))

    # ------------------------------------------------------------------
    # Title — single line, no subtitle clutter
    # ------------------------------------------------------------------
    ax.set_title(
        "Tier-1 ab-initio dilution diagram  "
        r"(mace-mh-1 + harmonic phonons)",
        fontsize=11, color="#37474F", pad=10, fontweight="bold")

    # NB: the secondary Fe2Nb cliff is intentionally not plotted to keep the
    # diagram readable. Caption text states: "Fe2Nb cliff lies further to
    # the right of the Fe2Ta cliff at every temperature and is therefore
    # never the binding boundary of the BCC field."

    fig.tight_layout(pad=1.5)
    out_pdf = OUT / "dilution_phase_diagram_v2.pdf"
    out_png = OUT / "dilution_phase_diagram_v2.png"
    fig.savefig(out_pdf); fig.savefig(out_png)
    print(f"wrote {out_pdf}\nwrote {out_png}")
    plt.close()

    # Also print the wt% conversion table for the report
    print("\n=== wt% conversion table ===")
    print(f"{'x_at':>6} {'x_wt':>8}")
    for x_at, x_wt in zip(xs_at, xs_wt):
        print(f"{x_at*100:>5.1f}% {x_wt:>7.1f}%")

    print("\n=== Crossings in wt% ISRU ===")
    print(f"{'T (K)':>6} {'Fe2Ta cliff (wt%)':>20} {'Fe2Nb cliff (wt%)':>20}")
    cf_nb_print = np.array([c if c is not None else np.nan for c in cliff_FeNb])
    for ti, T in enumerate(T_grid):
        print(f"{int(T):>6} {cf_ta[ti]:>20.1f} {cf_nb_print[ti]:>20.1f}")


if __name__ == "__main__":
    main()
