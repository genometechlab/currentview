import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
from typing import List, Optional, Union

from .base_visualizer import BaseStatsVisualizer
from ..utils.data_classes import Condition
from ..utils.plotly_utils import PlotStyle
from ..utils.color_utils import to_rgba_str


class PlotlyStatsVisualizer(BaseStatsVisualizer):
    """Plotly backend for stats — interactive subplots with KDE/histogram."""

    # =========================================================================
    # Figure creation
    # =========================================================================

    def _create_figure(self):
        self._plot_func = go.Scattergl if self.style.renderer == "WebGL" else go.Scatter

        column_titles = self.window_labels or [
            str(i) for i in range(-(self.K // 2), self.K // 2 + self.K % 2)
        ]
        column_titles = [str(t) for t in column_titles[: self.K]]

        v_spacing = self.style.subplot_vertical_spacing or (
            0.15 / self.n_stats if self.n_stats > 1 else 0
        )
        h_spacing = self.style.subplot_horizontal_spacing or (
            0.1 / self.K if self.K > 1 else 0
        )

        self.fig = make_subplots(
            rows=self.n_stats,
            cols=self.K,
            subplot_titles=None,
            row_titles=self.stats_names,
            column_titles=column_titles,
            vertical_spacing=v_spacing,
            horizontal_spacing=h_spacing,
            specs=[
                [{"type": "xy"} for _ in range(self.K)] for _ in range(self.n_stats)
            ],
        )

        layout_dict = self.style.get_layout_dict()
        xaxis_layout = layout_dict.pop("xaxis", {}) or {}
        yaxis_layout = layout_dict.pop("yaxis", {}) or {}

        layout_dict.setdefault("title", {}).update(
            {
                "text": self.title,
                "font": {"size": self.style.title_font_size},
                "x": 0.5,
                "xanchor": "center",
            }
        )

        xaxis_layout["tickangle"] = 90
        yaxis_layout.update({"showticklabels": False, "ticks": "", "showgrid": False})

        self.fig.update_layout(**layout_dict)

        for row in range(1, self.n_stats + 1):
            for col in range(1, self.K + 1):
                self.fig.update_xaxes(title_text=None, **xaxis_layout, row=row, col=col)
                self.fig.update_yaxes(
                    title_text="Density" if col == 1 else "",
                    **yaxis_layout,
                    row=row,
                    col=col,
                )

    # =========================================================================
    # Rendering
    # =========================================================================

    def _render_histogram(
        self,
        values,
        label,
        color,
        opacity,
        line_width,
        line_style,
        row,
        col,
        showlegend,
        legendgroup,
    ):
        fill_color = to_rgba_str(color, 0.2)
        self.fig.add_trace(
            go.Histogram(
                x=values,
                histnorm="probability density",
                nbinsx=30,
                name=label,
                marker=dict(color=fill_color, line=dict(color=color, width=line_width)),
                opacity=0.7,
                showlegend=showlegend,
                legendgroup=legendgroup,
                meta={"cond": label, "kind": "hist"},
                hovertemplate="%{x}<br>Density: %{y}<extra></extra>",
            ),
            row=row,
            col=col,
        )

    def _render_kde(
        self,
        x_range,
        density,
        label,
        color,
        opacity,
        line_width,
        line_style,
        row,
        col,
        showlegend,
        legendgroup,
    ):
        fill_color = to_rgba_str(color, 0.2)
        self.fig.add_trace(
            self._plot_func(
                x=x_range,
                y=density,
                cliponaxis=False,
                mode="lines",
                name=label,
                line=dict(color=color, width=line_width, dash=line_style),
                fill="tozeroy" if self.distribution_kind == "kde" else None,
                fillcolor=fill_color if self.distribution_kind == "kde" else None,
                showlegend=showlegend,
                legendgroup=legendgroup,
                meta={"cond": label, "kind": "kde"},
                hovertemplate="%{x:.2f}<br>Density: %{y:.3f}<extra></extra>",
            ),
            row=row,
            col=col,
        )

    def _render_kde_fallback(
        self, values, label, color, opacity, row, col, showlegend, legendgroup
    ):
        y_jitter = np.random.normal(0, 0.02, values.size)
        self.fig.add_trace(
            self._plot_func(
                x=values,
                y=y_jitter,
                cliponaxis=False,
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

    def _do_remove_condition_traces(self, label: str):
        self.fig.data = tuple(
            tr for tr in self.fig.data if getattr(tr, "meta", {}).get("cond") != label
        )

    def _do_set_title(self, title: str):
        self.fig.update_layout(
            title={
                "text": title,
                "font": {"size": self.style.title_font_size},
                "x": 0.5,
                "xanchor": "center",
            }
        )

    # =========================================================================
    # Display / save
    # =========================================================================

    def get_fig(self):
        return self.fig

    def show(self):
        self.fig.show()

    def save(self, path, format=None, scale=None, **kwargs):
        from pathlib import Path

        path = Path(path)
        fmt = format or path.suffix.lstrip(".").lower() or "png"
        if fmt == "html":
            self.fig.write_html(str(path), **kwargs)
        else:
            self.fig.write_image(
                str(path),
                format=fmt,
                scale=scale or self.style.toImageButtonOptions.get("scale", 2),
                width=self.style.width,
                height=self.style.height,
                **kwargs,
            )
        self.logger.info(f"Saved stats figure to {path}")
