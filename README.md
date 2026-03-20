# Terrane-Aware Lunar Metallurgy: Analysis Pipeline

**Companion code and data for WAMS 2026 Paper #68:**

> *Refractory High-Entropy Alloys and Hybrid Additive Routes for Metallurgy in Lunar Mare, Highlands and KREEP Terranes*
>
> S. Y. Kovid and K. Gruning (Bimo Tech)

This repository contains the complete analysis pipeline, figure-generation scripts, and input data used to produce all quantitative results and figures in the paper.

---

## Repository Structure

```
wams2026-lunar-metallurgy/
├── notebooks/
│   └── wams2026_pipeline.ipynb        # Main pipeline: data → PCA → indices → maps
├── src/                               # Reusable Python modules
│   ├── preprocess.py                  # CLR transform, terrane classification, imputation
│   ├── pca_analysis.py                # PCA, bootstrap loadings, silhouette/DBI
│   ├── indices.py                     # I_FeTi, I_AlCa, I_KREEP computation
│   ├── compatibility.py               # Terrane → alloy/process mapping
│   ├── plotting.py                    # Publication figure styling
│   └── io_utils.py                    # File I/O helpers
├── scripts/                           # Standalone figure generators
│   ├── regenerate_figures.py          # Monte Carlo sensitivity + violin/heatmap/contour
│   ├── generate_dual_purpose_figures.py   # Dual-purpose mass break-even (2×2 panel)
│   └── generate_dilution_diagram.py   # RHEA → ISRU pseudo-binary phase diagram
├── phase_diagrams/                    # Thermochemical calculations
│   ├── generate_diagrams.py           # Binary phase diagrams (Fe-Ti, Al-Fe, Al-Ti, Al-Ni)
│   ├── generate_rhea.py              # RHEA phase stability (HfNbTaTiZr, MoNbTaTiV)
│   ├── generate_combined.py          # Combined 2×2 binary layout
│   ├── COST507.tdb                   # EU COST Action 507 thermochemical database
│   ├── nial_dupin.tdb                # Ni-Al binary (Dupin et al. 2001)
│   └── alfe_sei.tdb                  # Al-Fe binary database
├── data/
│   ├── lunar_geochem_2deg.csv         # LP-GRS 2° elemental abundances (11,306 pixels)
│   ├── lunar_geochem.csv              # Full-resolution LP-GRS dataset
│   └── DATA_SOURCES.md               # Data provenance and download instructions
├── figures/                           # Generated publication figures (PDF)
├── tables/                            # Generated CSV tables
└── requirements.txt                   # Python dependencies
```

## Data Sources

The primary dataset is the **Lunar Prospector Gamma Ray Spectrometer (LP-GRS)** 2-degree elemental abundance product:

- **Source:** NASA Planetary Data System (PDS) Geosciences Node
- **URL:** https://pds-geosciences.wustl.edu/missions/lunarp/
- **Reference:** Prettyman et al. (2006), *J. Geophys. Res.* 111, E12007
- **Resolution:** 2° x 2° equal-area pixels, 11,306 total
- **Variables:** FeO, TiO2, Al2O3, CaO, MgO, SiO2 (wt%); K, Th, U (ppm)

The thermochemical databases (`.tdb` files) are from the EU COST Action 507 project for light metal alloys and published binary assessments.

## Reproducing the Results

### Prerequisites

```bash
pip install -r requirements.txt
```

Key dependencies: `numpy`, `pandas`, `scikit-learn`, `matplotlib`, `scipy`, `pycalphad`, `tqdm`

### Step 1: Run the main pipeline

Open and execute `notebooks/wams2026_pipeline.ipynb`. This produces:
- PCA decomposition (Figures 1-2, Tables 2-3)
- Terrane classification (8,472 highlands / 1,222 mare / 1,612 KREEP)
- Metallurgical potential indices I_FeTi, I_AlCa, I_KREEP (Table 3)
- Selenographic resource maps (Figures 3-4)
- Cluster validation metrics (silhouette = 0.367, DBI = 1.138)

