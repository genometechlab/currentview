"""Shared preprocessing configuration for the GMM and UMAP handlers.

Both handlers apply the same downsample -> outlier-removal -> standardize
pipeline, so they share one config class. Keeping a single definition means a
``PreprocessConfig`` built for one handler can be passed to the other.
"""

from dataclasses import dataclass
from typing import Literal, Optional


@dataclass
class PreprocessConfig:
    """Options for the downsample / outlier / standardize pipeline."""

    # Downsampling
    enable_downsample: bool = False
    max_samples: Optional[int] = None
    downsample_strategy: Literal["random"] = "random"
    random_state: Optional[int] = None

    # Deprecated alias for ``random_state``, kept so configs written against the
    # old GMM-only class keep working. When set, it wins over ``random_state``.
    ds_random_state: Optional[int] = None

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

    def __post_init__(self):
        if self.ds_random_state is not None:
            self.random_state = self.ds_random_state
