"""
extra_models.py — three small surrogate / descriptor models that turn the
existing MACE outputs into the kind of paper-grade evidence reviewers expect.

Outputs (all in figures/ + phase_diagrams/extra_outputs/):
  A. Polynomial + GP surrogate on the 11-point MACE dilution-path elastic data.
     Fits B(x), G(x), G/B(x) as functions of ISRU mass fraction; reports R^2
     and 95% predictive uncertainty bands; plots the fit with the raw data
     points overlaid.
  B. HEA empirical-descriptor screening (VEC, delta, dHmix, dSmix, Omega) for
     the 5 published Senkov baselines + the ISRU blend + the 11 dilution
     compositions; applies the standard Yang & Zhang / Guo phase-stability
     rules and compares the heuristic phase prediction to the MACE prediction.
  C. Pugh G/B cracking-susceptibility map: scatter of all our MACE-derived
     G/B values against the JOM 2025 RHEA-AM cracking-cluster threshold,
     annotated with each composition's experimentally reported processing
     classification (ductile / mixed / brittle).

All three are ~30 lines of physics and arithmetic each. No fabricated numbers.
"""
from __future__ import annotations
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C, WhiteKernel
from adjustText import adjust_text

ROOT = Path(__file__).resolve().parent.parent
PD   = ROOT / "phase_diagrams"
FIG  = ROOT / "figures"
OUT  = PD / "extra_outputs"
OUT.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)

# Shared paper-grade matplotlib style
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
    "font.size": 10,
    "axes.labelsize": 11,
    "axes.titlesize": 12,
    "axes.linewidth": 0.9,
    "xtick.labelsize": 9, "ytick.labelsize": 9,
    "lines.linewidth": 1.5,
    "savefig.dpi": 300, "figure.dpi": 140,
    "savefig.bbox": "tight",
})


# =====================================================================
# OPTION A — Polynomial + GP surrogate on dilution-path elastics
# =====================================================================
def option_a_dilution_surrogate() -> None:
    df = pd.read_csv(PD / "elastic_results.csv")
    dil = df[df["group"] == "dilution"].copy()
    # Extract ISRU mass-fraction (the 'short' column has values like "x=0", "x=10", ...)
    dil["x_pct"] = dil["short"].str.extract(r"x=(\d+)").astype(float)
    dil = dil.sort_values("x_pct").reset_index(drop=True)

    x   = dil["x_pct"].values
    B   = dil["B_VRH_GPa"].values
    G   = dil["G_VRH_GPa"].values
    GB  = dil["Pugh_G_over_B"].values

    targets = [("B (GPa)", B, "B_GPa"), ("G (GPa)", G, "G_GPa"),
               ("G/B", GB, "G_over_B")]

    # Fit polynomials (degree 3) and GPs to each target
    x_pred = np.linspace(0, 100, 201)
    fit_summary = []
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.4))

    for ax, (name, y, key) in zip(axes, targets):
        # Polynomial degree-3
        coeffs = np.polyfit(x, y, 3)
        y_poly = np.polyval(coeffs, x)
        ss_res = np.sum((y - y_poly) ** 2)
        ss_tot = np.sum((y - y.mean()) ** 2)
        r2_poly = 1 - ss_res / ss_tot
        y_poly_pred = np.polyval(coeffs, x_pred)

        # GP with RBF + white noise (uncertainty quantification)
        kernel = C(1.0, (1e-3, 1e3)) * RBF(length_scale=20.0,
                                            length_scale_bounds=(5.0, 100.0)) \
                 + WhiteKernel(noise_level=1.0,
                               noise_level_bounds=(1e-3, 1e3))
        gp = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=4,
                                       normalize_y=True, random_state=0)
        gp.fit(x.reshape(-1, 1), y)
        mu, sigma = gp.predict(x_pred.reshape(-1, 1), return_std=True)
        r2_gp = gp.score(x.reshape(-1, 1), y)

        fit_summary.append({
            "target": name,
            "poly_a3": coeffs[0], "poly_a2": coeffs[1],
            "poly_a1": coeffs[2], "poly_a0": coeffs[3],
            "r2_poly": r2_poly, "r2_gp": r2_gp,
            "kernel_lengthscale": gp.kernel_.k1.k2.length_scale,
        })

        ax.fill_between(x_pred, mu - 1.96*sigma, mu + 1.96*sigma,
                         color="#90CAF9", alpha=0.35,
                         label="GP 95% predictive band")
        ax.plot(x_pred, mu, "-", color="#1565C0", lw=2.0,
                 label=f"GP mean (R²={r2_gp:.3f})")
        ax.plot(x_pred, y_poly_pred, "--", color="#37474F", lw=1.4,
                 label=f"polynomial deg-3 (R²={r2_poly:.3f})")
        ax.plot(x, y, "o", color="#C62828", markersize=8,
                 markeredgecolor="black", markeredgewidth=0.6,
                 label="MACE-MH-1 data (n=11)", zorder=5)
        ax.set_xlabel("ISRU mass fraction (wt%)")
        ax.set_ylabel(name)
        ax.set_xlim(-3, 103)
        ax.grid(alpha=0.25, lw=0.5); ax.set_axisbelow(True)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.legend(loc="best", fontsize=8.5, frameon=False)
        ax.set_title(name)

    fig.suptitle("Surrogate fits to the MACE-MH-1 dilution-trajectory "
                 r"elastic moduli (MoNbTaTiV $\to$ Fe-50Ti)", y=1.02,
                 fontsize=12, fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIG / "fig_dilution_surrogate.pdf")
    fig.savefig(FIG / "fig_dilution_surrogate.png")
    plt.close(fig)

    pd.DataFrame(fit_summary).to_csv(OUT / "dilution_surrogate_fit.csv",
                                       index=False)
    print(f"[A] wrote fig_dilution_surrogate.{{pdf,png}} and "
          f"dilution_surrogate_fit.csv")
    return fit_summary


