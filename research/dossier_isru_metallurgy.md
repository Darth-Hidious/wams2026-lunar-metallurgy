# Lunar ISRU metallurgy with refractory high-entropy alloys — manufacturing-engineering research dossier

**Scope note.** This dossier is restricted to manufacturing-engineering evidence relevant to feedstock qualification, consolidation, additive demonstration, and hot-fire validation. It does not modify first-party alloy-design, XRD, phonon, or mechanical-test claims. Citation keys are formatted for direct use in `references.bib`; complete BibTeX entries are collected in §7. Values marked `[unknown]` were not found in open primary or peer-reviewed review literature and should not be replaced by estimates without a source.

## §1. ISRU extraction routes — comparative quantitative table

**Interpretation of “product”.** The three ISRU routes below are oxygen-production routes that also generate metal-bearing products. For the manuscript’s RHEA manufacturing claim, the important point is that none of the three routes has yet demonstrated production of purified refractory elemental powders such as Mo, Nb, Ta, W, Cr, or V. Where power is reported per kg O₂ rather than per kg metal, this is stated explicitly.

| Process | Primary product(s) | Feedstock requirement | Operating T (K) | Operating P | Reagents required | Power demand (kWh / kg product) | Demonstrated TRL | Demonstrated throughput | Best-known O₂ co-yield (kg O₂ / kg metal) | Key open issues | Primary reference |
|---|---|---|---:|---|---|---|---|---|---|---|---|
| H₂ reduction of ilmenite | Reduced Fe-bearing grains plus H₂O; O₂ is obtained only after downstream water electrolysis. Ti remains mainly as TiO₂-bearing residue. | Specific limiting phase: ilmenite, FeTiO₃. Best target is high-Ti mare basalt/regolith. Mapped ilmenite examples: Mare Australe 4–7 wt% in many mare units and 7–11 wt% on some crater walls; Mare Ingenii 0–6 wt% \cite{Lemelin2013IlmeniteMapping}. Apollo high-Ti mare soils/basalts are the canonical feedstock class \cite{Chambers1995IlmeniteOxygen}. | 1123–1373 K in Sargeant laboratory tests; practical processing commonly centred near 1273 K for ilmenite reduction kinetics \cite{Sargeant2020IlmeniteHydrogen}. | Laboratory H₂ partial pressures 118–418 mbar in Sargeant static-system tests; lunar production pressure not yet fixed \cite{Sargeant2020IlmeniteHydrogen}. | Stoichiometric reaction FeTiO₃ + H₂ → Fe + TiO₂ + H₂O requires 0.036 kg H₂ per kg Fe if H₂ is not recycled. Net make-up H₂ for a closed lunar plant is `[unknown]`. | 24.3 ± 5.8 kWh per kg **liquid O₂** for an end-to-end model at 10 wt% ilmenite feedstock; power per kg Fe product is `[unknown]` because Fe recovery/product handling was not the modeled product \cite{Leger2025EnergyIlmenite}. | TRL 4–5 for chemistry plus payload/breadboard demonstration logic; no open source found assigning a formal production-plant TRL. Sargeant/ProSPA is a small-scale ISRU demonstration path, not a kg/day production plant \cite{Sargeant2020IlmeniteHydrogen}. | Sargeant experiments used approximately tens of mg of ilmenite per run; open literature does not report a kg/day ilmenite-reduction metal-production throughput. Write `[unknown]` for g/day or kg/day production. | Stoichiometric O₂-equivalent from the reducible FeO component is 16/55.845 = 0.286 kg O₂ per kg Fe. Sargeant measured 4.42 ± 0.18 wt% O₂-equivalent from ilmenite at 1100 °C after 4 h, corresponding to 42.0 ± 1.7% of the theoretical FeO-component oxygen yield \cite{Sargeant2020IlmeniteHydrogen}. | Requires ilmenite-rich terrane and beneficiation; H₂ recycle/leakage is mission-critical; kinetics and grain-size dependence dominate plant sizing; Fe product is not a purified RHEA feedstock. | Sargeant et al., 2020, *Planetary and Space Science*, DOI 10.1016/j.pss.2019.104751. |
| Molten Regolith Electrolysis (MRE) | Fe–Si-rich cathode alloy/metal plus O₂ at the anode; product chemistry follows regolith chemistry and electrochemical selectivity. | Bulk silicate regolith, not a single mineral phase. Highlands regolith is attractive for oxygen production; mare regolith gives more Fe-bearing metal. Mineral-phase fraction is therefore `[not applicable]`; the limiting feed is molten bulk regolith plus electrode/containment compatibility \cite{Sibille2010MRE,Schreiner2016MREModel}. | Approximately 1873 K; Sibille describes direct electrolysis of molten regolith near 1600 °C without a supporting electrolyte \cite{Sibille2010MRE}. | Laboratory reactor pressure is not a standard product specification in the cited MRE papers; operation is in a sealed high-temperature cell, and lunar-vacuum interface design is `[unknown]`. | No stoichiometric chemical reductant. Consumables are electrical energy, electrodes/anode materials, containment, and product-withdrawal hardware. Net electrode/containment loss per kg product is `[unknown]`. | Schreiner’s sizing model gives 14 kW for 1000 kg O₂/yr and 56.5 kW for 10,000 kg O₂/yr; calculated continuous-energy equivalents are 122.6 and 49.5 kWh/kg O₂, respectively. kWh/kg Fe–Si alloy is `[unknown]` \cite{Schreiner2016MREModel}. | TRL 3–4 for integrated laboratory reactor demonstrations with molten transfer; no open source found for a formal flight-production TRL. | Sibille reports scale-up from earlier 20–200 g experiments to 500 g–1 kg molten simulant volumes and currents up to 10 A. Metal kg/day throughput is `[unknown]` \cite{Sibille2010MRE}. | A review/system case reports 23.9 t/yr O₂ co-produced with 25 t/yr ferrosilicon alloy, i.e. approximately 0.956 kg O₂/kg Fe–Si alloy; this is a system-study value and composition-dependent \cite{Schluter2020OxygenReview}. | Inert anode durability, refractory containment corrosion, melt withdrawal, alloy-composition control, and dust-to-melt thermal management. Product is a mixed Fe–Si stream, not RHEA-grade elemental powder. | Sibille et al., 2010, NASA/AIAA/NTRS; Schreiner et al., 2016, *Advances in Space Research*, DOI 10.1016/j.asr.2016.01.006. |
| FFC-Cambridge / molten-salt electro-deoxidation of regolith | Mixed metallic alloy powder/agglomerates plus O₂ at an oxygen-evolving anode; typical products from simulants are multi-element Al/Si/Ca/Fe/Ti-bearing metal mixtures rather than purified elements. | Powdered bulk regolith/simulant in molten salt. Not mineral-phase-specific. Highlands anorthositic simulants are favourable for electrochemical efficiency and Al/Ca/Si-rich products; mare simulants give more Fe/Ti-bearing products. Limiting mineral mass fraction is therefore `[not applicable]` unless anorthosite is deliberately isolated \cite{Lomax2020FFC,Schild2025HighlandProducts}. | CaCl₂ FFC work is commonly in the 1173–1223 K class. A related molten-fluoride study used 1073 K for mare analogue in LiF–NaF; do not transfer the fluoride number directly to CaCl₂ FFC \cite{Schwandt2012FFCLunar,Maes2024FluorideSalt}. | Laboratory molten-salt cells; pressure specification for a lunar pilot is `[unknown]`. Operation is not demonstrated as an exposed-vacuum process. | Salt inventory, anode material, and reactor hardware. Carbon anodes would be consumed if used; oxygen-evolving SnO₂-type anodes reduce carbon demand but corrosion/losses remain. kg reagent loss per kg product is `[unknown]` \cite{Lomax2020FFC}. | FFC kWh/kg metal product is `[unknown]` in the open sources reviewed. Lomax demonstrates extraction viability; Maes reports 12.3 kWh/kg O at 43.4% current efficiency for a different molten-fluoride route, not directly FFC \cite{Lomax2020FFC,Maes2024FluorideSalt}. | TRL 3–4 for laboratory electrochemical proof-of-concept; no open source found for a formal lunar pilot-plant TRL. | Batch laboratory scale; open sources do not report a kg/day FFC regolith-metal-production demonstration. Write `[unknown]` for demonstrated g/day or kg/day throughput unless a project-specific test report is provided. | Lomax reports up to 96% total oxygen extraction from simulant, but only approximately one-third of oxygen was detected in the off-gas in that apparatus, with the remainder associated with reactor/anode corrosion losses. kg O₂/kg metal depends on feedstock oxide chemistry and is `[unknown]` for purified alloy product \cite{Lomax2020FFC}. | Metal product is heterogeneous and multiphase; salt carryover and anode/containment contamination must be removed before any PM feedstock claim; product refining into specific alloys is not yet demonstrated. | Lomax et al., 2020, *Planetary and Space Science*, DOI 10.1016/j.pss.2019.104748; Schwandt et al., 2012, *Planetary and Space Science*, DOI 10.1016/j.pss.2012.06.011. |

**Terrane suitability — H₂ reduction of ilmenite.** This route is best matched to ilmenite-bearing high-Ti mare basalt and high-Ti mare regolith, not highlands anorthosite and not KREEP as a primary process target. The limiting mineral is ilmenite, FeTiO₃. The strongest open quantitative terrane support is orbital/regional ilmenite mapping: Lemelin et al. report Mare Australe values of 4–7 wt% in many mare units and 7–11 wt% on some crater walls, while Mare Ingenii ranges from 0–6 wt% \cite{Lemelin2013IlmeniteMapping}. Chambers et al. show why high-Ti Apollo mare materials have historically been the oxygen-production benchmark and why beneficiation is essential: even an ilmenite-rich soil is still a mixed mineral assemblage, and ilmenite liberation/concentration matters \cite{Chambers1995IlmeniteOxygen}. For the manuscript, H₂ reduction should be described as a mare-specific Fe/O₂ route with possible Fe-bearing byproduct, not a general lunar metal-feedstock route for refractory RHEAs.

