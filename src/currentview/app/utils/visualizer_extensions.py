# dash_app/utils/visualizer_extensions.py
"""Extensions for the GenomicPositionVisualizer to support dynamic style updates."""

from currentview import PlotStyle


def apply_plot_style_extensions():
    """Add methods to GenomicPositionVisualizer for style updates.

    This is a monkey-patch approach to add methods without modifying the original class.
    """
    from currentview import GenomicPositionVisualizer

    def set_signals_style(self, style: PlotStyle):
        """Set the plot style for signals visualization.

        Args:
            style: PlotStyle instance with configuration
        """
        self.signals_plot_style = style
        # Clear cached visualization to force recreation with new style
        if hasattr(self, "_signal_viz"):
            delattr(self, "_signal_viz")

    def set_stats_style(self, style: PlotStyle):
        """Set the plot style for statistics visualization.

        Args:
            style: PlotStyle instance with configuration
        """
        self.stats_plot_style = style
        # Clear cached visualization to force recreation with new style
        if hasattr(self, "_stats_viz"):
            delattr(self, "_stats_viz")

    # Add methods to the class
    if not hasattr(GenomicPositionVisualizer, "set_signals_style"):
        GenomicPositionVisualizer.set_signals_style = set_signals_style

    if not hasattr(GenomicPositionVisualizer, "set_stats_style"):
        GenomicPositionVisualizer.set_stats_style = set_stats_style
