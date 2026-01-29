# gmm_stats_tests.py
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Literal, Optional, Sequence

import numpy as np
from scipy.stats import ks_2samp

from .gmm_handler import GMMHandler


# -----------------------------------------------------------------------------
# KS test (per-feature marginal, with multiple-testing correction)
# -----------------------------------------------------------------------------
@dataclass(frozen=True)
class KSTestResult:
    label_p: str
    label_q: str
    n_p_raw: int
    n_q_raw: int
    n_p_used: List[int]  # per-dimension after finite filtering
    n_q_used: List[int]  # per-dimension after finite filtering
    feature_names: List[str]
    D: np.ndarray  # (d,)
    p_raw: np.ndarray  # (d,)
    p_adj: np.ndarray  # (d,)
    alpha: float
    correction: Literal["bonferroni"]
    significant_dims: List[int]  # indices into feature_names


def ks_test(
    gmm_handler: GMMHandler,
    label_p: str,
    label_q: str,
    feature_names: Optional[Sequence[str]] = None,
    *,
    alpha: float = 0.05,
    correction: Literal["bonferroni"] = "bonferroni",
    alternative: Literal["two-sided", "less", "greater"] = "two-sided",
    mode: Literal["auto", "exact", "asymp"] = "auto",
    drop_nonfinite: bool = True,
    verbose: bool = True,
) -> KSTestResult:
    """
    Per-feature two-sample Kolmogorov–Smirnov tests on marginal distributions.

    Notes:
      - This is a *marginal* (per-dimension) test, not a multivariate KS test.
      - Multiple testing is handled via Bonferroni correction across dimensions.

    Logging:
      - If verbose=True, emits a structured summary via gmm_handler.logger if present,
        else uses module logger.
    """
    logger = getattr(gmm_handler, "logger", None)

    if not (0.0 < float(alpha) < 1.0):
        raise ValueError("alpha must be in (0, 1)")

    X_p = np.asarray(gmm_handler.get_condition_data(label_p), dtype=float)
    X_q = np.asarray(gmm_handler.get_condition_data(label_q), dtype=float)

    # Ensure 2D
    if X_p.ndim == 1:
        X_p = X_p[:, None]
    if X_q.ndim == 1:
        X_q = X_q[:, None]
    if X_p.ndim != 2 or X_q.ndim != 2:
        raise ValueError(
            f"Expected 1D/2D arrays; got X_p.ndim={X_p.ndim}, X_q.ndim={X_q.ndim}"
        )

    n_p_raw, d_p = X_p.shape
    n_q_raw, d_q = X_q.shape
    if d_p != d_q:
        raise ValueError(f"X_p and X_q must have same #dims; got {d_p} vs {d_q}")
    d = d_p

    if n_p_raw == 0 or n_q_raw == 0:
        raise ValueError(
            f"Empty data: {label_p} has n={n_p_raw}, {label_q} has n={n_q_raw}. "
            "Cannot run KS test."
        )

    if feature_names is None:
        feature_names = (
            [gmm_handler.stat1_name, gmm_handler.stat2_name]
            if d == 2
            else [f"dim {i+1}" for i in range(d)]
        )
    else:
        feature_names = list(feature_names)
        if len(feature_names) != d:
            raise ValueError(
                f"feature_names must have length d={d}; got {len(feature_names)}"
            )

    D_vals = np.full(d, np.nan, dtype=float)
    p_raw = np.full(d, np.nan, dtype=float)
    n_p_used = [0] * d
    n_q_used = [0] * d

    for i in range(d):
        xp = X_p[:, i]
        xq = X_q[:, i]

        if drop_nonfinite:
            xp = xp[np.isfinite(xp)]
            xq = xq[np.isfinite(xq)]

        n_p_used[i] = int(xp.size)
        n_q_used[i] = int(xq.size)

        if xp.size == 0 or xq.size == 0:
            continue

        res = ks_2samp(xp, xq, alternative=alternative, method=mode)
        D_vals[i] = float(res.statistic)
        p_raw[i] = float(res.pvalue)

    if np.all(~np.isfinite(p_raw)):
        raise ValueError(
            "KS test could not be computed for any dimension (likely all values were non-finite)."
        )

    if correction != "bonferroni":
        raise ValueError(f"Unsupported correction: {correction}")

    testable = np.isfinite(p_raw)
    m = int(testable.sum())
    if m == 0:
        raise ValueError("No testable dimensions after filtering.")

    p_adj = np.full_like(p_raw, np.nan)
    p_adj[testable] = np.minimum(p_raw[testable] * m, 1.0)

    significant_dims = [i for i in range(d) if testable[i] and (p_adj[i] < alpha)]

    out = KSTestResult(
        label_p=label_p,
        label_q=label_q,
        n_p_raw=int(n_p_raw),
        n_q_raw=int(n_q_raw),
        n_p_used=n_p_used,
        n_q_used=n_q_used,
        feature_names=list(feature_names),
        D=D_vals,
        p_raw=p_raw,
        p_adj=p_adj,
        alpha=float(alpha),
        correction="bonferroni",
        significant_dims=significant_dims,
    )

    if verbose:
        msg_lines: List[str] = []
        alpha_per_test = alpha / m
        msg_lines.append("Per-feature two-sample KS tests (marginals)")
        msg_lines.append(
            f"Populations: {label_p} (n_raw={n_p_raw}) vs {label_q} (n_raw={n_q_raw})"
        )
        msg_lines.append(f"Dimensions: d={d} (testable={m})")
        msg_lines.append(
            f"Alternative: {alternative} | mode={mode} | drop_nonfinite={drop_nonfinite}"
        )
        msg_lines.append(
            f"Family-wise alpha={alpha} | Bonferroni per-test alpha={alpha_per_test:.6g}"
        )
        msg_lines.append("Per-feature results:")
        for i in range(d):
            fname = feature_names[i]
            if not testable[i]:
                msg_lines.append(
                    f"  - {fname}: SKIPPED (n_used {n_p_used[i]} vs {n_q_used[i]})"
                )
                continue
            msg_lines.append(
                f"  - {fname}: D={D_vals[i]:.6f}, p_raw={p_raw[i]:.4g}, p_adj={p_adj[i]:.4g} "
                f"(n_used {n_p_used[i]} vs {n_q_used[i]})"
            )
        if significant_dims:
            sig = ", ".join(feature_names[i] for i in significant_dims)
            msg_lines.append(
                f"Decision: REJECT global 'all marginals equal' at alpha={alpha}. Significant: {sig}"
            )
        else:
            msg_lines.append(
                f"Decision: DO NOT REJECT global 'all marginals equal' at alpha={alpha}. Significant: none"
            )
        msg_lines.append("Note: marginal test only (not multivariate joint KS).")

        msg = "\n".join(msg_lines)
        if logger is not None:
            logger.info(msg)
        else:
            # fallback: print if no handler logger
            print(msg)

    return out


