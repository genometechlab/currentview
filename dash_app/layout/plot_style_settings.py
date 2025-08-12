# dash_app/layout/plot_style_settings.py
"""Plot style settings components for the settings panel."""

import dash_bootstrap_components as dbc
from dash import html, dcc

from ..config import LINE_STYLES


def create_plot_style_settings(prefix: str = "signals") -> html.Div:
    """Create plot style settings for signals or stats.
    
    Args:
        prefix: Either "signals" or "stats" to create unique IDs
    """
    return html.Div([
        # Dimensions
        html.H6("Dimensions", className="mb-3"),
        dbc.Row([
            dbc.Col([
                dbc.Label("Width (px)", html_for=f"{prefix}-width"),
                dbc.Input(
                    id=f"{prefix}-width",
                    type="number",
                    value=1200,
                    min=400,
                    max=4000,
                    step=50
                ),
            ], width=6),
            dbc.Col([
                dbc.Label("Height (px)", html_for=f"{prefix}-height"),
                dbc.Input(
                    id=f"{prefix}-height",
                    type="number",
                    value=800,
                    min=300,
                    max=3000,
                    step=50
                ),
            ], width=6),
        ], className="mb-3"),
        
        # Line Styling
        html.H6("Line Styling", className="mb-3"),
        dbc.Row([
            dbc.Col([
                dbc.Label("Line Width", html_for=f"{prefix}-line-width-style"),
                dbc.Input(
                    id=f"{prefix}-line-width-style",
                    type="number",
                    value=2.0,
                    min=0.1,
                    max=10.0,
                    step=0.1
                ),
            ], width=6),
            dbc.Col([
                dbc.Label("Line Style", html_for=f"{prefix}-line-style-default"),
                dbc.Select(
                    id=f"{prefix}-line-style-default",
                    options=LINE_STYLES,
                    value="solid"
                ),
            ], width=6),
        ], className="mb-3"),
        
        # Opacity
        dbc.Row([
            dbc.Col([
                dbc.Label("Opacity Mode", html_for=f"{prefix}-opacity-mode"),
                dbc.Select(
                    id=f"{prefix}-opacity-mode",
                    options=[
                        {"label": "Auto", "value": "auto"},
                        {"label": "Fixed", "value": "fixed"},
                    ],
                    value="auto"
                ),
            ], width=6),
            dbc.Col([
                dbc.Label("Fixed Opacity", html_for=f"{prefix}-fixed-opacity"),
                dbc.Input(
                    id=f"{prefix}-fixed-opacity",
                    type="number",
                    value=0.8,
                    min=0.1,
                    max=1.0,
                    step=0.1,
                    disabled=True
                ),
            ], width=6),
        ], className="mb-3"),
        
        # Colors and Theme
        html.H6("Colors and Theme", className="mb-3"),
        dbc.Row([
            dbc.Col([
                dbc.Label("Template", html_for=f"{prefix}-template"),
                dbc.Select(
                    id=f"{prefix}-template",
                    options=[
                        {"label": "Plotly White", "value": "plotly_white"},
                        {"label": "Plotly Dark", "value": "plotly_dark"},
                        {"label": "Simple White", "value": "simple_white"},
                        {"label": "None", "value": "none"},
                    ],
                    value="plotly_white"
                ),
            ], width=12),
        ], className="mb-3"),
        
        # Grid and Axes
        html.H6("Grid and Axes", className="mb-3"),
        dbc.Row([
            dbc.Col([
                dbc.Switch(
                    id=f"{prefix}-show-grid",
                    label="Show Grid",
                    value=False,
                ),
            ], width=6),
            dbc.Col([
                dbc.Switch(
                    id=f"{prefix}-show-legend",
                    label="Show Legend",
                    value=True,
                ),
            ], width=6),
        ], className="mb-3"),
        
        dbc.Row([
            dbc.Col([
                dbc.Switch(
                    id=f"{prefix}-zeroline",
                    label="Show Zero Line",
                    value=False,
                ),
            ], width=6),
            dbc.Col([
                dbc.Switch(
                    id=f"{prefix}-showline",
                    label="Show Axis Lines",
                    value=True,
                ),
            ], width=6),
        ], className="mb-3"),
        
        # Fonts
        html.H6("Font Sizes", className="mb-3"),
        dbc.Row([
            dbc.Col([
                dbc.Label("Title", html_for=f"{prefix}-title-font-size"),
                dbc.Input(
                    id=f"{prefix}-title-font-size",
                    type="number",
                    value=20,
                    min=8,
                    max=48,
                    step=1
                ),
            ], width=6),
            dbc.Col([
                dbc.Label("Axis Title", html_for=f"{prefix}-axis-title-font-size"),
                dbc.Input(
                    id=f"{prefix}-axis-title-font-size",
                    type="number",
                    value=16,
                    min=8,
                    max=36,
                    step=1
                ),
            ], width=6),
        ], className="mb-3"),
        
        dbc.Row([
            dbc.Col([
                dbc.Label("Tick Labels", html_for=f"{prefix}-tick-font-size"),
                dbc.Input(
                    id=f"{prefix}-tick-font-size",
                    type="number",
                    value=12,
                    min=6,
                    max=24,
                    step=1
                ),
            ], width=6),
            dbc.Col([
                dbc.Label("Legend", html_for=f"{prefix}-legend-font-size"),
                dbc.Input(
                    id=f"{prefix}-legend-font-size",
                    type="number",
                    value=12,
                    min=6,
                    max=24,
                    step=1
                ),
            ], width=6),
        ], className="mb-3"),
        
        # Margins
        html.H6("Margins", className="mb-3"),
        dbc.Row([
            dbc.Col([
                dbc.Label("Left", html_for=f"{prefix}-margin-l"),
                dbc.Input(
                    id=f"{prefix}-margin-l",
                    type="number",
                    value=80,
                    min=0,
                    max=200,
                    step=10
                ),
            ], width=3),
            dbc.Col([
                dbc.Label("Right", html_for=f"{prefix}-margin-r"),
                dbc.Input(
                    id=f"{prefix}-margin-r",
                    type="number",
                    value=80,
                    min=0,
                    max=200,
                    step=10
                ),
            ], width=3),
            dbc.Col([
                dbc.Label("Top", html_for=f"{prefix}-margin-t"),
                dbc.Input(
                    id=f"{prefix}-margin-t",
                    type="number",
                    value=100,
                    min=0,
                    max=200,
                    step=10
                ),
            ], width=3),
            dbc.Col([
                dbc.Label("Bottom", html_for=f"{prefix}-margin-b"),
                dbc.Input(
                    id=f"{prefix}-margin-b",
                    type="number",
                    value=80,
                    min=0,
                    max=200,
                    step=10
                ),
            ], width=3),
        ], className="mb-3"),
        
        # Barrier Style (for k-mer barriers)
        html.H6("K-mer Barrier Style", className="mb-3"),
        dbc.Row([
            dbc.Col([
                dbc.Label("Barrier Style", html_for=f"{prefix}-barrier-style"),
                dbc.Select(
                    id=f"{prefix}-barrier-style",
                    options=LINE_STYLES,
                    value="solid"
                ),
            ], width=6),
            dbc.Col([
                dbc.Label("Barrier Opacity", html_for=f"{prefix}-barrier-opacity"),
                dbc.Input(
                    id=f"{prefix}-barrier-opacity",
                    type="number",
                    value=0.25,
                    min=0.0,
                    max=1.0,
                    step=0.05
                ),
            ], width=6),
        ], className="mb-3"),
        
        dbc.Row([
            dbc.Col([
                dbc.Label("Barrier Color", html_for=f"{prefix}-barrier-color"),
                dbc.Input(
                    id=f"{prefix}-barrier-color",
                    type="color",
                    value="#808080"  # grey
                ),
            ], width=6),
        ], className="mb-3"),
        
        # Apply button
        dbc.Button(
            f"Apply {prefix.capitalize()} Style",
            id=f"{prefix}-apply-style",
            color="primary",
            className="w-100 mt-3"
        ),
    ])