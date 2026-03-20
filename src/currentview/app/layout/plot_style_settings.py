"""Plot style settings components for the settings panel."""

import dash_bootstrap_components as dbc
from dash import html

from ..config import LINE_STYLES
from .elements import create_input, create_button, create_select, create_label
from ..styles.constants import (
    BORDER_RADIUS,
    COLOR_BORDER,
    COLOR_BG_INPUT,
    FORM_CONTROL_HEIGHT,
    RADIUS_LEFT,
    RADIUS_RIGHT,
)

# ── Shared sub-component styles ───────────────────────────────────────────────

_UNIT_TEXT_STYLE = {
    "borderRadius": RADIUS_RIGHT,
    "background": COLOR_BG_INPUT,
    "border": f"1.5px solid {COLOR_BORDER}",
    "height": FORM_CONTROL_HEIGHT,
}

_SWITCH_STYLE = {
    "fontSize": "0.9375rem",
    "fontWeight": "500",
    "color": "#475569",
}

_HR = html.Hr(style={"opacity": "0.1", "margin": "24px 0"})


# ── Section wrapper ───────────────────────────────────────────────────────────


def create_settings_section(title: str, icon: str, children) -> html.Div:
    return html.Div(
        [
            html.Div(
                [
                    html.I(className=f"bi bi-{icon} me-2", style={"color": "#667eea"}),
                    html.H6(
                        title,
                        className="mb-0",
                        style={"display": "inline", "fontWeight": "600"},
                    ),
                ],
                className="mb-3",
            ),
            html.Div(children, style={"paddingLeft": "24px"}),
        ]
    )


# ── Sub-component helpers ─────────────────────────────────────────────────────


def _px_input(id: str, value, min, max, step=1) -> dbc.InputGroup:
    return dbc.InputGroup(
        [
            create_input(
                id=id,
                type="number",
                value=value,
                min=min,
                max=max,
                step=step,
                style={"borderRadius": RADIUS_LEFT},
            ),
            dbc.InputGroupText("px", style=_UNIT_TEXT_STYLE),
        ]
    )


def _switch(id: str, label: str, value: bool = False) -> dbc.Switch:
    return dbc.Switch(id=id, label=label, value=value, style=_SWITCH_STYLE)


# ── Main builder ──────────────────────────────────────────────────────────────


