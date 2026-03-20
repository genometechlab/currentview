from dash import Input, Output, State, callback, no_update
from dash.exceptions import PreventUpdate

from currentview import PlotStyle
from .initialization import get_visualizer
from ..styles.constants import COLOR_TEXT, COLOR_BG_INPUT, COLOR_BORDER


# ── Theme token maps ──────────────────────────────────────────────────────────

_THEME_TOKENS = {
    "light": dict(
        template="plotly_white",
        title_color=COLOR_TEXT,
        axis_title_color=COLOR_TEXT,
        plot_bgcolor=COLOR_BG_INPUT,
        paper_bgcolor=COLOR_BG_INPUT,
        grid_color="rgba(128,128,128,0.2)",
        linecolor=COLOR_TEXT,
        tick_color=COLOR_TEXT,
        legend_bgcolor=COLOR_BG_INPUT,
        legend_bordercolor=COLOR_BORDER,
        hoverlabel_bgcolor=COLOR_BG_INPUT,
        hoverlabel_bordercolor=COLOR_TEXT,
    ),
    "dark": dict(
        template="plotly_dark",
        title_color="#e4e4e7",
        axis_title_color="#e4e4e7",
        plot_bgcolor="#18181b",
        paper_bgcolor="#18181b",
        grid_color="rgba(255,255,255,0.1)",
        linecolor="#e4e4e7",
        tick_color="#e4e4e7",
        legend_bgcolor="rgba(0,0,0,0.8)",
        legend_bordercolor="#3f3f46",
        hoverlabel_bgcolor="#27272a",
        hoverlabel_bordercolor="#e4e4e7",
    ),
}

_APPLY_METHOD = {
    "signals": "set_signals_style",
    "stats": "set_stats_style",
}


# ── Style factory ─────────────────────────────────────────────────────────────


def _build_plot_style(
    theme_mode: str,
    width,
    height,
    line_width,
    line_style,
    show_grid,
    show_legend,
    zeroline,
    showline,
    title_font,
    axis_font,
    tick_font,
    legend_font,
    margin_l,
    margin_r,
    margin_t,
    margin_b,
    barrier_style,
    barrier_opacity,
    barrier_color,
) -> PlotStyle:
    tokens = _THEME_TOKENS.get(theme_mode, _THEME_TOKENS["light"])
    return PlotStyle(
        width=width,
        height=height,
        line_width=line_width,
        line_style=line_style,
        show_grid=show_grid,
        show_legend=show_legend,
        zeroline=zeroline,
        showline=showline,
        title_font_size=title_font,
        axis_title_font_size=axis_font,
        tick_font_size=tick_font,
        legend_font_size=legend_font,
        margin={"l": margin_l, "r": margin_r, "t": margin_t, "b": margin_b},
        barrier_style=barrier_style,
        barrier_opacity=barrier_opacity,
        barrier_color=barrier_color,
        **tokens,
    )


# ── Callback registration ─────────────────────────────────────────────────────


def register_plot_settings_callbacks():

    def _make_apply_callback(target: str):
        label = "Signals" if target == "signals" else "Statistics"
        p = target

        extra_states = (
            [State("stats-distribution-kind", "value")] if target == "stats" else []
        )

        @callback(
            Output("alert", "children", allow_duplicate=True),
            Output("alert", "is_open", allow_duplicate=True),
            Output("plot-trigger", "data", allow_duplicate=True),
            Input(f"{p}-apply-style", "n_clicks"),
            State("session-id", "data"),
            State("plot-trigger", "data"),
            State(f"{p}-width", "value"),
            State(f"{p}-height", "value"),
            State(f"{p}-line-width-style", "value"),
            State(f"{p}-line-style-default", "value"),
            State(f"{p}-template", "value"),
            State(f"{p}-show-grid", "value"),
            State(f"{p}-show-legend", "value"),
            State(f"{p}-zeroline", "value"),
            State(f"{p}-showline", "value"),
            State(f"{p}-title-font-size", "value"),
            State(f"{p}-axis-title-font-size", "value"),
            State(f"{p}-tick-font-size", "value"),
            State(f"{p}-legend-font-size", "value"),
            State(f"{p}-margin-l", "value"),
            State(f"{p}-margin-r", "value"),
            State(f"{p}-margin-t", "value"),
            State(f"{p}-margin-b", "value"),
            State(f"{p}-barrier-style", "value"),
            State(f"{p}-barrier-opacity", "value"),
            State(f"{p}-barrier-color", "value"),
            State("theme-store", "data"),
            *extra_states,
            prevent_initial_call=True,
        )
        def apply_style(
            n_clicks,
            session_id,
            trigger,
            width,
            height,
            line_width,
            line_style,
            template_mode,
            show_grid,
            show_legend,
            zeroline,
            showline,
            title_font,
            axis_font,
            tick_font,
            legend_font,
            margin_l,
            margin_r,
            margin_t,
            margin_b,
            barrier_style,
            barrier_opacity,
            barrier_color,
            app_theme,
            distribution_kind=None,
        ):
            if not n_clicks:
                raise PreventUpdate

            viz = get_visualizer(session_id)
            if not viz:
                return "Please initialize the visualizer first", True, no_update

            theme_mode = app_theme if template_mode == "auto" else template_mode

            try:
                style = _build_plot_style(
                    theme_mode,
                    width,
                    height,
                    line_width,
                    line_style,
                    show_grid,
                    show_legend,
                    zeroline,
                    showline,
                    title_font,
                    axis_font,
                    tick_font,
                    legend_font,
                    margin_l,
                    margin_r,
                    margin_t,
                    margin_b,
                    barrier_style,
                    barrier_opacity,
                    barrier_color,
                )
                getattr(viz, _APPLY_METHOD[target])(style)
                if distribution_kind is not None:
                    viz.set_distribution_kind(distribution_kind)
                return f"{label} plot style updated", True, trigger + 1
            except Exception as e:
                return f"Error applying style: {e}", True, no_update

    for target in ("signals", "stats"):
        _make_apply_callback(target)