**Terrane suitability — MRE.** MRE is the least terrane-restrictive of the three routes because it melts and electrolyses bulk silicate regolith rather than targeting one mineral phase. For oxygen production, highlands regolith is attractive because it is abundant and oxygen-rich; Schreiner’s sizing model is explicitly a highlands-regolith oxygen-plant model \cite{Schreiner2016MREModel}. For metal feedstock, mare regolith is more attractive when the desired coproduct is Fe-bearing cathode metal, because FeO-bearing mafic components increase Fe in the melt. The limiting “mass fraction” is not a mineral such as ilmenite but the bulk oxide inventory and melt/electrode compatibility. Therefore, MRE can support a credible ISRU Fe–Si alloy lane, but it does not by itself support a claim of Mo/Nb/Ta/W RHEA powder substitution.

**Terrane suitability — FFC-Cambridge.** FFC-style molten-salt electro-deoxidation is suitable for powdered bulk regolith or isolated mineral fractions, but product chemistry follows feedstock chemistry. Highlands anorthosite-rich material can give Al/Ca/Si-rich products and, in recent FFC endpoint/product studies, appears electrochemically favourable relative to mare simulants \cite{Lomax2025Endpoint,Schild2025HighlandProducts}. Mare material can yield Fe/Ti-bearing products but tends to complicate product heterogeneity. KREEP is not the natural primary target for mass production because its defining incompatible-element enrichment is not aligned with bulk O₂ or simple alloy production. The manuscript should treat FFC products as mixed precursor metals requiring refining, not as direct RHEA elemental powder feedstock.

## §2. Equipment vendors and lunar-deployment readiness

**Boundary condition.** The equipment below is real terrestrial equipment or peer-reviewed process demonstration hardware. None of the open sources reviewed shows a flight-qualified lunar HP/SPS, mechanical-alloying, LPBF/DED, or <1 ppm O₂/H₂O powder glovebox system. NASA field-analog ISRU integration literature is useful for system-level mass/power thinking, but it does not close this metal-manufacturing equipment gap \cite{Sanders2011ISRUFieldAnalogs}. Therefore the safest manuscript wording is: *COTS terrestrial hardware demonstrates the thermal, pressure, atmosphere, and powder-handling envelope; lunar deployment requires a separate mass-, dust-, vacuum-, thermal-control-, and autonomy-focused equipment-development programme.*

### Consolidation and validation equipment comparison

| Equipment class | Earth-side vendors / models with relevant envelope | Published mass / footprint / power | Flight heritage or space-qualification status in open literature | 1 kg/day lunar pilot-plant implication |
|---|---|---|---|---|
| HP / SPS / FAST at 1200–1700 °C, 30–50 MPa, vacuum-capable, hot-zone ≥50 mm | FCT Systeme HP D / H-HP D series. FCT brochure lists HP D 10 with Ø50 mm, 100 kN, 37 kW; HP D 25 with Ø80 mm, 250 kN, 60 kW; and H-HP D25 class with Ø100 mm, 250 kN, 60 kW FAST / 80 kW induction / 100 kW hybrid capability \cite{FCT2014SPSBrochure}. IFW Dresden’s FCT H-HP D25-5D/FL facility page reports 250 kN, 60 kW FAST/SPS, 80 kW induction, 100 kW hybrid, Ar/N₂/vacuum, graphite tooling to 50 MPa, and 10–80 mm pressing-tool diameters \cite{IFW2026FCTHHPD25}. MTI’s YLJ-SPS-T20 page gives 50 MPa and 1600 °C in a smaller SPS class \cite{MTI2026SPST20}. | FCT power is public as above. Open FCT/IFW sources reviewed do not give machine mass or full footprint for the ≥50 mm hot-zone class, so mass/footprint are `[unknown]`. | No lunar or orbital flight heritage found for HP/SPS/FAST metal-consolidation equipment in the open literature reviewed. Space qualification should not be implied. | Use 60–100 kW peak electrical as a ground-pilot power class for an Ø80–100 mm COTS-equivalent SPS/FAST module. Mass is `[unknown]`; any manuscript number below a weighed vendor design would be speculative. A 1 kg/day pilot can plausibly use batch SPS/HP if billets are ≤50–80 mm diameter, but duty factor, tooling mass, die wear, and autonomous powder loading remain unproven. |
| Mechanical alloying mills demonstrated for sub-µm / ultrafine RHEA powder production | Tong et al. used a TENCAN planetary mill to prepare ultrafine MoNbTaW powders by mechanical alloying with no PCA, ethanol, and stearic acid; the paper reports single-BCC powder formation and nanoscale crystallites after 60 h \cite{Tong2018MoNbTaWPowders}. Qiao et al. mechanically alloyed a Ti/Zr/Nb/Ta RHEA powder family and showed liquid PCA improved recovery and homogeneity \cite{Qiao2020TiZrNbTaPCA}. Vendor analogues suitable for sealed inert milling include Retsch PM 400 and Fritsch PULVERISETTE 7 premium line with gas-tight/gassing lids \cite{Retsch2026PM400,Fritsch2026Pulverisette7}. | Retsch PM 400: 4 grinding stations, jar sizes up to 500 mL, final fineness down to 0.1 µm, power consumption about 2200 W, dimensions 836 × 1220/1900 × 780 mm, net weight about 290 kg \cite{Retsch2026PM400}. Fritsch PULVERISETTE 7 premium line: 2 bowls, up to 1100 rpm, 1200 W electrical, vendor-reported weight about 44 kg in reseller technical data; official Fritsch page gives the 1200 W value \cite{Fritsch2026Pulverisette7}. | No flight heritage found for high-energy RHEA mechanical-alloying mills. Gas-tight jars are terrestrial COTS, not lunar-qualified rotating pressure vessels. | If the existing process retains 40 h MA residence time, one daily 1 kg output requires either a >1 kg sealed charge or multiple parallel jars. Public mill datasheets report jar volume and machine mass/power but not qualified RHEA charge mass per cycle, so charge mass per cycle is `[unknown]`. A conservative COTS pilot stack would be at least one PM400-class mill, 290 kg and 2.2 kW; two PM400-class mills would be 580 kg and 4.4 kW before glovebox, jars, spares, and dust containment. |
| LPBF / DED for refractory metals and RHEA near-net-shape coupons | EOS M 290 and EOS M 290 1kW: 250 × 250 × 325 mm build volume; 400 W or 1000 W Yb-fibre laser options; EOS reports typical/max power values for the M290 class and a mass of about 1250 kg \cite{EOS2026M290,EOS2026M2901kW}. Nikon SLM 280: 280 × 280 × 365 mm build volume, up to two 700 W lasers in public brochures \cite{NikonSLM2024SLM280}. DMG MORI LASERTEC 65 DED hybrid provides a DED-plus-machining architecture for larger 5-axis parts, but open product data reviewed did not provide a clean mass/power figure for lunar sizing \cite{DMGMori2026Lasertec65DED}. | EOS M 290: build 250 × 250 × 325 mm; machine mass about 1250 kg; recommended installation space 4800 × 3600 × 2900 mm; power values in the M290 class include typical 2.4 kW and maximum 8.5 kW for single-laser configurations \cite{EOS2026M290,EOS2026M2901kW}. Nikon and DMG open pages give build envelope but mass/power for a specific lunar-relevant configuration are `[unknown]`. | No flight heritage found for metal LPBF/DED systems. These are terrestrial industrial systems with inert gas, optics, powder sieving, and dust-explosion control requirements. | A realistic ground pilot can use one EOS M290-class machine for coupon/chamber-liner demonstrations: 1250 kg and up to 8.5 kW machine power, excluding gas-handling, powder recycle, sieving, and inspection. A lunar pilot should not depend on LPBF as the daily 1 kg consolidation route unless powder recycle and optics contamination under lunar dust conditions are separately qualified. |
| Glovebox / inert-atmosphere powder handling at O₂ <1 ppm and H₂O <1 ppm | MBRAUN LABmaster Pro offers <1 ppm oxygen and humidity in N₂/Ar/He environments \cite{MBraun2026LABmasterPro}. VAC Omni-Lab systems specify purifier operation to below 1 ppm O₂/H₂O in user documentation and product pages \cite{VAC2026OmniLab}. MTI multi-chamber glovebox examples specify O₂ <1 ppm and H₂O <1 ppm and publish a 6 kW maximum power value for a five-chamber configuration \cite{MTI2026Glovebox}. | MBRAUN and VAC provide purity specifications but open pages reviewed did not give a complete mass/power/flight package for powder metallurgy. VAC single-length glovebox dimensions in public user documentation are 1143 × 762 × 914 mm for a two-port box \cite{VAC2026OmniLab}. MTI gives 6 kW maximum power for a five-chamber <1 ppm glovebox \cite{MTI2026Glovebox}. Mass is `[unknown]`. | No open source found for a lunar-qualified <1 ppm O₂/H₂O powder-metallurgy glovebox running RHEA powders. Existing space gloveboxes are not direct substitutes for abrasive reactive metal-powder processing. | Treat the glovebox as a required subsystem, not laboratory furniture. For a 1 kg/day ground pilot, assume at least one two- to four-port powder glovebox plus antechambers, purifier, HEPA/metal-dust filters, and mill-jar interface. Use 2–6 kW as a sourced terrestrial power envelope only if the exact vendor configuration is selected; mass remains `[unknown]`. |



### Mechanical-alloying mill specifics for the RHEA powder lane

