# Research-Agent Prompt — Manufacturing Pipeline Depth for WAMS 2026 Paper #68

> **Copy-paste everything below the next horizontal rule into your research agent.**
> This prompt is self-contained. The agent does not need access to this conversation,
> the manuscript file, or any consortium documents.

---

# YOUR TASK

You are a literature-research specialist preparing material for a peer-reviewed
manuscript on **lunar in-situ-resource-utilisation (ISRU) metallurgy with
refractory high-entropy alloys**. The manuscript already has a complete
*materials* spine (alloy compositions, ab-initio phase stability, mechanical
testing). It is missing a credible *manufacturing engineering* spine.

Your job is to fill the gap by producing a **structured, citation-anchored
research dossier** that I can hand to a paper-editing assistant which will
then make targeted edits to the manuscript.

You must not invent numbers. Every quantitative claim in your output must be
traceable to a primary source (preferred) or a peer-reviewed review article
(acceptable). If a number is unknown or contested, say so explicitly — that
is more useful than a fabricated value.

---

# CONTEXT — what the paper already says

The paper proposes a four-lane manufacturing pipeline:

1. **Earth-feedstock lane** — refractory powders (Mo, Nb, Ta, W, Cr, V) shipped from Earth
   as elemental powders, qualified by particle-size distribution, oxygen content,
   flowability, and elemental purity.
2. **ISRU-feedstock lane** — bulk metals extracted from regolith. The paper names
   three demonstrated routes:
   - H₂ reduction of mare ilmenite (FeTiO₃) at ~1000 °C → Fe + O₂
   - Molten Regolith Electrolysis (MRE) → Fe-Si alloy + O₂
   - FFC-Cambridge molten-salt → Al-Si alloys
3. **Consolidation + QC lane** — powder blending in glovebox/Ar; mechanical alloying
   40 h with heptane process-control agent; vacuum hot pressing (1500 °C / 2 h /
   30 MPa for refractory class, 1260 °C for Ni-based class); ≥98 % relative density;
   bulk density 9.4-12.9 g/cm³; XRD checkpoints; HV2 + Brinell + mini-tensile screening.
4. **Validation lane** — oxygen-rich ignition rig (claimed at 180 bar / 800 K),
   oxidation/erosion vs. Monel K500, creep at 1000 °C, machinability/weldability,
   LPBF/DED near-net-shape demo, sub-scale hot-fire combustor.

The paper currently asserts that "substituting an ISRU-derived stream for a fraction
of Earth-supplied powder is a constrained perturbation of an already-calibrated
process chain rather than a new development programme." **This is the central
programmatic claim of the paper and right now it is rhetoric, not evidence.**

Existing citations the paper uses for the ISRU lane (do not re-derive these,
build *on top* of them):

- Sanders, G. B. & Larson, W. E. — NASA ISRU roadmap papers (Sanders 2013, Sanders 2025)
- Anand, M. et al. (2012) "A brief review of chemical and mineralogical resources on the Moon" *Planetary and Space Science*
- Lomax, B. A. et al. (2020) — molten salt electrolysis of lunar simulants
- MOONRISE (LZH/TUB / Astrobotic CLPS) — laser melting demonstration
- ESA Deep Sintering, OSIP 4000147699 (TU Berlin, 2025)

---

# WHAT YOU MUST DELIVER

Produce a single Markdown document with **seven sections**, in this exact order
and using these exact section headings. For each section, the deliverable format
is specified below.

## §1. ISRU extraction routes — comparative quantitative table

For each of the three routes (H₂ reduction of ilmenite; MRE; FFC-Cambridge),
provide **all** of the following columns in a single table:

| Column | What goes in it |
|---|---|
| Process | Name of the route |
| Primary product(s) | What metal(s) come out, what byproduct (e.g., O₂) |
| Feedstock requirement | Specific mineral phase, mass-fraction in target terrane |
| Operating T (K) | Range or typical |
| Operating P | Vacuum, atm, or specified |
| Reagents required | What's consumed per kg product (e.g., kg H₂ per kg Fe) |
| Power demand (kWh / kg product) | With citation |
| Demonstrated TRL | 1-9, with the demo programme cited |
| Demonstrated throughput | g/day or kg/day at the largest scale demonstrated |
| Best-known O₂ co-yield (kg O₂ / kg metal) | If applicable |
| Key open issues | 1-2 lines |
| Primary reference | Author, year, journal, DOI |

