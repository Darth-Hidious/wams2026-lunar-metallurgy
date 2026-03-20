"""Terrane -> alloy-family -> process compatibility mapping (Table 1 + Eq 5)."""
import logging

import pandas as pd

log = logging.getLogger(__name__)

# Table 1 from paper draft (template)
COMPATIBILITY_MATRIX = pd.DataFrame([
    {
        "Terrane": "Mare",
        "Chemistry": "Fe/Ti-rich",
        "Alloy family": "Ni-superalloy / RHEA",
        "Likely process": "DED + hybrid finishing",
        "Main risks": "O pickup, feed variability",
        "Evidence class": "Model-derived + Measured (Earth-side)",
    },
    {
        "Terrane": "Highlands",
        "Chemistry": "Al/Ca-rich",
        "Alloy family": "HEA / Ni-superalloy",
        "Likely process": "PM + SLM/DED",
        "Main risks": "Crack/oxidation balance",
        "Evidence class": "Model-derived",
    },
    {
        "Terrane": "KREEP-bearing",
        "Chemistry": "K/REE/P proxies",
        "Alloy family": "HEA / functional RHEA layers",
        "Likely process": "Graded/coating routes",
        "Main risks": "Heterogeneity, beneficiation",
        "Evidence class": "Assumed + Roadmap hypothesis",
    },
])


def get_compatibility_matrix() -> pd.DataFrame:
    """Return the terrane-to-alloy-to-process compatibility matrix."""
    return COMPATIBILITY_MATRIX.copy()


def assign_portfolio(df: pd.DataFrame) -> pd.DataFrame:
    """Eq 5: F(x_t, q_f, d_c) -> (a_f, b_w, p_r, c_l)

    Assigns each pixel:
      a_f = alloy family
      b_w = blend window (ISRU fraction estimate)
      p_r = process route
      c_l = confidence level
    """
    df = df.copy()

    # Rule-based assignment from terrane label
    alloy_map = {"mare": "Ni-superalloy / RHEA", "highlands": "HEA / Ni-superalloy",
                 "kreep": "HEA / functional RHEA layers"}
    process_map = {"mare": "DED + hybrid", "highlands": "PM + SLM/DED",
                   "kreep": "Graded/coating"}

    df["alloy_family"] = df["terrane"].map(alloy_map).fillna("Unclassified")
    df["process_route"] = df["terrane"].map(process_map).fillna("Unclassified")

    # Blend window: fraction of alloy that could be ISRU-sourced (heuristic)
    # Mare Fe-Ti: high ISRU potential; highlands Al: moderate; KREEP: low (need imported bases)
    blend_map = {"mare": 0.7, "highlands": 0.5, "kreep": 0.3}
    df["blend_window"] = df["terrane"].map(blend_map).fillna(0.0)

    # Confidence level based on evidence class
    conf_map = {"mare": "medium", "highlands": "medium", "kreep": "low"}
    df["confidence"] = df["terrane"].map(conf_map).fillna("low")

    log.info("Portfolio assigned. Distribution:\n%s",
             df["alloy_family"].value_counts().to_string())
    return df
