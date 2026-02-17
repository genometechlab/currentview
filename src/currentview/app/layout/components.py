import dash_bootstrap_components as dbc
from dash import dcc, html
from typing import Optional, Dict, Any, List

from ..config import (
    WINDOW_SIZE_MIN,
    WINDOW_SIZE_MAX,
    WINDOW_SIZE_DEFAULT,
    WINDOW_SIZE_STEP,
    LINE_STYLES,
    VERBOSITY_LEVELS,
    STATISTICS_OPTIONS,
    STYLE_OPTIONS,
    NORMALIZATION_METHODS,
    FILTERING_OPTIONS,
    DEFAULT_COLOR,
    DEFAULT_LINE_WIDTH,
    DEFAULT_OPACITY,
)

from .elements import create_button, create_card, create_input, create_label


# ============================================================================
# Styling Constants
# ============================================================================

TAB_STYLE = {"borderRadius": "8px 8px 0 0"}
ACTIVE_TAB_STYLE = {
    "borderRadius": "8px 8px 0 0",
    "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    "color": "white",
}

# ============================================================================
# Helper Functions
# ============================================================================


def create_tab(label: str, tab_id: str, disabled: bool = False) -> dbc.Tab:
    """Create a styled tab component."""
    kwargs = {
        "label": label,
        "id": f"{tab_id}-tab",
        "tab_id": tab_id,
        "disabled": disabled,
        "tab_style": TAB_STYLE,
        "active_tab_style": ACTIVE_TAB_STYLE,
    }

    return dbc.Tab(**kwargs)


def create_input_row(inputs: List[Dict[str, Any]], className: str = "g-2") -> dbc.Row:
    """Create a row of input fields.

    Args:
        inputs: List of dicts with keys: component, width
        className: CSS class for the row
    """
    cols = [dbc.Col(inp["component"], width=inp.get("width", "auto")) for inp in inputs]
    return dbc.Row(cols, className=className)


# ============================================================================
# Top Bar
# ============================================================================


def create_top_bar() -> html.Div:
    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Button(
                                html.I(className="bi bi-gear-fill"),
                                id="settings-btn",
                                color="link",
                                className="text-white",
                                style={
                                    "display": "none",
                                    "marginLeft": "20px",
                                    "fontSize": "1.2rem",
                                },
                            )
                        ],
                        width=3,
                        className="d-flex align-items-center",
                    ),
                    dbc.Col(
                        [
                            html.Img(
                                src="assets/icon.png",
                                height="40px",
                                style={"marginRight": "15px"},
                            ),
                            html.H2(
                                "CurrentView",
                                className="text-center mb-0",
                                id="app-title",
                                style={
                                    "color": "white",
                                    "fontWeight": "300",
                                    "letterSpacing": "3px",
                                    "fontSize": "1.8rem",
                                    "textShadow": "2px 2px 4px rgba(0,0,0,0.3)",
                                    "cursor": "pointer",
                                },
                            ),
                        ],
                        width=6,
                        className="d-flex align-items-center justify-content-center",
                    ),
                    dbc.Col(
                        [
                            html.Div(
                                [
                                    html.I(
                                        id="sun-icon",
                                        className="bi bi-sun-fill",
                                        style={
                                            "color": "#ffc107",
                                            "fontSize": "1.2rem",
                                        },
                                    ),
                                    dbc.Switch(
                                        id="theme-toggle",
                                        value=False,
                                        className="mx-2",
                                        style={"fontSize": "1.2rem"},
                                    ),
                                    html.I(
                                        id="moon-icon",
                                        className="bi bi-moon",
                                        style={
                                            "color": "#6c757d",
                                            "fontSize": "1.2rem",
                                        },
                                    ),
                                ],
                                className="d-flex align-items-center",
                                style={"marginRight": "20px", "gap": "0"},
                            )
                        ],
                        width=3,
                        className="d-flex align-items-center justify-content-end",
                    ),
                ],
                className="align-items-center",
                style={"height": "48px", "margin": "0"},
            ),
        ],
        id="top-bar",
        style={
            "position": "fixed",
            "top": 0,
            "left": 0,
            "right": 0,
            "background": "#1e293b",
            "backdropFilter": "blur(10px)",
            "boxShadow": "0 4px 6px rgba(0,0,0,.3)",
            "paddingTop": "12px",
            "paddingBottom": "12px",
            "zIndex": 1030,
        },
    )


