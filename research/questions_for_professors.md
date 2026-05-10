# Pipeline Research Questions — for next discussion with professors
**Status:** the §Manufacturing Pipeline section in `main.tex` is the *outline*. This file is the
*reading list and question list* that has to come back from those discussions before the section
can stop being a roadmap and start being engineering.

---

## 0. Honest assessment of what is and isn't there

What the current §Manufacturing Pipeline (lines 756-769 of `main.tex`) **does** have:
- Three named ISRU extraction routes, each with a real citation:
  - **H₂ reduction of mare ilmenite** at ~1000 °C → Fe + O₂  (Sanders 2013, Anand 2012)
  - **Molten Regolith Electrolysis (MRE)** → Fe-Si alloy + O₂  (Sanders 2025, Lomax 2020)
  - **FFC-Cambridge molten-salt** → Al-Si alloy  (Lomax 2020)
- Process windows that come from the SPARK Phase 2 campaign (HP 1500 °C / 2 h / 30 MPa, MA 40 h heptane PCA, ≥98 % rel. density, 9.4-12.9 g/cm³).
- Three Phase-3 closure paths (oxygen-rich ignition; oxidation/erosion vs. Monel K500; LPBF/DED near-net-shape demo).

What the section **does not** have, and what the professor discussion is for:
- **Mass balance.** Kilograms of metal per tonne of regolith — for each of the three routes and each of the three terranes (mare, highlands, KREEP).
- **Power budget.** kWh per kg of Fe, per kg of Al, per kg of O₂.
- **Throughput.** kg/day per reactor unit at flight scale.
- **Machinery TRLs.** Has anyone actually built an H₂-reduction reactor? An MRE cell? An FFC-Cambridge cell sized for kilograms-per-day, not laboratory grams?
- **Equipment vendors.** Who supplies the press, the mill, the atmosphere control, the LPBF system?
- **What gets shipped vs. what's built on the Moon.** The pipeline section reads as if everything happens on the lunar surface, but a hot press is a 30 t machine. What's the actual launch manifest?
- **Heptane PCA on the Moon.** Heptane is an Earth-supplied process-control agent; we cannot ship it at scale. What replaces it for lunar mechanical alloying?
- **Atmosphere control.** Glovebox-grade Ar on the Moon — where does the Ar come from? (Solar-wind-implanted noble gases in regolith are real but extraction is its own pipeline.)
- **The "ISRU substitution boundary" claim.** The current paragraph asserts chemistry-control is separable from feedstock-source. That's the central programmatic claim of the framework and right now it stands on rhetoric, not evidence.

---

## 1. ISRU extraction — literature targets per stream

These are the specific authors / programmes the next reading sweep should hit. Cited papers in
`references.bib` are marked **[bib]**.

### 1a. Iron and oxygen (mare ilmenite, FeTiO₃)
- **H₂ reduction of ilmenite**:
  - Allen, Morris, Lindstrom, Lindstrom, Lockwood (1996) — JGR Planets, the canonical paper
  - Massieon, Cutler, Shadman (1992) — Met Trans B, kinetics
  - Hegde, Balasubramaniam, Gupta (2009-2014) — IIT-K, Indian programme
  - **Sanders 2013 [bib]**, **Anand 2012 [bib]** — already in the paper
- **Carbothermal reduction**:
  - Gustafson et al., Lockheed/Aerojet "Carbotek" papers, NASA SBIR series 2008-2015
  - Rosenberg, Beegle, Guter, Foster (1965-1996) — original carbothermal work
- **Vacuum thermal decomposition / pyrolysis**:
  - Senior (1993), Schwandt (2012)

**Question for the professors:** which of these three actually hits TRL 6 first under realistic
mare conditions? Allen-style H₂ reduction is the lab-favourite but needs H₂ as a consumable.

### 1b. Aluminium and silicon (highlands anorthite, CaAl₂Si₂O₈)
- **FFC-Cambridge process**:
  - Chen, Fray, Farthing (2000) — Nature, the original method
  - Schwandt, Hamilton, Fray (2012) — JOM lunar adaptation
  - **Lomax 2020 [bib]** — already in the paper
