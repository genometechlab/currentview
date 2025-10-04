import logging
import numpy as np
import plotly.graph_objects as go
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union, Literal, Any
from dataclasses import dataclass, field
from collections import OrderedDict

from .readers import AlignmentExtractor
from .readers import SignalExtractor
from .utils import ReadAlignment, Condition
from .utils import validate_files
from .utils import PlotStyle, ColorScheme
from .utils import to_rgba_str, get_contrasting_color


class GMMVisualizer:
    """Handles all plotting, visualization, and figure management using Plotly."""

    def __init__(
        self,
        style: Optional[PlotStyle] = None,
        color_scheme: Optional[ColorScheme] = None,
        logger: Optional[logging.Logger] = None,
    ):
        pass

    def _create_figure(self):
        pass

    def plot_gmms(self, conditions: List[Condition]):
        pass

    def show(self):
        """Display the plot."""
        self.logger.info("Displaying plot")
        self.fig.show()

    def get_fig(self):
        self.logger.info("Returning fig")
        return self.fig

    def save(
        self,
        path: Union[str, Path],
        format: Optional[str] = None,
        scale: Optional[float] = None,
        **kwargs,
    ):
        """Save the figure to file."""
        path = Path(path)

        if format is None:
            format = path.suffix.lstrip(".").lower() or "png"

        self.logger.debug(f"Saving figure: path={path}, format={format}")

        try:
            if format == "html":
                self.fig.write_html(str(path), **kwargs)
            else:
                write_kwargs = {
                    "format": format,
                    "scale": scale or self.style.toImageButtonOptions.get("scale", 2),
                }
                write_kwargs.update(kwargs)
                self.fig.write_image(str(path), **write_kwargs)

            self.logger.info(f"Saved figure to {path}")
        except Exception as e:
            self.logger.error(f"Failed to save figure: {type(e).__name__}: {str(e)}")
            raise e
