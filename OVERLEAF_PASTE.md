# Overleaf paste sheet — every change to apply to the paper

Everything you need to add to the WAMS 2026 manuscript on Overleaf, in
copy-paste-ready form. Organized by location in `main.tex`. Code blocks
contain the exact LaTeX text — paste verbatim.

---

## Files to upload to Overleaf

| File on local disk | Upload to (in Overleaf) |
|---|---|
| `figures/dilution_phase_diagram_v2.pdf` | `figures/dilution_phase_diagram_v2.pdf` |

That's the only new figure. Pugh G/B is reported as inline numbers in §5.2,
no figure needed.

---

## A. (No typo fixes needed)

I previously listed two "typo fixes" at lines 278 and 1020. After you sent
me your live Overleaf version, I confirmed those are **not bugs in your
file** — your version reads `2$^\circ$\times 2$^\circ$` and
`Anomalous $T \uparrow$`, both of which compile fine. Skip this section.

---

## B. Eight new content insertions in `main.tex`

### B.1 — End of §1 (Introduction)

**Where**: paste *after* the closing `\end{keyhighlight}` of the key-highlight
box at the end of §1, and *before* the `% ============` separator that
precedes `\section{Scope, Claim Boundary, and Evidence Classes}`.

```latex
\paragraph{European programme context.}
The framework presented here is complementary to several active European lunar-manufacturing programmes. The DLR/ESA LUNA analogue facility (Cologne, opened September 2024) provides the regolith-simulant testbed at the scale required for integrated ISRU experiments. The ESA OSIP-funded \emph{Deep Sintering of Lunar Regolith Simulants} project (Activity~4000147699, TU~Berlin, implemented March 2025) demonstrates subsurface viscous sintering at 700--950$^\circ$C on both Mare and Highland simulants, directly relevant to the paper's terrane-resolved framework~\cite{ESADeepSintering2025}. The MOONRISE flight payload (LZH and TU~Berlin, DLR/BMWK funded, scheduled for an Astrobotic CLPS landing in late 2026) will demonstrate diode-laser melting of regolith on the lunar surface~\cite{MOONRISE2024}. On the metallic ISRU side, the Metalysis FFC-Cambridge process (UK SME with ESA development contract; ESA Grand Challenge Phase~1 winner) is the European Al--Si producer reduced from regolith~\cite{Lomax2020}; the Al--Si-blended alloy concept proposed below is directly compatible with that feedstock. Hot-section validation is anchored in the DLR P8 bench at Lampoldshausen, where ArianeGroup has already qualified a fully additively manufactured combustion chamber over 14 hot fires; the Stage-2 RHEA throat-inlay test of Section~\ref{sec:roadmap} is positioned within that established infrastructure.
```

### B.2 — §4.5 (Published process baselines for candidate alloy families)

**Where**: paste *immediately after* the COST507-caveat sentence ending
"...provides the primary evidence for BCC phase stability." (in the same
paragraph that references Figure~\ref{fig:rhea_stability}).

```latex
\paragraph{Ab-initio cross-check.}
To complement the COST507 treatment, which lacks binary interaction parameters for most refractory pairs, we recompute the $T = 0$\,K phase competition for all three reference compositions of Figure~\ref{fig:rhea_stability} using the \texttt{mace-mh-1} foundation interatomic potential~\cite{Batatia2025MACEMH1,Batatia2022MACE}, OMAT/PBE head, on 100-atom random-substitution supercells in BCC, FCC, and HCP. Formation enthalpies relative to the pure-element ground states (Fe BCC, Al FCC, Ti/Zr/Hf HCP, Mo/Nb/Ta/V BCC) are $\Delta H_f^{\text{BCC}}(\text{HfNbTaTiZr}) = +94$~meV/atom, $\Delta H_f^{\text{BCC}}(\text{MoNbTaTiV}) = -1$~meV/atom, and $\Delta H_f^{\text{BCC}}(\text{Fe}_{0.3}\text{Ti}_{0.3}\text{Al}_{0.2}\text{Nb}_{0.1}\text{Ta}_{0.1}) = -117$~meV/atom; in all three cases BCC is preferred over FCC and HCP by 21--48~meV/atom. This is an independent ab-initio confirmation of the BCC stability claim established by SPARK XRD evidence and the published Senkov / Cao literature~\cite{Senkov2011,Cao2019}, and the result for the ISRU blend ($-117$~meV/atom) is the first quantitative indication that the proposed blend is strongly exothermic to form, not merely metastable.
```

### B.3 — End of §5.2 (What SPARK provides: calibrated process knowledge)

**Where**: paste *immediately before* `\subsection{The bridge: blending ISRU
bulk metals with Earth-shipped refractories}`.

