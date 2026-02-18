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

from .elements import (
    create_button,
    create_card,
    create_input,
    create_label,
    create_select,
    create_button_group,
)

from .constants import *

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
    return dbc.Row(cols, className=className, align="end")


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
                                    create_label("Window Size (K)", required=True),
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
                                    html.Div(style={"height": "16px"}),  # Spacer
                                    create_label("K-mer Labels"),
                                    dbc.Textarea(
                                        id="kmer-labels",
                                        rows=2,
                                        placeholder="Enter custom labels (comma separated)\nExample: A,T,G,C,A,T,G,C,A",
                                        style={
                                            "fontFamily": "'Fira Code', monospace",
                                            "borderRadius": "10px",
                                            "border": "1.5px solid #e2e8f0",
                                            "padding": "10px 14px",
                                        },
                                    ),
                                    dbc.FormText(
                                        "Optional: Custom labels for each window position"
                                    ),
                                ],
                                width=6,
                            ),
                            dbc.Col(
                                [
                                    create_label("Statistics Functions", required=True),
                                    dbc.InputGroup(
                                        [
                                            create_select(
                                                id="stat-select",
                                                options=STATISTICS_OPTIONS,
                                                placeholder="Select statistic...",
                                                style={"borderRadius": RADIUS_LEFT},
                                            ),
                                            create_button(
                                                "Add",
                                                id="add-stat",
                                                color="success",
                                                size="md",
                                                style={"borderRadius": RADIUS_RIGHT},
                                            ),
                                        ],
                                    ),
                                    html.Div(id="stats-list", className="mt-3"),
                                    dbc.FormText(
                                        "Statistics to calculate for each position"
                                    ),
                                    html.Div(style={"height": "16px"}),  # Spacer
                                    create_label("Molecule Type", required=True),
                                    dbc.RadioItems(
                                        options=[
                                            {"label": "DNA", "value": "dna"},
                                            {"label": "RNA", "value": "rna"},
                                        ],
                                        value="rna",
                                        id="molecule-type-options",
                                        className="modern-checklist",
                                    ),
                                ],
                                width=6,
                            ),
                        ],
                        className="g-4",
                    ),
                    html.Div(style={"height": "24px"}),  # Spacer
                    create_button(
                        "Initialize",
                        id="init-btn",
                        color="primary",
                        size="lg",
                        className="w-100",
                        icon="bi bi-play-fill",
                    ),
                    html.Hr(style={"opacity": "0.1", "margin": "24px 0"}),
                    dbc.Collapse(
                        [create_advanced_options()],
                        id="advanced",
                        is_open=False,
                    ),
                    dbc.Button(
                        "▼ Advanced Options",
                        id="toggle-adv",
                        color="link",
                        size="sm",
                        style={
                            "padding": "0",
                            "textDecoration": "none",
                            "color": "#667eea",
                        },
                    ),
                ],
                className="mb-4",
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
                            create_label("Title"),
                            create_input(
                                id="custom-title",
                                placeholder="Nanopore Signal Visualization",
                            ),
                            html.Div(style={"height": "16px"}),
                            create_label("Verbosity Level"),
                            create_select(
                                id="verbosity",
                                options=VERBOSITY_LEVELS,
                                value="0",
                            ),
                        ],
                        width=6,
                    ),
                    dbc.Col(
                        [
                            create_label("Signal Normalization"),
                            dbc.RadioItems(
                                id="normalization-options",
                                options=NORMALIZATION_METHODS,
                                value="none",
                                inline=True,
                                className="modern-checklist",
                            ),
                            html.Div(style={"height": "16px"}),
                            create_label("Signal Filtering"),
                            dbc.RadioItems(
                                id="filtering-options",
                                options=FILTERING_OPTIONS,
                                value="none",
                                className="modern-checklist",
                                inline=True,
                            ),
                            # Collapse sections for filter params
                            dbc.Collapse(
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                create_label("Sigma"),
                                                create_input(
                                                    id="gaussian-sigma",
                                                    type="number",
                                                    value=1,
                                                    min=0,
                                                    step=0.1,
                                                    size="sm",
                                                ),
                                            ],
                                            width=6,
                                        ),
                                    ],
                                    className="g-2 mt-2",
                                ),
                                id="gaussian-params",
                                is_open=False,
                            ),
                            dbc.Collapse(
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                create_label("Order"),
                                                create_input(
                                                    id="bessel-order",
                                                    type="number",
                                                    value=4,
                                                    min=1,
                                                    step=1,
                                                    size="sm",
                                                ),
                                            ],
                                            width=6,
                                        ),
                                        dbc.Col(
                                            [
                                                create_label("Cutoff (0–1)"),
                                                create_input(
                                                    id="bessel-cutoff",
                                                    type="number",
                                                    value=0.2,
                                                    min=0,
                                                    max=1,
                                                    step=0.01,
                                                    size="sm",
                                                ),
                                            ],
                                            width=6,
                                        ),
                                    ],
                                    className="g-2 mt-2",
                                ),
                                id="bessel-params",
                                is_open=False,
                            ),
                        ],
                        width=6,
                    ),
                ],
                className="g-4",
            ),
            html.Hr(style={"opacity": "0.1", "margin": "24px 0"}),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            create_label("Plot Styles"),
                            dbc.Checklist(
                                id="style-options",
                                options=STYLE_OPTIONS,
                                value=[],
                                inline=True,
                                className="modern-checklist",
                            ),
                            html.Div(style={"height": "16px"}),
                            create_label("Custom Plot Style (JSON)"),
                            dbc.Textarea(
                                id="custom-style",
                                rows=3,
                                placeholder='{"line_width": 1.5, "opacity_mode": "auto"}',
                                style={
                                    "fontFamily": "'Fira Code', monospace",
                                    "borderRadius": "10px",
                                    "border": "1.5px solid #e2e8f0",
                                    "padding": "10px 14px",
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
                                className="mb-0",
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
                    create_file_inputs(),
                    html.Div(style={"height": "8px"}),
                    create_condition_parameters(),
                    html.Div(style={"height": "8px"}),
                    create_visualization_style_inputs(),
                    html.Div(style={"height": "24px"}),
                    create_button(
                        "Add Condition",
                        id="add-condition-button",
                        color="success",
                        className="w-100",
                        size="lg",
                        icon="bi bi-plus-lg",
                    ),
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
        overlay_style={"visibility": "visible", "opacity": 0.25},
        delay_show=100,
        custom_spinner=html.H2(["Adding Condition ", dbc.Spinner(color="primary")]),
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
            "boxShadow": "0 4px 6px rgba(0, 0, 0, 0.1)",
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
                                style={"borderRadius": RADIUS_LEFT},
                            ),
                            create_button(
                                "Browse",
                                id="bam-browse",
                                size="md",
                                color="secondary",
                                icon="bi bi-folder-open",
                                style={"borderRadius": RADIUS_RIGHT},
                            ),
                        ]
                    ),
                ],
                width=6,
            ),
            dbc.Col(
                [
                    create_label("POD5 File or Directory", required=True),
                    dbc.InputGroup(
                        [
                            create_input(
                                id="pod5-display",
                                disabled=True,
                                placeholder="No file selected",
                                style={"borderRadius": RADIUS_LEFT},
                            ),
                            create_button(
                                "Browse",
                                id="pod5-browse",
                                size="md",
                                color="secondary",
                                icon="bi bi-folder-open",
                                style={"borderRadius": RADIUS_RIGHT},
                            ),
                        ]
                    ),
                ],
                width=6,
            ),
        ],
        className="g-3",
    )