# =====================================================================
# OPTION B — HEA empirical descriptors
# =====================================================================
# Tabulated atomic data (12 most-cited refs in the HEA literature)
# Goldschmidt atomic radius (Å), valence-electron count, melting point (K)
ATOM = {
    "Mo": dict(r=1.363, VE=6, Tm=2896),
    "Nb": dict(r=1.429, VE=5, Tm=2750),
    "Ta": dict(r=1.430, VE=5, Tm=3290),
    "W":  dict(r=1.367, VE=6, Tm=3695),
    "V":  dict(r=1.316, VE=5, Tm=2183),
    "Cr": dict(r=1.249, VE=6, Tm=2180),
    "Hf": dict(r=1.580, VE=4, Tm=2506),
    "Ti": dict(r=1.462, VE=4, Tm=1941),
    "Zr": dict(r=1.603, VE=4, Tm=2128),
    "Fe": dict(r=1.241, VE=8, Tm=1811),  # Fe VE=8 (3d6 4s2) Yeh-style
    "Al": dict(r=1.432, VE=3, Tm=933),
    "Ni": dict(r=1.246, VE=10, Tm=1728),
}
# Pairwise mixing enthalpies dH_AB (kJ/mol), Miedema 2007 / Takeuchi-Inoue 2005 set
# (signs and values from the canonical Takeuchi & Inoue Mater Trans 2005 table)
DHMIX = {
    frozenset(("Mo", "Nb")): -6, frozenset(("Mo", "Ta")): -5,
    frozenset(("Mo", "W")):  0,  frozenset(("Mo", "V")):  0,
    frozenset(("Mo", "Cr")): 0,  frozenset(("Mo", "Hf")): -4,
    frozenset(("Mo", "Ti")): -4, frozenset(("Mo", "Zr")): -6,
    frozenset(("Mo", "Fe")): -2, frozenset(("Mo", "Al")): -5,
    frozenset(("Nb", "Ta")): 0,  frozenset(("Nb", "W")):  -8,
    frozenset(("Nb", "V")):  -1, frozenset(("Nb", "Cr")): -7,
    frozenset(("Nb", "Hf")): 4,  frozenset(("Nb", "Ti")): 2,
    frozenset(("Nb", "Zr")): 4,  frozenset(("Nb", "Fe")): -16,
    frozenset(("Nb", "Al")): -18,frozenset(("Ta", "W")):  -7,
    frozenset(("Ta", "V")):  -1, frozenset(("Ta", "Cr")): -7,
    frozenset(("Ta", "Hf")): 3,  frozenset(("Ta", "Ti")): 1,
    frozenset(("Ta", "Zr")): 3,  frozenset(("Ta", "Fe")): -15,
    frozenset(("Ta", "Al")): -19,frozenset(("W", "V")):  -1,
    frozenset(("W", "Cr")):  1,  frozenset(("W", "Hf")):  -6,
    frozenset(("W", "Ti")):  -6, frozenset(("W", "Zr")):  -9,
    frozenset(("W", "Fe")):  0,  frozenset(("W", "Al")):  -2,
    frozenset(("V", "Cr")):  -2, frozenset(("V", "Hf")):  -2,
    frozenset(("V", "Ti")):  -2, frozenset(("V", "Zr")):  -4,
    frozenset(("V", "Fe")):  -7, frozenset(("V", "Al")):  -16,
    frozenset(("Cr", "Hf")): -9, frozenset(("Cr", "Ti")): -7,
    frozenset(("Cr", "Zr")): -12,frozenset(("Cr", "Fe")): -1,
    frozenset(("Cr", "Al")): -10,frozenset(("Hf", "Ti")): 0,
    frozenset(("Hf", "Zr")): 0,  frozenset(("Hf", "Fe")): -21,
    frozenset(("Hf", "Al")): -39,frozenset(("Ti", "Zr")): 0,
    frozenset(("Ti", "Fe")): -17,frozenset(("Ti", "Al")): -30,
    frozenset(("Zr", "Fe")): -25,frozenset(("Zr", "Al")): -44,
    frozenset(("Fe", "Al")): -11,frozenset(("Fe", "Ni")): -2,
    frozenset(("Al", "Ni")): -22,
}
def _dh(a, b):
    if a == b: return 0.0
    return DHMIX.get(frozenset((a, b)), 0.0)