```latex
\paragraph{Pugh's G/B as a single-descriptor printability surrogate.}
The recently published JOM 2025 RHEA additive-manufacturability index of Oriola \emph{et al.}~\cite{Oriola2025AMI,Oriola2025LaserGlazing} establishes Pugh's $G/B$ ratio~\cite{Pugh1954} as the strongest single empirical predictor of laser-powder-bed-fusion cracking susceptibility in refractory HEAs (Pearson $r = -0.90$ against cumulative crack length on a four-alloy validation set, with $G/B$ values clustered at 0.402--0.404). Using \texttt{mace-mh-1}-derived elastic constants for all five published baselines of Table~\ref{tab:sps_baselines} plus the BCC compositions along the dilution path, we compute Voigt--Reuss--Hill polycrystalline $G/B$ values: 0.273 (HfNbTaTiZr), 0.259 (MoNbTaTiV), 0.325 (MoNbTaVW), 0.339 (AlMo$_{0.5}$NbTa$_{0.5}$TiZr), 0.364 (MoNbTaW), with Fe$_2$Nb (0.44) and Fe$_2$Ta (0.50) as Laves end-members. All published BCC baselines and dilution-path compositions sit below the Pugh ductile/brittle threshold of 0.57, in the predicted ductile regime; MoNbTaW (the 0\%-ISRU baseline) has the highest $G/B$ of the pure-refractory family and is therefore predicted to be the most cracking-prone of that family by the JOM 2025 correlation. AlMo$_{0.5}$NbTa$_{0.5}$TiZr, the 19\%-ISRU literature headline, gives $G/B = 0.339$ --- comparable to the JOM cohort, predicted ductile-printable. Full evaluation of the JOM 2025 index requires the freezing-range and Kou-CSI components, which depend on a TCHEA-grade thermodynamic database and remain future work.
```

### B.4 — End of §5.3 (The bridge: blending ISRU bulk metals with Earth-shipped refractories)

**Where**: paste *immediately before* `\subsection{Broader implications}`.

```latex
\paragraph{Solute dissolution refines the blending narrative.}
Single-substitution dilute-solute calculations with \texttt{mace-mh-1} into the relaxed BCC matrices of HfNbTaTiZr and MoNbTaTiV show that, at infinite dilution, Fe and Ti are both \emph{energetically uphill} solutes in the pure refractory matrices ($E_{\text{sub}}(\text{Fe}) = +0.19$~eV in HfNbTaTiZr; $+0.30$~eV in MoNbTaTiV; $E_{\text{sub}}(\text{Ti}) = +0.09$ and $+0.35$~eV respectively), with only Al favourable ($-0.72$~eV in HfNbTaTiZr; $-0.09$~eV in MoNbTaTiV). The simplest reading of the blending concept --- ``Fe-Ti from ISRU dissolves into a refractory matrix'' --- is therefore not supported by the dilute-solute thermodynamics. The favourable formation enthalpy of the ISRU blend Fe$_{0.3}$Ti$_{0.3}$Al$_{0.2}$Nb$_{0.1}$Ta$_{0.1}$ ($\Delta H_f = -117$~meV/atom) originates from bulk Fe-Ti-Al chemistry, in which the refractory elements act as solid-solution strengtheners of an ISRU-dominated matrix rather than as the matrix itself. This refinement is consistent with, and strengthens, the graded-architecture proposal above: pure RHEAs for hot sections, ISRU-dominated blends for medium-temperature service.
```

### B.5 — §6.6 (Metallurgical validation requirements paragraph)

**Where**: paste *immediately after* the `\end{enumerate}` that closes the
3-item list (Dilution trajectory modelling / Impurity tolerance assessment /
Process path definition), and *before* `\paragraph{Limitations.}`.

```latex
\paragraph{Tier-1 ab-initio first pass on dilution-trajectory modelling.}
As an open-source first pass on the TCHEA-grade dilution-trajectory mapping called for in Item~1 above, we have computed solid-state phase boundaries along the MoNbTaTiV~$\rightarrow$~Fe-50Ti dilution path using the \texttt{mace-mh-1} interatomic potential combined with harmonic phonopy phonons~\cite{Togo2015Phonopy} and a Bragg--Williams configurational-entropy model. With pure Fe$_2$Nb (C14) and Fe$_2$Ta (C14) treated as Laves competitors, the single-phase BCC field is bounded by an Fe$_2$Ta cliff at 22.6~wt\% ISRU and an Fe$_2$Nb cliff at 47.7~wt\% ISRU at 1\,000~K, with both cliffs shifting to higher ISRU fraction with temperature. The proposed dilution window (75--90~wt\% ISRU, Section~\ref{subsec:blending}) sits past both cliffs at every temperature studied, supporting the qualitative picture in Figure~\ref{fig:dilution_diagram}. Computed Laves heats of formation for Fe$_2$Nb ($-12.2$~kJ/mol$\cdot$atom) and Fe$_2$Ta ($-17.7$~kJ/mol$\cdot$atom) fall inside published experimental ranges, providing indirect validation of the foundation-MLIP energetics. This Tier-1 calculation does not replace the TCHEA assessment called for above: liquidus, solidus, and proper composition-balanced tie lines still require the assessed CALPHAD database. Figure~\ref{fig:dilution_diagram_v2} shows the ab-initio solid-state boundaries in the same visual layout as Figure~\ref{fig:dilution_diagram}.
```