# ============================================================================
# Initialization Card
# ============================================================================


def create_initialization_card() -> html.Div:
    """Create the initialization card component with modern design."""
    return html.Div(
        [
            create_card(
                [
                    html.Div(
                        [
                            html.H4(
                                [
                                    html.I(className="bi bi-rocket-takeoff me-2"),
                                    "Initialize Visualizer",
                                ],
                                className="mb-4 card-title",
                                style={"fontWeight": "600", "color": "#2d3748"},
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            html.Label(
                                                "Window Size (K)",
                                                className="modern-label",
                                            ),
                                            create_input(
                                                id="window-size",
                                                type="number",
                                                value=WINDOW_SIZE_DEFAULT,
                                                min=WINDOW_SIZE_MIN,
                                                max=WINDOW_SIZE_MAX,
                                                step=WINDOW_SIZE_STEP,
                                            ),
                                            dbc.FormFeedback(
                                                "Must be odd number", type="invalid"
                                            ),
                                            html.Br(),
                                            html.Label(
                                                "K-mer Labels", className="modern-label"
                                            ),
                                            dbc.Textarea(
                                                id="kmer-labels",
                                                rows=2,
                                                placeholder="Enter custom labels for each position (comma separated)\nExample: A,T,G,C,A,T,G,C,A",
                                                style={
                                                    "fontFamily": "'Fira Code', monospace",
                                                    "borderRadius": "10px",
                                                    "border": "1px solid rgba(0, 0, 0, 0.1)",
                                                    "background": "rgba(255, 255, 255, 0.5)",
                                                    "padding": "12px",
                                                },
                                            ),
                                            dbc.FormText(
                                                "Optional: Provide custom labels for each position in the window"
                                            ),
                                        ],
                                        width=6,
                                    ),
                                    dbc.Col(
                                        [
                                            html.Label(
                                                "Statistics Functions",
                                                className="modern-label",
                                            ),
                                            dbc.InputGroup(
                                                [
                                                    dbc.Select(
                                                        id="stat-select",
                                                        options=STATISTICS_OPTIONS,
                                                        placeholder="Select statistic...",
                                                        style={
                                                            "borderRadius": "10px 0 0 10px"
                                                        },
                                                    ),
                                                    create_button(
                                                        "Add",
                                                        id="add-stat",
                                                        color="success",
                                                        size="sm",
                                                    ),
                                                ],
                                                style={"borderRadius": "10px"},
                                            ),
                                            html.Div(id="stats-list", className="mt-3"),
                                            dbc.FormText(
                                                "Select statistics to calculate for each position"
                                            ),
                                            html.Br(),
                                            html.Label(
                                                "Molecule Type",
                                                className="modern-label",
                                            ),
                                            dbc.RadioItems(
                                                options=[
                                                    {"label": "DNA", "value": "dna"},
                                                    {"label": "RNA", "value": "rna"},
                                                ],
                                                value="rna",
                                                id="molecule-type-options",
                                                className="modern-checklist",
                                            ),
                                        ]
                                    ),
                                ]
                            ),
                            dbc.Row(
                                [
                                    html.Div(
                                        style={"height": "29px"}
                                    ),  # Spacer to align button
                                    create_button(
                                        "Initialize",
                                        id="init-btn",
                                        color="primary",
                                        className="w-100",
                                        icon="bi bi-play-fill",
                                    ),
                                ]
                            ),
                            html.Hr(style={"opacity": "0.1", "margin": "24px 0"}),
                            dbc.Collapse(
                                [create_advanced_options()],
                                id="advanced",
                                is_open=False,
                            ),
                            dbc.Button(
                                [
                                    "▼ Advanced Options",
                                ],
                                id="toggle-adv",
                                color="link",
                                size="sm",
                                style={
                                    "padding": "0",
                                    "textDecoration": "none",
                                    "color": "#667eea",
                                },
                            ),
                        ]
                    )
                ],
                className="mb-4",
                style={"animation": "fadeIn 0.5s ease"},
            )
        ],
        id="init-card",
    )


