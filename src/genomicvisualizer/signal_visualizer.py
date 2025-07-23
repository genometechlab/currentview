import logging
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union, Literal, Any
from dataclasses import dataclass
from collections import OrderedDict

from .readers import AlignmentExtractor
from .readers import SignalExtractor
from .utils import ReadAlignment, PlottedCondition
from .utils import validate_files
from .utils import PlotStyle, ColorScheme

class SignalVisualizer:
    """Handles all plotting, visualization, and figure management."""
    
    def __init__(self,
                 K: int,
                 window_labels: Optional[List[Union[str, int]]] = None,
                 plot_style: Optional[PlotStyle] = None,
                 title: Optional[str] = None,
                 figsize: Optional[Tuple[float, float]] = None,
                 logger: Optional[logging.Logger] = None):
        """
        Initialize the visualizer.
        
        Args:
            K: Number of bases to show
            window_labels: Optional custom labels for x-axis
            plot_style: Optional PlotStyle configuration
            title: Optional custom title
            figsize: Optional figure size override
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        self.logger.debug(f"Initializing SignalVisualizer with K={K}")
        
        self.K = K
        self.window_labels = window_labels
        
        # Setup style
        self.style = plot_style or PlotStyle()
        if figsize:
            self.logger.debug(f"Overriding figsize from {self.style.figsize} to {figsize}")
            self.style.figsize = figsize
        
        # Initialize colors
        self.logger.debug("Initializing color palette")
        self._init_colors()
        
        # Create figure
        self.logger.debug(f"Creating figure with size {self.style.figsize}")
        self.fig, self.ax = self._create_figure(title)
        
        # Add position barriers
        self.logger.debug("Adding position barriers")
        self._add_position_barriers()
        
        # Apply custom labels if provided
        if window_labels:
            self.logger.debug(f"Applying custom window labels: {window_labels}")
            self._apply_custom_labels()
        
        # Track plotting state
        self._plot_count = 0
        self._plotted_conditions_map: Dict[str, PlottedCondition] = OrderedDict()
        
        self.logger.info(f"Initialized SignalVisualizer with K={K}, style={self.style.color_scheme.value}")
    
    def plot_reads(self,
                   reads: List[ReadAlignment],
                   positions: List[int],
                   label: Optional[str] = None,
                   color: Optional[Any] = None,
                   alpha: Optional[float] = None,
                   line_width: Optional[float] = None,
                   line_style: Optional[str] = None):
        """Plot a processed group of reads."""
        self.logger.debug(f"plot_reads called: label='{label}', n_reads={len(reads)}, positions={positions[0]}-{positions[-1]}")
        
        # Assign color if not specified
        if color is None:
            color = self._get_next_color()
            self.logger.debug(f"Auto-assigned color for plot group {self._plot_count}")

        if alpha is None:
            if self.style.alpha_mode=='fixed':
                alpha = self.style.fixed_alpha
            elif self.style.alpha_mode=='auto':
                alpha = self._calculate_alpha(len(reads))
        
        # Extract reference bases
        self.logger.debug("Extracting reference bases for k-mer labels")
        kmer_dict = self._extract_reference_bases(positions, reads)
        position_labels = [f"{pos} - {kmer_dict[pos]}" for pos in positions]
        
        # Log k-mer if in debug mode
        if self.logger.isEnabledFor(logging.DEBUG):
            kmer_seq = ''.join(kmer_dict[p] for p in positions)
            self.logger.debug(f"Reference k-mer: {kmer_seq}")

        # Use style defaults
        line_width = line_width or self.style.line_width
        line_style = line_style or self.style.line_style

        # Store plotted condition
        self.logger.debug(f"Storing plotted condition '{label}'")
        self._plotted_conditions_map[label] = PlottedCondition(
            label=label,
            color=color,
            alpha=alpha,
            line_width=line_width,
            line_style=line_style,
            xticklabels=position_labels,
        )
        
        # Update x-axis labels
        if not self.window_labels:
            self.logger.debug("Updating position labels on x-axis")
            self._update_position_labels()
        
        # Plot the reads
        self.logger.info(f"Plotting {len(reads)} reads for condition '{label}'")
        self._plot_reads(
            reads,
            positions,
            color=color,
            alpha=alpha,
            line_width=line_width,
            line_style=line_style
        )
        
        # Update legend
        self.logger.debug("Updating legend")
        self._update_legend()
        
        self._plot_count += 1
        self.logger.debug(f"Plot count incremented to {self._plot_count}")
    
    def highlight_position(self,
                          window_idx: Optional[int] = None,
                          color: str = 'red',
                          alpha: float = 0.2) -> 'SignalVisualizer':
        """Highlight a position in the window."""
        if window_idx is None:
            window_idx = self.K // 2  # Center position
            self.logger.debug(f"Using center position {window_idx} for highlighting")
        
        self.logger.debug(f"Highlighting position {window_idx} with color={color}, alpha={alpha}")
        
        self.ax.axvspan(
            window_idx - self.style.padding / 2,
            window_idx + 1 - self.style.padding / 2,
            alpha=alpha,
            color=color,
            zorder=0
        )
        
        self.logger.info(f"Highlighted window position {window_idx}")
        return self
    
    def add_annotation(self,
                      window_idx: int,
                      text: str,
                      y_position: Optional[float] = None,
                      **kwargs) -> 'SignalVisualizer':
        """Add text annotation at a specific position."""
        if window_idx is None:
            window_idx = self.K // 2
            self.logger.debug(f"Using center position {window_idx} for annotation")
        
        x_pos = window_idx + 0.5 - self.style.padding / 2
        
        if y_position is None:
            y_lim = self.ax.get_ylim()
            y_position = y_lim[1] * 0.95
            self.logger.debug(f"Auto-calculated y_position: {y_position} (95% of y_max={y_lim[1]})")
        
        self.logger.debug(f"Adding annotation '{text}' at position ({x_pos}, {y_position})")
        
        default_kwargs = {
            'ha': 'center',
            'va': 'top',
            'fontsize': self.style.tick_labelsize,
            'bbox': dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7)
        }
        default_kwargs.update(kwargs)
        
        self.ax.annotate(text, xy=(x_pos, y_position), **default_kwargs)
        
        self.logger.info(f"Added annotation '{text}' at window position {window_idx}")
        return self
    
    def set_title(self, title: str) -> 'SignalVisualizer':
        """Set or update the plot title."""
        self.logger.debug(f"Setting plot title: '{title}'")
        self.ax.set_title(title, fontsize=self.style.title_fontsize, pad=10)
        return self
    
    def set_ylim(self, bottom: Optional[float] = None, top: Optional[float] = None) -> 'SignalVisualizer':
        """Set y-axis limits."""
        self.logger.debug(f"Setting y-axis limits: bottom={bottom}, top={top}")
        self.ax.set_ylim(bottom, top)
        
        # Log actual limits after setting
        if self.logger.isEnabledFor(logging.DEBUG):
            actual_ylim = self.ax.get_ylim()
            self.logger.debug(f"Actual y-axis limits: {actual_ylim}")
        
        return self
    
    def show(self):
        """Display the plot."""
        self.logger.info("Displaying plot")
        plt.show()
    
    def save(self, 
             path: Union[str, Path],
             dpi: Optional[int] = None,
             bbox_inches: str = 'tight',
             **kwargs):
        """Save the figure to file."""
        save_dpi = dpi or self.style.dpi
        self.logger.debug(f"Saving figure: path={path}, dpi={save_dpi}, bbox_inches={bbox_inches}")
        
        try:
            self.fig.savefig(path, dpi=save_dpi, bbox_inches=bbox_inches, **kwargs)
            self.logger.info(f"Saved figure to {path}")
        except Exception as e:
            self.logger.error(f"Failed to save figure: {type(e).__name__}: {str(e)}")
            raise
    
    def _init_colors(self):
        """Initialize the color palette."""
        scheme = self.style.color_scheme.value
        self.logger.debug(f"Initializing color scheme: {scheme}")
        
        if scheme == "tab10":
            self.colors = plt.cm.tab10
        elif scheme in ["viridis", "plasma", "inferno"]:
            cmap = plt.get_cmap(scheme)
            self.colors = lambda i: cmap(i / 10)
        else:
            self.colors = plt.cm.get_cmap(scheme)
        
        self.logger.debug(f"Color palette initialized with scheme '{scheme}'")
    
    def _get_next_color(self):
        """Get the next color from the palette."""
        color_index = self._plot_count % 10
        color = self.colors(color_index)
        self.logger.debug(f"Getting color {color_index} from palette")
        return color
    
    def _create_figure(self, title: Optional[str] = None) -> Tuple[plt.Figure, plt.Axes]:
        """Create and configure the matplotlib figure."""
        self.logger.debug("Creating matplotlib figure")
        
        fig = plt.figure(figsize=self.style.figsize, dpi=self.style.dpi)
        ax = fig.add_subplot(111)
        
        # Set title
        if title is None:
            title = 'Nanopore Signal Visualization'
        self.logger.debug(f"Setting initial title: '{title}'")
        ax.set_title(title, fontsize=self.style.title_fontsize, pad=10)
        
        # Configure axes
        ax.set_xlabel('Genomic Position', fontsize=self.style.label_fontsize)
        ax.set_ylabel('Signal (pA)', fontsize=self.style.label_fontsize)
        
        # Configure spines
        all_spines = ['top', 'bottom', 'left', 'right']
        hidden_spines = [s for s in all_spines if s not in self.style.show_spines]
        if hidden_spines:
            self.logger.debug(f"Hiding spines: {hidden_spines}")
        for spine in all_spines:
            if spine not in self.style.show_spines:
                ax.spines[spine].set_visible(False)
        
        # Configure grid
        if self.style.show_grid:
            self.logger.debug(f"Enabling grid with alpha={self.style.grid_alpha}")
            ax.grid(True, alpha=self.style.grid_alpha, axis='y')
        
        # Set tick label sizes
        ax.tick_params(axis='both', labelsize=self.style.tick_labelsize)
        
        self.logger.debug(f"Figure created: size={self.style.figsize}, dpi={self.style.dpi}")
        return fig, ax
    
    def _add_position_barriers(self):
        """Add vertical lines to separate positions."""
        self.logger.debug(f"Adding {self.K + 1} position barriers")
        
        for i in range(self.K + 1):
            x_pos = i - self.style.padding / 2
            self.ax.axvline(
                x=x_pos,
                alpha=self.style.position_barrier_alpha,
                linestyle=self.style.position_barrier_style,
                color=self.style.position_barrier_color,
                linewidth=1.5,
                zorder=0
            )
        
        # Set x-axis limits
        x_limits = (-0.1, self.K - self.style.padding + 0.1)
        self.ax.set_xlim(x_limits)
        self.logger.debug(f"Set x-axis limits: {x_limits}")
    
    def _apply_custom_labels(self):
        """Apply custom window labels."""
        self.logger.debug(f"Applying {len(self.window_labels)} custom labels")
        
        tick_positions = np.arange(self.K) + 0.5 - self.style.padding / 2
        self.ax.set_xticks(tick_positions)
        self.ax.set_xticklabels(self.window_labels)
        
        self.logger.debug(f"Custom labels applied at positions: {tick_positions}")

    def _extract_reference_bases(self,
                                positions: List[int],
                                reads: List[ReadAlignment]) -> Dict[int, str]:
        """Extract reference bases from reads."""
        self.logger.debug(f"Extracting reference bases for {len(positions)} positions from {len(reads)} reads")
        
        kmer_dict = {position: '_' for position in positions}
        bases_found = 0
        
        for read_idx, read_alignment in enumerate(reads):
            for aligned_base in read_alignment.aligned_bases:
                if aligned_base.reference_pos not in positions:
                    continue
                if kmer_dict[aligned_base.reference_pos] == '_':
                    kmer_dict[aligned_base.reference_pos] = aligned_base.reference_base
                    bases_found += 1
            
            if all(base != '_' for base in kmer_dict.values()):
                self.logger.debug(f"All reference bases found after checking {read_idx + 1} reads")
                break
        
        # Log any missing bases
        missing_positions = [pos for pos, base in kmer_dict.items() if base == '_']
        if missing_positions:
            self.logger.warning(f"Could not find reference bases for positions: {missing_positions}")
        else:
            self.logger.debug(f"Successfully extracted all {len(positions)} reference bases")
        
        return kmer_dict
    
    def _update_position_labels(self):
        """Update x-axis labels with stacked position values."""
        self.logger.debug("Updating position labels on x-axis")
        
        tick_positions = np.arange(self.K) + 0.5 - self.style.padding / 2
        self.ax.set_xticks(tick_positions)
        
        plotted_conditions = list(self._plotted_conditions_map.values())
        n_conditions = len(plotted_conditions)
        self.logger.debug(f"Updating labels for {n_conditions} conditions")
        
        if n_conditions == 1:
            # Single set of labels
            self.logger.debug("Single condition - applying simple labels")
            labels = self.ax.set_xticklabels(plotted_conditions[0].xticklabels)
            # Color the labels
            if plotted_conditions:
                for label in labels:
                    label.set_color(plotted_conditions[-1].color)
        else:
            # Multiple label sets - create stacked labels
            self.logger.debug(f"Multiple conditions ({n_conditions}) - creating stacked labels")
            self.ax.set_xticklabels([''] * self.K)
            
            # Add colored text for each row
            for i in range(self.K):
                x_pos = tick_positions[i]
                y_base = self.style.xtick_label_y_start
                y_offset = self.style.xtick_label_row_spacing
                
                for j, group in enumerate(plotted_conditions):
                    if j < len(plotted_conditions):
                        color = plotted_conditions[j].color
                    else:
                        color = 'black'
                    
                    trans = self.ax.get_xaxis_transform()
                    self.ax.text(x_pos, y_base + j * y_offset, str(group.xticklabels[i]),
                            transform=trans,
                            ha='center', va='top',
                            fontsize=self.style.tick_labelsize,
                            color=color,
                            clip_on=False)
        
        # Always adjust x-label padding based on number of conditions
        # This ensures xlabel is positioned correctly even for single condition
        label_padding = self.style.xlabel_margin_base + (n_conditions - 1) * self.style.xlabel_margin_per_row
        self.ax.set_xlabel('Genomic Position', fontsize=self.style.label_fontsize,
                        labelpad=label_padding)
        self.logger.debug(f"Set x-label padding to {label_padding} (base={self.style.xlabel_margin_base}, "
                        f"rows={n_conditions}, per_row={self.style.xlabel_margin_per_row})")

    
    def _update_legend(self):
        """Create custom legend on the right side."""
        if not self.style.show_legend:
            self.logger.debug("Legend disabled by style settings")
            return
            
        if not self._plotted_conditions_map:
            self.logger.debug("No conditions to show in legend")
            return
        
        self.logger.debug(f"Creating legend for {len(self._plotted_conditions_map)} conditions")
        
        # Remove default legend if exists
        if self.ax.get_legend() is not None:
            self.ax.get_legend().remove()
            self.logger.debug("Removed existing legend")
        
        # Adjust figure for legend
        self.fig.subplots_adjust(right=0.75)
        
        # Add title
        self.fig.text(0.77, 0.9, 'Groups:', 
                     fontsize=self.style.label_fontsize,
                     weight='bold',
                     transform=self.fig.transFigure)
        
        plotted_conditions = list(self._plotted_conditions_map.values())
        
        # Add each group
        y_pos = 0.85
        for i, group in enumerate(plotted_conditions):
            # Draw line sample using matplotlib Line2D instead of axes
            from matplotlib.lines import Line2D
            line = Line2D([0.77, 0.79], [y_pos, y_pos], 
                         color=group.color, 
                         linewidth=group.line_width * 2,
                         linestyle=group.line_style,
                         transform=self.fig.transFigure)
            self.fig.add_artist(line)
            
            # Add label text
            self.fig.text(0.80, y_pos, group.label,
                         fontsize=self.style.legend_fontsize,
                         color='black',
                         transform=self.fig.transFigure,
                         va='center')
            
            y_pos -= 0.08
            
            # Add separator
            if i < len(plotted_conditions) - 1:
                self.fig.text(0.77, y_pos + 0.03, '─' * 20,
                             fontsize=self.style.legend_fontsize * 0.7,
                             color='lightgray',
                             transform=self.fig.transFigure)
        
        self.logger.debug("Legend created successfully")
    
    def _plot_reads(self,
                   reads: List[ReadAlignment],
                   positions: List[int],
                   color: Any,
                   alpha: Optional[float],
                   line_width: Optional[float],
                   line_style: Optional[str]):
        """Plot a group of reads."""
        self.logger.debug(f"Starting to plot {len(reads)} reads")
        
        # Auto-calculate alpha if needed
        if alpha is None and self.style.alpha_mode == 'auto':
            alpha = self._calculate_alpha(len(reads))
            self.logger.debug(f"Auto-calculated alpha: {alpha} for {len(reads)} reads")
        elif alpha is None:
            alpha = self.style.fixed_alpha
            self.logger.debug(f"Using fixed alpha: {alpha}")
        
        # Statistics for logging
        signals_plotted = 0
        missing_signals = 0
        
        # Plot each read
        for read_idx, read_alignment in enumerate(reads):
            bases_dict = {
                base.reference_pos: base 
                for base in read_alignment.aligned_bases
            }
            
            # Plot signal for each position
            for pos_idx, genomic_pos in enumerate(positions):
                if genomic_pos in bases_dict and bases_dict[genomic_pos].has_signal:
                    base = bases_dict[genomic_pos]
                    signal = base.signal
                    
                    if read_alignment.is_reversed:
                        signal = signal[::-1]
                    
                    # Calculate x-coordinates
                    signal_length = len(signal)
                    x_start = pos_idx
                    x_end = pos_idx + 1 - self.style.padding
                    x_coords = np.linspace(x_start, x_end, signal_length)
                    
                    # Plot the signal
                    self.ax.plot(
                        x_coords, signal,
                        color=color,
                        alpha=alpha,
                        linewidth=line_width,
                        linestyle=line_style,
                    )
                    signals_plotted += 1
                elif genomic_pos in bases_dict:
                    missing_signals += 1
        
        self.logger.info(f"Plotted {signals_plotted} signal segments from {len(reads)} reads")
        if missing_signals > 0:
            self.logger.warning(f"{missing_signals} bases had no signal data")
        
        # Log plot statistics if in debug mode
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug(f"Plot parameters: color={color}, alpha={alpha}, "
                            f"line_width={line_width}, line_style={line_style}")
    
    def _calculate_alpha(self, n_reads: int) -> float:
        """Calculate appropriate alpha value."""
        if n_reads <= 1:
            alpha = 1.0
        elif n_reads <= 3:
            alpha = 0.9
        elif n_reads <= 10:
            alpha = 0.6
        elif n_reads <= 50:
            alpha = 0.6 - (n_reads - 10) * 0.3 / 40
        elif n_reads <= 100:
            alpha = 0.3 - (n_reads - 50) * 0.15 / 50
        elif n_reads <= 500:
            log_scale = np.log10(n_reads / 100) / np.log10(5)
            alpha = 0.15 - log_scale * 0.1
        else:
            alpha = max(0.02, 0.05 - (n_reads - 500) * 0.03 / 500)
        
        self.logger.debug(f"Calculated alpha={alpha:.3f} for {n_reads} reads")
        return alpha