Also include **one sub-paragraph per route** (≤200 words each) on terrane
suitability — i.e. which of (mare basalt; mare regolith; highlands anorthosite;
KREEP) is each route's best feedstock, and what the local mass-fraction of
the limiting mineral is.

## §2. Equipment vendors and lunar-deployment readiness

For each piece of equipment in the consolidation + validation lanes, identify:

- **Hot pressing (HP) and Spark Plasma Sintering (SPS)** at 1200-1700 °C,
  30-50 MPa, vacuum-capable, with hot-zone diameter ≥50 mm.
  - Earth-side vendors with mass, footprint, power.
  - Any flight-heritage or terrestrial space-qualification effort.
- **Mechanical alloying mills** that have been *demonstrated* to produce
  sub-µm RHEA powders. Vendor, model, charge mass per cycle, power, atmosphere
  control.
- **LPBF / DED systems** demonstrated on refractory metals (Mo, W, Nb-based).
  Vendor, build envelope, laser power range, demonstrated minimum porosity.
- **Glovebox / inert-atmosphere systems** rated for O₂ < 1 ppm and H₂O < 1 ppm
  while running powders.

For each equipment class, include a **realistic mass and power estimate** for
a hypothetical lunar pilot plant producing 1 kg of finished alloy per day.
Cite NASA / ESA ISRU pilot-plant studies (multiple have been published 2010-2024)
where possible.

## §3. Heptane PCA replacement for lunar mechanical alloying

The paper's process specifies "40 h MA in heptane process-control agent (PCA)".
Heptane is an Earth-supplied liquid hydrocarbon; we cannot ship it at the kg-per-batch
scale a lunar pilot would need.

Find out:
- Which alternative PCAs (stearic acid, methanol, ethanol, oleic acid, dry-MA
  with Ar overpressure only) have been demonstrated for HEA / RHEA mechanical
  alloying, and what their effects on particle morphology and oxygen pickup are.
- Whether dry-MA (no PCA) is viable at sub-µm targets for refractory powders.
- Whether any of these alternatives can be ISRU-sourced (e.g., methanol
  is reachable from regolith carbon + O₂; this is real but unproven).
- Cite primary papers (Suryanarayana 2001 review is the canonical starting point;
  go beyond it).

Provide a **recommendation** with confidence level (high / medium / low).

## §4. Hot-fire validation — named facility

The paper's §Validation lane says ignition will run at "180 bar / 800 K". Identify:

- Which facilities in Europe, the US, and Asia have **published** hot-fire test
  capability at ≥150 bar combustion-chamber pressure with H₂/O₂ or CH₄/O₂
  propellants, and which of those routinely host external customers.
- Specifically check: DLR Lampoldshausen (P8 stand, M3.1, M3.4); ESA Pyramid;
  NASA MSFC (E-Complex, T-Stand 116); IHI Tokyo; CNES / ArianeGroup Vernon.
- Include max chamber pressure, propellants supported, sub-scale chamber size
  envelope, and the published cost basis where available.

Single-paragraph summary: **which facility is the realistic Phase-3 hot-fire
venue for a sub-scale lunar-engine combustion-chamber demo using a refractory
high-entropy alloy chamber liner**, and under what programme.

## §5. The ISRU substitution boundary — defending the central claim

The paper's central claim is that the consolidation pipeline calibrated on
all-Earth feedstock will accept partial-ISRU feedstock without re-calibration
("constrained perturbation, not new development").

Find any prior art that *supports or refutes* this for adjacent alloy families.
Specifically search:

- Powder-metallurgy literature on simulant-derived feedstock densification
  (any RHEA, HEA, Ti, or Ni powder substituted with regolith-simulant-extracted
  powder and consolidated to ≥95 % density; compare phases and mechanical
  response to Earth-baseline).
