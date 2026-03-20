from dash import Input, Output, callback

from ..styles.theme_styles import get_theme_clientside_callback


def register_theme_callbacks(app):

    @callback(
        Output("theme-store", "data"),
        Input("theme-toggle", "value"),
        prevent_initial_call=True,
    )
    def toggle_theme(toggle_value):
        return "dark" if toggle_value else "light"

    app.clientside_callback(
        get_theme_clientside_callback(),
        Output("theme-styles", "children"),
        Input("theme-store", "data"),
    )
