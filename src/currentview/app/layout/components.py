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
    create_dropdown,
)
from ..styles.constants import (
    BORDER_RADIUS,
    BORDER_RADIUS_SM,
    BORDER_RADIUS_LG,
    COLOR_BORDER,
    COLOR_BG_INPUT,
    COLOR_TEXT_MUTED,
    FORM_CONTROL_HEIGHT,
    FORM_CONTROL_HEIGHT_SM,
    TRANSITION,
    TAB_STYLE,
    ACTIVE_TAB_STYLE,
    RADIUS_LEFT,
    RADIUS_RIGHT,
    RADIUS_NONE,
    GRADIENT_PRIMARY,
)


# ── Shared styles ─────────────────────────────────────────────────────────────

_TEXTAREA_STYLE = {
    "fontFamily": "'Fira Code', monospace",
    "borderRadius": BORDER_RADIUS,
    "border": f"1.5px solid {COLOR_BORDER}",
    "padding": "10px 14px",
}

_CARD_TITLE_STYLE = {"fontWeight": "600"}

_INPUT_GROUP_TEXT_STYLE = {
    "background": COLOR_BG_INPUT,
    "height": FORM_CONTROL_HEIGHT,
}

_INPUT_GROUP_TEXT_STYLE_SM = {
    "background": COLOR_BG_INPUT,
    "fontSize": "0.875rem",
}

_CHECKBOX_STYLE = {
    "fontSize": "0.875rem",
    "fontWeight": "500",
    "color": COLOR_TEXT_MUTED,
}

_SPACER_SM = html.Div(style={"height": "8px"})
_SPACER_MD = html.Div(style={"height": "16px"})
_SPACER_LG = html.Div(style={"height": "24px"})
_HR = html.Hr(style={"opacity": "0.1", "margin": "24px 0"})

_ANALYSIS_CARD_STYLE = {"display": "none"}
_ANALYSIS_CARD_CLASS = "mb-3 p-3 bg-light rounded"


# ── Helpers ───────────────────────────────────────────────────────────────────


def create_tab(label: str, tab_id: str, disabled: bool = False) -> dbc.Tab:
    return dbc.Tab(
        label=label,
        id=f"{tab_id}-tab",
        tab_id=tab_id,
        disabled=disabled,
        tab_style=TAB_STYLE,
        active_tab_style=ACTIVE_TAB_STYLE,
    )


def create_input_row(inputs: List[Dict[str, Any]], className: str = "g-2") -> dbc.Row:
    """Row of input fields. Each dict requires 'component' and optionally 'width'."""
    cols = [dbc.Col(inp["component"], width=inp.get("width", "auto")) for inp in inputs]
    return dbc.Row(cols, className=className, align="end")


def _color_input(id, value, size: str = "md") -> dbc.Input:
    h = FORM_CONTROL_HEIGHT if size == "md" else FORM_CONTROL_HEIGHT_SM
    r = BORDER_RADIUS if size == "md" else BORDER_RADIUS_SM
    return dbc.Input(
        id=id,
        type="color",
        value=value,
        style={
            "height": h,
            "borderRadius": r,
            "cursor": "pointer",
            "padding": "4px" if size == "md" else "2px",
        },
    )


def _unit_input_group(input_component, unit: str, size: str = "md") -> dbc.InputGroup:
    text_style = _INPUT_GROUP_TEXT_STYLE if size == "md" else _INPUT_GROUP_TEXT_STYLE_SM
    return dbc.InputGroup(
        [
            input_component,
            dbc.InputGroupText(
                unit, style={**text_style, "borderRadius": RADIUS_RIGHT}
            ),
        ]
    )


def _with_loading(card, spinner_label: str) -> dcc.Loading:
    return dcc.Loading(
        [card],
        type="circle",
        overlay_style={"visibility": "visible", "opacity": 0.25},
        delay_show=100,
        custom_spinner=html.H2([spinner_label, dbc.Spinner(color="primary")]),
    )


