"""PCA analysis: decomposition, loadings, terrane separability metrics."""
import logging

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score, davies_bouldin_score

log = logging.getLogger(__name__)


def run_pca(X_std: np.ndarray, n_components: int = 3, seed: int = 42) -> tuple[PCA, np.ndarray]:
    """Fit PCA and return fitted model + scores."""
    pca = PCA(n_components=n_components, random_state=seed)
    Z = pca.fit_transform(X_std)
    ev = pca.explained_variance_ratio_
    log.info("PCA explained variance: %s (cumulative: %.3f)", np.round(ev, 4), ev.sum())
    return pca, Z


def get_loadings(pca: PCA, feature_names: list[str]) -> pd.DataFrame:
    """Extract loadings as a DataFrame."""
    n_comp = pca.n_components_
    cols = [f"PC{i+1}" for i in range(n_comp)]
    return pd.DataFrame(pca.components_.T, index=feature_names, columns=cols)


def terrane_separability(Z: np.ndarray, labels: np.ndarray) -> dict:
    """Compute silhouette and Davies-Bouldin scores on PCA scores.

    Uses true terrane labels (not KMeans clusters) for separability assessment.
    """
    Z2 = Z[:, :2]  # use PC1-PC2 plane
    unique = np.unique(labels)
    if len(unique) < 2:
        log.warning("Need >= 2 terrane classes for separability; got %d", len(unique))
        return {"silhouette": np.nan, "davies_bouldin": np.nan, "n_classes": len(unique)}

    sil = silhouette_score(Z2, labels)
    dbi = davies_bouldin_score(Z2, labels)
    log.info("Separability — Silhouette: %.3f | Davies-Bouldin: %.3f", sil, dbi)
    return {"silhouette": round(sil, 4), "davies_bouldin": round(dbi, 4), "n_classes": len(unique)}


def bootstrap_loadings(X_std: np.ndarray, n_components: int = 3,
                       n_boot: int = 200, seed: int = 42) -> tuple[np.ndarray, np.ndarray]:
    """Bootstrap confidence intervals on PCA loadings with sign correction.

    PCA eigenvectors have arbitrary sign.  Without correction, bootstrap
    iterations randomly flip component signs, inflating std by up to 17x.
    We align each bootstrap component to the reference PCA via dot-product
    sign check (Procrustes-lite).

    Returns:
        mean_loadings: (D, n_components)
        std_loadings:  (D, n_components)
    """
    # Fit reference PCA for sign alignment
    ref_pca = PCA(n_components=n_components)
    ref_pca.fit(X_std)
    ref_components = ref_pca.components_  # (n_components, D)

    rng = np.random.default_rng(seed)
    n, d = X_std.shape
    all_loadings = np.zeros((n_boot, d, n_components))

    for b in range(n_boot):
        idx = rng.choice(n, size=n, replace=True)
        pca_b = PCA(n_components=n_components)
        pca_b.fit(X_std[idx])
        for c in range(n_components):
            if np.dot(pca_b.components_[c], ref_components[c]) < 0:
                all_loadings[b, :, c] = -pca_b.components_[c]
            else:
                all_loadings[b, :, c] = pca_b.components_[c]

    mean_l = all_loadings.mean(axis=0)
    std_l = all_loadings.std(axis=0)
    log.info("Bootstrap loadings: %d iterations, max std = %.4f (sign-corrected)", n_boot, std_l.max())
    return mean_l, std_l
