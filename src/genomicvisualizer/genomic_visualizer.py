import logging
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union, Literal, Any
from dataclasses import dataclass
from enum import IntEnum

from .utils import validate_files
from .utils import PlotStyle, ColorScheme

from .io_processor import DataProcessor
from .signal_visualizer import SignalVisualizer


class VerbosityLevel(IntEnum):
    """Define verbosity levels as constants."""
    SILENT = 0    # No output
    ERROR = 1     # Only errors
    WARNING = 2   # Errors and warnings
    INFO = 3      # Errors, warnings, and info (default)
    DEBUG = 4     # Everything including debug messages


class GenomicPositionVisualizer:
    """
    Main API that combines DataProcessor and SignalVisualizer.
    
    This provides a unified interface while maintaining separation of concerns.
    """
    
    def __init__(self,
                 K: int = 9,
                 kmer: Optional[List[Union[str, int]]] = None,
                 plot_style: Optional[PlotStyle] = None,
                 title: Optional[str] = None,
                 figsize: Optional[Tuple[float, float]] = None,
                 verbosity: VerbosityLevel = VerbosityLevel.SILENT,
                 logger: Optional[logging.Logger] = None):
        """
        Initialize the complete visualization system.
        
        Args:
            K: Window size (will be made odd if even)
            kmer: Optional k-mer labels
            plot_style: Style configuration for plots
            title: Optional plot title
            figsize: Figure size (width, height)
            verbosity: Logging verbosity level (0-4)
                0 = SILENT: No output
                1 = ERROR: Only errors
                2 = WARNING: Errors and warnings  
                3 = INFO: Errors, warnings, and info (default)
                4 = DEBUG: Everything including debug messages
            logger: Optional logger instance (overrides verbosity if provided)
        """
        # Setup logger with verbosity
        self.verbosity = verbosity
        self.logger = logger or self._setup_logger_with_verbosity(verbosity)
        
        # Create components with the same logger
        self.processor = DataProcessor(K, self.logger)
        self.visualizer = SignalVisualizer(
            self.processor.K,  # Use adjusted window size
            kmer,
            plot_style,
            title,
            figsize,
            self.logger
        )
        
        # For backward compatibility
        self.K = self.processor.K
        self.half_window = (K - 1) // 2
        self.style = self.visualizer.style
        self.fig = self.visualizer.fig
        self.ax = self.visualizer.ax
        self._extracted_conditions_map = self.processor._extracted_conditions_map
        self._plotted_conditions_map = self.visualizer._plotted_conditions_map
        
        self.logger.debug(f"Initialized GenomicPositionVisualizer with K={self.K}, verbosity={verbosity}")
    
    def set_verbosity(self, level: int):
        """
        Change verbosity level after initialization.
        
        Args:
            level: New verbosity level (0-4)
        """
        self.verbosity = level
        
        # Update logger level
        if hasattr(self.logger, 'setLevel'):
            log_level = self._verbosity_to_log_level(level)
            self.logger.setLevel(log_level)
            
            # Also update handler levels
            for handler in self.logger.handlers:
                handler.setLevel(log_level)
        
        self.logger.info(f"Verbosity level changed to {level}")
    
    def plot_condition(self,
                      bam_path: Union[str, Path],
                      pod5_path: Union[str, Path],
                      contig: str,
                      target_position: int,
                      read_ids: Optional[Union[Set[str], List[str]]] = None,
                      max_reads: Optional[int] = None,
                      exclude_reads_with_indels: bool = False,
                      label: Optional[str] = None,
                      color: Optional[Union[str, Tuple[float, float, float]]] = None,
                      alpha: Optional[float] = None,
                      line_width: Optional[float] = None,
                      line_style: Optional[str] = None) -> 'GenomicPositionVisualizer':
        """Process and plot reads from specified files."""
        
        self.logger.debug(f"Starting plot_condition for {contig}:{target_position}")
        
        # Check for validity of label
        if label is None:
            label = f"{contig}:{target_position}"
            self.logger.debug(f"Auto-generated label: {label}")
            
        if label in self._extracted_conditions_map:
            self.logger.error(f"Label '{label}' already exists")
            raise KeyError(f"Please provide a unique label that is not used before")

        # Process the data
        self.logger.info(f"Processing reads from {Path(bam_path).name} for condition '{label}'")
        
        aligned_reads = self.processor.process_reads(
            bam_path, pod5_path, label, contig, target_position,
            read_ids, max_reads,
            exclude_reads_with_indels
        )
        
        if aligned_reads:
            # Plot the processed group
            positions = list(range(
                target_position - self.half_window,
                target_position + self.half_window + 1
            ))
            
            self.logger.debug(f"Plotting {len(aligned_reads)} reads for positions {positions[0]}-{positions[-1]}")
                    
            self.visualizer.plot_reads(
                aligned_reads, positions, label, color, alpha, line_width, line_style
            )

            self.logger.info(f"Condition '{label}' plotted with {len(aligned_reads)} reads")
        else:
            self.logger.warning(f"No reads found for condition '{label}'")
        
        return self
    
    def highlight_position(self, window_idx: Optional[int] = None, 
                          color: str = 'red', alpha: float = 0.2) -> 'GenomicPositionVisualizer':
        """Highlight a position in the window."""
        self.logger.debug(f"Highlighting position {window_idx} with color={color}, alpha={alpha}")
        self.visualizer.highlight_position(window_idx, color, alpha)
        return self
    
    def add_annotation(self, window_idx: int, text: str, 
                      y_position: Optional[float] = None, **kwargs) -> 'GenomicPositionVisualizer':
        """Add text annotation."""
        self.logger.debug(f"Adding annotation '{text}' at position {window_idx}")
        self.visualizer.add_annotation(window_idx, text, y_position, **kwargs)
        return self
    
    def set_title(self, title: str) -> 'GenomicPositionVisualizer':
        """Set plot title."""
        self.logger.debug(f"Setting title: {title}")
        self.visualizer.set_title(title)
        return self
    
    def set_ylim(self, bottom: Optional[float] = None, 
                 top: Optional[float] = None) -> 'GenomicPositionVisualizer':
        """Set y-axis limits."""
        self.logger.debug(f"Setting y-axis limits: bottom={bottom}, top={top}")
        self.visualizer.set_ylim(bottom, top)
        return self
    
    def show(self):
        """Display the plot."""
        self.logger.info("Displaying plot")
        self.visualizer.show()
    
    def save(self, path: Union[str, Path], dpi: Optional[int] = None, 
             bbox_inches: str = 'tight', **kwargs):
        """Save the figure."""
        self.logger.info(f"Saving figure to {path}")
        self.visualizer.save(path, dpi, bbox_inches, **kwargs)
    
    def get_summary(self) -> Dict:
        """Get summary of all processed groups."""
        self.logger.debug("Getting summary")
        return self.processor.get_summary()
    
    def print_summary(self):
        """Print a formatted summary."""
        summary = self.get_summary()
        
        # Summary is always printed regardless of verbosity
        # unless verbosity is SILENT
        if self.verbosity > VerbosityLevel.SILENT:
            print("\n" + "="*60)
            print("Genomic Position Visualization Summary")
            print("="*60)
            print(f"Window Size: {summary['K']}")
            print(f"Groups Plotted: {summary['n_groups']}")
            print(f"Total Reads: {summary['total_reads']}")
            print("\nGroups:")
            for group in summary['groups']:
                print(f"  • {group['label']}: {group['n_reads']} reads from {group['contig']}:{group['position']}")
            print("="*60 + "\n")
    
    def _verbosity_to_log_level(self, verbosity: int) -> int:
        """Convert verbosity level to logging level."""
        level_map = {
            VerbosityLevel.SILENT: logging.CRITICAL + 10,  # Higher than CRITICAL
            VerbosityLevel.ERROR: logging.ERROR,
            VerbosityLevel.WARNING: logging.WARNING,
            VerbosityLevel.INFO: logging.INFO,
            VerbosityLevel.DEBUG: logging.DEBUG
        }
        return level_map.get(verbosity, logging.INFO)
    
    def _setup_logger_with_verbosity(self, verbosity: int) -> logging.Logger:
        """Set up a logger with the specified verbosity level."""
        logger = logging.getLogger(f"{__name__}.{id(self)}")  # Unique logger per instance
        logger.handlers.clear()  # Clear any existing handlers
        
        # Set logger level based on verbosity
        log_level = self._verbosity_to_log_level(verbosity)
        logger.setLevel(log_level)
        
        # Create handler only if not SILENT
        if verbosity > VerbosityLevel.SILENT:
            handler = logging.StreamHandler()
            handler.setLevel(log_level)
            
            # Create formatter with different formats based on verbosity
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
        
        # Prevent propagation to root logger
        logger.propagate = False
        
        return logger
    
    def _setup_default_logger(self) -> logging.Logger:
        """Set up a default logger (for backward compatibility)."""
        return self._setup_logger_with_verbosity(VerbosityLevel.INFO)