def create_advanced_options() -> html.Div:
    """Create the advanced options section with modern styling."""
    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Label("Title", className="modern-label"),
                            create_input(
                                id="custom-title",
                                placeholder="Nanopore Signal Visualization",
                            ),
                            html.Br(),
                            html.Label("Verbosity Level", className="modern-label"),
                            dbc.Select(
                                id="verbosity",
                                options=VERBOSITY_LEVELS,
                                value="0",
                                style={
                                    "borderRadius": "10px",
                                    "border": "1px solid rgba(0, 0, 0, 0.1)",
                                    "background": "rgba(255, 255, 255, 0.9)",
                                    "padding": "12px",
                                },
                            ),
                        ],
                        width=6,
                    ),
                    dbc.Col(
                        [
                            html.Label(
                                "Signal Normalization", className="modern-label"
                            ),
                            dbc.RadioItems(
                                id="normalization-options",
                                options=NORMALIZATION_METHODS,
                                value="none",
                                inline=True,
                                className="modern-checklist",
                            ),
                            html.Br(),
                            html.Label("Signal Filtering", className="modern-label"),
                            dbc.RadioItems(
                                id="filtering-options",
                                options=FILTERING_OPTIONS,
                                value="none",
                                className="modern-checklist",
                                inline=True,
                            ),
                            dbc.Collapse(
                                id="gaussian-params",
                                is_open=False,
                                children=[
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    html.Label(
                                                        "Sigma", className="small-label"
                                                    ),
                                                    dbc.Input(
                                                        id="gaussian-sigma",
                                                        type="number",
                                                        min=0,
                                                        step=0.1,
                                                        value=1,
                                                    ),
                                                ],
                                                width=6,
                                            ),
                                        ],
                                        className="g-2",
                                    ),
                                ],
                            ),
                            dbc.Collapse(
                                id="bessel-params",
                                is_open=False,
                                children=[
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    html.Label(
                                                        "Order", className="small-label"
                                                    ),
                                                    dbc.Input(
                                                        id="bessel-order",
                                                        type="number",
                                                        min=1,
                                                        step=1,
                                                        value=4,
                                                    ),
                                                ],
                                                width=6,
                                            ),
                                            dbc.Col(
                                                [
                                                    html.Label(
                                                        "Cutoff (0–1)",
                                                        className="small-label",
                                                    ),
                                                    dbc.Input(
                                                        id="bessel-cutoff",
                                                        type="number",
                                                        min=0,
                                                        max=1,
                                                        step=0.01,
                                                        value=0.2,
                                                    ),
                                                ],
                                                width=6,
                                            ),
                                        ],
                                        className="g-2",
                                    ),
                                ],
                            ),
                        ],
                        width=6,
                    ),
                ]
            ),
            html.Hr(style={"opacity": "0.1", "margin": "24px 0"}),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Label("Plot Styles", className="modern-label"),
                            dbc.Checklist(
                                id="style-options",
                                options=STYLE_OPTIONS,
                                value=[],
                                inline=True,
                                className="modern-checklist",
                            ),
                            html.Br(),
                            html.Label(
                                "Custom Plot Style (JSON)", className="modern-label"
                            ),
                            dbc.Textarea(
                                id="custom-style",
                                rows=3,
                                placeholder='{"line_width": 1.5, "opacity_mode": "auto"}',
                                style={
                                    "fontFamily": "'Fira Code', monospace",
                                    "borderRadius": "10px",
                                    "border": "1px solid rgba(0, 0, 0, 0.1)",
                                    "background": "rgba(255, 255, 255, 0.5)",
                                    "padding": "12px",
                                },
                            ),
                            dbc.FormText(
                                "Optional: JSON format for PlotStyle parameters"
                            ),
                        ],
                        width=6,
                    ),
                ]
            ),
        ],
        style={"marginTop": "20px"},
    )