# ── Top Bar ───────────────────────────────────────────────────────────────────


def create_top_bar() -> html.Div:
    return html.Div(
        dbc.Row(
            [
                dbc.Col(
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
                    ),
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
                    html.Div(
                        [
                            html.I(
                                id="sun-icon",
                                className="bi bi-sun-fill",
                                style={"color": "#ffc107", "fontSize": "1.2rem"},
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
                                style={"color": "#6c757d", "fontSize": "1.2rem"},
                            ),
                        ],
                        className="d-flex align-items-center",
                        style={"marginRight": "20px", "gap": "0"},
                    ),
                    width=3,
                    className="d-flex align-items-center justify-content-end",
                ),
            ],
            className="align-items-center",
            style={"height": "48px", "margin": "0"},
        ),
        id="top-bar",
        style={
            "position": "fixed",
            "top": 0,
            "left": 0,
            "right": 0,
            "backdropFilter": "blur(10px)",
            "boxShadow": "0 4px 6px rgba(0,0,0,.3)",
            "paddingTop": "12px",
            "paddingBottom": "12px",
            "zIndex": 1030,
        },  # background handled by #top-bar in theme CSS
    )


# ── Initialization Card ───────────────────────────────────────────────────────


def create_initialization_card() -> html.Div:
    return html.Div(
        create_card(
            [
                html.H4(
                    [
                        html.I(className="bi bi-rocket-takeoff me-2"),
                        "Initialize Visualizer",
                    ],
                    className="mb-4 card-title",
                    style=_CARD_TITLE_STYLE,
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
                                dbc.FormFeedback("Must be odd number", type="invalid"),
                                _SPACER_MD,
                                create_label("K-mer Labels"),
                                dbc.Textarea(
                                    id="kmer-labels",
                                    rows=2,
                                    placeholder="Enter custom labels (comma separated)\nExample: A,T,G,C,A,T,G,C,A",
                                    style=_TEXTAREA_STYLE,
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
                                    ]
                                ),
                                html.Div(id="stats-list", className="mt-3"),
                                dbc.FormText(
                                    "Statistics to calculate for each position"
                                ),
                                _SPACER_MD,
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
                _SPACER_LG,
                create_button(
                    "Initialize",
                    id="init-btn",
                    color="primary",
                    size="lg",
                    className="w-100",
                    icon="bi bi-play-fill",
                ),
                _HR,
                dbc.Collapse([create_advanced_options()], id="advanced", is_open=False),
                dbc.Button(
                    "▼ Advanced Options",
                    id="toggle-adv",
                    color="link",
                    size="sm",
                    style={
                        "padding": "0",
                        "textDecoration": "none",
                        "color": GRADIENT_PRIMARY.split(",")[0].split("(")[1].strip(),
                    },
                ),
            ],
            className="mb-4",
        ),
        id="init-card",
    )


def create_advanced_options() -> html.Div:
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
                            _SPACER_MD,
                            create_label("Verbosity Level"),
                            create_select(
                                id="verbosity", options=VERBOSITY_LEVELS, value="0"
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
                            _SPACER_MD,
                            create_label("Signal Filtering"),
                            dbc.RadioItems(
                                id="filtering-options",
                                options=FILTERING_OPTIONS,
                                value="none",
                                inline=True,
                                className="modern-checklist",
                            ),
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
            _HR,
            dbc.Row(
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
                        _SPACER_MD,
                        create_label("Custom Plot Style (JSON)"),
                        dbc.Textarea(
                            id="custom-style",
                            rows=3,
                            placeholder='{"line_width": 1.5, "opacity_mode": "auto"}',
                            style=_TEXTAREA_STYLE,
                        ),
                        dbc.FormText("Optional: JSON format for PlotStyle parameters"),
                    ],
                    width=6,
                ),
            ),
        ],
        style={"marginTop": "20px"},
    )


