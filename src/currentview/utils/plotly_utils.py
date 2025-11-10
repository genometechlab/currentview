from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, Union, Literal
from matplotlib.colors import to_rgba
import re


@dataclass
class PlotStyle:
    """Configuration for Plotly plot styling."""

    # Figure dimensions
    width: int = 1200  # pixels
    height: int = 800  # pixels

    # Backend
    renderer: Literal["SVG", "WebGL"] = "SVG"

    # Trace styling
    line_width: float = 2.0
    line_style: str = "solid"  # "solid", "dash", "dot", "dashdot"
    opacity_mode: Literal["auto", "fixed"] = "auto"
    fixed_opacity: float = 0.8
    fill_opacity: float = 0.3

    # Layout and spacing
    margin: Dict[str, int] = field(
        default_factory=lambda: {"l": 80, "r": 80, "t": 100, "b": 80}
    )

    # Grids, kmer barriers, and axes
    show_grid: bool = False
    grid_color: str = "rgba(128, 128, 128, 0.2)"
    zeroline: bool = False
    positions_padding: float = 0.025
    barrier_style: str = "solid"
    barrier_opacity: str = 0.25
    barrier_color: str = "grey"

    # Background colors
    plot_bgcolor: str = "white"
    paper_bgcolor: str = "white"

    # Colors and themes
    template: str = "plotly_white"  # Plotly template
    colorway: Optional[List[str]] = None  # Custom color sequence

    # Fonts
    font_family: str = "Arial, sans-serif"
    title_font_size: int = 20
    titlecolor: str = "black"
    axis_title_font_size: int = 16
    axis_title_color: str = "black"
    tick_font_size: int = 12
    legend_font_size: int = 12
    annotation_font_size: int = 11

    # Legend
    show_legend: bool = True
    legend_orientation: Literal["v", "h"] = "v"
    legend_x: float = 1.02
    legend_y: float = 1
    legend_xanchor: str = "left"
    legend_yanchor: str = "top"
    legend_bgcolor: str = "rgba(255, 255, 255, 0.8)"
    legend_bordercolor: str = "rgba(0, 0, 0, 0.2)"
    legend_borderwidth: int = 1

    # Hover
    hovermode: Literal["x", "y", "closest", "x unified", "y unified"] = "closest"
    hoverlabel_bgcolor: str = "white"
    hoverlabel_bordercolor: str = "black"
    hoverlabel_font_size: int = 12

    # Subplots
    subplot_vertical_spacing: Optional[float] = None  # Auto-calculated if None
    subplot_horizontal_spacing: Optional[float] = None  # Auto-calculated if None
    subplot_title_font_size: int = 14

    # Axes
    showline: bool = True
    linecolor: str = "black"
    linewidth: int = 1
    mirror: bool = False  # Mirror axis lines

    # Ticks
    ticks: str = "outside"  # "outside", "inside", ""
    ticklen: int = 5
    tickwidth: int = 1
    tickcolor: str = "black"

    # Interactive features
    dragmode: Literal["zoom", "pan", "select", "lasso", "orbit", "turntable"] = "zoom"
    selectdirection: Literal["d", "h", "v", "any"] = (
        "d"  # d=diagonal, h=horizontal, v=vertical
    )

    # Export config
    toImageButtonOptions: Dict[str, any] = field(
        default_factory=lambda: {
            "format": "png",
            "width": 1200,
            "height": 800,
            "scale": 2,  # For higher resolution
        }
    )

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
                    "color": self.titlecolor,
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

        # Axes defaults
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
            "tickfont": {
                "size": self.tick_font_size,
                "color": self.tickcolor,
            },  # Changed from 'tickfont'
            "title": {  # Changed from 'titlefont' - now it's a dict with font inside
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

    @staticmethod
    def _paper_single_column() -> "PlotStyle":
        """
        Style optimized for single-column figures in academic papers.
        - Column width: 3.5 inches (standard single column)
        - High DPI for print
        - Minimal colors (works in B&W)
        - Clean, professional appearance
        """
        return PlotStyle(
            # Journal single column width at 300 DPI
            width=1050,  # 3.5 inches * 300 DPI
            height=700,  # 2.33 inches * 300 DPI (3:2 ratio)
            # SVG for performance
            renderer="SVG",
            # Professional appearance
            template="plotly_white",
            # Crisp lines for print
            line_width=1.5,
            show_grid=False,
            # Minimal margins for space efficiency
            margin={"l": 60, "r": 20, "t": 40, "b": 50},
            # Font settings for readability at small size
            font_family="Arial, sans-serif",
            title_font_size=14,
            axis_title_font_size=12,
            tick_font_size=10,
            legend_font_size=10,
            annotation_font_size=9,
            # Compact legend
            legend_x=0.02,
            legend_y=0.98,
            legend_xanchor="left",
            legend_yanchor="top",
            legend_bgcolor="rgba(255, 255, 255, 0.9)",
            # Clean axes
            showline=True,
            linecolor="black",
            linewidth=1,
            ticks="outside",
            ticklen=4,
            # High resolution export
            toImageButtonOptions={
                "format": "svg",  # Vector format preferred
                "width": 1050,
                "height": 700,
                "scale": 3,
            },
        )

    @staticmethod
    def _paper_two_column() -> "PlotStyle":
        """
        Style optimized for two-column (full width) figures in academic papers.
        - Full page width: 7.0 inches (standard two-column span)
        - High DPI for print
        - More space for complex visualizations
        - Clean, professional appearance
        """
        return PlotStyle(
            # Journal two-column width at 300 DPI
            width=2100,  # 7.0 inches * 300 DPI
            height=1050,  # 3.5 inches * 300 DPI (2:1 ratio)
            # SVG for performance with larger plots
            renderer="SVG",
            # Professional appearance
            template="plotly_white",
            # Crisp lines for print
            line_width=1.5,
            show_grid=False,
            # Balanced margins for larger figure
            margin={"l": 80, "r": 40, "t": 60, "b": 60},
            # Slightly larger fonts for two-column width
            font_family="Arial, sans-serif",
            title_font_size=16,
            axis_title_font_size=14,
            tick_font_size=11,
            legend_font_size=11,
            annotation_font_size=10,
            # Legend positioning for wider format
            legend_x=0.02,
            legend_y=0.98,
            legend_xanchor="left",
            legend_yanchor="top",
            legend_bgcolor="rgba(255, 255, 255, 0.9)",
            # Clean axes
            showline=True,
            linecolor="black",
            linewidth=1,
            ticks="outside",
            ticklen=4,
            # High resolution export
            toImageButtonOptions={
                "format": "svg",  # Vector format preferred
                "width": 2100,
                "height": 1050,
                "scale": 3,
            },
        )

    @staticmethod
    def _poster() -> "PlotStyle":
        """
        Style optimized for academic posters.
        - Large dimensions for poster printing
        - Bold, eye-catching colors
        - Extra large fonts for readability at distance
        - High visual impact
        """
        return PlotStyle(
            # Large size for poster sections
            width=2400,  # 8 inches at 300 DPI
            height=1800,  # 6 inches at 300 DPI
            # Fast rendering for large plots
            renderer="SVG",
            # Bold appearance
            template="plotly_white",
            # Thick lines for visibility
            line_width=4.0,
            show_grid=False,
            grid_color="rgba(200, 200, 200, 0.3)",
            # Generous margins for titles
            margin={"l": 120, "r": 80, "t": 150, "b": 120},
            # Extra large fonts for poster viewing distance
            font_family="Arial Black, sans-serif",
            title_font_size=48,
            axis_title_font_size=36,
            tick_font_size=24,
            legend_font_size=28,
            annotation_font_size=24,
            # Prominent legend
            legend_x=0.02,
            legend_y=0.98,
            legend_borderwidth=2,
            # Bold axes
            showline=True,
            linecolor="black",
            linewidth=3,
            ticks="outside",
            ticklen=10,
            tickwidth=2,
            # High resolution export
            toImageButtonOptions={
                "format": "png",
                "width": 2400,
                "height": 1800,
                "scale": 2,
            },
        )

    @staticmethod
    def _presentation() -> "PlotStyle":
        """
        Style optimized for presentations and slides.
        - 16:9 aspect ratio for modern projectors
        - High contrast colors
        - Large fonts for back-of-room visibility
        - Clean design that projects well
        """
        return PlotStyle(
            # 16:9 aspect ratio for slides
            width=1920,
            height=1080,
            # SVG for smooth transitions
            renderer="SVG",
            # High contrast
            template="plotly_white",
            # Visible lines
            line_width=3.0,
            show_grid=False,
            grid_color="rgba(230, 230, 230, 0.5)",
            # Balanced margins
            margin={"l": 100, "r": 80, "t": 120, "b": 100},
            # Large fonts for projection
            font_family="Helvetica, Arial, sans-serif",
            title_font_size=36,
            axis_title_font_size=28,
            tick_font_size=20,
            legend_font_size=22,
            annotation_font_size=18,
            # Clear legend
            legend_x=0.02,
            legend_y=0.98,
            legend_bgcolor="rgba(255, 255, 255, 0.95)",
            legend_borderwidth=2,
            # Prominent axes
            showline=True,
            linecolor="black",
            linewidth=2,
            mirror=True,  # Frame the plot
            # Simplified interaction for presentations
            dragmode="pan",
            hovermode="x unified",
            # Export settings
            toImageButtonOptions={
                "format": "png",
                "width": 1920,
                "height": 1080,
                "scale": 1,
            },
        )

    @staticmethod
    def _interactive() -> "PlotStyle":
        """
        Style optimized for interactive exploration.
        - Rich hover information
        - Full interactivity enabled
        - Detailed grid for value reading
        - Optimized for screen viewing
        """
        return PlotStyle(
            # Standard screen size
            width=1200,
            height=800,
            # SVG for performance
            renderer="SVG",
            # Modern appearance
            template="plotly_white",
            # Standard lines
            line_width=2.0,
            opacity_mode="auto",
            # Detailed grid for exploration
            show_grid=False,
            grid_color="rgba(128, 128, 128, 0.2)",
            zeroline=False,
            # Comfortable margins
            margin={"l": 80, "r": 80, "t": 100, "b": 80},
            # Readable fonts
            font_family="Arial, sans-serif",
            title_font_size=20,
            axis_title_font_size=16,
            tick_font_size=12,
            legend_font_size=12,
            annotation_font_size=11,
            # Interactive legend
            legend_x=1.02,
            legend_y=1,
            legend_xanchor="left",
            legend_yanchor="top",
            # Detailed hover
            hovermode="closest",
            hoverlabel_font_size=14,
            # Full interactivity
            dragmode="zoom",
            selectdirection="any",
            # Standard export
            toImageButtonOptions={
                "format": "png",
                "width": 1200,
                "height": 800,
                "scale": 2,
            },
        )

    @staticmethod
    def _dark_interactive() -> "PlotStyle":
        """
        Dark theme variant for dark tehemed interactive enviromentes
        """
        style = PlotStyle._interactive()

        # Dark theme modifications
        style.template = "plotly_dark"
        style.plot_bgcolor = "#111111"
        style.paper_bgcolor = "#0a0a0a"
        style.grid_color = "rgba(255, 255, 255, 0.1)"
        style.linecolor = "white"
        style.tickcolor = "white"
        style.legend_bgcolor = "rgba(0, 0, 0, 0.8)"
        style.legend_bordercolor = "rgba(255, 255, 255, 0.3)"
        style.hoverlabel_bgcolor = "#222222"
        style.hoverlabel_bordercolor = "white"

        return style

    @staticmethod
    def _dark_presentation() -> "PlotStyle":
        """
        Dark theme variant for presentations in dimmed rooms.
        """
        style = PlotStyle._presentation()

        # Dark theme modifications
        style.template = "plotly_dark"
        style.plot_bgcolor = "#111111"
        style.paper_bgcolor = "#0a0a0a"
        style.grid_color = "rgba(255, 255, 255, 0.1)"
        style.linecolor = "white"
        style.tickcolor = "white"
        style.legend_bgcolor = "rgba(0, 0, 0, 0.8)"
        style.legend_bordercolor = "rgba(255, 255, 255, 0.3)"
        style.hoverlabel_bgcolor = "#222222"
        style.hoverlabel_bordercolor = "white"

        return style

    @staticmethod
    def get_style(style_name: str) -> "PlotStyle":
        """
        Get a predefined style by name.

        Args:
            style_name: Name of the style. Available options:
                - 'paper_single': Single-column paper figure
                - 'paper_double': Two-column (full width) paper figure
                - 'poster': Conference poster
                - 'presentation': Slide presentation
                - 'presentation_dark': Dark theme presentation
                - 'interactive': Interactive exploration

        Returns:
            PlotStyle instance with predefined settings

        Raises:
            ValueError: If style_name is not recognized

        Example:
            >>> style = PlotStyles.get_style('paper_single')
            >>> style.width = 1200  # Can still modify after creation
        """
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
            raise ValueError(
                f"Unknown style '{style_name}'. " f"Available styles: {available}"
            )

        return styles[style_name]()
