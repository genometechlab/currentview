import numpy as np
from typing import List, Union, Callable, Dict, Optional, Tuple
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from multiprocessing import cpu_count
import warnings
import logging

from .stats_funcs import StatisticsFuncs
from ..utils.data_classes import ReadAlignment


class StatsCalculator:
    """Calculate and manage statistics for signal data with automatic parallel processing."""

    def __init__(
        self,
        statistics: Optional[List[Union[StatisticsFuncs, Callable, str]]] = None,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize calculator with statistics to compute.

        Args:
            statistics: List of statistics to calculate. Can be:
                - StatisticsFuncs enum values
                - String names (e.g., 'mean', 'std')
                - Callable functions
                If None, uses defaults.
            logger: Optional logger for debugging
        """
        self.logger = logger or logging.getLogger(__name__)

        # Initialize statistics
        if statistics is None:
            statistics = [
                StatisticsFuncs.MEAN,
                StatisticsFuncs.MEDIAN,
                StatisticsFuncs.STD,
            ]

        self.statistics = self._parse_statistics(statistics)
        self._validate_statistics()

        # Determine optimal worker count
        self._n_workers = min(cpu_count(), 8)  # Cap at 8 workers

        # Pre-compile statistics functions for better performance
        self._compiled_stats = self._compile_statistics()

        self.logger.debug(
            f"Initialized StatsCalculator with {len(self.statistics)} statistics"
        )
        
    def calculate_multi_position_stats(
        self, aligned_reads: List[ReadAlignment], K: Optional[int] = None
    ):
        stats_dict = {self._get_stat_name(stat): [] for stat in self.statistics}

        for read in aligned_reads:
            signal = read.get_signal(K=K)
            for stat, compiled_func in zip(self.statistics, self._compiled_stats):
                stat_name = self._get_stat_name(stat)
                try:
                    value = compiled_func(signal)
                    # Ensure scalar
                    if isinstance(value, np.ndarray):
                        value = float(value)
                except Exception as e:
                    if self.logger.isEnabledFor(logging.DEBUG):
                        self.logger.debug(f"Failed to calculate {stat_name}: {e}")

                stats_dict[stat_name].append(value)
                
        stats_dict = {k: np.array(v, dtype=np.float32) for k,v in stats_dict.items()}

        return stats_dict

    def calculate_per_position_stats(
        self, aligned_reads: List[ReadAlignment], target_position: int, K: int
    ) -> Dict[int, Dict[str, np.ndarray]]:
        """
        Calculate statistics for each read at each position in a condition.

        Uses parallel processing across positions for optimal performance.

        Args:
            aligned_reads: List of aligned reads
            target_position: Center position
            K: Window size

        Returns:
            Dict mapping position -> stat_name -> array of values (one per read)
        """
        # Calculate positions
        half_window = K // 2
        positions = list(
            range(target_position - half_window, target_position + half_window + 1)
        )

        n_reads = len(aligned_reads)
        n_positions = len(positions)

        self.logger.info(
            f"Calculating stats for {n_reads} reads across {n_positions} positions"
        )

        stats_by_position = {}
        # Use parallel processing for positions if worthwhile
        if n_positions < 3 or n_reads < 10:
            # Small dataset - sequential is faster
            for pos in positions:
                pos_stats = self._calculate_position_stats(aligned_reads, pos)
                stats_by_position[pos] = pos_stats
        else:
            # Parallel processing across positions
            chunk_size = max(1, len(positions) // (self._n_workers * 2))

            with ThreadPoolExecutor(max_workers=self._n_workers) as executor:
                # Submit position chunks for processing
                future_to_positions = {}

                for i in range(0, len(positions), chunk_size):
                    chunk_positions = positions[i : i + chunk_size]
                    future = executor.submit(
                        self._process_position_chunk, aligned_reads, chunk_positions
                    )
                    future_to_positions[future] = chunk_positions

                # Collect results as they complete
                for future in as_completed(future_to_positions):
                    try:
                        chunk_results = future.result()
                        stats_by_position.update(chunk_results)
                    except Exception as e:
                        self.logger.error(f"Error processing position chunk: {e}")
                        # Fall back to sequential for failed chunks
                        for pos in future_to_positions[future]:
                            stats_by_position[pos] = self._calculate_position_stats(
                                aligned_reads, pos
                            )
        return stats_by_position

    def _process_position_chunk(
        self, reads: List[ReadAlignment], positions: List[int]
    ) -> Dict[int, Dict[str, np.ndarray]]:
        """Process a chunk of positions (runs in worker thread)."""
        result = {}
        for pos in positions:
            result[pos] = self._calculate_position_stats(reads, pos)
        return result

    def _calculate_position_stats(
        self, reads: List[ReadAlignment], pos: int
    ) -> Dict[str, np.ndarray]:
        """
        Calculate statistics for each read at a specific position.

        Returns:
            Dict[stat_name, array of values] where each value is from one read
        """
        # Initialize result dict
        stats_dict = {self._get_stat_name(stat): [] for stat in self.statistics}

        # Collect signals from reads at this position
        valid_signals = []

        for read in reads:
            pos_base = read.get_base_at_ref_pos(pos)

            if pos_base is not None and pos_base.has_signal:
                signal = pos_base.signal

                # Handle reversed reads
                if read.is_reversed:
                    signal = signal[::-1]

                valid_signals.append(signal)

        # Calculate statistics for each signal
        if valid_signals:
            # Use pre-compiled functions for efficiency
            for stat, compiled_func in zip(self.statistics, self._compiled_stats):
                stat_name = self._get_stat_name(stat)

                # Calculate statistic for each signal
                values = []
                for signal in valid_signals:
                    try:
                        value = compiled_func(signal)
                        # Ensure scalar
                        if isinstance(value, np.ndarray):
                            value = float(value)
                        values.append(value)
                    except Exception as e:
                        if self.logger.isEnabledFor(logging.DEBUG):
                            self.logger.debug(f"Failed to calculate {stat_name}: {e}")
                        values.append(np.nan)

                stats_dict[stat_name] = np.array(values, dtype=np.float32)
        else:
            # No valid signals - return empty arrays
            for stat_name in stats_dict:
                stats_dict[stat_name] = np.array([], dtype=np.float32)

        # Log coverage warning if needed
        coverage = len(valid_signals) / len(reads) if reads else 0
        if coverage < 0.5 and len(reads) > 0:
            self.logger.warning(
                f"Low coverage at position {pos}: {len(valid_signals)}/{len(reads)} "
                f"reads ({coverage*100:.1f}%) have signal"
            )

        return stats_dict

    def _compile_statistics(self) -> List[Callable]:
        """Get optimal (compiled if available) version of each statistic function."""
        optimized = []

        for stat in self.statistics:
            if isinstance(stat, StatisticsFuncs):
                # Try to get compiled version first
                compiled_func = stat.to_compiled_function()
                if compiled_func is not None:
                    optimized.append(compiled_func)
                    self.logger.debug(f"Using compiled version for {stat.value}")
                else:
                    # Fall back to regular function
                    optimized.append(stat.to_function())
            else:
                # Custom callable - use as is
                optimized.append(stat)

        return optimized

    def _parse_statistics(
        self, statistics: List[Union[StatisticsFuncs, Callable, str]]
    ) -> List[Union[StatisticsFuncs, Callable]]:
        """Parse and validate statistics list."""
        parsed = []

        for stat in statistics:
            if isinstance(stat, str):
                # Convert string to enum
                try:
                    stat_enum = StatisticsFuncs(stat.lower())
                    parsed.append(stat_enum)
                except ValueError:
                    try:
                        stat_enum = StatisticsFuncs[stat.upper()]
                        parsed.append(stat_enum)
                    except KeyError:
                        raise ValueError(
                            f"Unknown statistic: '{stat}'. "
                            f"Valid options are: {[s.value for s in StatisticsFuncs]}"
                        )
            elif isinstance(stat, StatisticsFuncs):
                parsed.append(stat)
            elif callable(stat):
                parsed.append(stat)
            else:
                raise TypeError(
                    f"Invalid statistic type: {type(stat)}. "
                    f"Expected StatisticsFuncs, str, or callable."
                )

        # Remove duplicates while preserving order
        seen = set()
        unique = []
        for stat in parsed:
            key = stat if isinstance(stat, StatisticsFuncs) else id(stat)
            if key not in seen:
                seen.add(key)
                unique.append(stat)

        return unique

    def _validate_statistics(self):
        """Validate that we have at least one statistic."""
        if not self.statistics:
            raise ValueError("At least one statistic must be specified.")

    def _get_stat_name(self, stat: Union[StatisticsFuncs, Callable]) -> str:
        """Get human-readable name for a statistic."""
        if isinstance(stat, StatisticsFuncs):
            return stat.value
        if isinstance(stat, str):
            return stat
        return getattr(stat, "__name__", "custom_stat")

    def get_summary(
        self,
        stats_by_position: Dict[int, Dict[str, np.ndarray]],
        condition_label: Optional[str] = None,
    ) -> Dict:
        """
        Get summary of statistics across all positions.

        Args:
            stats_by_position: Output from calculate_per_position_stats
            condition_label: Optional label for the condition

        Returns:
            Summary dictionary with aggregated statistics
        """
        summary = {
            "condition": condition_label or "Unknown",
            "n_positions": len(stats_by_position),
            "positions": list(stats_by_position.keys()),
            "statistics": {},
        }

        # For each statistic type
        for stat in self.statistics:
            stat_name = self._get_stat_name(stat)

            # Collect all values for this stat across all positions
            all_values = []
            position_means = []

            for pos, pos_stats in stats_by_position.items():
                if stat_name in pos_stats:
                    values = pos_stats[stat_name]
                    if len(values) > 0:
                        all_values.extend(values)
                        position_means.append(np.mean(values))

            # Calculate summary statistics
            if all_values:
                all_values_array = np.array(all_values)
                summary["statistics"][stat_name] = {
                    "n_values": len(all_values),
                    "mean_across_all": float(np.mean(all_values_array)),
                    "std_across_all": float(np.std(all_values_array)),
                    "min": float(np.min(all_values_array)),
                    "max": float(np.max(all_values_array)),
                    "mean_of_position_means": (
                        float(np.mean(position_means)) if position_means else None
                    ),
                    "std_of_position_means": (
                        float(np.std(position_means))
                        if len(position_means) > 1
                        else None
                    ),
                }
            else:
                summary["statistics"][stat_name] = {
                    "n_values": 0,
                    "message": "No values calculated",
                }

        return summary

    @property
    def num_stats(self) -> int:
        """Number of statistics to calculate."""
        return len(self.statistics)

    @property
    def stats_names(self) -> List[str]:
        """Names of statistics to calculate."""
        return [self._get_stat_name(stat) for stat in self.statistics]
