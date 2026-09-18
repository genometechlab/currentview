import time
from collections import OrderedDict
from dataclasses import fields
from threading import Lock

from dash import Input, Output, State, callback, ctx, html, no_update, ALL
import dash_bootstrap_components as dbc

from currentview import CurrentView, PlotStyle
from ..utils import validate_window_size, validate_json_string, validate_kmer_labels
from ..utils.processing_factory import (
    process_signal,
    DEFAULT_BESSEL_ORDER,
    DEFAULT_BESSEL_CUTOFF,
    DEFAULT_GAUSSIAN_SIGMA,
)


# Each CurrentView holds every read's raw signal, so an unbounded store would
# leak a full dataset per browser tab. Cap the number of live sessions and
# expire idle ones.
#
# NOTE: this is per-process — sessions are not shared across workers. If
# deploying with multiple gunicorn workers, replace with a server-side cache
# (e.g. Redis, Flask-Caching) keyed by session_id.
MAX_SESSIONS = 8
SESSION_TTL_SECONDS = 2 * 60 * 60  # 2 hours idle

_visualizers: "OrderedDict[str, CurrentView]" = OrderedDict()
_last_seen: dict[str, float] = {}
# Last GMM/UMAP figure rendered per session, so those tabs can be exported.
# Figures are cheap next to a CurrentView, and expire with their session.
_analysis_figures: dict[str, dict] = {}
_lock = Lock()


def _forget_locked(session_id: str) -> None:
    _visualizers.pop(session_id, None)
    _last_seen.pop(session_id, None)
    _analysis_figures.pop(session_id, None)


def _evict_locked() -> None:
    """Drop expired sessions, then the least recently used ones over the cap."""
    now = time.monotonic()

    for sid in [s for s, t in _last_seen.items() if now - t > SESSION_TTL_SECONDS]:
        _forget_locked(sid)

    while len(_visualizers) > MAX_SESSIONS:
        sid, _ = _visualizers.popitem(last=False)
        _last_seen.pop(sid, None)
        _analysis_figures.pop(sid, None)


def set_analysis_figure(session_id: str, tab: str, fig) -> None:
    """Remember the most recent GMM/UMAP figure for a session."""
    with _lock:
        _analysis_figures.setdefault(session_id, {})[tab] = fig


def get_analysis_figure(session_id: str, tab: str):
    """Return the most recent GMM/UMAP figure for a session, if any."""
    with _lock:
        return _analysis_figures.get(session_id, {}).get(tab)


def set_visualizer(session_id: str, viz: CurrentView) -> None:
    """Register the visualizer for a session, evicting stale ones."""
    with _lock:
        _visualizers[session_id] = viz
        _visualizers.move_to_end(session_id)
        _last_seen[session_id] = time.monotonic()
        _evict_locked()


def get_visualizer(session_id: str) -> CurrentView | None:
    """Get the visualizer instance for a session, refreshing its idle timer."""
    with _lock:
        viz = _visualizers.get(session_id)
        if viz is not None:
            _visualizers.move_to_end(session_id)
            _last_seen[session_id] = time.monotonic()
        return viz


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

        style_overrides = {}
        if custom_style:
            is_valid, style_data, error_msg = validate_json_string(custom_style)
            if not is_valid:
                return _init_error(error_msg)
            if style_data is not None:
                if not isinstance(style_data, dict):
                    return _init_error(
                        "Custom plot style must be a JSON object, "
                        'e.g. {"line_width": 1.5}'
                    )
                style_overrides = style_data

        # Build plot style from style options
        base = "interactive_dark" if "dark" in style_opts else "interactive"
        plot_style = PlotStyle.get_style(base)
        plot_style.show_grid = "grid" in style_opts
        plot_style.show_legend = "legend" in style_opts
        plot_style.renderer = "WebGL" if "webgl" in style_opts else "SVG"

        # Apply the user's JSON overrides last so they win over the checkboxes
        unknown = [f for f in style_overrides if not hasattr(plot_style, f)]
        if unknown:
            valid = ", ".join(sorted(f.name for f in fields(PlotStyle)))
            return _init_error(
                f"Unknown plot style field(s): {', '.join(unknown)}. Valid: {valid}"
            )
        for field_name, value in style_overrides.items():
            setattr(plot_style, field_name, value)

        params["signals_plot_style"] = plot_style
        params["stats_plot_style"] = plot_style

        params["signal_processing_fn"] = lambda signal: process_signal(
            signal,
            normalization_method=normalization,
            filtering_method=filtering_option,
            bessel_order=bessel_order or DEFAULT_BESSEL_ORDER,
            bessel_cutoff=bessel_cutoff or DEFAULT_BESSEL_CUTOFF,
            gaussian_sigma=gaussian_sigma or DEFAULT_GAUSSIAN_SIGMA,
        )

        set_visualizer(session_id, CurrentView(**params))

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