from .elements import (
    create_button,
    create_card,
    create_input,
    create_label,
    create_select,
    create_button_group,
    COLOR_TEXT_MUTED,
)


def create_condition_parameters() -> html.Div:
    """Create condition parameter inputs with modern styling."""
    checkbox_style = {
        "fontSize": "0.875rem",
        "fontWeight": "500",
        "color": COLOR_TEXT_MUTED,
    }

    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            create_label("Contig", required=True),
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
                            create_label("Matched Query Base"),
                            create_button_group(
                                [
                                    {"text": "A", "id": "base-a"},
                                    {"text": "C", "id": "base-c"},
                                    {"text": "G", "id": "base-g"},
                                    {"text": "T", "id": "base-t"},
                                ],
                                size="md",
                            ),
                        ],
                        width=2,
                    ),
                    dbc.Col(
                        [
                            create_label("Max Reads"),
                            create_input(
                                id="max-reads", type="number", placeholder="e.g., 100"
                            ),
                        ],
                        width=2,
                    ),
                    dbc.Col(
                        [
                            create_label("Label"),
                            create_input(
                                id="condition-label", placeholder="Auto-generated"
                            ),
                        ],
                        width=3,
                    ),
                ],
                className="g-3",
                align="end",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Checkbox(
                            id="exclude-indels",
                            label="Exclude reads with indels",
                            value=False,
                            className="modern-checkbox",
                            style=checkbox_style,
                        ),
                        width="auto",
                    ),
                    dbc.Col(
                        dbc.Checkbox(
                            id="exclude-non-primaries",
                            label="Exclude non-primaries",
                            value=True,
                            className="modern-checkbox",
                            style=checkbox_style,
                        ),
                        width="auto",
                    ),
                ],
                className="mt-3",
                justify="center",
            ),
        ]
    )


