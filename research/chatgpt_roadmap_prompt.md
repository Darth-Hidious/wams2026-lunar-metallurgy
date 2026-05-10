# ChatGPT prompt — manufacturing roadmap PNG for WAMS 2026 Paper #68

> **Copy everything below the next horizontal rule into a fresh ChatGPT conversation
> (one with image generation enabled — GPT-4o or GPT-image-1).** Iterate 1–2 times if
> the first render mis-spells anything; the model lands within 2–3 generations on
> dense technical diagrams.

---

# Role

You are a senior scientific-infographic illustrator preparing a single composite figure for a peer-reviewed aerospace-materials paper. The figure must be print-ready (PNG, ≥300 dpi, white background) and look like the kind of swim-lane process diagram that appears in *Acta Astronautica* or *Journal of the British Interplanetary Society*. Clean, technical, restrained. No 3D, no glossy effects, no decorative shading. Sans-serif throughout.

# Object

A single composite **swim-lane / process-flow diagram** titled **"Lunar metallurgy manufacturing roadmap: Earth-supplied refractory feedstock + ISRU-derived streams through TRL gates."**

Aspect ratio: **landscape, approximately 16:10**. Final canvas size: **2400 × 1500 px** (or larger).

# Layout

The diagram is organised on a **4-row × 3-column grid**:

- **4 rows = swim lanes** (top to bottom): Earth feedstock | ISRU feedstock | Consolidation + QC | Validation
- **3 columns = TRL stages** (left to right): Stage 1 (TRL 3–5, current) | Stage 2 (TRL 5–6) | Stage 3 (TRL 6+, lunar architecture)
- Vertical **dashed dividers** separate the three TRL stages and run the full height of the figure
- Horizontal **light-grey lane backgrounds** behind each row, with the lane name in bold on the left edge

## Boxes per lane (all rounded rectangles with thin borders)

### Lane 1 — Earth feedstock (BLUE family, e.g. #1565C0 borders, #E3F2FD fill)

- **Stage 1 box A**: header "Refractory powders". Body text: "Mo, Nb, Ta, W, Cr, V (Earth-supplied) — 10–20 wt% of final blend".
- **Stage 1 box B**: header "Powder qualification". Body text: "PSD, oxygen content, flowability, elemental purity. Release spec: <500 ppm O on milled powder."
- An **arrow** from box A to box B inside Stage 1.
- A long arrow from box B that crosses the Stage-1/Stage-2 divider into the Consolidation lane (down-and-right).

### Lane 2 — ISRU feedstock (GREEN family, e.g. #2E7D32 borders, #E8F5E9 fill)

- **Stage 1 box A**: header "Lunar regolith". Body text: "Mare ilmenite (FeTiO₃) | highlands anorthosite | KREEP enriched units".
- **Stage 2 box B (large, three sub-rows inside one box)**: header "Three demonstrated extraction routes (mixed-metal product, not RHEA-grade)". Three sub-rows stacked vertically inside the box, each with its own colour stripe on the left:
  - Sub-row 1: "H₂ reduction of ilmenite ~1000 °C → reduced Fe + H₂O → O₂ via electrolysis. **TRL 4–5** (ProSPA breadboard)."
  - Sub-row 2: "Molten Regolith Electrolysis (MRE) ~1600 °C → Fe–Si cathode + O₂. **TRL 3–4** (0.5–1 kg simulant melt; 14 kW for 1000 kg O₂/yr)."
  - Sub-row 3: "FFC-Cambridge molten-salt electro-deoxidation → heterogeneous multiphase metal product. **TRL 3–4**."
- **Stage 2 box C** (just to the right of box B, smaller): header "Refining + release-spec qualification". Body text: "PSD, chemistry, phase identity, flowability, lot homogeneity. Output: candidate precursor only."
- An **arrow** from box A to box B (within the lane).
- An **arrow** from box B to box C (within the lane).
- From box C, an arrow goes upward to the **Conditional Gate** (see below) sitting between Lanes 2 and 3 in Stage 2.

### Lane 3 — Consolidation + QC (ORANGE family, e.g. #F57C00 borders, #FFF3E0 fill)

- **Stage 2 box A**: header "Powder blending". Body text: "Glovebox / Ar atm. | MA 40 h with ethanol PCA (lunar baseline; heptane = lab control) | sub-µm output."
- **Stage 2 box B**: header "Vacuum hot pressing". Body text: "RHEA: 1500 °C / 2 h / 30 MPa. HESA: 1260 °C / 2 h / 30 MPa."
- **Stage 2 box C**: header "Densified compact". Body text: "≥ 98% relative density. XRD phase check: BCC (RHEA) / FCC + MC (HESA). Bulk ρ = 9.4–12.9 g/cm³."
- Arrows: A → B → C (within Stage 2).
- A connector down into Lane 4 (Validation) at the Stage-2/Stage-3 boundary.

### Lane 4 — Validation (RED family, e.g. #C62828 borders, #FFEBEE fill)