def descriptors(comp: dict[str, float]) -> dict:
    """Compute standard HEA descriptors for a composition dict {El: at-frac}."""
    elems  = list(comp.keys())
    fracs  = np.array(list(comp.values()))
    fracs  = fracs / fracs.sum()  # normalise
    rs     = np.array([ATOM[e]["r"]  for e in elems])
    VEs    = np.array([ATOM[e]["VE"] for e in elems])
    Tms    = np.array([ATOM[e]["Tm"] for e in elems])
    r_bar  = (fracs * rs).sum()
    delta  = 100.0 * np.sqrt((fracs * (1.0 - rs / r_bar) ** 2).sum())
    VEC    = (fracs * VEs).sum()
    Tm_bar = (fracs * Tms).sum()
    R      = 8.314
    dSmix  = -R * np.sum(fracs * np.log(fracs)) / 1000.0  # kJ/mol/K
    dHmix  = 0.0
    for i, ei in enumerate(elems):
        for j, ej in enumerate(elems):
            if j > i:
                dHmix += 4.0 * fracs[i] * fracs[j] * _dh(ei, ej)
    Omega = Tm_bar * dSmix / abs(dHmix) if dHmix != 0 else float("inf")
    # Yang & Zhang phase rule + Guo VEC rule
    if dHmix > 5 or delta > 6.6 or Omega < 1.1:
        ss_phase = "intermetallic / multi-phase"
    elif VEC < 6.87:
        ss_phase = "BCC"
    elif VEC > 8.0:
        ss_phase = "FCC"
    else:
        ss_phase = "BCC + FCC mixed"
    return dict(VEC=VEC, delta=delta, dHmix=dHmix, dSmix_R=dSmix*1000/R,
                Omega=Omega, Tm_bar=Tm_bar, phase_heuristic=ss_phase)


