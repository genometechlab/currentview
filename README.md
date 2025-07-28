# Current View

A Python package for visualizing nanopore sequencing signals at specific genomic positions. This tool enables researchers to plot and compare signal patterns from POD5 files aligned to reference genomes via BAM files.

## Features

- **Signal Visualization**: Plot nanopore signals from POD5 files at specific genomic positions
- **Multi-condition Comparison**: Overlay multiple conditions/samples for direct comparison

## Table of Contents
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Core API](#core-api)
  - [GenomicPositionVisualizer](#genomicpositionvisualizer)
  - [Styling and Customization using PlotStyle](#styling-and-customization-using-plotstyle)
- [Practical considerations](#practical-considerations)

## Installation

```bash
git clone https://github.com/genometechlab/current-view.git
cd kmer-visualizer
pip install -e .
```

### Dependencies
- numpy >= 1.20.0
- matplotlib >= 3.5.0
- pysam >= 0.19.0 (for BAM file reading)
- pod5 >= 0.2.0 (for POD5 file reading)

## Quick Start

```python
from currentview import GenomicPositionVisualizer, PlotStyle

# Create visualizer for a 9-base window
viz = GenomicPositionVisualizer(K=9, stats=['mean', ...])

# Plot signals from a genomic position
viz.add_condition(
    bam_path="sample1.bam",
    pod5_path="sample1.pod5",
    contig="chr1",
    target_position=1000000,
    label="Control"
)

# Add another condition for comparison
viz.add_condition(
    bam_path="sample2.bam",
    pod5_path="sample2.pod5",
    contig="chr1",
    target_position=1000000,
    label="Treatment",
    color="red"
)

# Display the signal plot
viz.show_signals()

# Display the stat plot
viz.show_stats()
```

## Core API

### GenomicPositionVisualizer

The main class that initiate the visualization.

```python
GenomicPositionVisualizer(
    K: int = 9,
    kmer: Optional[List[Union[str, int]]] = None,
    plot_style: Optional[PlotStyle] = None,
    title: Optional[str] = None,
    figsize: Optional[Tuple[float, float]] = None,
    verbosity: VerbosityLevel = VerbosityLevel.SILENT,
    logger: Optional[logging.Logger] = None
)
```

**Parameters:**
- `K`: Window size (will be made odd if even). Default: 9
- `kmer`: Optional custom k-mer labels for x-axis. Should be an iterable with size `K`
- `plot_style`: PlotStyle object for customization. Please refer to `PlotStyle` section
- `title`: Plot title
- `figsize`: Figure size (width, height) in inches
- `verbosity`: Logging level (0-4):
  - 0 = SILENT: No output
  - 1 = ERROR: Only errors
  - 2 = WARNING: Errors and warnings
  - 3 = INFO: Errors, warnings, and info
  - 4 = DEBUG: Everything including debug messages
- `logger`: Optional custom logger instance

#### Main Methods

##### plot_condition()

Plot reads from specified BAM and POD5 files at a genomic position.

```python
viz.plot_condition(
    bam_path: Union[str, Path],
    pod5_path: Union[str, Path],
    contig: str,
    target_position: int,
    read_ids: Optional[Union[Set[str], List[str]]] = None,
    max_reads: Optional[int] = None,
    exclude_reads_with_indels: bool = False,
    label: Optional[str] = None,
    color: Optional[Union[str, Tuple[float, float, float]]] = None,
    alpha: Optional[float] = None,
    line_width: Optional[float] = None,
    line_style: Optional[str] = None
) -> GenomicPositionVisualizer
```

**Parameters:**
- `bam_path`: Path to BAM alignment file (Required) 
- `pod5_path`: Path to POD5 signal file (Required) 
- `contig`: Chromosome/contig name (e.g., "chr1") (Required) 
- `target_position`: 0-based reference genomic position (Required)
- `target_base`: Required read base matched to the reference target position (Default: None - tollkot doesn't care about the base matched to target position)
- `read_ids`: Specific read IDs to include (default: None - fetched all aligned reads)
- `max_reads`: Maximum number of reads to plot(default: None - No limitation of the fetched reads)
- `exclude_reads_with_indels`: Skip reads with insertions/deletions (default: False)
- `label`: Condition label for legend (default: {contig}:{target-position})
- `color`: Line color (matplotlib color) (default: style.color_scheme - please refer to plot style below)
- `alpha`: Line transparency (0-1) (default: based on style.alpha_mode - please refer to plot style below)
- `line_width`: Line thickness (default: style.line_width - please refer to plot style below)
- `line_style`: Line style ('-', '--', ':', etc.) (default: style.line_style - please refer to plot style below)

#### Other Methods

```python
# Highlight a position in the window
viz.highlight_position(window_idx=4, color='red', alpha=0.2)

# Add text annotation
viz.add_annotation(window_idx=4, text="SNP", y_position=150)

# Set plot title
viz.set_title("Nanopore Signal Comparison at chr1:1000000")

# Set y-axis limits
viz.set_ylim(bottom=50, top=200)

# Show interactive plot
viz.show()

# Save to file
viz.save("output.png", dpi=300)
viz.save("output.pdf", dpi=300)

# Get summary statistics
summary = viz.get_summary()
viz.print_summary()

# Change verbosity
viz.set_verbosity(3)  # Set to INFO level
```

### Styling and Customization using PlotStyle

The appearance of plots can be extensively customized using the `PlotStyle` class:

```python
from genomic_position_visualizer.utils.visualization_utils import PlotStyle, ColorScheme

# Create custom style
style = PlotStyle(
    figsize=(12, 8),
    dpi=300,  # High resolution
    line_width=1.5,
    show_grid=True,
    grid_alpha=0.3,
    color_scheme=ColorScheme.COLORBLIND,
    title_fontsize=16,
    label_fontsize=14,
    show_legend=True
)

viz = GenomicPositionVisualizer(K=9, plot_style=style)
```

#### Available PlotStyle Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| **Figure Settings** | | | |
| `figsize` | tuple | (12, 8) | Figure size in inches (width, height) |
| `dpi` | int | 100 | Resolution (dots per inch) |
| `padding` | float | 0.025 | Padding between genomic positions |
| **Line Styling** | | | |
| `line_width` | float | 1.0 | Default line thickness |
| `line_style` | str | '-' | Default line style ('-', '--', ':', '-.') |
| `alpha_mode` | 'auto'/'fixed' | 'auto' | Alpha calculation mode ('Auto': based on the number of plotted reads, 'fixed': fixed value provided via `fixed_alpha`) |
| `fixed_alpha` | float | 0.8 | Alpha value when mode is 'fixed' |
| **Grid and Axes** | | | |
| `show_grid` | bool | False | Show background grid |
| `grid_alpha` | float | 0.3 | Grid line transparency |
| `show_spines` | list | ['left', 'bottom'] | Which plot borders to show |
| **Position Barriers** | | | |
| `position_barrier_color` | str | 'gray' | Color of vertical position separators |
| `position_barrier_style` | str | '--' | Line style for position barriers |
| `position_barrier_alpha` | float | 0.3 | Transparency of position barriers |
| **Colors** | | | |
| `color_scheme` | ColorScheme | DEFAULT | Color palette for multiple conditions |
| **Text and Labels** | | | |
| `title_fontsize` | int | 14 | Plot title font size |
| `label_fontsize` | int | 12 | Axis label font size |
| `tick_labelsize` | int | 10 | Tick label font size |
| **Legend** | | | |
| `show_legend` | bool | True | Display legend |
| `legend_location` | str | 'best' | Legend position (currently not used) |
| `legend_fontsize` | int | 10 | Legend text font size |
| **X-axis Label Positioning** | | | |
| `xtick_label_y_start` | float | -0.02 | Starting y-position for x-tick labels |
| `xtick_label_row_spacing` | float | -0.03 | Spacing between stacked label rows |
| `xlabel_margin_base` | float | 20.0 | Base margin between tick labels and x-label |
| `xlabel_margin_per_row` | float | 15.0 | Additional margin per row of stacked labels |

##### Color Schemes

Available color schemes via `ColorScheme` enum:
- `DEFAULT`: General purpose (matplotlib 'tab10')
- `COLORBLIND`: Optimized for color vision deficiency (same as DEFAULT)
- `VIRIDIS`, `PLASMA`, `INFERNO`: Sequential, perceptually uniform
- `SEABORN`: Aesthetic palette (Set2)
- `CATEGORICAL`: Many distinct colors (Set3)
- `PASTEL`: Soft colors (Pastel1)
- `DARK`: High contrast colors (Dark2)

#### Examples

**Example 1: Basic Single Condition**

```python
from genomic_position_visualizer import GenomicPositionVisualizer

# Visualize a 9-base window around position 1000000
viz = GenomicPositionVisualizer(K=9, verbosity=3)  # INFO level logging

viz.plot_condition(
    bam_path="bam_1.bam",
    pod5_path="pod5_1.pod5",
    contig="chr1",
    target_position=1000000
)

viz.set_title("Nanopore Signals at chr1:1000000")
viz.show()
```

**Example 2: Comparing Multiple Conditions**

```python
# Create visualizer with custom style
style = PlotStyle(
    figsize=(14, 8),
    color_scheme=ColorScheme.CATEGORICAL,
    show_grid=True
)
viz = GenomicPositionVisualizer(K=9, plot_style=style)

# Plot multiple conditions
conditions = [
    ("bam_1.bam", "pod5_1.pod5", "contig_1", "blue"),
    ("bam_2.bam", "pod5_2.pod5", "contig_2", "blue"),
    ("bam_3.bam", "pod5_3.pod5", "contig_3", "blue"),
]

for bam, pod5, label, color in conditions:
    viz.plot_condition(
        bam_path=bam,
        pod5_path=pod5,
        contig="chr1",
        target_position=1000000,
        label=label,
        color=color,
        max_reads=50  # Limit reads for clarity
    )

# Highlight the center position
viz.highlight_position(window_idx=4, color='yellow', alpha=0.3)
viz.add_annotation(window_idx=4, text="Target", y_position=None)

viz.set_title("Signal Comparison at chr1:1000000")
viz.save("comparison.png", dpi=300)
```

**Example 3: Filtering Specific Reads**

```python
# Only plot specific reads
target_reads = ["read_001", "read_002", "read_003"]

viz = GenomicPositionVisualizer(K=11)  # 11-base window

viz.plot_condition(
    bam_path="bam_1.bam",
    pod5_path="pod5_1.pod5",
    contig="chr2",
    target_position=5000000,
    read_ids=target_reads,  # Only these reads
    exclude_reads_with_indels=True,  # Skip reads with indels
    label="Selected Reads"
)

# Get summary of what was plotted
viz.print_summary()
viz.show()
```

## Practical Considerations

### Performance Optimization

This tool will extract aligned reads to a specific genmoc position from a BAM file, and extract their corresponding read record from pod5 files.        
Both BAM and pod5 files can be large and indexing and iterating them can be computationaly expensive. It may take up to several minutes for the output to be displayed.     
For a better performance, consider:

1. **Limit reads for large datasets**:
   ```python
   viz.plot_condition(..., max_reads=100)
   ```

2. **Filter out reads with indels, since they distrupt the current**:
   ```python
   viz.plot_condition(..., exclude_reads_with_indels=True)
   ```

3. **Use appropriate verbosity**:
   ```python
   # Silent for production
   viz = GenomicPositionVisualizer(K=9, verbosity=0)
   
   # Debug for troubleshooting
   viz.set_verbosity(4)
   ```

### Visual Clarity

1. **Adjust alpha for overlapping signals**:
   ```python
   # Auto mode adjusts based on read count
   style = PlotStyle(alpha_mode='auto')
   
   # Or set manually per condition
   viz.plot_condition(..., alpha=0.5)
   ```

2. **Use contrasting colors**:
   ```python
   style = PlotStyle(color_scheme=ColorScheme.COLORBLIND)
   ```

3. **Limit window size for clarity**:
   - K=9 or K=11 work well for most cases
   - Larger windows may require bigger figures

### Common Issues

1. **No reads found at position**:
   - Verify correct contig name (e.g., "chr1" vs "1")
   - Ensure position is 0-based
   - Increase verbosity to see detailed logs

2. **Memory issues with large files**:
   - Use `max_reads` parameter
   - Filter reads by previously extracted read ID

3. **Overlapping signals hard to see**:
   - Adjust alpha transparency
   - Reduce number of reads
   - Use different colors
   - Increase figure size

4. **Label "already exists" error**:
   - Each condition needs a unique label
   - Specify custom labels for each `plot_condition()` call

## License

MIT License - see LICENSE file for details.

## Citation

If you use this tool in your research, please cite:
```
# TODO
```