| Mill / source | RHEA or HEA powder evidence | Charge mass per cycle | Power / footprint / mass | Atmosphere control | Notes for 1 kg/day pilot |
|---|---|---|---|---|---|
| TENCAN planetary ball mill used by Tong et al. | MoNbTaW powder, 300 rpm, ball-to-powder ratio 10:1, up to 60 h; evacuated/refilled Ar vials; no PCA, ethanol, and stearic-acid cases; crystallite sizes 11.8 nm, 24.2 nm, and 14.7 nm for no PCA, ethanol, and stearic acid, respectively \cite{Tong2018MoNbTaWPowders}. | `[unknown]`; the paper reports BPR and milling schedule, not kg-scale charge mass. | Vendor model, machine power, and machine mass are `[unknown]` in the paper. | Evacuated and refilled with high-purity Ar; steel vials/balls. | Strong RHEA powder evidence but not a scaleable pilot-plant equipment specification. |
| RHEA liquid-PCA MA study by Qiao et al. | Refractory Ti/Zr/Nb/Ta powder family; no PCA and stearic acid produced severe cold-welding/low recovery, while ethanol/n-heptane liquid PCAs increased recovery from 5% to 90% and improved homogeneity \cite{Qiao2020TiZrNbTaPCA}. | `[unknown]` in the accessible source summary. | Machine power/mass `[unknown]` in the accessible source summary. | Liquid PCA cases; inert handling implied by RHEA powder practice but flight atmosphere control not established. | Strong evidence that PCA choice is a process variable, not a consumables footnote. |
| Retsch PM 400 COTS analogue | Vendor mill, not itself a published RHEA demonstration in the sources reviewed. Supports dry/wet grinding and inert jar options; final fineness specification down to 0.1 µm \cite{Retsch2026PM400}. | RHEA charge mass per cycle `[unknown]`; jar volume up to 500 mL. | ≈2.2 kW, ≈290 kg, 836 × 1220/1900 × 780 mm \cite{Retsch2026PM400}. | Gas-tight/aeration lid options; actual Ar-overpressure RHEA protocol must be qualified. | A COTS mass/power anchor for a ground pilot, not proof of 1 kg/day RHEA throughput. |
| Fritsch PULVERISETTE 7 premium line COTS analogue | Vendor mill suitable for high-energy dry/wet grinding; not itself a published RHEA pilot throughput demonstration in the sources reviewed \cite{Fritsch2026Pulverisette7}. | RHEA charge mass per cycle `[unknown]`; bowl sizes in the micro-mill class are small relative to 1 kg/day production. | 1200 W electrical; public reseller data give about 44 kg, but the official Fritsch citation used here anchors the power value \cite{Fritsch2026Pulverisette7}. | Protective-gas lids are available in the product family; exact lunar-safe jar configuration must be qualified. | Useful for screening PCA/atmosphere matrices, not a sufficient production mill by itself. |

### LPBF / DED refractory-metal demonstration specifics

| System or process evidence | Vendor / build envelope / laser power | Demonstrated refractory result | Demonstrated minimum porosity or density | Caveat for manuscript wording |
|---|---|---|---|---|
| EOS M 290 / EOS M 290 1kW COTS LPBF | EOS; 250 × 250 × 325 mm build volume; 400 W and 1000 W single-laser options; machine mass about 1250 kg; typical/max power values in the M290 class include 2.4/8.5 kW for single-laser configurations \cite{EOS2026M290,EOS2026M2901kW}. | Vendor platform is suitable for controlled refractory-powder AM trials; the cited RHEA demonstrations are process evidence, not necessarily EOS-specific qualification. | Vendor page does not provide a RHEA porosity number. | Use as a ground-pilot platform reference, not a lunar-qualified printer. |
| Pure Mo LPBF process demonstration | Rebesan et al. report LPBF of pure Mo; the article notes dense Mo was obtained even with laser power lower than 200 W \cite{Rebesan2021MolybdenumLPBF}. | Pure Mo, a refractory metal. | 99.5 ± 0.5% density by Archimedes; equivalent residual porosity should be reported as approximately 0.5% only with the same uncertainty caveat \cite{Rebesan2021MolybdenumLPBF}. | Strong evidence for refractory LPBF processability, not ISRU powder equivalence. |
| RHEA LPBF / SLM demonstrations | Gu et al. on VNbMoTaW SLM; Mooraj et al. on near-defect-free TiZrNbTa LPBF by in-situ alloying of elemental powders \cite{Gu2022VNbMoTaWLPBF,Mooraj2024TiZrNbTaLPBF}. | Refractory HEA families processed by powder-bed fusion. | Numeric porosity values are not extracted in this dossier except where explicitly reported in the accessible source; write `[unknown]` for a manuscript table unless the original article’s porosity/density value is inserted. | Supports “LPBF/DED demo is credible,” not “ISRU-derived powder is qualified.” |
| Nikon SLM 280 COTS LPBF | Nikon SLM Solutions; 280 × 280 × 365 mm build envelope; public brochure class supports up to two 700 W lasers \cite{NikonSLM2024SLM280}. | Vendor platform only in this dossier. | `[unknown]` for RHEA porosity from the vendor sheet. | Include only as an available industrial platform if the manuscript needs vendor examples. |
| DMG MORI LASERTEC 65 DED hybrid | DMG MORI; 5-axis DED-plus-machining platform; public page gives large workpiece-envelope information but not a clean lunar-sizing mass/power value in the sources reviewed \cite{DMGMori2026Lasertec65DED}. | DED architecture is relevant to chamber-liner repair/build-up; refractory HEA DED process evidence comes from Dobbelstein and Li rather than this vendor sheet \cite{Dobbelstein2019TiZrNbTaLMD,Li2019WxNbMoTaCladding}. | `[unknown]` for vendor-specific RHEA porosity in open data reviewed. | Treat as a terrestrial near-net-shape demonstrator, not a flight plant. |

### Equipment-specific manufacturing notes for manuscript use

**HP/SPS.** The paper’s current hot-pressing parameters, 1500 °C / 2 h / 30 MPa for refractory-class material and a lower-temperature condition for Ni-based material, are inside the public thermal-pressure envelope of terrestrial HP/SPS/FAST hardware. The manufacturing risk is therefore not “can Earth machines press this billet?” but “can a lunar-qualified machine close the same thermal, pressure, atmosphere, tooling, and metrology loop?” FCT/IFW-class equipment demonstrates that 50 MPa graphite-tooling SPS with 10–80 mm die diameters and 60–100 kW heating hardware is a real engineering envelope \cite{FCT2014SPSBrochure,IFW2026FCTHHPD25}. The manuscript should state that lunar pilot mass is not yet defensible from open literature.

**Mechanical alloying.** RHEA mechanical alloying has been demonstrated on refractory powder systems, but the papers show strong sensitivity to PCA choice, cold welding, morphology, and contamination. Tong et al. obtained ultrafine MoNbTaW powders by MA under no PCA, ethanol, and stearic-acid conditions; Qiao et al. found that liquid PCA raised powder recovery from 5% to 90% in a refractory Ti/Zr/Nb/Ta powder family \cite{Tong2018MoNbTaWPowders,Qiao2020TiZrNbTaPCA}. Therefore, the equipment lane should be written as “MA process qualification under a defined PCA/atmosphere matrix,” not “40 h heptane milling is flight-ready.”

**LPBF/DED.** LPBF and DED are credible validation tools for near-net-shape demonstration, not yet the least-risk route for daily lunar production. Pure Mo LPBF reached 99.5 ± 0.5% density in Rebesan et al.; LPBF/SLM of VNbMoTaW and near-defect-free LPBF of TiZrNbTa-class refractory HEA have been reported; laser metal deposition of compositionally graded TiZrNbTa and laser cladding of WxNbMoTa have also been demonstrated \cite{Rebesan2021MolybdenumLPBF,Gu2022VNbMoTaWLPBF,Mooraj2024TiZrNbTaLPBF,Dobbelstein2019TiZrNbTaLMD,Li2019WxNbMoTaCladding}. The manuscript should use LPBF/DED as a Phase-2/Phase-3 coupon and liner-shape demonstrator, not as proof that regolith-derived metal powders can be substituted into RHEA PM lots.

**Glovebox and powder QC.** The <1 ppm O₂/<1 ppm H₂O requirement is reachable in terrestrial gloveboxes, but lunar qualification introduces abrasive dust, electrostatic fines, vacuum/pressure-cycle hardware, leak-rate control, and remote maintenance. The current manuscript’s “powder blending in glovebox/Ar” statement is technically plausible but underspecified. Add acceptance tests for O/N/H/C/S, PSD, apparent/tap density, Hall/Carney flow, XRD, SEM-EDS homogeneity, and lot-level retained witnesses before any ISRU substitution lot is admitted.

## §3. Heptane PCA replacement for lunar mechanical alloying

The existing “40 h MA in heptane process-control agent” is a laboratory baseline, not a lunar baseline. Suryanarayana’s review frames the central issue: a PCA suppresses excessive cold welding during high-energy milling, but the PCA also becomes a potential source of C, O, and H contamination and can change particle morphology, recovery, and alloying kinetics \cite{Suryanarayana2001Mechanical}. HEA/RHEA-specific work confirms that this is not a minor detail; it is a feedstock-qualification variable \cite{Vaidya2019HEAMechanicalAlloying,Tong2018MoNbTaWPowders,Qiao2020TiZrNbTaPCA,Moravcik2020Contamination}.

