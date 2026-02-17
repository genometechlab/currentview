# dash_app/layout/plot_style_settings.py
"""Plot style settings components for the settings panel."""

import dash_bootstrap_components as dbc
from dash import html

from ..config import LINE_STYLES

from .elements import (
    create_input,
    create_button,
    create_select,
    create_label,
)

from .constants import *

# Shared style for InputGroupText units ("px", "%") — right-side cap
_UNIT_TEXT_STYLE = {
    "borderRadius": RADIUS_RIGHT,
    "background": COLOR_BG_INPUT,
    "border": f"1.5px solid {COLOR_BORDER}",
    "height": FORM_CONTROL_HEIGHT,
}

# Inline switch style used directly in the panel
_SWITCH_STYLE = {
    "fontSize": "0.9375rem",
    "fontWeight": "500",
    "color": "#475569",
}


def create_settings_section(title: str, icon: str, children) -> html.Div:
    """Create a settings section with modern styling."""
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


def _px_input(id: str, value, min, max, step=1) -> dbc.InputGroup:
    """Shorthand for a number input with a px unit cap."""
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


def create_plot_style_settings(prefix: str = "signals") -> html.Div:
    """Create plot style settings for signals or stats with modern design.

    Args:
        prefix: Either "signals" or "stats" to create unique IDs
    """
    return html.Div(
        [
            # Dimensions Section
            create_settings_section(
                "Dimensions",
                "aspect-ratio",
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                create_label("Width"),
                                _px_input(
                                    f"{prefix}-width",
                                    value=1200,
                                    min=400,
                                    max=4000,
                                    step=50,
                                ),
                            ],
                            width=6,
                        ),
                        dbc.Col(
                            [
                                create_label("Height"),
                                _px_input(
                                    f"{prefix}-height",
                                    value=800,
                                    min=300,
                                    max=3000,
                                    step=50,
                                ),
                            ],
                            width=6,
                        ),
                    ],
                    className="mb-4",
                ),
            ),
            html.Hr(style={"opacity": "0.1", "margin": "24px 0"}),
            # Line Styling Section
            create_settings_section(
                "Line Styling",
                "brush",
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                create_label("Line Width"),
                                _px_input(
                                    f"{prefix}-line-width-style",
                                    value=2.0,
                                    min=0.1,
                                    max=10.0,
                                    step=0.1,
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
            html.Hr(style={"opacity": "0.1", "margin": "24px 0"}),
            # Colors and Theme Section
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
            html.Hr(style={"opacity": "0.1", "margin": "24px 0"}),
            # Grid and Axes Section
            create_settings_section(
                "Grid and Axes",
                "grid-3x3",
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.Switch(
                                id=f"{prefix}-show-grid",
                                label="Grid",
                                value=False,
                                style=_SWITCH_STYLE,
                            ),
                            width=6,
                        ),
                        dbc.Col(
                            dbc.Switch(
                                id=f"{prefix}-show-legend",
                                label="Legend",
                                value=False,
                                style=_SWITCH_STYLE,
                            ),
                            width=6,
                        ),
                        dbc.Col(
                            dbc.Switch(
                                id=f"{prefix}-zeroline",
                                label="Zero Line",
                                value=False,
                                style=_SWITCH_STYLE,
                            ),
                            width=6,
                            className="mt-2",
                        ),
                        dbc.Col(
                            dbc.Switch(
                                id=f"{prefix}-showline",
                                label="Axis Lines",
                                value=True,
                                style=_SWITCH_STYLE,
                            ),
                            width=6,
                            className="mt-2",
                        ),
                    ],
                    className="mb-4",
                ),
            ),
            html.Hr(style={"opacity": "0.1", "margin": "24px 0"}),
            # Typography Section
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
            html.Hr(style={"opacity": "0.1", "margin": "24px 0"}),
            # Margins Section
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
            html.Hr(style={"opacity": "0.1", "margin": "24px 0"}),
            # K-mer Barrier Style Section
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
                                            dbc.InputGroupText(
                                                "%", style=_UNIT_TEXT_STYLE
                                            ),
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
            # Apply button
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
            ),
        ],
        style={"padding": "20px"},
    )
