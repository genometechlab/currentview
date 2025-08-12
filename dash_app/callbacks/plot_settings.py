from dash import Input, Output, State, callback, ALL
from dash.exceptions import PreventUpdate

from currentview import PlotStyle
from .initialization import get_visualizer


def register_plot_settings_callbacks():
    """Register all plot settings related callbacks."""
    
    # Enable/disable fixed opacity based on mode
    for prefix in ["signals", "stats"]:
        @callback(
            Output(f"{prefix}-fixed-opacity", "disabled"),
            Input(f"{prefix}-opacity-mode", "value"),
            prevent_initial_call=True
        )
        def toggle_opacity_input(mode, p=prefix):
            """Enable fixed opacity input only when mode is 'fixed'."""
            return mode != "fixed"
    
    # Apply signals style
    @callback(
        [Output("alert", "children", allow_duplicate=True),
         Output("alert", "is_open", allow_duplicate=True),
         Output("plot-trigger", "data", allow_duplicate=True)],
        Input("signals-apply-style", "n_clicks"),
        [State("session-id", "data"),
         State("plot-trigger", "data"),
         # Dimension states
         State("signals-width", "value"),
         State("signals-height", "value"),
         # Line styling states
         State("signals-line-width-style", "value"),
         State("signals-line-style-default", "value"),
         State("signals-opacity-mode", "value"),
         State("signals-fixed-opacity", "value"),
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
         State("signals-barrier-color", "value")],
        prevent_initial_call=True
    )
    def apply_signals_style(n_clicks, session_id, trigger, width, height,
                           line_width, line_style, opacity_mode, fixed_opacity,
                           template, show_grid, show_legend, zeroline, showline,
                           title_font, axis_font, tick_font, legend_font,
                           margin_l, margin_r, margin_t, margin_b,
                           barrier_style, barrier_opacity, barrier_color):
        """Apply plot style settings to signals visualization."""
        if not n_clicks:
            raise PreventUpdate
        
        viz = get_visualizer(session_id)
        if not viz:
            return "Please initialize visualizer first", True, trigger
        
        try:
            # Create PlotStyle instance with all settings
            style = PlotStyle(
                width=width,
                height=height,
                line_width=line_width,
                line_style=line_style,
                opacity_mode=opacity_mode,
                fixed_opacity=fixed_opacity,
                template=template,
                show_grid=show_grid,
                show_legend=show_legend,
                zeroline=zeroline,
                showline=showline,
                title_font_size=title_font,
                axis_title_font_size=axis_font,
                tick_font_size=tick_font,
                legend_font_size=legend_font,
                margin={
                    'l': margin_l,
                    'r': margin_r,
                    't': margin_t,
                    'b': margin_b
                },
                barrier_style=barrier_style,
                barrier_opacity=barrier_opacity,
                barrier_color=barrier_color
            )
            
            # Apply style to visualizer
            if hasattr(viz, 'set_signals_style'):
                viz.set_signals_style(style)
            else:
                # Fallback: directly set the style
                viz.signals_plot_style = style
            
            return "Signals plot style updated", True, trigger + 1
            
        except Exception as e:
            return f"Error applying style: {str(e)}", True, trigger
    
    # Apply stats style
    @callback(
        [Output("alert", "children", allow_duplicate=True),
         Output("alert", "is_open", allow_duplicate=True),
         Output("plot-trigger", "data", allow_duplicate=True)],
        Input("stats-apply-style", "n_clicks"),
        [State("session-id", "data"),
         State("plot-trigger", "data"),
         # Dimension states
         State("stats-width", "value"),
         State("stats-height", "value"),
         # Line styling states
         State("stats-line-width-style", "value"),
         State("stats-line-style-default", "value"),
         State("stats-opacity-mode", "value"),
         State("stats-fixed-opacity", "value"),
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
         State("stats-barrier-color", "value")],
        prevent_initial_call=True
    )
    def apply_stats_style(n_clicks, session_id, trigger, width, height,
                         line_width, line_style, opacity_mode, fixed_opacity,
                         template, show_grid, show_legend, zeroline, showline,
                         title_font, axis_font, tick_font, legend_font,
                         margin_l, margin_r, margin_t, margin_b,
                         barrier_style, barrier_opacity, barrier_color):
        """Apply plot style settings to statistics visualization."""
        if not n_clicks:
            raise PreventUpdate
        
        viz = get_visualizer(session_id)
        if not viz:
            return "Please initialize visualizer first", True, trigger
        
        try:
            # Create PlotStyle instance with all settings
            style = PlotStyle(
                width=width,
                height=height,
                line_width=line_width,
                line_style=line_style,
                opacity_mode=opacity_mode,
                fixed_opacity=fixed_opacity,
                template=template,
                show_grid=show_grid,
                show_legend=show_legend,
                zeroline=zeroline,
                showline=showline,
                title_font_size=title_font,
                axis_title_font_size=axis_font,
                tick_font_size=tick_font,
                legend_font_size=legend_font,
                margin={
                    'l': margin_l,
                    'r': margin_r,
                    't': margin_t,
                    'b': margin_b
                },
                barrier_style=barrier_style,
                barrier_opacity=barrier_opacity,
                barrier_color=barrier_color
            )
            
            # Apply style to visualizer
            if hasattr(viz, 'set_stats_style'):
                viz.set_stats_style(style)
            else:
                # Fallback: directly set the style
                viz.stats_plot_style = style
            
            return "Statistics plot style updated", True, trigger + 1
            
        except Exception as e:
            return f"Error applying style: {str(e)}", True, trigger