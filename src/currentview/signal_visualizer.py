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

@dataclass
class PlottedCondition:
    """Track information about each plotted group."""
    condition: Condition
    position_labels: List[str]
    trace_indices: List[int] = field(default_factory=list)
    y_min: float = field(default=float('inf'))
    y_max: float = field(default=float('-inf'))

class SignalVisualizer:
    """Handles all plotting, visualization, and figure management using Plotly."""
    
    def __init__(self,
                 K: int,
                 window_labels: Optional[List[Union[str, int]]] = None,
                 plot_style: Optional[PlotStyle] = None,
                 title: Optional[str] = None,
                 logger: Optional[logging.Logger] = None):
        """
        Initialize the visualizer.
        
        Args:
            K: Number of bases to show
            window_labels: Optional custom labels for x-axis
            plot_style: Optional PlotStyle configuration
            title: Optional custom title
            width: Optional figure width in pixels
            height: Optional figure height in pixels
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        self.logger.debug(f"Initializing SignalVisualizer with K={K}")
        
        self.K = K
        self.window_labels = window_labels
        
        # Setup style
        self.style = plot_style or PlotStyle()
        
        if self.style.renderer=='SVG':
            self._plot_func = go.Scatter
        elif self.style.renderer=='WebGL':
            self._plot_func = go.Scattergl
        
        # Store initial title
        self.title = title or 'Nanopore Signal Visualization'
        
        # Initialize color palette
        self.color_sequence = self.style.get_color_sequence()
        
        # Create figure
        self.logger.debug(f"Creating Plotly figure")
        self._create_figure()
        
        # Add position barriers
        self.logger.debug("Adding position barriers")
        self._add_position_barriers()
        
        # Track plotting state
        self._plot_count = 0
        self._plotted_conditions_map: Dict[str, PlottedCondition] = OrderedDict()
        
        # Store color assignments
        self._color_assignments: Dict[str, str] = {}
        
        # Store additional plot elements
        self._highlight_shapes = []
        self._annotation_indices = []
        
        # Track global y-axis limits
        self._global_y_min = float('inf')
        self._global_y_max = float('-inf')
        self._auto_ylim = True  # Flag to enable/disable auto y-axis adjustment
        
        self.logger.info(f"Initialized SignalVisualizer with K={K}")
    
    def _create_figure(self):
        """Create and configure the Plotly figure."""
        self.logger.debug("Creating Plotly figure")
        
        self.fig = go.Figure()
        
        # Apply style
        layout_dict = self.style.get_layout_dict()
        if 'title' not in layout_dict:
            layout_dict['title'] = {}
        layout_dict['title'].update({
            'text': self.title,
            'x': 0.5,
            'xanchor': 'center'
        })
        # Preserve font settings from style if they exist
        if 'font' not in layout_dict['title']:
            layout_dict['title']['font'] = {'size': self.style.title_font_size}
        
        # Merge xaxis settings
        if 'xaxis' not in layout_dict:
            layout_dict['xaxis'] = {}
        layout_dict['xaxis'].update({
            'title': 'Genomic Position',
            'showgrid': False,
            'tickmode': 'array',
            'tickvals': [],
            'ticktext': [],
            'range': [-0.1, self.K - 0.025 + 0.1]  # Using 0.025 as default padding
        })
        
        # Merge yaxis settings
        if 'yaxis' not in layout_dict:
            layout_dict['yaxis'] = {}
        layout_dict['yaxis'].update({
            'title': 'Signal (pA)'
        })
        
        self.fig.update_layout(**layout_dict)
        
        # Apply custom labels if provided
        if self.window_labels:
            self._apply_custom_labels()
    
    def _add_position_barriers(self):
        """Add vertical lines to separate positions."""
        self.logger.debug(f"Adding {self.K + 1} position barriers")
        
        # Add vertical lines as shapes
        for i in range(self.K + 1):
            x_pos = i - self.style.padding / 2  # Using 0.025 as default padding
            
            self.fig.add_shape(
                type="line",
                x0=x_pos, x1=x_pos,
                y0=0, y1=1,
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
        
        tick_positions = np.arange(self.K) + 0.5 - self.style.padding / 2
        
        self.fig.update_xaxes(
            tickmode='array',
            tickvals=tick_positions,
            ticktext=[str(label) for label in self.window_labels]
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
        
        self.logger.debug(f"plot_condition called: label='{label}', n_reads={len(reads)}")
        
        # Check if condition already plotted
        if label in self._plotted_conditions_map:
            self.logger.warning(f"Condition '{label}' already plotted. Updating it.")
            self.remove_condition(label)
        
        # Assign color if not specified
        if color is None:
            if label in self._color_assignments:
                color = self._color_assignments[label]
            else:
                color = self._get_next_color()
                self._color_assignments[label] = color
            condition.color = color
        else:
            self._color_assignments[label] = color
        
        # Calculate opacity if not specified
        if opacity is None:
            if self.style.opacity_mode == 'fixed':
                opacity = self.style.fixed_opacity
            elif self.style.opacity_mode == 'auto':
                opacity = self._calculate_opacity(len(reads))
            condition.alpha = opacity
        
        # Extract reference bases
        self.logger.debug("Extracting reference bases")
        kmer_dict = self._extract_reference_bases(positions, reads)
        position_labels = [f"{pos} - {kmer_dict[pos]}" for pos in positions]
        
        line_style = line_style or self.style.line_style
        condition.line_style = line_style
        
        # Use style defaults
        line_width = line_width or self.style.line_width
        condition.line_width = line_width
        
        # Plot the signals and get y-axis bounds
        self.logger.info(f"Plotting {len(reads)} reads for condition '{label}'")
        trace_indices, y_min, y_max = self._plot_signals(condition)
        
        # Store plotted condition with y-axis bounds
        plotted_condition = PlottedCondition(
            condition=condition,
            position_labels=position_labels,
            trace_indices=trace_indices,
            y_min=y_min,
            y_max=y_max
        )
        self._plotted_conditions_map[label] = plotted_condition
        
        # Update global y-axis limits
        self._update_global_ylim()
        
        # Update position labels
        if not self.window_labels:
            self._update_position_labels()
        
        self._plot_count += 1
    
    def _plot_signals(self, condition: Condition) -> Tuple[List[int], float, float]:
        """Plot signals and return trace indices and y-axis bounds."""
        trace_indices = []
        
        # Combine all signals for this condition
        all_x = []
        all_y = []
        
        # Track min/max for this condition
        condition_y_min = float('inf')
        condition_y_max = float('-inf')
        
        # Plot each read
        for read_idx, read_alignment in enumerate(condition.reads):
            bases_dict = read_alignment.bases_by_ref_pos
            
            # Plot signal for each position
            for pos_idx, genomic_pos in enumerate(condition.positions):
                if genomic_pos in bases_dict and bases_dict[genomic_pos].has_signal:
                    base = bases_dict[genomic_pos]
                    signal = base.signal
                    
                    if read_alignment.is_reversed:
                        signal = signal[::-1]
                    
                    # Update condition's y-axis bounds
                    if len(signal) > 0:
                        condition_y_min = min(condition_y_min, np.min(signal))
                        condition_y_max = max(condition_y_max, np.max(signal))
                    
                    # Calculate x-coordinates
                    signal_length = len(signal)
                    x_start = pos_idx
                    x_end = pos_idx + 1 - self.style.padding
                    x_coords = np.linspace(x_start, x_end, signal_length)
                    
                    # Add to combined data
                    all_x.extend(x_coords)
                    all_y.extend(signal)
                    
                    # Add None to create line breaks between segments
                    all_x.append(None)
                    all_y.append(None)
        
        # Add single trace for all signals of this condition
        if all_x:
            show_legend = self.style.show_legend
            
            # Create the main trace with the actual opacity
            self.fig.add_trace(
                self._plot_func(
                    x=all_x,
                    y=all_y,
                    mode='lines',
                    name=condition.label,
                    line=dict(
                        color=condition.color,
                        width=condition.line_width,
                        dash=condition.line_style
                    ),
                    opacity=condition.alpha,
                    showlegend=False,  # Hide this trace from legend
                    legendgroup=condition.label,
                    hovertemplate='Position: %{x:.2f}<br>Signal: %{y:.1f} pA<extra></extra>'
                )
            )
            
            trace_indices.append(len(self.fig.data) - 1)
            
            # Add a dummy trace just for the legend with full opacity
            if show_legend:
                self.fig.add_trace(
                    self._plot_func(
                        x=[None],  # No actual data points
                        y=[None],
                        mode='lines',
                        name=condition.label,
                        line=dict(
                            color=condition.color,
                            width=condition.line_width,
                            dash=condition.line_style
                        ),
                        opacity=1.0,  # Full opacity in legend
                        showlegend=True,
                        legendgroup=condition.label,
                        hoverinfo='skip'  # No hover for dummy trace
                    )
                )
                
                trace_indices.append(len(self.fig.data) - 1)
        
        # Handle case where no valid signals were found
        if condition_y_min == float('inf'):
            condition_y_min = 0
            condition_y_max = 100
        
        return trace_indices, condition_y_min, condition_y_max
    
    def _update_global_ylim(self):
        """Update global y-axis limits based on all plotted conditions."""
        if not self._auto_ylim:
            return
        
        # Reset global limits
        self._global_y_min = float('inf')
        self._global_y_max = float('-inf')
        
        # Find min/max across all conditions
        for plotted_condition in self._plotted_conditions_map.values():
            self._global_y_min = min(self._global_y_min, plotted_condition.y_min)
            self._global_y_max = max(self._global_y_max, plotted_condition.y_max)
        
        # Add some padding (5% on each side)
        if self._global_y_min != float('inf') and self._global_y_max != float('-inf'):
            y_range = self._global_y_max - self._global_y_min
            padding = y_range * 0.05
            
            self.logger.debug(f"Updating y-axis limits: [{self._global_y_min - padding:.1f}, {self._global_y_max + padding:.1f}]")
            
            self.fig.update_yaxes(range=[self._global_y_min - padding, self._global_y_max + padding])
    
    def remove_condition(self, label: str) -> bool:
        """Remove a specific condition from the plot."""
        if label not in self._plotted_conditions_map:
            self.logger.warning(f"Condition '{label}' not found in plot")
            return False
        
        self.logger.info(f"Removing condition '{label}' from plot")
        
        # Get the condition
        condition = self._plotted_conditions_map[label]
        
        # Remove traces
        for idx in sorted(condition.trace_indices, reverse=True):
            if idx < len(self.fig.data):
                self.fig.data = self.fig.data[:idx] + self.fig.data[idx+1:]
        
        # Remove from plotted conditions
        del self._plotted_conditions_map[label]
        
        # Update trace indices for remaining conditions
        self._update_trace_indices()
        
        # Update y-axis limits
        self._update_global_ylim()
        
        # Update position labels
        if not self.window_labels:
            self._update_position_labels()
        
        return True
    
    def _update_trace_indices(self):
        """Update trace indices after removal."""
        current_idx = 0
        for condition in self._plotted_conditions_map.values():
            new_indices = []
            for _ in condition.trace_indices:
                new_indices.append(current_idx)
                current_idx += 1
            condition.trace_indices = new_indices
    
    def clear_conditions(self):
        """Remove all plotted conditions."""
        self.logger.info("Clearing all conditions from plot")
        
        # Clear all traces
        self.fig.data = []
        
        # Clear the map
        self._plotted_conditions_map.clear()
        
        # Reset plot count
        self._plot_count = 0
        
        # Reset y-axis limits
        self._global_y_min = float('inf')
        self._global_y_max = float('-inf')
        
        # Update position labels
        if not self.window_labels:
            self._update_position_labels()
    
    def set_auto_ylim(self, enabled: bool = True) -> 'SignalVisualizer':
        """Enable or disable automatic y-axis limit adjustment."""
        self._auto_ylim = enabled
        if enabled:
            self._update_global_ylim()
        return self
    
    def highlight_position(self, window_idx: Optional[int] = None,
                        color: str = 'red',
                        opacity: float = 0.2) -> 'SignalVisualizer':
        """Highlight a position in the window."""
        if window_idx is None:
            window_idx = self.K // 2
        
        self.logger.debug(f"Highlighting position {window_idx}")
        
        # Add highlight as a shape
        shape = dict(
            type="rect",
            x0=window_idx - self.style.padding / 2,  # Using 0.025 as default padding
            x1=window_idx + 1 - self.style.padding / 2,
            y0=0,
            y1=1,
            yref="paper",
            fillcolor=color,
            opacity=opacity,
            line=dict(width=0),
            layer="below",
            name=f"user_highlight_{len(self._highlight_shapes)}",  # Custom identifier
        )
        
        self.fig.add_shape(**shape)
        
        # Store the index of the shape 
        self._highlight_shapes.append(shape['name'])
        
        return self

    def clear_highlights(self):
        """Remove all position highlights."""
        # Filter out our annotations
        new_shapes = [
            ann for ann in self.fig.layout.shapes 
            if not (hasattr(ann, 'name') and ann.name in self._highlight_shapes)
        ]
        self.fig.layout.shapes = new_shapes
        self._annotation_indices.clear()
    
    def add_annotation(self, window_idx: int, text: str,
                    y_position: Optional[float] = None,
                    **kwargs) -> 'SignalVisualizer':
        """Add text annotation at a specific position."""
        if window_idx is None:
            window_idx = self.K // 2
        
        x_pos = window_idx + 0.5 - self.style.padding / 2
        
        if y_position is None:
            # Get current y range
            y_range = self.fig.layout.yaxis.range
            if y_range:
                y_position = y_range[1] * 0.95
            else:
                y_position = 100  # Default
        
        self.logger.debug(f"Adding annotation '{text}' at position {x_pos}")
        
        # Add a custom attribute to identify our annotations
        annotation = dict(
            x=x_pos,
            y=y_position,
            text=text,
            showarrow=False,
            font=dict(size=self.style.annotation_font_size),
            bgcolor="rgba(255, 255, 0, 0.7)",
            borderpad=4,
            name=f"user_annotation_{len(self._annotation_indices)}",  # Custom identifier
            **kwargs
        )
        
        self.fig.add_annotation(**annotation)
        self._annotation_indices.append(annotation['name'])
        
        return self

    def clear_annotations(self):
        """Remove all annotations."""
        # Filter out our annotations
        new_annotations = [
            ann for ann in self.fig.layout.annotations 
            if not (hasattr(ann, 'name') and ann.name in self._annotation_indices)
        ]
        self.fig.layout.annotations = new_annotations
        self._annotation_indices.clear()
    
    def set_title(self, title: str) -> 'SignalVisualizer':
        """Set or update the plot title."""
        self.logger.debug(f"Setting plot title: '{title}'")
        self.title = title
        self.fig.update_layout(
            title={
                'text': title,
                'font': {'size': self.style.title_font_size},
                'x': 0.5,
                'xanchor': 'center'
            }
        )
        return self
    
    def set_ylim(self, bottom: Optional[float] = None,
                 top: Optional[float] = None) -> 'SignalVisualizer':
        """Set y-axis limits manually (disables auto ylim)."""
        self.logger.debug(f"Setting y-axis limits: bottom={bottom}, top={top}")
        self._auto_ylim = False  # Disable auto adjustment when manually setting limits
        self.fig.update_yaxes(range=[bottom, top])
        return self
    
    def reset_view(self):
        """Reset the view to default."""
        self.logger.info("Resetting view to default")
        
        # Clear highlights and annotations
        self.clear_highlights()
        self.clear_annotations()
        
        # Re-enable auto ylim and update
        self._auto_ylim = True
        self._update_global_ylim()
        
        # Reset x-axis
        self.fig.update_xaxes(range=[-0.1, self.K - 0.025 + 0.1])
    
    def show(self):
        """Display the plot."""
        self.logger.info("Displaying plot")
        self.fig.show()
    
    def save(self, path: Union[str, Path], format: Optional[str] = None,
             scale: Optional[float] = None, **kwargs):
        """Save the figure to file."""
        path = Path(path)
        
        if format is None:
            format = path.suffix.lstrip('.').lower() or 'png'
        
        self.logger.debug(f"Saving figure: path={path}, format={format}")
        
        try:
            if format == 'html':
                self.fig.write_html(str(path), **kwargs)
            else:
                write_kwargs = {
                    'format': format,
                    'scale': scale or self.style.toImageButtonOptions.get('scale', 2)
                }
                write_kwargs.update(kwargs)
                self.fig.write_image(str(path), **write_kwargs)
            
            self.logger.info(f"Saved figure to {path}")
        except Exception as e:
            self.logger.error(f"Failed to save figure: {type(e).__name__}: {str(e)}")
            raise e
    
    def get_plotted_labels(self) -> List[str]:
        """Get list of currently plotted condition labels."""
        return list(self._plotted_conditions_map.keys())
    
    def has_condition(self, label: str) -> bool:
        """Check if a condition is currently plotted."""
        return label in self._plotted_conditions_map
    
    def _get_next_color(self) -> str:
        """Get the next color from the palette."""
        color_index = len(self._color_assignments) % len(self.color_sequence)
        return self.color_sequence[color_index]
    
    def _extract_reference_bases(self, positions: List[int],
                                reads: List[ReadAlignment]) -> Dict[int, str]:
        """Extract reference bases from reads."""
        self.logger.debug(f"Extracting reference bases for {len(positions)} positions")
        
        kmer_dict = {position: '_' for position in positions}
        rem = len(kmer_dict)
        
        for read_alignment in reads:
            for aligned_base in read_alignment.aligned_bases:
                if aligned_base.reference_pos in positions:
                    if kmer_dict[aligned_base.reference_pos] == '_':
                        kmer_dict[aligned_base.reference_pos] = aligned_base.reference_base.upper()
                        rem-=1
            
            if rem==0:
                break
        
        return kmer_dict
    
    def _update_position_labels(self):
        """Update x-axis labels based on plotted conditions."""
        self.logger.debug("Updating position labels")
        
        plotted_conditions = list(self._plotted_conditions_map.values())
        n_conditions = len(plotted_conditions)
        
        tick_positions = np.arange(self.K) + 0.5 - self.style.padding / 2
        
        if n_conditions == 0:
            # Default labels
            tick_text = [str(i) for i in range(self.K)]
        elif n_conditions == 1:
            # Single condition labels
            tick_text = plotted_conditions[0].position_labels
        else:
            # Multiple conditions - create multi-line labels
            tick_text = []
            for i in range(self.K):
                labels = []
                for cond in plotted_conditions:
                    color = cond.condition.color
                    label = cond.position_labels[i]
                    labels.append(f"<span style='color:{color}'>{label}</span>")
                tick_text.append("<br>".join(labels))
        
        self.fig.update_xaxes(
            tickmode='array',
            tickvals=tick_positions,
            ticktext=tick_text
        )
    
    def _calculate_opacity(self, n_reads: int) -> float:
        """Calculate appropriate opacity value."""
        if n_reads <= 1:
            opacity = 1.0
        elif n_reads <= 3:
            opacity = 0.9
        elif n_reads <= 10:
            opacity = 0.6
        elif n_reads <= 50:
            opacity = 0.4
        elif n_reads <= 100:
            opacity = 0.3
        else:
            opacity = 0.2
        
        self.logger.debug(f"Calculated opacity={opacity:.2f} for {n_reads} reads")
        return opacity