def create_visualization_style_inputs() -> dbc.Row:
    """Create visualization style inputs with modern design."""
    return dbc.Row(
        [
            dbc.Col(
                [
                    create_label("Visualization Style"),
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.Label("Color", className="small-label mb-1"),
                                    dbc.Input(
                                        id="condition-color",
                                        type="color",
                                        value=DEFAULT_COLOR,
                                        style={
                                            "height": FORM_CONTROL_HEIGHT,
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
                                    html.Label(
                                        "Line Style", className="small-label mb-1"
                                    ),
                                    create_select(
                                        id="line-style",
                                        options=LINE_STYLES,
                                        value="solid",
                                    ),
                                ],
                                width=3,
                            ),
                            dbc.Col(
                                [
                                    html.Label(
                                        "Line Width", className="small-label mb-1"
                                    ),
                                    dbc.InputGroup(
                                        [
                                            create_input(
                                                id="line-width",
                                                type="number",
                                                value=DEFAULT_LINE_WIDTH,
                                                min=0.1,
                                                max=5.0,
                                                step=0.1,
                                                style={"borderRadius": RADIUS_LEFT},
                                            ),
                                            dbc.InputGroupText(
                                                "px",
                                                style={
                                                    "background": COLOR_BG_INPUT,
                                                    "borderRadius": RADIUS_RIGHT,
                                                    "height": FORM_CONTROL_HEIGHT,
                                                },
                                            ),
                                        ]
                                    ),
                                ],
                                width=3,
                            ),
                            dbc.Col(
                                [
                                    html.Label("Opacity", className="small-label mb-1"),
                                    dbc.InputGroup(
                                        [
                                            create_input(
                                                id="opacity",
                                                type="number",
                                                value=DEFAULT_OPACITY,
                                                min=1,
                                                max=100,
                                                step=1,
                                                style={"borderRadius": RADIUS_LEFT},
                                            ),
                                            dbc.InputGroupText(
                                                "%",
                                                style={
                                                    "background": COLOR_BG_INPUT,
                                                    "borderRadius": RADIUS_RIGHT,
                                                    "height": FORM_CONTROL_HEIGHT,
                                                },
                                            ),
                                        ]
                                    ),
                                ],
                                width=3,
                            ),
                        ],
                        className="g-2",
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
                [html.I(className="bi bi-list-check me-2"), "Conditions"],
                className="mb-3",
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
        overlay_style={"visibility": "visible", "opacity": 0.25},
        delay_show=100,
        custom_spinner=html.H2(["Updating Conditions ", dbc.Spinner(color="primary")]),
    )


def create_condition_card(
    label: str, color: str, line_style: str, line_width: float, opacity: int
) -> html.Div:
    """Create a condition card for the conditions list with modern design."""
    return create_card(
        [
            html.H6(
                label,
                className="mb-3",
                style={"fontWeight": "600", "color": "#2d3748"},
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Label("Color", className="small-label mb-1"),
                            dbc.Input(
                                id={"type": "color-edit", "index": label},
                                type="color",
                                value=color,
                                style={
                                    "height": FORM_CONTROL_HEIGHT_SM,
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
                            html.Label("Line Style", className="small-label mb-1"),
                            create_select(
                                id={"type": "line-style-edit", "index": label},
                                options=LINE_STYLES,
                                value=line_style,
                                size="sm",
                            ),
                        ],
                        width=2,
                    ),
                    dbc.Col(
                        [
                            html.Label("Line Width", className="small-label mb-1"),
                            dbc.InputGroup(
                                [
                                    create_input(
                                        id={"type": "line-width-edit", "index": label},
                                        type="number",
                                        value=line_width,
                                        min=0.1,
                                        max=5.0,
                                        step=0.1,
                                        size="sm",
                                        style={"borderRadius": "8px 0 0 8px"},
                                    ),
                                    dbc.InputGroupText(
                                        "px",
                                        style={
                                            "background": COLOR_BG_INPUT,
                                            "borderRadius": "0 8px 8px 0",
                                            "fontSize": "0.875rem",
                                        },
                                    ),
                                ]
                            ),
                        ],
                        width=2,
                    ),
                    dbc.Col(
                        [
                            html.Label("Opacity", className="small-label mb-1"),
                            dbc.InputGroup(
                                [
                                    create_input(
                                        id={"type": "opacity-edit", "index": label},
                                        type="number",
                                        value=opacity,
                                        min=1,
                                        max=100,
                                        step=1,
                                        size="sm",
                                        style={"borderRadius": "8px 0 0 8px"},
                                    ),
                                    dbc.InputGroupText(
                                        "%",
                                        style={
                                            "background": COLOR_BG_INPUT,
                                            "borderRadius": "0 8px 8px 0",
                                            "fontSize": "0.875rem",
                                        },
                                    ),
                                ]
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
                                    "marginTop": "20px",
                                    "display": "flex",
                                    "justifyContent": "flex-end",
                                },
                            ),
                        ],
                        width=4,
                    ),
                ],
                align="end",
            ),
        ],
        className="mb-3",
        style={"padding": "20px"},
    )


