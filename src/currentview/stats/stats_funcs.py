from __future__ import annotations

from enum import Enum
from typing import Callable, Optional, Any
import numpy as np
from scipy import stats

# Try to import numba for compilation
try:
    import numba
    NUMBA_AVAILABLE = True
except ImportError:
    numba = None
    NUMBA_AVAILABLE = False


class StatisticsFuncs(Enum):
    """
    Statistical functions for signal analysis.

    Each member carries:
      - key: user/API string (e.g. "mean")
      - unit: display unit ("pA", "pA²", "samples", or None for unitless)
    """

    MEAN     = ("mean", "pA")
    MEDIAN   = ("median", "pA")
    STD      = ("std", "pA")
    VARIANCE = ("variance", "pA²")
    MIN      = ("min", "pA")
    MAX      = ("max", "pA")
    DURATION = ("duration", "samples")
    SKEW     = ("skewness", None)
    KURTOSIS = ("kurtosis", None)

    def __init__(self, key: str, unit: str | None):
        self.key = key
        self.unit = unit

    @property
    def label(self) -> str:
        """Human-friendly label including units where applicable."""
        base = self.key.capitalize()
        return base if self.unit is None else f"{base} ({self.unit})"

    def __str__(self) -> str:
        return self.label

    @classmethod
    def coerce(cls, value: str | "StatisticsFuncs") -> "StatisticsFuncs":
        """
        Accept either an enum member or a user-provided string like "median"/"MEDIAN".
        Normalizes and returns the enum member.
        """
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            s = value.strip().lower()
            for m in cls:
                if s == m.key or s == m.name.lower():
                    return m
        valid = ", ".join(m.key for m in cls)
        raise ValueError(f"Unknown statistic {value!r}. Choose from: {valid}")

    def to_function(self) -> Callable[[np.ndarray], float]:
        """Convert enum member to the corresponding statistical function."""
        function_map: dict[StatisticsFuncs, Callable[[np.ndarray], float]] = {
            StatisticsFuncs.MEAN: np.mean,
            StatisticsFuncs.MEDIAN: np.median,
            StatisticsFuncs.STD: np.std,
            StatisticsFuncs.VARIANCE: np.var,
            StatisticsFuncs.MIN: np.min,
            StatisticsFuncs.MAX: np.max,
            StatisticsFuncs.DURATION: lambda x: float(np.shape(x)[0]),
            StatisticsFuncs.SKEW: lambda x: float(stats.skew(x)) if len(x) > 1 else 0.0,
            StatisticsFuncs.KURTOSIS: lambda x: float(stats.kurtosis(x, fisher=True)) if len(x) > 1 else 0.0,
        }
        return function_map[self]

    def to_compiled_function(self) -> Optional[Callable[[np.ndarray], float]]:
        """
        Return a compiled version if available; otherwise None.
        """
        if not NUMBA_AVAILABLE:
            return None
        return _COMPILED_FUNCTIONS.get(self)


# ----------------------------
# Compiled function registry
# ----------------------------
_COMPILED_FUNCTIONS: dict[StatisticsFuncs, Callable[[np.ndarray], float]] = {}

if NUMBA_AVAILABLE:

    @numba.njit(cache=True)
    def _compiled_mean(arr):
        return np.mean(arr)

    @numba.njit(cache=True)
    def _compiled_median(arr):
        return np.median(arr)

    @numba.njit(cache=True)
    def _compiled_std(arr):
        return np.std(arr)

    @numba.njit(cache=True)
    def _compiled_var(arr):
        return np.var(arr)

    @numba.njit(cache=True)
    def _compiled_min(arr):
        return np.min(arr)

    @numba.njit(cache=True)
    def _compiled_max(arr):
        return np.max(arr)

    _COMPILED_FUNCTIONS = {
        StatisticsFuncs.MEAN: _compiled_mean,
        StatisticsFuncs.MEDIAN: _compiled_median,
        StatisticsFuncs.STD: _compiled_std,
        StatisticsFuncs.VARIANCE: _compiled_var,
        StatisticsFuncs.MIN: _compiled_min,
        StatisticsFuncs.MAX: _compiled_max,
    }
