# PlotStyle Configuration Guide for Plotly

## Available PlotStyle Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| **Figure Dimensions** ||||
| `width` | int | 1200 | Figure width in pixels |
| `height` | int | 800 | Figure height in pixels |
| **Rendering** ||||
| `renderer` | `'SVG'` / `'WebGL'` | `'SVG'` | Rendering backend |
| **Trace Styling** ||||
| `line_width` | float | 2.0 | Default line thickness for traces |
| `line_style` | str | `'solid'` | Line style (`'solid'`, `'dash'`, `'dot'`, `'dashdot'`) |
| `opacity_mode` | `'auto'` / `'fixed'` | `'auto'` | Opacity calculation mode |
| `fixed_opacity` | float | 0.8 | Opacity value when mode is `'fixed'` |
| `fill_opacity` | float | 0.3 | Opacity for filled areas |
| **Layout and Spacing** ||||
| `margin` | dict | `{'l': 80, 'r': 80, 't': 100, 'b': 80}` | Margins in pixels (left, right, top, bottom) |
| `positions_padding` | float | 0.025 | Padding between kmer position windows |
| **Grid and Barriers** ||||
| `show_grid` | bool | False | Show background grid |
| `grid_color` | str | `'rgba(128, 128, 128, 0.2)'` | Grid line color |
| `zeroline` | bool | False | Show zero line on axes |
| `barrier_style` | str | `'solid'` | Line style of position barrier lines (`'solid'`, `'dash'`, `'dot'`, `'dashdot'`) |
| `barrier_opacity` | float | 0.25 | Opacity of the barrier lines |
| `barrier_color` | str | `'grey'` | Barrier line color |
| **Axes** ||||
| `showline` | bool | True | Show axis lines |
| `linecolor` | str | `'black'` | Axis line color |
| `linewidth` | int | 1 | Axis line width |
| `mirror` | bool | False | Mirror axis lines to opposite side |
| **Background Colors** ||||
| `plot_bgcolor` | str | `'white'` | Plot area background color |
| `paper_bgcolor` | str | `'white'` | Full figure background color |
| **Colors and Themes** ||||
| `template` | str | `'plotly_white'` | Plotly built-in template |
| `colorway` | list[str] / None | None | Custom color sequence override |
| **Fonts** ||||
| `font_family` | str | `'Arial, sans-serif'` | Default font family |
| `title_font_size` | int | 20 | Main title font size |
| `titlecolor` | str | `'black'` | Title text color |
| `axis_title_font_size` | int | 16 | Axis title font size |
| `axis_title_color` | str | `'black'` | Axis title text color |
| `tick_font_size` | int | 12 | Tick label font size |
| `legend_font_size` | int | 12 | Legend text font size |
| `annotation_font_size` | int | 11 | Annotation text font size |
| `subplot_title_font_size` | int | 14 | Subplot title font size |
| **Legend** ||||
| `show_legend` | bool | True | Display legend |
| `legend_orientation` | `'v'` / `'h'` | `'v'` | Vertical or horizontal legend |
| `legend_x` | float | 1.02 | Legend x position (0-1 scale) |
| `legend_y` | float | 1 | Legend y position (0-1 scale) |
| `legend_xanchor` | str | `'left'` | X anchor point (`'left'`, `'center'`, `'right'`) |
| `legend_yanchor` | str | `'top'` | Y anchor point (`'top'`, `'middle'`, `'bottom'`) |
| `legend_bgcolor` | str | `'rgba(255, 255, 255, 0.8)'` | Legend background color |
| `legend_bordercolor` | str | `'rgba(0, 0, 0, 0.2)'` | Legend border color |
| `legend_borderwidth` | int | 1 | Legend border width |
| **Hover Interaction** ||||
| `hovermode` | str | `'closest'` | Hover mode (`'x'`, `'y'`, `'closest'`, `'x unified'`, `'y unified'`) |
| `hoverlabel_bgcolor` | str | `'white'` | Hover label background color |
| `hoverlabel_bordercolor` | str | `'black'` | Hover label border color |
| `hoverlabel_font_size` | int | 12 | Hover label font size |
| **Subplots** ||||
| `subplot_vertical_spacing` | float / None | None | Vertical spacing between subplots (auto if None) |
| `subplot_horizontal_spacing` | float / None | None | Horizontal spacing between subplots (auto if None) |
| **Ticks** ||||
| `ticks` | str | `'outside'` | Tick position (`'outside'`, `'inside'`, `''`) |
| `ticklen` | int | 5 | Tick length in pixels |
| `tickwidth` | int | 1 | Tick line width |
| `tickcolor` | str | `'black'` | Tick color |
| **Interactive Features** ||||
| `dragmode` | str | `'zoom'` | Default drag interaction (`'zoom'`, `'pan'`, `'select'`, `'lasso'`, `'orbit'`, `'turntable'`) |
| `selectdirection` | str | `'d'` | Selection direction (`'d'`=diagonal, `'h'`=horizontal, `'v'`=vertical, `'any'`) |
| **Export Configuration** ||||
| `toImageButtonOptions` | dict | `{'format': 'png', 'width': 1200, 'height': 800, 'scale': 2}` | Image export settings |

