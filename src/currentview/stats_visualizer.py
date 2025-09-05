import logging
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union, Literal, Any
from dataclasses import dataclass, field
from collections import OrderedDict
from scipy.stats import gaussian_kde

from .readers import AlignmentExtractor
from .readers import SignalExtractor
from .utils import ReadAlignment, Condition
from .utils import validate_files
from .utils import PlotStyle, ColorScheme
from .utils import to_rgba_str


@dataclass
class PlottedCondition:
    """Track information about each plotted group."""

    condition: Condition
    position_labels: List[str]
    trace_indices: List[int] = field(default_factory=list)  # Trace indices in fig.data


class StatsVisualizer:
    """Handles all plotting, visualization, and figure management using Plotly."""

    def __init__(
        self,
        K: int,
        n_stats: int,
        window_labels: Optional[List[Union[str, int]]] = None,
        stats_names: Optional[List[str]] = None,
        plot_style: Optional[PlotStyle] = None,
        title: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize the visualizer.

        Args:
            K: Number of bases to show
            n_stats: Number of statistics to plot
            window_labels: Optional custom labels for x-axis
            stats_names: Optional names for statistics
            plot_style: Optional PlotStyle configuration
            title: Optional custom title
            width: Optional figure width in pixels
            height: Optional figure height in pixels
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        self.logger.debug(f"Initializing StatsVisualizer with K={K}, n_stats={n_stats}")

        self.K = K
        self.n_stats = n_stats
        self.window_labels = window_labels
        self.stats_names = stats_names or [f"Stat {i+1}" for i in range(n_stats)]

        # Setup style
        self.style = plot_style or PlotStyle()

        if self.style.renderer == "SVG":
            self._plot_func = go.Scatter
        elif self.style.renderer == "WebGL":
            self._plot_func = go.Scattergl

        # Store initial title
        self.title = title or "Nanopore Signal Statistics"

        # Initialize color palette
        self.color_sequence = self.style.get_color_sequence()

        # Create figure
        self.logger.debug(f"Creating Plotly figure")
        self._create_figure()

        # Track plotting state
        self._plot_count = 0
        self._plotted_conditions_map: Dict[str, PlottedCondition] = OrderedDict()

        # Store color assignments to maintain consistency
        self._color_assignments: Dict[str, str] = {}

        self.logger.info(f"Initialized StatsVisualizer with K={K}, n_stats={n_stats}")

    def _create_figure(self):
        """Create and configure the Plotly figure."""
        self.logger.debug("Creating Plotly figure with subplots")

        # Set subplot titles for first row only
        column_titles = self.window_labels or [f"Position {i}" for i in range(self.K)]

        # Calculate spacing
        v_spacing = self.style.subplot_vertical_spacing or (
            0.15 / self.n_stats if self.n_stats > 1 else 0
        )
        h_spacing = self.style.subplot_horizontal_spacing or (
            0.1 / self.K if self.K > 1 else 0
        )

        # Create subplots
        self.fig = make_subplots(
            rows=self.n_stats,
            cols=self.K,
            subplot_titles=None,
            row_titles=self.stats_names,  # Keep stats names on the right
            column_titles=None,
            vertical_spacing=v_spacing,
            horizontal_spacing=h_spacing,
            specs=[
                [{"type": "xy"} for _ in range(self.K)] for _ in range(self.n_stats)
            ],
        )

        # Apply style - but DON'T include axis defaults
        layout_dict = self.style.get_layout_dict()

        # Remove axis defaults that only apply to main axes
        xaxis_layout = layout_dict.pop("xaxis", None)
        yaxis_layout = layout_dict.pop("yaxis", None)

        if "title" not in layout_dict:
            layout_dict["title"] = {}
        layout_dict["title"].update(
            {
                "text": self.title,
                "font": {"size": self.style.title_font_size},
                "x": 0.5,
                "xanchor": "center",
            }
        )
        yaxis_layout.update(
            {
                "showticklabels": False,  # Hide tick labels
                "ticks": "",  # Hide tick marks (empty string)
                "showgrid": False,
            }
        )

        self.fig.update_layout(**layout_dict)

        # Update all subplot axes
        for row in range(1, self.n_stats + 1):
            for col in range(1, self.K + 1):
                # Update x-axis with all style settings
                self.fig.update_xaxes(
                    title_text="Value" if row == self.n_stats else "",
                    **xaxis_layout,
                    row=row,
                    col=col,
                )

                # Update y-axis with all style settings
                self.fig.update_yaxes(
                    title_text="Density" if col == 1 else "",
                    **yaxis_layout,
                    row=row,
                    col=col,
                )

        if not self.window_labels:
            self._create_position_annotations()

    def _create_position_annotations(self):
        """Tag annotations with metadata for column titles, keeping order."""
        new_annotations = []

        for ann in self.fig.layout.annotations:
            ann_dict = ann.to_plotly_json()  # Convert to plain dict

            if "text" in ann_dict and "Position" in ann_dict["text"]:
                ann_dict["name"] = "ColumnTitle_" + ann_dict["text"]  # Add your marker
            new_annotations.append(ann_dict)

        # Replace layout.annotations with new dict-based ones
        self.fig.layout.annotations = new_annotations

    def plot_condition(self, condition: Condition):
        """Plot a processed group of reads."""
        reads = condition.reads
        positions = condition.positions
        label = condition.label
        color = condition.color
        opacity = condition.alpha
        line_width = condition.line_width
        line_style = condition.line_style

        self.logger.debug(
            f"plot_condition called: label='{label}', n_reads={len(reads)}, positions={positions[0]}-{positions[-1]}"
        )

        # Check if condition already plotted
        if label in self._plotted_conditions_map:
            self.logger.warning(f"Condition '{label}' already plotted. Updating it.")
            self.remove_condition(label)

        # Assign color if not specified
        if color is None:
            if label in self._color_assignments:
                color = self._color_assignments[label]
                self.logger.debug(f"Reusing previous color for '{label}'")
            else:
                color = self._get_next_color()
                self._color_assignments[label] = color
                self.logger.debug(f"Auto-assigned new color for '{label}'")
            condition.color = color
        else:
            self._color_assignments[label] = color

        # Calculate opacity if not specified
        if opacity is None:
            if self.style.opacity_mode == "fixed":
                opacity = self.style.fixed_opacity
            elif self.style.opacity_mode == "auto":
                opacity = self._calculate_opacity(len(reads))
            condition.alpha = opacity

        # Extract reference bases
        self.logger.debug("Extracting reference bases for k-mer labels")
        kmer_dict = self._extract_reference_bases(positions, reads)
        position_labels = [f"{pos} - {kmer_dict[pos]}" for pos in positions]

        line_style = line_style or self.style.line_style
        condition.line_style = line_style

        # Use style defaults
        line_width = line_width or self.style.line_width
        condition.line_width = line_width

        # Plot the stats and collect trace indices
        self.logger.info(f"Plotting stats for condition '{label}'")
        trace_indices = self._plot_stats(condition)

        # Store plotted condition
        self._plotted_conditions_map[label] = PlottedCondition(
            condition=condition,
            position_labels=position_labels,
            trace_indices=trace_indices,
        )

        # Update position labels
        if not self.window_labels:
            self._update_position_labels()

        self._plot_count += 1
        self.logger.debug(f"Plot count incremented to {self._plot_count}")

    def _plot_stats(self, condition: Condition) -> List[int]:
        """Plot statistics and return trace indices."""
        trace_indices = []

        stats_data = condition.stats
        positions = condition.positions

        # Show legend for all conditions
        show_legend = self.style.show_legend

        # Plot each statistic
        for stat_idx, stat_name in enumerate(self.stats_names):
            row = stat_idx + 1

            # Plot KDE for each position
            for pos_idx, position in enumerate(positions):
                col = pos_idx + 1

                if position in stats_data and stat_name in stats_data[position]:
                    values = stats_data[position][stat_name]

                    if values is not None and len(values) > 0:
                        # Only show legend for first subplot
                        show_legend_here = (
                            show_legend and stat_idx == 0 and pos_idx == 0
                        )

                        trace_idx = self._plot_single_kde(
                            values=values,
                            label=condition.label,
                            color=condition.color,
                            opacity=condition.alpha,
                            line_width=condition.line_width,
                            line_style=condition.line_style,
                            row=row,
                            col=col,
                            showlegend=show_legend_here,
                            legendgroup=condition.label,
                        )

                        if trace_idx is not None:
                            trace_indices.append(trace_idx)

        return trace_indices

    def _plot_single_kde(
        self,
        values: List[float],
        label: str,
        color: str,
        opacity: float,
        line_width: float,
        line_style: str,
        row: int,
        col: int,
        showlegend: bool,
        legendgroup: str,
    ) -> Optional[int]:
        """Plot KDE on a single subplot and return trace index."""
        values = np.array(values)

        if len(values) > 2:  # Need at least 3 values for KDE
            try:
                kde = gaussian_kde(values)
                x_range = np.linspace(values.min(), values.max(), 200)
                density = kde(x_range)

                # Convert color to RGBA for fill
                fill_color = to_rgba_str(color, 0.2)

                # Single trace with both line and fill
                self.fig.add_trace(
                    self._plot_func(
                        x=x_range,
                        y=density,
                        mode="lines",
                        name=label,
                        line=dict(color=color, width=line_width, dash=line_style),
                        fill="tozeroy",
                        fillcolor=fill_color,
                        showlegend=showlegend,
                        legendgroup=legendgroup,
                        hovertemplate="%{x:.2f}<br>Density: %{y:.3f}<extra></extra>",
                    ),
                    row=row,
                    col=col,
                )

                return len(self.fig.data) - 1

            except Exception as e:
                self.logger.warning(f"KDE failed: {e}")
                return None

        else:
            # For few values, plot as scatter with jitter
            y_jitter = np.random.normal(0, 0.02, len(values))

            self.fig.add_trace(
                self._plot_func(
                    x=values,
                    y=y_jitter,
                    mode="markers",
                    name=label,
                    marker=dict(color=color, size=8, opacity=opacity * 0.6),
                    showlegend=showlegend,
                    legendgroup=legendgroup,
                    hovertemplate="Value: %{x:.2f}<extra></extra>",
                ),
                row=row,
                col=col,
            )

            return len(self.fig.data) - 1

    def remove_condition(self, label: str) -> bool:
        """Remove a specific condition from the plot."""
        if label not in self._plotted_conditions_map:
            self.logger.warning(f"Condition '{label}' not found in plot")
            return False

        self.logger.info(f"Removing condition '{label}' from plot")

        # Get the condition
        condition = self._plotted_conditions_map[label]

        # Remove traces (in reverse order to maintain indices)
        for idx in sorted(condition.trace_indices, reverse=True):
            if idx < len(self.fig.data):
                self.fig.data = self.fig.data[:idx] + self.fig.data[idx + 1 :]

        # Remove from plotted conditions
        del self._plotted_conditions_map[label]

        # Update trace indices for remaining conditions
        self._update_trace_indices()

        # Update position labels
        if not self.window_labels:
            self._update_position_labels()

        self.logger.debug(f"Successfully removed condition '{label}'")
        return True

    def _update_trace_indices(self):
        """Update trace indices after removal."""
        # This is needed because removing traces changes indices
        current_idx = 0
        for condition in self._plotted_conditions_map.values():
            new_indices = []
            for _ in condition.trace_indices:
                new_indices.append(current_idx)
                current_idx += 1
            condition.trace_indices = new_indices

    def clear_conditions(self):
        """Remove all plotted conditions."""
        self.logger.info("Clearing all conditions from plot")

        # Clear all traces
        self.fig.data = []

        # Clear the map
        self._plotted_conditions_map.clear()

        # Reset plot count
        self._plot_count = 0

        # Update position labels
        if not self.window_labels:
            self._update_position_labels()

        self.logger.debug("All conditions cleared")

    def _update_position_labels(self):
        """Update x-axis labels based on plotted conditions."""
        if True:
            return
        self.logger.debug("Updating position labels")

        plotted_conditions = list(self._plotted_conditions_map.values())
        n_conditions = len(plotted_conditions)

        if n_conditions == 0:
            # Default labels
            titles_text = [str(i) for i in range(self.K)]
        elif n_conditions == 1:
            # Single condition labels
            titles_text = plotted_conditions[0].position_labels
        else:
            # Multiple conditions - create multi-line labels
            titles_text = []
            for i in range(self.K):
                labels = []
                for cond in plotted_conditions:
                    color = cond.condition.color
                    label = cond.position_labels[i]
                    labels.append(f"<span style='color:{color}'>{label}</span>")
                titles_text.append("<br>".join(labels * 3))

        # Update the first K subplot titles (one per column in row=1)
        for ann in self.fig.layout.annotations:
            ann_dict = ann.to_plotly_json()

            # Check if this is a positional column title
            name = ann_dict.get("name")
            if not (isinstance(name, str) and "ColumnTitle_Position" in name):
                continue

            # Extract index from text like "Position 3"
            curr_txt = ann_dict.get("text", "")
            print(f"Original text: {curr_txt}")

            try:
                idx = int(name.split(" ")[-1])
                ann["text"] = titles_text[idx]  # use the real index from the label
            except (IndexError, ValueError) as e:
                print(f"Skipping annotation with invalid text: {curr_txt}")
                continue

    def get_plotted_labels(self) -> List[str]:
        """Get list of currently plotted condition labels."""
        return list(self._plotted_conditions_map.keys())

    def has_condition(self, label: str) -> bool:
        """Check if a condition is currently plotted."""
        return label in self._plotted_conditions_map

    def set_title(self, title: str) -> "StatsVisualizer":
        """Set or update the plot title."""
        self.logger.debug(f"Setting plot title: '{title}'")
        self.title = title
        self.fig.update_layout(
            title={
                "text": title,
                "font": {"size": self.style.title_font_size},
                "x": 0.5,
                "xanchor": "center",
            }
        )
        return self

    def show(self):
        """Display the plot."""
        self.logger.info("Displaying plot")
        self.fig.show()

    def get_fig(self):
        self.logger.info("Returning fig")
        return self.fig

    def save(
        self,
        path: Union[str, Path],
        format: Optional[str] = None,
        scale: Optional[float] = None,
        **kwargs,
    ):
        """
        Save the figure to file.

        Args:
            path: Output file path
            format: File format ('png', 'jpg', 'svg', 'pdf', 'html')
            scale: Scale factor for raster formats
            **kwargs: Additional arguments passed to write function
        """
        path = Path(path)

        # Determine format from extension if not specified
        if format is None:
            format = path.suffix.lstrip(".").lower()
            if not format:
                format = "png"

        self.logger.debug(f"Saving figure: path={path}, format={format}")

        try:
            if format == "html":
                self.fig.write_html(str(path), **kwargs)
            else:
                # For image formats
                write_kwargs = {
                    "format": format,
                    "scale": scale or self.style.toImageButtonOptions.get("scale", 2),
                }
                write_kwargs.update(kwargs)
                self.fig.write_image(str(path), **write_kwargs)

            self.logger.info(f"Saved figure to {path}")
        except Exception as e:
            self.logger.error(f"Failed to save figure: {type(e).__name__}: {str(e)}")
            raise

    def _get_next_color(self) -> str:
        """Get the next color from the palette."""
        color_index = len(self._color_assignments) % len(self.color_sequence)
        color = self.color_sequence[color_index]
        self.logger.debug(f"Getting color {color_index} from palette: {color}")
        return color

    def _extract_reference_bases(
        self, positions: List[int], reads: List[ReadAlignment]
    ) -> Dict[int, str]:
        """Extract reference bases from reads."""
        self.logger.debug(f"Extracting reference bases for {len(positions)} positions")

        kmer_dict = {position: "_" for position in positions}

        for read_alignment in reads:
            for aligned_base in read_alignment.aligned_bases:
                if aligned_base.reference_pos in positions:
                    if kmer_dict[aligned_base.reference_pos] == "_":
                        kmer_dict[aligned_base.reference_pos] = (
                            aligned_base.reference_base
                        )

            if all(base != "_" for base in kmer_dict.values()):
                break

        return kmer_dict

    def _calculate_opacity(self, n_reads: int) -> float:
        """Calculate appropriate opacity value based on number of reads."""
        if n_reads <= 1:
            opacity = 1.0
        elif n_reads <= 3:
            opacity = 0.9
        elif n_reads <= 10:
            opacity = 0.7
        elif n_reads <= 50:
            opacity = 0.5
        elif n_reads <= 100:
            opacity = 0.3
        else:
            opacity = 0.2

        self.logger.debug(f"Calculated opacity={opacity:.2f} for {n_reads} reads")
        return opacity
