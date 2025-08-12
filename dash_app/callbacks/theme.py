from dash import Input, Output, State, callback, no_update
from .initialization import get_visualizer

def register_theme_callbacks(app):
    """Register theme-related callbacks."""
    
    # Theme toggle callback

    @callback(
        Output('theme-store', 'data'),
        Input('theme-toggle', 'value'),
        prevent_initial_call=True
    )
    def toggle_theme(toggle_value):
        return 'dark' if toggle_value else 'light'
    
    # Import theme styles
    from ..styles.theme_styles import get_theme_clientside_callback
    
    # Register clientside callback for theme application
    app.clientside_callback(
        get_theme_clientside_callback(),
        Output('theme-styles', 'children'),
        Input('theme-store', 'data')
    )