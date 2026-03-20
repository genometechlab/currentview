from pathlib import Path

import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, dcc, html, no_update
from dash.exceptions import PreventUpdate

from ..config import DEFAULT_PLOT_HEIGHT
from .initialization import get_visualizer


# ── Alert helpers ─────────────────────────────────────────────────────────────


def _info_alert(msg: str) -> dbc.Alert:
    return dbc.Alert(msg, color="info", className="text-center")


def _warn_alert(msg: str) -> dbc.Alert:
    return dbc.Alert(msg, color="warning", className="text-center")


def _error_alert(msg: str) -> dbc.Alert:
    return dbc.Alert(msg, color="danger", className="text-center")


def _sync_error_alert(error_msg: str) -> dbc.Alert:
    return dbc.Alert(
        [
            html.H5("Synchronization Error", className="alert-heading"),
            html.P("The plot data is out of sync with the conditions."),
            html.Hr(),
            html.P("Try these solutions:", className="mb-1"),
            html.Ul(
                [
                    html.Li("Click 'Clear Cache' then 'Refresh Plot'"),
                    html.Li("Remove and re-add the problematic condition"),
                    html.Li("Reinitialize the visualizer if the problem persists"),
                ]
            ),
            html.P(
                f"Technical details: {error_msg}", className="mb-0 small text-muted"
            ),
        ],
        color="danger",
    )


# ── Tab dispatch maps ─────────────────────────────────────────────────────────

# Tabs that produce a plot — maps tab_id → visualizer method name
_PLOT_TABS = {
    "signals": "get_signals_fig",
    "stats": "get_stats_fig",
}

# Tabs that show instructions instead of a plot
_INSTRUCTION_TABS = {
    "gmm": "Configure GMM parameters above and click 'Run GMM' to generate plot",
    "umap": "Configure UMAP parameters above and click 'Run UMAP' to generate plot",
}


# ── Callbacks ─────────────────────────────────────────────────────────────────


def register_visualization_callbacks():

    @callback(
        Output("plot-container", "children"),
        Input("generate", "n_clicks"),
        Input("plot-trigger", "data"),
        Input("tabs", "active_tab"),
        State("session-id", "data"),
        prevent_initial_call=True,
    )
    def generate_plot(n_clicks, trigger, active_tab, session_id):
        viz = get_visualizer(session_id)
        if not viz:
            return _warn_alert("Please initialize the visualizer first")
        if viz.n_conditions == 0:
            return _info_alert("Please add at least one condition to visualize")

        # Instruction-only tabs (GMM, UMAP)
        if active_tab in _INSTRUCTION_TABS:
            return _info_alert(_INSTRUCTION_TABS[active_tab])

        # Unknown tab
        if active_tab not in _PLOT_TABS:
            return _error_alert(f"Unknown tab: {active_tab}")

        # Generate plot
        plot_fn = getattr(viz, _PLOT_TABS[active_tab])
        try:
            fig = plot_fn()
        except ValueError as e:
            error_msg = str(e)
            if "is not in list" not in error_msg:
                return _error_alert(f"Error generating plot: {error_msg}")
            # Sync error — clear cache and retry once
            try:
                viz.clear_cache()
                fig = plot_fn()
            except Exception:
                return _sync_error_alert(error_msg)
        except Exception as e:
            return _error_alert(f"Error generating plot: {e}")

        return dcc.Graph(id="plot", figure=fig, style={"height": DEFAULT_PLOT_HEIGHT})

    @callback(
        Output("alert", "children", allow_duplicate=True),
        Output("alert", "is_open", allow_duplicate=True),
        Output("plot-trigger", "data", allow_duplicate=True),
        Input("clear-cache", "n_clicks"),
        State("session-id", "data"),
        State("plot-trigger", "data"),
        prevent_initial_call=True,
    )
    def clear_cache(n_clicks, session_id, trigger):
        if not n_clicks:
            raise PreventUpdate

        viz = get_visualizer(session_id)
        if not viz:
            return "No visualizer found", True, no_update

        cleared = viz.clear_cache()  # expected to return list of cleared cache names

        if cleared:
            return f"Cleared cache for: {', '.join(cleared)}", True, trigger + 1
        return "No cache to clear", True, no_update

    @callback(
        Output("alert", "children", allow_duplicate=True),
        Output("alert", "is_open", allow_duplicate=True),
        Input("export-modal-save", "n_clicks"),
        State("session-id", "data"),
        State("tabs", "active_tab"),
        State("export-modal-input-path", "value"),
        State("export-modal-format", "value"),
        prevent_initial_call=True,
    )
    def export_plot(n_clicks, session_id, active_tab, path_str, fmt):
        if not n_clicks:
            raise PreventUpdate

        viz = get_visualizer(session_id)
        if not viz:
            return "No visualizer found", True
        if viz.n_conditions == 0:
            return f"No {active_tab} plot is currently available", True

        path = Path(path_str).resolve()
        # Normalise both sides so ".html" == ".html" regardless of case/dot presence
        if path.suffix.lower() != f".{fmt.lstrip('.').lower()}":
            return f"File extension must be {fmt}", True

        fmt = fmt.lstrip(".").lower()

        _EXPORT = {
            "signals": (viz.save_signals, "Signals"),
            "stats": (viz.save_stats, "Statistics"),
        }

        if active_tab not in _EXPORT:
            return f"Cannot export '{active_tab}' tab", True

        save_fn, label = _EXPORT[active_tab]
        try:
            save_fn(path=path, format=fmt)
        except Exception as e:
            return f"Export failed: {e}", True

        return f"{label} plot exported to {path}", True
