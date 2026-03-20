from dash import Input, Output, State, callback, ctx, html, no_update, ALL
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

from currentview import CurrentView, PlotStyle
from ..utils import validate_window_size, validate_json_string, validate_kmer_labels
from ..utils.processing_factory import process_signal


# NOTE: Module-level dict — sessions are not shared across workers.
# If deploying with multiple gunicorn workers, replace with a server-side
# cache (e.g. Redis, Flask-Caching) keyed by session_id.
visualizers: dict[str, CurrentView] = {}


def get_visualizer(session_id: str) -> CurrentView | None:
    """Get the visualizer instance for a session."""
    return visualizers.get(session_id)


# ── Shared helpers ────────────────────────────────────────────────────────────


def _init_error(msg: str) -> tuple:
    """Return tuple for a failed initialization — keeps all 7 outputs."""
    return {"display": "none"}, {}, msg, True, True, {"display": "none"}, no_update


def _make_stat_badges(stats: list[str], rm_type: str) -> list:
    return [
        dbc.Badge(
            [
                stat,
                dbc.Button(
                    "×",
                    id={"type": rm_type, "stat": stat},
                    size="sm",
                    className="ms-1 p-0 text-white",
                    style={"border": "none", "background": "transparent"},
                ),
            ],
            color="primary",
            className="me-1 mb-1",
            style={"fontSize": "0.9rem", "padding": "0.5rem"},
        )
        for stat in stats
    ] or [html.Small("No statistics selected", className="text-muted")]


def _update_stat_list(
    trigger,
    selected: str | None,
    current: list[str],
    add_id: str,
    rm_type: str,
) -> list[str]:
    """Add or remove a stat from the current list based on the trigger."""
    if trigger == add_id:
        if selected and selected not in current:
            return current + [selected]
    elif isinstance(trigger, dict) and trigger.get("type") == rm_type:
        return [s for s in current if s != trigger["stat"]]
    return current


# ── Callbacks ─────────────────────────────────────────────────────────────────


def register_initialization_callbacks():

    @callback(
        Output("bessel-params", "is_open"),
        Output("gaussian-params", "is_open"),
        Input("filtering-options", "value"),
    )
    def toggle_filter_params(filtering_option):
        return filtering_option == "bessel", filtering_option == "gaussian"

    @callback(
        Output("advanced", "is_open"),
        Output("toggle-adv", "children"),
        Input("toggle-adv", "n_clicks"),
        State("advanced", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_advanced(n_clicks, is_open):
        is_open = not is_open
        return is_open, "▲ Advanced Options" if is_open else "▼ Advanced Options"

    @callback(
        Output("window-size", "invalid"),
        Input("window-size", "value"),
    )
    def validate_window(value):
        return validate_window_size(value)

    @callback(
        Output("stats-store", "data"),
        Output("stats-list", "children"),
        Input("add-stat", "n_clicks"),
        Input({"type": "rm-stat", "stat": ALL}, "n_clicks"),
        State("stat-select", "value"),
        State("stats-store", "data"),
        prevent_initial_call=True,
    )
    def manage_stats(add_click, remove_clicks, selected, stats):
        stats = _update_stat_list(
            ctx.triggered_id, selected, stats or [], "add-stat", "rm-stat"
        )
        return stats, _make_stat_badges(stats, "rm-stat")

    @callback(
        Output("main", "style"),
        Output("init-card", "style"),
        Output("alert", "children"),
        Output("alert", "is_open"),
        Output("stats-tab", "disabled"),
        Output("settings-btn", "style"),
        Output("molecule-type-store", "data"),
        Input("init-btn", "n_clicks"),
        State("window-size", "value"),
        State("kmer-labels", "value"),
        State("stats-store", "data"),
        State("molecule-type-options", "value"),
        State("custom-title", "value"),
        State("verbosity", "value"),
        State("style-options", "value"),
        State("filtering-options", "value"),
        State("bessel-order", "value"),
        State("bessel-cutoff", "value"),
        State("gaussian-sigma", "value"),
        State("normalization-options", "value"),
        State("custom-style", "value"),
        State("session-id", "data"),
        prevent_initial_call=True,
    )
    def initialize(
        n_clicks,
        k,
        kmer_text,
        stats,
        molecule_type,
        title,
        verbosity,
        style_opts,
        filtering_option,
        bessel_order,
        bessel_cutoff,
        gaussian_sigma,
        normalization,
        custom_style,
        session_id,
    ):
        if not k or k % 2 == 0:
            return _init_error("Window size must be an odd number!")

        params = {"K": k, "verbosity": int(verbosity)}

        if kmer_text:
            is_valid, kmers, error_msg = validate_kmer_labels(kmer_text, k)
            if not is_valid:
                return _init_error(error_msg)
            params["kmer"] = kmers

        if stats:
            params["stats"] = stats

        if title:
            params["title"] = title

        if custom_style:
            is_valid, style_data, error_msg = validate_json_string(custom_style)
            if not is_valid:
                return _init_error(error_msg)
            # style_data is passed as overrides into PlotStyle below

        # Build plot style from style options
        base = "interactive_dark" if "dark" in style_opts else "interactive"
        plot_style = PlotStyle.get_style(base)
        plot_style.show_grid = "grid" in style_opts
        plot_style.show_legend = "legend" in style_opts
        plot_style.renderer = "WebGL" if "webgl" in style_opts else "SVG"

        params["signals_plot_style"] = plot_style
        params["stats_plot_style"] = plot_style

        params["signal_processing_fn"] = lambda signal: process_signal(
            signal,
            normalization_method=normalization,
            filter_method=filtering_option,
            bessel_order=bessel_order,
            bessel_cutoff=bessel_cutoff,
            gaussian_sigma=gaussian_sigma,
        )

        visualizers[session_id] = CurrentView(**params)

        msg = f"Initialized with K={k}"
        if stats:
            msg += f", stats={stats}"

        return (
            {"display": "block"},
            {"display": "none"},
            msg,
            True,
            len(stats) == 0,
            {"display": "inline-block", "marginLeft": "20px", "fontSize": "1.2rem"},
            molecule_type,
        )
