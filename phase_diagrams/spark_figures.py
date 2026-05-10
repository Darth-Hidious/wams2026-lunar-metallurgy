"""
Generate four figures from the SPARK Phase 2 dataset.

Produces:
  figures/fig_alloy_landscape.pdf       Hardness + UTS landscape, brittle/ductile coded
  figures/fig_strength_retention.pdf    UTS vs T including Inconel and Monel benchmarks
  figures/fig_xrd_panel.pdf             3-panel XRD composite reproduced from data
  figures/fig_manufacturing_roadmap.pdf Earth + ISRU pipeline through TRL gates

No alloy compositions are disclosed beyond the existing programme designators
(SPARK-R1 ... SPARK-R6, SPARK-H1 ... SPARK-H3, SPARK-S1) that already appear
in the manuscript. Only mechanical-property data and family-level descriptors
are shown. The DKP document is not referenced.
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
from adjustText import adjust_text

ROOT = Path(__file__).resolve().parent.parent
OUT  = ROOT / "figures"
OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Shared style — clean, paper-ready matplotlib
# ---------------------------------------------------------------------------
plt.rcParams.update({
    "font.family":       "sans-serif",
    "font.sans-serif":   ["Helvetica", "Arial", "DejaVu Sans"],
    "font.size":         10,
    "axes.labelsize":    11,
    "axes.titlesize":    12,
    "xtick.labelsize":   9,
    "ytick.labelsize":   9,
    "axes.linewidth":    0.9,
    "lines.linewidth":   1.5,
    "savefig.dpi":       300,
    "figure.dpi":        140,
    "savefig.bbox":      "tight",
})

DUCTILE = "#2E7D32"   # green
MIXED   = "#F57C00"   # orange
BRITTLE = "#C62828"   # red
NEUTRAL = "#37474F"   # dark grey
ACCENT  = "#1565C0"   # info blue


# ===========================================================================
# 1. Alloy landscape (hardness + UTS, brittle/ductile coded)
# ===========================================================================
def fig_alloy_landscape() -> None:
    """Bar / dot chart of SPARK alloys — uses programme designators only."""

    # Data, mapped to the manuscript's anonymised designators.
    # (HV2 numbers from Bimo Tech mechanical-property dataset; the manuscript's
    # Tables 11/12 already publish identical values.)
    rows = [
        # name      HV2_avg  RT_UTS  T1000_UTS  category   downselected
        ("SPARK-R1",  1219.,  504.,   532.,    "ductile",   True),
        ("SPARK-R2",  1170.,  368.,   None,    "mixed",     False),
        ("SPARK-R3",   620.,  272.,   252.,    "mixed",     False),
        ("SPARK-R4",   400.,  None,   None,    "mixed",     False),
        ("SPARK-R5",   785.,  171.,   None,    "brittle",   False),
        ("SPARK-R6",  1050.,  191.,   None,    "brittle",   False),
        ("SPARK-H1",   585.,  None,   None,    "brittle",   False),
        ("SPARK-H2",   705.,  None,   None,    "brittle",   False),
        ("SPARK-H3",   840.,  165.,   None,    "brittle",   False),
        ("SPARK-S1",   570., 1250.,   510.,    "ductile",   True),
    ]
    color_for = {"ductile": DUCTILE, "mixed": MIXED, "brittle": BRITTLE}

    fig, (axH, axU) = plt.subplots(2, 1, figsize=(8.6, 6.4), sharex=True,
                                    gridspec_kw=dict(hspace=0.18, height_ratios=[1, 1]))

    names = [r[0] for r in rows]
    x = np.arange(len(names))

    # ---- Top: Hardness ----
    hv = np.array([r[1] for r in rows])
    cats = [r[4] for r in rows]
    bars = axH.bar(x, hv, color=[color_for[c] for c in cats],
                    edgecolor="black", linewidth=0.6, width=0.66)
    for b, v, ds in zip(bars, hv, [r[5] for r in rows]):
        axH.text(b.get_x() + b.get_width() / 2, v + 25, f"{int(v)}",
                  ha="center", va="bottom", fontsize=8.5,
                  fontweight="bold" if ds else "normal")
        if ds:
            axH.text(b.get_x() + b.get_width() / 2, v + 95, "*",
                      ha="center", va="bottom", fontsize=14, color="black")
    axH.set_ylabel("Vickers hardness HV2")
    axH.set_ylim(0, max(hv) * 1.22)
    axH.grid(axis="y", alpha=0.25, lw=0.5)
    axH.set_axisbelow(True)
    axH.spines["top"].set_visible(False)
    axH.spines["right"].set_visible(False)
    axH.set_title("SPARK Phase-2 alloy landscape  ·  hardness, UTS, brittleness category",
                   pad=8)

    # ---- Bottom: UTS RT and 1000 K ----
    rt = np.array([r[2] if r[2] is not None else np.nan for r in rows])
    hi = np.array([r[3] if r[3] is not None else np.nan for r in rows])
    w = 0.32
    bRT = axU.bar(x - w/2, rt, w, color=[color_for[c] for c in cats],
                   edgecolor="black", linewidth=0.6, label="UTS RT")
    bHi = axU.bar(x + w/2, hi, w, color=[color_for[c] for c in cats],
                   edgecolor="black", linewidth=0.6, alpha=0.55,
                   hatch="///", label="UTS 1000 K")
    for b, v in zip(bRT, rt):
        if not np.isnan(v):
            axU.text(b.get_x() + b.get_width() / 2, v + 25, f"{int(v)}",
                      ha="center", va="bottom", fontsize=7.6)
    for b, v in zip(bHi, hi):
        if not np.isnan(v):
            axU.text(b.get_x() + b.get_width() / 2, v + 25, f"{int(v)}",
                      ha="center", va="bottom", fontsize=7.6, alpha=0.8)
    # Inconel HP benchmark (RT and 1000 K) — drawn from the same lab campaign
    # (the manuscript's Inconel-HP comparison row in Table 12).
    # Labels placed in the empty mid-x region (between brittle bars and
    # the SPARK-S1 column) with a white bbox so they stay legible
    # regardless of which bars they sit near.
    axU.axhline(738, color=ACCENT, lw=1.0, ls="--", alpha=0.7)
    axU.text(6.5, 738, "Inconel HP, RT  738 MPa",
              ha="center", va="center", fontsize=8, color=ACCENT,
              style="italic", fontweight="bold",
              bbox=dict(boxstyle="round,pad=0.30",
                          facecolor="white", edgecolor=ACCENT,
                          alpha=0.95, linewidth=0.5))
    axU.axhline(974, color=ACCENT, lw=1.0, ls=":", alpha=0.7)
    axU.text(6.5, 974, "Inconel HP, 1000 K  974 MPa",
              ha="center", va="center", fontsize=8, color=ACCENT,
              style="italic", fontweight="bold",
              bbox=dict(boxstyle="round,pad=0.30",
                          facecolor="white", edgecolor=ACCENT,
                          alpha=0.95, linewidth=0.5))
    # Brittle / no-tensile labels
    for i, r in enumerate(rows):
        if r[2] is None and r[3] is None:
            axU.text(i, 30, "no tensile\n(brittle)", ha="center", va="bottom",
                      fontsize=7.2, color=BRITTLE, style="italic")

    axU.set_ylabel("Mini-tensile UTS (MPa)")
    axU.set_ylim(0, 1450)
    axU.grid(axis="y", alpha=0.25, lw=0.5)
    axU.set_axisbelow(True)
    axU.spines["top"].set_visible(False)
    axU.spines["right"].set_visible(False)
    axU.set_xticks(x)
    axU.set_xticklabels(names, rotation=20, ha="right")
    axU.legend(loc="upper left", fontsize=8.5, frameon=False)

    # Shared category legend at top
    handles = [
        plt.Rectangle((0,0),1,1, facecolor=DUCTILE, edgecolor="black",
                       label="ductile, single-phase"),
        plt.Rectangle((0,0),1,1, facecolor=MIXED,   edgecolor="black",
                       label="reduced ductility / segregation"),
        plt.Rectangle((0,0),1,1, facecolor=BRITTLE, edgecolor="black",
                       label="brittle (fractured during processing)"),
        plt.Line2D([0],[0], marker="*", lw=0, color="black", markersize=10,
                    label="down-selected for Phase 3"),
    ]
    axH.legend(handles=handles, loc="upper right", fontsize=8.5,
                frameon=True, ncol=1, bbox_to_anchor=(1.0, 1.0))

    out = OUT / "fig_alloy_landscape"
    fig.savefig(out.with_suffix(".pdf")); fig.savefig(out.with_suffix(".png"))
    plt.close(fig)
    print(f"  ✓ {out.name}")


# ===========================================================================
# 2. Strength retention vs temperature
# ===========================================================================
def fig_strength_retention() -> None:
    """UTS vs T for SPARK down-selected candidates against incumbents.

    Legend redesign: split into two panels (SPARK / benchmarks), placed
    BELOW the plot in a clean 2-column grid so it stops competing with
    the data labels. Down-selection asterisk lives next to the legend
    entry, not in the line label.
    """
    fig = plt.figure(figsize=(8.4, 5.8))
    # Reserve the bottom 22% of the figure for the legend block.
    ax = fig.add_axes([0.10, 0.30, 0.85, 0.60])
    leg_ax = fig.add_axes([0.10, 0.04, 0.85, 0.20]); leg_ax.set_axis_off()

    T = np.array([295, 1000])

    # (label, RT, T_high, color, linestyle, marker, linewidth, group)
    # group: "spark_ds" = SPARK down-selected, "spark"  = SPARK other,
    #        "bench" = literature / in-house benchmark
    series = [
        ("SPARK-R1",           np.array([504,  532]),  DUCTILE,   "-",  "o", 2.8, "spark_ds"),
        ("SPARK-S1",           np.array([1250, 510]),  ACCENT,    "-",  "o", 2.8, "spark_ds"),
        ("SPARK-R3",           np.array([272,  252]),  MIXED,     "-",  "s", 1.8, "spark"),
        ("Inconel HP",         np.array([738,  974]),  "#7B1FA2", "--", "D", 1.8, "bench"),
        ("Monel K500",         np.array([550,  480]),  "#5D4037", ":",  "^", 1.8, "bench"),
    ]

    # Plot the lines and collect data-point label objects so adjust_text
    # can repel them from each other once everything is on the canvas.
    label_texts = []
    label_anchors = []  # (x, y) of each label's true marker position
    for name, vals, col, ls, mk, lw, _ in series:
        ax.plot(T, vals, ls=ls, marker=mk, color=col, lw=lw, markersize=8,
                  markeredgecolor="black", markeredgewidth=0.6)
        for ti, v in zip(T, vals):
            t = ax.text(ti, v, f"{int(v)}",
                         fontsize=8.4, color=col, fontweight="bold",
                         ha="center", va="center",
                         bbox=dict(boxstyle="round,pad=0.15",
                                     facecolor="white", edgecolor="none",
                                     alpha=0.85))
            label_texts.append(t)
            label_anchors.append((ti, v))

    # Preburner working window
    ax.axvspan(900, 1200, color="#FFF59D", alpha=0.30, zorder=0)
    ax.text(1050, 1380, "Preburner working window  (1000–1200 K)",
             ha="center", va="top", fontsize=8.6, color="#5D4037",
             style="italic")

    # Repel the data-value labels from each other and from the markers,
    # with thin grey leader lines back to the original (T, value) point.
    adjust_text(
        label_texts, ax=ax,
        expand_text=(1.5, 1.6), expand_points=(1.6, 1.7),
        force_text=(0.8, 1.0), force_points=(0.6, 0.9),
        arrowprops=dict(arrowstyle="-", color="#9E9E9E", lw=0.5,
                         alpha=0.7, shrinkA=2, shrinkB=4),
    )

    ax.set_xlabel("Temperature (K)")
    ax.set_ylabel("Ultimate tensile strength (MPa)")
    ax.set_xlim(200, 1100)
    ax.set_ylim(0, 1450)
    ax.set_xticks([295, 500, 700, 900, 1000])
    ax.grid(alpha=0.25, lw=0.5)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_title(
        "Strength retention at temperature  ·  SPARK down-selected vs benchmarks",
        pad=8)

    # ------------------------------------------------------------------
    # Custom two-column legend below the plot
    # ------------------------------------------------------------------
    from matplotlib.lines import Line2D
    spark_handles = []
    bench_handles = []
    for name, _, col, ls, mk, lw, group in series:
        h = Line2D([0], [0], color=col, ls=ls, marker=mk,
                    lw=lw, markersize=8, markeredgecolor="black",
                    markeredgewidth=0.6,
                    label=(name + "  (down-selected)") if group == "spark_ds" else name)
        if group.startswith("spark"):
            spark_handles.append(h)
        else:
            bench_handles.append(h)

    leg1 = leg_ax.legend(handles=spark_handles,
                          title="SPARK candidates (this work)",
                          loc="upper left", bbox_to_anchor=(0.0, 1.0),
                          fontsize=9.0, title_fontsize=9.5,
                          frameon=False, alignment="left",
                          handlelength=2.5, borderaxespad=0.0)
    leg1.get_title().set_fontweight("bold")
    leg_ax.add_artist(leg1)

    leg2 = leg_ax.legend(handles=bench_handles,
                          title="Reference benchmarks",
                          loc="upper left", bbox_to_anchor=(0.50, 1.0),
                          fontsize=9.0, title_fontsize=9.5,
                          frameon=False, alignment="left",
                          handlelength=2.5, borderaxespad=0.0)
    leg2.get_title().set_fontweight("bold")

    leg_ax.text(0.0, -0.10,
                 "All SPARK and Inconel HP values from in-house mini-tensile "
                 "(~0.5 × 1.2 mm gauge); Monel K500 from literature handbook.",
                 transform=leg_ax.transAxes, ha="left", va="top",
                 fontsize=7.8, color=NEUTRAL, style="italic")

    out = OUT / "fig_strength_retention"
    fig.savefig(out.with_suffix(".pdf")); fig.savefig(out.with_suffix(".png"))
    plt.close(fig)
    print(f"  ✓ {out.name}")


# ===========================================================================
# 3. XRD evidence panel — composite of 3 measurement panels
# ===========================================================================
def fig_xrd_panel() -> None:
    """Composite the three measured XRD patterns into a single paper figure.

    Reads the original Origin-style PNGs already produced by the lab and
    arranges them as a 3-row figure. The originals are in
    /tmp/hesa_xrd/slide{1,2,3}.png (extracted from HESA XRD.pptx) — but for
    portability we copy them into figures/_xrd_input/ and read from there.
    """
    import shutil
    src = Path("/tmp/hesa_xrd")
    dst = OUT / "_xrd_input"
    dst.mkdir(exist_ok=True)
    for nm in ("slide1.png", "slide2.png", "slide3.png"):
        if (src / nm).exists() and not (dst / nm).exists():
            shutil.copy(src / nm, dst / nm)

    panels = [
        (dst / "slide1.png",
         "(a) SPARK-S1 (Ni-based HESA): MA powder vs HP compact",
         "FCC matrix + minor MC carbide phase confirmed in HP compact."),
        (dst / "slide2.png",
         "(b) Eight-element MA powders: SPARK-H2 vs SPARK-H3",
         "BCC matrix; Ni-bearing variant shows additional MC carbide intensity."),
        (dst / "slide3.png",
         "(c) Eight-element compact heated to 1000 °C",
         "Multiple sharp low-angle peaks show phase decomposition that "
         "contributes to embrittlement."),
    ]

    if not all(p.exists() for p, _, _ in panels):
        print("  ⚠ XRD images not present in figures/_xrd_input/, skipping")
        return

    import matplotlib.image as mpimg
    # 1x3 horizontal layout — wide and short so the figure fits
    # comfortably on a single textwidth-sized portrait page.
    fig, axes = plt.subplots(1, 3, figsize=(15.0, 4.8),
                              gridspec_kw=dict(wspace=0.10))
    short_titles = [
        "(a) HESA-class compact: FCC + minor MC carbide",
        "(b) 8-element MA powders: BCC matrix",
        "(c) 8-element compact at 1000 °C: phase decomposition",
    ]
    short_subs = [
        "MA powder vs HP compact, SPARK-S1.",
        "Ni-bearing variant shows extra MC intensity.",
        "Sharp low-angle peaks indicate embrittling phase split.",
    ]
    for ax, (path, _, _), title, sub in zip(axes, panels, short_titles, short_subs):
        ax.imshow(mpimg.imread(str(path)))
        ax.set_axis_off()
        ax.set_title(title, fontsize=10.5, fontweight="bold", color=NEUTRAL,
                      loc="left", pad=6)
        ax.text(0.0, -0.045, sub, transform=ax.transAxes, ha="left",
                 va="top", fontsize=8.6, color="#555", style="italic")

    out = OUT / "fig_xrd_panel"
    fig.savefig(out.with_suffix(".pdf"))
    fig.savefig(out.with_suffix(".png"))
    plt.close(fig)
    print(f"  ✓ {out.name}")


# ===========================================================================
# 4. Manufacturing roadmap (the big missing piece)
# ===========================================================================
def fig_manufacturing_roadmap() -> None:
    fig, ax = plt.subplots(figsize=(13.5, 8.5))
    ax.set_xlim(0, 100); ax.set_ylim(0, 70)
    ax.set_aspect("auto"); ax.set_axis_off()

    # Define swim lanes
    lane_y = {
        "earth": 53,    # Earth-supplied refractory feedstock
        "isru":  37,    # ISRU bulk metal extraction
        "consol":21,    # Powder blending + consolidation
        "test":   5,    # Testing + validation
    }

    def box(x, y, w, h, label, sub="", fc="#E3F2FD", ec="#1565C0", fs=10,
            sub_fs=8.2):
        b = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.18",
                            facecolor=fc, edgecolor=ec, linewidth=1.4,
                            zorder=3)
        ax.add_patch(b)
        ax.text(x + w/2, y + h*0.66, label, ha="center", va="center",
                 fontsize=fs, fontweight="bold", color=NEUTRAL, zorder=4)
        if sub:
            ax.text(x + w/2, y + h*0.30, sub, ha="center", va="center",
                     fontsize=sub_fs, color="#555", zorder=4, style="italic")

    def arrow(x1, y1, x2, y2, color="#666", lw=1.4, ls="-"):
        a = FancyArrowPatch((x1, y1), (x2, y2),
                             arrowstyle="-|>,head_length=8,head_width=5",
                             linewidth=lw, color=color, ls=ls, zorder=2)
        ax.add_patch(a)

    # Title
    ax.text(50, 67, "Lunar-metallurgy manufacturing roadmap",
             ha="center", va="bottom", fontsize=15, fontweight="bold",
             color=NEUTRAL)
    ax.text(50, 64.5,
             "Earth-side process calibration (SPARK Phase 2) "
             "$\\to$ ISRU integration $\\to$ hot-fire validation",
             ha="center", va="bottom", fontsize=10, color="#555",
             style="italic")

    # Swim-lane labels (left edge)
    lanes = [
        ("Earth feedstock",     lane_y["earth"]+4, "#1565C0"),
        ("ISRU feedstock",      lane_y["isru"]+4,  "#2E7D32"),
        ("Consolidation + QC", lane_y["consol"]+4, "#F57C00"),
        ("Validation",          lane_y["test"]+4,  "#C62828"),
    ]
    for name, y, color in lanes:
        ax.text(0.5, y, name, ha="left", va="center", fontsize=10.5,
                 fontweight="bold", color=color, rotation=0)

    # ------------------------------------------------------------------
    # Earth-feedstock lane (top)
    # ------------------------------------------------------------------
    box(11, lane_y["earth"], 14, 7,
         "Refractory powders",
         "Mo, Nb, Ta, W, Cr, V (Earth-supplied)\n"
         "10--20 wt$\\%$ of final blend",
         fc="#E3F2FD", ec="#1565C0")
    box(28, lane_y["earth"], 14, 7,
         "Powder qualification",
         "PSD, oxygen content,\nflowability, purity",
         fc="#E3F2FD", ec="#1565C0")
    arrow(25, lane_y["earth"]+3.5, 28, lane_y["earth"]+3.5)

    # ------------------------------------------------------------------
    # ISRU lane
    # ------------------------------------------------------------------
    box(11, lane_y["isru"], 14, 7,
         "Lunar regolith",
         "Mare ilmenite (FeTiO$_3$),\nhighlands anorthosite",
         fc="#E8F5E9", ec="#2E7D32")
    box(28, lane_y["isru"], 14, 7,
         "Extraction routes",
         "H$_2$ red.\\ $\\to$ Fe + O$_2$\n"
         "FFC-Cambridge $\\to$ Al--Si\n"
         "MRE $\\to$ Fe--Si",
         fc="#E8F5E9", ec="#2E7D32", sub_fs=7.8)
    arrow(25, lane_y["isru"]+3.5, 28, lane_y["isru"]+3.5)

    # ------------------------------------------------------------------
    # Convergence at consolidation lane
    # ------------------------------------------------------------------
    box(45, lane_y["consol"]+3, 14, 7,
         "Powder blending",
         "Glovebox / Ar atm.\n"
         "MA 40 h, heptane PCA\n"
         "$\\to$ sub-$\\mu$m powder",
         fc="#FFF3E0", ec="#F57C00", sub_fs=8.0)
    # Earth and ISRU both feed into blending
    arrow(42, lane_y["earth"]+3.5, 47, lane_y["consol"]+9, color="#1565C0")
    arrow(42, lane_y["isru"]+3.5,  47, lane_y["consol"]+8, color="#2E7D32")

    box(62, lane_y["consol"]+3, 14, 7,
         "Vacuum hot pressing",
         "RHEA: 1500°C / 2 h / 30 MPa\n"
         "HESA: 1260°C / 2 h / 30 MPa",
         fc="#FFF3E0", ec="#F57C00", sub_fs=8.0)
    arrow(59, lane_y["consol"]+6.5, 62, lane_y["consol"]+6.5)

    box(79, lane_y["consol"]+3, 14, 7,
         "Densified compact",
         "$\\geq 98\\%$ rel.\\ density\n"
         "Single-phase BCC / FCC+MC\n"
         "$\\rho = 9.4$--12.9 g/cm$^3$",
         fc="#FFF3E0", ec="#F57C00", sub_fs=8.0)
    arrow(76, lane_y["consol"]+6.5, 79, lane_y["consol"]+6.5)

    # ------------------------------------------------------------------
    # Testing lane (bottom)
    # ------------------------------------------------------------------
    box(11, lane_y["test"], 14, 7,
         "Mechanical screening",
         "HV2 RT, HB RT/1000K\n"
         "Mini-tensile UTS\n"
         "DKP gate (TRL 3$\\to$4)",
         fc="#FFEBEE", ec="#C62828", sub_fs=7.8)
    # Vertical drop from consolidation chain to validation lane
    arrow(86, lane_y["consol"]+3, 86, lane_y["test"]+7,
           color="#9E9E9E", lw=1.0, ls="--")
    arrow(18, lane_y["consol"]+3, 18, lane_y["test"]+7,
           color="#9E9E9E", lw=1.0, ls="--")

    box(28, lane_y["test"], 14, 7,
         "Phase-3 qualification",
         "Ignition (BeBlue / Air Liquide)\n"
         "Oxidation/erosion vs Monel K500\n"
         "Creep at 1000°C (TRL 5)",
         fc="#FFEBEE", ec="#C62828", sub_fs=7.6)
    arrow(25, lane_y["test"]+3.5, 28, lane_y["test"]+3.5, color="#C62828")

    box(45, lane_y["test"], 14, 7,
         "Near-net-shape",
         "LPBF / DED with\nSPARK-calibrated parameters\n"
         "(planned, TRL 5--6)",
         fc="#FFEBEE", ec="#C62828", sub_fs=7.8)
    arrow(42, lane_y["test"]+3.5, 45, lane_y["test"]+3.5, color="#C62828")

    box(62, lane_y["test"], 14, 7,
         "Hot-fire validation",
         "AGG sub-scale\npre-combustion chamber\n"
         "(P8 bench, TRL 6+)",
         fc="#FFEBEE", ec="#C62828", sub_fs=7.8)
    arrow(59, lane_y["test"]+3.5, 62, lane_y["test"]+3.5, color="#C62828")

    box(79, lane_y["test"], 14, 7,
         "Lunar production",
         "Modular metallurgical\nstation, $\\sim$100--1000 kg/yr\n"
         "(TRL 7--9)",
         fc="#FFEBEE", ec="#C62828", sub_fs=7.8)
    arrow(76, lane_y["test"]+3.5, 79, lane_y["test"]+3.5, color="#C62828")

    # TRL gate annotations along the bottom
    gate_y = -0.6
    ax.text(18, gate_y, "Stage 1 (TRL 3--5)\nEarth-side calibration",
             ha="center", va="top", fontsize=8.5, color="#1B5E20",
             fontweight="bold", style="italic")
    ax.text(45, gate_y, "Stage 2 (TRL 5--6)\nProxy feedstock + LPBF",
             ha="center", va="top", fontsize=8.5, color="#E65100",
             fontweight="bold", style="italic")
    ax.text(72, gate_y, "Stage 3 (TRL 6+)\nLunar architecture",
             ha="center", va="top", fontsize=8.5, color="#B71C1C",
             fontweight="bold", style="italic")

    # Vertical TRL gate dividers
    for x_div in (32, 60):
        ax.plot([x_div, x_div], [3, 60], color="#9E9E9E", lw=0.7,
                  ls="--", zorder=1)

    fig.tight_layout()
    out = OUT / "fig_manufacturing_roadmap"
    fig.savefig(out.with_suffix(".pdf"))
    fig.savefig(out.with_suffix(".png"))
    plt.close(fig)
    print(f"  ✓ {out.name}")


# ===========================================================================
# Driver
# ===========================================================================
if __name__ == "__main__":
    print("Generating SPARK figures from Phase-2 dataset:")
    fig_alloy_landscape()
    fig_strength_retention()
    fig_xrd_panel()
    # NOTE: fig_manufacturing_roadmap() intentionally NOT called.
    # The manufacturing roadmap shipped with the paper is a ChatGPT-rendered
    # PNG (figures/fig_manufacturing_roadmap.png) authored separately.
    # Re-running this matplotlib version would overwrite that PNG.
    # See phase_diagrams/extra_models.py for the additional figures.
    print("\nDone.")
