"""Manufacturability / access indices with penalty terms (Eqs 2-4)."""
import logging

import numpy as np
import pandas as pd

log = logging.getLogger(__name__)


def _minmax(s: pd.Series) -> pd.Series:
    """Min-max normalize to [0, 1]."""
    rng = s.max() - s.min()
    if rng == 0:
        log.warning("Zero range in column — returning 0.5 for all")
        return pd.Series(0.5, index=s.index)
    return (s - s.min()) / rng


# Default weights — configurable, pending professor review.
# Paper Eq 2-4: [VERIFY: Finalize weights with professor review and sensitivity analysis.]
# Note: LP-GRS measures K, Th, U (not P). U = 0.27*Th (tied), so partially redundant.
DEFAULT_WEIGHTS = {
    "I_FeTi": {"w_FeO": 0.50, "w_TiO2": 0.40, "w_penalty": 0.10},
    "I_AlCa": {"v_Al2O3": 0.55, "v_CaO": 0.35, "v_penalty": 0.10},
    "I_KREEP": {"u_K": 0.40, "u_Th": 0.40, "u_U": 0.10, "u_unc": 0.10},
}


def compute_penalty_impurity(df: pd.DataFrame) -> pd.Series:
    """Penalty for Fe-Ti index (Eq 2): KREEP contamination in mare-like pixels.

    High K or Th in a pixel that should be Fe-Ti-dominated suggests mixing
    with incompatible-element-rich material, degrading feedstock purity.
    """
    penalty = pd.Series(0.0, index=df.index)
    if "K" in df.columns and "Th" in df.columns:
        penalty = 0.6 * _minmax(df["K"]) + 0.4 * _minmax(df["Th"])
    elif "K" in df.columns:
        penalty = _minmax(df["K"])
    else:
        log.warning("No K/Th columns — impurity penalty set to 0")
    return penalty


def compute_penalty_heterogeneity(df: pd.DataFrame) -> pd.Series:
    """Penalty for Al-Ca index (Eq 3): compositional heterogeneity.

    Uses deviation of SiO2 from terrane mean as proxy for mixing.
    """
    penalty = pd.Series(0.0, index=df.index)
    if "SiO2" in df.columns and "terrane" in df.columns:
        terrane_mean = df.groupby("terrane")["SiO2"].transform("mean")
        deviation = np.abs(df["SiO2"] - terrane_mean)
        penalty = _minmax(deviation)
    else:
        log.warning("No SiO2/terrane — heterogeneity penalty set to 0")
    return penalty


def compute_uncertainty_proxy(df: pd.DataFrame) -> pd.Series:
    """Uncertainty proxy for KREEP index (Eq 4).

    LP-GRS counting statistics improve with dwell time; polar regions
    have fewer orbits. Use |lat| as a rough proxy (higher lat = fewer counts).
    """
    if "lat" in df.columns:
        return _minmax(np.abs(df["lat"]))
    log.warning("No lat column — uncertainty proxy set to 0")
    return pd.Series(0.0, index=df.index)


def compute_indices(df: pd.DataFrame,
                    weights: dict | None = None) -> pd.DataFrame:
    """Compute all three metallurgical potential indices (Eqs 2-4).

    Returns DataFrame with columns: I_FeTi, I_AlCa, I_KREEP.
    """
    w = weights or DEFAULT_WEIGHTS
    df = df.copy()

    # Normalize all inputs to [0,1]
    nFeO = _minmax(df["FeO"])
    nTiO2 = _minmax(df["TiO2"])
    nAl2O3 = _minmax(df["Al2O3"])
    nCaO = _minmax(df["CaO"])

    pen_imp = compute_penalty_impurity(df)
    pen_het = compute_penalty_heterogeneity(df)
    pen_unc = compute_uncertainty_proxy(df)

    wf = w["I_FeTi"]
    df["I_FeTi"] = (wf["w_FeO"] * nFeO + wf["w_TiO2"] * nTiO2
                    - wf["w_penalty"] * pen_imp)

    wa = w["I_AlCa"]
    df["I_AlCa"] = (wa["v_Al2O3"] * nAl2O3 + wa["v_CaO"] * nCaO
                    - wa["v_penalty"] * pen_het)

    wk = w["I_KREEP"]
    if "K" in df.columns and "Th" in df.columns:
        nK = _minmax(df["K"])
        nTh = _minmax(df["Th"])
        nU = _minmax(df["U"]) if "U" in df.columns else pd.Series(0.0, index=df.index)
        df["I_KREEP"] = (wk["u_K"] * nK + wk["u_Th"] * nTh
                         + wk["u_U"] * nU - wk["u_unc"] * pen_unc)
    else:
        log.warning("K/Th not available — I_KREEP set to NaN")
        df["I_KREEP"] = np.nan

    # Clip to [0, 1]
    for col in ["I_FeTi", "I_AlCa", "I_KREEP"]:
        df[col] = df[col].clip(0, 1)

    log.info("Indices computed. Means: I_FeTi=%.3f, I_AlCa=%.3f, I_KREEP=%.3f",
             df["I_FeTi"].mean(), df["I_AlCa"].mean(),
             df["I_KREEP"].mean() if not df["I_KREEP"].isna().all() else float("nan"))
    return df
