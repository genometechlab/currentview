# dash_app/callbacks/initialization.py
"""Initialization related callbacks."""

from dash import Input, Output, State, callback, ctx, html, ALL
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

from currentview import GenomicPositionVisualizer, PlotStyle
from ..utils.validators import validate_window_size, validate_json_string, validate_kmer_labels


# Global storage for visualizers
visualizers = {}


def register_initialization_callbacks():
    """Register all initialization related callbacks."""
    
    @callback(
        [Output("advanced", "is_open"), 
         Output("toggle-adv", "children")],
        Input("toggle-adv", "n_clicks"),
        State("advanced", "is_open"),
        prevent_initial_call=True
    )
    def toggle_advanced(n_clicks, is_open):
        """Toggle advanced options visibility."""
        is_open = not is_open
        return is_open, "Advanced ▲" if is_open else "Advanced ▼"
    
    @callback(
        Output("window-size", "invalid"),
        Input("window-size", "value")
    )
    def validate_window(value):
        """Validate window size input."""
        return validate_window_size(value)
    
    @callback(
        [Output("stats-store", "data"), 
         Output("stats-list", "children")],
        [Input("add-stat", "n_clicks"),
         Input({"type": "rm-stat", "stat": ALL}, "n_clicks")],
        [State("stat-select", "value"), 
         State("stats-store", "data")],
        prevent_initial_call=True
    )
    def manage_stats(add_click, remove_clicks, selected, stats):
        """Manage statistics selection."""
        trigger = ctx.triggered_id
        
        if trigger == "add-stat" and selected and selected not in stats:
            stats.append(selected)
        elif isinstance(trigger, dict) and trigger["type"] == "rm-stat":
            stats = [s for s in stats if s != trigger["stat"]]
        
        badges = [
            dbc.Badge([
                stat, 
                dbc.Button(
                    "×", 
                    id={"type": "rm-stat", "stat": stat}, 
                    size="sm", 
                    className="ms-1 p-0 text-white"
                )
            ], className="me-1") 
            for stat in stats
        ] or [html.Small("No statistics selected", className="text-muted")]
        
        return stats, badges
    
    @callback(
        [Output("main", "style"), 
         Output("init-card", "style"),
         Output("alert", "children"), 
         Output("alert", "is_open"),
         Output("stats-tab", "disabled")],
        Input("init-btn", "n_clicks"),
        [State("window-size", "value"), 
         State("kmer-labels", "value"),
         State("stats-store", "data"), 
         State("custom-title", "value"),
         State("verbosity", "value"), 
         State("style-options", "value"),
         State("custom-style", "value"), 
         State("session-id", "data")],
        prevent_initial_call=True
    )
    def initialize(n_clicks, k, kmer_text, stats, title, verbosity, 
                   style_opts, custom_style, session_id):
        """Initialize the visualizer with provided parameters."""
        
        # Validate window size
        if not k or k % 2 == 0:
            return (
                {"display": "none"}, 
                {}, 
                "Window size must be odd!", 
                True, 
                True
            )
        
        # Initialize parameters
        params = {
            'K': k, 
            'verbosity': int(verbosity)
        }
        
        # Validate and add k-mer labels
        if kmer_text:
            is_valid, kmers, error_msg = validate_kmer_labels(kmer_text, k)
            if not is_valid:
                return {"display": "none"}, {}, error_msg, True, True
            params['kmer'] = kmers
        
        # Add statistics if selected
        if stats:
            params['stats'] = stats
        
        # Add custom title
        if title:
            params['title'] = title
        
        # Validate and add custom style
        if custom_style:
            is_valid, style_data, error_msg = validate_json_string(custom_style)
            if not is_valid:
                return {"display": "none"}, {}, error_msg, True, True
            params['signals_plot_style'] = style_data
        
        # Configure plot style based on options
        if "dark" in style_opts:
            plot_style = PlotStyle.get_style('interactive_dark')
        else:
            plot_style = PlotStyle.get_style('interactive')
        
        plot_style.show_grid = 'grid' in style_opts
        plot_style.show_legend = 'legend' in style_opts
        plot_style.renderer = "WebGL" if "WebGL" in style_opts else "SVG"
        
        params['signals_plot_style'] = plot_style
        params['stats_plot_style'] = plot_style
        
        # Create visualizer instance
        viz = GenomicPositionVisualizer(**params)
        visualizers[session_id] = viz
        
        # Construct success message
        msg = f"Initialized with K={k}"
        if stats:
            msg += f", stats={stats}"
        
        return (
            {"display": "block"}, 
            {"display": "none"}, 
            msg, 
            True, 
            len(stats) == 0
        )


def get_visualizer(session_id: str) -> GenomicPositionVisualizer:
    """Get visualizer instance for a session."""
    return visualizers.get(session_id)