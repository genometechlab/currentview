# dash_app/layout/main_layout.py
"""Main layout assembly for the Dash application."""

import uuid
import dash_bootstrap_components as dbc
from dash import dcc, html

from .components import (
    create_initialization_card,
    create_add_condition_card,
)
from .plot_style_settings import create_plot_style_settings
from .modals import create_file_browser_modal
from ..config import DEFAULT_BAM_PATH, DEFAULT_POD5_PATH, DEFAULT_PLOT_HEIGHT


def create_layout() -> html.Div:
    """Create the main application layout."""
    return html.Div([
        # Professional Top Bar
        html.Div([
            dbc.Row([
                dbc.Col([
                    dbc.Button(
                        html.I(className="bi bi-gear-fill"),
                        id="settings-btn",
                        color="link",
                        className="text-white",
                        style={"display": "none", "marginLeft": "20px", "fontSize": "1.2rem"}
                    )
                ], width=3, className="d-flex align-items-center"),
                dbc.Col([
                    html.H2(
                        "CurrentView",
                        className="text-center mb-0",
                        id="app-title",
                        style={
                            "color": "white",
                            "fontWeight": "300",
                            "letterSpacing": "3px",
                            "fontSize": "1.8rem",
                        }
                    )
                ], width=6, className="d-flex align-items-center justify-content-center"),
                dbc.Col([
                    html.Div([
                        html.I(id="sun-icon", className="bi bi-sun-fill", style={"color": "#ffc107", "fontSize": "1.2rem"}),
                        dbc.Switch(
                            id="theme-toggle",
                            value=False,
                            className="mx-2",
                            style={"fontSize": "1.2rem"}
                        ),
                        html.I(id="moon-icon", className="bi bi-moon", style={"color": "#6c757d", "fontSize": "1.2rem"}),
                    ], className="d-flex align-items-center", style={"marginRight": "20px", "gap": "0"})
                ], width=3, className="d-flex align-items-center justify-content-end"),
            ], className="align-items-center", style={"height": "48px", "margin": "0"}),
        ], id="top-bar", style={
            "position": "fixed",
            "top": 0,
            "left": 0,
            "right": 0,
            "backgroundColor": "#2c3e50",  # Dark blue-gray
            "boxShadow": "0 2px 4px rgba(0,0,0,.2)",
            "paddingTop": "12px",
            "paddingBottom": "12px",
            "zIndex": 1030  # High z-index to stay above other content
        }),
        
        # Spacer div to push content below fixed header
        html.Div(style={"height": "72px"}),  # 48px bar height + 12px top padding + 12px bottom padding
        
        # Settings Panel (Offcanvas)
        dbc.Offcanvas(
            [
                html.H4("Plot Settings", className="mb-4"),
                html.Hr(),
                dbc.Tabs([
                    dbc.Tab(
                        create_plot_style_settings("signals"),
                        label="Signals Plot",
                        tab_id="signals-settings-tab"
                    ),
                    dbc.Tab(
                        create_plot_style_settings("stats"),
                        label="Statistics Plot",
                        tab_id="stats-settings-tab"
                    ),
                ], id="settings-tabs", active_tab="signals-settings-tab"),
            ],
            id="settings-panel",
            is_open=False,
            placement="start",  # Slides from left
            backdrop=True,
            style={"width": "500px"}  # Wider for more settings
        ),
        
        # Main Container with all existing content
        dbc.Container([
            # Stores
            dcc.Store(id='session-id', data=str(uuid.uuid4())),
            dcc.Store(id='stats-store', data=[]),
            dcc.Store(id='files-store', data={}),
            dcc.Store(id='conditions-metadata', data={}),  # Store condition styling metadata
            dcc.Store(id='plot-trigger', data=0),  # Trigger for plot updates
            dcc.Store(id='theme-store', data='light'),  # Store for theme state
            
            # Custom CSS for dark mode
            html.Div(id="theme-styles", style={"display": "none"}),
            
            # File browser modals
            create_file_browser_modal(
                "bam-modal", 
                "Select BAM File", 
                file_extension=".bam", 
                default=DEFAULT_BAM_PATH
            ),
            create_file_browser_modal(
                "pod5-modal", 
                "Select POD5 File", 
                allow_dir=True, 
                file_extension=None,
                default=DEFAULT_POD5_PATH
            ),
            
            # Initialization Card (removed the old header since we have the top bar now)
            create_initialization_card(),
            
            # Main Interface (hidden initially)
            html.Div([
                # Add Condition Card
                create_add_condition_card(),
                
                # Conditions List
                dbc.Card([
                    dbc.CardHeader("Conditions"),
                    dbc.CardBody(id="conditions")
                ], className="mb-4"),
                
                # Visualization
                dbc.Card([
                    dbc.CardHeader([
                        dbc.Tabs([
                            dbc.Tab(label="Signals", tab_id="signals"),
                            dbc.Tab(label="Statistics", tab_id="stats", disabled=True, id="stats-tab"),
                        ], id="tabs", active_tab="signals"),
                    ]),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                dbc.Button("Refresh Plot", id="generate", color="secondary", size="sm"),
                            ], width="auto"),
                            dbc.Col([
                                dbc.Button("Clear Cache", id="clear-cache", color="warning", size="sm", outline=True),
                            ], width="auto"),
                        ], className="mb-3"),
                        html.Div(
                            id="plot-container", 
                            className="d-flex justify-content-center"
                        ),
                    ])
                ])
            ], id="main", style={"display": "none"}),
            
            # Alert for notifications
            dbc.Alert(id="alert", is_open=False, duration=4000),
        ], fluid=True)
    ], id="theme-container", style={"minHeight": "100vh", "backgroundColor": "#f8f9fa"})