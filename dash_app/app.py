# dash_app/app.py
"""Dash application initialization and callback registration."""

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, html

from .layout.main_layout import create_layout
from .callbacks.file_browser import register_file_browser_callbacks
from .callbacks.initialization import register_initialization_callbacks
from .callbacks.conditions import register_condition_callbacks
from .callbacks.visualization import register_visualization_callbacks
from .callbacks.plot_settings import register_plot_settings_callbacks
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
    register_initialization_callbacks()
    register_condition_callbacks()
    register_visualization_callbacks()
    register_plot_settings_callbacks()
    
    # Theme toggle callback
    @callback(
        Output('theme-store', 'data'),
        Input('theme-toggle', 'value'),
        prevent_initial_call=True
    )
    def toggle_theme(toggle_value):
        """Toggle between light and dark themes."""
        if toggle_value:
            return 'dark'
        return 'light'
    
    # Settings panel toggle callback
    @callback(
        Output("settings-panel", "is_open"),
        Input("settings-btn", "n_clicks"),
        State("settings-panel", "is_open"),
        prevent_initial_call=True
    )
    def toggle_settings(n_clicks, is_open):
        """Toggle the settings panel."""
        return not is_open
    
    # Clientside callback for theme application and icon updates
    app.clientside_callback(
        """
        function(theme) {
            // Remove existing theme style if any
            const existingStyle = document.getElementById('dash-theme-styles');
            if (existingStyle) {
                existingStyle.remove();
            }
            
            // Update icon classes
            const sunIcon = document.getElementById('sun-icon');
            const moonIcon = document.getElementById('moon-icon');
            
            if (theme === 'dark') {
                // Dark mode: empty sun, filled moon
                if (sunIcon) sunIcon.className = 'bi bi-sun';
                if (moonIcon) moonIcon.className = 'bi bi-moon-fill';
                
                // Create and inject dark theme styles
                const style = document.createElement('style');
                style.id = 'dash-theme-styles';
                style.innerHTML = `
                    #theme-container {
                        background-color: #1a1a1a !important;
                        color: #ffffff !important;
                    }
                    #top-bar {
                        background-color: #0d0d0d !important;
                        border-bottom: 1px solid #333 !important;
                    }
                    #app-title {
                        color: #ffffff !important;
                    }
                    .form-switch {
                        padding-left: 0 !important;
                        margin-bottom: 0 !important;
                    }
                    .form-switch .form-check-input {
                        width: 3em !important;
                        margin-left: 0 !important;
                        margin-right: 0 !important;
                        background-color: #6c757d !important;
                        border-color: #6c757d !important;
                        cursor: pointer !important;
                        float: none !important;
                    }
                    .form-switch .form-check-input:checked {
                        background-color: #0d6efd !important;
                        border-color: #0d6efd !important;
                    }
                    .card {
                        background-color: #2d2d2d !important;
                        color: #ffffff !important;
                        border-color: #444 !important;
                    }
                    .card-header {
                        background-color: #3d3d3d !important;
                        border-color: #444 !important;
                    }
                    .form-control, .form-select {
                        background-color: #2d2d2d !important;
                        color: #ffffff !important;
                        border-color: #444 !important;
                    }
                    .form-control:focus, .form-select:focus {
                        background-color: #2d2d2d !important;
                        color: #ffffff !important;
                        border-color: #0d6efd !important;
                    }
                    .form-control::placeholder {
                        color: #aaa !important;
                        opacity: 1 !important;
                    }
                    .form-control:disabled {
                        background-color: #1d1d1d !important;
                        color: #888 !important;
                    }
                    .modal-content {
                        background-color: #2d2d2d !important;
                        color: #ffffff !important;
                    }
                    .list-group-item {
                        background-color: #2d2d2d !important;
                        color: #ffffff !important;
                        border-color: #444 !important;
                    }
                    .list-group-item:hover {
                        background-color: #3d3d3d !important;
                    }
                    .list-group-item.active {
                        background-color: #0d6efd !important;
                        border-color: #0d6efd !important;
                    }
                    .alert {
                        background-color: #3d3d3d !important;
                        color: #ffffff !important;
                        border-color: #444 !important;
                    }
                    .nav-tabs .nav-link {
                        color: #aaa !important;
                    }
                    .nav-tabs .nav-link.active {
                        background-color: #2d2d2d !important;
                        color: #ffffff !important;
                        border-color: #444 #444 #2d2d2d !important;
                    }
                    .btn-secondary {
                        background-color: #3d3d3d !important;
                        border-color: #444 !important;
                    }
                    .btn-secondary:hover {
                        background-color: #4d4d4d !important;
                        border-color: #555 !important;
                    }
                    .btn-link {
                        color: #fff !important;
                    }
                    .btn-link:hover {
                        color: #ccc !important;
                    }
                    input[type="color"] {
                        background-color: #2d2d2d !important;
                        border-color: #444 !important;
                    }
                    textarea.form-control {
                        background-color: #2d2d2d !important;
                        color: #ffffff !important;
                        border-color: #444 !important;
                    }
                    textarea.form-control::placeholder {
                        color: #aaa !important;
                        opacity: 1 !important;
                    }
                    .input-group-text {
                        background-color: #3d3d3d !important;
                        color: #ffffff !important;
                        border-color: #444 !important;
                    }
                    .form-text {
                        color: #999 !important;
                    }
                    .offcanvas {
                        background-color: #2d2d2d !important;
                        color: #ffffff !important;
                    }
                    .offcanvas-header {
                        border-bottom: 1px solid #444 !important;
                    }
                    .offcanvas hr {
                        border-color: #444 !important;
                        opacity: 0.5 !important;
                    }
                    .nav-tabs .nav-item .nav-link {
                        color: #aaa !important;
                        background-color: transparent !important;
                        border-color: #444 !important;
                    }
                    .nav-tabs .nav-item .nav-link.active {
                        color: #fff !important;
                        background-color: #2d2d2d !important;
                        border-color: #444 #444 #2d2d2d !important;
                    }
                `;
                document.head.appendChild(style);
            } else {
                // Light mode: filled sun, empty moon
                if (sunIcon) sunIcon.className = 'bi bi-sun-fill';
                if (moonIcon) moonIcon.className = 'bi bi-moon';
                
                // Light mode styles for top bar
                const style = document.createElement('style');
                style.id = 'dash-theme-styles';
                style.innerHTML = `
                    #top-bar {
                        background-color: #2c3e50 !important;
                    }
                    #app-title {
                        color: #ffffff !important;
                    }
                    .form-switch {
                        padding-left: 0 !important;
                        margin-bottom: 0 !important;
                    }
                    .form-switch .form-check-input {
                        width: 3em !important;
                        margin-left: 0 !important;
                        margin-right: 0 !important;
                        cursor: pointer !important;
                        float: none !important;
                    }
                `;
                document.head.appendChild(style);
            }
            
            return '';  // Return empty string for the dummy output
        }
        """,
        Output('theme-styles', 'children'),
        Input('theme-store', 'data')
    )
    
    # Add condition collapse toggle
    @callback(
        [Output("add-condition-collapse", "is_open"),
         Output("add-condition-chevron", "className")],
        Input("toggle-add-condition", "n_clicks"),
        State("add-condition-collapse", "is_open"),
        prevent_initial_call=True
    )
    def toggle_add_condition(n_clicks, is_open):
        """Toggle the add condition card collapse state."""
        new_state = not is_open
        chevron_class = "bi bi-chevron-up" if new_state else "bi bi-chevron-down"
        return new_state, chevron_class
    
    return app