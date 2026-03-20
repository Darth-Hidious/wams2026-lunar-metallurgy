"""I/O utilities: data loading, validation, schema checks, run manifest."""
import os
import json
import hashlib
import logging
from datetime import datetime, timezone

import numpy as np
import pandas as pd

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------
REQUIRED_COLS = ["lat", "lon", "terrane", "FeO", "TiO2", "Al2O3", "CaO", "MgO", "SiO2"]
OPTIONAL_COLS = ["K", "Th", "P", "U", "bin_id", "source"]
CHEM_MAJOR = ["FeO", "TiO2", "Al2O3", "CaO", "MgO", "SiO2"]
CHEM_TRACE = ["K", "Th", "U"]  # ppm — NOT compositional, excluded from CLR
VALID_TERRANES = {"mare", "highlands", "kreep"}

UNITS = {
    "lat": "deg", "lon": "deg",
    "FeO": "wt%", "TiO2": "wt%", "Al2O3": "wt%",
    "CaO": "wt%", "MgO": "wt%", "SiO2": "wt%",
    "K": "ppm", "Th": "ppm", "P": "ppm", "U": "ppm",
}

# Physical bounds (generous, LP-GRS range)
BOUNDS = {
    "lat": (-90, 90), "lon": (-180, 180),
    "FeO": (0, 30), "TiO2": (0, 20), "Al2O3": (0, 40),
    "CaO": (0, 25), "MgO": (0, 25), "SiO2": (30, 65),
    "K": (0, 10000), "Th": (0, 25), "P": (0, 5000),
}


def file_sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_schema(df: pd.DataFrame) -> list[str]:
    """Return list of issues (empty = OK)."""
    issues = []
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        issues.append(f"Missing required columns: {missing}")
    bad_terranes = set(df["terrane"].dropna().unique()) - VALID_TERRANES if "terrane" in df.columns else set()
    if bad_terranes:
        issues.append(f"Unknown terrane values: {bad_terranes}. Expected: {VALID_TERRANES}")
    for col, (lo, hi) in BOUNDS.items():
        if col in df.columns:
            oob = ((df[col] < lo) | (df[col] > hi)).sum()
            if oob > 0:
                issues.append(f"{col}: {oob} values outside [{lo}, {hi}]")
    return issues


def load_data(path: str, strict: bool = True) -> pd.DataFrame:
    """Load CSV, validate schema, log summary."""
    log.info("Loading %s", path)
    df = pd.read_csv(path)
    log.info("Shape: %s", df.shape)
    issues = validate_schema(df)
    for iss in issues:
        log.warning("SCHEMA: %s", iss)
    if strict and any("Missing required" in i for i in issues):
        raise ValueError(f"Schema validation failed: {issues}")
    return df


def create_manifest(data_path: str, out_dir: str, extra: dict | None = None) -> dict:
    """Create a run manifest with timestamp, input hash, and metadata."""
    manifest = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "input_file": os.path.basename(data_path),
        "input_sha256": file_sha256(data_path) if os.path.exists(data_path) else "SYNTHETIC",
        "python_packages": {},
    }
    try:
        import sklearn
        manifest["python_packages"]["scikit-learn"] = sklearn.__version__
    except ImportError:
        pass
    manifest["python_packages"]["numpy"] = np.__version__
    manifest["python_packages"]["pandas"] = pd.__version__
    if extra:
        manifest.update(extra)
    mpath = os.path.join(out_dir, "manifest.json")
    with open(mpath, "w") as f:
        json.dump(manifest, f, indent=2)
    log.info("Manifest saved to %s", mpath)
    return manifest


# ---------------------------------------------------------------------------
# Synthetic data generator (for demo / CI)
# ---------------------------------------------------------------------------
def generate_synthetic(n_per_terrane: int = 300, seed: int = 42) -> pd.DataFrame:
    """Generate realistic synthetic LP-GRS-like data for 3 terranes.

    Ranges based on Prettyman 2006, Lucey 2000, Jolliff 2000.
    CLEARLY FLAGGED as synthetic — not real mission data.
    """
    rng = np.random.default_rng(seed)
    records = []

    specs = {
        "mare": {
            "lat": (-30, 30), "lon": (-60, 60),
            "FeO": (15, 22), "TiO2": (1, 13), "Al2O3": (8, 14),
            "CaO": (8, 12), "MgO": (6, 12), "SiO2": (40, 48),
            "K": (200, 1500), "Th": (0.5, 4), "P": (50, 300),
        },
        "highlands": {
            "lat": (-80, 80), "lon": (-180, 180),
            "FeO": (2, 8), "TiO2": (0.1, 1.5), "Al2O3": (24, 32),
            "CaO": (14, 18), "MgO": (3, 8), "SiO2": (43, 48),
            "K": (100, 600), "Th": (0.2, 1.5), "P": (20, 150),
        },
        "kreep": {
            "lat": (-10, 40), "lon": (-50, 30),
            "FeO": (8, 14), "TiO2": (1, 5), "Al2O3": (12, 20),
            "CaO": (8, 12), "MgO": (6, 10), "SiO2": (44, 52),
            "K": (1500, 5000), "Th": (4, 12), "P": (200, 800),
        },
    }

    for terrane, ranges in specs.items():
        for _ in range(n_per_terrane):
            row = {"terrane": terrane, "source": "SYNTHETIC"}
            for col, (lo, hi) in ranges.items():
                row[col] = rng.uniform(lo, hi)
            records.append(row)

    df = pd.DataFrame(records)
    log.warning("*** SYNTHETIC DATA — not real LP-GRS mission data ***")
    return df
