import numpy as np
from typing import List, Union, Callable, Dict, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict
from .stats_funcs import StatisticsFuncs
from ..utils import ReadAlignment


class StatsCalculator:
    """Calculate and manage statistics for signal data."""
    
    def __init__(self,
                 statistics: Optional[List[Union[StatisticsFuncs, Callable, str]]] = None):
        """
        Initialize calculator with statistics to compute.
        
        Args:
            statistics: List of statistics to calculate. Can be:
                - StatisticsFuncs enum values
                - String names (e.g., 'mean', 'std')
                - Callable functions
                If None, uses defaults.
        """
        if statistics is None:
            # Default statistics
            statistics = [
                StatisticsFuncs.MEAN,
                StatisticsFuncs.MEDIAN,
                StatisticsFuncs.STD,
            ]
        
        self.statistics = []
        
        for stat in statistics:
            if isinstance(stat, str):
                # Convert string to StatisticsFuncs enum
                try:
                    # Try to find matching enum value
                    stat_enum = StatisticsFuncs(stat.lower())
                    self.statistics.append(stat_enum)
                except ValueError:
                    # If not a valid enum value, check if it's a valid enum name
                    try:
                        stat_enum = StatisticsFuncs[stat.upper()]
                        self.statistics.append(stat_enum)
                    except KeyError:
                        raise ValueError(f"Unknown statistic: '{stat}'. "
                                       f"Valid options are: {[s.value for s in StatisticsFuncs]}")
            
            elif isinstance(stat, StatisticsFuncs):
                # Already a StatisticsFuncs enum
                self.statistics.append(stat)
            
            elif callable(stat):
                # Custom callable function
                self.statistics.append(stat)
            
            else:
                raise TypeError(f"Invalid statistic type: {type(stat)}. "
                              f"Expected StatisticsFuncs, str, or callable.")
        
        # Validate we have at least one statistic
        if not self.statistics:
            raise ValueError("At least one statistic must be specified.")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_stats = []
        for stat in self.statistics:
            # Create a hashable key for the stat
            if isinstance(stat, StatisticsFuncs):
                key = stat
            elif callable(stat):
                key = id(stat)  # Use object id for callables
            else:
                key = stat
            
            if key not in seen:
                seen.add(key)
                unique_stats.append(stat)
        
        self.statistics = unique_stats

    def calculate_condition_stats(self,
                                  aligned_reads: List[ReadAlignment],
                                  target_position: int,
                                  K: int) -> Dict[int, Dict[str, List[float]]]:
        """
        Calculate statistics for each read at each position in a condition.
        
        Args:
            aligned_condition: AlignedCondition object containing reads
            target_position: Center position
            K: Window size
            
        Returns:
            Dict mapping position -> stat_name -> list of values (one per read)
        """
        
        # Calculate positions
        half_window = K // 2
        positions = list(range(
            target_position - half_window,
            target_position + half_window + 1
        ))
        
        # Calculate stats for each position
        stats_by_position = {}
        for pos in positions:
            pos_stats = self._calculate_position_stats(aligned_reads, pos)
            stats_by_position[pos] = pos_stats
        
        return stats_by_position
    
    def _calculate_position_stats(self,
                                  reads: List[ReadAlignment],
                                  pos: int) -> Dict[str, List[float]]:
        """
        Calculate statistics for each read at a specific position.
        
        Returns:
            Dict[stat_name, List[values]] where each value is from one read
        """
        # Initialize result dict with proper type
        stats_dict = {self._get_stat_name(stat): [] 
                      for stat in self.statistics}
        
        # Track reads with valid signals
        reads_with_signal = 0
        
        # For each read
        for read in reads:
            # Get base at position
            pos_base = read.get_base_at_ref_pos(pos)
            
            if pos_base is not None and pos_base.has_signal:
                signal = pos_base.signal
                
                # Handle reversed reads
                if read.is_reversed:
                    signal = signal[::-1]
                
                reads_with_signal += 1
                
                # Calculate each statistic for THIS read's signal
                for stat in self.statistics:
                    stat_name = self._get_stat_name(stat)
                    stat_value = self._calculate_single_stat(signal, stat)
                    stats_dict[stat_name].append(stat_value)
        
        # Log warning if many reads have no signal at this position
        if reads_with_signal < len(reads) * 0.5 and len(reads) > 0:
            coverage_percent = (reads_with_signal / len(reads)) * 100
            print(f"Warning: Only {reads_with_signal}/{len(reads)} reads "
                  f"({coverage_percent:.1f}%) have signal at position {pos}")
            
        stats_dict = {k: np.array(v) for k,v in stats_dict.items()}
        
        return stats_dict
    
    def _calculate_single_stat(self,
                               signal: np.ndarray,
                               stat: Union[StatisticsFuncs, Callable]) -> float:
        """Calculate a single statistic on a signal."""
        try:
            if isinstance(stat, StatisticsFuncs):
                func = stat.to_function()
            else:
                func = stat
            
            result = func(signal)
            
            # Ensure it's a scalar float
            if isinstance(result, np.ndarray):
                result = float(result)
            
            return result
            
        except Exception as e:
            print(f"Warning: Failed to calculate {self._get_stat_name(stat)}: {e}")
            return np.nan
    
    def _get_stat_name(self, stat: Union[StatisticsFuncs, Callable]) -> str:
        """Get human-readable name for a statistic."""
        if isinstance(stat, StatisticsFuncs):
            return stat.value
        else:
            # Try to get function name
            if hasattr(stat, '__name__'):
                return stat.__name__
            else:
                return 'custom_stat'
    
    def get_summary(self, 
                    stats_by_position: Dict[int, Dict[str, List[float]]],
                    condition_label: Optional[str] = None) -> Dict:
        """
        Get summary of statistics across all positions.
        
        Args:
            stats_by_position: Output from calculate_condition_stats
            condition_label: Optional label for the condition
            
        Returns:
            Summary dictionary with aggregated statistics
        """
        summary = {
            'condition': condition_label or 'Unknown',
            'n_positions': len(stats_by_position),
            'positions': list(stats_by_position.keys()),
            'statistics': {}
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
                    all_values.extend(values)
                    
                    # Calculate mean for this position
                    if values:
                        position_means.append(np.mean(values))
            
            # Calculate summary statistics
            if all_values:
                summary['statistics'][stat_name] = {
                    'n_values': len(all_values),
                    'mean_across_all': float(np.mean(all_values)),
                    'std_across_all': float(np.std(all_values)),
                    'min': float(np.min(all_values)),
                    'max': float(np.max(all_values)),
                    'mean_of_position_means': float(np.mean(position_means)) if position_means else None,
                    'std_of_position_means': float(np.std(position_means)) if len(position_means) > 1 else None
                }
            else:
                summary['statistics'][stat_name] = {
                    'n_values': 0,
                    'message': 'No values calculated'
                }
        
        return summary
    
    @property
    def num_stats(self):
        if hasattr(self, 'statistics'):
            return len(self.statistics)
        return 0
    
    @property
    def stats_names(self):
        if hasattr(self, 'statistics'):
            return [self._get_stat_name(stat) for stat in self.statistics]
        return None