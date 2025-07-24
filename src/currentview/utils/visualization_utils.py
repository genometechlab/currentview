from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, Union, Literal

class ColorScheme(Enum):
    """Predefined color schemes for visualization."""
    DEFAULT = "tab10"
    VIRIDIS = "viridis"
    PLASMA = "plasma"
    INFERNO = "inferno"
    SEABORN = "Set2"
    CATEGORICAL = "Set3"
    PASTEL = "Pastel1"
    DARK = "Dark2"
    COLORBLIND = "tab10"  # Colorblind-friendly palette


@dataclass
class PlotStyle:
    """Configuration for plot styling."""
    figsize: Tuple[float, float] = (12, 8)
    dpi: int = 100
    line_width: float = 1.0
    line_style: str = '-'
    alpha_mode: Literal['auto', 'fixed'] = 'auto'
    fixed_alpha: float = 0.8
    padding: float = 0.025
    
    # Grid and axes
    show_grid: bool = False
    grid_alpha: float = 0.3
    show_spines: List[str] = field(default_factory=lambda: ['left', 'bottom'])
    
    # Colors
    color_scheme: ColorScheme = ColorScheme.DEFAULT
    position_barrier_color: str = 'gray'
    position_barrier_style: str = '--'
    position_barrier_alpha: float = 0.3
    
    # Labels and title
    title_fontsize: int = 14
    label_fontsize: int = 12
    tick_labelsize: int = 10
    
    # Legend
    show_legend: bool = True
    legend_location: str = 'best'
    legend_fontsize: int = 10

    # X-axis tick labels positioning (for stacked labels)
    xtick_label_y_start: float = -0.02      # Starting y-position for first row of x-tick labels
    xtick_label_row_spacing: float = -0.04  # Spacing between rows of stacked x-tick labels
    xlabel_margin_base: float = 15.0        # Base margin between x-tick labels and x-axis label
    xlabel_margin_per_row: float = 15.0     # Additional margin per row of stacked labels