### Step 2: Monte Carlo sensitivity analysis

```bash
cd scripts
python regenerate_figures.py
```

Produces (10,000 weight perturbations, sigma = 0.20):
- `figures/monte_carlo_indices.pdf` — Violin plots of index distributions
- `figures/weight_sensitivity_heatmap.pdf` — Per-weight sensitivity heatmap
- `figures/breakeven_contours.pdf` — Break-even cost contours
- `tables/monte_carlo_summary.csv` — Percentile statistics
- `tables/ranking_stability.csv` — 100% ranking stability confirmed

### Step 3: Phase diagrams

```bash
cd phase_diagrams
python generate_diagrams.py      # Fe-Ti, Al-Ti, Al-Fe, Al-Ni binaries
python generate_rhea.py          # HfNbTaTiZr, MoNbTaTiV, ISRU-blend stability
python generate_combined.py      # Combined 2×2 layout
```

Uses pycalphad with the COST507 thermochemical database. Note: COST507 was designed for light Al-based alloys. Binary parameters for refractory pairs (Mo-Nb, Hf-Ta, etc.) are likely absent; calculations for refractory compositions should be treated as illustrative.

### Step 4: Economic analysis figures

```bash
cd scripts
python generate_dual_purpose_figures.py    # 2×2 break-even comparison
python generate_dilution_diagram.py        # RHEA → Fe-Ti pseudo-binary
```

## Figure Provenance

| Figure | Script | Key Input |
|--------|--------|-----------|
| Fig. 1 (PCA biplot) | `notebooks/wams2026_pipeline.ipynb` | `data/lunar_geochem_2deg.csv` |
| Fig. 2 (PCA loadings) | `notebooks/wams2026_pipeline.ipynb` | `data/lunar_geochem_2deg.csv` |
| Figs. 3-4 (Resource maps) | `notebooks/wams2026_pipeline.ipynb` | `data/lunar_geochem_2deg.csv` |
| Fig. 5 (Binary phase diagrams) | `phase_diagrams/generate_combined.py` | `phase_diagrams/COST507.tdb` |
| Fig. 6 (RHEA phase stability) | `phase_diagrams/generate_rhea.py` | `phase_diagrams/COST507.tdb` |
| Fig. 8 (MC violin plots) | `scripts/regenerate_figures.py` | Synthetic LP-GRS (seed=42) |
| Fig. 9 (Weight sensitivity) | `scripts/regenerate_figures.py` | Synthetic LP-GRS (seed=42) |
| Fig. 10 (Break-even contours) | `scripts/regenerate_figures.py` | Parametric model |
| Fig. 11 (Dilution diagram) | `scripts/generate_dilution_diagram.py` | Literature + COST507 |
| Fig. 12 (Dual-purpose break-even) | `scripts/generate_dual_purpose_figures.py` | Parametric model |

## Key Equations

The three metallurgical potential indices (Eqs. 2-4 in the paper):

```
I_FeTi  = 0.50·ĉ_FeO + 0.40·ĉ_TiO2 - 0.10·P_imp
I_AlCa  = 0.55·ĉ_Al2O3 + 0.35·ĉ_CaO - 0.10·P_het
I_KREEP = 0.40·ĉ_K + 0.40·ĉ_Th + 0.10·ĉ_U - 0.10·P_unc
```

where ĉ_x denotes min-max normalized concentrations over the full dataset.

## Citation

If you use this code or data, please cite:

```bibtex
@inproceedings{Kovid2026wams,
  author    = {Kovid, Siddhartha Yash and Gr{\"u}ning, Kevin},
  title     = {Refractory High-Entropy Alloys and Hybrid Additive Routes
               for Metallurgy in Lunar Mare, Highlands and KREEP Terranes},
  booktitle = {World Additive Manufacturing Summit (WAMS) 2026},
  year      = {2026},
  note      = {Paper \#68}
}
```

## License

MIT License. See [LICENSE](LICENSE) for details.

The LP-GRS dataset is in the public domain (NASA PDS). The COST507 database is distributed for academic use under the EU COST Action 507 project terms.