### B.6 — New Figure 12 v2 (immediately after the existing Figure 12)

**Where**: paste *immediately after* the `\end{figure}` of the existing
Figure 12 (`\label{fig:dilution_diagram}`).

```latex
\begin{figure}[p]
\centering
\includegraphics[width=0.85\textwidth]{figures/dilution_phase_diagram_v2.pdf}
\caption{Ab-initio Tier-1 dilution diagram (this work), drawn in the same visual layout as Figure~\ref{fig:dilution_diagram} for direct A/B comparison. Solid-state phase boundaries (Fe$_2$Ta cliff in blue, Fe$_2$Nb cliff in red dotted) are computed from the \texttt{mace-mh-1} foundation interatomic potential~\cite{Batatia2025MACEMH1} combined with harmonic phonopy phonons~\cite{Togo2015Phonopy} on the MoNbTaTiV $\rightarrow$ Fe-50Ti dilution path, with pure C14 Laves references (Fe$_2$Nb, Fe$_2$Ta). The diagram is bounded at 1\,800~K above which the harmonic-phonon regime is no longer valid; full $T$--$x$ including liquidus / solidus requires TCHEA. The 75--90~wt\% ISRU target window (green band) is past the Fe$_2$Ta cliff at every temperature.}
\label{fig:dilution_diagram_v2}
\end{figure}
```

Also (optional but recommended): add a forward pointer at the end of the
existing Figure 12 caption. **Find** the closing of the existing caption:

```latex
... quantitative phase boundaries require TCHEA-grade CALPHAD calculations for specific RHEA$+$Fe--Ti pseudo-binaries.}
```

**Replace with:**

```latex
... quantitative phase boundaries require TCHEA-grade CALPHAD calculations for specific RHEA$+$Fe--Ti pseudo-binaries. See Figure~\ref{fig:dilution_diagram_v2} for an ab-initio Tier-1 version of the solid-state boundaries.}
```

### B.7 — Table 8 (Evidence Class) — add 4 new rows

**Where**: in the existing Table 8, paste *immediately before* the
`\bottomrule` line (after the existing row 20 about mini-tensile geometry).

```latex
21 & $T = 0$\,K phase competition for HfNbTaTiZr, MoNbTaTiV, and the ISRU blend prefers BCC by 21--48~meV/atom & D & \texttt{mace-mh-1} + 100-atom supercells (this work) \\
22 & Computed Fe$_2$Nb / Fe$_2$Ta C14 Laves $\Delta H_f$ within experimental ranges & D + M & this work + Kubaschewski / assessed CALPHAD \\
23 & Pugh's $G/B$ for all five Table-11 baselines (0.26--0.36); MoNbTaW the highest of pure refractories & D & \texttt{mace-mh-1} + Voigt--Reuss--Hill (this work); framework per Oriola \emph{et al.} 2025 \\
24 & Tier-1 ab-initio dilution diagram (Fig.~\ref{fig:dilution_diagram_v2}): Fe$_2$Ta cliff at 22.6~wt\% ISRU, Fe$_2$Nb cliff at 47.7~wt\% at 1\,000~K; target window past both cliffs & D & \texttt{mace-mh-1} + harmonic phonopy + Bragg--Williams (this work); full TCHEA still required \\
```

### B.8 — Author Contributions table — delete the placeholder row

**Where**: in the `\section*{Author Contributions (CRediT-style)}` table.

**Find and delete the entire line**:

```latex
\textit{[Add author]} & \textit{[Add contribution terms]} \\
```

The remaining table should have just two rows (Siddhartha Yash Kovid; Kevin
Grüning) plus `\bottomrule`.

---

## C. New BibTeX entries in `references.bib`

**Where**: paste at the end of `references.bib` (after the last existing
`@article{Gorsse2017, ...}` entry).