# ============================================================================
# Add Condition Card
# ============================================================================


def create_add_condition_card() -> html.Div:
    """Create the add condition card component with modern design."""
    card = create_card(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H5(
                                [
                                    html.I(className="bi bi-plus-circle me-2"),
                                    "Add Condition",
                                ],
                                className="mb-0 card-title",
                                style={"fontWeight": "600", "color": "#2d3748"},
                            ),
                        ],
                        width=10,
                    ),
                    dbc.Col(
                        [
                            dbc.Button(
                                html.I(
                                    className="bi bi-chevron-up",
                                    id="add-condition-chevron",
                                ),
                                id="toggle-add-condition",
                                color="link",
                                size="sm",
                                className="float-end p-0",
                            ),
                        ],
                        width=2,
                        className="text-end",
                    ),
                ],
                align="center",
                className="mb-3",
            ),
            dbc.Collapse(
                [
                    html.Div(
                        [
                            create_file_inputs(),
                            html.Hr(style={"opacity": "0.0", "margin": "8px 0"}),
                            create_condition_parameters(),
                            html.Hr(style={"opacity": "0.1", "margin": "8 0"}),
                            create_visualization_style_inputs(),
                            html.Hr(style={"opacity": "0.1", "margin": "12 0px"}),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            create_button(
                                                "Add Condition",
                                                id="add-condition-button",
                                                color="success",
                                                className="w-100",
                                                size="lg",
                                                icon="bi bi-plus-lg",
                                            ),
                                        ],
                                        width=12,
                                    ),
                                ]
                            ),
                        ]
                    )
                ],
                id="add-condition-collapse",
                is_open=True,
            ),
        ],
        className="mb-4",
    )
    return dcc.Loading(
        [card],
        type="circle",
        overlay_style={
            "visibility": "visible",
            "opacity": 0.25,
        },
        delay_show=100,
        custom_spinner=html.H2(
            ["Adding Condition ", dbc.Spinner(color="primary")],
        ),
    )


def create_add_condition_alert_box() -> dbc.Alert:
    return dbc.Alert(
        id="add-condition-alert",
        is_open=False,
        duration=4000,
        color="danger",
        style={
            "borderRadius": "12px",
            "border": "none",
            "boxShadow": "0 4px 6px rgba(0, 0, 0, 0.1),",
        },
    )


def create_file_inputs() -> dbc.Row:
    """Create file input section with modern styling."""
    return dbc.Row(
        [
            dbc.Col(
                [
                    create_label("BAM File", required=True),
                    dbc.InputGroup(
                        [
                            create_input(
                                id="bam-display",
                                disabled=True,
                                placeholder="No file selected",
                            ),
                            create_button(
                                "Browse",
                                id="bam-browse",
                                size="sm",
                                color="secondary",
                                icon="bi bi-folder-open",
                            ),
                        ],
                        style={"gap": "8px"},
                    ),
                ],
                width=6,
            ),
            dbc.Col(
                [
                    create_label("POD5 Directory", required=True),
                    dbc.InputGroup(
                        [
                            create_input(
                                id="pod5-display",
                                disabled=True,
                                placeholder="No file selected",
                            ),
                            create_button(
                                "Browse",
                                id="pod5-browse",
                                size="sm",
                                color="secondary",
                                icon="bi bi-folder-open",
                            ),
                        ],
                        style={"gap": "8px"},
                    ),
                ],
                width=6,
            ),
        ]
    )


