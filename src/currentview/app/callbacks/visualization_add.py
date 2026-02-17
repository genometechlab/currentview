from dash import Input, Output, State, callback, dcc, html, ctx, ALL, no_update
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

from .initialization import get_visualizer
from ..config import DEFAULT_PLOT_HEIGHT


def register_visualization_add_callbacks():
    """Register all visualization related callbacks."""

    @callback(
        [
            Output("gmm-position-range", "min"),
            Output("gmm-position-range", "max"),
            Output("gmm-position-range", "value"),
            Output("gmm-position-range", "marks"),
        ],
        Input("init-btn", "n_clicks"),
        State("session-id", "data"),
        prevent_initial_call=True,
    )
    def update_gmm_position_range(init_clicks, session_id):
        """Update GMM position range slider based on window size K."""
        viz = get_visualizer(session_id)

        if not viz:
            return -5, 5, [-5, 5], {-5: "-5", 0: "0", 5: "5"}

        K = viz.K
        half_k = K // 2

        marks = {}

        if K > 20:
            step = K // 10
            for i in range(-half_k + step, half_k, step):
                marks[i] = str(i)

        return -half_k, half_k, [-half_k, half_k], marks

    @callback(
        [
            Output("gmm-stat1", "options"),
            Output("gmm-stat2", "options"),
        ],
        Input("stats-store", "data"),
    )
    def update_gmm_stat_options(stored_stats):
        """Update GMM stat dropdowns based on stored statistics."""
        if not stored_stats:
            return [], []
        return stored_stats, stored_stats

    @callback(
        Output("plot-container", "children", allow_duplicate=True),
        Input("gmm-run-btn", "n_clicks"),
        [
            State("session-id", "data"),
            State("gmm-stat1", "value"),
            State("gmm-stat2", "value"),
            State("gmm-covariance-type", "value"),
            State("gmm-position-range", "value"),
        ],
        prevent_initial_call=True,
    )
    def generate_gmm_plot(
        n_clicks,
        session_id,
        stat1,
        stat2,
        covariance_type,
        position_range,
    ):
        """Generate GMM plot when Run GMM button is clicked."""
        viz = get_visualizer(session_id)
        if not viz:
            return dbc.Alert(
                "Please initialize visualizer first",
                color="warning",
                className="text-center",
            )

        # Validate stats
        if not stat1 or not stat2:
            return dbc.Alert(
                "Please select both Stat 1 and Stat 2",
                color="warning",
                className="text-center",
            )

        try:
            # Extract position range
            start_pos, end_pos = position_range

            # Fit UMAP with user-selected parameters
            gmm_handler = viz.fit_gmms(
                stat1=stat1,
                stat2=stat2,
                offsets_window=(start_pos, end_pos),
                covariance_type=covariance_type,
            )

            # Generate visualization
            fig = gmm_handler.visualize().get_fig()

            # Return the plot
            return dcc.Loading(
                dcc.Graph(id="plot", figure=fig, style={"height": DEFAULT_PLOT_HEIGHT})
            )

        except ValueError as e:
            return dbc.Alert(
                f"Invalid parameter values: {str(e)}",
                color="danger",
                className="text-center",
            )
        except Exception as e:
            return dbc.Alert(
                f"Error generating GMM plot: {str(e)}",
                color="danger",
                className="text-center",
            )

    # -------------------------------------
    # umap related callbacks
    # -------------------------------------

    @callback(
        [
            Output("umap-position-range", "min"),
            Output("umap-position-range", "max"),
            Output("umap-position-range", "value"),
            Output("umap-position-range", "marks"),
        ],
        [
            Input("session-id", "data"),
            Input("init-btn", "n_clicks"),  # Trigger when init button is clicked
        ],
        prevent_initial_call=True,
    )
    def update_umap_position_range(session_id, init_clicks):
        """Update UMAP position range slider based on window size K."""
        viz = get_visualizer(session_id)

        if not viz:
            # Default values if no visualizer
            return -5, 5, [-5, 5], {-5: "-5", 0: "0", 5: "5"}

        K = viz.K
        half_k = K // 2

        # Create marks at key positions
        marks = {}

        # Add intermediate marks for larger K values
        if K > 20:
            step = K // 10
            for i in range(-half_k + step, half_k, step):
                marks[i] = str(i)

        return -half_k, half_k, [-half_k, half_k], marks

    @callback(
        Output("umap-stats-select", "options"),
        Input("stats-store", "data"),
    )
    def update_umap_stats_options(stored_stats):
        """Update UMAP stats dropdown based on stored statistics."""
        if not stored_stats:
            return []
        return stored_stats

    @callback(
        Output("umap-stats-list", "children"),
        [
            Input("select-umap-stat", "n_clicks"),
            Input({"type": "rm-umap-stat", "stat": ALL}, "n_clicks"),
        ],
        [
            State("umap-stats-select", "value"),
            State("umap-stats-list", "children"),
        ],
        prevent_initial_call=True,
    )
    def manage_umap_stats(add_click, remove_clicks, selected, current_children):
        """Manage UMAP statistics selection."""
        trigger = ctx.triggered_id

        # Extract current stats from badges
        current_stats = []
        if current_children and isinstance(current_children, list):
            for badge in current_children:
                if isinstance(badge, dict) and badge.get("type") == "Badge":
                    # Extract stat from badge children
                    children = badge.get("props", {}).get("children", [])
                    if children and isinstance(children, list):
                        stat = children[0]
                        if isinstance(stat, str):
                            current_stats.append(stat)

        # Handle add stat
        if trigger == "select-umap-stat" and selected and selected not in current_stats:
            current_stats.append(selected)
        # Handle remove stat
        elif isinstance(trigger, dict) and trigger["type"] == "rm-umap-stat":
            current_stats = [s for s in current_stats if s != trigger["stat"]]

        # Create badges
        badges = [
            dbc.Badge(
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
            for stat in current_stats
        ] or [html.Small("No statistics selected", className="text-muted")]

        return badges

    @callback(
        Output("plot-container", "children", allow_duplicate=True),
        Input("umap-run-btn", "n_clicks"),
        [
            State("session-id", "data"),
            State("umap-n-neighbors", "value"),
            State("umap-min-dist", "value"),
            State("umap-stats-list", "children"),
            State("umap-position-range", "value"),
        ],
        prevent_initial_call=True,
    )
    def generate_umap_plot(
        n_clicks, session_id, n_neighbors, min_dist, stats_list, position_range
    ):
        """Generate UMAP plot when Run UMAP button is clicked."""
        viz = get_visualizer(session_id)
        if not viz:
            return dbc.Alert(
                "Please initialize visualizer first",
                color="warning",
                className="text-center",
            )

        # Extract selected stats from the badges
        selected_stats = []
        if stats_list and isinstance(stats_list, list):
            for badge in stats_list:
                if isinstance(badge, dict) and badge.get("type") == "Badge":
                    children = badge.get("props", {}).get("children", [])
                    if children and isinstance(children, list):
                        stat = children[0]
                        if isinstance(stat, str):
                            selected_stats.append(stat)

        # Validate that at least one stat is selected
        if not selected_stats:
            return dbc.Alert(
                "Please select at least one statistic for UMAP visualization",
                color="warning",
                className="text-center",
            )

        # Validate UMAP parameters
        if n_neighbors is None or n_neighbors < 2:
            return dbc.Alert(
                "Please provide a valid number of neighbors (minimum 2)",
                color="warning",
                className="text-center",
            )

        if min_dist is None or min_dist < 0 or min_dist > 1:
            return dbc.Alert(
                "Please provide a valid min distance (between 0 and 1)",
                color="warning",
                className="text-center",
            )

        # Validate position range
        if not position_range or len(position_range) != 2:
            return dbc.Alert(
                "Please select a valid position range",
                color="warning",
                className="text-center",
            )

        try:
            # Extract position range
            start_pos, end_pos = position_range

            # Fit UMAP with user-selected parameters
            umap_handler = viz.fit_umap(
                stats=selected_stats,
                offsets_window=(start_pos, end_pos),
                n_neighbors=int(n_neighbors),
                min_dist=float(min_dist),
            )

            # Generate visualization
            fig = umap_handler.visualize().get_fig()

            # Return the plot
            return dcc.Loading(
                dcc.Graph(id="plot", figure=fig, style={"height": DEFAULT_PLOT_HEIGHT})
            )

        except ValueError as e:
            return dbc.Alert(
                f"Invalid parameter values: {str(e)}",
                color="danger",
                className="text-center",
            )
        except Exception as e:
            return dbc.Alert(
                f"Error generating UMAP plot: {str(e)}",
                color="danger",
                className="text-center",
            )
