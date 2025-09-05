from enum import Enum
from typing import Callable, Union, Optional
import numpy as np
from scipy import stats

# Try to import numba for compilation
try:
    import numba

    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False


class StatisticsFuncs(Enum):
    """Statistical functions for signal analysis with optional compiled versions."""

    MEAN = "mean"
    MEDIAN = "median"
    STD = "std"
    VARIANCE = "variance"
    MIN = "min"
    MAX = "max"
    DURATION = "duration"
    SKEW = "skewness"
    KURTOSIS = "kurtosis"

    def to_function(self) -> Callable[[np.ndarray], float]:
        """Convert enum value to the corresponding statistical function."""
        function_map = {
            self.MEAN: np.mean,
            self.MEDIAN: np.median,
            self.STD: np.std,
            self.VARIANCE: np.var,
            self.MIN: np.min,
            self.MAX: np.max,
            self.DURATION: lambda x: np.shape(x)[0],
            self.SKEW: lambda x: stats.skew(x) if len(x) > 1 else 0,
            self.KURTOSIS: lambda x: (
                stats.kurtosis(x, fisher=True) if len(x) > 1 else 0
            ),
        }
        return function_map[self]

    def to_compiled_function(self) -> Optional[Callable[[np.ndarray], float]]:
        """
        Get compiled version of the function if available.

        Returns None if compilation is not supported for this function
        or if numba is not available.
        """
        if not NUMBA_AVAILABLE:
            return None

        # Return pre-compiled functions
        return _COMPILED_FUNCTIONS.get(self, None)


# Create compiled versions of functions that support it
_COMPILED_FUNCTIONS = {}

if NUMBA_AVAILABLE:

    @numba.jit(nopython=True, cache=True)
    def _compiled_mean(arr):
        """Compiled mean function."""
        return np.mean(arr)

    @numba.jit(nopython=True, cache=True)
    def _compiled_median(arr):
        """Compiled median function."""
        return np.median(arr)

    @numba.jit(nopython=True, cache=True)
    def _compiled_std(arr):
        """Compiled standard deviation function."""
        return np.std(arr)

    @numba.jit(nopython=True, cache=True)
    def _compiled_var(arr):
        """Compiled variance function."""
        return np.var(arr)

    @numba.jit(nopython=True, cache=True)
    def _compiled_min(arr):
        """Compiled minimum function."""
        return np.min(arr)

    @numba.jit(nopython=True, cache=True)
    def _compiled_max(arr):
        """Compiled maximum function."""
        return np.max(arr)

    # Note: median, skewness, and kurtosis are more complex and not easily compiled

    _COMPILED_FUNCTIONS = {
        StatisticsFuncs.MEAN: _compiled_mean,
        StatisticsFuncs.MEDIAN: _compiled_median,
        StatisticsFuncs.STD: _compiled_std,
        StatisticsFuncs.VARIANCE: _compiled_var,
        StatisticsFuncs.MIN: _compiled_min,
        StatisticsFuncs.MAX: _compiled_max,
    }
