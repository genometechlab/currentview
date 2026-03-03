import logging
import numpy as np
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Union, Literal
from collections import OrderedDict
from scipy.stats import gaussian_kde

from ..utils.data_classes import Condition
from ..utils.plotly_utils import PlotStyle

VALID_DISTRIBUTIONS = {"kde", "histogram", "both"}

DK_ALIASES = {
    None: "kde",
    "density": "kde",
    "hist": "histogram",
}


class BaseStatsVisualizer(ABC):
    """
    Abstract base class for stats visualization backends.
    Handles condition tracking, KDE/histogram computation, and shared logic.
    Subclasses implement only the rendering calls.
    """

    def __init__(
        self,
        K: int,
        n_stats: int,
        window_labels: Optional[List[Union[str, int]]] = None,
        stats_names: Optional[List[str]] = None,
        distribution_kind: Literal["kde", "histogram", "both"] = "kde",
        plot_style: Optional[PlotStyle] = None,
        title: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
    ):
        self.logger = logger or logging.getLogger(__name__)
        self.K = K
        self.n_stats = n_stats
        self.window_labels = window_labels
        self.stats_names = stats_names or [f"Stat {i+1}" for i in range(n_stats)]
        self.style = plot_style or PlotStyle()
        self.title = title or "Nanopore Signal Statistics"

        dk = DK_ALIASES.get(distribution_kind, distribution_kind)
        if dk not in VALID_DISTRIBUTIONS:
            self.logger.warning(
                f"Invalid distribution_kind '{distribution_kind}'. Defaulting to 'kde'."
            )
            dk = "kde"
        self.distribution_kind = dk

        self._conditions_info: OrderedDict[str, Dict] = OrderedDict()

        self._create_figure()
        self.logger.info(
            f"Initialized {self.__class__.__name__} with K={K}, n_stats={n_stats}"
        )

    # =========================================================================
    # Abstract interface
    # =========================================================================

    @abstractmethod
    def _create_figure(self):
        """Create and configure the backend figure with subplots."""

    @abstractmethod
    def _render_histogram(
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
        """Render a single histogram into subplot (row, col)."""

    @abstractmethod
    def _render_kde(
        self,
        x_range: np.ndarray,
        density: np.ndarray,
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
        """Render a precomputed KDE curve into subplot (row, col)."""

    @abstractmethod
    def _render_kde_fallback(
        self,
        values: np.ndarray,
        label: str,
        color: str,
        opacity: float,
        row: int,
        col: int,
        showlegend: bool,
        legendgroup: str,
    ):
        """Render fallback scatter (when KDE fails or n<=2) into subplot (row, col)."""

    @abstractmethod
    def _do_remove_condition_traces(self, label: str):
        """Remove all rendered traces belonging to a condition."""

    @abstractmethod
    def _do_set_title(self, title: str):
        """Apply title to the figure."""

    @abstractmethod
    def get_fig(self):
        """Return the underlying figure object."""

    @abstractmethod
    def show(self):
        """Display the figure."""

    @abstractmethod
    def save(self, path: Union[str, Path], **kwargs):
        """Save the figure to disk."""

    # =========================================================================
    # Shared public API
    # =========================================================================

    def plot_condition(self, condition: Condition):
        """Add or update a condition on the plot."""
        label = condition.label
        self.logger.debug(f"plot_condition: '{label}', n_reads={len(condition.reads)}")

        if label in self._conditions_info:
            self.logger.warning(f"Condition '{label}' already plotted — replacing.")
            self.remove_condition(label)

        self._conditions_info[label] = {"style": condition.style}
        self._plot_stats(condition)

    def remove_condition(self, label: str) -> bool:
        if label not in self._conditions_info:
            self.logger.warning(f"Condition '{label}' not found")
            return False
        self._do_remove_condition_traces(label)
        self._conditions_info.pop(label)
        return True

    def clear_conditions(self):
        for label in list(self._conditions_info.keys()):
            self._do_remove_condition_traces(label)
        self._conditions_info.clear()

    def set_title(self, title: str) -> "BaseStatsVisualizer":
        self.title = title
        self._do_set_title(title)
        return self

    def get_plotted_labels(self) -> List[str]:
        return list(self._conditions_info.keys())

    def has_condition(self, label: str) -> bool:
        return label in self._conditions_info

    # =========================================================================
    # Shared internal logic
    # =========================================================================

    def _plot_stats(self, condition: Condition):
        """Dispatch rendering for all stat/position combinations."""
        stats_data = condition.stats or {}

        for stat_idx, stat_name in enumerate(self.stats_names):
            row = stat_idx + 1
            for pos_idx, position in enumerate(condition.positions):
                col = pos_idx + 1

                if position not in stats_data or stat_name not in stats_data[position]:
                    continue

                values = np.asarray(stats_data[position][stat_name], dtype=float)
                values = values[np.isfinite(values)]
                if values.size == 0:
                    continue

                # Only show legend on the very first subplot
                showlegend = self.style.show_legend and stat_idx == 0 and pos_idx == 0

                lw = condition.style.line_width or self.style.line_width
                ls = condition.style.line_style or self.style.line_style

                if self.distribution_kind in {"histogram", "both"}:
                    self._render_histogram(
                        values=values,
                        label=condition.label,
                        color=condition.style.color,
                        opacity=condition.style.alpha,
                        line_width=lw,
                        line_style=ls,
                        row=row,
                        col=col,
                        showlegend=showlegend,
                        legendgroup=condition.label,
                    )

                if self.distribution_kind in {"kde", "both"}:
                    self._compute_and_render_kde(
                        values=values,
                        label=condition.label,
                        color=condition.style.color,
                        opacity=condition.style.alpha,
                        line_width=lw,
                        line_style=ls,
                        row=row,
                        col=col,
                        showlegend=showlegend and self.distribution_kind != "both",
                        legendgroup=condition.label,
                    )

    def _compute_and_render_kde(
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
        """Compute KDE then call _render_kde or _render_kde_fallback."""
        if values.size > 2:
            try:
                vmin, vmax = float(values.min()), float(values.max())
                if vmin == vmax:
                    pad = max(1e-6, abs(vmin) * 1e-3 or 1e-3)
                    vmin, vmax = vmin - pad, vmax + pad

                x_range = np.linspace(vmin, vmax, 200)
                density = gaussian_kde(values)(x_range)

                self._render_kde(
                    x_range=x_range,
                    density=density,
                    label=label,
                    color=color,
                    opacity=opacity,
                    line_width=line_width,
                    line_style=line_style,
                    row=row,
                    col=col,
                    showlegend=showlegend,
                    legendgroup=legendgroup,
                )
                return
            except Exception as e:
                self.logger.warning(
                    f"KDE failed for '{label}' (row={row}, col={col}): {e}"
                )

        # Fallback for n<=2 or KDE failure
        self._render_kde_fallback(
            values=values,
            label=label,
            color=color,
            opacity=opacity,
            row=row,
            col=col,
            showlegend=showlegend,
            legendgroup=legendgroup,
        )
