import logging
import numpy as np
import plotly.graph_objects as go
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union, Literal, Any
from dataclasses import dataclass, field
from collections import OrderedDict

from .readers import AlignmentExtractor
from .readers import SignalExtractor

from .utils.data_classes import ReadAlignment, Condition
from .utils.path_utils import validate_files
from .utils.plotly_utils import PlotStyle
from .utils.color_utils import to_rgba_str, get_contrasting_color


class SignalVisualizer:
    """Handles all plotting, visualization, and figure management using Plotly."""

    def __init__(
        self,
        K: int,
        window_labels: Optional[List[Union[str, int]]] = None,
        plot_style: Optional[PlotStyle] = None,
        title: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize the visualizer.

        Args:
            K: Number of bases to show
            window_labels: Optional custom labels for x-axis
            plot_style: Optional PlotStyle configuration
            title: Optional custom title
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        self.logger.debug(f"Initializing SignalVisualizer with K={K}")

        self.K = K
        self.window_labels = window_labels
        if self.window_labels and len(self.window_labels) != self.K:
            raise ValueError("window_labels must have length K")

        # Setup style
        self.style = plot_style or PlotStyle()

        if self.style.renderer == "SVG":
            self._plot_func = go.Scatter
        elif self.style.renderer == "WebGL":
            self._plot_func = go.Scattergl
        else:
            self.logger.warning(
                f"Invalid renderer selected. Available options: 'SVG' and 'WebGL'. Defaulting to 'SVG'."
            )
            self._plot_func = go.Scatter

        # Store initial title
        self.title = title or "Nanopore Signal Visualization"

        # Create figure
        self.logger.debug(f"Creating Plotly figure")
        self._create_figure()

        # Add position barriers
        self.logger.debug("Adding position barriers")
        self._add_position_barriers()

        # Track plotting state
        self._conditions_info: "OrderedDict[str, Dict]" = OrderedDict()

        # store indices for shapes/annotations
        self._highlight_shapes: List[str] = []
        self._annotation_indices: List[str] = []

        # Track global y-axis limits
        self._auto_ylim = True  # Flag to enable/disable auto y-axis adjustment

        self.logger.info(f"Initialized SignalVisualizer with K={K}")

    def _create_figure(self):
        """Create and configure the Plotly figure."""
        self.logger.debug("Creating Plotly figure")

        self.fig = go.Figure()

        # Apply style
        layout_dict = self.style.get_layout_dict()
        if "title" not in layout_dict:
            layout_dict["title"] = {}
        layout_dict["title"].update({"text": self.title, "x": 0.5, "xanchor": "center"})
        # Preserve font settings from style if they exist
        if "font" not in layout_dict["title"]:
            layout_dict["title"]["font"] = {"size": self.style.title_font_size}

        # Merge xaxis settings
        if "xaxis" not in layout_dict:
            layout_dict["xaxis"] = {}
        else:
            try:
                title_font = layout_dict["xaxis"]["title"]["font"]
            except:
                title_font = {}
        layout_dict["xaxis"].update(
            {
                "title": {"text": "Genomic Position", "font": title_font},
                "showgrid": False,
                "tickmode": "array",
                "tickvals": [],
                "ticktext": [],
                "range": [
                    -0.1,
                    self.K - self.style.positions_padding + 0.1,
                ],  # Using 0.025 as default padding
            }
        )

        # Merge yaxis settings
        if "yaxis" not in layout_dict:
            layout_dict["yaxis"] = {}
        else:
            try:
                title_font = layout_dict["yaxis"]["title"]["font"]
            except:
                title_font = {}
        layout_dict["yaxis"].update(
            {
                "title": {"text": "Signal (pA)", "font": title_font},
            }
        )

        self.fig.update_layout(**layout_dict)

        # Apply custom labels if provided
        if self.window_labels:
            self._apply_custom_labels()

    def _add_position_barriers(self):
        """Add vertical lines to separate positions."""
        self.logger.debug(f"Adding {self.K + 1} position barriers")

        # Add vertical lines as shapes
        for i in range(self.K + 1):
            x_pos = i - self.style.positions_padding / 2  # Using 0.025 as default padding

            self.fig.add_shape(
                type="line",
                x0=x_pos,
                x1=x_pos,
                y0=0,
                y1=1,
                yref="paper",
                line=dict(
                    color=self.style.barrier_color,
                    width=1.5,
                    dash=self.style.barrier_style,
                ),
                layer="below",
                opacity=self.style.barrier_opacity,
            )

    def _apply_custom_labels(self):
        """Apply custom window labels."""
        self.logger.debug(f"Applying {len(self.window_labels)} custom labels")

        tick_positions = np.arange(self.K) + 0.5 - self.style.positions_padding / 2

        self.fig.update_xaxes(
            tickmode="array",
            tickvals=tick_positions,
            ticktext=[str(label) for label in self.window_labels],
        )

    def plot_condition(self, condition: Condition):
        """Plot a processed group of reads."""
        reads = condition.reads
        positions = condition.positions
        label = condition.label
        color = condition.color
        opacity = condition.alpha
        line_width = condition.line_width
        line_style = condition.line_style

        self.logger.debug(
            f"plot_condition called: label='{label}', n_reads={len(reads)}"
        )

        # Check if condition already plotted
        if label in self._conditions_info:
            self.logger.warning(f"Condition '{label}' already plotted. Updating it.")
            self.remove_condition(label)

        # Extract reference bases
        self.logger.debug("Extracting reference bases")
        kmer_dict = self._extract_reference_bases(positions, reads)
        position_labels = [f"{pos} - {kmer_dict[pos]}" for pos in positions]
        condition_info = {"color": color, "pos_labels": position_labels}

        # Plot the signals and get y-axis bounds
        self.logger.info(f"Plotting {len(reads)} reads for condition '{label}'")
        self._plot_signals(condition)

        # Store plotted condition
        self._conditions_info[condition.label] = condition_info

        # Update position labels
        self._update_global_ylim()
        if not self.window_labels:
            self._update_position_labels()

    def _get_base_signal(
        self, read_alignment: ReadAlignment, genomic_pos: int
    ) -> np.ndarray:
        base = read_alignment.get_base_at_ref_pos(genomic_pos)
        if base is None or not base.has_signal:
            return None
        base_sig = base.get_signal(read=read_alignment)
        if base_sig is None:
            return None
        base_sig = np.asarray(
            base_sig, dtype=float
        ).ravel()  # <- robust to list/np/scalar
        if base_sig.size == 0:
            return None
        return base_sig

    def _get_insertions_signal(
        self, read_alignment: ReadAlignment, genomic_pos: int
    ) -> np.ndarray:
        insertions = read_alignment.insertions_by_ref_pos.get(genomic_pos, None)
        if insertions is None:
            insertions_sig = np.empty((0,))
        else:
            insertions_sig = [
                insertion.get_signal(read=read_alignment)
                for insertion in insertions
                if insertion.has_signal
            ]
            insertions_sig = np.concatenate(insertions_sig)
        return insertions_sig

    def _plot_signals(self, condition: Condition):
        """Plot each read as its own trace (condition alpha applied per-read)."""
        pad = self.style.positions_padding
        lw = condition.line_width or self.style.line_width
        ls = condition.line_style or self.style.line_style
        col = condition.color
        alp = condition.alpha

        for read_alignment in condition.reads:
            matched_x: List[np.ndarray] = []
            matched_y: List[np.ndarray] = []

            insertions_x: List[np.ndarray] = []
            insertions_y: List[np.ndarray] = []

            for pos_idx, genomic_pos in enumerate(condition.positions):
                base_sig = self._get_base_signal(read_alignment, genomic_pos)
                insertions_sig = self._get_insertions_signal(
                    read_alignment, genomic_pos
                )
                if base_sig is None:
                    continue

                x0 = pos_idx
                x1 = pos_idx + 1 - pad
                x_arr = np.linspace(
                    x0, x1, base_sig.shape[0] + insertions_sig.shape[0], dtype=float
                )

                x_arr_base = x_arr[: base_sig.shape[0]]
                matched_x.append(x_arr_base)
                matched_y.append(base_sig)
                # break between positions
                matched_x.append(np.array([np.nan], dtype=float))
                matched_y.append(np.array([np.nan], dtype=float))

                x_arr_insertions = x_arr[base_sig.shape[0] :]
                insertions_x.append(x_arr_base[-1:])
                insertions_y.append(base_sig[-1:])

                insertions_x.append(x_arr_insertions)
                insertions_y.append(insertions_sig)
                # break between positions
                insertions_x.append(np.array([np.nan], dtype=float))
                insertions_y.append(np.array([np.nan], dtype=float))

            if matched_x:
                all_x = np.concatenate(matched_x)
                all_y = np.concatenate(matched_y)

                self.fig.add_trace(
                    self._plot_func(
                        x=all_x,
                        y=all_y,
                        mode="lines",
                        name=condition.label,
                        legendgroup=condition.label,
                        meta={"cond": condition.label, "kind": "read"},
                        showlegend=False,  # keep legend clean
                        line=dict(color=col, width=lw, dash=ls),
                        opacity=alp,
                        hovertemplate="Position: %{x:.2f}<br>Signal: %{y:.1f} pA<extra></extra>",
                    )
                )

            if insertions_x:
                all_x = np.concatenate(insertions_x)
                all_y = np.concatenate(insertions_y)

                self.fig.add_trace(
                    self._plot_func(
                        x=all_x,
                        y=all_y,
                        mode="lines",
                        name=condition.label,
                        legendgroup=condition.label,
                        meta={"cond": condition.label, "kind": "read"},
                        showlegend=False,  # keep legend clean
                        line=dict(color=col, width=lw, dash="dot"),
                        opacity=alp,
                        hovertemplate="Position: %{x:.2f}<br>Signal: %{y:.1f} pA<extra></extra>",
                    )
                )

        # one legend entry per condition
        if self.style.show_legend:
            self.fig.add_trace(
                self._plot_func(
                    x=[np.nan],
                    y=[np.nan],
                    mode="lines",
                    name=condition.label,
                    legendgroup=condition.label,
                    meta={"cond": condition.label, "kind": "legend"},
                    showlegend=True,
                    line=dict(color=col, width=lw, dash=ls),
                    opacity=1.0,
                    hoverinfo="skip",
                )
            )

    def _update_global_ylim(self):
        """Update global y-axis limits based on all plotted conditions."""
        if not self._auto_ylim:
            return

        ys = []
        for tr in self.fig.data:
            arr = np.asarray(getattr(tr, "y", []), dtype=float)
            if arr.size:
                arr = arr[np.isfinite(arr)]
                if arr.size:
                    ys.extend(arr)
        if not ys:
            return
        ymin, ymax = float(np.min(ys)), float(np.max(ys))
        pad = max(1e-6, (ymax - ymin) * 0.05)
        self.logger.debug(f"Updating y-axis limits to [{ymin - pad}, {ymax + pad}]")
        self.fig.update_yaxes(range=[ymin - pad, ymax + pad])

    def remove_condition(self, label: str) -> bool:
        """Remove a specific condition from the plot."""
        if label not in self._conditions_info:
            self.logger.warning(f"Condition '{label}' not found in plot")
            return False

        self.logger.info(f"Removing condition '{label}' from plot")

        # Remove traces
        kept = []
        for tr in self.fig.data:
            if getattr(tr, "meta", {}).get("cond") != label:
                kept.append(tr)
        self.fig.data = tuple(kept)

        # Remove from plotted conditions
        self._conditions_info.pop(label, None)

        # Update y-axis limits
        self._update_global_ylim()

        # Update position labels
        if not self.window_labels:
            self._update_position_labels()

        return True

    def clear_conditions(self) -> "SignalVisualizer":
        """Remove all plotted conditions."""
        self.logger.info("Clearing all conditions from plot")

        # Clear all traces
        self.fig.data = tuple()

        # Clear the map
        self._conditions_info.clear()

        # Update position labels
        if not self.window_labels:
            self._update_position_labels()

        return self

    def set_auto_ylim(self, enabled: bool = True) -> "SignalVisualizer":
        """Enable or disable automatic y-axis limit adjustment."""
        self._auto_ylim = enabled
        if enabled:
            self._update_global_ylim()
        return self

    def highlight_position(
        self, window_idx: Optional[int] = None, color: str = "red", alpha: float = 0.2
    ) -> "SignalVisualizer":
        """Highlight a position in the window."""
        if window_idx is None:
            window_idx = self.K // 2

        self.logger.debug(f"Highlighting position {window_idx}")

        # Create unique identifier for the shape
        uid = f"user_highlight_{len(self._highlight_shapes)}"

        # Add highlight as a shape
        shape = dict(
            type="rect",
            x0=window_idx - self.style.positions_padding / 2,  # Using 0.025 as default padding
            x1=window_idx + 1 - self.style.positions_padding / 2,
            y0=0,
            y1=1,
            yref="paper",
            fillcolor=color,
            opacity=alpha,
            line=dict(width=0),
            layer="below",
            name=uid,
        )

        self.fig.add_shape(**shape)

        # Store the index of the shape
        self._highlight_shapes.append(uid)

        return self

    def clear_highlights(self):
        """Remove all position highlights."""
        # Filter out our highlights
        keep = [
            shape
            for shape in self.fig.layout.shapes
            if not (hasattr(shape, "name") and shape.name in self._highlight_shapes)
        ]
        self.fig.layout.shapes = tuple(keep)
        self._highlight_shapes.clear()

    def add_annotation(
        self,
        window_idx: int,
        text: str,
        color: str = "rgba(255, 255, 0, 0.7)",
        fontsize: int = None,
        fontcolor: str = None,
        y_position: Optional[float] = None,
        **kwargs,
    ) -> "SignalVisualizer":
        """Add text annotation at a specific position."""
        if window_idx is None:
            window_idx = self.K // 2

        x_pos = window_idx + 0.5 - self.style.positions_padding / 2
        fontcolor = fontcolor or get_contrasting_color(color)
        if y_position is None:
            # Get current y range
            y_range = self.fig.layout.yaxis.range
            if y_range:
                y_position = y_range[1] * 0.95
            else:
                y_position = 100  # Default

        self.logger.debug(f"Adding annotation '{text}' at position {x_pos}")

        # Create unique identifier for the annotation
        uid = f"user_annotation_{len(self._annotation_indices)}"

        # Add a custom attribute to identify our annotations
        annotation = dict(
            x=x_pos,
            y=y_position,
            text=text,
            showarrow=False,
            font=dict(
                size=fontsize or self.style.annotation_font_size, color=fontcolor
            ),
            bgcolor=color,
            borderpad=4,
            name=uid,
            **kwargs,
        )

        self.fig.add_annotation(**annotation)

        # Store the index of the annotation
        self._annotation_indices.append(uid)

        return self

    def clear_annotations(self) -> "SignalVisualizer":
        """Remove all annotations."""
        # Filter out our annotations
        keep = [
            ann
            for ann in self.fig.layout.annotations
            if not (hasattr(ann, "name") and ann.name in self._annotation_indices)
        ]
        self.fig.layout.annotations = tuple(keep)
        self._annotation_indices.clear()
        return self

    def set_title(self, title: str) -> "SignalVisualizer":
        """Set or update the plot title."""
        self.logger.debug(f"Setting plot title: '{title}'")
        self.title = title
        self.fig.update_layout(
            title={
                "text": title,
                "font": {"size": self.style.title_font_size},
                "x": 0.5,
                "xanchor": "center",
            }
        )
        return self

    def set_ylim(
        self, bottom: Optional[float] = None, top: Optional[float] = None
    ) -> "SignalVisualizer":
        """Set y-axis limits manually (disables auto ylim)."""
        self.logger.debug(f"Setting y-axis limits: bottom={bottom}, top={top}")
        self._auto_ylim = False  # Disable auto adjustment when manually setting limits
        # derive current if needed
        curr_lo, curr_hi = (
            list(self.fig.layout.yaxis.range)
            if self.fig.layout.yaxis.range
            else [None, None]
        )
        lo = bottom if bottom is not None else curr_lo
        hi = top if top is not None else curr_hi

        # If still None (e.g., first call), compute from plotted data
        if lo is None or hi is None:
            ys = []
            for tr in self.fig.data:
                if hasattr(tr, "y") and tr.y is not None:
                    ys.extend([v for v in tr.y if isinstance(v, (int, float))])
            if ys:
                ymin, ymax = float(np.nanmin(ys)), float(np.nanmax(ys))
                pad = max(1e-6, (ymax - ymin) * 0.05)
                lo = ymin - pad if lo is None else lo
                hi = ymax + pad if hi is None else hi

        if lo is not None and hi is not None:
            self.fig.update_yaxes(range=[lo, hi])
        return self

    def reset_view(self) -> "SignalVisualizer":
        """Reset the view to default."""
        self.logger.info("Resetting view to default")

        # Clear highlights and annotations
        self.clear_highlights()
        self.clear_annotations()

        # Re-enable auto ylim and update
        self._auto_ylim = True
        self._update_global_ylim()

        # Reset x-axis
        self.fig.update_xaxes(range=[-0.1, self.K - self.style.positions_padding + 0.1])

        return self

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
                    "width": self.style.width,
                    "height": self.style.height,
                }
                write_kwargs.update(kwargs)
                self.fig.write_image(str(path), **write_kwargs)

            self.logger.info(f"Saved figure to {path}")
        except Exception as e:
            self.logger.error(f"Failed to save figure: {type(e).__name__}: {str(e)}")
            raise e

    def get_plotted_labels(self) -> List[str]:
        """Get list of currently plotted condition labels."""
        return list(self._conditions_info.keys())

    def has_condition(self, label: str) -> bool:
        """Check if a condition is currently plotted."""
        return label in self._conditions_info

    def _extract_reference_bases(
        self, positions: List[int], reads: List[ReadAlignment]
    ) -> Dict[int, str]:
        """Extract reference bases from reads."""
        self.logger.debug(f"Extracting reference bases for {len(positions)} positions")

        kmer_dict = {position: "_" for position in positions}
        rem = len(kmer_dict)

        for read_alignment in reads:
            for aligned_base in read_alignment.aligned_bases:
                if aligned_base.reference_pos in positions:
                    if kmer_dict[aligned_base.reference_pos] == "_":
                        if aligned_base.reference_base is not None:
                            kmer_dict[aligned_base.reference_pos] = (
                                aligned_base.reference_base.upper()
                            )
                        else:
                            kmer_dict[aligned_base.reference_pos] = "*"
                        rem -= 1

            if rem == 0:
                break

        return kmer_dict

    def _update_position_labels(self):
        """Update x-axis labels based on plotted conditions."""
        self.logger.debug("Updating position labels")

        tick_positions = np.arange(self.K) + 0.5 - self.style.positions_padding / 2

        if not self._conditions_info:
            # Default labels
            tick_text = (
                [str(i) for i in range(self.K)]
                if not self.window_labels
                else [str(l) for l in self.window_labels]
            )
        elif len(self._conditions_info) == 1:
            # Single condition labels
            label = next(iter(self._conditions_info))
            tick_text = (
                self._conditions_info.get(label, {}).get("pos_labels")
                or [str(i) for i in range(self.K)]
            )
        else:
            # Multiple conditions - create multi-line labels
            tick_text = []
            for i in range(self.K):
                lines = []
                for label, cond_info_dict in self._conditions_info.items():
                    color = cond_info_dict["color"]
                    pos_labels = cond_info_dict["pos_labels"]
                    # if cache missing, fallback gracefully
                    text = pos_labels[i] if pos_labels else str(i)
                    lines.append(f"<span style='color:{color}'>{text}</span>")
                tick_text.append("<br>".join(lines))

        self.fig.update_xaxes(
            tickmode="array", tickvals=tick_positions, ticktext=tick_text
        )
