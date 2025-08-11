# dash_app/layout/components.py
"""Reusable UI components for the Dash application."""

import dash_bootstrap_components as dbc
from dash import dcc, html
from typing import Optional, Dict, Any

from ..config import (
    WINDOW_SIZE_MIN, WINDOW_SIZE_MAX, WINDOW_SIZE_DEFAULT, WINDOW_SIZE_STEP,
    LINE_STYLES, VERBOSITY_LEVELS, STATISTICS_OPTIONS, STYLE_OPTIONS,
    DEFAULT_COLOR, DEFAULT_LINE_WIDTH, DEFAULT_OPACITY
)


def create_initialization_card() -> dbc.Card:
    """Create the initialization card component."""
    return dbc.Card([
        dbc.CardHeader("Initialize Visualizer"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.Label("Window Size (K)"),
                    dbc.Input(
                        id="window-size", 
                        type="number", 
                        value=WINDOW_SIZE_DEFAULT, 
                        min=WINDOW_SIZE_MIN, 
                        max=WINDOW_SIZE_MAX, 
                        step=WINDOW_SIZE_STEP
                    ),
                    dbc.FormFeedback("Must be odd number", type="invalid"),
                ], width=6),
                dbc.Col([
                    html.Br(),
                    dbc.Button(
                        "Initialize", 
                        id="init-btn", 
                        color="primary", 
                        className="w-100"
                    ),
                ], width=6),
            ]),
            html.Hr(),
            dbc.Collapse([
                create_advanced_options()
            ], id="advanced", is_open=False),
            dbc.Button("Advanced ▼", id="toggle-adv", color="link", size="sm"),
        ])
    ], className="mb-4", id="init-card")


def create_advanced_options() -> html.Div:
    """Create the advanced options section."""
    return html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Label("K-mer Labels"),
                dbc.Textarea(
                    id="kmer-labels", 
                    rows=4, 
                    placeholder="Enter custom labels for each position (one per line)\nExample:\nA\nT\nG\nC\nA\nT\nG\nC\nA", 
                    style={"fontFamily": "monospace"}
                ),
                dbc.FormText("Optional: Provide custom labels for each position in the window"),
            ], width=6),
            dbc.Col([
                dbc.Label("Title"),
                dbc.Input(id="custom-title", placeholder="Nanopore Signal Visualization"),
                html.Br(),
                dbc.Label("Verbosity Level"),
                dbc.Select(id="verbosity", options=VERBOSITY_LEVELS, value="0"),
            ], width=6),
        ]),
        html.Hr(),
        dbc.Row([
            dbc.Col([
                dbc.Label("Statistics Functions"),
                dbc.InputGroup([
                    dbc.Select(
                        id="stat-select", 
                        options=STATISTICS_OPTIONS, 
                        placeholder="Select statistic..."
                    ),
                    dbc.Button("Add", id="add-stat", color="success", size="sm"),
                ], size="sm"),
                html.Div(id="stats-list", className="mt-2"),
                dbc.FormText("Select statistics to calculate for each position"),
            ], width=6),
            dbc.Col([
                dbc.Label("Plot Styles"),
                dbc.Checklist(
                    id="style-options", 
                    options=STYLE_OPTIONS, 
                    value=["WebGL"], 
                    inline=True
                ),
                html.Br(),
                dbc.Label("Custom Plot Style (JSON)"),
                dbc.Textarea(
                    id="custom-style", 
                    rows=3, 
                    placeholder='{"line_width": 1.5, "opacity_mode": "auto"}', 
                    style={"fontFamily": "monospace"}
                ),
                dbc.FormText("Optional: JSON format for PlotStyle parameters"),
            ], width=6),
        ]),
    ])


def create_add_condition_card() -> dbc.Card:
    """Create the add condition card component."""
    return dbc.Card([
        dbc.CardHeader("Add Condition"),
        dbc.CardBody([
            create_file_inputs(),
            html.Hr(),
            create_condition_parameters(),
            html.Hr(),
            create_visualization_style_inputs(),
            html.Hr(),
            dbc.Row([
                dbc.Col([
                    dbc.Button(
                        "Add Condition", 
                        id="add-condition-button", 
                        color="success", 
                        className="w-100", 
                        size="lg"
                    ),
                ], width=12),
            ]),
        ])
    ], className="mb-4")


def create_file_inputs() -> dbc.Row:
    """Create file input section."""
    return dbc.Row([
        dbc.Col([
            dbc.Label("BAM File"),
            dbc.InputGroup([
                dbc.Input(id="bam-display", disabled=True, placeholder="No file selected"),
                dbc.Button("Browse", id="bam-browse", outline=True, color="primary"),
            ]),
        ], width=6),
        dbc.Col([
            dbc.Label("POD5 File"),
            dbc.InputGroup([
                dbc.Input(id="pod5-display", disabled=True, placeholder="No file selected"),
                dbc.Button("Browse", id="pod5-browse", outline=True, color="primary"),
            ]),
        ], width=6),
    ])