- **Molten Regolith Electrolysis (MRE)**:
  - Sirk, Sadoway, Sibille (2010-2014) — MIT, ESA, the foundational MRE papers
  - Curreri (2006-2010) — NASA MSFC molten oxide work
  - **Sanders 2025 [bib]**, **Lomax 2020 [bib]** — already in the paper
- **Magnesiothermic / Aluminothermic options**:  Schlüter & Cowley reviews

**Question for the professors:** is FFC-Cambridge actually compatible with anorthite chemistry,
or does the literature mostly demonstrate it on TiO₂? The anorthite case may need a different cell.

### 1c. Oxygen as a primary product (not a metallurgical question, but it sets the energy economics)
- **NASA ISRU roadmap** — Sanders, Larson 2013-2022 series
- **PROSPECT (ESA, Luna-27)** — Reiss et al. 2020-2024
- **MOXIE (Mars context, but transferable)** — Hoffman et al. 2022 *Science Advances*

### 1d. Recent reviews to anchor the literature scan
- Crawford, Anand, Cockell, Falcke (2022) "Lunar resources: a review" — *Progress in Physical Geography*
- Anand et al. (2012) "A brief review of chemical and mineralogical resources" *Planet. Space Sci.* — already cited as Anand2012 [bib]
- Schlüter & Cowley (2020) "Review of techniques for In-Situ oxygen extraction on the moon" *Planet. Space Sci.*

---

## 2. Equipment-side questions per pipeline lane

### 2a. Earth feedstock lane
- Where does Mo, Nb, Ta, W, Cr, V powder come from at flight quality? (H.C. Starck / Plansee / Tosoh)
- O content threshold for LPBF feedstock: typical 200-1000 ppm. Can we hit that on Mo, Ta, W?
- Particle size: GA (gas atomized) vs. PA (plasma atomized) — which goes to mechanical alloying without breaking the AM-grade window?

### 2b. ISRU feedstock lane
- For each extraction route in §1: vendor, scale, demonstrated TRL, power, footprint.
- Reference-class machinery:
  - Hot-stage furnaces:  Aerojet/Carbotek prototype, NASA Marshall MRE cell
  - **MOONRISE** (LZH/TUB, on Astrobotic CLPS) — already cited [bib], the in-flight laser melting demo
  - **ESA Deep Sintering** (TU Berlin, OSIP 4000147699) — already cited [bib], regolith sintering at scale
- Question: any of these rated for >1 kg/day? Most lab demos are at ~1-100 g/day.

### 2c. Consolidation + QC lane
- Hot press vendors at SPARK scale: FCT Systeme (Rauenstein, DE), Thermal Technology (Santa Rosa, US), Centorr Vacuum (NH, US). Working pressure 30-50 MPa, max T 2200 °C — both standard.
- Spark Plasma Sintering (SPS) as alternative: Sumitomo / FCT / Thermal Technology — much shorter cycle, 5-15 min vs. 2 h.
- Mechanical alloying mills: SPEX 8000M (lab), Fritsch P5/P7 (mid), Zoz Simoloyer CM01-08s (production, kg/h scale).
- **Lunar question:** which of these has been considered for a lunar pilot? None of them have flight heritage. The MOONRISE laser-melting precedent is the closest, but it's much smaller scale.

### 2d. Validation lane
- Ignition rig at 180 bar / 800 K — DLR Lampoldshausen has a relevant facility. **Confirm with the professors which rig the SPARK Phase-3 ignition test will actually use.**
- LPBF for high-density refractories — Mo and W LPBF parameter windows are published (Higashi & Ozaki 2020, Becker et al. 2022). Is there a SPARK-validated parameter window yet, or is this still aspirational?
- Sub-scale combustor hot-fire — DLR / ESA-ISP / NASA MSFC are the candidate facilities.

---

## 3. The "ISRU substitution boundary" claim — what would make it real

The current paragraph says: *substituting an ISRU-derived stream for a fraction of Earth-supplied
powder is a constrained perturbation of an already-calibrated process chain rather than a new
development programme*.

To make that claim defensible, the next revision needs **one of**:
1. A controlled experiment where SPARK runs the same consolidation recipe on (a) all-Earth feedstock
   and (b) feedstock with X% surrogate-regolith-derived Fe substituted in, and shows the densification
   window and phase-stability gates are unchanged. JSC-1A or LHS-1 simulant on the Fe-Ti side, NU-LHT
   on the highlands side.