def create_condition_parameters() -> dbc.Row:
    """Create condition parameter inputs with modern styling."""
    return dbc.Row(
        [
            dbc.Col(
                [
                    create_label("contig", required=True),
                    create_input(id="contig", placeholder="e.g., chr1, chrX"),
                ],
                width=3,
            ),
            dbc.Col(
                [
                    create_label("Target Position", required=True),
                    create_input(
                        id="position", type="number", placeholder="e.g., 12345"
                    ),
                ],
                width=2,
            ),
            dbc.Col(
                [
                    html.Label("Matched Query Base", className="modern-label"),
                    dbc.ButtonGroup(
                        [
                            dbc.Button(
                                "A",
                                id="base-a",
                                outline=True,
                                color="secondary",
                                size="sm",
                                style={"padding": "8px 6px"},
                            ),
                            dbc.Button(
                                "C",
                                id="base-c",
                                outline=True,
                                color="secondary",
                                size="sm",
                                style={"padding": "8px 6px"},
                            ),
                            dbc.Button(
                                "G",
                                id="base-g",
                                outline=True,
                                color="secondary",
                                size="sm",
                                style={"padding": "8px 6px"},
                            ),
                            dbc.Button(
                                "T",
                                id="base-t",
                                outline=True,
                                color="secondary",
                                size="sm",
                                style={"padding": "8px 6px"},
                            ),
                        ],
                    ),
                ],
                width=2,
            ),
            dbc.Col(
                [
                    html.Label("Max Reads", className="modern-label"),
                    create_input(
                        id="max-reads", type="number", placeholder="e.g., 100"
                    ),
                ],
                width=2,
            ),
            dbc.Col(
                [
                    html.Label("Label", className="modern-label"),
                    create_input(id="condition-label", placeholder="Auto-generated"),
                ],
                width=3,
            ),
        ]
    )


def create_visualization_style_inputs() -> dbc.Row:
    """Create visualization style inputs with modern design."""
    return dbc.Row(
        [
            dbc.Col(
                [
                    create_label("Visualization Style", required=False),
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.Label("Color", className="small-label"),
                                    dbc.Input(
                                        id="condition-color",
                                        type="color",
                                        value=DEFAULT_COLOR,
                                        style={
                                            "height": "44px",
                                            "borderRadius": "10px",
                                            "cursor": "pointer",
                                            "padding": "4px",
                                        },
                                    ),
                                ],
                                width=3,
                            ),
                            dbc.Col(
                                [
                                    html.Label("Line Style", className="small-label"),
                                    dbc.Select(
                                        id="line-style",
                                        options=LINE_STYLES,
                                        value="solid",
                                        style={
                                            "borderRadius": "10px",
                                            "border": "1px solid rgba(0, 0, 0, 0.1)",
                                            "background": "rgba(255, 255, 255, 0.9)",
                                            "padding": "8px 16px",
                                        },
                                    ),
                                ],
                                width=3,
                            ),
                            dbc.Col(
                                [
                                    html.Label("Line Width", className="small-label"),
                                    dbc.InputGroup(
                                        [
                                            create_input(
                                                id="line-width",
                                                type="number",
                                                value=DEFAULT_LINE_WIDTH,
                                                min=0.1,
                                                max=5.0,
                                                step=0.1,
                                                style={"borderRadius": "10px 0 0 10px"},
                                            ),
                                            dbc.InputGroupText(
                                                "px",
                                                style={"borderRadius": "0 10px 10px 0"},
                                            ),
                                        ]
                                    ),
                                ],
                                width=3,
                            ),
                            dbc.Col(
                                [
                                    html.Label("Opacity", className="small-label"),
                                    dbc.InputGroup(
                                        [
                                            create_input(
                                                id="opacity",
                                                type="number",
                                                value=DEFAULT_OPACITY,
                                                min=1,
                                                max=100,
                                                step=1,
                                                style={"borderRadius": "10px 0 0 10px"},
                                            ),
                                            dbc.InputGroupText(
                                                "%",
                                                id="opacity-text",
                                                style={
                                                    "borderRadius": "0 10px 10px 0"
                                                },  # Only round the RIGHT side
                                            ),
                                        ]
                                    ),
                                ],
                                width=3,
                            ),
                        ]
                    ),
                ],
                width=12,
            ),
        ]
    )


