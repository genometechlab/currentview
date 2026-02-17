from dash import Input, Output, State, callback, ctx


def register_ui_callbacks():
    """Register UI interaction callbacks."""

    # Settings panel toggle callback
    @callback(
        Output("settings-panel", "is_open"),
        Input("settings-btn", "n_clicks"),
        State("settings-panel", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_settings(n_clicks, is_open):
        """Toggle the settings panel."""
        return not is_open

    # Add condition collapse toggle
    @callback(
        [
            Output("add-condition-collapse", "is_open"),
            Output("add-condition-chevron", "className"),
        ],
        Input("toggle-add-condition", "n_clicks"),
        State("add-condition-collapse", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_add_condition(n_clicks, is_open):
        """Toggle the add condition card collapse state."""
        new_state = not is_open
        chevron_class = "bi bi-chevron-up" if new_state else "bi bi-chevron-down"
        return new_state, chevron_class

    @callback(
        [
            Output("gmm-tab", "disabled"),
            Output("umap-tab", "disabled"),
        ],
        [
            Input("conditions-metadata", "data"),
            Input("stats-store", "data"),
        ],
    )
    def toggle_analysis_tabs(conditions_metadata, stored_stats):
        """Enable or disable analysis tabs based on whether conditions and stats are available."""
        # Check if we have at least one condition
        has_conditions = len(conditions_metadata) > 0 if conditions_metadata else False

        # Check if we have at least one stat
        has_stats = len(stored_stats) > 0 if stored_stats else False

        # Both conditions AND stats must be available to enable tabs
        if has_conditions and has_stats:
            return False, False  # Enable tabs
        else:
            return True, True  # Disable tabs

    @callback(
        [
            Output("base-a", "active"),
            Output("base-c", "active"),
            Output("base-g", "active"),
            Output("base-t", "active"),
            Output("matched-query-base", "data"),  # dcc.Store to hold the actual value
        ],
        [
            Input("base-a", "n_clicks"),
            Input("base-c", "n_clicks"),
            Input("base-g", "n_clicks"),
            Input("base-t", "n_clicks"),
        ],
        [
            State("base-a", "active"),
            State("base-c", "active"),
            State("base-g", "active"),
            State("base-t", "active"),
        ],
        prevent_initial_call=True,
    )
    def toggle_base_buttons(
        a_clicks, c_clicks, g_clicks, t_clicks, a_active, c_active, g_active, t_active
    ):
        """Toggle base buttons and update selected bases."""
        triggered_id = ctx.triggered_id

        # Toggle whichever button was clicked
        states = {
            "base-a": a_active,
            "base-c": c_active,
            "base-g": g_active,
            "base-t": t_active,
        }
        states[triggered_id] = not states[triggered_id]

        # If none selected, treat as all selected (return None)
        selected = [
            b for b, active in zip(["A", "C", "G", "T"], states.values()) if active
        ]
        store_value = selected if selected else None  # None means "any"

        return (
            states["base-a"],
            states["base-c"],
            states["base-g"],
            states["base-t"],
            store_value,
        )
