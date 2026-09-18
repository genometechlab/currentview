import argparse
import ipaddress
import webbrowser
from threading import Timer

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output

from .layout.main_layout import create_layout
from .callbacks.file_browser import register_file_callbacks
from .callbacks.initialization import register_initialization_callbacks
from .callbacks.conditions import register_condition_callbacks
from .callbacks.visualization import register_visualization_callbacks
from .callbacks.visualization_add import register_visualization_add_callbacks
from .callbacks.plot_settings import register_plot_settings_callbacks
from .callbacks.theme import register_theme_callbacks
from .callbacks.ui_interactions import register_ui_callbacks


def create_app() -> dash.Dash:
    """Create and configure the Dash application."""
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

    # Assign the function, not its result: Dash calls it on every page load so
    # each browser tab gets its own session id (and therefore its own
    # CurrentView). Assigning create_layout() would bake one id into a static
    # layout and make every visitor share a single visualizer.
    app.layout = create_layout

    # Register callbacks
    register_file_callbacks()
    register_initialization_callbacks()
    register_condition_callbacks()
    register_visualization_callbacks()
    register_visualization_add_callbacks()
    register_plot_settings_callbacks()
    register_theme_callbacks(app)
    register_ui_callbacks()

    return app


def open_browser(port: int):
    webbrowser.open_new(f"http://127.0.0.1:{port}")


def _is_loopback(host: str) -> bool:
    if host in ("localhost", ""):
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def main():
    parser = argparse.ArgumentParser(description="Run CurrentView Dash App")
    parser.add_argument("--port", type=int, default=8050, help="Port to serve on")
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help=(
            "Interface to bind (default: 127.0.0.1, this machine only). "
            "Use 0.0.0.0 to expose the app on your network — see the warning "
            "printed at startup before doing so."
        ),
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")

    args = parser.parse_args()

    if not _is_loopback(args.host):
        print(
            "\n"
            "  WARNING: binding to a non-loopback address.\n"
            "  CurrentView has no authentication. Anyone who can reach\n"
            f"  {args.host}:{args.port} will be able to browse this machine's\n"
            "  filesystem through the file picker and write exported plots to it.\n"
            "  Only do this on a network you trust.\n"
        )

    app = create_app()

    # Only open the browser once, not on each reloader cycle
    if not args.debug:
        Timer(1, open_browser, args=(args.port,)).start()

    app.run(debug=args.debug, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
