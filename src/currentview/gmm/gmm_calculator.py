import itertools
import logging
from typing import List, Union, Callable, Dict, Optional, Tuple

import numpy as np
from sklearn.mixture import GaussianMixture
from multiprocessing import cpu_count
from concurrent.futures import ThreadPoolExecutor

from ..stats.stats_funcs import StatisticsFuncs

# ---- Typing aliases ---------------------------------------------------------

StatName = str
StatPair = Tuple[StatName, StatName]
GMMParams = Tuple[np.ndarray, np.ndarray]  # (mean_vector shape (2,), covariance_matrix shape (2,2))


class GMMCalculator:
    """
    Fit a 1-component Gaussian Mixture Model (GMM) for every pairwise
    combination of provided statistics.

    Given a dict mapping `stat_name -> 1D numpy array` (all arrays same length),
    this computes, for each pair (A, B), the mean vector and covariance matrix
    of a 2D single-component GMM fit to points [A[i], B[i]].
    """

    def __init__(
        self,
        statistics: Optional[List[Union[StatisticsFuncs, Callable, str]]] = None,
        logger: Optional[logging.Logger] = None,
        max_workers: int = 8,
        random_state: Optional[int] = 0,
    ):
        """
        Args:
            statistics:
                List of statistics to consider. Each item may be:
                  - a `StatisticsFuncs` enum member (its `.value` is used)
                  - a string (used as-is, e.g., "mean")
                  - a callable (its `__name__` is used)
                If None or empty, no pairs will be computed.
            logger:
                Optional logger for debug/info messages.
            max_workers:
                Upper bound for parallel worker threads.
            random_state:
                Random seed for `GaussianMixture` to keep results reproducible.
        """
        self.logger = logger or logging.getLogger(__name__)
        self.random_state = random_state

        statistics = statistics or []
        self.stat_names: List[StatName] = [self._get_stat_name(s) for s in statistics]
        self.stat_pairs: List[StatPair] = list(itertools.combinations(self.stat_names, 2))

        # Determine worker count (at least 1, capped by CPU and max_workers)
        try:
            cpu_cap = cpu_count()
        except Exception:
            cpu_cap = 1
        self._n_workers: int = max(1, min(cpu_cap, max_workers))

        self.logger.debug(
            f"Initialized GMMCalculator with {len(self.stat_pairs)} pairs.",
        )

    # --------------------------------------------------------------------- API

    def calculate_pairwise_gmms(
        self,
        calculated_statistics: Dict[StatName, np.ndarray],
    ) -> Dict[StatPair, GMMParams]:
        """
        Fit a single-component GMM for each statistic pair.

        Args:
            calculated_statistics:
                Mapping from stat name to a 1D numpy array of values.
                All arrays must have identical length.

        Returns:
            Dict mapping (stat_a, stat_b) -> (mean_vector, covariance_matrix).
        """
        if not self.stat_pairs:
            self.logger.info("No statistic pairs to compute.")
            return {}

        # Validate inputs
        for name in self.stat_names:
            if name not in calculated_statistics:
                raise KeyError(f"Missing required statistic '{name}' in calculated_statistics.")

        lengths = {len(np.atleast_1d(calculated_statistics[n])) for n in self.stat_names}
        if len(lengths) != 1:
            raise ValueError(f"All statistic arrays must have the same length; got lengths {sorted(lengths)}")

        num_pairs = len(self.stat_pairs)
        self.logger.info("Fitting %d GMM(s) over statistic pairs.", num_pairs)

        # Small jobs are typically faster sequentially
        if num_pairs <= 3 or self._n_workers == 1:
            return self._fit_pairs_sequential(calculated_statistics)
        else:
            return self._fit_pairs_parallel(calculated_statistics)

    # ----------------------------------------------------------- Implementation

    def _fit_pairs_sequential(
        self,
        calculated_statistics: Dict[StatName, np.ndarray],
    ) -> Dict[StatPair, GMMParams]:
        """
        Sequentially fit GMMs for all statistic pairs.
        """
        results: Dict[StatPair, GMMParams] = {}
        for pair in self.stat_pairs:
            results[pair] = self._fit_single_gmm(pair, calculated_statistics)
        return results

    def _fit_pairs_parallel(
        self,
        calculated_statistics: Dict[StatName, np.ndarray],
    ) -> Dict[StatPair, GMMParams]:
        """
        Fit GMMs for all statistic pairs using a thread pool.
        """
        results: Dict[StatPair, GMMParams] = {}
        with ThreadPoolExecutor(max_workers=self._n_workers) as executor:
            futures = {
                executor.submit(self._fit_single_gmm, pair, calculated_statistics): pair
                for pair in self.stat_pairs
            }
            for future in futures:
                pair = futures[future]
                results[pair] = future.result()
        return results

    def _fit_single_gmm(
        self,
        pair: StatPair,
        calculated_statistics: Dict[StatName, np.ndarray],
    ) -> GMMParams:
        """
        Fit a 1-component GMM for a single pair of statistics.

        Args:
            pair: (stat_a, stat_b)
            calculated_statistics: mapping stat name -> 1D array

        Returns:
            (mean_vector shape (2,), covariance_matrix shape (2,2))
        """
        stat_a, stat_b = pair
        a = np.asarray(calculated_statistics[stat_a]).reshape(-1)
        b = np.asarray(calculated_statistics[stat_b]).reshape(-1)
        data_2d = np.column_stack([a, b])

        gmm = GaussianMixture(
            n_components=1,
            covariance_type="full",
            random_state=self.random_state,
        )
        gmm.fit(data_2d)

        mean_vec = gmm.means_[0]       # shape (2,)
        cov_mat = gmm.covariances_[0]  # shape (2, 2)
        return mean_vec, cov_mat

    # --------------------------------------------------------------- Utilities

    def _get_stat_name(self, stat: Union[StatisticsFuncs, Callable, str]) -> StatName:
        """
        Normalize a statistic identifier (enum, string, or callable) to a string name.
        """
        if isinstance(stat, StatisticsFuncs):
            return stat.value
        if isinstance(stat, str):
            return stat
        return getattr(stat, "__name__", "custom_stat")

    @property
    def num_gmms(self) -> int:
        """
        Number of GMMs to be fitted (i.e., number of pairwise combinations).
        """
        return len(self.stat_pairs)
