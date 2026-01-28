import logging
from typing import Dict, Iterable, List, Optional, Union, Tuple, Literal
from dataclasses import dataclass, field

import numpy as np
from sklearn.mixture import GaussianMixture

from ..stats import StatsCalculator
from ..utils.data_classes import Condition, ConditionStyle


# ----------------------------
# Configs
# ----------------------------
@dataclass
class GMMConfig:
    n_components: Union[int, Dict[str, int], str] = "auto"  # integer, dict, or "auto"
    candidate_components: List[int] = field(default_factory=lambda: [1, 2])
    selection_criterion: str = "bic"  # "bic" or "aic"

    covariance_type: str = "full"
    reg_covar: float = 1e-6
    max_iter: int = 200
    tol: float = 1e-3
    random_state: Optional[int] = None
    n_init: int = 3


@dataclass
class PreprocessConfig:
    # Downsampling
    enable_downsample: bool = False
    max_samples: Optional[int] = None
    downsample_strategy: Literal["random"] = "random"
    random_state: Optional[int] = None

    # Outlier removal
    enable_outliers: bool = False
    outlier_method: Literal["zscore", "mad", "iqr"] = "zscore"
    z_thresh: float = 3.0  # for zscore
    mad_thresh: float = 3.5  # for MAD (≈ 3σ equivalent when scaled)
    iqr_k: float = 1.5  # for IQR fences
    drop_if_any_axis: bool = True  # drop row if any axis flagged (else both)

    # Standardization
    enable_standardize: bool = False
    standardize_center: bool = True
    standardize_scale: Literal["std", "mad"] = "std"
    eps: float = 1e-9  # numerical floor


# ----------------------------
# Per-condition container
# ----------------------------
@dataclass
class ConditionGMM:
    label: str
    X: np.ndarray  # (N, 2) stat matrix (post-preprocess)
    model: Optional[GaussianMixture] = None  # fitted GMM (or None if skipped)
    selected_n_components: Optional[int] = None  # chosen number of components
    converged: Optional[bool] = None  # sklearn converged_ flag
    meta: Dict[str, Union[int, float, str, Dict]] = field(
        default_factory=dict
    )  # preprocessing & fit metadata
    style: ConditionStyle = field(default_factory=ConditionStyle)


