from enum import Enum
from typing import Callable, Union
import numpy as np
from scipy import stats


class StatisticsFuncs(Enum):
    """Statistical functions for signal analysis."""
    
    MEAN = "mean"
    MEDIAN = "median"
    STD = "std"
    VARIANCE = "variance"
    MIN = "min"
    MAX = "max"
    SKEWNESS = "skewness"
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
            self.SKEWNESS: lambda x: stats.skew(x) if len(x) > 1 else 0,
            self.KURTOSIS: lambda x: stats.kurtosis(x) if len(x) > 1 else 0,
        }
        return function_map[self]