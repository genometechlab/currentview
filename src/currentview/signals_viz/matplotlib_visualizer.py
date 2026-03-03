import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
from pathlib import Path
from typing import Dict, List, Optional, Union

from .base_visualizer import BaseSignalVisualizer
from ..utils.data_classes import Condition
from ..utils.plotly_utils import PlotStyle
from ..utils.color_utils import get_contrasting_color


class MatplotlibSignalVisualizer(BaseSignalVisualizer):
    """
    Matplotlib backend — static PNG output, notebook-friendly, lightweight.
    Renders to an inline PNG instead of embedding JSON, so notebooks stay small.
    Alpha stacking works naturally since each read is its own Line2D.
    """

    # =========================================================================
    # Figure creation
    # =========================================================================

    def _create_figure(self):
        if self.style.mpl_style:
            plt.style.use(self.style.mpl_style)

        self.fig, self.ax = plt.subplots(figsize=self.style.figsize)

        # Apply shared style settings via the helper on PlotStyle
        self.style.apply_to_mpl_axes(self.ax, title_text=self.title)

        self.ax.set_xlabel(
            "Genomic Position",
            fontsize=self.style.axis_title_font_size,
            color=self.style.axis_title_color,
        )
        self.ax.set_ylabel(
            "Signal (pA)",
            fontsize=self.style.axis_title_font_size,
            color=self.style.axis_title_color,
        )

        self.ax.set_xlim(-0.1, self.K - self.style.positions_padding + 0.1)

        # Tighten layout using margins (convert pixels → figure fraction)
        m = self.style.margin
        w_px, h_px = self.style.width, self.style.height
        self.fig.subplots_adjust(
            left=m["l"] / w_px,
            right=1 - m["r"] / w_px,
            top=1 - m["t"] / h_px,
            bottom=m["b"] / h_px,
        )

        # Internal bookkeeping
        # legend handles: label -> Line2D proxy
        self._legend_handles: Dict[str, Line2D] = {}
        # highlight patches: uid -> Rectangle
        self._highlight_patches: Dict[str, mpatches.Rectangle] = {}
        # annotation texts: uid -> Text
        self._annotation_texts: Dict[str, plt.Text] = {}
        # per-condition lines: label -> list of Line2D
        self._condition_lines: Dict[str, List] = {}

    def _add_position_barriers(self):
        from ..utils.color_utils import to_mpl_color

        pad = self.style.positions_padding
        for i in range(self.K + 1):
            x = i - pad / 2
            self.ax.axvline(
                x=x,
                color=to_mpl_color(self.style.barrier_color),
                linewidth=1.5,
                linestyle=self.style.mpl_barrier_linestyle,
                alpha=self.style.barrier_opacity,
                zorder=0,
            )

    def _apply_custom_labels(self):
        tick_pos = np.arange(self.K) + 0.5 - self.style.positions_padding / 2
        self.ax.set_xticks(tick_pos)
        self.ax.set_xticklabels(
            [str(l) for l in self.window_labels],
            fontsize=self.style.tick_font_size,
        )

    def _update_position_labels(self):
        tick_pos = np.arange(self.K) + 0.5 - self.style.positions_padding / 2
        self.ax.set_xticks(tick_pos)
        half = self.K // 2
        tick_text = [str(i) for i in range(-half, half + 1)]
        self.ax.set_xticklabels(tick_text, fontsize=self.style.tick_font_size)

    # =========================================================================
    # Signal rendering
    # =========================================================================

    def _plot_signals(self, condition: Condition):
        col = condition.style.color
        alp = condition.style.alpha
        lw = condition.style.line_width or self.style.line_width
        ls = condition.style.line_style or self.style.line_style
        mpl_ls = self.style.mpl_linestyle  # uses style's line_style field

        # Override with condition-specific line style if set
        if condition.style.line_style:
            from ..utils.plotly_utils import PlotStyle as _PS

            _tmp = _PS(line_style=condition.style.line_style)
            mpl_ls = _tmp.mpl_linestyle

        lines_for_condition = []

        for read in condition.reads:
            mx, my, ix, iy = self._build_read_arrays(read, condition.positions)
            if mx is None:
                continue

            self._track_y(my)

            (line,) = self.ax.plot(
                mx,
                my,
                color=col,
                alpha=alp,
                linewidth=lw,
                linestyle=mpl_ls,
                zorder=2,
            )
            lines_for_condition.append(line)

            if ix is not None:
                (ins_line,) = self.ax.plot(
                    ix,
                    iy,
                    color=col,
                    alpha=alp,
                    linewidth=lw,
                    linestyle=":",  # dotted for insertions
                    zorder=2,
                )
                lines_for_condition.append(ins_line)

        self._condition_lines[condition.label] = lines_for_condition

        # Legend proxy — one entry per condition, full opacity
        if self.style.show_legend:
            proxy = Line2D(
                [0],
                [0],
                color=col,
                linewidth=lw,
                linestyle=mpl_ls,
                alpha=1.0,
                label=condition.label,
            )
            self._legend_handles[condition.label] = proxy
            self._refresh_legend()

    def _do_remove_condition_traces(self, label: str):
        for line in self._condition_lines.pop(label, []):
            line.remove()
        self._legend_handles.pop(label, None)
        self._refresh_legend()

    def _recompute_ylim_from_figure(self):
        for lines in self._condition_lines.values():
            for line in lines:
                ydata = np.asarray(line.get_ydata(), dtype=np.float32)
                self._track_y(ydata)

    def _refresh_legend(self):
        """Rebuild legend from current proxy handles."""
        if not self.style.show_legend or not self._legend_handles:
            if self.ax.get_legend():
                self.ax.get_legend().remove()
            return

        handles = list(self._legend_handles.values())
        from ..utils.color_utils import to_mpl_color

        self.ax.legend(
            handles=handles,
            loc=self.style.mpl_legend_loc,
            bbox_to_anchor=(self.style.legend_x, self.style.legend_y),
            fontsize=self.style.legend_font_size,
            framealpha=0.8,
            edgecolor=to_mpl_color(self.style.legend_bordercolor),
            facecolor=to_mpl_color(self.style.legend_bgcolor),
        )

    # =========================================================================
    # Highlights (basic support)
    # =========================================================================

    def _do_highlight(self, uid: str, window_idx: int, color: str, alpha: float):
        pad = self.style.positions_padding
        x0 = window_idx - pad / 2
        width = 1.0  # one position wide

        # axvspan is simpler but doesn't give us a handle to remove it easily,
        # so we use a Rectangle on the axes transform instead
        rect = mpatches.Rectangle(
            (x0, 0),
            width,
            1,
            transform=self.ax.get_xaxis_transform(),  # x in data, y in axes [0,1]
            color=color,
            alpha=alpha,
            linewidth=0,
            zorder=1,
        )
        self.ax.add_patch(rect)
        self._highlight_patches[uid] = rect

    def _do_clear_highlights(self):
        for uid in list(self._highlight_shapes):
            patch = self._highlight_patches.pop(uid, None)
            if patch is not None:
                patch.remove()

    # =========================================================================
    # Annotations (basic support)
    # =========================================================================

    def _do_add_annotation(
        self, uid, x_pos, y_pos, text, color, fontsize, fontcolor, **kwargs
    ):
        txt = self.ax.text(
            x_pos,
            y_pos,
            text,
            fontsize=fontsize,
            color=fontcolor,
            ha="center",
            va="top",
            bbox=dict(
                boxstyle="round,pad=0.3", facecolor=color, edgecolor="none", alpha=0.8
            ),
            zorder=5,
        )
        self._annotation_texts[uid] = txt

    def _do_clear_annotations(self):
        for uid in list(self._annotation_indices):
            txt = self._annotation_texts.pop(uid, None)
            if txt is not None:
                txt.remove()

    # =========================================================================
    # Axes, title, display, save
    # =========================================================================

    def _do_set_ylim(self, lo: float, hi: float):
        self.ax.set_ylim(lo, hi)

    def _do_set_title(self, title: str):
        self.ax.set_title(
            title,
            fontsize=self.style.title_font_size,
            color=self.style.title_color,
            fontfamily=self.style.mpl_font_family,
        )

    def get_fig(self):
        return self.fig

    def show(self):
        """Display inline in notebook and return figure."""
        plt.show()
        return self.fig

    def save(
        self,
        path: Union[str, Path],
        format: Optional[str] = None,
        dpi: Optional[int] = None,
        **kwargs,
    ):
        path = Path(path)
        fmt = format or path.suffix.lstrip(".").lower() or "png"
        self.fig.savefig(
            str(path),
            format=fmt,
            dpi=dpi or self.style.dpi,
            facecolor=self.style.paper_bgcolor,
            bbox_inches="tight",
            **kwargs,
        )
        self.logger.info(f"Saved figure to {path}")