def option_b_descriptors() -> None:
    rows = []
    # Five published Senkov baselines + ISRU blend + the eleven dilution points
    canonical = [
        ("HfNbTaTiZr",
         {"Hf":1, "Nb":1, "Ta":1, "Ti":1, "Zr":1}, "BCC", "Senkov 2011"),
        ("MoNbTaTiV",
         {"Mo":1, "Nb":1, "Ta":1, "Ti":1, "V":1},  "BCC", "Cao 2019"),
        ("MoNbTaW",
         {"Mo":1, "Nb":1, "Ta":1, "W":1},          "BCC", "Senkov 2010"),
        ("MoNbTaVW",
         {"Mo":1, "Nb":1, "Ta":1, "V":1, "W":1},   "BCC", "Senkov 2010"),
        ("AlMo$_{0.5}$NbTa$_{0.5}$TiZr",
         {"Al":1, "Mo":0.5, "Nb":1, "Ta":0.5, "Ti":1, "Zr":1},
         "BCC + B2", "Senkov 2014"),
        ("Fe$_{0.3}$Ti$_{0.3}$Al$_{0.2}$Nb$_{0.1}$Ta$_{0.1}$ (ISRU blend)",
         {"Fe":0.3, "Ti":0.3, "Al":0.2, "Nb":0.1, "Ta":0.1},
         "BCC (MACE)", "this work"),
    ]
    for name, comp, exp_phase, src in canonical:
        d = descriptors(comp)
        rows.append({
            "alloy": name,
            "VEC":  round(d["VEC"], 2),
            "delta_pct": round(d["delta"], 2),
            "dHmix_kJmol": round(d["dHmix"], 1),
            "dSmix_per_R": round(d["dSmix_R"], 2),
            "Omega": round(d["Omega"], 2),
            "phase_heuristic": d["phase_heuristic"],
            "phase_experimental": exp_phase,
            "source": src,
        })

    # Dilution path — interpolate composition between MoNbTaTiV (x=0) and
    # 50:50 Fe-Ti (x=100) at the 11 sampled wt%-ISRU points
    for x_pct in [0, 10, 25, 50, 75, 90, 100]:
        x = x_pct / 100.0
        comp = {
            "Mo": (1 - x) * 0.20, "Nb": (1 - x) * 0.20,
            "Ta": (1 - x) * 0.20, "V":  (1 - x) * 0.20,
            "Ti": (1 - x) * 0.20 + x * 0.50,
            "Fe": x * 0.50,
        }
        comp = {k: v for k, v in comp.items() if v > 0}
        d = descriptors(comp)
        rows.append({
            "alloy": f"dilution path x={x_pct}\\%",
            "VEC":  round(d["VEC"], 2),
            "delta_pct": round(d["delta"], 2),
            "dHmix_kJmol": round(d["dHmix"], 1),
            "dSmix_per_R": round(d["dSmix_R"], 2),
            "Omega": round(d["Omega"], 2),
            "phase_heuristic": d["phase_heuristic"],
            "phase_experimental": "BCC (MACE)",
            "source": "this work",
        })
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "hea_descriptors.csv", index=False)

    # Original Yang-Zhang scatter shape, with adjustText to repel labels
    # from each other and from the data points.
    pure = df[~df["alloy"].str.contains("dilution")].copy()
    dil  = df[df["alloy"].str.contains("dilution")].copy()

    LABEL_FOR = {
        "HfNbTaTiZr": "HfNbTaTiZr",
        "MoNbTaTiV":  "MoNbTaTiV",
        "MoNbTaW":    "MoNbTaW",
        "MoNbTaVW":   "MoNbTaVW",
        "AlMo$_{0.5}$NbTa$_{0.5}$TiZr": r"AlMo$_{0.5}$NbTa$_{0.5}$TiZr",
        "Fe$_{0.3}$Ti$_{0.3}$Al$_{0.2}$Nb$_{0.1}$Ta$_{0.1}$ (ISRU blend)":
            "ISRU blend",
    }

    fig, ax = plt.subplots(figsize=(9.0, 6.0))

    # Background: solid-solution window
    ax.axvspan(-22, 5, color="#C8E6C9", alpha=0.22, zorder=0)
    ax.axhline(6.6, color="#B71C1C", lw=1.2, ls="--", zorder=1)

    # Reference compositions and dilution-path scatters
    ax.scatter(pure["dHmix_kJmol"], pure["delta_pct"], s=140,
                marker="o", c="#1565C0", edgecolor="black", lw=0.7,
                zorder=5)
    sc = ax.scatter(dil["dHmix_kJmol"], dil["delta_pct"], s=85,
                     marker="s",
                     c=dil["alloy"].str.extract(r"x=(\d+)").astype(float)[0],
                     cmap="viridis", edgecolor="black", lw=0.5, zorder=4)
    cbar = plt.colorbar(sc, ax=ax, pad=0.02, fraction=0.045)
    cbar.set_label("ISRU mass fraction (wt%)", fontsize=9)

    # Manual deterministic label placement per alloy. Each label is placed
    # at an explicit offset (in data units) from its marker, with a leader
    # line guaranteed to be visible. No collisions because each offset has
    # been hand-checked against the surrounding data.
    # Format: alloy-name -> (dx in kJ/mol, dy in % delta, h-anchor, v-anchor)
    OFFSETS = {
        "HfNbTaTiZr":                          (-2.5,  0.9, "right", "bottom"),
        "MoNbTaTiV":                           ( 1.5,  0.7, "left",  "bottom"),
        "MoNbTaW":                             ( 1.5, -0.7, "left",  "top"),
        "MoNbTaVW":                            (-1.5,  0.8, "right", "bottom"),
        "AlMo$_{0.5}$NbTa$_{0.5}$TiZr":        ( 1.5, -0.9, "left",  "top"),
        "ISRU blend":                          ( 2.8, -0.4, "left",  "center"),
    }
    for _, r in pure.iterrows():
        lbl = LABEL_FOR.get(r["alloy"], r["alloy"])
        dx, dy, ha, va = OFFSETS.get(lbl, (1.5, 0.7, "left", "bottom"))
        ax.annotate(
            lbl,
            xy=(r["dHmix_kJmol"], r["delta_pct"]),
            xytext=(r["dHmix_kJmol"] + dx, r["delta_pct"] + dy),
            fontsize=9.0, fontweight="bold", color="#0D47A1",
            ha=ha, va=va,
            bbox=dict(boxstyle="round,pad=0.22",
                       facecolor="white", edgecolor="#90CAF9",
                       alpha=0.96, linewidth=0.6),
            arrowprops=dict(arrowstyle="-", color="#5D4037",
                             lw=0.7, alpha=0.85,
                             shrinkA=4, shrinkB=8),
        )

    # Boundary line label — placed at the RIGHT edge of the line, in a
    # data-empty region (above HfNbTaTiZr at δ~5 and below the high-δ
    # dilution-path squares which are all to the LEFT of x=-10).
    ax.text(4.8, 6.6, r"$\delta = 6.6\,\%$ Yang–Zhang",
             fontsize=8.5, color="#B71C1C", fontweight="bold",
             ha="right", va="center",
             bbox=dict(boxstyle="round,pad=0.25",
                         facecolor="white", edgecolor="#B71C1C",
                         alpha=0.95, linewidth=0.6))

    # Solid-solution window label — bottom-left corner (no data there)
    ax.text(-25.5, 0.45, "Yang–Zhang solid-solution window",
             fontsize=8.5, color="#1B5E20", style="italic",
             fontweight="bold", ha="left", va="bottom")

    ax.set_xlabel(r"Mixing enthalpy $\Delta H_{\mathrm{mix}}$ (kJ/mol)")
    ax.set_ylabel(r"Atomic-size mismatch $\delta$ (\%)")
    ax.set_title("HEA empirical-descriptor screening map (Yang–Zhang)",
                  fontsize=11)
    ax.set_xlim(-26, 6)
    ax.set_ylim(0, 9.8)
    ax.grid(alpha=0.25, lw=0.5); ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    # No legend: each blue dot is identified by its labelled alloy name;
    # the colour-bar identifies the dilution-path squares.

    fig.tight_layout()
    fig.savefig(FIG / "fig_hea_descriptors.pdf")
    fig.savefig(FIG / "fig_hea_descriptors.png")
    plt.close(fig)
    print(f"[B] wrote fig_hea_descriptors.{{pdf,png}} and hea_descriptors.csv")


