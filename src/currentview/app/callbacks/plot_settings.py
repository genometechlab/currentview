from dash import Input, Output, State, callback, ALL, no_update
from dash.exceptions import PreventUpdate

from currentview import PlotStyle
from .initialization import get_visualizer


def create_plot_style_for_theme(
    theme,
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
):
    """Helper to create PlotStyle based on theme."""
    if theme == "light":
        template = "plotly_white"
        titlecolor = "black"
        axis_title_color = "black"
        plot_bgcolor = "white"
        paper_bgcolor = "white"
        grid_color = "rgba(128, 128, 128, 0.2)"
        linecolor = "black"
        tickcolor = "black"
        legend_bgcolor = "rgba(255, 255, 255, 0.8)"
        legend_bordercolor = "rgba(0, 0, 0, 0.2)"
        hoverlabel_bgcolor = "white"
        hoverlabel_bordercolor = "black"
    else:
        template = "plotly_dark"
        titlecolor = "white"
        axis_title_color = "white"
        plot_bgcolor = "#18181b"
        paper_bgcolor = "#18181b"
        grid_color = "rgba(255, 255, 255, 0.1)"
        linecolor = "white"
        tickcolor = "white"
        legend_bgcolor = "rgba(0, 0, 0, 0.8)"
        legend_bordercolor = "rgba(255, 255, 255, 0.3)"
        hoverlabel_bgcolor = "#222222"
        hoverlabel_bordercolor = "white"

    return PlotStyle(
        width=width,
        height=height,
        line_width=line_width,
        line_style=line_style,
        template=template,
        show_grid=show_grid,
        show_legend=show_legend,
        zeroline=zeroline,
        showline=showline,
        title_font_size=title_font,
        titlecolor=titlecolor,
        axis_title_color=axis_title_color,
        axis_title_font_size=axis_font,
        tick_font_size=tick_font,
        legend_font_size=legend_font,
        margin={"l": margin_l, "r": margin_r, "t": margin_t, "b": margin_b},
        barrier_style=barrier_style,
        barrier_opacity=barrier_opacity,
        barrier_color=barrier_color,
        plot_bgcolor=plot_bgcolor,
        paper_bgcolor=paper_bgcolor,
        grid_color=grid_color,
        linecolor=linecolor,
        tickcolor=tickcolor,
        legend_bgcolor=legend_bgcolor,
        legend_bordercolor=legend_bordercolor,
        hoverlabel_bgcolor=hoverlabel_bgcolor,
        hoverlabel_bordercolor=hoverlabel_bordercolor,
    )


def register_plot_settings_callbacks():
    """Register all plot settings related callbacks."""

    # Apply signals style
    @callback(
        [
            Output("alert", "children", allow_duplicate=True),
            Output("alert", "is_open", allow_duplicate=True),
            Output("plot-trigger", "data", allow_duplicate=True),
        ],
        Input("signals-apply-style", "n_clicks"),
        [
            State("session-id", "data"),
            State("plot-trigger", "data"),
            # Dimension states
            State("signals-width", "value"),
            State("signals-height", "value"),
            # Line styling states
            State("signals-line-width-style", "value"),
            State("signals-line-style-default", "value"),
            # Theme states
            State("signals-template", "value"),
            # Grid and axes states
            State("signals-show-grid", "value"),
            State("signals-show-legend", "value"),
            State("signals-zeroline", "value"),
            State("signals-showline", "value"),
            # Font states
            State("signals-title-font-size", "value"),
            State("signals-axis-title-font-size", "value"),
            State("signals-tick-font-size", "value"),
            State("signals-legend-font-size", "value"),
            # Margin states
            State("signals-margin-l", "value"),
            State("signals-margin-r", "value"),
            State("signals-margin-t", "value"),
            State("signals-margin-b", "value"),
            # Barrier states
            State("signals-barrier-style", "value"),
            State("signals-barrier-opacity", "value"),
            State("signals-barrier-color", "value"),
            # Theme
            State("theme-store", "data"),
        ],
        prevent_initial_call=True,
    )
    def apply_signals_style(
        n_clicks,
        session_id,
        trigger,
        width,
        height,
        line_width,
        line_style,
        template,
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
        theme,
    ):
        """Apply plot style settings to signals visualization."""
        if not n_clicks:
            raise PreventUpdate

        viz = get_visualizer(session_id)
        if not viz:
            return "Please initialize visualizer first", True, trigger

        # Determine actual theme to use
        theme_to_use = theme if template == "auto" else template

        try:
            # Create PlotStyle instance
            style = create_plot_style_for_theme(
                theme_to_use,
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

            # Apply style to visualizer
            if hasattr(viz, "set_signals_style"):
                viz.set_signals_style(style)
            else:
                viz.signals_plot_style = style

            return "Signals plot style updated", True, trigger + 1

        except Exception as e:
            return f"Error applying style: {str(e)}", True, trigger

    # Apply stats style
    @callback(
        [
            Output("alert", "children", allow_duplicate=True),
            Output("alert", "is_open", allow_duplicate=True),
            Output("plot-trigger", "data", allow_duplicate=True),
        ],
        Input("stats-apply-style", "n_clicks"),
        [
            State("session-id", "data"),
            State("plot-trigger", "data"),
            # Dimension states
            State("stats-width", "value"),
            State("stats-height", "value"),
            # Line styling states
            State("stats-line-width-style", "value"),
            State("stats-line-style-default", "value"),
            # Theme states
            State("stats-template", "value"),
            # Grid and axes states
            State("stats-show-grid", "value"),
            State("stats-show-legend", "value"),
            State("stats-zeroline", "value"),
            State("stats-showline", "value"),
            # Font states
            State("stats-title-font-size", "value"),
            State("stats-axis-title-font-size", "value"),
            State("stats-tick-font-size", "value"),
            State("stats-legend-font-size", "value"),
            # Margin states
            State("stats-margin-l", "value"),
            State("stats-margin-r", "value"),
            State("stats-margin-t", "value"),
            State("stats-margin-b", "value"),
            # Barrier states
            State("stats-barrier-style", "value"),
            State("stats-barrier-opacity", "value"),
            State("stats-barrier-color", "value"),
            # Theme
            State("theme-store", "data"),
        ],
        prevent_initial_call=True,
    )
    def apply_stats_style(
        n_clicks,
        session_id,
        trigger,
        width,
        height,
        line_width,
        line_style,
        template,
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
        theme,
    ):
        """Apply plot style settings to statistics visualization."""
        if not n_clicks:
            raise PreventUpdate

        viz = get_visualizer(session_id)
        if not viz:
            return "Please initialize visualizer first", True, trigger

        # Determine actual theme to use
        theme_to_use = theme if template == "auto" else template

        try:
            # Create PlotStyle instance
            style = create_plot_style_for_theme(
                theme_to_use,
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

            # Apply style to visualizer
            if hasattr(viz, "set_stats_style"):
                viz.set_stats_style(style)
            else:
                viz.stats_plot_style = style

            return "Statistics plot style updated", True, trigger + 1

        except Exception as e:
            return f"Error applying style: {str(e)}", True, trigger
