# umap_visualizer.py
from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Union

import numpy as np
import plotly.graph_objects as go

from .umap_handler import ConditionUMAP
from ..utils.plotly_utils import PlotStyle


class UMAPVisualizer:
    """
    Plotly visualizer for ConditionUMAP records (scatter plots of 2D embeddings).

    - Axis labels can be provided at init / from_handler (fallback: UMAP1/UMAP2).
    - `plot_umaps()` populates the figure with scatter points from ConditionUMAPs.
    - `show()` displays AND returns the figure; `get_fig()` just returns; `save()` writes to disk.
    """

    _MARKER_SIZE: int = 6

    def __init__(
        self,
        *,
        style: Optional[PlotStyle] = None,
        x_label: Optional[str] = None,
        y_label: Optional[str] = None,
        title: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
    ):
        self.style: PlotStyle = style or PlotStyle.get_style("interactive")
        self.x_label = x_label or "UMAP1"
        self.y_label = y_label or "UMAP2"
        self.title = title or "UMAP Embeddings"
        self.logger = logger or logging.getLogger(__name__)

        self.fig: Optional[go.Figure] = None

        self._create_figure()

    @classmethod
    def from_handler(
        cls,
        handler,
        *,
        style: Optional[PlotStyle] = None,
        x_label: Optional[str] = None,
        y_label: Optional[str] = None,
        title: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
    ) -> "UMAPVisualizer":
        # Default axis labels
        xl = x_label or "UMAP1"
        yl = y_label or "UMAP2"
        cls_ = cls(
            style=style,
            x_label=xl,
            y_label=yl,
            title=title,
            logger=logger,
        )
        cls_.plot_umaps(handler.conditions_umaps_.values())
        return cls_

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------
    def _create_figure(self) -> go.Figure:
        """Create an empty styled figure (no traces)."""
        self.logger.debug("Creating empty figure with styled layout")
        self.fig = go.Figure()
        layout = self.style.get_layout_dict()

        # Title & axis labels
        layout.setdefault("title", {})
        layout["title"]["text"] = self.title

        layout.setdefault("xaxis", layout.get("xaxis", {}))
        layout["xaxis"]["title"] = {
            "text": self.x_label,
            **layout["xaxis"].get("title", {}),
        }

        layout.setdefault("yaxis", layout.get("yaxis", {}))
        layout["yaxis"]["title"] = {
            "text": self.y_label,
            **layout["yaxis"].get("title", {}),
        }

        self.fig.update_layout(**layout)
        return self.fig

    def plot_umaps(
        self, records: Iterable[ConditionUMAP], *, clear: bool = True
    ) -> go.Figure:
        """
        Populate the figure with scatter plots for the given UMAP records.
        """
        if clear:
            self._create_figure()

        records = list(records) if records is not None else []
        if not records:
            raise ValueError("No records provided to plot_umaps()")

        self._warn_if_all_invalid(records)

        # Choose scatter class based on PlotStyle.renderer
        scatter_cls = (
            go.Scattergl
            if getattr(self.style, "renderer", "WebGL") == "WebGL"
            else go.Scatter
        )

        for rec in records:
            if rec.embedding is None or rec.embedding.size == 0:
                continue

            color = getattr(rec.style, "color", "#444")
            label = rec.label

            # Add scatter trace
            self.fig.add_trace(
                scatter_cls(
                    x=rec.embedding[:, 0],
                    y=rec.embedding[:, 1],
                    mode="markers",
                    name=label,
                    marker=dict(size=self._MARKER_SIZE, color=color),
                    showlegend=self.style.show_legend,
                    legendgroup=label,
                )
            )

        return self.fig

    def show(self):
        """Display the plot"""
        self.logger.info("Displaying plot")
        self.fig.show()

    def get_fig(self) -> go.Figure:
        """Return the current figure."""
        self.logger.info("Returning fig")
        return self.fig

    def save(
        self,
        path: Union[str, Path],
        *,
        format: Optional[str] = None,
        scale: Optional[float] = None,
        **kwargs,
    ):
        """Save the figure to file."""
        path = Path(path)

        if format is None:
            format = path.suffix.lstrip(".").lower() or "png"

        self.logger.debug(f"Saving figure: path={path}, format={format}")

        try:
            if format == "html":
                self.fig.write_html(str(path), **kwargs)
            else:
                write_kwargs = {
                    "format": format,
                    "scale": scale or self.style.toImageButtonOptions.get("scale", 2),
                    "width": self.style.width,
                    "height": self.style.height,
                }
                write_kwargs.update(kwargs)
                self.fig.write_image(str(path), **write_kwargs)

            self.logger.info(f"Saved figure to {path}")
        except Exception as e:
            self.logger.error(f"Failed to save figure: {type(e).__name__}: {str(e)}")
            raise e

    # ---------------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------------
    def _warn_if_all_invalid(self, recs: List[ConditionUMAP]) -> None:
        invalid = [
            getattr(r, "label", "unnamed")
            for r in recs
            if r.embedding is None or r.embedding.size == 0
        ]
        if len(invalid) == len(recs):
            raise ValueError("All records have empty embeddings; nothing to visualize.")
        if invalid:
            self.logger.warning(f"Skipping records without embeddings: {invalid}")