## Example Usage

```python
from currentview.utils.plotly_utils import PlotStyle

# Create a custom style
style = PlotStyle(
    width=1400,
    height=900,
    title_font_size=24,
    show_grid=True,
    hovermode='x unified',
    line_width=2.5,
    opacity_mode='fixed',
    fixed_opacity=0.7
)

# Use with GenomicPositionVisualizer
from currentview import GenomicPositionVisualizer

viz = GenomicPositionVisualizer(
    K=9,
    signals_plot_style=style,
    stats_plot_style=style
)
```

## Predefined Styles

Use `PlotStyle.get_style()` to access predefined configurations for different contexts. These can be used as a starting point and further customized.

```python
from currentview.utils.plotly_utils import PlotStyle

# Get a predefined style by name
style = PlotStyle.get_style('presentation')

# Modify as needed
style.line_width = 3.5
style.show_grid = True
```

### Available Style Names

| Style Name | Description | Dimensions | Primary Use Case |
|------------|-------------|------------|------------------|
| `'paper_single'` | Single-column journal figure | 1050×700 (3.5"×2.33" at 300 DPI) | Academic papers, single column |
| `'paper_double'` | Two-column journal figure | 2100×1050 (7"×3.5" at 300 DPI) | Academic papers, full width |
| `'poster'` | Conference poster figure | 2400×1800 (8"×6" at 300 DPI) | Academic posters |
| `'presentation'` | Slide presentation (light) | 1920×1080 (16:9) | Talks, lectures |
| `'presentation_dark'` | Dark theme presentation | 1920×1080 (16:9) | Talks in dimmed rooms |
| `'interactive'` | Web/exploration (light) | 1200×800 | Data exploration, notebooks |
| `'interactive_dark'` | Dark theme interactive | 1200×800 | Dark-themed environments |

### Style Details

**`paper_single`** - Optimized for single-column academic figures:
- Compact margins for space efficiency
- Smaller fonts sized for print readability
- SVG export format preferred
- Clean, minimal design

**`paper_double`** - Optimized for full-width academic figures:
- 2:1 aspect ratio
- Slightly larger fonts than single-column
- More space for complex visualizations

**`poster`** - Optimized for conference posters:
- Extra large fonts for distance viewing
- Bold line widths (4.0)
- High visual impact design
- Arial Black font family

**`presentation`** - Optimized for slides:
- 16:9 aspect ratio
- Large fonts for back-of-room visibility
- High contrast design
- Mirrored axes for framing

**`presentation_dark`** - Dark variant for dimmed rooms:
- Dark background (`#0a0a0a`)
- Light text and grid lines
- High contrast for projection

**`interactive`** - Optimized for exploration:
- Standard screen dimensions
- Auto opacity mode
- Full zoom/pan interactivity
- Detailed hover information

**`interactive_dark`** - Dark theme for notebooks/web:
- Dark background
- Reduced eye strain
- Same interactivity as light version