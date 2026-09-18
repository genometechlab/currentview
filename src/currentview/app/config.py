import os
from pathlib import Path

# Default directory the file pickers open in. Defaults to the directory the app
# was launched from, and can be pointed elsewhere with CURRENTVIEW_DATA_DIR.
DEFAULT_DATA_PATH = os.environ.get("CURRENTVIEW_DATA_DIR") or str(Path.cwd())
DEFAULT_BAM_PATH = DEFAULT_DATA_PATH
DEFAULT_POD5_PATH = DEFAULT_DATA_PATH

# UI Constants
WINDOW_SIZE_MIN = 3
WINDOW_SIZE_MAX = 99
WINDOW_SIZE_DEFAULT = 9
WINDOW_SIZE_STEP = 2

# Styling
LINE_STYLES = [
    {"label": "Solid (—)", "value": "solid"},
    {"label": "Dashed (--)", "value": "dash"},
    {"label": "Dotted (···)", "value": "dot"},
    {"label": "Dash-Dot (-·-)", "value": "dashdot"},
]

VERBOSITY_LEVELS = [
    {"label": "Silent (0)", "value": "0"},
    {"label": "Error (1)", "value": "1"},
    {"label": "Warning (2)", "value": "2"},
    {"label": "Info (3)", "value": "3"},
    {"label": "Debug (4)", "value": "4"},
]

STATISTICS_OPTIONS = [
    {"label": "Mean", "value": "mean"},
    {"label": "Median", "value": "median"},
    {"label": "Standard Deviation", "value": "std"},
    {"label": "Variance", "value": "variance"},
    {"label": "Minimum", "value": "min"},
    {"label": "Maximum", "value": "max"},
    {"label": "Skewness", "value": "skewness"},
    {"label": "Kurtosis", "value": "kurtosis"},
    {"label": "Duration/Dwell time", "value": "duration"},
]

STYLE_OPTIONS = [
    {"label": "Dark theme", "value": "dark"},
    {"label": "Show grid", "value": "grid"},
    {"label": "Show legend", "value": "legend"},
    {"label": "Use WebGL renderer", "value": "webgl"},
]

NORMALIZATION_METHODS = [
    {"label": "No normalization", "value": "none"},
    {"label": "Z-score normalization", "value": "zscore"},
    {"label": "Min-Max normalization", "value": "minmax"},
]

FILTERING_OPTIONS = [
    {"label": "No filtering", "value": "none"},
    {"label": "Bessel Filter", "value": "bessel"},
    {"label": "Gaussian Filter", "value": "gaussian"},
]

EXPORT_FORMATS = [
    {"label": "HTML", "value": ".html"},
    {"label": "PNG", "value": ".png"},
    {"label": "SVG", "value": ".svg"},
    {"label": "PDF", "value": ".pdf"},
]

# Plot settings
# Must carry a CSS unit — a bare "800" is invalid CSS and silently ignored.
DEFAULT_PLOT_HEIGHT = "800px"
DEFAULT_COLOR = "#3498db"
DEFAULT_LINE_WIDTH = 1.0
DEFAULT_OPACITY = 10