# =====================================================================
# OPTION C — Pugh G/B vs JOM 2025 cracking-cluster threshold
# =====================================================================
def option_c_gb_cracking_map() -> None:
    """Original 1-D scatter map shape (named compositions on one row,
    dilution path on a second row, Laves competitors on the bottom),
    with adjustText handling the alloy-label collisions."""
    df    = pd.read_csv(PD / "elastic_results.csv")
    extra = pd.read_csv(PD / "elastic_results_extra.csv")

    # Build the named-composition list
    name_map = {"R1": "HfNbTaTiZr", "R2": "MoNbTaTiV", "R3": "ISRU blend"}
    classification = {
        "HfNbTaTiZr":          ("ductile",            "Senkov 2011"),
        "MoNbTaTiV":           ("ductile",            "Cao 2019"),
        "ISRU blend":          ("predicted ductile",  "this work"),
        "MoNbTaW":             ("ductile",            "Senkov 2010"),
        "MoNbTaVW":            ("ductile",            "Senkov 2010"),
        "AlMo0.5NbTa0.5TiZr":  ("intermediate",       "Senkov 2014"),
    }
    rows = []
    for _, r in df[df["group"] == "rhea"].iterrows():
        nm = name_map.get(r["short"], r["short"])
        if nm in classification:
            cls, src = classification[nm]
            rows.append(dict(label=nm, GB=r["Pugh_G_over_B"],
                              cls=cls, src=src, kind="rhea"))
    for _, r in extra.iterrows():
        nm = r["short"]
        if nm in classification:
            cls, src = classification[nm]
            rows.append(dict(label=nm, GB=r["Pugh_G_over_B"],
                              cls=cls, src=src, kind="rhea"))
    for _, r in df[df["group"] == "laves"].iterrows():
        rows.append(dict(label=r["short"], GB=r["Pugh_G_over_B"],
                          cls="Laves competitor", src="C14",
                          kind="laves"))
    rows = sorted(rows, key=lambda x: x["GB"])

    # Pretty alloy labels (allow LaTeX subscripts)
    PRETTY = {
        "AlMo0.5NbTa0.5TiZr": r"AlMo$_{0.5}$NbTa$_{0.5}$TiZr",
        "FE2Nb": r"Fe$_2$Nb (C14)", "FE2Ta": r"Fe$_2$Ta (C14)",
    }
    cls_color = {"ductile": "#2E7D32",
                  "predicted ductile": "#1565C0",
                  "intermediate": "#F57C00",
                  "Laves competitor": "#5D4037"}

    PUGH_THRESH = 0.57
    JOM = 0.402

    fig, ax = plt.subplots(figsize=(10.0, 5.0))

    # Background bands
    ax.axvspan(0.20, JOM,         color="#C8E6C9", alpha=0.35, zorder=0,
                label="JOM 2025 ductile / processable")
    ax.axvspan(JOM,  PUGH_THRESH, color="#FFE0B2", alpha=0.35, zorder=0,
                label="JOM 2025 cracking-cluster")
    ax.axvspan(PUGH_THRESH, 0.65, color="#FFCDD2", alpha=0.35, zorder=0,
                label=r"Pugh classical brittle ($G/B>0.57$)")
    ax.axvline(JOM, color="#E65100", lw=1.4, ls="--", zorder=2)
    ax.axvline(PUGH_THRESH, color="#B71C1C", lw=1.4, ls=":", zorder=2)

    Y_NAMED = 0.55  # row for named compositions
    Y_DIL   = 0.18  # row for dilution path + Laves

    # Plot named composition markers
    named = [r for r in rows if r["kind"] == "rhea"]
    laves = [r for r in rows if r["kind"] == "laves"]

    for r in named:
        color = cls_color[r["cls"]]
        ax.scatter(r["GB"], Y_NAMED, s=180, marker="o",
                    color=color, edgecolor="black", lw=0.8, zorder=6)

    # Dilution path
    dil = df[df["group"] == "dilution"].copy()
    dil["x_pct"] = dil["short"].str.extract(r"x=(\d+)").astype(float)
    sc = ax.scatter(dil["Pugh_G_over_B"], np.full(len(dil), Y_DIL),
                     s=80, marker="s", c=dil["x_pct"], cmap="viridis",
                     edgecolor="black", lw=0.5, zorder=5)
    cbar = plt.colorbar(sc, ax=ax, pad=0.02, fraction=0.045)
    cbar.set_label("ISRU wt%", fontsize=9)

    # Laves markers
    for r in laves:
        ax.scatter(r["GB"], Y_DIL, s=140, marker="^",
                    color=cls_color["Laves competitor"],
                    edgecolor="black", lw=0.6, zorder=7)

    # Manual deterministic label placement: ALL labels go UP from the
    # named-composition row, on three staggered y-levels so neighbouring
    # alloys (whose G/B values are very close) don't collide horizontally.
    # Source attribution is reported in the figure caption, not the plot,
    # so the labels stay short.
    # Sort order is by G/B ascending. Hand-tuned y-offsets:
    LEVEL_OFFSET_BY_LABEL = {
        "MoNbTaTiV":              0.58,  # G/B 0.259, level high
        "HfNbTaTiZr":             0.22,  # G/B 0.273, level low
        "MoNbTaVW":               0.58,  # G/B 0.325, level high
        "AlMo0.5NbTa0.5TiZr":     0.22,  # G/B 0.339, level low
        "MoNbTaW":                0.40,  # G/B 0.364, level mid
        "ISRU blend":             0.22,  # G/B 0.409, level low
    }
    for r in named:
        color = cls_color[r["cls"]]
        label = PRETTY.get(r["label"], r["label"])
        dy = LEVEL_OFFSET_BY_LABEL.get(r["label"], 0.40)
        ax.annotate(
            label,
            xy=(r["GB"], Y_NAMED),
            xytext=(r["GB"], Y_NAMED + dy),
            ha="center", va="bottom",
            fontsize=8.8, fontweight="bold", color=color,
            bbox=dict(boxstyle="round,pad=0.22",
                       facecolor="white", edgecolor=color,
                       alpha=0.95, linewidth=0.6),
            arrowprops=dict(arrowstyle="-", color=color,
                             lw=0.7, alpha=0.85,
                             shrinkA=4, shrinkB=10),
        )

    # Laves labels: place BELOW their markers
    for r in laves:
        nm = PRETTY.get(r["label"], r["label"])
        ax.annotate(
            nm,
            xy=(r["GB"], Y_DIL),
            xytext=(r["GB"], Y_DIL - 0.12),
            ha="center", va="top",
            fontsize=8.5, fontweight="bold", style="italic",
            color=cls_color["Laves competitor"],
            bbox=dict(boxstyle="round,pad=0.22",
                       facecolor="white",
                       edgecolor=cls_color["Laves competitor"],
                       alpha=0.95, linewidth=0.6),
            arrowprops=dict(arrowstyle="-",
                             color=cls_color["Laves competitor"],
                             lw=0.7, alpha=0.85,
                             shrinkA=4, shrinkB=8),
        )

    # Threshold annotations near the top of the plot, above all data.
    # Pugh annotation anchored to right edge of its bbox so it stays
    # inside the plot area away from the colorbar.
    y_anno = 1.18
    ax.text(JOM,         y_anno, f"JOM 2025  $G/B={JOM}$",
             ha="center", va="top", fontsize=8.5, color="#E65100",
             fontweight="bold",
             bbox=dict(boxstyle="round,pad=0.20", facecolor="white",
                         edgecolor="#E65100", alpha=0.95, linewidth=0.5))
    ax.text(PUGH_THRESH + 0.005, y_anno, f"Pugh  $G/B={PUGH_THRESH}$",
             ha="left", va="top", fontsize=8.5, color="#B71C1C",
             fontweight="bold",
             bbox=dict(boxstyle="round,pad=0.20", facecolor="white",
                         edgecolor="#B71C1C", alpha=0.95, linewidth=0.5))

    # Row identifiers on the left margin
    ax.text(0.205, Y_NAMED, "named\ncompositions", ha="left",
             va="center", fontsize=8.0, color="#37474F", style="italic")
    ax.text(0.205, Y_DIL, "dilution path\n+ Laves", ha="left",
             va="center", fontsize=8.0, color="#37474F", style="italic")

    ax.set_xlim(0.20, 0.65)  # extended right so Pugh band + label fit inside
    ax.set_ylim(0.0, 1.30)
    ax.set_yticks([])
    ax.set_xlabel("Pugh ratio $G/B$ (this work, MACE-MH-1)",
                   fontsize=10.5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.set_title("LPBF cracking-susceptibility map for SPARK-relevant "
                  "RHEAs", fontsize=11.5, pad=8)

    # Band legend below
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.18),
               ncol=3, fontsize=8.5, frameon=False)

    fig.tight_layout()
    fig.savefig(FIG / "fig_gb_cracking_map.pdf")
    fig.savefig(FIG / "fig_gb_cracking_map.png")
    plt.close(fig)
    print("[C] wrote fig_gb_cracking_map.{pdf,png}")


# =====================================================================
# Driver
# =====================================================================
if __name__ == "__main__":
    print("Running Options A, B, C — small surrogate / descriptor models")
    summary = option_a_dilution_surrogate()
    option_b_descriptors()
    option_c_gb_cracking_map()
    print("\nDone. Outputs in figures/ and phase_diagrams/extra_outputs/")
    print("\n=== Option A summary ===")
    for s in summary:
        print(f"  {s['target']:<8s}: poly R²={s['r2_poly']:.4f}  "
              f"GP R²={s['r2_gp']:.4f}  ℓ={s['kernel_lengthscale']:.1f}")
