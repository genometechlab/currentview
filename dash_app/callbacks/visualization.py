# dash_app/callbacks/visualization.py
"""Visualization related callbacks."""

from dash import Input, Output, State, callback, dcc, html
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

from .initialization import get_visualizer
from ..config import DEFAULT_PLOT_HEIGHT


def register_visualization_callbacks():
    """Register all visualization related callbacks."""
    
    @callback(
        Output("plot-container", "children"),
        [Input("generate", "n_clicks"),
         Input("plot-trigger", "data"),
         Input("tabs", "active_tab")],
        State("session-id", "data"),
        prevent_initial_call=True
    )
    def generate_plot(n_clicks, trigger, active_tab, session_id):
        """Generate plot based on various triggers."""
        # Get visualizer instance
        viz = get_visualizer(session_id)
        if not viz:
            # Return error message instead of empty plot
            return dbc.Alert(
                "Please initialize visualizer first", 
                color="warning",
                className="text-center"
            )
        
        # Check if there are any conditions
        if viz.n_conditions==0:
            return dbc.Alert(
                "Please add at least one condition to visualize", 
                color="info",
                className="text-center"
            )
        
        try:
            # Generate appropriate plot based on active tab
            if active_tab == "signals":
                viz._ensure_signal_viz()
                fig = viz._signal_viz.fig
            else:
                viz._ensure_stats_viz()
                fig = viz._stats_viz.fig
            
            # Return the graph component wrapped in loading
            return dcc.Loading(
                dcc.Graph(
                    id="plot", 
                    figure=fig,
                    style={"height": DEFAULT_PLOT_HEIGHT}
                )
            )
        except Exception as e:
            return dbc.Alert(
                f"Error generating plot: {str(e)}", 
                color="danger",
                className="text-center"
            )