| PCA / atmosphere option | Demonstrated for HEA/RHEA MA? | Reported morphology / recovery effect | Reported oxygen/carbon pickup effect | Lunar sourcing plausibility | Dossier judgement |
|---|---|---|---|---|---|
| n-Heptane | Yes, in refractory Ti/Zr/Nb/Ta MA as a liquid PCA comparator \cite{Qiao2020TiZrNbTaPCA}. | Liquid PCA mitigated cold welding and raised recovery relative to no PCA/solid PCA; Qiao reports recovery improvement from 5% to 90% when liquid PCA was used \cite{Qiao2020TiZrNbTaPCA}. | Qiao reports minimal C/O interstitial contamination for the liquid-PCA powders, but the open abstract/summary does not provide a universal oxygen-in-ppm number. | Poor. Heptane is an Earth-supplied hydrocarbon; lunar synthesis at kg/batch scale would require a separate carbon/hydrogen chemical plant. | Good laboratory control, poor lunar baseline. Keep only as Earth-control condition. |
| Ethanol | Yes. Tong used ethanol in MoNbTaW MA; Qiao used ethanol in refractory Ti/Zr/Nb/Ta MA \cite{Tong2018MoNbTaWPowders,Qiao2020TiZrNbTaPCA}. | Tong reports alcohol PCA changes powder morphology relative to no PCA/stearic acid; Qiao shows liquid PCA suppresses cold welding and improves homogeneity/recovery \cite{Tong2018MoNbTaWPowders,Qiao2020TiZrNbTaPCA}. | Quantitative O pickup is not consistently reported as a comparable ppm value. Qiao states C/O interstitial contamination was minimal under liquid-PCA conditions; Tong reports Fe/Cr wear contamination, reminding that jar/ball chemistry is also a contamination source \cite{Tong2018MoNbTaWPowders,Qiao2020TiZrNbTaPCA}. | Possible only with a separate C/H/O chemical loop; not demonstrated as lunar ISRU consumable. | Best near-term replacement candidate for ground qualification because it is already demonstrated in RHEA MA, but not “ISRU-sourced” today. |
| Methanol | Demonstrated in mechanically alloyed HEA work as a PCA, but not found as a primary RHEA demonstration in the open sources reviewed \cite{RuizEsparza2021PCA}. | HEA literature shows PCA choice influences synthesis and phase stability; direct RHEA sub-µm morphology transfer is `[unknown]` \cite{RuizEsparza2021PCA}. | Methanol introduces O/H/C contamination risk; quantitative oxygen pickup for the target RHEA lane is `[unknown]`. | Chemically plausible from CO/CO₂ + H₂ chemistry if carbon and hydrogen streams exist, but lunar regolith carbon is scarce and a pilot-scale methanol plant is unproven. | Plausible research option; do not make it the baseline without a RHEA powder recovery/contamination dataset. |
| Stearic acid | Yes. Tong used stearic acid in MoNbTaW MA; Qiao used it as a solid PCA comparator \cite{Tong2018MoNbTaWPowders,Qiao2020TiZrNbTaPCA}. | Tong found stearic-acid/no-PCA conditions yielded near-spherical powders relative to alcohol-lamellar morphologies; Qiao found solid PCA did not solve the cold-welding/recovery problem as effectively as liquid PCA \cite{Tong2018MoNbTaWPowders,Qiao2020TiZrNbTaPCA}. | High C/H/O contamination risk relative to dry inert milling; target-lot quantitative O/C uptake is `[unknown]`. | Poor. Long-chain organic acid is not a credible lunar consumable unless shipped. | Useful negative/control condition; not recommended for lunar baseline. |
| Oleic acid | Commonly used as a PCA in broader powder metallurgy, but no primary RHEA MA paper was found in the reviewed sources demonstrating oleic acid for sub-µm refractory HEA powder. | `[unknown]` for the target RHEA lane. | `[unknown]`; likely C/H/O risk. | Poor as an Earth-supplied liquid organic; ISRU synthesis unproven. | Do not include as a baseline unless a target-alloy MA study is generated. |
| Dry MA under Ar overpressure only | Yes for MoNbTaW in Tong et al.; Qiao found severe cold-welding/recovery problems without liquid PCA in a different refractory powder family \cite{Tong2018MoNbTaWPowders,Qiao2020TiZrNbTaPCA}. | Viable in some refractory systems, but not robust. Tong reports single-BCC MoNbTaW powders and nanoscale crystallites without PCA; Qiao reports low recovery without PCA and much better recovery under liquid PCA \cite{Tong2018MoNbTaWPowders,Qiao2020TiZrNbTaPCA}. | Avoids organic C/H/O source, but increases risk of cold welding, jar/ball wear, and Fe/Cr or WC pickup depending media. Tong reports Fe/Cr contamination in milled powder, so dry MA does not eliminate contamination \cite{Tong2018MoNbTaWPowders,Moravcik2020Contamination}. | Excellent from consumables perspective because Ar is already needed for powder handling, but Ar itself must be supplied or recycled. | Attractive but composition-dependent. It must be qualified, not assumed. |

**Recommendation.** Replace “40 h MA in heptane PCA” with “40 h MA under a qualified PCA/atmosphere condition; heptane is the Earth-control condition.” The qualification matrix should include dry Ar, ethanol, n-heptane, and stearic acid at minimum; methanol can be added as a lunar-chemistry research option if the manuscript discusses possible carbon chemistry. The release criteria should be powder recovery, PSD, morphology, flowability, O/N/H/C/S, Fe/Cr/WC wear pickup, XRD phase completion after MA, and post-HP/SPS density and phase equivalence. **Confidence: medium** for replacing heptane in the laboratory with ethanol or dry-Ar variants after down-selection; **confidence: low** that any liquid PCA can be ISRU-sourced at a useful lunar pilot scale today; **confidence: low-to-medium** for dry-MA as a universal sub-µm RHEA route because the RHEA literature is composition-dependent and sometimes contradictory \cite{Tong2018MoNbTaWPowders,Qiao2020TiZrNbTaPCA,RuizEsparza2021PCA,Moravcik2020Contamination}.

## §4. Hot-fire validation — named facility

The manuscript’s “180 bar / 800 K” validation statement needs a named facility and a staged test plan. In open literature, the only facility in the checked list with clear public ≥150 bar class combustion capability for small rocket-combustor research is DLR Lampoldshausen P8. Several other named sites are relevant to lower-pressure or system-level LOX/methane development, but the public sources reviewed do not support claiming they can host a 180 bar external sub-scale RHEA liner demo.

| Facility / stand checked | Region | Published chamber-pressure capability | Propellants supported in public sources | Sub-scale chamber / article envelope | External-customer hosting | Published cost basis | Fit for 180 bar RHEA chamber-liner hot-fire demo |
|---|---|---|---|---|---|---|---|
| DLR Lampoldshausen P8 | Europe | DLR states P8 is designed for operating pressures up to 360 bar and reports highest achieved combustion-chamber pressure of 330 bar \cite{DLR2026P8}. | Public P8 descriptions and SCORE-D facility papers support cryogenic H₂/O₂ research; P8 has also hosted high-pressure combustion research in European propulsion programmes \cite{DLR2026P8,Greuel2013SCORED}. | Research and technology test bench for sub-scale combustion devices, injectors, combustion chambers, and high-pressure technology demonstrations \cite{DLR2026P8,Greuel2013SCORED}. | Yes, via DLR/ESA/CNES/ArianeGroup-style research campaigns; open page describes regular research/test operations but not a simple list-price service. | `[not public]`. | **Best fit** in the checked list for ≥150 bar H₂/O₂ or oxygen-rich sub-scale combustion work. |
| DLR Lampoldshausen M3 / M3.1 / M3.4 family | Europe | DLR M3 fact sheet gives system pressures up to 40 bar for the M3 technical centre; older methane-facility literature reports ambient-pressure methane/oxygen work up to about 10 MPa for some M3 test capability, still below 150 bar \cite{DLR2023M3Factsheet}. | LOX, LN₂, gaseous fuels including H₂ and hydrocarbons in the public M3 fact sheet; methane/oxygen sub-scale work in older DLR literature \cite{DLR2023M3Factsheet}. | Useful for ignition, injector, cooling-channel, materials-screening, and lower-pressure combustion experiments. | Likely through DLR campaigns; no list-price external service basis found. | `[not public]`. | **Not sufficient** for a 180 bar chamber-pressure claim based on public data; useful Phase-2/early Phase-3 stepping stone. |
| ESA “Pyramid” | Europe | No public source found in this search establishing an ESA Pyramid hot-fire facility with ≥150 bar H₂/O₂ or CH₄/O₂ chamber-pressure capability. | `[unknown]`. | `[unknown]`. | `[unknown]`. | `[unknown]`. | Do not cite as a 180 bar venue unless an open facility data sheet is added. |
| NASA MSFC Propulsion Test Laboratory / E-Complex / Test Stand 116 | US | NASA public pages identify Test Stand 116 as a subscale test facility for high-pressure engine systems and components, but the public pages reviewed do not state a maximum combustion-chamber pressure \cite{NASA2021MSFCPTL,NASA2023TF116}. | NASA’s PTL capability sheet lists H₂, methane, O₂, N₂, He, RP-1, water, and TEA/TEB support media across the laboratory \cite{NASA2021MSFCPTL}. | Test Stand 115/116 descriptions include injectors, preburners, turbopumps, combustion chambers, igniters, seals, bearings, valves, and engine subsystems \cite{NASA2021MSFCPTL,NASA2023TF116}. | NASA can host external/partner tests through agreements, but open documents reviewed do not provide routine customer terms for this exact use case. | `[not public]`. | **Potential US candidate**, but do not claim ≥150 bar suitability unless MSFC provides a public or citable facility pressure envelope. |
| IHI / JAXA LOX-methane published test activity | Asia | Published LOX/LNG or LOX/methane injector/engine work found here reports lower-pressure ranges: an AIAA LOX/LNG injector study discusses experiments around 1–5 MPa and target needs around 8–10 MPa, while a 30 kN LOX/methane full-expander campaign reports successful hot-fire testing but not a ≥150 bar public chamber-pressure envelope \cite{Asakawa2016LOXLNG,Sakaki2023JAXAIHI}. | LOX/LNG or LOX/methane. | Engine/injector development articles, not general external sub-scale material-liner facility sheets. | External customer hosting not established in the open sources reviewed. | `[not public]`. | **Not supported** as a ≥150 bar external venue in the checked literature. |
| CNES / ArianeGroup Vernon / Prometheus-related testing | Europe | Prometheus public technical papers state a nominal chamber pressure of 100 bar, below the manuscript’s 180 bar claim \cite{Iannetti2017Prometheus}. | LOX/LCH₄ for Prometheus-class reusable engine development \cite{Iannetti2017Prometheus}. | Full engine and subsystem development context, not a general external high-pressure materials-liner rig. | External access not established in the open sources reviewed. | `[not public]`. | **Not sufficient** for a 180 bar validation claim; useful contextual European LOX/methane engine-development reference. |

**Facility recommendation.** The realistic Phase-3 venue for a sub-scale lunar-engine combustion-chamber demonstration using a refractory high-entropy-alloy chamber liner is **DLR Lampoldshausen P8**, under an ESA/DLR propulsion-materials demonstration campaign or a contracted DLR high-pressure combustor test campaign. The manuscript should make M3/M3.1/M3.4 the lower-pressure ignition/injector/cooling precursor venue, not the final 180 bar venue, unless a new public M3 pressure envelope is provided. NASA MSFC Test Stand 116 is a credible US discussion point because it is publicly described as a subscale high-pressure propulsion test facility with H₂/CH₄/O₂ support media, but its maximum chamber pressure for this use case is not public in the reviewed documents; therefore the paper should list it as “candidate pending facility confirmation,” not as the named baseline \cite{DLR2026P8,DLR2023M3Factsheet,NASA2021MSFCPTL,NASA2023TF116}.

## §5. The ISRU substitution boundary — defending the central claim