```bibtex
% =====================================================================
% Added 2026-05-06: ab-initio + JOM 2025 RHEA-AM index references
% =====================================================================

@article{Batatia2025MACEMH1,
  author  = {Batatia, Ilyes and Lin, Chen and Hart, Joseph and Kasoar, Elliott and Elena, Alin M.\ and Norwood, Sam Walton and Wolf, Thomas and Cs{\'a}nyi, G{\'a}bor},
  title   = {Cross Learning between Electronic Structure Theories for Unifying Molecular, Surface, and Inorganic Crystal Foundation Force Fields},
  journal = {arXiv preprint arXiv:2510.25380},
  year    = {2025}
}

@article{Batatia2022MACE,
  author  = {Batatia, Ilyes and Kov{\'a}cs, D{\'a}vid P{\'e}ter and Simm, Gregor and Ortner, Christoph and Cs{\'a}nyi, G{\'a}bor},
  title   = {{MACE}: Higher Order Equivariant Message Passing Neural Networks for Fast and Accurate Force Fields},
  journal = {Advances in Neural Information Processing Systems},
  volume  = {35},
  pages   = {11423--11436},
  year    = {2022}
}

@article{Oriola2025AMI,
  author  = {Oriola, A.\ T.\ and Maile, J.\ D.\ and Nguyen, A.\ and Payton, E.\ J.},
  title   = {Toward an Index for Predicting Additive Manufacturability of Refractory High-Entropy Alloys},
  journal = {JOM},
  volume  = {77},
  number  = {10},
  pages   = {7222--7234},
  year    = {2025},
  doi     = {10.1007/s11837-025-07552-3}
}

@article{Oriola2025LaserGlazing,
  author  = {Oriola, A.\ T.\ and Maile, J.\ D.\ and Nguyen, A.\ and Do, H.\ and Kumar, R.\ and Payton, E.\ J.},
  title   = {Screening of Refractory High-Entropy Alloy Solidification Behavior Through Laser Glazing},
  journal = {JOM},
  volume  = {77},
  number  = {10},
  pages   = {7247--7263},
  year    = {2025},
  doi     = {10.1007/s11837-025-07620-8}
}

@article{Kou2015,
  author  = {Kou, Sindo},
  title   = {A criterion for cracking during solidification},
  journal = {Acta Materialia},
  volume  = {88},
  pages   = {366--374},
  year    = {2015},
  doi     = {10.1016/j.actamat.2015.01.034}
}

@article{Pugh1954,
  author  = {Pugh, S.\ F.},
  title   = {Relations between the elastic moduli and the plastic properties of polycrystalline pure metals},
  journal = {The London, Edinburgh, and Dublin Philosophical Magazine and Journal of Science},
  volume  = {45},
  number  = {367},
  pages   = {823--843},
  year    = {1954},
  doi     = {10.1080/14786440808520496}
}

@article{Togo2015Phonopy,
  author  = {Togo, Atsushi and Tanaka, Isao},
  title   = {First principles phonon calculations in materials science},
  journal = {Scripta Materialia},
  volume  = {108},
  pages   = {1--5},
  year    = {2015},
  doi     = {10.1016/j.scriptamat.2015.07.021}
}

@misc{ESADeepSintering2025,
  author       = {{ESA Open Space Innovation Platform}},
  title        = {Deep Sintering of Lunar Regolith Simulants (Activity 4000147699)},
  howpublished = {ESA OSIP / Discovery and Preparation; implementation TU~Berlin, March 2025},
  year         = {2025},
  url          = {https://activities.esa.int/4000147699}
}

@misc{MOONRISE2024,
  author       = {{MOONRISE Consortium}},
  title        = {{MOONRISE}: Laser melting of regolith on the Moon},
  howpublished = {Laser Zentrum Hannover (LZH) and TU~Berlin; DLR / BMWK funded; flight on an Astrobotic CLPS lander},
  year         = {2024},
  url          = {https://www.lzh.de/en/moonrise}
}
```

---

## D. Summary of touch points

| File | What changes |
|---|---|
| `main.tex` | 2 typo fixes + 6 new paragraphs + 4 new Table 8 rows + 1 new figure block + delete placeholder row |
| `references.bib` | Append 9 new BibTeX entries |
| `figures/` | Upload 1 new file: `dilution_phase_diagram_v2.pdf` |

After pasting, recompile on Overleaf — the new `\cite{}` keys all resolve to
the bib entries above; the new `\ref{fig:dilution_diagram_v2}` resolves to
the new figure; no other cross-reference changes are needed.

---

*End of paste sheet. Paired with: `MACE_RESULTS_FOR_PAPER.md` (technical
report with caveats and audit), `MACE_RESULTS_REPORT.pdf` (companion PDF),
and the local compile at `/Users/siddharthakovid/Downloads/outputs/main.pdf`
(the 48-page paper with everything already integrated and compiled).*
