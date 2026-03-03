import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.lines import Line2D
from pathlib import Path
from typing import Dict, List, Optional, Union

from .base_visualizer import BaseStatsVisualizer
from ..utils.plotly_utils import PlotStyle
from ..utils.color_utils import to_mpl_color


class MatplotlibStatsVisualizer(BaseStatsVisualizer):
    """
    Matplotlib backend for stats — static PNG subplots, notebook-friendly.
    Full parity with Plotly backend: KDE, histogram, and both modes supported.
    """

    # =========================================================================
    # Figure creation
    # =========================================================================

    def _create_figure(self):
        if self.style.mpl_style:
            plt.style.use(self.style.mpl_style)

        self.fig = plt.figure(figsize=self.style.figsize)
        self.fig.patch.set_facecolor(to_mpl_color(self.style.paper_bgcolor))

        # Build grid: n_stats rows x K cols
        self._gs = gridspec.GridSpec(
            self.n_stats,
            self.K,
            figure=self.fig,
            hspace=self.style.subplot_vertical_spacing or 0.5,
            wspace=self.style.subplot_horizontal_spacing or 0.15,
        )

        # Create all axes upfront and store in a 2D list [row][col] (0-indexed)
        self._axes: List[List[plt.Axes]] = []
        half = self.K // 2
        col_labels = self.window_labels or [str(i) for i in range(-half, half + 1)]

        for r in range(self.n_stats):
            row_axes = []
            for c in range(self.K):
                ax = self.fig.add_subplot(self._gs[r, c])
                self.style.apply_to_mpl_axes(ax)
                ax.set_facecolor(to_mpl_color(self.style.plot_bgcolor))

                # Column header (position label) — top row only
                if r == 0:
                    ax.set_title(
                        str(col_labels[c]),
                        fontsize=self.style.subplot_title_font_size,
                        color=to_mpl_color(self.style.title_color),
                        pad=4,
                    )

                # Y-axis label — leftmost column only
                if c == 0:
                    ax.set_ylabel(
                        self.stats_names[r],
                        fontsize=self.style.axis_title_font_size,
                        color=to_mpl_color(self.style.axis_title_color),
                    )
                else:
                    ax.set_yticklabels([])
                    ax.set_yticks([])

                # X tick rotation to match Plotly
                ax.tick_params(
                    axis="x", rotation=90, labelsize=self.style.tick_font_size
                )
                ax.tick_params(axis="y", labelsize=self.style.tick_font_size)

                row_axes.append(ax)
            self._axes.append(row_axes)

        # Overall figure title
        self.fig.suptitle(
            self.title,
            fontsize=self.style.title_font_size,
            color=to_mpl_color(self.style.title_color),
            fontfamily=self.style.mpl_font_family,
            y=1.01,
        )

        # Apply margins
        m = self.style.margin
        w, h = self.style.width, self.style.height
        self.fig.subplots_adjust(
            left=m["l"] / w,
            right=1 - m["r"] / w,
            top=1 - m["t"] / h,
            bottom=m["b"] / h,
        )

        # Legend handles per condition: label -> Line2D proxy
        self._legend_handles: Dict[str, Line2D] = {}
        # Per-condition artists for removal: label -> list of artists
        self._condition_artists: Dict[str, list] = {}

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
        ax = self._axes[row - 1][col - 1]
        mpl_color = to_mpl_color(color)
        r, g, b, _ = mpl_color
        # Convert to hex so matplotlib never sees numpy scalar tuples
        hex_color = "#{:02x}{:02x}{:02x}".format(
            int(r * 255), int(g * 255), int(b * 255)
        )

        n, bins, patches = ax.hist(
            values,
            bins=30,
            density=True,
            color=hex_color,
            edgecolor=hex_color,
            linewidth=line_width,
            alpha=0.3,
        )

        self._condition_artists.setdefault(label, []).extend(patches)

        if showlegend:
            self._update_legend_handle(
                label, mpl_color, line_width, self.style.mpl_linestyle
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
        ax = self._axes[row - 1][col - 1]
        mpl_color = to_mpl_color(color)

        # Resolve line style from condition style string if set
        from ..utils.plotly_utils import PlotStyle as _PS

        mpl_ls = _PS(line_style=line_style).mpl_linestyle

        r, g, b, _ = mpl_color
        hex_color = "#{:02x}{:02x}{:02x}".format(
            int(r * 255), int(g * 255), int(b * 255)
        )

        (line,) = ax.plot(
            x_range, density, color=hex_color, linewidth=line_width, linestyle=mpl_ls
        )

        if self.distribution_kind == "kde":
            fill = ax.fill_between(
                x_range,
                density,
                color=hex_color,
                alpha=0.2,
            )
            self._condition_artists.setdefault(label, []).append(fill)

        self._condition_artists.setdefault(label, []).append(line)

        if showlegend:
            self._update_legend_handle(label, mpl_color, line_width, mpl_ls)

    def _render_kde_fallback(
        self, values, label, color, opacity, row, col, showlegend, legendgroup
    ):
        ax = self._axes[row - 1][col - 1]
        mpl_color = to_mpl_color(color)
        r, g, b, _ = mpl_color
        hex_color = "#{:02x}{:02x}{:02x}".format(
            int(r * 255), int(g * 255), int(b * 255)
        )
        y_jitter = np.random.normal(0, 0.02, values.size)
        sc = ax.scatter(
            values, y_jitter, color=hex_color, s=30, alpha=opacity * 0.6, zorder=3
        )
        self._condition_artists.setdefault(label, []).append(sc)
        if showlegend:
            self._update_legend_handle(label, hex_color, self.style.line_width, "-")

    def _update_legend_handle(
        self, label: str, color, line_width: float, linestyle: str
    ):
        """Add or refresh legend proxy for a condition."""
        proxy = Line2D(
            [0],
            [0],
            color=color,
            linewidth=line_width,
            linestyle=linestyle,
            alpha=1.0,
            label=label,
        )
        self._legend_handles[label] = proxy
        self._refresh_legend()

    def _refresh_legend(self):
        """Rebuild legend on the top-left axes."""
        if not self.style.show_legend or not self._legend_handles:
            return
        ax = self._axes[0][0]
        ax.legend(
            handles=list(self._legend_handles.values()),
            loc=self.style.mpl_legend_loc,
            fontsize=self.style.legend_font_size,
            framealpha=0.8,
            edgecolor=to_mpl_color(self.style.legend_bordercolor),
            facecolor=to_mpl_color(self.style.legend_bgcolor),
        )

    # =========================================================================
    # Condition removal
    # =========================================================================

    def _do_remove_condition_traces(self, label: str):
        for artist in self._condition_artists.pop(label, []):
            try:
                artist.remove()
            except Exception:
                pass
        self._legend_handles.pop(label, None)
        self._refresh_legend()

    # =========================================================================
    # Title, display, save
    # =========================================================================

    def _do_set_title(self, title: str):
        self.fig.suptitle(
            title,
            fontsize=self.style.title_font_size,
            color=to_mpl_color(self.style.title_color),
            fontfamily=self.style.mpl_font_family,
        )

    def get_fig(self):
        return self.fig

    def show(self):
        plt.show()
        return self.fig

    def save(self, path, format=None, dpi=None, **kwargs):
        path = Path(path)
        fmt = format or path.suffix.lstrip(".").lower() or "png"
        self.fig.savefig(
            str(path),
            format=fmt,
            dpi=dpi or self.style.dpi,
            facecolor=to_mpl_color(self.style.paper_bgcolor),
            bbox_inches="tight",
            **kwargs,
        )
        self.logger.info(f"Saved stats figure to {path}")
