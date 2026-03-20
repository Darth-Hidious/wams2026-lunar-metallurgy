"""Preprocessing: cleaning, terrane-wise imputation, CLR transform (Eq 1)."""
import logging

import numpy as np
import pandas as pd

log = logging.getLogger(__name__)

CHEM_MAJOR = ["FeO", "TiO2", "Al2O3", "CaO", "MgO", "SiO2"]
CHEM_TRACE = ["K", "Th", "U"]  # ppm — NOT compositional, excluded from CLR


def clip_to_bounds(df: pd.DataFrame, bounds: dict) -> pd.DataFrame:
    """Replace out-of-bounds values with NaN."""
    df = df.copy()
    clipped = 0
    for col, (lo, hi) in bounds.items():
        if col not in df.columns:
            continue
        mask = (df[col] < lo) | (df[col] > hi)
        n = mask.sum()
        if n > 0:
            df.loc[mask, col] = np.nan
            clipped += n
            log.info("Clipped %d values in %s to NaN (outside [%s, %s])", n, col, lo, hi)
    log.info("Total clipped: %d", clipped)
    return df


def terrane_impute(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Median imputation stratified by terrane (not global)."""
    df = df.copy()
    for terrane in df["terrane"].unique():
        mask = df["terrane"] == terrane
        subset = df.loc[mask, cols]
        medians = subset.median()
        filled = subset.fillna(medians)
        n_filled = subset.isna().sum().sum()
        df.loc[mask, cols] = filled
        if n_filled > 0:
            log.info("Terrane '%s': imputed %d missing values (median)", terrane, n_filled)
    remaining = df[cols].isna().sum().sum()
    if remaining > 0:
        log.warning("Still %d NaN after terrane imputation — falling back to global median", remaining)
        df[cols] = df[cols].fillna(df[cols].median())
    return df


def clr_transform(X: np.ndarray, eps: float = 1e-10) -> np.ndarray:
    """Centered Log-Ratio transform for compositional data (Aitchison, 1986).

    Eq 1: clr(c_i) = ln(c_i / g(c)),  g(c) = (prod c_j)^(1/D)

    Args:
        X: (n_samples, D) array of positive compositions.
        eps: small constant to avoid log(0).

    Returns:
        (n_samples, D) CLR-transformed array.
    """
    X = np.asarray(X, dtype=np.float64)
    if np.any(X <= 0):
        n_zero = np.sum(X <= 0)
        log.warning("CLR: %d zero/negative values replaced with eps=%g", n_zero, eps)
    X = np.clip(X, eps, None)
    geometric_mean = np.exp(np.mean(np.log(X), axis=1, keepdims=True))
    return np.log(X / geometric_mean)


def _replace_oxide_zeros(df: pd.DataFrame, oxide_cols: list[str]) -> pd.DataFrame:
    """Replace exact zeros in oxide columns with terrane-wise medians.

    LP-GRS unmixing can return 0 for below-detection oxides (especially TiO2
    at polar latitudes).  CLR(0) → -inf, so eps-clipping to 1e-10 creates
    extreme outliers (~-21 sigma) that dominate PCA.  Terrane-wise median
    replacement is geochemically defensible and eliminates this distortion.
    """
    df = df.copy()
    total = 0
    for col in oxide_cols:
        for terrane in df["terrane"].unique():
            mask = (df["terrane"] == terrane) & (df[col] == 0)
            n = mask.sum()
            if n > 0:
                nonzero = df.loc[(df["terrane"] == terrane) & (df[col] > 0), col]
                med = nonzero.median() if len(nonzero) > 0 else 0.1
                df.loc[mask, col] = med
                total += n
                log.info("Zero-replace: %s %s — %d zeros → median %.4f wt%%",
                         terrane, col, n, med)
    if total > 0:
        log.info("Total oxide zeros replaced: %d", total)
    return df


def preprocess_pipeline(df: pd.DataFrame, bounds: dict) -> tuple[pd.DataFrame, np.ndarray, np.ndarray, list[str]]:
    """Full preprocessing: clean -> impute -> CLR (oxides only) -> standardize.

    CLR is applied ONLY to the 6 major oxides (wt%, compositional).
    Trace elements (K, Th, U in ppm) are standardized independently and
    appended after the CLR-transformed oxides.

    Returns:
        df_clean: cleaned DataFrame
        X_clr: CLR-transformed oxide array (n, 6)
        X_std: standardized array (n, 6+T) where T = available trace cols
        feature_names: ordered list of feature names matching X_std columns
    """
    from sklearn.preprocessing import StandardScaler

    oxide_cols = [c for c in CHEM_MAJOR if c in df.columns]
    trace_cols = [c for c in CHEM_TRACE if c in df.columns]
    all_chem = oxide_cols + trace_cols
    log.info("Preprocessing %d rows | oxides (CLR): %s | traces (z-score): %s",
             len(df), oxide_cols, trace_cols)

    df_clean = df.dropna(subset=["lat", "lon", "terrane"]).copy()
    dropped = len(df) - len(df_clean)
    if dropped:
        log.info("Dropped %d rows missing lat/lon/terrane", dropped)

    df_clean = clip_to_bounds(df_clean, bounds)
    df_clean = terrane_impute(df_clean, all_chem)

    # Replace exact zeros in oxide columns with terrane-wise medians.
    # Zeros in compositional data (esp. TiO2) create extreme CLR outliers
    # (~-21 sigma) that destroy PCA separability.
    df_clean = _replace_oxide_zeros(df_clean, oxide_cols)

    # CLR on oxides only (compositional, sum ~97 wt%)
    X_oxide = df_clean[oxide_cols].values
    X_clr = clr_transform(X_oxide)
    X_oxide_std = StandardScaler().fit_transform(X_clr)

    # Standardize traces independently (ppm, non-compositional)
    if trace_cols:
        X_trace = df_clean[trace_cols].values
        X_trace_std = StandardScaler().fit_transform(X_trace)
        X_std = np.hstack([X_oxide_std, X_trace_std])
    else:
        X_std = X_oxide_std

    feature_names = oxide_cols + trace_cols
    log.info("Preprocessing done. X_std shape: %s, features: %s", X_std.shape, feature_names)
    return df_clean, X_clr, X_std, feature_names