2. A mass-balance argument that quantifies *how* perturbed the chemistry is at each substitution level
   and shows it stays inside the SPARK calibration envelope by construction.
3. A literature precedent where this was done for a different alloy family.

**Right now we have none of those.** The claim is plausible but unsupported.

---

## 4. Specific questions to bring to the professors

1. Of the three ISRU routes (H₂ reduction, MRE, FFC-Cambridge), which is the one we should depth-resource for the paper's TRL roadmap, and which two stay as alternatives?
2. Is the SPARK Phase-2 hot press going to migrate to SPS for the Phase-3 demo (faster cycle, smaller flightable footprint), or stay as HP?
3. What replaces heptane as a process-control agent for lunar mechanical alloying — or do we drop the wet-MA step entirely and switch to dry-MA + reactive sintering?
4. Has anyone in the consortium done a mass balance on Fe yield per kg of mare regolith for our SPARK-grade purity spec? If yes, can we cite it. If no, this is the most useful thing to do next.
5. For the validation lane, which rig at DLR / ESA-ISP / NASA MSFC is the *named* Phase-3 hot-fire venue? The paper currently dodges this.
6. Should any of the 11 ovito-rendered atomic structures (presentation slides 7-9) and the MD snapshots (slides 4-6, 9) move into the paper proper? They were generated for the deck, not the manuscript. (See §5 below for the catalogue.)

---

## 5. Existing presentation diagrams — catalogue and proposed disposition

Located at:
`/Users/siddharthakovid/Downloads/wams2026-lunar-metallurgy/.claude/worktrees/gifted-moore-e74ef6/figures/presentation/`

| File | Subject | In paper? | Proposed disposition |
|---|---|---|---|
| slide_01_phase_competition.pdf | T=0 phase-competition energies (BCC vs. Laves) | no | candidate for §6.6 supplementary; the math is already in the prose |
| slide_02_bcc_preference.pdf | BCC stability landscape across compositions | no | maybe §4.5 or supplementary |
| slide_03_solute_dissolution.pdf | Solute-dissolution energies (Fe, Ti, Al into RHEAs) | no | strong candidate for §5.3 — the prose already cites this concept |
| slide_04_md_energy.pdf | MD potential-energy vs. step | no | supplementary only — too detailed for main text |
| slide_05_md_temperature.pdf | MD temperature trace | no | supplementary |
| slide_06_md_rdf.pdf | Radial distribution functions | no | supplementary; useful for "is it a glass or a crystal?" Q&A |
| slide_07_structures_bcc.pdf | Rendered BCC structures (R1, R2, R3 ISRU blend) | no | strong candidate for §6 — visual anchor for the three reference compositions |
| slide_08_structures_isru_phases.pdf | Rendered FCC, HCP, BCC ISRU structures | no | strong candidate for §6 |
| slide_09_md_snapshot.pdf | MD snapshot at high T | no | supplementary |
| slide_10_pugh_ductility.pdf | Pugh G/B map | DEPRECATED | user instruction: do not use Pugh diagrams in the paper |
| slide_11_pugh_dilution_path.pdf | Pugh G/B along dilution path | DEPRECATED | same |

Plus 11 individual `ovito/*.png` atomic-structure renders (HfNbTaTiZr, MoNbTaTiV, ISRU blend BCC/FCC/HCP).
**Recommendation:** if any of slide_03, slide_07, slide_08 belong in the paper, they should be added
as labelled figures with proper captions (and `\cite{Batatia2025MACEMH1, Togo2015Phonopy}` already
in `references.bib`). All others are presentation-only.

---

## 6. What I will *not* do until you've had the professor discussion

- I will not invent numbers (mass balance, power budget, throughput) that aren't in the literature.
- I will not name vendors or facilities in the paper that haven't been confirmed by the consortium.
- I will not extend the §Manufacturing Pipeline section in `main.tex` until §1-§4 of this file are at least partly answered.
- I will not move any of the presentation slides into the paper without your explicit go-ahead.

What I *will* do, on your word:
- Run a focused literature scan on any specific question above using web search / paper search MCP.
- Draft replacement paragraphs for §Manufacturing Pipeline that swap rhetoric for cited numbers, once
  we know which numbers are defensible.
- Pull any of slides 03 / 07 / 08 into the paper as a properly captioned figure.
