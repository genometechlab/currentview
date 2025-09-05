# dash_app/layout/plot_style_settings.py
"""Plot style settings components for the settings panel."""

import dash_bootstrap_components as dbc
from dash import html, dcc

from ..config import LINE_STYLES

# Assuming you'll import these from utils:
from .elements import create_input, create_button, create_switch


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
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.Label("Width", className="modern-label"),
                                    dbc.InputGroup(
                                        [
                                            create_input(
                                                id=f"{prefix}-width",
                                                type="number",
                                                value=1200,
                                                min=400,
                                                max=4000,
                                                step=50,
                                            ),
                                            dbc.InputGroupText(
                                                "px",
                                                style={
                                                    "borderRadius": "0 10px 10px 0",
                                                    "background": "rgba(255, 255, 255, 0.1)",
                                                    "border": "1px solid rgba(0, 0, 0, 0.1)",
                                                },
                                            ),
                                        ]
                                    ),
                                ],
                                width=6,
                            ),
                            dbc.Col(
                                [
                                    html.Label("Height", className="modern-label"),
                                    dbc.InputGroup(
                                        [
                                            create_input(
                                                id=f"{prefix}-height",
                                                type="number",
                                                value=800,
                                                min=300,
                                                max=3000,
                                                step=50,
                                            ),
                                            dbc.InputGroupText(
                                                "px",
                                                style={
                                                    "borderRadius": "0 10px 10px 0",
                                                    "background": "rgba(255, 255, 255, 0.1)",
                                                    "border": "1px solid rgba(0, 0, 0, 0.1)",
                                                },
                                            ),
                                        ]
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
            # Line Styling Section
            create_settings_section(
                "Line Styling",
                "brush",
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.Label("Line Width", className="modern-label"),
                                    dbc.InputGroup(
                                        [
                                            create_input(
                                                id=f"{prefix}-line-width-style",
                                                type="number",
                                                value=2.0,
                                                min=0.1,
                                                max=10.0,
                                                step=0.1,
                                            ),
                                            dbc.InputGroupText(
                                                "px",
                                                style={
                                                    "borderRadius": "0 10px 10px 0",
                                                    "background": "rgba(255, 255, 255, 0.1)",
                                                    "border": "1px solid rgba(0, 0, 0, 0.1)",
                                                },
                                            ),
                                        ]
                                    ),
                                ],
                                width=6,
                            ),
                            dbc.Col(
                                [
                                    html.Label("Line Style", className="modern-label"),
                                    dbc.Select(
                                        id=f"{prefix}-line-style-default",
                                        options=LINE_STYLES,
                                        value="solid",
                                        style={
                                            "borderRadius": "10px",
                                            "border": "1px solid rgba(0, 0, 0, 0.1)",
                                            "background": "rgba(255, 255, 255, 0.9)",
                                            "padding": "12px 16px",
                                            "transition": "all 0.3s ease",
                                        },
                                    ),
                                ],
                                width=6,
                            ),
                        ],
                        className="mb-3",
                    ),
                ],
            ),
            html.Hr(style={"opacity": "0.1", "margin": "24px 0"}),
            # Colors and Theme Section
            create_settings_section(
                "Colors and Theme",
                "palette",
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.Label("Template", className="modern-label"),
                                    dbc.Select(
                                        id=f"{prefix}-template",
                                        options=[
                                            {"label": "Light", "value": "light"},
                                            {"label": "Dark", "value": "dark"},
                                        ],
                                        value="light",
                                        style={
                                            "borderRadius": "10px",
                                            "border": "1px solid rgba(0, 0, 0, 0.1)",
                                            "background": "rgba(255, 255, 255, 0.9)",
                                            "padding": "12px 16px",
                                            "transition": "all 0.3s ease",
                                        },
                                    ),
                                ],
                                width=12,
                            ),
                        ],
                        className="mb-4",
                    ),
                ],
            ),
            html.Hr(style={"opacity": "0.1", "margin": "24px 0"}),
            # Grid and Axes Section
            create_settings_section(
                "Grid and Axes",
                "grid-3x3",
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    create_switch(
                                        id=f"{prefix}-show-grid",
                                        label="Grid",
                                        value=False,
                                    ),
                                ],
                                width=6,
                            ),
                            dbc.Col(
                                [
                                    create_switch(
                                        id=f"{prefix}-show-legend",
                                        label="Legend",
                                        value=False,
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
                                    create_switch(
                                        id=f"{prefix}-zeroline",
                                        label="Zero Line",
                                        value=False,
                                    ),
                                ],
                                width=6,
                            ),
                            dbc.Col(
                                [
                                    create_switch(
                                        id=f"{prefix}-showline",
                                        label="Axis Lines",
                                        value=True,
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
            # Font Sizes Section
            create_settings_section(
                "Typography",
                "fonts",
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.Label("Title Size", className="modern-label"),
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
                                    html.Label(
                                        "Axis Title Size", className="modern-label"
                                    ),
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
                                    html.Label(
                                        "Tick Labels Size", className="modern-label"
                                    ),
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
                                    html.Label("Legend Size", className="modern-label"),
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
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.Label("Left", className="small-label"),
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
                                    html.Label("Right", className="small-label"),
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
                                    html.Label("Top", className="small-label"),
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
                                    html.Label("Bottom", className="small-label"),
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
                ],
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
                                    html.Label(
                                        "Barrier Style", className="modern-label"
                                    ),
                                    dbc.Select(
                                        id=f"{prefix}-barrier-style",
                                        options=LINE_STYLES,
                                        value="solid",
                                        style={
                                            "borderRadius": "10px",
                                            "border": "1px solid rgba(0, 0, 0, 0.1)",
                                            "background": "rgba(255, 255, 255, 0.9)",
                                            "padding": "12px 16px",
                                            "transition": "all 0.3s ease",
                                        },
                                    ),
                                ],
                                width=6,
                            ),
                            dbc.Col(
                                [
                                    html.Label(
                                        "Barrier Opacity", className="modern-label"
                                    ),
                                    dbc.InputGroup(
                                        [
                                            create_input(
                                                id=f"{prefix}-barrier-opacity",
                                                type="number",
                                                value=0.25,
                                                min=0.0,
                                                max=1.0,
                                                step=0.05,
                                            ),
                                            dbc.InputGroupText(
                                                "%",
                                                style={
                                                    "borderRadius": "0 10px 10px 0",
                                                    "background": "rgba(255, 255, 255, 0.1)",
                                                    "border": "1px solid rgba(0, 0, 0, 0.1)",
                                                },
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
                                    html.Label(
                                        "Barrier Color", className="modern-label"
                                    ),
                                    dbc.Input(
                                        id=f"{prefix}-barrier-color",
                                        type="color",
                                        value="#808080",
                                        style={
                                            "height": "44px",
                                            "borderRadius": "10px",
                                            "cursor": "pointer",
                                            "padding": "4px",
                                            "border": "1px solid rgba(0, 0, 0, 0.1)",
                                            "background": "rgba(255, 255, 255, 0.9)",
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
                [
                    create_button(
                        f"Apply {prefix.capitalize()} Style",
                        id=f"{prefix}-apply-style",
                        color="primary",
                        className="w-100",
                        size="lg",
                        icon="bi bi-check-circle",
                    ),
                ],
                style={"marginTop": "32px"},
            ),
        ],
        style={"padding": "20px"},
    )
