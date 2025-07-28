import logging
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union, Literal, Any
from dataclasses import dataclass, field
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
    position_labels: List[str]
    line_artists: List[Any] = field(default_factory=list)

class StatsVisualizer:
    """Handles all plotting, visualization, and figure management."""
    
    def __init__(self,
                 K: int,
                 n_stats: int,
                 window_labels: Optional[List[Union[str, int]]] = None,
                 stats_names: Optional[List[str]] = None,
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
        self.logger.debug(f"Initializing StatsVisualizer with K={K}")
        
        self.K = K
        self.n_stats = n_stats
        self.window_labels = window_labels
        self.stats_names = stats_names
        
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
        self.fig, self.axes = self._create_figure(self.title)
        
        # Apply custom labels if provided
        if window_labels:
            self.logger.debug(f"Applying custom window labels: {window_labels}")
            self._apply_custom_labels()
        
        # Track plotting state
        self._plot_count = 0
        self._plotted_conditions_map: Dict[str, PlottedCondition] = OrderedDict()
        
        # Store color assignments to maintain consistency
        self._color_assignments: Dict[str, Any] = {}
        
        self.logger.info(f"Initialized StatsVisualizer with K={K}, style={self.style.color_scheme.value}")

    def _create_figure(self, title: Optional[str] = None) -> Tuple[plt.Figure, plt.Axes]:
        """Create and configure the matplotlib figure."""
        self.logger.debug("Creating matplotlib figure")
        
        plt.ioff()  # Turn off interactive mode during creation
        
        fig, axes = plt.subplots(figsize=self.style.figsize, dpi=self.style.dpi, nrows=self.n_stats, ncols=self.K)

        # Make sure axes is a 2d matrix even if only 1 stat is provided
        axes = np.atleast_2d(axes)

        # Set title
        self.logger.debug(f"Setting initial title: '{title}'")
        fig.suptitle(title, fontsize=self.style.title_fontsize)
        
        # Configure axes
        for row_index, row_axes in enumerate(axes):
            for col_index, ax in enumerate(row_axes):
                if col_index==0:
                    stat_label = self.stats_names[row_index] if self.stats_names else f'Stat {row_index+1}'
                    ax.set_ylabel(f'{stat_label}\nDensity', fontsize=self.style.label_fontsize)

                if row_index==self.n_stats-1:
                    ax.set_xlabel('Data', fontsize=self.style.label_fontsize)
                
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
        return fig, axes
    
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
        line_artists = self._plot_stats(condition)

        # Store plotted condition with line artists
        self.logger.debug(f"Storing plotted condition '{label}'")
        self._plotted_conditions_map[label] = PlottedCondition(
            condition=condition,
            position_labels=position_labels,
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
    
    def get_plotted_labels(self) -> List[str]:
        """Get list of currently plotted condition labels."""
        return list(self._plotted_conditions_map.keys())
    
    def has_condition(self, label: str) -> bool:
        """Check if a condition is currently plotted."""
        return label in self._plotted_conditions_map
    
    
    def set_title(self, title: str) -> 'StatsVisualizer':
        """Set or update the plot title."""
        self.logger.debug(f"Setting plot title: '{title}'")
        self.title = title
        self.fig.suptitle(title, fontsize=self.style.title_fontsize)
        return self
    
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
        return None

    
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
    
    def _apply_custom_labels(self):
        """Apply custom window labels."""
        self.logger.debug(f"Applying {len(self.window_labels)} custom labels")
        
        for row_index, row_axes in enumerate(self.axes):
            for col_index, ax in enumerate(row_axes):
                if row_index==0:
                    ax.set_title(self.window_labels[col_index])
            if row_index!=0:
                break
        
        self.logger.debug(f"Custom labels applied at titles")

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
        """Update subplot titles with stacked position values."""
        self.logger.debug("Updating position labels on subplot titles")
        
        # First, clear any existing custom title elements
        for ax_row in self.axes:
            for ax in ax_row:
                # Remove any custom text objects that were added as title supplements
                for txt in ax.texts:
                    if hasattr(txt, '_is_position_label'):
                        txt.remove()
        
        plotted_conditions = list(self._plotted_conditions_map.values())
        n_conditions = len(plotted_conditions)
        
        if n_conditions == 0:
            # No conditions, just show positions or window labels
            for col_idx, ax in enumerate(self.axes[0]):
                if self.window_labels:
                    ax.set_title(self.window_labels[col_idx])
                else:
                    ax.set_title(f"Position {col_idx}")
        elif n_conditions == 1:
            # Single set of labels
            self.logger.debug("Single condition - applying simple labels")
            for col_idx, ax in enumerate(self.axes[0]):
                ax.set_title(plotted_conditions[0].position_labels[col_idx], 
                            color=plotted_conditions[0].condition.color,
                            fontsize=self.style.title_fontsize)
        else:
            # Multiple label sets - create stacked labels
            self.logger.debug(f"Multiple conditions ({n_conditions}) - creating stacked labels")
            
            for col_idx in range(self.K):
                ax = self.axes[0][col_idx]
                
                # Clear the main title
                ax.set_title('')
                
                # Add colored text for each condition
                y_offset_base = 1.15  # Start position above the subplot
                y_offset_step = 0.15  # Space between lines
                
                for j, group in enumerate(plotted_conditions[::-1]):
                    color = group.condition.color
                    
                    # Add text above the subplot
                    txt = ax.text(0.5, y_offset_base + j * y_offset_step, 
                                group.position_labels[col_idx],
                                transform=ax.transAxes,
                                ha='center', va='bottom',
                                fontsize=self.style.tick_labelsize,
                                color=color)
                    # Mark as position label for removal
                    txt._is_position_label = True
        
        # Adjust top margin if multiple conditions
        if n_conditions > 1:
            top_margin = 0.93 - (n_conditions - 1) * 0.02
            self.fig.subplots_adjust(top=top_margin)
        else:
            self.fig.subplots_adjust(top=0.93)
        
        self.logger.debug(f"Updated position labels for {n_conditions} conditions")

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
    
    def _plot_stats(self, condition: Condition) -> List[Any]:
        """Plot a group of reads and return line artists."""
        if self.axes is None:
            return
        
        artists = []
        
        # Determine which stats to plot (up to n_stats)
        stats_data = condition.stats
        positions = condition.positions
        
        # Plot each statistic
        for stat_idx, stat_name in enumerate(self.stats_names):
            
            # Plot KDE for each position
            for pos_idx, position in enumerate(positions):
                if position in stats_data and stat_name in stats_data[position]:
                    values = stats_data[position][stat_name]
                    
                    if values is not None and pos_idx < self.K:
                        ax = self.axes[stat_idx][pos_idx]
                        single_artists = self._plot_single_kde(
                            ax, values, condition.label, condition.color,
                        )
                        artists.extend(single_artists)
        return artists

    def _plot_single_kde(self,
                        ax: plt.Axes,
                        values: List[float],
                        label: str,
                        color: Any,):
        """Plot KDE on a single axes using seaborn."""
        artists = []
        values = np.array(values)
        
        if len(values) > 2:  # Need at least 3 values for KDE
            
            from scipy.stats import gaussian_kde
            kde = gaussian_kde(values)
            q1, q9 = np.percentile(values, [1, 99])
            x_range = np.linspace(q1, q9, 200)
            density = kde(x_range)

            # Plot KDE curve
            line = ax.plot(x_range, density, color=color,
                   linewidth=self.style.line_width,
                   alpha=0.8)
            artists.extend(line)  
            poly = ax.fill_between(x_range, density, color=color, alpha=0.3)  
            artists.append(poly)  
        else:
            # For few values, plot as scatter
            y_jitter = np.random.normal(0, 0.02, len(values))
            line = ax.scatter(values, y_jitter, color=color, alpha=0.6, s=30)
            artists.extend(line)
        
        ax.locator_params(axis='x', nbins=4)
        return artists
    
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