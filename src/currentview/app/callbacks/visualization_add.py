from dash import Input, Output, State, callback, dcc, html, ctx, ALL, no_update
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

from .initialization import get_visualizer
from ..config import DEFAULT_PLOT_HEIGHT


# ── Shared helpers ────────────────────────────────────────────────────────────


def _warn_alert(msg: str) -> dbc.Alert:
    return dbc.Alert(msg, color="warning", className="text-center")


def _error_alert(msg: str) -> dbc.Alert:
    return dbc.Alert(msg, color="danger", className="text-center")


def _position_range_outputs(viz) -> tuple:
    """Compute slider min/max/value/marks from a visualizer instance."""
    if not viz:
        return -5, 5, [-5, 5], {-5: "-5", 0: "0", 5: "5"}

    half_k = viz.K // 2
    marks = {}
    if viz.K > 20:
        step = viz.K // 10
        for i in range(-half_k + step, half_k, step):
            marks[i] = str(i)

    return -half_k, half_k, [-half_k, half_k], marks


def _extract_stats_from_store(stats_store: list) -> list[str]:
    """Read selected stats from the umap-stats store."""
    return stats_store or []


def _stat_badge(stat: str) -> dbc.Badge:
    return dbc.Badge(
        [
            stat,
            dbc.Button(
                "×",
                id={"type": "rm-umap-stat", "stat": stat},
                size="sm",
                className="ms-1 p-0 text-white",
                style={"border": "none", "background": "transparent"},
            ),
        ],
        color="primary",
        className="me-2 mb-2",
        style={"fontSize": "0.9rem", "padding": "0.5rem"},
    )


# ── Callbacks ─────────────────────────────────────────────────────────────────


def register_visualization_add_callbacks():

    # ── Shared: position range slider ─────────────────────────────────────────

    for slider_id in ("gmm-position-range", "umap-position-range"):

        @callback(
            Output(slider_id, "min"),
            Output(slider_id, "max"),
            Output(slider_id, "value"),
            Output(slider_id, "marks"),
            Input("session-id", "data"),
            Input("init-btn", "n_clicks"),
            State("session-id", "data"),
            prevent_initial_call=True,
        )
        def update_position_range(_session_trigger, _init_clicks, session_id):
            return _position_range_outputs(get_visualizer(session_id))

    # ── GMM ───────────────────────────────────────────────────────────────────

    @callback(
        Output("gmm-stat1", "options"),
        Output("gmm-stat2", "options"),
        Input("stats-store", "data"),
    )
    def update_gmm_stat_options(stored_stats):
        opts = stored_stats or []
        return opts, opts

    @callback(
        Output("plot-container", "children", allow_duplicate=True),
        Input("gmm-run-btn", "n_clicks"),
        State("session-id", "data"),
        State("gmm-stat1", "value"),
        State("gmm-stat2", "value"),
        State("gmm-covariance-type", "value"),
        State("gmm-position-range", "value"),
        prevent_initial_call=True,
    )
    def generate_gmm_plot(
        n_clicks, session_id, stat1, stat2, covariance_type, position_range
    ):
        viz = get_visualizer(session_id)
        if not viz:
            return _warn_alert("Please initialize the visualizer first")
        if not stat1 or not stat2:
            return _warn_alert("Please select both Stat 1 and Stat 2")

        try:
            start_pos, end_pos = position_range
            gmm_handler = viz.fit_gmms(
                stat1=stat1,
                stat2=stat2,
                offsets_window=(start_pos, end_pos),
                covariance_type=covariance_type,
            )
            fig = gmm_handler.visualize().get_fig()
            return dcc.Graph(
                id="plot", figure=fig, style={"height": DEFAULT_PLOT_HEIGHT}
            )
        except ValueError as e:
            return _error_alert(f"Invalid parameter values: {e}")
        except Exception as e:
            return _error_alert(f"Error generating GMM plot: {e}")

    # ── UMAP ──────────────────────────────────────────────────────────────────

    @callback(
        Output("umap-stats-select", "options"),
        Input("stats-store", "data"),
    )
    def update_umap_stats_options(stored_stats):
        return stored_stats or []

    @callback(
        Output("umap-stats-store", "data"),
        Output("umap-stats-list", "children"),
        Input("select-umap-stat", "n_clicks"),
        Input({"type": "rm-umap-stat", "stat": ALL}, "n_clicks"),
        State("umap-stats-select", "value"),
        State("umap-stats-store", "data"),
        prevent_initial_call=True,
    )
    def manage_umap_stats(add_click, remove_clicks, selected, current_stats):
        current_stats = current_stats or []
        trigger = ctx.triggered_id

        if trigger == "select-umap-stat":
            if selected and selected not in current_stats:
                current_stats = current_stats + [selected]
        elif isinstance(trigger, dict) and trigger.get("type") == "rm-umap-stat":
            current_stats = [s for s in current_stats if s != trigger["stat"]]

        badges = [_stat_badge(s) for s in current_stats] or [
            html.Small("No statistics selected", className="text-muted")
        ]
        return current_stats, badges

    @callback(
        Output("plot-container", "children", allow_duplicate=True),
        Input("umap-run-btn", "n_clicks"),
        State("session-id", "data"),
        State("umap-n-neighbors", "value"),
        State("umap-min-dist", "value"),
        State("umap-stats-store", "data"),
        State("umap-position-range", "value"),
        prevent_initial_call=True,
    )
    def generate_umap_plot(
        n_clicks, session_id, n_neighbors, min_dist, selected_stats, position_range
    ):
        viz = get_visualizer(session_id)
        if not viz:
            return _warn_alert("Please initialize the visualizer first")

        selected_stats = selected_stats or []
        if not selected_stats:
            return _warn_alert(
                "Please select at least one statistic for UMAP visualization"
            )
        if n_neighbors is None or n_neighbors < 2:
            return _warn_alert("Please provide a valid number of neighbors (minimum 2)")
        if min_dist is None or not (0 <= min_dist <= 1):
            return _warn_alert("Please provide a valid min distance (between 0 and 1)")
        if not position_range or len(position_range) != 2:
            return _warn_alert("Please select a valid position range")

        try:
            start_pos, end_pos = position_range
            umap_handler = viz.fit_umap(
                stats=selected_stats,
                offsets_window=(start_pos, end_pos),
                n_neighbors=int(n_neighbors),
                min_dist=float(min_dist),
            )
            fig = umap_handler.visualize().get_fig()
            return dcc.Graph(
                id="plot", figure=fig, style={"height": DEFAULT_PLOT_HEIGHT}
            )
        except ValueError as e:
            return _error_alert(f"Invalid parameter values: {e}")
        except Exception as e:
            return _error_alert(f"Error generating UMAP plot: {e}")
