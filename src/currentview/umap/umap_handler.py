import logging
from typing import (
    Dict,
    Iterable,
    List,
    Optional,
    Union,
    Tuple,
    Literal,
    Sequence,
    TYPE_CHECKING,
)
from dataclasses import dataclass, field

import numpy as np

from ..stats import StatsCalculator, StatisticsFuncs
from ..utils.data_classes import Condition, ConditionStyle

if TYPE_CHECKING:
    from .umap_visualizer import UMAPVisualizer
    from ..utils.plotly_utils import PlotStyle


# ----------------------------
# Configs
# ----------------------------
@dataclass
class UMAPConfig:
    n_components: int = 2
    n_neighbors: int = 15
    min_dist: float = 0.1
    metric: str = "euclidean"
    random_state: Optional[int] = 42
    verbose: bool = False


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
class ConditionUMAP:
    label: str
    X: np.ndarray  # (N, D) stat matrix (post-preprocess), D = n_stats * n_positions
    embedding: Optional[np.ndarray] = None  # (N, 2) UMAP embedding
    meta: Dict[str, Union[int, float, str, Dict]] = field(
        default_factory=dict
    )  # preprocessing metadata
    style: ConditionStyle = field(default_factory=ConditionStyle)


# ----------------------------
# Handler
# ----------------------------
class UMAPHandler:
    """
    Fit and manage UMAP embeddings over per-read statistics across multiple positions.

    - Fits a single UMAP model on combined data from all conditions.
    - Optional preprocessing: downsample, outlier removal, standardize (configurable).
    - Clean logging at INFO/DEBUG levels.
    - Keeps per-condition metadata (rec.meta) about preprocessing.
    """

    def __init__(
        self,
        stats: List[str],
        offsets_window: Tuple[int, int],
        *,
        umap_config: Optional[UMAPConfig] = None,
        preprocess_config: Optional[PreprocessConfig] = None,
        logger: Optional[logging.Logger] = None,
    ):
        self.logger = logger or logging.getLogger(__name__)

        self.stats_calculator = StatsCalculator(statistics=stats)
        self._stats_names = self.stats_calculator.stats_names
        self._n_stats = len(self._stats_names)

        self.offsets_window = offsets_window
        self._num_positions = self.offsets_window[1] - self.offsets_window[0] + 1

        self.config = umap_config or UMAPConfig()
        self.pp = preprocess_config or PreprocessConfig()

        self.umap_model_ = None  # Shared UMAP model
        self.conditions_umaps_: Dict[str, ConditionUMAP] = {}

        self.logger.debug(
            f"Initialized UMAPHandler with stats={self._stats_names}, "
            f"offsets_window={self.offsets_window}, "
            f"feature_dim={self._n_stats * self._num_positions}, "
            f"umap_config={self.config}, preprocess_config={self.pp}"
        )

    # -------- public API --------
    def set_preprocess_config(self, cfg: PreprocessConfig) -> None:
        """Update preprocessing configuration."""
        self.pp = cfg
        self.logger.info(f"Updated PreprocessConfig: {self.pp}")

    def fit_umap(self, conditions: Iterable[Condition]) -> None:
        """Fit UMAP model on combined data from all conditions, reduced to two dimensions."""
        try:
            import umap
        except ImportError:
            self.logger.error(
                "UMAP not installed. Install with: pip install umap-learn"
            )
            raise ImportError("umap-learn package required for UMAP functionality")

        conditions = list(conditions)
        self.conditions_umaps_.clear()

        self.logger.info(
            f"Fitting UMAP on combined data from {len(conditions)} conditions"
        )

        # Step 1: Fetch and preprocess data for each condition
        processed_data = []
        valid_conditions = []

        for cond in conditions:
            label = cond.label
            X_raw = self._fetch_condition_data(cond)

            # preprocess
            X, meta = self._preprocess(label, X_raw)
            rec = ConditionUMAP(label=label, X=X, meta=meta, style=cond.style)
            self.conditions_umaps_[label] = rec

            if X.shape[0] == 0:
                self.logger.warning(
                    f"No usable data for condition '{label}' after preprocessing; skipping UMAP."
                )
                continue

            processed_data.append(X)
            valid_conditions.append(rec)

            self.logger.info(
                f"Preprocessed '{label}': n_samples={len(X)}, n_features={X.shape[1]}"
            )

        if not processed_data:
            self.logger.error("No valid data found across all conditions")
            return

        # Step 2: Combine all data
        combined_data = np.vstack(processed_data)
        self.logger.info(
            f"Combined data shape: {combined_data.shape} "
            f"({combined_data.shape[0]} samples × {combined_data.shape[1]} features)"
        )

        # Step 3: Fit UMAP on combined data
        n_neighbors = min(self.config.n_neighbors, combined_data.shape[0] - 1)
        if n_neighbors < 2:
            self.logger.error(
                f"Not enough samples ({combined_data.shape[0]}) to fit UMAP (need at least 2)"
            )
            return

        reducer = umap.UMAP(
            n_components=self.config.n_components,
            n_neighbors=n_neighbors,
            min_dist=self.config.min_dist,
            metric=self.config.metric,
            random_state=self.config.random_state,
            verbose=self.config.verbose,
        )

        self.logger.info(
            f"Fitting UMAP (n_neighbors={n_neighbors}, min_dist={self.config.min_dist})..."
        )
        embedding = reducer.fit_transform(combined_data)
        self.umap_model_ = reducer

        # Step 4: Split embeddings back to per-condition
        start_idx = 0
        for rec in valid_conditions:
            n_reads = len(rec.X)
            end_idx = start_idx + n_reads

            rec.embedding = embedding[start_idx:end_idx]
            self.logger.info(f"Extracted embedding for '{rec.label}': {n_reads} reads")
            start_idx = end_idx

        self.logger.info("UMAP fitting complete")

    def get_condition_data(self, label: str) -> np.ndarray:
        """Get preprocessed data (before UMAP) for a condition."""
        if label not in self.conditions_umaps_:
            raise KeyError(
                f"Condition '{label}' not found. Available: {list(self.conditions_umaps_.keys())}"
            )
        return self.conditions_umaps_[label].X

    def get_condition_embedding(self, label: str) -> np.ndarray:
        """Get UMAP embedding for a condition."""
        rec = self.conditions_umaps_.get(label)
        if rec is None or rec.embedding is None:
            raise KeyError(
                f"UMAP embedding for condition '{label}' not found. "
                f"Have you called fit_umap()? Available: {list(self.conditions_umaps_.keys())}"
            )
        return rec.embedding

    def get_condition_result(self, label: str) -> ConditionUMAP:
        """Get full ConditionUMAP record for a condition."""
        rec = self.conditions_umaps_.get(label)
        if rec is None:
            raise KeyError(
                f"Condition '{label}' not found. Available: {list(self.conditions_umaps_.keys())}"
            )
        return rec

    def transform(self, X: np.ndarray) -> np.ndarray:
        """Transform new data using the fitted UMAP model."""
        if self.umap_model_ is None:
            raise ValueError("UMAP model not fitted. Call fit_umap() first.")
        return self.umap_model_.transform(X)

    # -------- data & preprocessing --------
    def _fetch_condition_data(self, condition: Condition) -> np.ndarray:
        """
        Compute per-read stats for a condition across multiple positions.
        Returns (n_reads, n_stats * n_positions) array.
        """
        condition_stats = condition.stats
        feat_mat = np.zeros((self._num_positions, condition.n_reads, self._n_stats))

        positions_range = (
            condition.target_position + self.offsets_window[0],
            condition.target_position + self.offsets_window[1] + 1,
        )

        for pos_idx, pos in enumerate(range(*positions_range)):
            pos_feat_map = np.zeros((condition.n_reads, self._n_stats))
            for stat_idx, stat_name in enumerate(self._stats_names):
                pos_feat_map[:, stat_idx] = condition_stats[pos][stat_name]
            feat_mat[pos_idx] = pos_feat_map

        # Permute and reshape to get (n_reads, n_stats * n_positions)
        feat_mat = np.transpose(feat_mat, (1, 0, 2))  # (n_reads, n_positions, n_stats)
        feat_mat = feat_mat.reshape(
            condition.n_reads, -1
        )  # (n_reads, n_stats * n_positions)

        self.logger.debug(
            f"Fetched raw data for '{condition.label}': shape={feat_mat.shape}, "
            f"stats={self._stats_names}, positions={self._num_positions}"
        )
        return feat_mat

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
            rng = np.random.default_rng(self.pp.random_state)
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
            center = (
                np.median(X, axis=0)
                if self.pp.standardize_center
                else np.zeros(X.shape[1])
            )
            scale = np.median(np.abs(X - np.median(X, axis=0)), axis=0)
            scale = 1.4826 * np.where(scale < self.pp.eps, self.pp.eps, scale)
        else:  # "std"
            center = (
                X.mean(axis=0) if self.pp.standardize_center else np.zeros(X.shape[1])
            )
            scale = X.std(axis=0, ddof=0)
            scale = np.where(scale < self.pp.eps, self.pp.eps, scale)

        Xs = (X - center) / scale
        meta["center"] = center.tolist()
        meta["scale"] = scale.tolist()
        meta["method"] = self.pp.standardize_scale
        return Xs, meta

    # -------- Visualizing --------
    def visualize(
        self,
        *,
        style: Optional["PlotStyle"] = None,
        x_label: Optional[str] = None,
        y_label: Optional[str] = None,
        title: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
    ) -> "UMAPVisualizer":
        # local import avoids circular deps + optional dependency pressure
        from .umap_visualizer import UMAPVisualizer

        return UMAPVisualizer.from_handler(
            self,
            style=style,
            x_label=x_label,
            y_label=y_label,
            title=title,
            logger=logger,
        )

    def figure(self, **kwargs):
        """Convenience: return plotly fig directly."""
        return self.visualize(**kwargs).get_fig()