# ============================================================================
# Conditions List Card
# ============================================================================


def create_conditions_list_card():
    card = create_card(
        [
            html.H4(
                [
                    html.I(className="bi bi-list-check me-2"),
                    "Conditions",
                ],
                className="mb-3 card-title",
                style={"fontWeight": "600", "color": "#2d3748"},
            ),
            html.Hr(style={"opacity": "0.1"}),
            html.Div(id="conditions"),
        ],
        className="mb-4",
    )
    return dcc.Loading(
        [card],
        type="circle",
        overlay_style={
            "visibility": "visible",
            "opacity": 0.25,
        },
        delay_show=100,
        custom_spinner=html.H2(
            ["Updating Conditions ", dbc.Spinner(color="primary")],
        ),
    )


def create_condition_card(
    label: str, color: str, line_style: str, line_width: float, opacity: int
) -> html.Div:
    """Create a condition card for the conditions list with modern design."""
    return create_card(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H6(
                                label,
                                className="mb-3",
                                style={"fontWeight": "600", "color": "#2d3748"},
                            ),
                        ],
                        width=12,
                    ),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Label("Color", className="small-label"),
                            dbc.Input(
                                id={"type": "color-edit", "index": label},
                                type="color",
                                value=color,
                                style={
                                    "height": "40px",
                                    "borderRadius": "8px",
                                    "cursor": "pointer",
                                    "padding": "2px",
                                },
                            ),
                        ],
                        width=2,
                    ),
                    dbc.Col(
                        [
                            html.Label("Line Style", className="small-label"),
                            dbc.Select(
                                id={"type": "line-style-edit", "index": label},
                                options=LINE_STYLES,
                                value=line_style,
                                style={"borderRadius": "8px", "fontSize": "0.9rem"},
                            ),
                        ],
                        width=2,
                    ),
                    dbc.Col(
                        [
                            html.Label("Line Width", className="small-label"),
                            dbc.InputGroup(
                                [
                                    create_input(
                                        id={"type": "line-width-edit", "index": label},
                                        type="number",
                                        value=line_width,
                                        min=0.1,
                                        max=5.0,
                                        step=0.1,
                                    ),
                                    dbc.InputGroupText(
                                        "px", style={"fontSize": "0.9rem"}
                                    ),
                                ],
                                size="sm",
                            ),
                        ],
                        width=2,
                    ),
                    dbc.Col(
                        [
                            html.Label("Opacity", className="small-label"),
                            dbc.InputGroup(
                                [
                                    create_input(
                                        id={"type": "opacity-edit", "index": label},
                                        type="number",
                                        value=opacity,
                                        min=1,
                                        max=100,
                                        step=1,
                                    ),
                                    dbc.InputGroupText(
                                        "%", style={"fontSize": "0.9rem"}
                                    ),
                                ],
                                size="sm",
                            ),
                        ],
                        width=2,
                    ),
                    dbc.Col(
                        [
                            html.Div(
                                [
                                    create_button(
                                        "Update",
                                        color="info",
                                        size="sm",
                                        id={"type": "update-btn", "index": label},
                                        className="me-2",
                                        icon="bi bi-check-lg",
                                    ),
                                    create_button(
                                        "Remove",
                                        color="danger",
                                        size="sm",
                                        id={"type": "remove-btn", "index": label},
                                        icon="bi bi-trash",
                                    ),
                                ],
                                style={
                                    "marginTop": "24px",
                                    "display": "flex",
                                    "justifyContent": "flex-end",
                                },
                            )
                        ],
                        width=4,
                    ),
                ]
            ),
        ],
        className="mb-3",
        style={"padding": "20px"},
    )


