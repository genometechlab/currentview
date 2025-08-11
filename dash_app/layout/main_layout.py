import uuid
import dash_bootstrap_components as dbc
from dash import dcc, html

from .components import (
    create_initialization_card,
    create_add_condition_card,
)
from .modals import create_file_browser_modal
from ..config import DEFAULT_BAM_PATH, DEFAULT_POD5_PATH, DEFAULT_PLOT_HEIGHT


def create_layout() -> dbc.Container:
    """Create the main application layout."""
    return dbc.Container([
        # Stores
        dcc.Store(id='session-id', data=str(uuid.uuid4())),
        dcc.Store(id='stats-store', data=[]),
        dcc.Store(id='files-store', data={}),
        dcc.Store(id='conditions-metadata', data={}),  # Store condition styling metadata
        dcc.Store(id='plot-trigger', data=0),  # Trigger for plot updates
        
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
        
        # Header
        html.H1("Nanopore Signal Visualizer", className="text-center mb-4"),
        
        # Initialization Card
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
                    dbc.Button("Generate Plot", id="generate", color="primary", className="mb-3"),
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