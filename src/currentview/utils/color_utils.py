from matplotlib.colors import to_rgba
import re
from enum import Enum
from typing import List, Dict


def calculate_opacity(self, n_reads: int) -> float:
    """Calculate appropriate opacity value."""
    if n_reads <= 1:
        opacity = 1.0
    elif n_reads <= 3:
        opacity = 0.9
    elif n_reads <= 10:
        opacity = 0.6
    elif n_reads <= 50:
        opacity = 0.4
    elif n_reads <= 100:
        opacity = 0.3
    else:
        opacity = 0.2
    return opacity


def to_rgba_str(color, alpha=0.2):
    # Handle 'rgb(r,g,b)' or 'rgba(r,g,b,a)' format
    if isinstance(color, str) and color.startswith(("rgb(", "rgba(")):
        # Extract numbers from rgb/rgba string
        numbers = re.findall(r"[\d.]+", color)  # Changed to handle decimals
        if len(numbers) >= 3:
            r, g, b = (
                int(float(numbers[0])),
                int(float(numbers[1])),
                int(float(numbers[2])),
            )
            # If rgba, multiply alphas
            if color.startswith("rgba(") and len(numbers) >= 4:
                existing_alpha = float(numbers[3])
                alpha = existing_alpha * alpha
            return f"rgba({r}, {g}, {b}, {alpha})"

    # For other formats, use matplotlib
    r, g, b, *rest = to_rgba(color)
    # Check if matplotlib returned an alpha
    if rest:
        existing_alpha = rest[0]
        alpha = existing_alpha * alpha
    return f"rgba({int(r*255)}, {int(g*255)}, {int(b*255)}, {alpha})"


def get_contrasting_color(bgcolor):
    """Determine whether black or white text provides better contrast."""
    # Handle 'rgb(r,g,b)' or 'rgba(r,g,b,a)' format
    if isinstance(bgcolor, str) and bgcolor.startswith(("rgb(", "rgba(")):
        # Extract numbers from rgb/rgba string
        numbers = re.findall(r"[\d.]+", bgcolor)
        if len(numbers) >= 3:
            r, g, b = (
                int(float(numbers[0])),
                int(float(numbers[1])),
                int(float(numbers[2])),
            )
        else:
            # Fallback if parsing fails
            r, g, b = 128, 128, 128
    else:
        # For other formats, use matplotlib
        rgba = to_rgba(bgcolor)
        r, g, b = int(rgba[0] * 255), int(rgba[1] * 255), int(rgba[2] * 255)

    # Calculate luminance using W3C formula
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255

    # Return black for light backgrounds, white for dark backgrounds
    return "black" if luminance > 0.5 else "white"


class ColorScheme(Enum):
    TAB10 = "tab10"
    PLOTLY_DARK = "plotly_dark"
    PASTEL = "Pastel"
    DARK = "Dark2"
    COLORBLIND = "Safe"


_COLOR_MAP: Dict[ColorScheme, List[str]] = {
    ColorScheme.TAB10: [
        "#1f77b4",
        "#ff7f0e",
        "#2ca02c",
        "#d62728",
        "#9467bd",
        "#8c564b",
        "#e377c2",
        "#7f7f7f",
        "#bcbd22",
        "#17becf",
    ],
    ColorScheme.PLOTLY_DARK: [
        "#636EFA",
        "#EF553B",
        "#00CC96",
        "#AB63FA",
        "#FFA15A",
        "#19D3F3",
        "#FF6692",
        "#B6E880",
        "#FF97FF",
        "#FECB52",
    ],
    ColorScheme.COLORBLIND: [
        "#0173B2",
        "#DE8F05",
        "#029E73",
        "#CC78BC",
        "#CA9161",
        "#FBAFE4",
        "#949494",
        "#ECE133",
        "#56B4E9",
        "#208F90",
    ],
    ColorScheme.PASTEL: [
        "#FBB4AE",
        "#B3CDE3",
        "#CCEBC5",
        "#DECBE4",
        "#FED9A6",
        "#FFFFCC",
        "#E5D8BD",
        "#FDDAEC",
        "#F2F2F2",
        "#B3E2CD",
    ],
    ColorScheme.DARK: [
        "#1B9E77",
        "#D95F02",
        "#7570B3",
        "#E7298A",
        "#66A61E",
        "#E6AB02",
        "#A6761D",
        "#666666",
        "#FF7F00",
        "#6A3D9A",
    ],
}


class ColorPalette:
    """Independent palette object; knows nothing about PlotStyle."""

    def __init__(self, scheme: ColorScheme):
        self.scheme = scheme

    def colors(self) -> List[str]:
        return _COLOR_MAP[self.scheme]

    @staticmethod
    def from_name(name: str) -> "ColorPalette":
        try:
            return ColorPalette(ColorScheme[name.upper()])
        except KeyError as e:
            valid = ", ".join(cs.name.lower() for cs in ColorScheme)
            raise ValueError(f"Unknown color scheme '{name}'. Valid: {valid}") from e

    @staticmethod
    def default_palette() -> "ColorPalette":
        return ColorPalette(ColorScheme.TAB10)