# ============================================================================
# Analysis Tab Input Bars
# ============================================================================


def create_stat_selector_with_list(
    select_id: str,
    add_button_id: str,
    list_id: str,
) -> List:
    """Create a statistic selector dropdown with add button and badge list."""
    return [
        dbc.InputGroup(
            [
                dbc.Select(
                    id=select_id,
                    options=None,
                    placeholder="Select statistic...",
                    style={"borderRadius": "10px 0 0 10px"},
                ),
                create_button(
                    "Add",
                    id=add_button_id,
                    color="success",
                    size="sm",
                ),
            ],
            style={"borderRadius": "10px"},
        ),
        html.Div(id=list_id, className="mt-3"),
    ]


def create_gmm_inputs() -> html.Div:
    """Create input bar for GMM tab."""
    return html.Div(
        [
            # First row: Range slider for position selection
            dbc.Row(
                [
                    dbc.Col(
                        [
                            create_label("Position Range", required=True),
                            dcc.RangeSlider(
                                id="gmm-position-range",
                                min=-5,
                                max=5,
                                step=1,
                                value=[-5, 5],
                                marks={},
                                tooltip={"placement": "bottom", "always_visible": True},
                                className="mb-3",
                            ),
                        ],
                        width=12,
                    ),
                ],
                className="mb-3",
            ),
            # Second row: GMM parameters
            dbc.Row(
                [
                    # Stat 1 dropdown
                    dbc.Col(
                        [
                            create_label("Statistic 1", required=True),
                            dbc.Select(
                                id="gmm-stat1",
                                options=None,
                                placeholder="Stat 1...",
                                style={"borderRadius": "10px"},
                            ),
                        ],
                        width=2,
                    ),
                    # Stat 2 dropdown
                    dbc.Col(
                        [
                            create_label("Statistic 2", required=False),
                            dbc.Select(
                                id="gmm-stat2",
                                options=None,
                                placeholder="Stat 2...",
                                style={"borderRadius": "10px"},
                            ),
                        ],
                        width=2,
                    ),
                    # Covariance type dropdown
                    dbc.Col(
                        [
                            create_label("Covariance Type", required=True),
                            dbc.Select(
                                id="gmm-covariance-type",
                                options=[
                                    {"label": "Full", "value": "full"},
                                    {"label": "Tied", "value": "tied"},
                                    {"label": "Diagonal", "value": "diag"},
                                    {"label": "Spherical", "value": "spherical"},
                                ],
                                value="full",
                                style={"borderRadius": "10px"},
                            ),
                        ],
                        width=2,
                    ),
                    # Run button
                    dbc.Col(
                        create_button(
                            "Run GMM",
                            id="gmm-run-btn",
                            color="primary",
                            size="sm",
                        ),
                        width="auto",
                        className="ms-auto",
                    ),
                ],
                className="g-2",
            ),
        ],
        id="gmm-inputs",
        style={"display": "none"},
        className="mb-3 p-3 bg-light rounded",
    )


