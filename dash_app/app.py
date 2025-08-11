# dash_app/app.py
"""Dash application initialization and callback registration."""

import dash
import dash_bootstrap_components as dbc

from .layout.main_layout import create_layout
from .callbacks.file_browser import register_file_browser_callbacks
from .callbacks.initialization import register_initialization_callbacks
from .callbacks.conditions import register_condition_callbacks
from .callbacks.visualization import register_visualization_callbacks


def create_app() -> dash.Dash:
    """Create and configure the Dash application."""
    
    # Initialize Dash app with Bootstrap theme
    app = dash.Dash(
        __name__, 
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        suppress_callback_exceptions=True  # Needed for dynamic callbacks
    )
    
    # Set the layout
    app.layout = create_layout()
    
    # Register all callbacks
    register_file_browser_callbacks()
    register_initialization_callbacks()
    register_condition_callbacks()
    register_visualization_callbacks()
    
    return app