**Verdict: plausible-but-unproven.** The central claim should be weakened from a declarative programme claim to a testable feedstock-equivalence hypothesis. The open literature supports the idea that powder metallurgy can tolerate controlled feedstock variation if incoming powder specifications are met and if consolidation/phase/mechanical equivalence are requalified. The open literature does **not** show direct substitution of a regolith-derived metal stream into a refractory HEA/RHEA mechanical-alloying plus hot-press/SPS chain, consolidated to ≥95–98% relative density, with phase and mechanical response matched against an all-Earth-powder control. Therefore the manuscript should not say that ISRU substitution is already a constrained perturbation of a calibrated chain; it should say that it *can be reduced to a constrained perturbation only after the ISRU stream passes feedstock-equivalence gates*.

### What supports the weaker claim

First, the materials-processing half of the chain is real. RHEA powders can be mechanically alloyed from refractory elemental powders, and dense refractory or RHEA-like parts can be produced by SPS/HP or additive routes. Tong et al. demonstrate single-BCC ultrafine MoNbTaW powders after mechanical alloying; Qiao et al. show that liquid PCA can greatly improve RHEA powder recovery and homogeneity; Rebesan et al. demonstrate high-density LPBF Mo; Gu, Mooraj, Dobbelstein, and Li show that LPBF/DED/cladding can process refractory HEA families or canonical refractory systems \cite{Tong2018MoNbTaWPowders,Qiao2020TiZrNbTaPCA,Rebesan2021MolybdenumLPBF,Gu2022VNbMoTaWLPBF,Mooraj2024TiZrNbTaLPBF,Dobbelstein2019TiZrNbTaLMD,Li2019WxNbMoTaCladding}. These papers justify a manufacturing spine based on incoming powder release specifications, inert handling, MA, densification, and coupon/liner validation.

Second, the lunar ISRU extraction half is also real, but at a different product definition. H₂ reduction produces Fe-bearing reduced products and water/O₂ from ilmenite; MRE produces Fe–Si-rich cathode alloy and O₂ from molten bulk regolith; FFC/molten-salt routes produce mixed metallic products and O₂ from regolith simulants \cite{Sargeant2020IlmeniteHydrogen,Sibille2010MRE,Schreiner2016MREModel,Lomax2020FFC,Schwandt2012FFCLunar}. These routes support an ISRU metal-stream concept for Fe-, Si-, Al-, Ca-, and Ti-bearing products, and they support oxygen co-production. They do not yet support direct Mo/Nb/Ta/W elemental powder production.

Third, adjacent regolith/manufacturing work shows that lunar-simulant material can be incorporated into manufacturing studies, but mostly as ceramic/regolith feed or graded composite material, not as extracted metal powder. ESA ACT work and the Laot/Popovich functionally graded material studies show spark-plasma-sintered and additively manufactured Ti6Al4V/regolith or regolith-rich graded materials; those studies are relevant because they expose interfacial-reaction and segregation hazards, but they do not validate metal-source substitution into an RHEA powder lot \cite{Popovich2020FGMReport,Laot2021RegolithFGM}.

### What refutes the strong version of the claim

The strongest counter-evidence is product heterogeneity. FFC products are not clean elemental powders. Lomax et al. demonstrate high oxygen extraction from simulant, but the experiment also reports incomplete oxygen recovery at the off-gas and losses associated with reactor/anode corrosion \cite{Lomax2020FFC}. Schild et al. are even more directly relevant to the manuscript claim: the metallic products from molten-salt electrolysis of lunar highland simulants are heterogeneous and multiphase, and the paper explicitly cautions that straightforward mechanical approaches are not suited to refining the product into specific alloys \cite{Schild2025HighlandProducts}. That is a direct objection to treating the output as a plug-in elemental powder stream.

A second counter-example is contamination and chemistry drift. Maes et al. show that molten-salt processing of lunar simulant can create electrode-specific deposits and has finite simulant solubility in the molten salt; this is useful electrochemistry, but it also demonstrates that electrode and salt chemistry are part of the product-definition problem \cite{Maes2024FluorideSalt}. In the downstream powder lane, Moravcik et al. review contamination induced by mechanical alloying and sintering, while Tong and Qiao show that PCA choice changes morphology, recovery, and contamination risk \cite{Tong2018MoNbTaWPowders,Qiao2020TiZrNbTaPCA,Moravcik2020Contamination}. The practical implication is that even a ±5 wt% shift in an impurity-bearing ISRU stream cannot be waved through as a minor perturbation without lot-level requalification.

A third counter-example is interface reaction in regolith-containing manufacturing. In ESA ACT/Laot/Popovich graded-material work, Ti alloy/regolith combinations produced reaction products, silicon segregation, and oxide-rich interfaces under thermal processing conditions \cite{Popovich2020FGMReport,Laot2021RegolithFGM}. This does not prove that refined ISRU metal substitution will fail; it does prove that regolith-derived chemistry is not neutral, and that phase/segregation checks are mandatory.

### Boundary statement the paper can defend

The defensible claim is:

> Partial ISRU substitution becomes a constrained perturbation of the calibrated powder-metallurgy chain **only after** the ISRU-derived metal is refined and qualified to the same incoming-powder specification as the Earth-supplied elemental powder it replaces. Until such a lot is demonstrated, ISRU substitution is a feedstock-equivalence hypothesis, not an established manufacturing fact.

The equivalence gate should include, at minimum, PSD and morphology, apparent/tap density, flowability, O/N/H/C/S by combustion/inert-gas fusion, metallic impurities by ICP-OES/MS, XRD phase identity, SEM-EDS homogeneity, retained-powder witness samples, MA recovery and wear pickup, consolidated relative density, XRD/SEM phase equivalence after HP/SPS, and a mechanical-screening comparison against the all-Earth-powder control. Without that gate, the central claim is overextended.

## §6. Suggested manuscript edits

The table below is written for handoff to a paper-editing assistant. It intentionally avoids SPARK-series composition details and does not alter first-party alloy data, mechanical results, XRD results, or ab-initio results.