def create_umap_inputs() -> html.Div:
    """Create input bar for UMAP tab with stat selector and position range slider."""
    return html.Div(
        [
            # First row: Range slider for position selection
            dbc.Row(
                [
                    dbc.Col(
                        [
                            create_label("Position Range", required=True),
                            dcc.RangeSlider(
                                id="umap-position-range",
                                min=-5,  # Will be updated by callback based on K
                                max=5,  # Will be updated by callback based on K
                                step=1,
                                value=[-5, 5],  # Will be updated by callback
                                marks={},  # Will be populated by callback
                                tooltip={"placement": "bottom", "always_visible": True},
                                className="mb-3",
                            ),
                        ],
                        width=12,
                    ),
                ],
                className="mb-3",
            ),
            # Second row: Stats selector and parameters
            dbc.Row(
                [
                    dbc.Col(
                        [
                            create_label("Statistics", required=True),
                            dbc.InputGroup(
                                [
                                    dbc.Select(
                                        id="umap-stats-select",
                                        options=None,
                                        placeholder="Select statistic...",
                                        style={"borderRadius": "10px 0 0 10px"},
                                    ),
                                    create_button(
                                        "Add",
                                        id="select-umap-stat",
                                        color="success",
                                        size="sm",
                                    ),
                                ],
                                style={"borderRadius": "10px"},
                            ),
                            html.Div(id="umap-stats-list", className="mt-3"),
                        ],
                        width=4,
                    ),
                    dbc.Col(
                        [
                            create_label("Number of neighbors", required=True),
                            create_input(
                                id="umap-n-neighbors",
                                type="number",
                                value=10,
                            ),
                        ],
                        width=2,
                    ),
                    dbc.Col(
                        [
                            create_label("Min distance", required=True),
                            create_input(
                                id="umap-min-dist",
                                type="number",
                                value=0.1,
                            ),
                        ],
                        width=2,
                    ),
                    dbc.Col(
                        create_button(
                            "Run UMAP",
                            id="umap-run-btn",
                            color="primary",
                            size="sm",
                        ),
                        width="auto",
                        className="ms-auto",
                    ),
                ],
                className="g-2",
            ),
        ],
        id="umap-inputs",
        style={"display": "none"},
        className="mb-3 p-3 bg-light rounded",
    )


# ============================================================================
# Visualization Card (Main Plot Area)
# ============================================================================


def create_visualization_card() -> html.Div:
    """Create a visualization card for the plot."""
    card = create_card(
        [
            # Tabs
            dbc.Tabs(
                [
                    create_tab("Signals", "signals"),
                    create_tab("Statistics", "stats", disabled=True),
                    create_tab("GMM", "gmm", disabled=True),
                    create_tab("UMAP", "umap", disabled=True),
                ],
                id="tabs",
                active_tab="signals",
                className="nav-pills mb-3",
            ),
            # Tab-specific input bars
            create_gmm_inputs(),
            create_umap_inputs(),
            # Divider
            html.Hr(style={"opacity": "0.1"}),
            # Control buttons
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Row(
                            [
                                dbc.Col(
                                    create_button(
                                        "Refresh Plot",
                                        id="generate",
                                        color="secondary",
                                        size="sm",
                                        icon="bi bi-arrow-clockwise",
                                    ),
                                    width="auto",
                                ),
                                dbc.Col(
                                    create_button(
                                        "Clear Cache",
                                        id="clear-cache",
                                        color="warning",
                                        size="sm",
                                        icon="bi bi-trash",
                                    ),
                                    width="auto",
                                ),
                            ],
                            className="g-2",
                        ),
                        width=6,
                        className="d-flex justify-content-start",
                    ),
                    dbc.Col(
                        dbc.Row(
                            [
                                dbc.Col(
                                    create_button(
                                        "Export",
                                        id="export-browse",
                                        color="success",
                                        size="sm",
                                        icon="bi bi-save",
                                    ),
                                    width="auto",
                                ),
                            ],
                            className="g-2",
                        ),
                        width=6,
                        className="d-flex justify-content-end",
                    ),
                ],
                className="mb-3",
            ),
            # Plot container
            html.Div(
                id="plot-container",
                className="d-flex justify-content-center",
            ),
        ]
    )

    # Wrap in loading component like the other cards
    return dcc.Loading(
        [card],
        type="circle",
        overlay_style={
            "visibility": "visible",
            "opacity": 0.25,
        },
        delay_show=100,
        custom_spinner=html.H2(
            ["Generating Plot ", dbc.Spinner(color="primary")],
        ),
    )
