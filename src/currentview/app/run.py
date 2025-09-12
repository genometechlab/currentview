import dash
import dash_bootstrap_components as dbc
import webbrowser
from threading import Timer
import argparse
import os

from .layout.main_layout import create_layout
from .callbacks.file_browser import (
    register_file_browser_callbacks,
    register_file_saver_callbacks,
)
from .callbacks.initialization import register_initialization_callbacks
from .callbacks.conditions import register_condition_callbacks
from .callbacks.visualization import register_visualization_callbacks
from .callbacks.plot_settings import register_plot_settings_callbacks
from .callbacks.theme import register_theme_callbacks
from .callbacks.ui_interactions import register_ui_callbacks
from .utils.visualizer_extensions import apply_plot_style_extensions

from dash import Dash, html, Input, Output


def create_app() -> dash.Dash:
    """Create and configure the Dash application."""
    apply_plot_style_extensions()

    app = dash.Dash(
        __name__,
        external_stylesheets=[
            dbc.themes.BOOTSTRAP,
            "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css",
        ],
        suppress_callback_exceptions=True,
        title="CurrentView",
        assets_folder="assets",
        assets_url_path="/assets/",
    )

    app.clientside_callback(
        """
        function(n_clicks) {
            if (n_clicks) {
                window.location.reload();
            }
            return null;
        }
        """,
        Output("app-title", "children"),
        Input("app-title", "n_clicks"),
        prevent_initial_call=True,
    )

    app.layout = create_layout()

    # Register callbacks
    register_file_browser_callbacks()
    register_file_saver_callbacks()
    register_initialization_callbacks()
    register_condition_callbacks()
    register_visualization_callbacks()
    register_plot_settings_callbacks()
    register_theme_callbacks(app)
    register_ui_callbacks()

    return app


def open_browser(port: int):
    webbrowser.open_new(f"http://127.0.0.1:{port}")


def main():
    parser = argparse.ArgumentParser(description="Run CurrentView Dash App")
    parser.add_argument("--port", type=int, default=8050, help="Port to serve on")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")

    args = parser.parse_args()
    app = create_app()

    # Only open the browser once, not on each reloader cycle
    if not args.debug:
        Timer(1, open_browser, args=(args.port,)).start()

    app.run(debug=args.debug, host="0.0.0.0", port=args.port)


if __name__ == "__main__":
    main()
