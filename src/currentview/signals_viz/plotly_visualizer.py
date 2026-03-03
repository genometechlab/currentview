import numpy as np
import plotly.graph_objects as go
from pathlib import Path
from typing import Dict, List, Optional, Union

from .base_visualizer import BaseSignalVisualizer
from ..utils.data_classes import Condition
from ..utils.plotly_utils import PlotStyle
from ..utils.color_utils import get_contrasting_color


class PlotlySignalVisualizer(BaseSignalVisualizer):
    """Plotly backend — interactive, heavier, best for exploration."""

    # =========================================================================
    # Figure creation
    # =========================================================================

    def _create_figure(self):
        self.fig = go.Figure()
        self._plot_func = go.Scattergl if self.style.renderer == "WebGL" else go.Scatter

        layout = self.style.get_layout_dict()

        layout.setdefault("title", {}).update(
            {
                "text": self.title,
                "x": 0.5,
                "xanchor": "center",
                "font": {"size": self.style.title_font_size},
            }
        )

        layout.setdefault("xaxis", {}).update(
            {
                "title": {"text": "Genomic Position"},
                "showgrid": False,
                "tickmode": "array",
                "tickvals": [],
                "ticktext": [],
                "range": [-0.1, self.K - self.style.positions_padding + 0.1],
            }
        )

        layout.setdefault("yaxis", {}).update({"title": {"text": "Signal (pA)"}})

        self.fig.update_layout(**layout)

    def _add_position_barriers(self):
        pad = self.style.positions_padding
        for i in range(self.K + 1):
            self.fig.add_shape(
                type="line",
                x0=i - pad / 2,
                x1=i - pad / 2,
                y0=0,
                y1=1,
                yref="paper",
                line=dict(
                    color=self.style.barrier_color,
                    width=1.5,
                    dash=self.style.barrier_style,
                ),
                layer="below",
                opacity=self.style.barrier_opacity,
            )

    def _apply_custom_labels(self):
        tick_pos = np.arange(self.K) + 0.5 - self.style.positions_padding / 2
        self.fig.update_xaxes(
            tickmode="array",
            tickvals=tick_pos,
            ticktext=[str(l) for l in self.window_labels],
        )

    def _update_position_labels(self):
        tick_pos = np.arange(self.K) + 0.5 - self.style.positions_padding / 2

        if not self._conditions_info:
            tick_text = [str(i) for i in range(self.K)]
        elif len(self._conditions_info) == 1:
            label = next(iter(self._conditions_info))
            tick_text = self._conditions_info[label].get("pos_labels") or [
                str(i) for i in range(self.K)
            ]
        else:
            tick_text = []
            for i in range(self.K):
                lines = []
                for label, info in self._conditions_info.items():
                    color = info["style"].color
                    text = info["pos_labels"][i] if info["pos_labels"] else str(i)
                    lines.append(f"<span style='color:{color}'>{text}</span>")
                tick_text.append("<br>".join(lines))

        self.fig.update_xaxes(tickmode="array", tickvals=tick_pos, ticktext=tick_text)

    # =========================================================================
    # Signal rendering
    # =========================================================================

    def _plot_signals(self, condition: Condition):
        col = condition.style.color
        alp = condition.style.alpha
        lw = condition.style.line_width or self.style.line_width
        ls = condition.style.line_style or self.style.line_style

        for read in condition.reads:
            mx, my, ix, iy = self._build_read_arrays(read, condition.positions)
            if mx is None:
                continue

            # Track y range incrementally
            self._track_y(my)

            self.fig.add_trace(
                self._plot_func(
                    x=mx,
                    y=my,
                    cliponaxis=False,
                    mode="lines",
                    name=condition.label,
                    legendgroup=condition.label,
                    meta={"cond": condition.label, "kind": "read"},
                    showlegend=False,
                    line=dict(color=col, width=lw, dash=ls),
                    opacity=alp,
                    hovertemplate="Position: %{x:.2f}<br>Signal: %{y:.1f} pA<extra></extra>",
                )
            )

            if ix is not None:
                self.fig.add_trace(
                    self._plot_func(
                        x=ix,
                        y=iy,
                        cliponaxis=False,
                        mode="lines",
                        name=condition.label,
                        legendgroup=condition.label,
                        meta={"cond": condition.label, "kind": "insertions"},
                        showlegend=False,
                        line=dict(color=col, width=lw, dash="dot"),
                        opacity=alp,
                        hovertemplate="Position: %{x:.2f}<br>Signal: %{y:.1f} pA<extra></extra>",
                    )
                )

        if self.style.show_legend:
            self.fig.add_trace(
                self._plot_func(
                    x=[np.nan],
                    y=[np.nan],
                    cliponaxis=False,
                    mode="lines",
                    name=condition.label,
                    legendgroup=condition.label,
                    meta={"cond": condition.label, "kind": "legend"},
                    showlegend=True,
                    line=dict(color=col, width=lw, dash=ls),
                    opacity=1.0,
                    hoverinfo="skip",
                )
            )

    def _do_remove_condition_traces(self, label: str):
        self.fig.data = tuple(
            tr for tr in self.fig.data if getattr(tr, "meta", {}).get("cond") != label
        )

    def _recompute_ylim_from_figure(self):
        for tr in self.fig.data:
            arr = getattr(tr, "y", None)
            if arr is None:
                continue
            arr = np.asarray(arr, dtype=np.float32)
            self._track_y(arr)

    # =========================================================================
    # Highlights and annotations
    # =========================================================================

    def _do_highlight(self, uid: str, window_idx: int, color: str, alpha: float):
        pad = self.style.positions_padding
        self.fig.add_shape(
            type="rect",
            x0=window_idx - pad / 2,
            x1=window_idx + 1 - pad / 2,
            y0=0,
            y1=1,
            yref="paper",
            fillcolor=color,
            opacity=alpha,
            line=dict(width=0),
            layer="below",
            name=uid,
        )

    def _do_clear_highlights(self):
        self.fig.layout.shapes = tuple(
            s
            for s in self.fig.layout.shapes
            if not (hasattr(s, "name") and s.name in self._highlight_shapes)
        )

    def _do_add_annotation(
        self, uid, x_pos, y_pos, text, color, fontsize, fontcolor, **kwargs
    ):
        self.fig.add_annotation(
            x=x_pos,
            y=y_pos,
            text=text,
            showarrow=False,
            font=dict(size=fontsize, color=fontcolor),
            bgcolor=color,
            borderpad=4,
            name=uid,
            **kwargs,
        )

    def _do_clear_annotations(self):
        self.fig.layout.annotations = tuple(
            a
            for a in self.fig.layout.annotations
            if not (hasattr(a, "name") and a.name in self._annotation_indices)
        )

    # =========================================================================
    # Axes, title, display
    # =========================================================================

    def _do_set_ylim(self, lo: float, hi: float):
        self.fig.update_yaxes(range=[lo, hi])

    def _do_set_title(self, title: str):
        self.fig.update_layout(
            title={
                "text": title,
                "font": {"size": self.style.title_font_size},
                "x": 0.5,
                "xanchor": "center",
            }
        )

    def get_fig(self):
        return self.fig

    def show(self):
        self.fig.show()

    def save(
        self,
        path: Union[str, Path],
        format: Optional[str] = None,
        scale: Optional[float] = None,
        **kwargs,
    ):
        path = Path(path)
        fmt = format or path.suffix.lstrip(".").lower() or "png"
        try:
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
            self.logger.info(f"Saved figure to {path}")
        except Exception as e:
            self.logger.error(f"Failed to save: {e}")
            raise
