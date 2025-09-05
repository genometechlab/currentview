from dash import Input, Output, State, callback


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
