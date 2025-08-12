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
# Assuming you'll add this import:
from ..utils import create_card, create_button


def create_layout() -> html.Div:
    """Create the main application layout."""
    return html.Div([
        # Modern Top Bar with glass effect
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
                            "textShadow": "2px 2px 4px rgba(0,0,0,0.3)"
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
            "background": "linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)",  # Modern gradient
            "backdropFilter": "blur(10px)",
            "boxShadow": "0 4px 6px rgba(0,0,0,.3)",
            "paddingTop": "12px",
            "paddingBottom": "12px",
            "zIndex": 1030
        }),
        
        # Spacer div to push content below fixed header
        html.Div(style={"height": "72px"}),
        
        # Settings Panel (Offcanvas) with modern styling
        dbc.Offcanvas(
            [
                html.H4("Plot Settings", className="mb-4", style={"fontWeight": "600"}),
                html.Hr(style={"opacity": "0.1"}),
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
                ], id="settings-tabs", active_tab="signals-settings-tab", className="nav-pills"),
            ],
            id="settings-panel",
            is_open=False,
            placement="start",
            backdrop=True,
            style={
                "width": "500px",
                "background": "rgba(255, 255, 255, 0.95)",
                "backdropFilter": "blur(20px)"
            }
        ),
        
        # Main Container with all existing content
        dbc.Container([
            # Stores
            dcc.Store(id='session-id', data=str(uuid.uuid4())),
            dcc.Store(id='stats-store', data=[]),
            dcc.Store(id='files-store', data={}),
            dcc.Store(id='conditions-metadata', data={}),
            dcc.Store(id='plot-trigger', data=0),
            dcc.Store(id='theme-store', data='light'),
            
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
            
            # Initialization Card
            create_initialization_card(),
            
            # Main Interface (hidden initially)
            html.Div([
                # Add Condition Card
                create_add_condition_card(),
                
                # Conditions List
                create_card([
                    html.H4([
                        html.I(className="bi bi-list-check me-2"),
                        "Conditions"
                    ], className="mb-3", style={"fontWeight": "600", "color": "#2d3748"}),
                    html.Hr(style={"opacity": "0.1"}),
                    html.Div(id="conditions")
                ], className="mb-4"),
                
                # Visualization
                create_card([
                    dbc.Tabs([
                        dbc.Tab(
                            label="Signals",
                            tab_id="signals",
                            tab_style={"borderRadius": "8px 8px 0 0"},
                            active_tab_style={
                                "borderRadius": "8px 8px 0 0",
                                "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                                "color": "white"
                            }
                        ),
                        dbc.Tab(
                            label="Statistics",
                            tab_id="stats",
                            disabled=True,
                            id="stats-tab",
                            tab_style={"borderRadius": "8px 8px 0 0"},
                            active_tab_style={
                                "borderRadius": "8px 8px 0 0",
                                "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                                "color": "white"
                            }
                        ),
                    ], id="tabs", active_tab="signals", className="nav-pills mb-3"),
                    
                    html.Hr(style={"opacity": "0.1"}),
                    
                    dbc.Row([
                        dbc.Col([
                            create_button(
                                "Refresh Plot",
                                id="generate",
                                color="secondary",
                                size="sm",
                                icon="bi bi-arrow-clockwise"
                            ),
                        ], width="auto"),
                        dbc.Col([
                            create_button(
                                "Clear Cache",
                                id="clear-cache",
                                color="secondary",
                                size="sm",
                                icon="bi bi-trash"
                            ),
                        ], width="auto"),
                    ], className="mb-3"),
                    
                    html.Div(
                        id="plot-container", 
                        className="d-flex justify-content-center",
                    ),
                ])
            ], id="main", style={"display": "none"}),
            
            # Alert for notifications
            dbc.Alert(
                id="alert",
                is_open=False,
                duration=4000,
                style={
                    "borderRadius": "12px",
                    "border": "none",
                    "boxShadow": "0 4px 6px rgba(0, 0, 0, 0.1)"
                }
            ),
        ], fluid=True, style={"padding": "2rem", "maxWidth": "1400px"})
    ], id="theme-container", style={
        "minHeight": "100vh",
        "background": "linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)",
        "backgroundAttachment": "fixed"
    })