# -----------------------------------------------------------------------------
# Jensen–Shannon (Monte Carlo) between fitted GMMs
# -----------------------------------------------------------------------------
@dataclass(frozen=True)
class JSTestResult:
    label_p: str
    label_q: str
    n_samples: int
    base: float
    js_divergence: float
    js_distance: float


def js_test(
    gmm_handler: GMMHandler,
    label_p: str,
    label_q: str,
    *,
    n_samples: int = 20000,
    base: float = 2.0,
    random_state: Optional[int] = None,
    verbose: bool = True,
) -> JSTestResult:
    """
    Monte-Carlo Jensen–Shannon divergence/distance between two fitted GMMs.

    - Divergence is computed in log-space and normalized by log(base).
      With base=2, JS divergence is in [0, 1].
    - Distance is sqrt(divergence); also in [0, 1].

    random_state:
      If provided, we sample using a NumPy RNG and sample components explicitly
      (reproducible, without mutating sklearn model state).

    Logging:
      - If verbose=True, emits a brief summary via gmm_handler.logger if present,
        else falls back to print.
    """
    logger = getattr(gmm_handler, "logger", None)

    if int(n_samples) < 2:
        raise ValueError("n_samples must be at least 2")
    if int(n_samples) % 2 == 1:
        raise ValueError("n_samples must be even")
    if float(base) <= 1.0:
        raise ValueError("base must be > 1.0")

    n_samples = int(n_samples)
    n_p = n_samples // 2
    n_q = n_samples - n_p

    gmm_p = gmm_handler.get_condition_gmm(label_p)
    gmm_q = gmm_handler.get_condition_gmm(label_q)

    if random_state is None:
        Xp, _ = gmm_p.sample(n_p)
        Xq, _ = gmm_q.sample(n_q)
    else:
        rng = np.random.default_rng(int(random_state))
        Xp = _sample_from_gmm_explicit(gmm_p, n_p, rng)
        Xq = _sample_from_gmm_explicit(gmm_q, n_q, rng)

    Xp = np.asarray(Xp, dtype=float)
    Xq = np.asarray(Xq, dtype=float)

    log_p_Xp = gmm_p.score_samples(Xp)
    log_q_Xp = gmm_q.score_samples(Xp)

    log_p_Xq = gmm_p.score_samples(Xq)
    log_q_Xq = gmm_q.score_samples(Xq)

    log2 = np.log(2.0)
    log_m_Xp = np.logaddexp(log_p_Xp, log_q_Xp) - log2
    log_m_Xq = np.logaddexp(log_p_Xq, log_q_Xq) - log2

    kl_p_m = float(np.mean(log_p_Xp - log_m_Xp))
    kl_q_m = float(np.mean(log_q_Xq - log_m_Xq))

    js_div_nat = 0.5 * (kl_p_m + kl_q_m)
    js_div = js_div_nat / np.log(float(base))

    js_div = float(max(js_div, 0.0))
    js_dist = float(np.sqrt(js_div))

    out = JSTestResult(
        label_p=label_p,
        label_q=label_q,
        n_samples=n_samples,
        base=float(base),
        js_divergence=js_div,
        js_distance=js_dist,
    )

    if verbose:
        msg = (
            "Jensen–Shannon test (MC, between fitted GMMs)\n"
            f"Populations: {label_p} vs {label_q}\n"
            f"n_samples={n_samples} (n_p={n_p}, n_q={n_q}) | base={base} | random_state={random_state}\n"
            f"JS divergence={js_div:.6g} | JS distance={js_dist:.6g}"
        )
        if logger is not None:
            logger.info(msg)
        else:
            print(msg)

    return out