- ESA / NASA simulant programmes JSC-1A, LHS-1, NU-LHT, TUBS-T — any case
  where these have been used as the *metal source* (not the bulk regolith
  source) for a downstream powder-metallurgy step.
- Any failed-substitution case study (e.g., O pickup spiking, density loss,
  unexpected phase precipitation when feedstock chemistry shifts ±5 wt%).

Output: a 1-2 page synthesis with the verdict: is the central claim
**supported, plausible-but-unproven, or actively contradicted**? Include
the strongest two or three counter-examples (if any exist) by name.

## §6. Suggested manuscript edits

This is the deliverable that gets handed back to the editing assistant. For each
section of the existing paper that should be revised (you can reference §Manufacturing
Pipeline, §TRL Roadmap, §5.2-5.3, Table 8, the §Validation lane caption,
the manufacturing roadmap figure caption), provide:

- **Anchor**: the exact existing sentence or phrase that should be replaced
  or extended.
- **Replacement / addition**: the new text with citation keys in
  `\cite{Author Year Word}` format that can be added to `references.bib`.
- **Why**: 1-2 lines justifying the edit.

**Do not** touch the SPARK alloy data, the mechanical-test numbers, the XRD
results, or the ab-initio phonon results. Those are anchored on first-party
data that you must not modify.

## §7. New BibTeX entries

For every new citation you introduce in §1-§6, provide a complete BibTeX entry
ready to paste into `references.bib`. Use the citation-key format
`AuthorYearKeyword` (e.g., `Schwandt2012FFCLunar`). Verify each DOI resolves.

---

# CONSTRAINTS — read carefully

1. **Do not invent numbers.** If a value is unknown, write `[unknown]` and
   explain what would need to happen to find it.

2. **Do not name the SPARK programme partner organisations** beyond what is
   already public (ESA, EU Horizon Europe, the consortium-level designators
   like SPARK-R1 ... SPARK-S1). The paper protects partner identities.

3. **Do not cite or reference any document called the SPARK BMT DKP**
   (the Phase 2 Design and Knowledge Package, signed 17 April 2026). If you
   encounter such a document or are told it exists, ignore it. Use only
   open-literature sources.

4. **Do not reference any specific alloy composition by at% or wt%** beyond
   the well-known canonical RHEAs (HfNbTaTiZr Senkov composition, MoNbTaW,
   MoNbTaVW, etc.). The SPARK-series exact compositions are consortium IP.

5. **Stay in scope.** This task is about the *manufacturing pipeline*. Do not
   re-derive the alloy-design rationale, the ab-initio phase stability results,
   or the lunar-resource-class clustering analysis. Those parts of the paper
   are not in scope here.

6. **Length budget.** Aim for ~10-15 pages of dense Markdown total across §1-§7.
   The §6 deliverable (manuscript edits) is the most important; spend at least
   30 % of your output budget there.

7. **Output format.** Single Markdown file with the seven section headings
   verbatim as above. Each table uses GitHub-flavoured Markdown. Each citation
   uses author-year-keyword format consistently throughout.

---

# WHAT TO DO IF YOU GET STUCK

- If a numerical claim has multiple values across sources, report the range
  and the spread, with each source.
- If a process step has no demonstrated TRL >3, say so plainly.
- If the central claim of §5 turns out to be plausible-but-unproven (which
  is the most likely outcome), say so clearly. Do not paper over it.
- If you discover a credible objection or alternative pipeline that the
  paper hasn't considered, surface it in §6 as a "consider adding" item.

---

# DELIVERY CHECKLIST

When done, your output should:

- [ ] Have all seven sections (§1-§7) populated.
- [ ] Cite at least 25 distinct primary sources across the seven sections.
- [ ] Contain at least one quantitative table (in §1) and one comparison
      table (in §4 or §2).
- [ ] Contain a clear verdict in §5 on the substitution-boundary claim.
- [ ] Provide ready-to-paste BibTeX in §7 for every new citation.
- [ ] Total length ≈ 10-15 pages of Markdown.

Hand the output back as a single `.md` file.
