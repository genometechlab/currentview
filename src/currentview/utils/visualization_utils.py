from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, Union, Literal

class ColorScheme(Enum):
    """Predefined color schemes for Plotly visualization."""
    TAB10 = "tab10"  # Matplotlib's tab10 color scheme
    PLOTLY_DARK = "plotly_dark"
    PASTEL = "Pastel"
    DARK = "Dark2"
    COLORBLIND = "Safe"  # Colorblind-friendly palette

@dataclass
class PlotStyle:
    """Configuration for Plotly plot styling."""
    # Figure dimensions
    width: int = 1200  # pixels
    height: int = 800  # pixels
    
    # Backend
    renderer: Literal['SVG', 'WebGL'] = 'WebGL'
    
    # Trace styling
    line_width: float = 2.0
    line_style: str = "solid"  # "solid", "dash", "dot", "dashdot"
    opacity_mode: Literal['auto', 'fixed'] = 'auto'
    fixed_opacity: float = 0.8
    fill_opacity: float = 0.3
    
    # Layout and spacing
    margin: Dict[str, int] = field(default_factory=lambda: {
        'l': 80, 'r': 80, 't': 100, 'b': 80
    })
    
    # Grids, kmer barriers, and axes
    show_grid: bool = True
    grid_color: str = "rgba(128, 128, 128, 0.2)"
    zeroline: bool = False
    padding: float = 0.025
    barrier_style: str = 'solid'
    barrier_opacity: str = .25
    barrier_color: str = 'grey'
    
    
    # Background colors
    plot_bgcolor: str = "white"
    paper_bgcolor: str = "white"
    
    # Colors and themes
    template: str = "plotly_white"  # Plotly template
    color_scheme: Union[ColorScheme, str] = ColorScheme.TAB10 
    colorway: Optional[List[str]] = None  # Custom color sequence
    
    # Fonts
    font_family: str = "Arial, sans-serif"
    title_font_size: int = 20
    axis_title_font_size: int = 16
    tick_font_size: int = 12
    legend_font_size: int = 12
    annotation_font_size: int = 11
    
    # Legend
    show_legend: bool = True
    legend_orientation: Literal['v', 'h'] = 'v'
    legend_x: float = 1.02
    legend_y: float = 1
    legend_xanchor: str = "left"
    legend_yanchor: str = "top"
    legend_bgcolor: str = "rgba(255, 255, 255, 0.8)"
    legend_bordercolor: str = "rgba(0, 0, 0, 0.2)"
    legend_borderwidth: int = 1
    
    # Hover
    hovermode: Literal['x', 'y', 'closest', 'x unified', 'y unified'] = 'closest'
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
    dragmode: Literal['zoom', 'pan', 'select', 'lasso', 'orbit', 'turntable'] = 'zoom'
    selectdirection: Literal['d', 'h', 'v', 'any'] = 'd'  # d=diagonal, h=horizontal, v=vertical
    
    # Export config
    toImageButtonOptions: Dict[str, any] = field(default_factory=lambda: {
        'format': 'png',
        'width': 1200,
        'height': 800,
        'scale': 2  # For higher resolution
    })

    def __post_init__(self):
        if isinstance(self.color_scheme, str):
            try:
                self.color_scheme = ColorScheme[self.color_scheme.upper()]
            except KeyError:
                raise ValueError(
                    f"Invalid color_scheme '{self.color_scheme}'. "
                    f"Must be one of: {[e.name.lower() for e in ColorScheme]}"
                )
    
    def get_layout_dict(self) -> Dict:
        """Convert style settings to Plotly layout dictionary."""
        layout = {
            'template': self.template,
            'width': self.width,
            'height': self.height,
            'margin': self.margin,
            'plot_bgcolor': self.plot_bgcolor,
            'paper_bgcolor': self.paper_bgcolor,
            'font': {
                'family': self.font_family,
                'size': self.tick_font_size
            },
            'title': {
                'font': {
                    'size': self.title_font_size,
                    'family': self.font_family
                }
            },
            'showlegend': self.show_legend,
            'hovermode': self.hovermode,
            'hoverlabel': {
                'bgcolor': self.hoverlabel_bgcolor,
                'bordercolor': self.hoverlabel_bordercolor,
                'font': {'size': self.hoverlabel_font_size}
            },
            'dragmode': self.dragmode,
            'selectdirection': self.selectdirection
        }
        
        if self.show_legend:
            layout['legend'] = {
                'orientation': self.legend_orientation,
                'x': self.legend_x,
                'y': self.legend_y,
                'xanchor': self.legend_xanchor,
                'yanchor': self.legend_yanchor,
                'bgcolor': self.legend_bgcolor,
                'bordercolor': self.legend_bordercolor,
                'borderwidth': self.legend_borderwidth,
                'font': {'size': self.legend_font_size}
            }
        
        # Axes defaults
        axis_defaults = {
            'showgrid': self.show_grid,
            'gridcolor': self.grid_color,
            'zeroline': self.zeroline,
            'showline': self.showline,
            'linecolor': self.linecolor,
            'linewidth': self.linewidth,
            'mirror': self.mirror,
            'ticks': self.ticks,
            'ticklen': self.ticklen,
            'tickwidth': self.tickwidth,
            'tickcolor': self.tickcolor,
            'tickfont': {'size': self.tick_font_size},  # Changed from 'tickfont'
            'title': {  # Changed from 'titlefont' - now it's a dict with font inside
                'font': {
                    'size': self.axis_title_font_size,
                    'family': self.font_family
                }
            }
        }
        
        layout['xaxis'] = axis_defaults.copy()
        layout['yaxis'] = axis_defaults.copy()
        
        return layout
    
    def get_color_sequence(self) -> List[str]:
        """Get color sequence based on color scheme."""
        if self.colorway:
            return self.colorway
        
        # Plotly's built-in color sequences
        color_sequences = {
            ColorScheme.TAB10: ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                           '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'],
            ColorScheme.PLOTLY_DARK: ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A',
                                      '#19D3F3', '#FF6692', '#B6E880', '#FF97FF', '#FECB52'],
            ColorScheme.COLORBLIND: ['#0173B2', '#DE8F05', '#029E73', '#CC78BC', '#CA9161',
                                    '#FBAFE4', '#949494', '#ECE133', '#56B4E9', '#208F90'],
            ColorScheme.PASTEL: ['#FBB4AE', '#B3CDE3', '#CCEBC5', '#DECBE4', '#FED9A6',
                                '#FFFFCC', '#E5D8BD', '#FDDAEC', '#F2F2F2', '#B3E2CD'],
            ColorScheme.DARK: ['#1B9E77', '#D95F02', '#7570B3', '#E7298A', '#66A61E',
                              '#E6AB02', '#A6761D', '#666666', '#FF7F00', '#6A3D9A'],
        }
        
        return color_sequences.get(self.color_scheme, color_sequences[ColorScheme.TAB10])
     
    @staticmethod
    def paper_single_column() -> "PlotStyle":
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
            height=700,   # 2.33 inches * 300 DPI (3:2 ratio)
            
            # WebGL for performance
            renderer='WebGL',
            
            # Professional appearance
            template="plotly_white",
            color_scheme=ColorScheme.TAB10,
            
            # Crisp lines for print
            line_width=1.5,
            show_grid=False,
            
            # Minimal margins for space efficiency
            margin={'l': 60, 'r': 20, 't': 40, 'b': 50},
            
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
                'format': 'svg',  # Vector format preferred
                'width': 1050,
                'height': 700,
                'scale': 3
            }
        )
    
    @staticmethod
    def paper_two_column() -> "PlotStyle":
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
            
            # WebGL for performance with larger plots
            renderer='WebGL',
            
            # Professional appearance
            template="plotly_white",
            color_scheme=ColorScheme.TAB10,
            
            # Crisp lines for print
            line_width=1.5,
            show_grid=False,
            
            # Balanced margins for larger figure
            margin={'l': 80, 'r': 40, 't': 60, 'b': 60},
            
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
                'format': 'svg',  # Vector format preferred
                'width': 2100,
                'height': 1050,
                'scale': 3
            }
        )
    
    @staticmethod
    def poster() -> "PlotStyle":
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
            renderer='WebGL',
            
            # Bold appearance
            template="plotly_white",
            color_scheme=ColorScheme.PLOTLY_DARK,  # Vibrant colors
            
            # Thick lines for visibility
            line_width=4.0,
            show_grid=True,
            grid_color="rgba(200, 200, 200, 0.3)",
            
            # Generous margins for titles
            margin={'l': 120, 'r': 80, 't': 150, 'b': 120},
            
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
                'format': 'png',
                'width': 2400,
                'height': 1800,
                'scale': 2
            }
        )
    
    @staticmethod
    def presentation() -> "PlotStyle":
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
            
            # WebGL for smooth transitions
            renderer='WebGL',
            
            # High contrast
            template="plotly_white",
            color_scheme=ColorScheme.PLOTLY_DARK,
            
            # Visible lines
            line_width=3.0,
            show_grid=True,
            grid_color="rgba(230, 230, 230, 0.5)",
            
            # Balanced margins
            margin={'l': 100, 'r': 80, 't': 120, 'b': 100},
            
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
            dragmode='pan',
            hovermode='x unified',
            
            # Export settings
            toImageButtonOptions={
                'format': 'png',
                'width': 1920,
                'height': 1080,
                'scale': 1
            }
        )
    
    @staticmethod
    def interactive() -> "PlotStyle":
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
            
            # WebGL for performance
            renderer='WebGL',
            
            # Modern appearance
            template="plotly_white",
            color_scheme=ColorScheme.TAB10,
            
            # Standard lines
            line_width=2.0,
            opacity_mode='auto',
            
            # Detailed grid for exploration
            show_grid=True,
            grid_color="rgba(128, 128, 128, 0.2)",
            zeroline=True,
            
            # Comfortable margins
            margin={'l': 80, 'r': 80, 't': 100, 'b': 80},
            
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
            hovermode='closest',
            hoverlabel_font_size=14,
            
            # Full interactivity
            dragmode='zoom',
            selectdirection='any',
            
            # Standard export
            toImageButtonOptions={
                'format': 'png',
                'width': 1200,
                'height': 800,
                'scale': 2
            }
        )
    
    @staticmethod
    def dark_presentation() -> "PlotStyle":
        """
        Dark theme variant for presentations in dimmed rooms.
        """
        style = PlotStyle.presentation()
        
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