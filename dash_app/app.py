import dash
import dash_bootstrap_components as dbc

from .layout.main_layout import create_layout
from .callbacks.file_browser import register_file_browser_callbacks, register_file_saver_callbacks
from .callbacks.initialization import register_initialization_callbacks
from .callbacks.conditions import register_condition_callbacks
from .callbacks.visualization import register_visualization_callbacks
from .callbacks.plot_settings import register_plot_settings_callbacks
from .callbacks.theme import register_theme_callbacks
from .callbacks.ui_interactions import register_ui_callbacks
from .utils.visualizer_extensions import apply_plot_style_extensions


def create_app() -> dash.Dash:
    """Create and configure the Dash application."""
    
    # Apply visualizer extensions
    apply_plot_style_extensions()
    
    # Initialize Dash app with Bootstrap theme
    app = dash.Dash(
        __name__, 
        external_stylesheets=[
            dbc.themes.BOOTSTRAP,
            "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css"  # For icons
        ],
        suppress_callback_exceptions=True  # Needed for dynamic callbacks
    )
    
    # Set the layout
    app.layout = create_layout()
    
    # Register all callbacks
    register_file_browser_callbacks()
    register_file_saver_callbacks()
    register_initialization_callbacks()
    register_condition_callbacks()
    register_visualization_callbacks()
    register_plot_settings_callbacks()
    register_theme_callbacks(app)  # Pass app for clientside callback
    register_ui_callbacks()
    
    return app