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

from .utils.data_classes import ReadAlignment, Condition
from .utils.path_utils import validate_files
from .utils.plotly_utils import PlotStyle
from .utils.color_utils import to_rgba_str


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
        else:
            self.logger.warning(
                f"Invalid renderer selected. Available options: 'SVG' and 'WebGL'. Defaulting to 'SVG'."
            )
            self._plot_func = go.Scatter

        # Store initial title
        self.title = title or "Nanopore Signal Statistics"

        # Create figure
        self.logger.debug(f"Creating Plotly figure")
        self._create_figure()

        # Track plotting state
        self._conditions: Dict[str, Condition] = OrderedDict()

        self.logger.info(f"Initialized StatsVisualizer with K={K}, n_stats={n_stats}")

    def _create_figure(self):
        """Create and configure the Plotly figure."""
        self.logger.debug("Creating Plotly figure with subplots")

        # Set subplot titles for first row only
        column_titles = self.window_labels or [f"Pos {i+1}" for i in range(self.K)]
        column_titles = [str(title) for title in column_titles[: self.K]]

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
            column_titles=column_titles,
            vertical_spacing=v_spacing,
            horizontal_spacing=h_spacing,
            specs=[
                [{"type": "xy"} for _ in range(self.K)] for _ in range(self.n_stats)
            ],
        )

        # Apply style - but DON'T include axis defaults
        layout_dict = self.style.get_layout_dict()

        # Remove axis defaults that only apply to main axes
        xaxis_layout = layout_dict.pop("xaxis", {}) or {}
        yaxis_layout = layout_dict.pop("yaxis", {}) or {}

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
        yaxis_layout.update({"showticklabels": False, "ticks": "", "showgrid": False})

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

    def plot_condition(self, condition: Condition):
        """Plot a processed group of reads."""
        reads = condition.reads
        positions = condition.positions
        label = condition.label
        color = condition.color

        self.logger.debug(
            f"plot_condition called: label='{label}', n_reads={len(reads)}, positions={positions[0]}-{positions[-1]}"
        )

        # Check if condition already plotted
        if label in self._conditions:
            self.logger.warning(f"Condition '{label}' already plotted. Updating it.")
            self.remove_condition(label)

        # Plot the stats and collect trace indices
        self.logger.info(f"Plotting stats for condition '{label}'")
        self._plot_stats(condition)

        # Store plotted condition
        self._conditions[condition.label] = condition

    def _plot_stats(self, condition: Condition):
        """Plot statistics for a condition."""
        stats_data = condition.stats or {}
        positions = condition.positions
        show_legend = self.style.show_legend

        for stat_idx, stat_name in enumerate(self.stats_names):
            row = stat_idx + 1
            for pos_idx, position in enumerate(positions):
                col = pos_idx + 1
                if position not in stats_data or stat_name not in stats_data[position]:
                    continue

                values = np.asarray(stats_data[position][stat_name], dtype=float)
                values = values[np.isfinite(values)]
                if values.size == 0:
                    continue

                show_legend_here = show_legend and stat_idx == 0 and pos_idx == 0

                self._plot_single_kde(
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

    def _plot_single_kde(
        self,
        values: np.ndarray,
        label: str,
        color: str,
        opacity: float,
        line_width: float,
        line_style: str,
        row: int,
        col: int,
        showlegend: bool,
        legendgroup: str,
    ):
        values = np.asarray(values, dtype=float)

        if values.size > 2:
            try:
                vmin, vmax = float(values.min()), float(values.max())
                if vmin == vmax:
                    pad = max(1e-6, abs(vmin) * 1e-3 or 1e-3)
                    vmin, vmax = vmin - pad, vmax + pad
                x_range = np.linspace(vmin, vmax, 200)
                kde = gaussian_kde(values)
                density = kde(x_range)

                fill_color = to_rgba_str(color, 0.2)
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
                        meta={"cond": label, "kind": "kde"},
                        hovertemplate="%{x:.2f}<br>Density: %{y:.3f}<extra></extra>",
                    ),
                    row=row,
                    col=col,
                )
                return
            except Exception as e:
                self.logger.warning(
                    f"KDE failed for {label} (row={row}, col={col}): {e}"
                )

        # Fallback: jitter points (values.size <= 2 or KDE failed)
        y_jitter = np.random.normal(0, 0.02, values.size)
        self.fig.add_trace(
            self._plot_func(
                x=values,
                y=y_jitter,
                mode="markers",
                name=label,
                marker=dict(color=color, size=8, opacity=opacity * 0.6),
                showlegend=showlegend,
                legendgroup=legendgroup,
                meta={"cond": label, "kind": "kde"},
                hovertemplate="Value: %{x:.2f}<extra></extra>",
            ),
            row=row,
            col=col,
        )

    def remove_condition(self, label: str) -> bool:
        """Remove a specific condition from the plot."""
        if label not in self._conditions:
            self.logger.warning(f"Condition '{label}' not found in plot")
            return False

        self.logger.info(f"Removing condition '{label}' from plot")

        # Remove traces (in reverse order to maintain indices)
        kept = []
        for tr in self.fig.data:
            if getattr(tr, "meta", {}).get("cond") != label:
                kept.append(tr)
        self.fig.data = tuple(kept)

        # Remove from plotted conditions
        self._conditions.pop(label, None)

        self.logger.debug(f"Successfully removed condition '{label}'")
        return True

    def clear_conditions(self):
        """Remove all plotted conditions."""
        self.logger.info("Clearing all conditions from plot")

        # Clear all traces
        self.fig.data = tuple()

        # Clear the map
        self._conditions.clear()

        self.logger.debug("All conditions cleared")

    def get_plotted_labels(self) -> List[str]:
        """Get list of currently plotted condition labels."""
        return list(self._conditions.keys())

    def has_condition(self, label: str) -> bool:
        """Check if a condition is currently plotted."""
        return label in self._conditions

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
