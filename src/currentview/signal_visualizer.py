import logging
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union, Literal, Any
from dataclasses import dataclass
from collections import OrderedDict

from .readers import AlignmentExtractor
from .readers import SignalExtractor
from .utils import ReadAlignment, Condition
from .utils import validate_files
from .utils import PlotStyle, ColorScheme

@dataclass
class PlottedCondition:
    """Track information about each plotted group."""
    condition: Condition
    xticklabels: List[str]
    line_artists: List[Any] = None  # Store line objects for removal

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
        
        # Store initial title
        self.title = title or 'Nanopore Signal Visualization'
        
        # Initialize colors
        self.logger.debug("Initializing color palette")
        self._init_colors()
        
        # Create figure
        self.logger.debug(f"Creating figure with size {self.style.figsize}")
        self.fig, self.ax = self._create_figure(self.title)
        
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
        
        # Store color assignments to maintain consistency
        self._color_assignments: Dict[str, Any] = {}
        
        # Store additional plot elements for clean removal
        self._highlight_patches = []
        self._annotations = []
        
        self.logger.info(f"Initialized SignalVisualizer with K={K}, style={self.style.color_scheme.value}")
    
    def plot_condition(self, condition: Condition):
        """Plot a processed group of reads."""
        reads = condition.reads
        positions = condition.positions
        label = condition.label
        color = condition.color
        alpha = condition.alpha
        line_width = condition.line_width
        line_style = condition.line_style
        
        self.logger.debug(f"plot_condition called: label='{label}', n_reads={len(reads)}, positions={positions[0]}-{positions[-1]}")
        
        # Check if condition already plotted
        if label in self._plotted_conditions_map:
            self.logger.warning(f"Condition '{label}' already plotted. Updating it.")
            self.remove_condition(label)
        
        # Assign color if not specified
        if color is None:
            # Check if we had a color for this label before
            if label in self._color_assignments:
                color = self._color_assignments[label]
                self.logger.debug(f"Reusing previous color for '{label}'")
            else:
                color = self._get_next_color()
                self._color_assignments[label] = color
                self.logger.debug(f"Auto-assigned new color for '{label}'")
            condition.color=color
        else:
            self._color_assignments[label] = color

        if alpha is None:
            if self.style.alpha_mode == 'fixed':
                alpha = self.style.fixed_alpha
            elif self.style.alpha_mode == 'auto':
                alpha = self._calculate_alpha(len(reads))
            condition.alpha=alpha
        
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
        condition.line_width=line_width
        line_style = line_style or self.style.line_style
        condition.line_style=line_style
        
        # Plot the reads and collect line artists
        self.logger.info(f"Plotting {len(reads)} reads for condition '{label}'")
        line_artists = self._plot_signals(condition)

        # Store plotted condition with line artists
        self.logger.debug(f"Storing plotted condition '{label}'")
        self._plotted_conditions_map[label] = PlottedCondition(
            condition=condition,
            xticklabels=position_labels,
            line_artists=line_artists
        )
        
        # Update x-axis labels
        if not self.window_labels:
            self.logger.debug("Updating position labels on x-axis")
            self._update_position_labels()
        
        # Update legend
        self.logger.debug("Updating legend")
        self._update_legend()
        
        self._plot_count += 1
        self.logger.debug(f"Plot count incremented to {self._plot_count}")
    
    def remove_condition(self, label: str) -> bool:
        """
        Remove a specific condition from the plot.
        
        Args:
            label: Label of the condition to remove
            
        Returns:
            True if condition was removed, False if not found
        """
        if label not in self._plotted_conditions_map:
            self.logger.warning(f"Condition '{label}' not found in plot")
            return False
        
        self.logger.info(f"Removing condition '{label}' from plot")
        
        # Get the condition
        condition = self._plotted_conditions_map[label]
        
        # Remove all line artists from the plot
        if condition.line_artists:
            for artist in condition.line_artists:
                artist.remove()
        
        # Remove from plotted conditions
        del self._plotted_conditions_map[label]
        
        # Update labels and legend
        self._update_position_labels()
        self._update_legend()
        
        # Redraw the canvas
        self.fig.canvas.draw_idle()
        
        self.logger.debug(f"Successfully removed condition '{label}'")
        return True
    
    def clear_conditions(self):
        """Remove all plotted conditions."""
        self.logger.info("Clearing all conditions from plot")
        
        # Remove all line artists
        for condition in self._plotted_conditions_map.values():
            if condition.line_artists:
                for artist in condition.line_artists:
                    artist.remove()
        
        # Clear the map
        self._plotted_conditions_map.clear()
        
        # Reset plot count
        self._plot_count = 0
        
        # Update labels and legend
        self._update_position_labels()
        self._update_legend()
        
        # Redraw
        self.fig.canvas.draw_idle()
        
        self.logger.debug("All conditions cleared")
    
    def update_condition(self, condition: Condition):
        """
        Update an existing condition or add it if it doesn't exist.
        
        This is more efficient than remove + add for updates.
        """
        if condition.label in self._plotted_conditions_map:
            # Remove the old one
            old_condition = self._plotted_conditions_map[condition.label]
            if old_condition.line_artists:
                for artist in old_condition.line_artists:
                    artist.remove()
        
        # Plot the new/updated condition
        self.plot_condition(condition)
    
    def get_plotted_labels(self) -> List[str]:
        """Get list of currently plotted condition labels."""
        return list(self._plotted_conditions_map.keys())
    
    def has_condition(self, label: str) -> bool:
        """Check if a condition is currently plotted."""
        return label in self._plotted_conditions_map
    
    def highlight_position(self,
                          window_idx: Optional[int] = None,
                          color: str = 'red',
                          alpha: float = 0.2) -> 'SignalVisualizer':
        """Highlight a position in the window."""
        if window_idx is None:
            window_idx = self.K // 2  # Center position
            self.logger.debug(f"Using center position {window_idx} for highlighting")
        
        self.logger.debug(f"Highlighting position {window_idx} with color={color}, alpha={alpha}")
        
        patch = self.ax.axvspan(
            window_idx - self.style.padding / 2,
            window_idx + 1 - self.style.padding / 2,
            alpha=alpha,
            color=color,
            zorder=0
        )
        
        # Store for potential removal
        self._highlight_patches.append(patch)
        
        self.logger.info(f"Highlighted window position {window_idx}")
        return self
    
    def clear_highlights(self):
        """Remove all position highlights."""
        for patch in self._highlight_patches:
            patch.remove()
        self._highlight_patches.clear()
        self.fig.canvas.draw_idle()
    
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
        
        annotation = self.ax.annotate(text, xy=(x_pos, y_position), **default_kwargs)
        
        # Store for potential removal
        self._annotations.append(annotation)
        
        self.logger.info(f"Added annotation '{text}' at window position {window_idx}")
        return self
    
    def clear_annotations(self):
        """Remove all annotations."""
        for annotation in self._annotations:
            annotation.remove()
        self._annotations.clear()
        self.fig.canvas.draw_idle()
    
    def set_title(self, title: str) -> 'SignalVisualizer':
        """Set or update the plot title."""
        self.logger.debug(f"Setting plot title: '{title}'")
        self.title = title
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
    
    def reset_view(self):
        """Reset the view to default (clear highlights, annotations, reset zoom)."""
        self.logger.info("Resetting view to default")
        
        # Clear highlights and annotations
        self.clear_highlights()
        self.clear_annotations()
        
        # Reset zoom
        self.ax.autoscale()
        
        # Redraw
        self.fig.canvas.draw_idle()
    
    def refresh(self):
        """Force a refresh of the plot."""
        self.fig.canvas.draw_idle()
    
    def show(self):
        """Display the plot."""
        self.logger.info("Displaying plot")

        try:
            # Check if in a Jupyter notebook
            from IPython import get_ipython
            shell = get_ipython().__class__.__name__

            if shell == 'ZMQInteractiveShell':
                # In Jupyter notebook or JupyterLab
                from IPython.display import display
                display(self.fig)
            else:
                # In terminal/IPython shell
                plt.show()
        except Exception as e:
            self.logger.debug(f"Fallback to plt.show() due to: {e}")
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
        color_index = len(self._color_assignments) % 10
        color = self.colors(color_index)
        self.logger.debug(f"Getting color {color_index} from palette")
        return color
    
    def _create_figure(self, title: Optional[str] = None) -> Tuple[plt.Figure, plt.Axes]:
        """Create and configure the matplotlib figure."""
        self.logger.debug("Creating matplotlib figure")
        
        plt.ioff()  # Turn off interactive mode during creation
        
        fig = plt.figure(figsize=self.style.figsize, dpi=self.style.dpi)
        ax = fig.add_subplot(111)
        
        # Set title
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
        
        # First, clear any existing custom labels
        for txt in self.ax.texts:
            if hasattr(txt, '_is_position_label'):
                txt.remove()
        
        tick_positions = np.arange(self.K) + 0.5 - self.style.padding / 2
        self.ax.set_xticks(tick_positions)
        
        plotted_conditions = list(self._plotted_conditions_map.values())
        n_conditions = len(plotted_conditions)
        
        if n_conditions == 0:
            # No conditions, just show positions
            self.ax.set_xticklabels([str(i) for i in range(self.K)])
        elif n_conditions == 1:
            # Single set of labels
            self.logger.debug("Single condition - applying simple labels")
            labels = self.ax.set_xticklabels(plotted_conditions[0].xticklabels)
            # Color the labels
            for label in labels:
                label.set_color(plotted_conditions[0].condition.color)
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
                    color = group.condition.color
                    
                    trans = self.ax.get_xaxis_transform()
                    txt = self.ax.text(x_pos, y_base + j * y_offset, str(group.xticklabels[i]),
                                       transform=trans,
                                       ha='center', va='top',
                                       fontsize=self.style.tick_labelsize,
                                       color=color,
                                       clip_on=False)
                    # Mark as position label for removal
                    txt._is_position_label = True
        
        # Always adjust x-label padding based on number of conditions
        label_padding = self.style.xlabel_margin_base + (n_conditions - 1) * self.style.xlabel_margin_per_row
        self.ax.set_xlabel('Genomic Position', fontsize=self.style.label_fontsize,
                          labelpad=label_padding)
        self.logger.debug(f"Set x-label padding to {label_padding}")

    def _update_legend(self):
        """Create custom legend on the right side."""
        # First, remove any existing legend elements
        for artist in self.fig.get_children():
            if isinstance(artist, plt.Text) and hasattr(artist, '_is_legend_element'):
                artist.remove()
        for artist in self.fig.artists:
            if hasattr(artist, '_is_legend_element'):
                artist.remove()
        
        if not self.style.show_legend:
            self.logger.debug("Legend disabled by style settings")
            return
            
        if not self._plotted_conditions_map:
            self.logger.debug("No conditions to show in legend")
            # Reset figure margins
            self.fig.subplots_adjust(right=0.9)
            return
        
        self.logger.debug(f"Creating legend for {len(self._plotted_conditions_map)} conditions")
        
        # Remove matplotlib legend if exists
        if self.ax.get_legend() is not None:
            self.ax.get_legend().remove()
        
        # Adjust figure for legend
        self.fig.subplots_adjust(right=0.75)
        
        # Add title
        title_text = self.fig.text(0.77, 0.9, 'Groups:', 
                                  fontsize=self.style.label_fontsize,
                                  weight='bold',
                                  transform=self.fig.transFigure)
        title_text._is_legend_element = True
        
        plotted_conditions = list(self._plotted_conditions_map.values())
        
        # Add each group
        y_pos = 0.85
        for i, group in enumerate(plotted_conditions):
            # Draw line sample
            from matplotlib.lines import Line2D
            line = Line2D([0.77, 0.79], [y_pos, y_pos], 
                         color=group.condition.color, 
                         linewidth=group.condition.line_width * 2,
                         linestyle=group.condition.line_style,
                         transform=self.fig.transFigure)
            line._is_legend_element = True
            self.fig.add_artist(line)
            
            # Add label text
            label_text = self.fig.text(0.80, y_pos, group.condition.label,
                                      fontsize=self.style.legend_fontsize,
                                      color='black',
                                      transform=self.fig.transFigure,
                                      va='center')
            label_text._is_legend_element = True
            
            y_pos -= 0.08
            
            # Add separator
            if i < len(plotted_conditions) - 1:
                sep_text = self.fig.text(0.77, y_pos + 0.03, '─' * 20,
                                        fontsize=self.style.legend_fontsize * 0.7,
                                        color='lightgray',
                                        transform=self.fig.transFigure)
                sep_text._is_legend_element = True
        
        self.logger.debug("Legend created successfully")
    
    def _plot_signals(self, condition: Condition) -> List[Any]:
        """Plot a group of reads and return line artists."""
        self.logger.debug(f"Starting to plot {len(condition.reads)} reads")
        
        # Statistics for logging
        signals_plotted = 0
        missing_signals = 0
        line_artists = []
        
        # Plot each read
        for read_idx, read_alignment in enumerate(condition.reads):
            bases_dict = read_alignment.bases_by_ref_pos
            
            # Plot signal for each position
            for pos_idx, genomic_pos in enumerate(condition.positions):
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
                    line = self.ax.plot(
                        x_coords, signal,
                        color=condition.color,
                        alpha=condition.alpha,
                        linewidth=condition.line_width,
                        linestyle=condition.line_style,
                    )
                    line_artists.extend(line)
                    signals_plotted += 1
                elif genomic_pos in bases_dict:
                    missing_signals += 1
        
        self.logger.info(f"Plotted {signals_plotted} signal segments from {len(condition.reads)} reads")
        if missing_signals > 0:
            self.logger.warning(f"{missing_signals} bases had no signal data")
        
        return line_artists
    
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