def create_plot_style_settings(prefix: str = "signals") -> html.Div:
    """Create plot style settings panel for signals or stats.

    Args:
        prefix: "signals" or "stats"
    """
    is_stats = prefix == "stats"

    sections = [
        # Dimensions
        create_settings_section(
            "Dimensions",
            "aspect-ratio",
            dbc.Row(
                [
                    dbc.Col(
                        [
                            create_label("Width"),
                            _px_input(f"{prefix}-width", 1200, 400, 4000, 50),
                        ],
                        width=6,
                    ),
                    dbc.Col(
                        [
                            create_label("Height"),
                            _px_input(f"{prefix}-height", 800, 300, 3000, 50),
                        ],
                        width=6,
                    ),
                ],
                className="mb-4",
            ),
        ),
        _HR,
        # Line Styling
        create_settings_section(
            "Line Styling",
            "brush",
            dbc.Row(
                [
                    dbc.Col(
                        [
                            create_label("Line Width"),
                            _px_input(
                                f"{prefix}-line-width-style", 2.0, 0.1, 10.0, 0.1
                            ),
                        ],
                        width=6,
                    ),
                    dbc.Col(
                        [
                            create_label("Line Style"),
                            create_select(
                                id=f"{prefix}-line-style-default",
                                options=LINE_STYLES,
                                value="solid",
                            ),
                        ],
                        width=6,
                    ),
                ],
                className="mb-3",
            ),
        ),
        _HR,
        # Colors and Theme
        create_settings_section(
            "Colors and Theme",
            "palette",
            dbc.Row(
                [
                    dbc.Col(
                        [
                            create_label("Template"),
                            create_select(
                                id=f"{prefix}-template",
                                options=[
                                    {"label": "Light", "value": "light"},
                                    {"label": "Dark", "value": "dark"},
                                ],
                                value="light",
                            ),
                        ],
                        width=12,
                    ),
                ],
                className="mb-4",
            ),
        ),
        _HR,
        # Grid and Axes
        create_settings_section(
            "Grid and Axes",
            "grid-3x3",
            dbc.Row(
                [
                    dbc.Col(_switch(f"{prefix}-show-grid", "Grid"), width=6),
                    dbc.Col(_switch(f"{prefix}-show-legend", "Legend"), width=6),
                    dbc.Col(
                        _switch(f"{prefix}-zeroline", "Zero Line"),
                        width=6,
                        className="mt-2",
                    ),
                    dbc.Col(
                        _switch(f"{prefix}-showline", "Axis Lines", value=True),
                        width=6,
                        className="mt-2",
                    ),
                ],
                className="mb-4",
            ),
        ),
        _HR,
        # Typography
        create_settings_section(
            "Typography",
            "fonts",
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                create_label("Title Size"),
                                create_input(
                                    id=f"{prefix}-title-font-size",
                                    type="number",
                                    value=20,
                                    min=8,
                                    max=48,
                                    step=1,
                                ),
                            ],
                            width=6,
                        ),
                        dbc.Col(
                            [
                                create_label("Axis Title Size"),
                                create_input(
                                    id=f"{prefix}-axis-title-font-size",
                                    type="number",
                                    value=16,
                                    min=8,
                                    max=36,
                                    step=1,
                                ),
                            ],
                            width=6,
                        ),
                    ],
                    className="mb-3",
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                create_label("Tick Labels Size"),
                                create_input(
                                    id=f"{prefix}-tick-font-size",
                                    type="number",
                                    value=12,
                                    min=6,
                                    max=24,
                                    step=1,
                                ),
                            ],
                            width=6,
                        ),
                        dbc.Col(
                            [
                                create_label("Legend Size"),
                                create_input(
                                    id=f"{prefix}-legend-font-size",
                                    type="number",
                                    value=12,
                                    min=6,
                                    max=24,
                                    step=1,
                                ),
                            ],
                            width=6,
                        ),
                    ],
                    className="mb-4",
                ),
            ],
        ),
        _HR,
        # Margins
        create_settings_section(
            "Margins",
            "arrows-expand",
            dbc.Row(
                [
                    dbc.Col(
                        [
                            create_label("Left"),
                            create_input(
                                id=f"{prefix}-margin-l",
                                type="number",
                                value=80,
                                min=0,
                                max=200,
                                step=10,
                            ),
                        ],
                        width=3,
                    ),
                    dbc.Col(
                        [
                            create_label("Right"),
                            create_input(
                                id=f"{prefix}-margin-r",
                                type="number",
                                value=80,
                                min=0,
                                max=200,
                                step=10,
                            ),
                        ],
                        width=3,
                    ),
                    dbc.Col(
                        [
                            create_label("Top"),
                            create_input(
                                id=f"{prefix}-margin-t",
                                type="number",
                                value=100,
                                min=0,
                                max=200,
                                step=10,
                            ),
                        ],
                        width=3,
                    ),
                    dbc.Col(
                        [
                            create_label("Bottom"),
                            create_input(
                                id=f"{prefix}-margin-b",
                                type="number",
                                value=80,
                                min=0,
                                max=200,
                                step=10,
                            ),
                        ],
                        width=3,
                    ),
                ],
                className="mb-4",
            ),
        ),
        _HR,
        # K-mer Barrier Style
        create_settings_section(
            "K-mer Barrier Style",
            "segmented-nav",
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                create_label("Barrier Style"),
                                create_select(
                                    id=f"{prefix}-barrier-style",
                                    options=LINE_STYLES,
                                    value="solid",
                                ),
                            ],
                            width=6,
                        ),
                        dbc.Col(
                            [
                                create_label("Barrier Opacity"),
                                dbc.InputGroup(
                                    [
                                        create_input(
                                            id=f"{prefix}-barrier-opacity",
                                            type="number",
                                            value=0.25,
                                            min=0.0,
                                            max=1.0,
                                            step=0.05,
                                            style={"borderRadius": RADIUS_LEFT},
                                        ),
                                        dbc.InputGroupText("%", style=_UNIT_TEXT_STYLE),
                                    ]
                                ),
                            ],
                            width=6,
                        ),
                    ],
                    className="mb-3",
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                create_label("Barrier Color"),
                                dbc.Input(
                                    id=f"{prefix}-barrier-color",
                                    type="color",
                                    value="#808080",
                                    style={
                                        "height": FORM_CONTROL_HEIGHT,
                                        "borderRadius": BORDER_RADIUS,
                                        "cursor": "pointer",
                                        "padding": "4px",
                                        "border": f"1.5px solid {COLOR_BORDER}",
                                        "background": COLOR_BG_INPUT,
                                    },
                                ),
                            ],
                            width=6,
                        ),
                    ],
                    className="mb-4",
                ),
            ],
        ),
    ]

    # Distribution kind — stats only
    if is_stats:
        sections += [
            _HR,
            create_settings_section(
                "Distribution",
                "bar-chart-line",
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                create_label("Display Type"),
                                create_select(
                                    id="stats-distribution-kind",
                                    options=[
                                        {"label": "KDE", "value": "kde"},
                                        {"label": "Histogram", "value": "histogram"},
                                        {"label": "Both", "value": "both"},
                                    ],
                                    value="kde",
                                ),
                            ],
                            width=8,
                        ),
                    ],
                    className="mb-4",
                ),
            ),
        ]

    sections.append(
        html.Div(
            create_button(
                f"Apply {prefix.capitalize()} Style",
                id=f"{prefix}-apply-style",
                color="primary",
                className="w-100",
                size="lg",
                icon="bi bi-check-circle",
            ),
            style={"marginTop": "32px"},
        )
    )

    return html.Div(sections, style={"padding": "20px"})