def create_condition_parameters() -> dbc.Row:
    """Create condition parameter inputs."""
    return dbc.Row([
        dbc.Col([
            dbc.Label("Contig"),
            dbc.Input(id="contig", type="text", placeholder="e.g., chr1, chrX"),
        ], width=3),
        dbc.Col([
            dbc.Label("Target Position"),
            dbc.Input(id="position", type="number", placeholder="e.g., 12345"),
        ], width=2),                    
        dbc.Col([
            dbc.Label("Target Base"),
            dbc.Input(id="target-base", type="text", placeholder="A,C,G, or T"),
        ], width=2),
        dbc.Col([
            dbc.Label("Max Reads"),
            dbc.Input(id="max-reads", type="number", placeholder="e.g., 100"),
        ], width=2),
        dbc.Col([
            dbc.Label("Label (optional)"),
            dbc.Input(id="condition-label", type="text", placeholder="Auto-generated"),
        ], width=3),
    ])


def create_visualization_style_inputs() -> dbc.Row:
    """Create visualization style inputs."""
    return dbc.Row([
        dbc.Col([
            dbc.Label("Visualization Style", className="mb-3"),
            dbc.Row([
                dbc.Col([
                    dbc.Label("Color", style={"fontSize": "0.9em"}),
                    dbc.Input(
                        id="condition-color", 
                        type="color", 
                        value=DEFAULT_COLOR,
                        style={"height": "40px"}
                    ),
                ], width=3),
                dbc.Col([
                    dbc.Label("Line Style", style={"fontSize": "0.9em"}),
                    dbc.Select(
                        id="line-style",
                        options=LINE_STYLES,
                        value="solid"
                    ),
                ], width=3),
                dbc.Col([
                    dbc.Label("Line Width", style={"fontSize": "0.9em"}),
                    dbc.InputGroup([
                        dbc.Input(
                            id="line-width",
                            type="number",
                            value=DEFAULT_LINE_WIDTH,
                            min=0.1,
                            max=5.0,
                            step=0.1
                        ),
                        dbc.InputGroupText("px")
                    ], size="sm"),
                ], width=3),
                dbc.Col([
                    dbc.Label("Opacity (Alpha)", style={"fontSize": "0.9em"}),
                    dbc.InputGroup([
                        dbc.Input(
                            id="opacity",
                            type="number",
                            value=DEFAULT_OPACITY,
                            min=1,
                            max=100,
                            step=1
                        ),
                        dbc.InputGroupText(id="opacity-text", children="%")
                    ], size="sm"),
                ], width=3),
            ])
        ], width=12),
    ])


def create_condition_card(
    label: str,
    color: str,
    line_style: str,
    line_width: float,
    opacity: int
) -> dbc.Card:
    """Create a condition card for the conditions list."""
    return dbc.Card(dbc.CardBody([
        dbc.Row([
            dbc.Col([
                html.H6(label, className="mb-1"),
            ], width=8),
        ]),
        dbc.Row([
            # Left group - 4 input columns
            dbc.Col([
                dbc.Label("Color", style={"fontSize": "0.9em"}),
                dbc.Input(
                    id={"type": "color-edit", "index": label},
                    type="color",
                    value=color,
                ),
            ], width=2),
            dbc.Col([
                dbc.Label("Line Style", style={"fontSize": "0.9em"}),
                dbc.Select(
                    id={"type": "line-style-edit", "index": label},
                    options=LINE_STYLES,
                    value=line_style,
                ),
            ], width=2),
            dbc.Col([
                dbc.Label("Line Width", style={"fontSize": "0.9em"}),
                dbc.InputGroup([
                    dbc.Input(
                        id={"type": "line-width-edit", "index": label},
                        type="number",
                        value=line_width,
                        min=0.1,
                        max=5.0,
                        step=0.1
                    ),
                    dbc.InputGroupText("px")
                ], size="sm"),
            ], width=2),
            dbc.Col([
                dbc.Label("Opacity (Alpha)", style={"fontSize": "0.9em"}),
                dbc.InputGroup([
                    dbc.Input(
                        id={"type": "opacity-edit", "index": label},
                        type="number",
                        value=opacity,
                        min=1,
                        max=100,
                        step=1
                    ),
                    dbc.InputGroupText("%")
                ], size="sm"),
            ], width=2),
            
            # Right group - buttons with spacing to align with inputs
            dbc.Col([
                dbc.Row([
                    dbc.Col([
                        dbc.Button(
                            "Update",
                            color="info",
                            size="sm",
                            id={"type": "update-btn", "index": label},
                            className="me-1",
                            style={"marginTop": "1.75rem"}
                        ),
                    ], width="auto"),
                    dbc.Col([
                        dbc.Button(
                            "Remove",
                            color="danger",
                            size="sm",
                            id={"type": "remove-btn", "index": label},
                            style={"marginTop": "1.75rem"}
                        ),
                    ], width="auto"),
                ], justify="end")
            ], width=4),
        ])
    ]), className="mb-2")