| Paper section | Anchor: existing sentence or phrase | Replacement / addition with citation keys | Why |
|---|---|---|---|
| §Manufacturing Pipeline / programme claim | “substituting an ISRU-derived stream for a fraction of Earth-supplied powder is a constrained perturbation of an already-calibrated process chain rather than a new development programme.” | Replace with: “Substituting an ISRU-derived stream should be treated as a **feedstock-equivalence hypothesis**. Once an ISRU-derived metal stream has been refined to meet the same incoming-powder release specification as the Earth-supplied powder it replaces—PSD, morphology, apparent/tap density, flowability, O/N/H/C/S, metallic impurity limits, phase identity, and lot homogeneity—partial substitution can be handled as a controlled requalification of the powder-metallurgy chain rather than an alloy-design restart. The open literature does not yet demonstrate direct substitution of regolith-derived metal into a refractory-HEA MA/HP/SPS lot; molten-salt and molten-regolith products remain mixed or heterogeneous and require refining before they can be treated as RHEA feedstock \cite{Lomax2020FFC,Schild2025HighlandProducts,Maes2024FluorideSalt,Tong2018MoNbTaWPowders,Qiao2020TiZrNbTaPCA}.” | This preserves the strategic argument but removes the unsupported implication that ISRU substitution has already been demonstrated. |
| §Manufacturing Pipeline / ISRU-feedstock lane | “bulk metals extracted from regolith” | Extend with: “In this paper, ‘bulk metals extracted from regolith’ denotes mixed ISRU metal streams, not automatically RHEA-grade elemental powder. H₂ reduction is ilmenite/mare-specific and produces Fe-bearing reduced material plus water/O₂ after electrolysis; MRE produces Fe–Si-rich cathode alloy plus O₂ from molten bulk regolith; FFC-style molten-salt electro-deoxidation produces mixed metallic products whose chemistry follows the regolith feedstock \cite{Sargeant2020IlmeniteHydrogen,Sibille2010MRE,Schreiner2016MREModel,Lomax2020FFC,Schwandt2012FFCLunar,Schild2025HighlandProducts}.” | The phrase “bulk metals” is too broad. This edit aligns each route with its actual product definition. |
| §Manufacturing Pipeline / ISRU-feedstock lane | “H₂ reduction of mare ilmenite (FeTiO₃) at ~1000 °C → Fe + O₂” | Replace with: “H₂ reduction of ilmenite at approximately 1000–1100 °C produces reduced Fe-bearing material and H₂O; O₂ is recovered only after downstream water electrolysis. The route is most suitable for ilmenite-rich mare terranes, with mapped ilmenite abundances varying strongly by mare unit, e.g. 4–7 wt% in many Mare Australe units and 7–11 wt% on some crater walls \cite{Sargeant2020IlmeniteHydrogen,Lemelin2013IlmeniteMapping,Chambers1995IlmeniteOxygen}.” | Avoids implying a direct one-step Fe + O₂ product and adds terrane dependence. |
| §Manufacturing Pipeline / ISRU-feedstock lane | “Molten Regolith Electrolysis (MRE) → Fe-Si alloy + O₂” | Add after phrase: “MRE is a bulk-regolith route rather than a mineral-specific route. Laboratory work has operated near 1600 °C and scaled molten simulant volumes to the 500 g–1 kg class with up to 10 A current; kg/day metal production and RHEA-grade metal refining remain unreported in open literature \cite{Sibille2010MRE}. Schreiner’s sizing model gives 14 kW for 1000 kg O₂/yr and 56.5 kW for 10,000 kg O₂/yr, corresponding to 122.6 and 49.5 kWh/kg O₂ on a continuous-energy basis \cite{Schreiner2016MREModel}.” | Adds the real engineering scale and prevents overclaiming throughput. |
| §Manufacturing Pipeline / ISRU-feedstock lane | “FFC-Cambridge molten-salt → Al-Si alloys” | Replace with: “FFC-Cambridge/molten-salt electro-deoxidation of regolith simulant can extract oxygen and produce mixed metal products, but the products are heterogeneous, multiphase, and feedstock-dependent. Recent product-characterisation work on highland simulants cautions that direct mechanical refining into specified alloys is not yet solved \cite{Lomax2020FFC,Schwandt2012FFCLunar,Schild2025HighlandProducts,Lomax2025Endpoint}.” | The current wording over-simplifies the product as a clean Al–Si alloy stream. |
| §Consolidation + QC lane | “powder blending in glovebox/Ar” | Add: “For ISRU-substitution lots, glovebox blending should be preceded by an incoming-powder release gate: PSD, SEM morphology, apparent/tap density, Hall/Carney flow where applicable, O/N/H/C/S, ICP-OES/MS impurities, XRD phase identity, and retained powder witnesses. Terrestrial gloveboxes can maintain <1 ppm O₂ and H₂O, but no open source was found for a lunar-qualified powder-metallurgy glovebox at this purity level \cite{MBraun2026LABmasterPro,VAC2026OmniLab,MTI2026Glovebox}.” | Converts glovebox handling from a generic statement to a QC-controlled interface. |
| §Consolidation + QC lane | “mechanical alloying 40 h with heptane process-control agent” | Replace with: “Mechanical alloying will be conducted for the calibrated residence time under a **qualified PCA/atmosphere condition**. Heptane is retained as the Earth-control PCA, not as the lunar baseline. A down-selection matrix should include dry Ar, ethanol, n-heptane, and stearic acid, with methanol as an optional ISRU-chemistry research case; selection is based on powder recovery, morphology, PSD, flowability, O/N/H/C/S, jar/ball wear pickup, XRD alloying completion, and post-consolidation density/phase equivalence \cite{Suryanarayana2001Mechanical,Tong2018MoNbTaWPowders,Qiao2020TiZrNbTaPCA,RuizEsparza2021PCA,Moravcik2020Contamination}.” | Heptane is an Earth-supplied hydrocarbon; the paper needs a lunar-compatible qualification plan. |
| §Consolidation + QC lane | Any implication that dry MA automatically solves the PCA issue | Add caution sentence: “Dry Ar mechanical alloying is attractive because it removes the organic PCA consumable, but it is not composition-agnostic: MoNbTaW powder has been mechanically alloyed without PCA, whereas a separate refractory Ti/Zr/Nb/Ta powder study found severe cold welding and low recovery without liquid PCA \cite{Tong2018MoNbTaWPowders,Qiao2020TiZrNbTaPCA}.” | Prevents a false fix: eliminating PCA may trade consumables for yield loss and contamination. |
| §Consolidation + QC lane | “vacuum hot pressing (1500 °C / 2 h / 30 MPa for refractory class...)” | Add after the parameter sentence: “These parameters fall within terrestrial HP/SPS/FAST equipment envelopes: FCT/IFW-class systems publicly report Ø50–80 mm tooling, 250 kN force, Ar/N₂/vacuum operation, graphite-tooling pressure up to 50 MPa, and 60–100 kW heating configurations. However, no open source was found for a lunar-qualified HP/SPS metal-consolidation unit; lunar deployment must therefore be treated as a separate equipment-development item \cite{FCT2014SPSBrochure,IFW2026FCTHHPD25,MTI2026SPST20}.” | Gives manufacturing credibility without implying flight readiness. |
| §Consolidation + QC lane | “≥98 % relative density” | Add: “For any ISRU-substitution lot, ≥98% relative density should be reported alongside the all-Earth-powder control made under the same die/tooling schedule, not as a stand-alone pass/fail value. Density equivalence should be paired with XRD phase equivalence and SEM/EDS segregation checks.” | The density target alone does not prove feedstock equivalence. |
| §Validation lane caption | “oxygen-rich ignition rig (claimed at 180 bar / 800 K)” | Replace with: “High-pressure oxygen-rich ignition/hot-fire validation will be staged. Lower-pressure ignition/injector and cooling-screening tests can use DLR M3-class facilities where appropriate, but a ≥150 bar sub-scale combustor/liner demonstration should nominate DLR Lampoldshausen P8, which publicly reports operation up to 360 bar and achieved combustion-chamber pressures up to 330 bar. NASA MSFC Test Stand 116 is a potential US candidate pending a citable maximum chamber-pressure envelope; Vernon/Prometheus-class public data are nominally 100 bar and should not be cited for a 180 bar validation claim \cite{DLR2026P8,DLR2023M3Factsheet,NASA2021MSFCPTL,NASA2023TF116,Iannetti2017Prometheus}.” | Names a realistic facility and removes unsupported generic “rig” language. |
| §Validation lane | “LPBF/DED near-net-shape demo” | Extend with: “The LPBF/DED activity should be framed as a geometry and processability demonstration, not as proof of ISRU-feedstock equivalence. Pure Mo LPBF has reached 99.5 ± 0.5% density, and refractory HEA LPBF/DED/cladding demonstrations exist, but those demonstrations used controlled terrestrial powders or elemental blends rather than regolith-derived metal streams \cite{Rebesan2021MolybdenumLPBF,Gu2022VNbMoTaWLPBF,Mooraj2024TiZrNbTaLPBF,Dobbelstein2019TiZrNbTaLMD,Li2019WxNbMoTaCladding}.” | Avoids conflating AM processability with ISRU-metal qualification. |
| §TRL Roadmap | Table row for ISRU extraction | Add sub-rows: “H₂ ilmenite reduction: TRL 4–5 chemistry/payload-breadboard class; kg/day Fe production `[unknown]`; 24.3 ± 5.8 kWh/kg liquid O₂ modeled at 10 wt% ilmenite \cite{Sargeant2020IlmeniteHydrogen,Leger2025EnergyIlmenite}. MRE: TRL 3–4 lab reactor; 500 g–1 kg simulant melt demonstrations; modelled 14 kW for 1000 kg O₂/yr \cite{Sibille2010MRE,Schreiner2016MREModel}. FFC: TRL 3–4 lab electrochemistry; up to 96% total oxygen extraction demonstrated but metal-product refining remains open \cite{Lomax2020FFC,Schild2025HighlandProducts}.” | Gives the roadmap a quantified evidence spine and separates oxygen route maturity from metal-feedstock maturity. |
| §TRL Roadmap | Table row for “ISRU substitution” | Add row: “Partial ISRU substitution into RHEA PM feedstock: TRL 2–3 in open literature. Required TRL-raising experiment: produce an ISRU-analogue or simulant-derived metal lot, refine it to the incoming-powder specification, blend at a stated substitution fraction with Earth powder, mechanically alloy, consolidate to the manuscript density criterion, and compare phase constitution, impurity pickup, hardness, and tensile-screening response against the all-Earth control \cite{Schild2025HighlandProducts,Maes2024FluorideSalt,Tong2018MoNbTaWPowders,Qiao2020TiZrNbTaPCA}.” | This directly addresses the central claim and defines the missing experiment. |
| Table 8 / manufacturing-readiness table | Existing equipment-readiness row, if present | Add: “COTS terrestrial envelope exists for HP/SPS, MA, LPBF, and <1 ppm glovebox handling; flight-qualified lunar equipment is not demonstrated. Representative COTS values: Retsch PM400 ≈290 kg and ≈2.2 kW; EOS M290 ≈1250 kg with 250 × 250 × 325 mm build volume and up to 8.5 kW maximum machine power; FCT/IFW SPS class 60–100 kW heating but open mass not reported \cite{Retsch2026PM400,EOS2026M290,EOS2026M2901kW,FCT2014SPSBrochure,IFW2026FCTHHPD25}.” | Gives the table concrete but traceable equipment values; flags unknowns rather than inventing lunar plant mass. |
| Manufacturing roadmap figure caption | Any arrow showing ISRU stream directly entering MA/HP/SPS | Add caption sentence: “The ISRU-to-PM arrow is conditional: it is gated by refining and incoming-powder equivalence tests. Until a substituted lot passes PSD/chemistry/phase/flowability and post-consolidation equivalence checks, the ISRU stream is a candidate precursor rather than released RHEA feedstock.” | Visual correction: the process should show a gate, not an unconditional substitution arrow. |
| §5.2–§5.3, or wherever the paper discusses QC | “XRD checkpoints; HV2 + Brinell + mini-tensile screening” | Extend with: “For substitution studies, mechanical screening should be paired with chemical and microstructural equivalence: LECO/inert-gas fusion O/N/H/C/S, ICP-OES/MS impurities, SEM-EDS homogeneity, retained powder witnesses, XRD after MA and after consolidation, density by Archimedes/helium pycnometry as appropriate, and fracture/segregation inspection after mini-tensile testing.” | HV/Brinell/tensile screening is insufficient to diagnose feedstock impurity and phase drift. |
| §5.2–§5.3 / risk register | No explicit counter-example to substitution | Add risk item: “Molten-salt and regolith-derived products can be chemically heterogeneous. FFC metal-product characterisation on highland simulants shows heterogeneous multiphase products and unresolved refining-to-specific-alloy issues; regolith/Ti alloy graded-material studies show oxide/interface reactions and Si-rich segregation risks \cite{Schild2025HighlandProducts,Popovich2020FGMReport,Laot2021RegolithFGM}.” | A credible manuscript should surface the strongest objection and show how the QC gate addresses it. |
| §Validation lane / hot-fire sequence | “sub-scale hot-fire combustor” | Add: “The hot-fire article should be a replaceable chamber-liner or couponed sub-scale chamber, not the first integrated flightlike chamber. Recommended sequence: inert oxidation/erosion coupon → low-pressure ignition and cooling-channel article → P8-class ≥150 bar sub-scale liner → post-test CT/metallography/chemistry against unexposed witness material.” | Creates a realistic test escalation path and protects the alloy claim from a single high-risk all-up test. |
| §Manufacturing Pipeline / alternative pipeline | No alternative use for mixed ISRU metals | Consider adding: “Mixed ISRU Fe–Si or Al/Si/Ca-bearing products may be better assigned initially to non-critical fixtures, shielding, balance masses, tooling trials, or sacrificial test articles, while refractory RHEA chamber-liner feedstock remains Earth-supplied until purified ISRU elemental or master-alloy streams are demonstrated \cite{Schluter2020OxygenReview,Schild2025HighlandProducts,Schreiner2016MREModel}.” | This gives the paper a credible fallback pipeline if RHEA feedstock substitution remains immature. |

## §7. New BibTeX entries

