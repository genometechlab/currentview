# dash_app/config.py
"""Configuration constants for the Dash application."""

# Default paths
DEFAULT_BAM_PATH = "/data/tRNA_model_training/Data/bam_files/06_07_25_RNA4/06_07_25_RNA4_ecolscerIVTpooltRNA.dorado_1.0.0.moves.aligned.sorted.filtered.bam"
DEFAULT_POD5_PATH = "/data/tRNA/yeast/06_07_25_RNA4_ecolscerIVTpooltRNA/06_07_25_RNA4_ecolscerIVTpooltRNA/20250617_1515_P2S-00721-A_PAW01223_5b5d2793/pod5_skip"
DEFAULT_DATA_PATH = "/data/tRNA"

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
    {"label": "Debug (4)", "value": "4"}
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
]

STYLE_OPTIONS = [
    {"label": "Dark theme", "value": "dark"},
    {"label": "Show grid", "value": "grid"},
    {"label": "Show legend", "value": "legend"},
    {"label": "Use WebGL renderer", "value": "WebGL"},
]

# Plot settings
DEFAULT_PLOT_HEIGHT = "800"
DEFAULT_COLOR = "#3498db"
DEFAULT_LINE_WIDTH = 1.0
DEFAULT_OPACITY = 10