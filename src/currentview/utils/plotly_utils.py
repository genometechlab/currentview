from dataclasses import dataclass, field
from typing import Dict, List, Optional, Literal


@dataclass
class PlotStyle:
    """
    Unified style configuration for both Plotly and Matplotlib backends.
    Fields are grouped by which backend uses them.
    Fields marked [BOTH] are used by both backends.
    Fields marked [PLOTLY] are Plotly-only.
    Fields marked [MPL] are Matplotlib-only.
    """

    # -------------------------------------------------------------------------
    # [BOTH] Figure dimensions
    # -------------------------------------------------------------------------
    width: int = 1200  # pixels — used directly by Plotly
    height: int = 800  # pixels — used directly by Plotly

    # [MPL] Physical size in inches — independent of DPI.
    # At dpi=150: 8x5.33" -> 1200x800px output
    # At dpi=600: 8x5.33" -> 4800x3200px output (hi-res, same physical size)
    mpl_fig_width_in: float = 8.0
    mpl_fig_height_in: float = 5.33
    dpi: int = 150  # [MPL] dots per inch — ignored by Plotly

    # -------------------------------------------------------------------------
    # [BOTH] Trace / line styling
    # -------------------------------------------------------------------------
    line_width: float = 2.0
    line_style: str = "solid"  # "solid", "dash", "dot", "dashdot"
    # Plotly uses these names natively;
    # Mpl maps them (see _mpl_linestyle)
    opacity_mode: Literal["auto", "fixed"] = "auto"
    fixed_opacity: float = 0.8
    fill_opacity: float = 0.3

    # -------------------------------------------------------------------------
    # [BOTH] Position barriers
    # -------------------------------------------------------------------------
    positions_padding: float = 0.025
    barrier_style: str = "solid"
    barrier_opacity: float = 0.25
    barrier_color: str = "grey"

    # -------------------------------------------------------------------------
    # [BOTH] Background
    # -------------------------------------------------------------------------
    plot_bgcolor: str = "white"
    paper_bgcolor: str = "white"  # [PLOTLY] figure bg; [MPL] fig.patch color

    # -------------------------------------------------------------------------
    # [BOTH] Fonts
    # -------------------------------------------------------------------------
    font_family: str = "Arial, sans-serif"
    title_font_size: int = 20
    title_color: str = "black"
    axis_title_font_size: int = 16
    axis_title_color: str = "black"
    tick_font_size: int = 12
    tick_color: str = "black"
    legend_font_size: int = 12
    annotation_font_size: int = 11

    # -------------------------------------------------------------------------
    # [BOTH] Grid and axes
    # -------------------------------------------------------------------------
    show_grid: bool = False
    grid_color: str = "rgba(128, 128, 128, 0.2)"
    zeroline: bool = False
    showline: bool = True
    linecolor: str = "black"
    linewidth: int = 1
    mirror: bool = False  # [PLOTLY] axis mirroring; [MPL] top/right spine

    # -------------------------------------------------------------------------
    # [BOTH] Ticks
    # -------------------------------------------------------------------------
    ticks: str = "outside"  # "outside", "inside", "" -> Mpl: tick direction
    ticklen: int = 5
    tickwidth: int = 1

    # -------------------------------------------------------------------------
    # [BOTH] Legend
    # -------------------------------------------------------------------------
    show_legend: bool = True
    legend_orientation: Literal["v", "h"] = "v"
    legend_x: float = 1.02
    legend_y: float = 1.0
    legend_xanchor: str = "left"  # Plotly anchor names; Mpl maps to loc string
    legend_yanchor: str = "top"
    legend_bgcolor: str = "rgba(255, 255, 255, 0.8)"
    legend_bordercolor: str = "rgba(0, 0, 0, 0.2)"
    legend_borderwidth: int = 1

    # -------------------------------------------------------------------------
    # [BOTH] Margins  (l/r/t/b in pixels for Plotly; converted to inches for Mpl)
    # -------------------------------------------------------------------------
    margin: Dict[str, int] = field(
        default_factory=lambda: {"l": 80, "r": 80, "t": 100, "b": 80}
    )

    # -------------------------------------------------------------------------
    # [PLOTLY] Template and colorway
    # -------------------------------------------------------------------------
    renderer: Literal["SVG", "WebGL"] = "SVG"
    template: str = "plotly_white"
    colorway: Optional[List[str]] = None

    # -------------------------------------------------------------------------
    # [PLOTLY] Hover
    # -------------------------------------------------------------------------
    hovermode: Literal["x", "y", "closest", "x unified", "y unified"] = "closest"
    hoverlabel_bgcolor: str = "white"
    hoverlabel_bordercolor: str = "black"
    hoverlabel_font_size: int = 12

    # -------------------------------------------------------------------------
    # [PLOTLY] Interaction
    # -------------------------------------------------------------------------
    dragmode: Literal["zoom", "pan", "select", "lasso", "orbit", "turntable"] = "zoom"
    selectdirection: Literal["d", "h", "v", "any"] = "d"

    # -------------------------------------------------------------------------
    # [PLOTLY] Subplot spacing
    # -------------------------------------------------------------------------
    subplot_vertical_spacing: Optional[float] = None
    subplot_horizontal_spacing: Optional[float] = None
    subplot_title_font_size: int = 14

    # -------------------------------------------------------------------------
    # [PLOTLY] Export button
    # -------------------------------------------------------------------------
    toImageButtonOptions: Dict = field(
        default_factory=lambda: {
            "format": "png",
            "width": 1200,
            "height": 800,
            "scale": 2,
        }
    )

    # -------------------------------------------------------------------------
    # [MPL] Style preset — maps to a matplotlib style sheet
    # -------------------------------------------------------------------------
    mpl_style: Optional[str] = None  # e.g. "seaborn-v0_8-whitegrid", "ggplot"

    # =========================================================================
    # Helpers for Matplotlib backend
    # =========================================================================

    @property
    def figsize(self) -> tuple:
        """Physical figure size in inches for Matplotlib.
        This is independent of DPI — DPI only controls output resolution.
        Example: 8x5.33 inches at dpi=150 -> 1200x800px
                 8x5.33 inches at dpi=600 -> 4800x3200px (same figure, higher res)
        """
        return (self.mpl_fig_width_in, self.mpl_fig_height_in)

    @property
    def mpl_linestyle(self) -> str:
        """Map unified line_style string to a Matplotlib linestyle."""
        mapping = {
            "solid": "-",
            "dash": "--",
            "dot": ":",
            "dashdot": "-.",
            # Plotly aliases
            "longdash": "--",
            "longdashdot": "-.",
        }
        return mapping.get(self.line_style, "-")

    @property
    def mpl_barrier_linestyle(self) -> str:
        mapping = {
            "solid": "-",
            "dash": "--",
            "dot": ":",
            "dashdot": "-.",
        }
        return mapping.get(self.barrier_style, "-")

    @property
    def mpl_tick_direction(self) -> str:
        """Map Plotly tick position to Matplotlib tick direction."""
        mapping = {"outside": "out", "inside": "in", "": ""}
        return mapping.get(self.ticks, "out")

    @property
    def mpl_legend_loc(self) -> str:
        """
        Convert Plotly legend anchor strings to a Matplotlib loc string.
        This is a best-effort mapping; fine-tuned positioning uses
        legend_x / legend_y with bbox_to_anchor directly.
        """
        x_anchor = self.legend_xanchor  # "left", "center", "right"
        y_anchor = self.legend_yanchor  # "top", "middle", "bottom"
        mapping = {
            ("left", "top"): "upper left",
            ("left", "middle"): "center left",
            ("left", "bottom"): "lower left",
            ("center", "top"): "upper center",
            ("center", "middle"): "center",
            ("center", "bottom"): "lower center",
            ("right", "top"): "upper right",
            ("right", "middle"): "center right",
            ("right", "bottom"): "lower right",
        }
        return mapping.get((x_anchor, y_anchor), "upper right")

    @property
    def mpl_font_family(self) -> str:
        """Extract first font from comma-separated font stack."""
        return self.font_family.split(",")[0].strip()

    def apply_to_mpl_axes(self, ax, title_text: str = ""):
        """
        Apply all relevant style settings to a Matplotlib Axes object.
        All color strings are converted via to_mpl_color() before being
        passed to matplotlib so rgba()/rgb() Plotly strings work correctly.
        """
        from .color_utils import to_mpl_color

        # Background
        ax.set_facecolor(to_mpl_color(self.plot_bgcolor))
        ax.figure.patch.set_facecolor(to_mpl_color(self.paper_bgcolor))

        # Title
        if title_text:
            ax.set_title(
                title_text,
                fontsize=self.title_font_size,
                fontfamily=self.mpl_font_family,
                color=to_mpl_color(self.title_color),
                pad=10,
            )

        # Axis label fonts
        ax.xaxis.label.set_fontsize(self.axis_title_font_size)
        ax.xaxis.label.set_color(to_mpl_color(self.axis_title_color))
        ax.yaxis.label.set_fontsize(self.axis_title_font_size)
        ax.yaxis.label.set_color(to_mpl_color(self.axis_title_color))

        # Tick params
        ax.tick_params(
            axis="both",
            direction=self.mpl_tick_direction,
            length=self.ticklen,
            width=self.tickwidth,
            colors=to_mpl_color(self.tick_color),
            labelsize=self.tick_font_size,
        )

        # Grid
        if self.show_grid:
            ax.grid(True, color=to_mpl_color(self.grid_color))
        else:
            ax.grid(False)
        ax.set_axisbelow(True)

        # Zero line
        if self.zeroline:
            ax.axhline(0, color=to_mpl_color(self.linecolor), linewidth=0.8, zorder=0)

        # Spines
        for spine in ax.spines.values():
            spine.set_visible(self.showline)
            spine.set_color(to_mpl_color(self.linecolor))
            spine.set_linewidth(self.linewidth)

        # Mirror (top/right spines)
        ax.spines["top"].set_visible(self.mirror)
        ax.spines["right"].set_visible(self.mirror)

    # =========================================================================
    # Helpers for Plotly backend (unchanged from original)
    # =========================================================================

    def get_layout_dict(self) -> Dict:
        """Convert style settings to Plotly layout dictionary."""
        layout = {
            "template": self.template,
            "width": self.width,
            "height": self.height,
            "margin": self.margin,
            "plot_bgcolor": self.plot_bgcolor,
            "paper_bgcolor": self.paper_bgcolor,
            "font": {"family": self.font_family, "size": self.tick_font_size},
            "title": {
                "font": {
                    "size": self.title_font_size,
                    "family": self.font_family,
                    "color": self.title_color,
                }
            },
            "showlegend": self.show_legend,
            "hovermode": self.hovermode,
            "hoverlabel": {
                "bgcolor": self.hoverlabel_bgcolor,
                "bordercolor": self.hoverlabel_bordercolor,
                "font": {"size": self.hoverlabel_font_size},
            },
            "dragmode": self.dragmode,
            "selectdirection": self.selectdirection,
        }

        if self.show_legend:
            layout["legend"] = {
                "orientation": self.legend_orientation,
                "x": self.legend_x,
                "y": self.legend_y,
                "xanchor": self.legend_xanchor,
                "yanchor": self.legend_yanchor,
                "bgcolor": self.legend_bgcolor,
                "bordercolor": self.legend_bordercolor,
                "borderwidth": self.legend_borderwidth,
                "font": {"size": self.legend_font_size},
            }

        axis_defaults = {
            "showgrid": self.show_grid,
            "gridcolor": self.grid_color,
            "zeroline": self.zeroline,
            "showline": self.showline,
            "linecolor": self.linecolor,
            "linewidth": self.linewidth,
            "mirror": self.mirror,
            "ticks": self.ticks,
            "ticklen": self.ticklen,
            "tickwidth": self.tickwidth,
            "tickfont": {"size": self.tick_font_size, "color": self.tick_color},
            "title": {
                "font": {
                    "color": self.axis_title_color,
                    "size": self.axis_title_font_size,
                    "family": self.font_family,
                }
            },
        }

        layout["xaxis"] = axis_defaults.copy()
        layout["yaxis"] = axis_defaults.copy()

        return layout

    # =========================================================================
    # Predefined styles (unchanged, just renamed titlecolor -> title_color)
    # =========================================================================

    @staticmethod
    def _paper_single_column() -> "PlotStyle":
        return PlotStyle(
            width=1050,
            height=700,
            mpl_fig_width_in=3.5,
            mpl_fig_height_in=2.33,
            dpi=300,
            renderer="SVG",
            template="plotly_white",
            line_width=1.5,
            show_grid=False,
            margin={"l": 60, "r": 20, "t": 40, "b": 50},
            font_family="Arial, sans-serif",
            title_font_size=14,
            axis_title_font_size=12,
            tick_font_size=10,
            legend_font_size=10,
            annotation_font_size=9,
            legend_x=0.02,
            legend_y=0.98,
            legend_xanchor="left",
            legend_yanchor="top",
            legend_bgcolor="rgba(255, 255, 255, 0.9)",
            showline=True,
            linecolor="black",
            linewidth=1,
            ticks="outside",
            ticklen=4,
            toImageButtonOptions={
                "format": "svg",
                "width": 1050,
                "height": 700,
                "scale": 3,
            },
        )

    @staticmethod
    def _paper_two_column() -> "PlotStyle":
        return PlotStyle(
            width=2100,
            height=1050,
            mpl_fig_width_in=7.0,
            mpl_fig_height_in=3.5,
            dpi=300,
            renderer="SVG",
            template="plotly_white",
            line_width=1.5,
            show_grid=False,
            margin={"l": 80, "r": 40, "t": 60, "b": 60},
            font_family="Arial, sans-serif",
            title_font_size=16,
            axis_title_font_size=14,
            tick_font_size=11,
            legend_font_size=11,
            annotation_font_size=10,
            legend_x=0.02,
            legend_y=0.98,
            legend_xanchor="left",
            legend_yanchor="top",
            legend_bgcolor="rgba(255, 255, 255, 0.9)",
            showline=True,
            linecolor="black",
            linewidth=1,
            ticks="outside",
            ticklen=4,
            toImageButtonOptions={
                "format": "svg",
                "width": 2100,
                "height": 1050,
                "scale": 3,
            },
        )

    @staticmethod
    def _poster() -> "PlotStyle":
        return PlotStyle(
            width=2400,
            height=1800,
            dpi=150,
            renderer="SVG",
            template="plotly_white",
            line_width=4.0,
            show_grid=False,
            margin={"l": 120, "r": 80, "t": 150, "b": 120},
            font_family="Arial Black, sans-serif",
            title_font_size=48,
            axis_title_font_size=36,
            tick_font_size=24,
            legend_font_size=28,
            annotation_font_size=24,
            legend_x=0.02,
            legend_y=0.98,
            legend_borderwidth=2,
            showline=True,
            linecolor="black",
            linewidth=3,
            ticks="outside",
            ticklen=10,
            tickwidth=2,
            toImageButtonOptions={
                "format": "png",
                "width": 2400,
                "height": 1800,
                "scale": 2,
            },
        )

    @staticmethod
    def _presentation() -> "PlotStyle":
        return PlotStyle(
            width=1920,
            height=1080,
            dpi=150,
            renderer="SVG",
            template="plotly_white",
            line_width=3.0,
            show_grid=False,
            margin={"l": 100, "r": 80, "t": 120, "b": 100},
            font_family="Helvetica, Arial, sans-serif",
            title_font_size=36,
            axis_title_font_size=28,
            tick_font_size=20,
            legend_font_size=22,
            annotation_font_size=18,
            legend_x=0.02,
            legend_y=0.98,
            legend_bgcolor="rgba(255, 255, 255, 0.95)",
            legend_borderwidth=2,
            showline=True,
            linecolor="black",
            linewidth=2,
            mirror=True,
            dragmode="pan",
            hovermode="x unified",
            toImageButtonOptions={
                "format": "png",
                "width": 1920,
                "height": 1080,
                "scale": 1,
            },
        )

    @staticmethod
    def _interactive() -> "PlotStyle":
        return PlotStyle(
            width=1200,
            height=800,
            dpi=150,
            renderer="SVG",
            template="plotly_white",
            line_width=2.0,
            opacity_mode="auto",
            show_grid=False,
            zeroline=False,
            margin={"l": 80, "r": 80, "t": 100, "b": 80},
            font_family="Arial, sans-serif",
            title_font_size=20,
            axis_title_font_size=16,
            tick_font_size=12,
            legend_font_size=12,
            annotation_font_size=11,
            legend_x=1.02,
            legend_y=1,
            legend_xanchor="left",
            legend_yanchor="top",
            hovermode="closest",
            hoverlabel_font_size=14,
            dragmode="zoom",
            selectdirection="any",
            toImageButtonOptions={
                "format": "png",
                "width": 1200,
                "height": 800,
                "scale": 2,
            },
        )

    @staticmethod
    def _dark_interactive() -> "PlotStyle":
        style = PlotStyle._interactive()
        style.template = "plotly_dark"
        style.plot_bgcolor = "#111111"
        style.paper_bgcolor = "#0a0a0a"
        style.grid_color = "rgba(255, 255, 255, 0.1)"
        style.linecolor = "white"
        style.tick_color = "white"
        style.legend_bgcolor = "rgba(0, 0, 0, 0.8)"
        style.legend_bordercolor = "rgba(255, 255, 255, 0.3)"
        style.hoverlabel_bgcolor = "#222222"
        style.hoverlabel_bordercolor = "white"
        return style

    @staticmethod
    def _dark_presentation() -> "PlotStyle":
        style = PlotStyle._presentation()
        style.template = "plotly_dark"
        style.plot_bgcolor = "#111111"
        style.paper_bgcolor = "#0a0a0a"
        style.grid_color = "rgba(255, 255, 255, 0.1)"
        style.linecolor = "white"
        style.tick_color = "white"
        style.legend_bgcolor = "rgba(0, 0, 0, 0.8)"
        style.legend_bordercolor = "rgba(255, 255, 255, 0.3)"
        style.hoverlabel_bgcolor = "#222222"
        style.hoverlabel_bordercolor = "white"
        return style

    @staticmethod
    def get_style(style_name: str) -> "PlotStyle":
        styles = {
            "paper_single": PlotStyle._paper_single_column,
            "paper_double": PlotStyle._paper_two_column,
            "poster": PlotStyle._poster,
            "presentation": PlotStyle._presentation,
            "presentation_dark": PlotStyle._dark_presentation,
            "interactive": PlotStyle._interactive,
            "interactive_dark": PlotStyle._dark_interactive,
        }
        if style_name not in styles:
            available = ", ".join(sorted(styles.keys()))
            raise ValueError(f"Unknown style '{style_name}'. Available: {available}")
        return styles[style_name]()
