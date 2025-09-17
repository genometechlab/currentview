from dash import Input, Output, State, callback, dcc, html, ctx, no_update
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

from .initialization import get_visualizer
from ..config import DEFAULT_PLOT_HEIGHT


def register_visualization_callbacks():
    """Register all visualization related callbacks."""

    @callback(
        Output("plot-container", "children"),
        [
            Input("generate", "n_clicks"),
            Input("plot-trigger", "data"),
            Input("tabs", "active_tab"),
        ],
        State("session-id", "data"),
        prevent_initial_call=True,
    )
    def generate_plot(n_clicks, trigger, active_tab, session_id):
        """Generate plot based on various triggers."""
        viz = get_visualizer(session_id)
        if not viz:
            # Return error message instead of empty plot
            return dbc.Alert(
                "Please initialize visualizer first",
                color="warning",
                className="text-center",
            )

        # Check if there are any conditions
        if viz.n_conditions == 0:
            return dbc.Alert(
                "Please add at least one condition to visualize",
                color="info",
                className="text-center",
            )

        try:
            # Generate appropriate plot based on active tab
            if active_tab == "signals":
                fig = viz.get_signals_fig()
            else:
                fig = viz.get_stats_fig()

            # Return the graph component wrapped in loading
            return dcc.Loading(
                dcc.Graph(id="plot", figure=fig, style={"height": DEFAULT_PLOT_HEIGHT})
            )
        except ValueError as e:
            # Handle specific ValueError which might be the "not in list" error
            error_msg = str(e)
            if "is not in list" in error_msg:
                # Try to recover by clearing cache and regenerating
                try:
                    if hasattr(viz, "_signal_viz"):
                        delattr(viz, "_signal_viz")
                    if hasattr(viz, "_stats_viz"):
                        delattr(viz, "_stats_viz")

                    # Try again after clearing cache
                    if active_tab == "signals":
                        viz._ensure_signal_viz()
                        fig = viz._signal_viz.fig
                    else:
                        viz._ensure_stats_viz()
                        fig = viz._stats_viz.fig

                    return dcc.Loading(
                        dcc.Graph(
                            id="plot", figure=fig, style={"height": DEFAULT_PLOT_HEIGHT}
                        )
                    )
                except Exception:
                    # If recovery fails, show error message
                    return dbc.Alert(
                        [
                            html.H5("Synchronization Error", className="alert-heading"),
                            html.P("The plot data is out of sync with the conditions."),
                            html.Hr(),
                            html.P("Try these solutions:", className="mb-1"),
                            html.Ul(
                                [
                                    html.Li("Click 'Clear Cache' then 'Refresh Plot'"),
                                    html.Li(
                                        "Remove and re-add the problematic condition"
                                    ),
                                    html.Li(
                                        "Reinitialize the visualizer if the problem persists"
                                    ),
                                ]
                            ),
                            html.P(
                                f"Technical details: {error_msg}",
                                className="mb-0 small text-muted",
                            ),
                        ],
                        color="danger",
                    )
            else:
                return dbc.Alert(
                    f"Error generating plot: {error_msg}",
                    color="danger",
                    className="text-center",
                )
        except Exception as e:
            return dbc.Alert(
                f"Error generating plot: {str(e)}",
                color="danger",
                className="text-center",
            )

    @callback(
        [
            Output("alert", "children", allow_duplicate=True),
            Output("alert", "is_open", allow_duplicate=True),
            Output("plot-trigger", "data", allow_duplicate=True),
        ],
        Input("clear-cache", "n_clicks"),
        [State("session-id", "data"), State("plot-trigger", "data")],
        prevent_initial_call=True,
    )
    def clear_cache(n_clicks, session_id, trigger):
        """Clear cached visualizations and trigger plot refresh."""
        if not n_clicks:
            raise PreventUpdate

        viz = get_visualizer(session_id)
        if not viz:
            return "No visualizer to clear", True, no_update

        # Clear all cached visualizations
        cleared = []
        if hasattr(viz, "_signal_viz") and viz._signal_viz is not None:
            viz._signal_viz = None
            cleared.append("signals")
        if hasattr(viz, "_stats_viz") and viz._stats_viz is not None:
            viz._stats_viz = None
            cleared.append("stats")
        viz._mark_for_update()

        if cleared:
            # Trigger plot update after clearing
            return f"Cleared cache for: {', '.join(cleared)}", True, trigger + 1
        else:
            return "No cache to clear", True, no_update

    @callback(
        [
            Output("alert", "children", allow_duplicate=True),
            Output("alert", "is_open", allow_duplicate=True),
        ],
        [Input("export-modal-save", "n_clicks")],
        [
            State("session-id", "data"),
            State("tabs", "active_tab"),
            State("export-modal-input-path", "value"),
            State("export-modal-format", "value"),
        ],
        prevent_initial_call=True,
    )
    def export_plot(n_clicks, session_id, active_tab, created, format):
        """Export the plot as an HTML file"""
        if not n_clicks:
            raise PreventUpdate

        viz = get_visualizer(session_id)
        if not viz:
            return "No visualizer to clear", True

        # Check if there are any conditions
        if viz.n_conditions == 0:
            return f"No {active_tab} plot is currently available", True

        from pathlib import Path

        path = created
        path = Path(path).resolve()
        if not path.suffix == format:
            return f"File extension must be {format}", True

        if active_tab == "signals":
            viz.save_signals(path=path, format=format)
            return f"Signals plot exported to {path}", True
        elif active_tab == "stats":
            viz.save_stats(path=path, format=format)
            return f"Statistics plot exported to {path}", True
        else:
            return f"Invalid plot to export", True