# ----------------------------
# Handler
# ----------------------------
class GMMHandler:
    """
    Fit and manage Gaussian Mixture Models over per-read statistics.

    - Optional preprocessing: downsample, outlier removal, standardize (configurable).
    - Clean logging at INFO/DEBUG levels.
    - Keeps per-condition metadata (rec.meta) about preprocessing and fit.
    """

    def __init__(
        self,
        stat1: str,
        stat2: str,
        K: Optional[int] = None,
        *,
        gmm_config: Optional[GMMConfig] = None,
        preprocess_config: Optional[PreprocessConfig] = None,
        logger: Optional[logging.Logger] = None,
    ):
        self.stat1 = stat1
        self.stat2 = stat2
        self.K = K
        self.config = gmm_config or GMMConfig()
        self.pp = preprocess_config or PreprocessConfig()

        self.logger = logger or logging.getLogger(__name__)

        self.stats_calculator = StatsCalculator(statistics=[self.stat1, self.stat2])
        self.stat1_name = self.stats_calculator._get_stat_name(self.stat1)
        self.stat2_name = self.stats_calculator._get_stat_name(self.stat2)

        self.conditions_gmms_: Dict[str, ConditionGMM] = {}

        self.logger.debug(
            f"Initialized GMMHandler with stats=({self.stat1_name}, {self.stat2_name}), "
            f"gmm_config={self.config}, preprocess_config={self.pp}"
        )

    # -------- public API --------
    def set_preprocess_config(self, cfg: PreprocessConfig) -> None:
        """Update preprocessing configuration."""
        self.pp = cfg
        self.logger.info(f"Updated PreprocessConfig: {self.pp}")

    def fit_gmms(self, conditions: Iterable[Condition]):
        self.conditions_gmms_.clear()

        for cond in conditions:
            label = cond.label
            X_raw = self._fetch_condition_data(cond)

            # preprocess
            X, meta = self._preprocess(label, X_raw)
            rec = ConditionGMM(label=label, X=X, meta=meta, style=cond.style)
            self.conditions_gmms_[label] = rec

            if X.shape[0] == 0:
                self.logger.warning(
                    f"No usable data for condition '{label}' after preprocessing; skipping GMM fit."
                )
                continue

            # choose k
            n_components = self._n_components_for(label, len(X), X=X)
            rec.selected_n_components = n_components

            # fit model
            model = self._fit_single_gmm(X, n_components=n_components)
            rec.model = model
            rec.converged = getattr(model, "converged_", None)

            self.logger.info(
                f"Fitted GMM for '{label}': n_samples={len(X)}, n_components={n_components}, "
                f"covariance_type={self.config.covariance_type}, converged={rec.converged}"
            )

    def get_condition_data(self, label: str) -> np.ndarray:
        if label not in self.conditions_gmms_:
            raise KeyError(
                f"Condition '{label}' not found. Available: {list(self.conditions_gmms_.keys())}"
            )
        return self.conditions_gmms_[label].X

    def get_condition_gmm(self, label: str) -> GaussianMixture:
        rec = self.conditions_gmms_.get(label)
        if rec is None or rec.model is None:
            raise KeyError(
                f"GMM for condition '{label}' not found. "
                f"Have you called fit_gmms()? Available: {list(self.conditions_gmms_.keys())}"
            )
        return rec.model

    def get_condition_result(self, label: str) -> GaussianMixture:
        rec = self.conditions_gmms_.get(label)
        if rec is None or rec.model is None:
            raise KeyError(
                f"GMM for condition '{label}' not found. "
                f"Have you called fit_gmms()? Available: {list(self.conditions_gmms_.keys())}"
            )
        return rec

    def predict_proba(self, label: str, X: np.ndarray) -> np.ndarray:
        model = self.get_condition_gmm(label)
        return model.predict_proba(self._ensure_2d(X))

    def score_samples(self, label: str, X: np.ndarray) -> np.ndarray:
        model = self.get_condition_gmm(label)
        return model.score_samples(self._ensure_2d(X))

    # -------- data & preprocessing --------
    def _fetch_condition_data(self, condition: Condition) -> np.ndarray:
        """Compute per-read stats for a condition and return Nx2 array: [stat1, stat2]."""
        stats = self.stats_calculator.calculate_multi_position_stats(
            condition, K=self.K
        )
        s1 = np.asarray(stats[self.stat1_name], dtype=float)
        s2 = np.asarray(stats[self.stat2_name], dtype=float)

        if s1.shape != s2.shape:
            self.logger.error(
                f"Stat arrays have different shapes for '{condition.label}': "
                f"{self.stat1_name}={s1.shape}, {self.stat2_name}={s2.shape}"
            )
            raise ValueError("Mismatched stat array shapes.")
        if s1.ndim != 1:
            self.logger.error("Expected 1D arrays from stats_calculator.")
            raise ValueError("Stats must be 1D arrays.")

        X = np.column_stack([s1, s2]) if s1.size > 0 else np.empty((0, 2), float)
        self.logger.debug(
            f"Fetched raw data for '{condition.label}': shape={X.shape}, "
            f"stats=({self.stat1_name}, {self.stat2_name})"
        )
        return X

    def _preprocess(self, label: str, X: np.ndarray) -> Tuple[np.ndarray, Dict]:
        """Apply (optional) downsample → outlier removal → standardization. Returns (X_proc, meta)."""
        meta: Dict[str, Union[int, float, str, Dict]] = {}
        n0 = len(X)
        meta["n_raw"] = int(n0)

        # 1) Downsample
        if (
            self.pp.enable_downsample
            and self.pp.max_samples is not None
            and n0 > self.pp.max_samples
        ):
            rng = np.random.default_rng(
                self.pp.random_state
                if self.pp.random_state is not None
                else self.config.random_state
            )
            idx = rng.choice(n0, size=self.pp.max_samples, replace=False)
            X = X[idx]
            meta["downsampled"] = True
            meta["n_after_downsample"] = int(len(X))
            self.logger.info(f"'{label}': downsampled {n0} → {len(X)}")
        else:
            meta["downsampled"] = False

        # 2) Outlier removal
        n_before_out = len(X)
        if self.pp.enable_outliers and n_before_out > 0:
            keep_mask = self._outlier_keep_mask(X)
            X = X[keep_mask]
            removed = int(n_before_out - len(X))
            meta["outliers_removed"] = removed
            meta["n_after_outliers"] = int(len(X))
            if removed > 0:
                self.logger.info(
                    f"'{label}': removed {removed} outliers ({removed/n_before_out:.1%})"
                )

        # 3) Standardization
        if self.pp.enable_standardize and len(X) > 0:
            X, scale_meta = self._standardize(X)
            meta["standardization"] = scale_meta
            self.logger.debug(f"'{label}': standardization params {scale_meta}")

        meta["n_final"] = int(len(X))
        return X, meta

    def _outlier_keep_mask(self, X: np.ndarray) -> np.ndarray:
        """Return boolean mask of rows to keep based on configured outlier rule."""
        if self.pp.outlier_method == "zscore":
            mu = X.mean(axis=0)
            sd = X.std(axis=0, ddof=0)
            sd = np.where(sd < self.pp.eps, self.pp.eps, sd)
            z = (X - mu) / sd
            flags = np.abs(z) > self.pp.z_thresh

        elif self.pp.outlier_method == "mad":
            med = np.median(X, axis=0)
            mad = np.median(np.abs(X - med), axis=0)
            mad = np.where(mad < self.pp.eps, self.pp.eps, mad)
            # consistent with normal: scale factor ~1.4826
            z = (X - med) / (1.4826 * mad)
            flags = np.abs(z) > self.pp.mad_thresh

        else:  # "iqr"
            q1 = np.percentile(X, 25, axis=0)
            q3 = np.percentile(X, 75, axis=0)
            iqr = q3 - q1
            iqr = np.where(iqr < self.pp.eps, self.pp.eps, iqr)
            lo = q1 - self.pp.iqr_k * iqr
            hi = q3 + self.pp.iqr_k * iqr
            flags = (X < lo) | (X > hi)

        if self.pp.drop_if_any_axis:
            keep = ~np.any(flags, axis=1)
        else:
            keep = ~np.all(flags, axis=1)
        return keep

    def _standardize(self, X: np.ndarray) -> Tuple[np.ndarray, Dict[str, List[float]]]:
        """Standardize columns (center+scale). Returns (X_std, meta)."""
        meta: Dict[str, List[float]] = {}
        if self.pp.standardize_scale == "mad":
            center = np.median(X, axis=0) if self.pp.standardize_center else np.zeros(2)
            scale = np.median(np.abs(X - np.median(X, axis=0)), axis=0)
            scale = 1.4826 * np.where(scale < self.pp.eps, self.pp.eps, scale)
        else:  # "std"
            center = X.mean(axis=0) if self.pp.standardize_center else np.zeros(2)
            scale = X.std(axis=0, ddof=0)
            scale = np.where(scale < self.pp.eps, self.pp.eps, scale)

        Xs = (X - center) / scale
        meta["center"] = center.tolist()
        meta["scale"] = scale.tolist()
        meta["method"] = self.pp.standardize_scale
        return Xs, meta

    # -------- GMM selection & fitting --------
    def _fit_single_gmm(self, X: np.ndarray, *, n_components: int) -> GaussianMixture:
        model = GaussianMixture(
            n_components=n_components,
            covariance_type=self.config.covariance_type,
            reg_covar=self.config.reg_covar,
            max_iter=self.config.max_iter,
            tol=self.config.tol,
            random_state=self.config.random_state,
            n_init=self.config.n_init,
        )
        model.fit(X)
        self.logger.debug(
            f"GMM fitted: n_components={n_components}, converged={getattr(model, 'converged_', None)}"
        )
        return model

    def _n_components_for(
        self, label: str, n_samples: int, X: Optional[np.ndarray] = None
    ) -> int:
        cfg = self.config.n_components
        if isinstance(cfg, dict):
            desired = cfg.get(label, 1)
        elif isinstance(cfg, int):
            desired = cfg
        elif isinstance(cfg, str) and cfg.lower() == "auto":
            if X is None or len(X) == 0:
                self.logger.warning(f"'{label}': empty data; defaulting k=1.")
                return 1
            return self._select_n_components_auto(X, label)
        else:
            desired = 1

        if n_samples < desired:
            self.logger.warning(
                f"'{label}': only {n_samples} samples; downscaling n_components "
                f"from {desired} to {max(1, n_samples)}"
            )
        return max(1, min(desired, n_samples))

    def _select_n_components_auto(self, X: np.ndarray, label: str) -> int:
        uniq = sorted(
            {
                nc
                for nc in self.config.candidate_components
                if isinstance(nc, int) and nc >= 1
            }
        )
        candidates = [nc for nc in uniq if nc <= len(X)]
        if not candidates:
            self.logger.warning(
                f"'{label}': no valid candidates (samples={len(X)}). Falling back to 1."
            )
            return 1

        scores = {}
        for k in candidates:
            model = GaussianMixture(
                n_components=k,
                covariance_type=self.config.covariance_type,
                reg_covar=self.config.reg_covar,
                max_iter=self.config.max_iter,
                tol=self.config.tol,
                random_state=self.config.random_state,
                n_init=self.config.n_init,
            ).fit(X)

            score = (
                model.aic(X)
                if self.config.selection_criterion.lower() == "aic"
                else model.bic(X)
            )
            scores[k] = float(score)
            self.logger.debug(
                f"'{label}': k={k}, {self.config.selection_criterion.upper()}={score:.2f}"
            )

        best_k = min(scores, key=lambda k: (scores[k], k))  # prefer smaller k on ties
        self.logger.info(
            f"'{label}': selected k={best_k} via {self.config.selection_criterion.upper()} from {sorted(candidates)}"
        )
        return best_k

    # -------- utils --------
    @staticmethod
    def _ensure_2d(X: np.ndarray) -> np.ndarray:
        X = np.asarray(X, dtype=float)
        if X.ndim == 1:
            if X.size == 2:
                return X.reshape(1, 2)
            raise ValueError("Expected 2D array with shape (N,2) or a single 2-vector.")
        if X.shape[1] != 2:
            raise ValueError(f"Expected shape (N,2); got {X.shape}.")
        return X
