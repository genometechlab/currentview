import logging
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union, Literal, Any, Callable
from dataclasses import dataclass, field
from enum import IntEnum
from collections import OrderedDict

from .utils import validate_files
from .utils import ReadAlignment, PlotStyle, ColorScheme, Condition

from .io_processor import DataProcessor
from .signal_visualizer import SignalVisualizer
from .stats_visualizer import StatsVisualizer
from .stats import StatsCalculator


class VerbosityLevel(IntEnum):
    """Define verbosity levels as constants."""
    SILENT = 0    # No output
    ERROR = 1     # Only errors
    WARNING = 2   # Errors and warnings
    INFO = 3      # Errors, warnings, and info (default)
    DEBUG = 4     # Everything including debug messages


class GenomicPositionVisualizer:
    """
    Visualize nanopore signals at specific genomic positions.
    
    This class provides a unified interface for processing and visualizing
    nanopore sequencing data, with optional statistical analysis.
    
    Examples:
        Basic usage:
        >>> viz = GenomicPositionVisualizer(K=9)
        >>> viz.add_condition("sample.bam", "sample.pod5", "chr1", 12345)
        >>> viz.show()
        
        With statistics:
        >>> viz = GenomicPositionVisualizer(K=9, stats=['mean', 'std'])
        >>> viz.add_condition("control.bam", "control.pod5", "chr1", 12345, label="Control")
        >>> viz.add_condition("treatment.bam", "treatment.pod5", "chr1", 12345, label="Treatment")
        >>> viz.show_signals()
        >>> viz.show_stats()
        
        Method chaining:
        >>> (viz.add_condition("sample.bam", "sample.pod5", "chr1", 12345)
        ...     .highlight_position(4)
        ...     .set_title("My Analysis")
        ...     .show())
    """
    
    def __init__(self,
                 K: int = 9,
                 kmer: Optional[List[Union[str, int]]] = None,
                 stats: Optional[List[Union[str, Callable]]] = None,
                 plot_style: Optional[PlotStyle] = None,
                 title: Optional[str] = None,
                 figsize: Optional[Tuple[float, float]] = None,
                 verbosity: Union[VerbosityLevel, int] = VerbosityLevel.SILENT,
                 logger: Optional[logging.Logger] = None):
        """
        Initialize the visualization system.
        
        Args:
            K: Window size around the target position (will be made odd if even)
            kmer: Optional custom labels for each position in the window
            stats: Optional list of statistics to calculate. Can be:
                   - String names: 'mean', 'median', 'std', 'variance', 'min', 'max', 'skewness', 'kurtosis'
                   - StatisticsFuncs enum values
                   - Custom callable functions that take a numpy array and return a float
            plot_style: Style configuration for plots
            title: Default title for plots
            figsize: Figure size as (width, height) in inches
            verbosity: Logging verbosity level (0-4 or VerbosityLevel enum)
            logger: Optional custom logger (overrides verbosity if provided)
        """
        # Setup logger
        self.verbosity = VerbosityLevel(verbosity) if isinstance(verbosity, int) else verbosity
        self.logger = logger or self._setup_logger_with_verbosity(self.verbosity)
        
        # Create data processor (handles K adjustment)
        self.processor = DataProcessor(K, self.logger)
        self.K = self.processor.K  # Use adjusted K
        self.half_window = (self.K - 1) // 2
        
        # Initialize statistics if requested
        self.stats_calculator = None
        self._stats_enabled = stats is not None
        self._stats_names = []
        
        if self._stats_enabled:
            self.logger.debug(f"Initializing statistics with {len(stats)} functions")
            self.stats_calculator = StatsCalculator(stats)
            # Extract stat names for display
            self._stats_names = self.stats_calculator.stats_names
            # Extract number of stats
            self._n_stats = self.stats_calculator.num_stats
        
        # Store visualization parameters
        self.kmer = kmer
        self.plot_style = plot_style or PlotStyle()
        self.title = title
        self.figsize = figsize
        
        # Lazy-initialized visualizers
        self._signal_viz = None
        self._stats_viz = None
        
        # Store processed conditions
        self._conditions: OrderedDict[str, Condition] = OrderedDict()
        
        # Track visualization state
        self._signal_viz_dirty = True
        self._stats_viz_dirty = True
        
        # Track modifications to apply to visualizers
        self._pending_modifications = []
        
        self.logger.debug(f"Initialized GenomicPositionVisualizer: K={self.K}, "
                         f"stats={self._stats_names if self._stats_enabled else 'disabled'}, "
                         f"verbosity={verbosity}")
    
    def add_condition(self,
                      bam_path: Union[str, Path],
                      pod5_path: Union[str, Path],
                      contig: str,
                      target_position: int,
                      *,  # Force keyword-only arguments after this
                      target_base: Optional[str] = None,
                      read_ids: Optional[Union[Set[str], List[str]]] = None,
                      max_reads: Optional[int] = None,
                      exclude_reads_with_indels: bool = False,
                      label: Optional[str] = None,
                      color: Optional[Union[str, Tuple[float, float, float]]] = None,
                      alpha: Optional[float] = None,
                      line_width: Optional[float] = None,
                      line_style: Optional[str] = None) -> 'GenomicPositionVisualizer':
        """
        Add and process a new condition.
        
        This method processes sequencing data from BAM and POD5 files and stores it
        for visualization. Multiple conditions can be added for comparison.
        
        Args:
            bam_path: Path to BAM alignment file
            pod5_path: Path to POD5 signal file
            contig: Chromosome/contig name (e.g., 'chr1', 'chrX')
            target_position: Genomic position of interest (1-based)
            target_base: Expected base at target position (for validation)
            read_ids: Specific read IDs to include (None = all reads)
            max_reads: Maximum number of reads to process
            exclude_reads_with_indels: Whether to exclude reads with insertions/deletions
            label: Display label for this condition (auto-generated if None)
            color: Plot color (auto-assigned if None)
            alpha: Transparency (0-1, auto-calculated based on read count if None)
            line_width: Line width for signal plots
            line_style: Line style ('-', '--', ':', '-.')
            
        Returns:
            self for method chaining
            
        Raises:
            KeyError: If a condition with the same label already exists
            FileNotFoundError: If BAM or POD5 files don't exist
            
        Examples:
            >>> viz.add_condition("sample.bam", "sample.pod5", "chr1", 12345)
            >>> viz.add_condition("control.bam", "control.pod5", "chr1", 12345, 
            ...                   label="Control", color="blue", max_reads=100)
        """
        # Step 1: Process the data
        processed_data = self._process_condition_data(
            bam_path=bam_path,
            pod5_path=pod5_path,
            contig=contig,
            target_position=target_position,
            target_base=target_base,
            read_ids=read_ids,
            max_reads=max_reads,
            exclude_reads_with_indels=exclude_reads_with_indels,
            label=label
        )
        
        if processed_data:
            # Step 2: Store the condition with visualization parameters
            self._store_condition(
                processed_data=processed_data,
                color=color,
                alpha=alpha,
                line_width=line_width,
                line_style=line_style
            )
            
            # Step 3: Mark visualizations as needing update
            self._mark_for_update()
            
            self.logger.info(f"Successfully added condition '{processed_data['label']}' "
                           f"with {len(processed_data['reads'])} reads")
        
        return self
    
    # Convenience method with cleaner name
    def add(self, *args, **kwargs) -> 'GenomicPositionVisualizer':
        """Alias for add_condition() with shorter name."""
        return self.add_condition(*args, **kwargs)
    
    def show(self):
        """Display the signal plot (convenience method)."""
        self.show_signals()
    
    def show_signals(self):
        """
        Display the signal visualization.
        
        Creates and displays a plot showing signal traces for all added conditions.
        The plot includes position barriers, reference bases, and a legend.
        
        Raises:
            RuntimeError: If no conditions have been added
        """
        if not self._conditions:
            raise RuntimeError("No conditions to display. Use add_condition() first.")
        
        self.logger.info("Displaying signal plot")
        self._ensure_signal_viz()
        self._signal_viz.show()
    
    def show_stats(self):
        """
        Display the stats visualization.
        
        Creates and displays a plot showing signal traces for all added conditions.
        The plot includes position barriers, reference bases, and a legend.
        
        Raises:
            RuntimeError: If no conditions have been added
        """
        if not self._stats_enabled:
            self.logger.warning(f"No stats is provided to the visualizer")
            return
        if not self._conditions:
            raise RuntimeError("No conditions to display. Use add_condition() first.")
        
        self.logger.info("Displaying stats plot")
        self._ensure_stats_viz()
        self._stats_viz.show()
    
    def save(self, *args, **kwargs):
        """
        Save the signal figure to file.
        
        Args:
            path: Output file path (format determined by extension)
            dpi: Resolution in dots per inch (uses style default if None)
            bbox_inches: How to handle the bounding box ('tight' removes extra whitespace)
            **kwargs: Additional arguments passed to matplotlib.savefig()
        """
        self.save_signals(*args, **kwargs)      

    
    def save_signals(self, path: Union[str, Path], *, dpi: Optional[int] = None, 
                     bbox_inches: str = 'tight', **kwargs):
        """Save the signal figure (explicit method name)."""  
        if not self._conditions:
            raise RuntimeError("No conditions to save. Use add_condition() first.")
        
        self.logger.info(f"Saving signal figure to {path}")
        self._ensure_signal_viz()
        self._signal_viz.save(path, dpi, bbox_inches, **kwargs)
    
    def save_stats(self, path: Union[str, Path], *, dpi: Optional[int] = None, 
                   bbox_inches: str = 'tight', **kwargs):
        """
        Save statistics visualization to file.
        
        Args:
            path: Output file path
            dpi: Resolution in dots per inch
            bbox_inches: How to handle the bounding box ('tight' removes extra whitespace)
            **kwargs: Additional arguments passed to savefig
        """
        if not self._stats_enabled:
            return
        
        if not self._conditions:
            raise RuntimeError("No conditions to save.")
        
        self.logger.info(f"Saving signal figure to {path}")
        self._ensure_signal_viz()
        self._signal_viz.save(path, dpi, bbox_inches, **kwargs)
    
    def highlight_position(self, window_idx: Optional[int] = None, *,
                          color: str = 'red', alpha: float = 0.2) -> 'GenomicPositionVisualizer':
        """
        Highlight a position in the window.
        
        Args:
            window_idx: Position index in window (0 to K-1). None = center position
            color: Highlight color
            alpha: Transparency (0-1)
            
        Returns:
            self for method chaining
        """
        if window_idx is None:
            window_idx = self.K // 2
        
        if not 0 <= window_idx < self.K:
            raise ValueError(f"window_idx must be between 0 and {self.K-1}, got {window_idx}")
        
        self.logger.debug(f"Highlighting position {window_idx} with color={color}, alpha={alpha}")
        
        # Apply immediately if viz exists, otherwise queue
        if self._signal_viz and not self._signal_viz_dirty:
            self._signal_viz.highlight_position(window_idx, color, alpha)
        else:
            self._pending_modifications.append(
                ('highlight_position', (window_idx,), {'color': color, 'alpha': alpha})
            )
        
        return self
    
    def highlight_center(self, **kwargs) -> 'GenomicPositionVisualizer':
        """Highlight the center position (convenience method)."""
        return self.highlight_position(None, **kwargs)
    
    def add_annotation(self, window_idx: int, text: str, *,
                      y_position: Optional[float] = None, **kwargs) -> 'GenomicPositionVisualizer':
        """
        Add text annotation at a specific position.
        
        Args:
            window_idx: Position index in window (0 to K-1)
            text: Annotation text
            y_position: Y-coordinate for annotation (auto-calculated if None)
            **kwargs: Additional arguments passed to matplotlib.annotate()
            
        Returns:
            self for method chaining
        """
        if not 0 <= window_idx < self.K:
            raise ValueError(f"window_idx must be between 0 and {self.K-1}, got {window_idx}")
        
        self.logger.debug(f"Adding annotation '{text}' at position {window_idx}")
        
        if self._signal_viz and not self._signal_viz_dirty:
            self._signal_viz.add_annotation(window_idx, text, y_position, **kwargs)
        else:
            self._pending_modifications.append(
                ('add_annotation', (window_idx, text), {'y_position': y_position, **kwargs})
            )
        
        return self
    
    def set_title(self, title: str) -> 'GenomicPositionVisualizer':
        """Set plot title."""
        self.logger.debug(f"Setting title: {title}")
        self.title = title
        
        if self._signal_viz:
            self._signal_viz.set_title(title)
        
        return self
    
    def set_ylim(self, bottom: Optional[float] = None, 
                 top: Optional[float] = None) -> 'GenomicPositionVisualizer':
        """Set y-axis limits for signal plot."""
        self.logger.debug(f"Setting y-axis limits: bottom={bottom}, top={top}")
        
        if self._signal_viz and not self._signal_viz_dirty:
            self._signal_viz.set_ylim(bottom, top)
        else:
            self._pending_modifications.append(
                ('set_ylim', (), {'bottom': bottom, 'top': top})
            )
        
        return self
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive summary of all processed conditions.
        
        Returns:
            Dictionary containing:
            - K: Window size
            - n_conditions: Number of conditions
            - total_reads: Total reads across all conditions
            - stats_enabled: Whether statistics are enabled
            - stats_names: List of statistic names (if enabled)
            - conditions: List of condition summaries
        """
        self.logger.debug("Getting summary")
        
        summary = {
            'K': self.K,
            'n_conditions': len(self._conditions),
            'total_reads': sum(cond.n_reads for cond in self._conditions.values()),
            'stats_enabled': self._stats_enabled,
            'stats_names': self._stats_names if self._stats_enabled else [],
            'conditions': []
        }
        
        for cond in self._conditions.values():
            cond_info = {
                'label': cond.label,
                'genomic_location': cond.genomic_location,
                'n_reads': cond.n_reads,
                'bam_file': str(cond.bam_path),
                'pod5_file': str(cond.pod5_path)
            }
            
            if cond.stats and self.stats_calculator:
                cond_info['stats_summary'] = self.stats_calculator.get_summary(
                    cond.stats, cond.label
                )
            
            summary['conditions'].append(cond_info)
        
        return summary
    
    def print_summary(self):
        """Print a formatted summary to console."""
        summary = self.get_summary()
        
        if self.verbosity > VerbosityLevel.SILENT:
            print("\n" + "="*60)
            print("Genomic Position Visualization Summary")
            print("="*60)
            print(f"Window Size: {summary['K']} bases")
            print(f"Conditions: {summary['n_conditions']}")
            print(f"Total Reads: {summary['total_reads']:,}")
            
            if summary['stats_enabled']:
                print(f"Statistics: {', '.join(summary['stats_names'])}")
            else:
                print("Statistics: Disabled")
            
            if summary['conditions']:
                print("\nConditions:")
                for i, cond in enumerate(summary['conditions'], 1):
                    print(f"  {i}. {cond['label']}:")
                    print(f"     - Location: {cond['genomic_location']}")
                    print(f"     - Reads: {cond['n_reads']:,}")
                    print(f"     - BAM: {Path(cond['bam_file']).name}")
                    print(f"     - POD5: {Path(cond['pod5_file']).name}")
            
            print("="*60 + "\n")
    
    def clear(self) -> 'GenomicPositionVisualizer':
        """Clear all conditions and reset visualizations."""
        self.logger.info("Clearing all conditions")
        
        # Clear data
        self._conditions.clear()
        
        # Clear visualizer if it exists
        if self._signal_viz:
            self._signal_viz.clear_conditions()
            self._signal_viz.clear_highlights()
            self._signal_viz.clear_annotations()
        
        # Reset stats viz
        self._stats_viz = None
        
        # Mark as dirty
        self._signal_viz_dirty = True
        self._stats_viz_dirty = True
        self._pending_modifications.clear()
        
        return self
    
    def remove_condition(self, label: str) -> 'GenomicPositionVisualizer':
        """
        Remove a specific condition by label.
        
        Args:
            label: Label of the condition to remove
            
        Returns:
            self for method chaining
            
        Raises:
            KeyError: If condition with given label doesn't exist
        """
        if label not in self._conditions:
            raise KeyError(f"Condition '{label}' not found. "
                          f"Available: {list(self._conditions.keys())}")
        
        self.logger.info(f"Removing condition '{label}'")
        
        # Remove from data
        del self._conditions[label]
        
        # Remove from visualizer if it exists
        if self._signal_viz and self._signal_viz.has_condition(label):
            self._signal_viz.remove_condition(label)
        else:
            # Mark as dirty to update on next display
            self._signal_viz_dirty = True
        
        # Mark stats as dirty
        self._stats_viz_dirty = True
        
        return self
    
    def get_condition_names(self) -> List[str]:
        """Get list of all condition labels."""
        return list(self._conditions.keys())
    
    def get_condition(self, label: str) -> Condition:
        """
        Get a specific condition by label.
        
        Args:
            label: Condition label
            
        Returns:
            Condition object
            
        Raises:
            KeyError: If condition not found
        """
        if label not in self._conditions:
            raise KeyError(f"Condition '{label}' not found")
        return self._conditions[label]
    
    @property
    def n_conditions(self) -> int:
        """Number of conditions added."""
        return len(self._conditions)
    
    @property
    def has_conditions(self) -> bool:
        """Whether any conditions have been added."""
        return len(self._conditions) > 0
    
    # Internal methods with clear separation of concerns
    
    def _process_condition_data(self, 
                               bam_path: Union[str, Path],
                               pod5_path: Union[str, Path],
                               contig: str,
                               target_position: int,
                               target_base: Optional[str],
                               read_ids: Optional[Union[Set[str], List[str]]],
                               max_reads: Optional[int],
                               exclude_reads_with_indels: bool,
                               label: Optional[str]) -> Optional[Dict[str, Any]]:
        """Process condition data (pure data processing, no visualization)."""
        # Convert paths
        bam_path = Path(bam_path)
        pod5_path = Path(pod5_path)
        
        # Generate label if needed
        if label is None:
            label = f"{contig}:{target_position}"
            self.logger.debug(f"Auto-generated label: {label}")
        
        # Check for duplicates
        if label in self._conditions:
            raise KeyError(f"Condition '{label}' already exists. "
                          f"Please use a unique label or remove the existing condition first.")
        
        # Process reads
        self.logger.info(f"Processing reads from {bam_path.name} for condition '{label}'")
        
        aligned_reads = self.processor.process_reads(
            bam_path, pod5_path, label, contig, target_position, target_base,
            read_ids, max_reads, exclude_reads_with_indels
        )
        
        if not aligned_reads:
            self.logger.warning(f"No reads found for condition '{label}'")
            return None
        
        # Calculate positions
        positions = list(range(
            target_position - self.half_window,
            target_position + self.half_window + 1
        ))
        
        # Calculate statistics if enabled
        condition_stats = None
        if self._stats_enabled and self.stats_calculator:
            self.logger.debug(f"Calculating statistics for condition '{label}'")
            condition_stats = self.stats_calculator.calculate_condition_stats(
                aligned_reads=aligned_reads,
                target_position=target_position,
                K=self.K
            )
        
        return {
            'label': label,
            'reads': aligned_reads,
            'positions': positions,
            'contig': contig,
            'target_position': target_position,
            'bam_path': bam_path,
            'pod5_path': pod5_path,
            'stats': condition_stats
        }
    
    def _store_condition(self,
                        processed_data: Dict[str, Any],
                        color: Optional[Any],
                        alpha: Optional[float],
                        line_width: Optional[float],
                        line_style: Optional[str]):
        """Store processed condition with visualization parameters."""
        condition = Condition(
            **processed_data,
            color=color,
            alpha=alpha,
            line_width=line_width,
            line_style=line_style
        )
        
        self._conditions[processed_data['label']] = condition
        self.logger.debug(f"Stored condition '{processed_data['label']}' with "
                         f"{condition.n_reads} reads")
    
    def _mark_for_update(self):
        """Mark visualizations as needing update."""
        self._signal_viz_dirty = True
        self._stats_viz_dirty = True
    
    def _ensure_signal_viz(self):
        """Ensure signal visualizer is created and up to date."""
        if self._signal_viz is None:
            # First time - create new visualizer
            self.logger.debug("Creating signal visualizer")
            
            self._signal_viz = SignalVisualizer(
                self.K,
                self.kmer,
                self.plot_style,
                self.title,
                self.figsize,
                self.logger
            )
            
        if self._signal_viz_dirty:
            # Update existing visualizer
            self.logger.debug("Updating signal visualizer")
            
            # Get currently plotted labels
            current_labels = self._signal_viz.get_plotted_labels()
            desired_labels = self._conditions.keys()
            
            # Remove conditions that shouldn't be there
            to_remove = [label for label in current_labels if label not in desired_labels]
            for label in to_remove:
                self.logger.debug(f"Removing condition '{label}' from plot")
                self._signal_viz.remove_condition(label)
            
            # Add or update conditions
            for label in desired_labels:
                cond = self._conditions[label]
                if label not in current_labels:
                    self.logger.debug(f"Adding condition '{label}' to plot")
                else:
                    self.logger.debug(f"Updating condition '{label}' in plot")
                self._signal_viz.plot_condition(cond)
            
            # Apply any pending modifications
            for method_name, args, kwargs in self._pending_modifications:
                method = getattr(self._signal_viz, method_name)
                method(*args, **kwargs)
            
            self._pending_modifications.clear()
            self._signal_viz_dirty = False
    
    def _ensure_stats_viz(self):
        """Ensure statistics visualizer is created and up to date."""
        if self._stats_viz is None:
            # First time - create new visualizer
            self.logger.debug("Creating signal visualizer")
            
            self._stats_viz = StatsVisualizer(
                self.K,
                self._n_stats,
                self.kmer,
                self._stats_names,
                self.plot_style,
                self.title,
                self.figsize,
                self.logger
            )

        if self._stats_viz_dirty:
            # Update existing visualizer
            self.logger.debug("Updating signal visualizer")
            
            # Get currently plotted labels
            current_labels = self._stats_viz.get_plotted_labels()
            desired_labels = self._conditions.keys()
            
            # Remove conditions that shouldn't be there
            to_remove = [label for label in current_labels if label not in desired_labels]
            for label in to_remove:
                self.logger.debug(f"Removing condition '{label}' from plot")
                self._stats_viz.remove_condition(label)
            
            # Add or update conditions
            for label in desired_labels:
                cond = self._conditions[label]
                if label not in current_labels:
                    self.logger.debug(f"Adding condition '{label}' to plot")
                else:
                    self.logger.debug(f"Updating condition '{label}' in plot")
                self._stats_viz.plot_condition(cond)
            
            self._pending_modifications.clear()
            self._stats_viz_dirty = False

    
    # Backward compatibility properties
    
    @property
    def style(self):
        """Get plot style (backward compatibility)."""
        return self.plot_style
    
    @property
    def _extracted_conditions_map(self):
        """Get extracted conditions (backward compatibility)."""
        return self.processor._extracted_conditions_map
    
    @property
    def _plotted_conditions_map(self):
        """Get plotted conditions (backward compatibility)."""
        if self._signal_viz:
            return self._signal_viz._plotted_conditions_map
        return {}
    
    # Verbosity and logging methods
    
    def set_verbosity(self, level: Union[VerbosityLevel, int]):
        """
        Change verbosity level after initialization.
        
        Args:
            level: New verbosity level (0-4 or VerbosityLevel enum)
        """
        self.verbosity = VerbosityLevel(level) if isinstance(level, int) else level
        
        if hasattr(self.logger, 'setLevel'):
            log_level = self._verbosity_to_log_level(self.verbosity)
            self.logger.setLevel(log_level)
            
            for handler in self.logger.handlers:
                handler.setLevel(log_level)
        
        self.logger.info(f"Verbosity level changed to {self.verbosity.name}")
    
    def _verbosity_to_log_level(self, verbosity: VerbosityLevel) -> int:
        """Convert verbosity level to logging level."""
        level_map = {
            VerbosityLevel.SILENT: logging.CRITICAL + 10,
            VerbosityLevel.ERROR: logging.ERROR,
            VerbosityLevel.WARNING: logging.WARNING,
            VerbosityLevel.INFO: logging.INFO,
            VerbosityLevel.DEBUG: logging.DEBUG
        }
        return level_map.get(verbosity, logging.INFO)
    
    def _setup_logger_with_verbosity(self, verbosity: VerbosityLevel) -> logging.Logger:
        """Set up a logger with the specified verbosity level."""
        logger = logging.getLogger(f"{__name__}.{id(self)}")
        logger.handlers.clear()
        
        log_level = self._verbosity_to_log_level(verbosity)
        logger.setLevel(log_level)
        
        if verbosity > VerbosityLevel.SILENT:
            handler = logging.StreamHandler()
            handler.setLevel(log_level)
            
            if verbosity >= VerbosityLevel.DEBUG:
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
                    datefmt='%H:%M:%S'
                )
            else:
                formatter = logging.Formatter(
                    '%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%H:%M:%S'
                )
            
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        logger.propagate = False
        return logger