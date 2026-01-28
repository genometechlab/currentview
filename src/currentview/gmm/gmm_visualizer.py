# gmm_visualizer.py
from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Tuple, Union

import numpy as np
import plotly.graph_objects as go

from .gmm_handler import ConditionGMM
from ..utils.plotly_utils import PlotStyle


class GMMVisualizer:
    """
    Plotly visualizer for ConditionGMM records (scatter + iso-mass contour lines).

    - Axis labels can be provided at init / from_handler (fallback: handler.stat1/stat2).
    - `plot_gmms()` populates the figure with contours/points/means from ConditionGMMs.
    - `show()` displays AND returns the figure; `get_fig()` just returns; `save()` writes to disk.

    Internal plotting params not in PlotStyle are kept fixed (sensible defaults):
      * grid: nx=250, ny=250, proportional padding (5% range, min 0.5)
      * iso-mass levels: linspace(0.60, 0.98, 7)
      * marker size: 6 (means: 12)
      * opacity: auto (based on N) unless PlotStyle.opacity_mode == "fixed"
    """

    # Fixed internal defaults (not in PlotStyle)
    _NX: int = 250
    _NY: int = 250
    _PAD_FRAC: float = 0.05  # 5% of data range per axis
    _PAD_MIN: float = 0.5  # absolute minimum pad per axis
    _N_LEVELS: int = 7
    _MASS_START: float = 0.60
    _MASS_END: float = 0.98
    _MARKER_SIZE: int = 6
    _MEAN_MARKER_SIZE: int = 12
    _EPS_NUM: float = 1e-12  # numerical floor for exp(logp)

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
        self.x_label = x_label or "stat1"
        self.y_label = y_label or "stat2"
        self.title = title or "GMM scatter with iso-mass contours"
        self.logger = logger or logging.getLogger(__name__)

        self.fig: Optional[go.Figure] = None
        # Shared grid cache (built when plotting)
        self._x = self._y = self._Xg = self._Yg = self._XX = None

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
    ) -> "GMMVisualizer":
        # Default axis labels from handler if not passed explicitly
        xl = x_label or handler.stat1.label
        yl = y_label or handler.stat2.label
        cls_ = cls(
            style=style,
            x_label=xl,
            y_label=yl,
            title=title,
            logger=logger,
        )
        cls_.plot_gmms(handler.conditions_gmms_.values())
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
        # Newer Plotly expects 'title' inside xaxis/yaxis dicts
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

    def plot_gmms(self, records: Iterable[ConditionGMM], *, clear: bool = True) -> go.Figure:
        """
        Populate the figure with iso-mass contours, points, and means for the given records.
        """
        if clear:
            self._create_figure()
        records = list(records) if records is not None else []
        if not records:
            raise ValueError("No records provided to plot_gmms()")

        records = [r for r in records]
        self._warn_if_all_invalid(records)

        # Build shared grid over *valid* records
        self._x, self._y, self._Xg, self._Yg, self._XX = self._build_shared_grid(
            records
        )

        # Choose shared iso-mass semantics; thresholds per-condition
        mass_levels = np.linspace(self._MASS_START, self._MASS_END, self._N_LEVELS)

        # Choose scatter class based on PlotStyle.renderer
        scatter_cls = (
            go.Scattergl
            if getattr(self.style, "renderer", "WebGL") == "WebGL"
            else go.Scatter
        )

        for rec in records:
            if (rec.model is None) or (rec.X is None) or (rec.X.size == 0):
                continue

            # PDF on the shared grid
            logp = rec.model.score_samples(self._XX)  # (nx*ny,)
            logp = np.clip(logp, a_min=np.log(self._EPS_NUM), a_max=None)
            pdf = np.exp(logp).reshape(self._Xg.shape)

            thresholds = self._mass_thresholds(pdf, mass_levels)

            color = getattr(rec.style, "color", "#444")
            label = rec.label

            # Contours: draw (pdf - thr) == 0 as a line per mass level
            for i, thr in enumerate(thresholds):
                self.fig.add_trace(
                    go.Contour(
                        x=self._x,
                        y=self._y,
                        z=(pdf - float(thr)),
                        contours=dict(start=0.0, end=0.0, size=1.0, coloring="lines"),
                        line=dict(width=self.style.line_width, color=color),
                        colorscale=[[0, color], [1, color]],
                        showscale=False,
                        name=(
                            f"{label} isomass" if i == 0 else None
                        ),  # one legend entry per condition
                        hoverinfo="skip",
                        showlegend=self.style.show_legend and (i == 0),
                        legendgroup=label,
                    )
                )

            # Points
            opacity = (
                self.style.fixed_opacity
                if getattr(self.style, "opacity_mode", "auto") == "fixed"
                else self._auto_opacity(len(rec.X))
            )
            self.fig.add_trace(
                scatter_cls(
                    x=rec.X[:, 0],
                    y=rec.X[:, 1],
                    mode="markers",
                    name=f"{label} points",
                    marker=dict(size=self._MARKER_SIZE, opacity=opacity, color=color),
                    showlegend=self.style.show_legend,
                    legendgroup=label,
                )
            )

            # GMM means
            if hasattr(rec.model, "means_"):
                k = getattr(rec, "selected_n_components", None) or len(rec.model.means_)
                self.fig.add_trace(
                    go.Scatter(
                        x=rec.model.means_[:, 0],
                        y=rec.model.means_[:, 1],
                        mode="markers",
                        name=f"{label} means (k={k})",
                        marker=dict(
                            size=self._MEAN_MARKER_SIZE, symbol="x", color=color
                        ),
                        showlegend=self.style.show_legend,
                        legendgroup=label,
                    )
                )

        # Fix axis ranges so the plot doesn't collapse
        if self._x is not None and self._y is not None:
            self.fig.update_xaxes(range=[self._x[0], self._x[-1]])
            self.fig.update_yaxes(range=[self._y[0], self._y[-1]])

        return self.fig

    def show(self):
        """Display the plot"""
        self.logger.info("Displaying plot")
        self.fig.show()

    def get_fig(self) -> go.Figure:
        """Return the current figure (create + populate if needed)."""
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
                    "height": self.style.height
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
    def _warn_if_all_invalid(self, recs: List[ConditionGMM]) -> None:
        invalid = [
            getattr(r, "label", "unnamed")
            for r in recs
            if (r.model is None) or (r.X is None) or (r.X.size == 0)
        ]
        if len(invalid) == len(recs):
            raise ValueError(
                "All records have empty data or missing models; nothing to visualize."
            )
        if invalid:
            print(
                f"[GMMVisualizer] Warning: Skipping records without data/model: {invalid}"
            )

    def _build_shared_grid(
        self, recs: List[ConditionGMM]
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        pts = [r.X for r in recs if (r.X is not None and r.X.size > 0)]
        if not pts:
            pts = [np.array([[0.0, 0.0]])]
        all_pts = np.vstack(pts)

        xlo, ylo = all_pts.min(axis=0)
        xhi, yhi = all_pts.max(axis=0)
        dx = float(xhi - xlo)
        dy = float(yhi - ylo)

        # Proportional padding with absolute floors
        pad_x = max(self._PAD_MIN, self._PAD_FRAC * dx)
        pad_y = max(self._PAD_MIN, self._PAD_FRAC * dy)

        if dx <= 1e-12:
            xlo -= self._PAD_MIN
            xhi += self._PAD_MIN
        else:
            xlo -= pad_x
            xhi += pad_x

        if dy <= 1e-12:
            ylo -= self._PAD_MIN
            yhi += self._PAD_MIN
        else:
            ylo -= pad_y
            yhi += pad_y

        x = np.linspace(xlo, xhi, self._NX)
        y = np.linspace(ylo, yhi, self._NY)
        Xg, Yg = np.meshgrid(x, y)
        XX = np.column_stack([Xg.ravel(), Yg.ravel()])
        return x, y, Xg, Yg, XX

    def _mass_thresholds(self, pdf: np.ndarray, mass_levels: np.ndarray) -> List[float]:
        """
        Given a pdf on a uniform grid, return density thresholds whose superlevel sets
        {x: pdf(x) >= t} enclose the requested mass levels (iso-mass).
        """
        p = pdf.ravel().astype(float)
        if not np.all(np.isfinite(p)):
            p = np.nan_to_num(p, nan=0.0, posinf=0.0, neginf=0.0)

        order = np.argsort(p)[::-1]  # descending by density
        p_sorted = p[order]
        c = np.cumsum(p_sorted)
        total = c[-1]
        if total <= 0:
            return [float(np.nanmin(p))] * len(mass_levels)
        c /= total

        thresholds: List[float] = []
        for m in mass_levels:
            mm = float(np.clip(m, 1e-6, 1 - 1e-6))
            j = int(np.searchsorted(c, mm, side="left"))
            j = min(j, len(p_sorted) - 1)
            thresholds.append(p_sorted[j])
        return thresholds

    @staticmethod
    def _auto_opacity(n: int) -> float:
        if n <= 100:
            return 0.8
        if n <= 500:
            return 0.6
        if n <= 2000:
            return 0.4
        return 0.25