def _sample_from_gmm_explicit(gmm, n: int, rng: np.random.Generator) -> np.ndarray:
    """
    Sampling from sklearn GaussianMixture.

    Draw z ~ Categorical(weights_), then x ~ N(mean_z, cov_z).
    Handles covariance_type in {"full","tied","diag","spherical"}.
    """
    w = np.asarray(gmm.weights_, dtype=float)
    w = w / w.sum()
    k = int(w.size)

    z = rng.choice(k, size=int(n), p=w)

    means = np.asarray(gmm.means_, dtype=float)  # (k, d)
    d = int(means.shape[1])

    cov_type = getattr(gmm, "covariance_type", "full")
    covs = getattr(gmm, "covariances_", None)
    if covs is None:
        raise ValueError("GMM is missing covariances_; is it fitted?")

    X = np.empty((int(n), d), dtype=float)

    if cov_type == "full":
        # covs: (k, d, d)
        for j in range(k):
            idx = np.where(z == j)[0]
            if idx.size == 0:
                continue
            X[idx] = rng.multivariate_normal(mean=means[j], cov=covs[j], size=idx.size)

    elif cov_type == "tied":
        # covs: (d, d)
        for j in range(k):
            idx = np.where(z == j)[0]
            if idx.size == 0:
                continue
            X[idx] = rng.multivariate_normal(mean=means[j], cov=covs, size=idx.size)

    elif cov_type == "diag":
        # covs: (k, d)
        for j in range(k):
            idx = np.where(z == j)[0]
            if idx.size == 0:
                continue
            X[idx] = means[j] + rng.normal(size=(idx.size, d)) * np.sqrt(covs[j])

    elif cov_type == "spherical":
        # covs: (k,)
        for j in range(k):
            idx = np.where(z == j)[0]
            if idx.size == 0:
                continue
            X[idx] = means[j] + rng.normal(size=(idx.size, d)) * np.sqrt(float(covs[j]))

    else:
        raise ValueError(f"Unsupported covariance_type: {cov_type}")

    return X
