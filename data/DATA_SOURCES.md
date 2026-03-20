# Data Sources for WAMS 2026 Paper #68

## Primary: LP-GRS Elemental Abundance (used in pipeline)

| Field | Value |
|-------|-------|
| **Dataset** | Lunar Prospector GRS Elemental Abundance V1.0 |
| **ID** | LP-L-GRS-5-ELEM-ABUNDANCE-V1.0 |
| **Producer** | T. H. Prettyman, Planetary Science Institute |
| **Reference** | Prettyman et al. (2006), *J. Geophys. Res.*, 111, E12007 |
| **Resolution** | 5-degree equal-area pixels (1,790 global pixels) |
| **Columns** | MgO, Al2O3, SiO2, CaO, TiO2, FeO (wt%), K, Th, U (ppm) + error matrix |
| **Altitude** | ~100 km (High Altitude 1 phase) |
| **Period** | 1998-01-17 to 1998-10-07 |
| **License** | NASA public domain |
| **Download** | https://pds-geosciences.wustl.edu/lunar/lp-l-grs-5-elem-abundance-v1/lp_9001/data/ |
| **PDS page** | https://pds-geosciences.wustl.edu/missions/lunarp/grs_elem_abundance.html |
| **PDS4** | https://arcnav.psi.edu/urn:nasa:pds:lp_grs_derived:data |

### Files at PDS
- `lpgrs_high1_elem_abundance_2deg.tab` (9.9 MB, 2-degree resolution)
- `lpgrs_high1_elem_abundance_5deg.tab` (1.5 MB, 5-degree resolution) **<-- used**
- `lpgrs_high1_elem_abundance_20deg.tab` (100 KB, 20-degree resolution)

### Terrane classification
Applied per Jolliff (2000) framework:
- **KREEP/PKT**: Th > 3.5 ppm (Procellarum KREEP Terrane)
- **Mare**: FeO > 8.0 wt% AND TiO2 > 0.5 wt% (basaltic signature)
- **Highlands**: everything else (anorthositic, high Al2O3)

---

## Alternative / Complementary Sources (not yet integrated)

### Chang'e-5 deep-learning oxide maps (high resolution)
- **Paper**: "Comprehensive mapping of lunar surface chemistry by adding Chang'e-5 samples with deep learning"
- **Journal**: Nature Communications (2023)
- **DOI**: https://doi.org/10.1038/s41467-023-43358-0
- **Data**: https://doi.org/10.6084/m9.figshare.24081438 and https://doi.org/10.6084/m9.figshare.24460114
- **Format**: TIF rasters, high spatial resolution
- **Advantage**: Much finer resolution than LP-GRS; calibrated with Chang'e-5 returned samples
- **Note**: Would need rasterio/GDAL to ingest; could replace LP-GRS for higher-res maps

### Chang'e-6 refined maps (2025)
- **Paper**: "Global chemical composition maps of oxide distributions on the Lunar surface"
- **Journal**: Communications Earth & Environment (2025)
- **DOI**: https://doi.org/10.1038/s43247-025-02914-w
- **Advantage**: Latest calibration including farside ground truth from Chang'e-6

### Clementine UVVIS FeO map (1 km resolution)
- **Source**: USGS Astropedia
- **URL**: https://astrogeology.usgs.gov/search/map/moon_clementine_uvvis_feo_color_binned_1km
- **Download**: https://planetarymaps.usgs.gov/mosaic/Lunar_Clementine_UVVIS_FeO_ClrBinned_70S70N_1km.tif
- **Format**: GeoTIFF, 133 MB, 8-bit 3-band, 1 km/pixel
- **Coverage**: 70S to 70N latitude
- **Reference**: Lucey et al. (2000), *J. Geophys. Res.*, 105(E8), 20297-20305
- **Note**: FeO only (not full oxide suite); needs GDAL to read

### Kaguya (SELENE) GRS
- **Source**: JAXA SELENE Data Archive
- **URL**: https://www.soac.selene.isas.jaxa.jp/archive/index.html.en
- **Advantage**: Independent GRS measurements, different orbit geometry

### Lunar ODE (Orbital Data Explorer)
- **URL**: https://ode.rsl.wustl.edu/moon/
- **Use**: Search/browse/download all PDS lunar mission data in one interface

---

## Key References for Terrane Framework

1. Jolliff B.L. et al. (2000) "Major lunar crustal terranes: Surface expressions and crust-mantle origins", *J. Geophys. Res.*, 105, 4197-4216. DOI: 10.1029/1999JE001103
2. Prettyman T.H. et al. (2006) "Elemental composition of the lunar surface: Analysis of gamma ray spectroscopy data from Lunar Prospector", *J. Geophys. Res.*, 111, E12007. DOI: 10.1029/2005JE002656
3. Lucey P.G. et al. (2000) "Lunar iron and titanium abundance algorithms based on final processing of Clementine UVVIS images", *J. Geophys. Res.*, 105, 20297-20305. DOI: 10.1029/1999JE001117