# ============================================================================
# Analysis Tab Input Bars
# ============================================================================


def create_gmm_inputs() -> html.Div:
    """Create input bar for GMM tab."""
    return html.Div(
        [
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
                                className="mb-2",
                            ),
                        ],
                        width=12,
                    ),
                ],
                className="mb-3",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            create_label("Statistic 1", required=True),
                            create_select(
                                id="gmm-stat1", options=None, placeholder="Stat 1..."
                            ),
                        ],
                        width=2,
                    ),
                    dbc.Col(
                        [
                            create_label("Statistic 2"),
                            create_select(
                                id="gmm-stat2", options=None, placeholder="Stat 2..."
                            ),
                        ],
                        width=2,
                    ),
                    dbc.Col(
                        [
                            create_label("Covariance Type", required=True),
                            create_select(
                                id="gmm-covariance-type",
                                options=[
                                    {"label": "Full", "value": "full"},
                                    {"label": "Tied", "value": "tied"},
                                    {"label": "Diagonal", "value": "diag"},
                                    {"label": "Spherical", "value": "spherical"},
                                ],
                                value="full",
                            ),
                        ],
                        width=2,
                    ),
                    dbc.Col(
                        create_button(
                            "Run GMM", id="gmm-run-btn", color="primary", size="md"
                        ),
                        width="auto",
                        className="ms-auto",
                    ),
                ],
                className="g-2",
                align="end",
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
            dbc.Row(
                [
                    dbc.Col(
                        [
                            create_label("Position Range", required=True),
                            dcc.RangeSlider(
                                id="umap-position-range",
                                min=-5,
                                max=5,
                                step=1,
                                value=[-5, 5],
                                marks={},
                                tooltip={"placement": "bottom", "always_visible": True},
                                className="mb-2",
                            ),
                        ],
                        width=12,
                    ),
                ],
                className="mb-3",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            create_label("Statistics", required=True),
                            dbc.InputGroup(
                                [
                                    create_select(
                                        id="umap-stats-select",
                                        options=None,
                                        placeholder="Select statistic...",
                                        style={"borderRadius": RADIUS_LEFT},
                                    ),
                                    create_button(
                                        "Add",
                                        id="select-umap-stat",
                                        color="success",
                                        size="md",
                                        style={"borderRadius": RADIUS_RIGHT},
                                    ),
                                ]
                            ),
                        ],
                        width=4,
                    ),
                    dbc.Col(
                        [
                            create_label("Neighbors", required=True),
                            create_input(
                                id="umap-n-neighbors", type="number", value=10
                            ),
                        ],
                        width=2,
                    ),
                    dbc.Col(
                        [
                            create_label("Min Distance", required=True),
                            create_input(
                                id="umap-min-dist", type="number", value=0.1, step=0.01
                            ),
                        ],
                        width=2,
                    ),
                    dbc.Col(
                        create_button(
                            "Run UMAP", id="umap-run-btn", color="primary", size="md"
                        ),
                        width="auto",
                        className="ms-auto",
                    ),
                ],
                className="g-2",
                align="end",
            ),
            # Selected stats badges — only visible once stats are added
            html.Div(id="umap-stats-list", style={"marginTop": "12px"}),
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
            create_gmm_inputs(),
            create_umap_inputs(),
            html.Hr(style={"opacity": "0.1"}),
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
                        create_button(
                            "Export",
                            id="export-browse",
                            color="success",
                            size="sm",
                            icon="bi bi-save",
                        ),
                        width=6,
                        className="d-flex justify-content-end",
                    ),
                ],
                className="mb-3",
            ),
            html.Div(id="plot-container", className="d-flex justify-content-center"),
        ]
    )

    return dcc.Loading(
        [card],
        type="circle",
        overlay_style={"visibility": "visible", "opacity": 0.25},
        delay_show=100,
        custom_spinner=html.H2(["Generating Plot ", dbc.Spinner(color="primary")]),
    )