```bibtex
@article{Sargeant2020IlmeniteHydrogen,
  author  = {Sargeant, Hannah M. and Barber, Sarah J. and Anand, Mahesh and Abernethy, Freya A. J. and Sheridan, Sarah and Wright, Ian P. and Gavilan, Lissette and Morse, Andrew D. and Franchi, Ian A. and Verchovsky, Alexander B. and others},
  title   = {Hydrogen reduction of ilmenite: Towards an in situ resource utilization demonstration on the surface of the Moon},
  journal = {Planetary and Space Science},
  volume  = {180},
  pages   = {104751},
  year    = {2020},
  doi     = {10.1016/j.pss.2019.104751}
}

@article{Chambers1995IlmeniteOxygen,
  author  = {Chambers, J. G. and Taylor, L. A. and Patchen, A. D. and McKay, D. S.},
  title   = {Quantitative mineralogical characterization of lunar high-Ti mare basalts and soils for oxygen production},
  journal = {Journal of Geophysical Research: Planets},
  volume  = {100},
  number  = {E7},
  pages   = {14391--14401},
  year    = {1995},
  doi     = {10.1029/95JE00503}
}

@article{Lemelin2013IlmeniteMapping,
  author  = {Lemelin, Myriam and Lucey, Paul G. and Song, Eugenie and Taylor, G. Jeffrey},
  title   = {Ilmenite mapping of the lunar regolith over Mare Australe and Mare Ingenii regions: Implications for lunar resource exploration},
  journal = {Journal of Geophysical Research: Planets},
  volume  = {118},
  number  = {9},
  pages   = {1772--1783},
  year    = {2013},
  doi     = {10.1002/2013JE004392}
}

@article{Leger2025EnergyIlmenite,
  author  = {Leger, Dorian and Ghaffari-Tabrizi, Fardin and Shaw, Matthew and Rasera, Joshua and Dickson, David and Valentin, Baptiste and Morlock, Anton and Thoresen, Freja and Cilliers, Jan J. and Hadler, Kathryn and Cowley, Aidan},
  title   = {Modeling energy requirements for oxygen production on the Moon},
  journal = {Proceedings of the National Academy of Sciences of the United States of America},
  volume  = {122},
  number  = {8},
  pages   = {e2306146122},
  year    = {2025},
  doi     = {10.1073/pnas.2306146122}
}

@inproceedings{Sibille2010MRE,
  author    = {Sibille, Laurent and Sadoway, Donald R. and Sirk, A. H. and Tripathy, P. K.},
  title     = {Performance Testing of Molten Regolith Electrolysis with Transfer of Molten Material for the Production of Oxygen and Metals on the Moon},
  booktitle = {48th AIAA Aerospace Sciences Meeting Including the New Horizons Forum and Aerospace Exposition},
  address   = {Orlando, Florida},
  year      = {2010},
  url       = {https://ntrs.nasa.gov/citations/20100012946},
  urldate   = {2026-05-10}
}

@article{Schreiner2016MREModel,
  author  = {Schreiner, Samuel S. and Sibille, Laurent and Dominguez, Jesus A. and Hoffman, Jeffrey A.},
  title   = {A parametric sizing model for Molten Regolith Electrolysis reactors to produce oxygen on the Moon},
  journal = {Advances in Space Research},
  volume  = {57},
  number  = {7},
  pages   = {1585--1603},
  year    = {2016},
  doi     = {10.1016/j.asr.2016.01.006}
}

@article{Schluter2020OxygenReview,
  author  = {Schl{\"u}ter, Lukas and Cowley, Aidan},
  title   = {Review of techniques for In-Situ oxygen extraction on the Moon},
  journal = {Planetary and Space Science},
  volume  = {181},
  pages   = {104753},
  year    = {2020},
  doi     = {10.1016/j.pss.2019.104753}
}

@article{Lomax2020FFC,
  author  = {Lomax, Bethany A. and Conti, Melchiorre and Khan, Nadia and Bennett, Neil S. and Ganin, Aleksey Y. and Symes, Mark D.},
  title   = {Proving the viability of an electrochemical process for the simultaneous extraction of oxygen and production of metal alloys from lunar regolith},
  journal = {Planetary and Space Science},
  volume  = {180},
  pages   = {104748},
  year    = {2020},
  doi     = {10.1016/j.pss.2019.104748}
}

@article{Schwandt2012FFCLunar,
  author  = {Schwandt, Carsten and Hamilton, James A. and Fray, Derek J. and Crawford, Ian A.},
  title   = {The production of oxygen and metal from lunar regolith},
  journal = {Planetary and Space Science},
  volume  = {74},
  number  = {1},
  pages   = {49--56},
  year    = {2012},
  doi     = {10.1016/j.pss.2012.06.011}
}

@article{Lomax2025Endpoint,
  author  = {Lomax, Bethany A. and others},
  title   = {Identifying an efficient endpoint for oxygen extraction from lunar regolith by FFC molten salt electrolysis},
  journal = {Acta Astronautica},
  year    = {2025},
  doi     = {10.1016/j.actaastro.2025.04.049}
}

@article{Schild2025HighlandProducts,
  author  = {Schild, Timon and Lomax, Bethany A. and Conti, Melchiorre and Aridon, Gwena{\"e}lle and Harries, Dennis and Hadler, Kathryn},
  title   = {Characterization of metal products from the molten salt electrolysis of lunar highland regolith simulants},
  journal = {Acta Astronautica},
  volume  = {232},
  pages   = {1--13},
  year    = {2025},
  doi     = {10.1016/j.actaastro.2025.02.021}
}

@article{Maes2024FluorideSalt,
  author  = {Maes, M. and Gibilaro, M. and Chamelot, P. and Chiron, C. and others},
  title   = {Lunar simulant behaviour in molten fluoride salt for ISRU applications},
  journal = {Planetary and Space Science},
  volume  = {242},
  pages   = {105854},
  year    = {2024},
  doi     = {10.1016/j.pss.2024.105854}
}

@article{Sanders2011ISRUFieldAnalogs,
  author  = {Sanders, Gerald B. and Larson, William E.},
  title   = {Integration of in-situ resource utilization into lunar/Mars exploration through field analogs},
  journal = {Advances in Space Research},
  volume  = {47},
  number  = {1},
  pages   = {20--33},
  year    = {2011},
  doi     = {10.1016/j.asr.2010.08.020}
}

@misc{FCT2014SPSBrochure,
  author  = {{FCT Systeme GmbH}},
  title   = {Our Products: High Temperature Vacuum Furnaces and Spark Plasma Sintering Systems},
  year    = {2014},
  url     = {https://www.hasmak.com.tr/yeni/FCT-Imagebrosch%C3%BCre%20EN%20Products.pdf},
  urldate = {2026-05-10}
}

@misc{IFW2026FCTHHPD25,
  author  = {{Leibniz Institute for Solid State and Materials Research Dresden}},
  title   = {Spark Plasma Sintering: FCT Sintering Plant KCE-FCT H-HP D25-5D/FL},
  year    = {2026},
  url     = {https://www.ifw-dresden.de/ifw-products/services/spark-plasma-sintering},
  urldate = {2026-05-10}
}

@misc{MTI2026SPST20,
  author  = {{MTI Korea}},
  title   = {Spark Plasma Sintering Furnace (SPS) up to 50 MPa Pressure and 1600 {\textdegree}C},
  year    = {2026},
  url     = {https://mtikorea.co.kr/product/spark-plasma-sintering-furnace-sps-upto-50-mpa-pressure-and-1600%C2%BAc-ylj/6177/},
  urldate = {2026-05-10}
}

@misc{Retsch2026PM400,
  author  = {{Retsch GmbH}},
  title   = {Planetary Ball Mill PM 400: Product Data Sheet},
  year    = {2026},
  url     = {https://www.retsch.com/products/milling/ball-mills/planetary-ball-mill-pm-400/},
  urldate = {2026-05-10}
}

@misc{Fritsch2026Pulverisette7,
  author  = {{FRITSCH GmbH}},
  title   = {Planetary Mill PULVERISETTE 7 premium line: Technical Details},
  year    = {2026},
  url     = {https://www.fritsch-international.com/sample-preparation/milling/planetary-mills/details/product/pulverisette-7-premium-line/technical-details/},
  urldate = {2026-05-10}
}

@article{Suryanarayana2001Mechanical,
  author  = {Suryanarayana, C.},
  title   = {Mechanical alloying and milling},
  journal = {Progress in Materials Science},
  volume  = {46},
  number  = {1--2},
  pages   = {1--184},
  year    = {2001},
  doi     = {10.1016/S0079-6425(99)00010-9}
}

@article{Vaidya2019HEAMechanicalAlloying,
  author  = {Vaidya, Mayur and Muralikrishna, Garlapati Mohan and Murty, Budaraju Srinivasa},
  title   = {High-entropy alloys by mechanical alloying: A review},
  journal = {Journal of Materials Research},
  volume  = {34},
  number  = {5},
  pages   = {664--686},
  year    = {2019},
  doi     = {10.1557/jmr.2019.37}
}

@article{Tong2018MoNbTaWPowders,
  author  = {Tong, Yonggang and Qi, Peibu and Liang, Xiubing and Chen, Yongxiong and Hu, Yongle and Hu, Zhenfeng},
  title   = {Different-Shaped Ultrafine MoNbTaW High-Entropy Alloy Powders Prepared via Mechanical Alloying},
  journal = {Materials},
  volume  = {11},
  number  = {7},
  pages   = {1250},
  year    = {2018},
  doi     = {10.3390/ma11071250}
}

@article{Qiao2020TiZrNbTaPCA,
  author  = {Qiao, Yating and Tang, Yu and Li, Shun and Ye, Yicong and Liu, Xiyue and Zhu, Li'an and Bai, Shuxin},
  title   = {Preparation of TiZrNbTa refractory high-entropy alloy powder by mechanical alloying with liquid process control agents},
  journal = {Intermetallics},
  volume  = {126},
  pages   = {106900},
  year    = {2020},
  doi     = {10.1016/j.intermet.2020.106900}
}

@article{RuizEsparza2021PCA,
  author  = {Ruiz-Esparza-Rodr{\'i}guez, M. A. and Garay-Reyes, C. G. and Estrada-Guel, I. and Hern{\'a}ndez-Rivera, J. L. and Cruz-Rivera, J. J. and Guti{\'e}rrez-Casta{\~n}eda, E. and G{\'o}mez-Esparza, C. D. and Mart{\'i}nez-S{\'a}nchez, R.},
  title   = {Influence of process control agent and Al concentration on synthesis and phase stability of a mechanically alloyed AlxCoCrFeMnNi high-entropy alloy},
  journal = {Journal of Alloys and Compounds},
  volume  = {882},
  pages   = {160770},
  year    = {2021},
  doi     = {10.1016/j.jallcom.2021.160770}
}

@article{Moravcik2020Contamination,
  author  = {Moravcik, Igor and Kubicek, Antonin and Moravcikova-Gouvea, Larissa and Adam, Ondrej and Kana, Vaclav and Pouchly, Vaclav and Zadera, Antonin and Dlouhy, Ivo},
  title   = {The Origins of High-Entropy Alloy Contamination Induced by Mechanical Alloying and Sintering},
  journal = {Metals},
  volume  = {10},
  number  = {9},
  pages   = {1186},
  year    = {2020},
  doi     = {10.3390/met10091186}
}

@misc{EOS2026M290,
  author  = {{EOS GmbH}},
  title   = {EOS M 290 Metal 3D Printer Technical Data},
  year    = {2026},
  url     = {https://www.eos.info/metal-solutions/metal-printers/eos-m-290},
  urldate = {2026-05-10}
}

@misc{EOS2026M2901kW,
  author  = {{EOS GmbH}},
  title   = {EOS M 290 1kW Metal 3D Printer Technical Data},
  year    = {2026},
  url     = {https://www.eos.info/metal-solutions/metal-printers/eos-m-290-1kw},
  urldate = {2026-05-10}
}

@misc{NikonSLM2024SLM280,
  author  = {{Nikon SLM Solutions}},
  title   = {SLM 280 System Brochure},
  year    = {2024},
  url     = {https://nikon-slm-solutions.com/wp-content/uploads/2024/04/Nikon-SLM-System-Brochure-SLM280-PS.pdf},
  urldate = {2026-05-10}
}

@misc{DMGMori2026Lasertec65DED,
  author  = {{DMG MORI}},
  title   = {LASERTEC 65 DED hybrid 2nd Generation},
  year    = {2026},
  url     = {https://en.dmgmori.com/products/machines/additive-manufacturing/powder-nozzle/lasertec-65-ded-hybrid-2nd},
  urldate = {2026-05-10}
}

@article{Rebesan2021MolybdenumLPBF,
  author  = {Rebesan, P. and Ballan, M. and Bonesso, M. and Campagnolo, A. and Corradetti, S. and Dima, R. and Gennari, C. and Longo, G. A. and Mancin, S. and Manzolaro, M. and Meneghetti, G. and Pepato, A. and Visconti, E. and Vedani, M.},
  title   = {Pure molybdenum manufactured by Laser Powder Bed Fusion: Thermal and mechanical characterization at room and high temperature},
  journal = {Additive Manufacturing},
  volume  = {47},
  pages   = {102277},
  year    = {2021},
  doi     = {10.1016/j.addma.2021.102277}
}

@article{Gu2022VNbMoTaWLPBF,
  author  = {Gu, Pengfei and Qi, Tengbo and Chen, Lan and Ge, Tong and Ren, Xudong},
  title   = {Manufacturing and analysis of VNbMoTaW refractory high-entropy alloy fabricated by selective laser melting},
  journal = {International Journal of Refractory Metals and Hard Materials},
  volume  = {105},
  pages   = {105834},
  year    = {2022},
  doi     = {10.1016/j.ijrmhm.2022.105834}
}

@article{Mooraj2024TiZrNbTaLPBF,
  author  = {Mooraj, Shahryar and Kim, George and Fan, Xuesong and Samuha, Shmuel and Xie, Yujun and Li, Tianyi and Tiley, Jaimie S. and Chen, Yan and Yu, Dunji and An, Ke and Hosemann, Peter and Liaw, Peter K. and Chen, Wei and Chen, Wen},
  title   = {Additive manufacturing of defect-free TiZrNbTa refractory high-entropy alloy with enhanced elastic isotropy via in-situ alloying of elemental powders},
  journal = {Communications Materials},
  volume  = {5},
  pages   = {14},
  year    = {2024},
  doi     = {10.1038/s43246-024-00452-0}
}

@article{Dobbelstein2019TiZrNbTaLMD,
  author  = {Dobbelstein, Henrik and Gurevich, Evgeny L. and George, Easo P. and Ostendorf, Andreas and Laplanche, Guillaume},
  title   = {Laser metal deposition of compositionally graded TiZrNbTa refractory high-entropy alloys using elemental powder blends},
  journal = {Additive Manufacturing},
  volume  = {25},
  pages   = {252--262},
  year    = {2019},
  doi     = {10.1016/j.addma.2018.10.042}
}

@article{Li2019WxNbMoTaCladding,
  author  = {Li, Qingyu and Zhang, Hang and Li, Dichen and Chen, Zihao and Huang, Shuo and Lu, Zhilin and Yan, Hui},
  title   = {WxNbMoTa Refractory High-Entropy Alloys Fabricated by Laser Cladding Deposition},
  journal = {Materials},
  volume  = {12},
  number  = {3},
  pages   = {533},
  year    = {2019},
  doi     = {10.3390/ma12030533}
}

@misc{MBraun2026LABmasterPro,
  author  = {{M. Braun Inertgas-Systeme GmbH}},
  title   = {LABmaster Pro Glovebox Workstation},
  year    = {2026},
  url     = {https://www.mbraun.com/en/products/glovebox-workstations/articles/labmasterpro.html},
  urldate = {2026-05-10}
}

@misc{VAC2026OmniLab,
  author  = {{Vacuum Atmospheres Company}},
  title   = {OMNI-LAB Glove Box},
  year    = {2026},
  url     = {https://vacatm.com/omni-lab-glove-box},
  urldate = {2026-05-10}
}

@misc{MTI2026Glovebox,
  author  = {{MTI Corporation}},
  title   = {Five Chambers Glove Box with Gas Purification System H2O and O2 <1ppm},
  year    = {2026},
  url     = {https://mtixtl.com/products/five-chambers-glove-box-with-gas-purification-system-h2o-o2-1ppm-vgb-6-v-ld},
  urldate = {2026-05-10}
}

@misc{DLR2026P8,
  author  = {{Deutsches Zentrum f{\"u}r Luft- und Raumfahrt}},
  title   = {Research and Technology Test Bench P8},
  year    = {2026},
  url     = {https://www.dlr.de/en/ra/research-transfer/research-and-test-infrastructure/test-benches-for-space-propulsion/research-and-technology-test-bench-p8-1},
  urldate = {2026-05-10}
}

@misc{DLR2023M3Factsheet,
  author  = {{Deutsches Zentrum f{\"u}r Luft- und Raumfahrt}},
  title   = {Technical Center M3: DLR site Lampoldshausen},
  year    = {2023},
  url     = {https://www.dlr.de/en/ra/multimedia/publications/fact-sheets/factsheet_technikum-m3_en.pdf/@@download/file/Factsheet_Technikum%20M3_EN.pdf},
  urldate = {2026-05-10}
}

@article{Greuel2013SCORED,
  author  = {Greuel, Dirk and Deeken, Jan C. and Suslov, Dmitry and Sch{\"a}fer, Klaus and Schlechtriem, Stefan},
  title   = {Test facilities for SCORE-D},
  journal = {CEAS Space Journal},
  volume  = {4},
  pages   = {55--69},
  year    = {2013},
  doi     = {10.1007/s12567-013-0033-x}
}

@misc{NASA2021MSFCPTL,
  author  = {{National Aeronautics and Space Administration}},
  title   = {Marshall Space Flight Center Propulsion Test Laboratory},
  year    = {2021},
  url     = {https://www.nasa.gov/wp-content/uploads/2016/01/et10_ptl_3_1_21.pdf},
  urldate = {2026-05-10}
}

@misc{NASA2023TF116,
  author  = {{National Aeronautics and Space Administration}},
  title   = {MSFC Test Facility 116},
  year    = {2023},
  url     = {https://www.nasa.gov/directorates/space-operations/rpt/msfc-test-facility-116/},
  urldate = {2026-05-10}
}

@inproceedings{Iannetti2017Prometheus,
  author    = {Iannetti, Alessandra and Girard, Nathalie and Ravier, Nicolas and Edeline, Emmanuel and Tchou-Kien, Denis},
  title     = {Prometheus, a low cost LOX/CH4 engine prototype},
  booktitle = {53rd AIAA/SAE/ASEE Joint Propulsion Conference},
  year      = {2017},
  doi       = {10.2514/6.2017-4750}
}

@inproceedings{Asakawa2016LOXLNG,
  author    = {Asakawa, Hiroya and Nanri, Hideaki and Masuda, Hideo and Shinohara, R. and Ishikawa, Yasuhiro and Sakaguchi, Hiroyuki},
  title     = {Study on Combustion Characteristics of LOX/LNG (methane) Co-axial Type Injector under High Pressure Condition},
  booktitle = {52nd AIAA/SAE/ASEE Joint Propulsion Conference},
  year      = {2016},
  doi       = {10.2514/6.2016-5078}
}

@inproceedings{Sakaki2023JAXAIHI,
  author    = {Sakaki, Kazuki and Hashizume, Tatsuya and Morito, Toshiki and Nanri, Hideaki and Ishihara, Shinji and Ishikawa, Yasuhiro},
  title     = {Results of Hot-fire Testing of 30kN LOX/Methane Full-expander Cycle Engine},
  booktitle = {Aerospace Europe Conference 2023 -- 10th EUCASS -- 9th CEAS},
  year      = {2023},
  doi       = {10.13009/EUCASS2023-536}
}

@techreport{Popovich2020FGMReport,
  author      = {Popovich, Vera and Laot, Mathilde and others},
  title       = {Additive Manufacturing of Functionally Graded Materials from Lunar Regolith},
  institution = {European Space Agency, Advanced Concepts Team},
  number      = {ACT-RPT-HAB-ARI-19-9401},
  year        = {2020},
  url         = {https://www.esa.int/gsp/ACT/doc/ARI/ARI%20Study%20Report/ACT-RPT-HAB-ARI-19-9401.pdf},
  urldate     = {2026-05-10}
}

@article{Laot2021RegolithFGM,
  author  = {Laot, Mathilde and Rich, Belinda and Cheibas, Ina and Fu, Jia and Zhu, Jia-Ning and Popovich, Vera A.},
  title   = {Additive Manufacturing and Spark Plasma Sintering of Lunar Regolith for Functionally Graded Materials},
  journal = {SPOOL},
  volume  = {8},
  number  = {2},
  pages   = {7--30},
  year    = {2021},
  doi     = {10.7480/spool.2021.2.5258}
}
```