# ── Add Condition Card ────────────────────────────────────────────────────────


def create_add_condition_card() -> dcc.Loading:
    card = create_card(
        [
            dbc.Row(
                [
                    dbc.Col(
                        html.H5(
                            [
                                html.I(className="bi bi-plus-circle me-2"),
                                "Add Condition",
                            ],
                            className="mb-0",
                            style=_CARD_TITLE_STYLE,
                        ),
                        width=10,
                    ),
                    dbc.Col(
                        dbc.Button(
                            html.I(
                                className="bi bi-chevron-up", id="add-condition-chevron"
                            ),
                            id="toggle-add-condition",
                            color="link",
                            size="sm",
                            className="float-end p-0",
                        ),
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
                    _SPACER_SM,
                    create_condition_parameters(),
                    _SPACER_SM,
                    create_visualization_style_inputs(),
                    _SPACER_LG,
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
    return _with_loading(card, "Adding Condition ")


def create_add_condition_alert_box() -> dbc.Alert:
    return dbc.Alert(
        id="add-condition-alert",
        is_open=False,
        duration=4000,
        color="danger",
        style={
            "borderRadius": BORDER_RADIUS_LG,
            "border": "none",
            "boxShadow": "0 4px 6px rgba(0,0,0,0.1)",
        },
    )


def create_file_inputs() -> dbc.Row:
    def _file_col(label, input_id, browse_id):
        return dbc.Col(
            [
                create_label(label, required=True),
                dbc.InputGroup(
                    [
                        create_input(
                            id=input_id,
                            disabled=True,
                            placeholder="No file selected",
                            style={"borderRadius": RADIUS_LEFT},
                        ),
                        create_button(
                            "Browse",
                            id=browse_id,
                            size="md",
                            color="info",
                            icon="bi bi-folder-open",
                            style={"borderRadius": RADIUS_RIGHT},
                        ),
                    ]
                ),
            ],
            width=6,
        )

    return dbc.Row(
        [
            _file_col("BAM File", "bam-display", "bam-browse"),
            _file_col("POD5 File or Directory", "pod5-display", "pod5-browse"),
        ],
        className="g-3",
    )


def create_condition_parameters() -> html.Div:
    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            create_label("Contig", required=True),
                            create_dropdown(
                                id="contig",
                                placeholder="e.g., chr1, chrX",
                                options=[],
                                disabled=True,
                            ),
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
                                    {"text": t, "id": f"base-{t.lower()}"}
                                    for t in ("A", "C", "G", "T")
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
                            style=_CHECKBOX_STYLE,
                        ),
                        width="auto",
                    ),
                    dbc.Col(
                        dbc.Checkbox(
                            id="exclude-non-primaries",
                            label="Exclude non-primaries",
                            value=True,
                            className="modern-checkbox",
                            style=_CHECKBOX_STYLE,
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
    def _style_col(label, component):
        return dbc.Col(
            [html.Label(label, className="small-label mb-1"), component], width=3
        )

    return dbc.Row(
        dbc.Col(
            [
                create_label("Visualization Style"),
                dbc.Row(
                    [
                        _style_col(
                            "Color", _color_input("condition-color", DEFAULT_COLOR)
                        ),
                        _style_col(
                            "Line Style",
                            create_select(
                                id="line-style", options=LINE_STYLES, value="solid"
                            ),
                        ),
                        _style_col(
                            "Line Width",
                            _unit_input_group(
                                create_input(
                                    id="line-width",
                                    type="number",
                                    value=DEFAULT_LINE_WIDTH,
                                    min=0.1,
                                    max=5.0,
                                    step=0.1,
                                    style={"borderRadius": RADIUS_LEFT},
                                ),
                                "px",
                            ),
                        ),
                        _style_col(
                            "Opacity",
                            _unit_input_group(
                                create_input(
                                    id="opacity",
                                    type="number",
                                    value=DEFAULT_OPACITY,
                                    min=1,
                                    max=100,
                                    step=1,
                                    style={"borderRadius": RADIUS_LEFT},
                                ),
                                "%",
                            ),
                        ),
                    ],
                    className="g-2",
                ),
            ],
            width=12,
        ),
    )


# ── Conditions List Card ──────────────────────────────────────────────────────


def create_conditions_list_card() -> dcc.Loading:
    card = create_card(
        [
            html.H4(
                [html.I(className="bi bi-list-check me-2"), "Conditions"],
                className="mb-3",
                style=_CARD_TITLE_STYLE,
            ),
            html.Hr(style={"opacity": "0.1"}),
            html.Div(id="conditions"),
        ],
        className="mb-4",
    )
    return _with_loading(card, "Updating Conditions ")


def create_condition_card(
    label: str, color: str, line_style: str, line_width: float, opacity: int
) -> html.Div:
    def _style_col(col_label, component):
        return dbc.Col(
            [html.Label(col_label, className="small-label mb-1"), component], width=2
        )

    return create_card(
        [
            html.H6(label, className="mb-3", style=_CARD_TITLE_STYLE),
            dbc.Row(
                [
                    _style_col(
                        "Color",
                        _color_input(
                            {"type": "color-edit", "index": label}, color, size="sm"
                        ),
                    ),
                    _style_col(
                        "Line Style",
                        create_select(
                            id={"type": "line-style-edit", "index": label},
                            options=LINE_STYLES,
                            value=line_style,
                            size="sm",
                        ),
                    ),
                    _style_col(
                        "Line Width",
                        _unit_input_group(
                            create_input(
                                id={"type": "line-width-edit", "index": label},
                                type="number",
                                value=line_width,
                                min=0.1,
                                max=5.0,
                                step=0.1,
                                size="sm",
                                style={"borderRadius": RADIUS_LEFT},
                            ),
                            "px",
                            size="sm",
                        ),
                    ),
                    _style_col(
                        "Opacity",
                        _unit_input_group(
                            create_input(
                                id={"type": "opacity-edit", "index": label},
                                type="number",
                                value=opacity,
                                min=1,
                                max=100,
                                step=1,
                                size="sm",
                                style={"borderRadius": RADIUS_LEFT},
                            ),
                            "%",
                            size="sm",
                        ),
                    ),
                    dbc.Col(
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
                        width=4,
                    ),
                ],
                align="end",
            ),
        ],
        className="mb-3",
        style={"padding": "20px"},
    )


# ── Analysis Input Cards ──────────────────────────────────────────────────────


def _range_slider(id: str) -> dcc.RangeSlider:
    return dcc.RangeSlider(
        id=id,
        min=-5,
        max=5,
        step=1,
        value=[-5, 5],
        marks={},
        tooltip={"placement": "bottom", "always_visible": True},
        className="mb-2",
    )


def create_gmm_inputs() -> html.Div:
    return create_card(
        [
            dbc.Row(
                dbc.Col(
                    [
                        create_label("Position Range", required=True),
                        _range_slider("gmm-position-range"),
                    ],
                    width=12,
                ),
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
        style=_ANALYSIS_CARD_STYLE,
        className=_ANALYSIS_CARD_CLASS,
        variant="ghost",
    )


def create_umap_inputs() -> html.Div:
    return create_card(
        [
            dbc.Row(
                dbc.Col(
                    [
                        create_label("Position Range", required=True),
                        _range_slider("umap-position-range"),
                    ],
                    width=12,
                ),
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
            html.Div(id="umap-stats-list", style={"marginTop": "12px"}),
        ],
        id="umap-inputs",
        style=_ANALYSIS_CARD_STYLE,
        className=_ANALYSIS_CARD_CLASS,
        variant="ghost",
    )


# ── Visualization Card ────────────────────────────────────────────────────────


def create_visualization_card() -> dcc.Loading:
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
    return _with_loading(card, "Generating Plot ")