- **Stage 1 box A**: header "Mechanical screening". Body text: "HV2 RT | Brinell RT/1000 K | mini-tensile UTS at RT and 1000 K. Phase 2 SPARK calibration gate (TRL 3 → 4)."
- **Stage 2 box B**: header "Phase-3 qualification". Body text: "Two-stage ignition (screen → 100 bar / 1000 K formal). Oxidation/erosion vs. Monel K500. Creep at 1000 °C. (TRL 5)."
- **Stage 2 box C**: header "Near-net-shape demonstration". Body text: "LPBF / DED on SPARK-calibrated parameter set (TRL 5–6)."
- **Stage 3 box D**: header "Hot-fire validation — DLR Lampoldshausen P8". Body text: "Sub-scale pre-combustion chamber, ≥150 bar, dual LOX/H₂ + LOX/CH₄. Replaceable chamber-liner article. (TRL 6+)."
- **Stage 3 box E**: header "Lunar production". Body text: "Modular metallurgical station, ~100–1000 kg/yr. (TRL 7–9)."
- Arrows: A → B → C → D → E.

## The Conditional Gate (the most important element)

Between Lane 2 (ISRU feedstock, Stage 2 box C) and Lane 3 (Consolidation + QC, Stage 2 box A), draw a **diamond-shaped decision symbol** spanning the lane boundary, filled solid yellow (#FFF59D) with a dark border. Label inside: "Incoming-powder equivalence gate". Two outgoing arrows:

- **PASS** (solid green arrow) → into Lane 3 box A (powder blending) with the label "released as RHEA feedstock"
- **FAIL** (dashed red arrow) → loops back to the Lane 2 box C with the label "candidate precursor — re-refine"

This gate is the **central conceptual claim of the figure** and must be visually prominent. It is the element that distinguishes this version of the roadmap from a naive "ISRU stream feeds straight into the press" picture.

## TRL stage labels (along the bottom of the figure)

Three stage labels in a horizontal band along the bottom, beneath the lanes:

- Below Stage 1 column: **"Stage 1 — Earth-side calibration (TRL 3–5, current)"** in dark green bold italic
- Below Stage 2 column: **"Stage 2 — Proxy feedstock + AM demonstration (TRL 5–6)"** in dark orange bold italic
- Below Stage 3 column: **"Stage 3 — Lunar architecture integration (TRL 6+)"** in dark red bold italic

## Title and subtitle

- Title (top, centred, bold, ~28 pt equivalent): **"Lunar-metallurgy manufacturing roadmap"**
- Subtitle (just under title, italic, ~14 pt equivalent, dark grey): "Earth-side process calibration (SPARK Phase 2) → ISRU integration → P8 hot-fire validation"

# Style

- **Colour palette per lane** as specified above (blue / green / orange / red), each used only for its lane's box borders, fills, and arrows.
- **Background**: white. Lane backgrounds: very light grey (#F5F5F5).
- **TRL stage dividers**: thin dashed grey vertical lines (#9E9E9E).
- **Arrows**: thin black, with arrowheads. Inter-lane arrows (e.g., Lane 1/2 → Lane 3) thinner than intra-lane arrows.
- **Fonts**: sans-serif (the rendered output will look like Helvetica, Arial, or Inter). Headers bold, body regular, metadata italic.
- **No clip art, no icons, no shadows, no gradients.** The diagram should look like a high-quality matplotlib figure or a tikz drawing, not like a marketing slide.
- All text must be **fully legible**: at least 12 pt equivalent for body text and 16 pt for headers when viewed at full canvas size.

# Constraints

1. The diagram is for a peer-reviewed paper. **Every text label above must appear verbatim**, including the TRL numbers, the temperatures (°C), the densities (g/cm³), the powder fractions (10–20 wt%), and the facility name "DLR Lampoldshausen P8".
2. **Do not** add any element that is not specified above. No regolith icons, no rocket icons, no lunar-surface backgrounds, no decorative starfields. Keep it strictly schematic.
3. **Do not** modify the SPARK programme designator labels (none should appear in this figure).
4. The **Conditional Gate** between ISRU feedstock and Consolidation must be clearly labelled and visually distinct (yellow diamond) — this is the figure's headline finding.
5. Output a single PNG file. White background. Margins ~5% on each side.
6. If you cannot render a diamond with text inside cleanly, render the gate as a hexagon or rounded rectangle with the same yellow fill and the same label.

# Iteration guidance

If the first render has wrong text on any box, re-prompt with: "Keep the same layout and colour palette, but re-render with these text corrections: [list corrections]". Do not start from scratch.

If the first render makes the gate too small or invisible, re-prompt with: "Make the yellow Incoming-powder equivalence gate diamond approximately 1.5× larger and place it so the PASS and FAIL arrows are both clearly readable. Keep everything else identical."

# What to expect from this prompt

A cleaner, more presentation-ready manufacturing roadmap than the matplotlib version currently in the paper as `fig_manufacturing_roadmap.pdf`. The new version explicitly visualises (i) the three ISRU extraction routes with their TRLs, (ii) the conditional incoming-powder gate (the central conceptual contribution after the dossier review), and (iii) DLR Lampoldshausen P8 as the named hot-fire venue.

When you have the PNG, save it as `fig_manufacturing_roadmap.png` and the paper's `\includegraphics{...}` line will pick it up automatically (matplotlib originally produced both PDF and PNG; the .tex line currently points to the PDF and can be switched to the PNG with no other change).
