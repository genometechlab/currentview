# PlotStyle Configuration Guide for Plotly

## Available PlotStyle Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| **Figure Dimensions** | | | |
| `width` | int | 1200 | Figure width in pixels |
| `height` | int | 800 | Figure height in pixels |
| **Rendering** | | | |
| `renderer` | 'SVG'/'WebGL' | 'WebGL' | Rendering option |
| **Trace Styling** | | | |
| `line_width` | float | 2.0 | Default line thickness for traces |
| `line_style` | str | 'solid' | Line style ('solid', 'dash', 'dot', 'dashdot') |
| `opacity_mode` | 'auto'/'fixed' | 'auto' | Opacity calculation mode |
| `fixed_opacity` | float | 0.8 | Opacity value when mode is 'fixed' |
| `fill_opacity` | float | 0.3 | Opacity for filled areas |
| **Layout and Spacing** | | | |
| `margin` | dict | {'l': 80, 'r': 80, 't': 100, 'b': 80} | Margins in pixels (left, right, top, bottom) |
| `padding` | float | 0.025 | Padding between kmer windows |
| **Grid and Axes** | | | |
| `show_grid` | bool | True | Show background grid |
| `grid_color` | str | 'rgba(128, 128, 128, 0.2)' | Grid line color (Plotly accepted format) |
| `zeroline` | bool | False | Show zero line on axes |
| `showline` | bool | True | Show axis lines |
| `linecolor` | str | 'black' | Axis line color |
| `barrier_style` | str | 'solid' | Line style of the barrier lines ('solid', 'dash', 'dot', 'dashdot') |
| `barrier_opacity` | float | 0.8 | Opacity of the barrier lines |
| `barrier_color` | str | 'grey' | Grid line color (Plotly accepted format) |
| `linewidth` | int | 1 | Axis line width |
| `mirror` | bool | False | Mirror axis lines to opposite side |
| **Background Colors** | | | |
| `plot_bgcolor` | str | 'white' | Plot area background color |
| `paper_bgcolor` | str | 'white' | Full figure background color |
| **Colors and Themes** | | | |
| `template` | str | 'plotly_white' | Plotly built-in template |
| `color_scheme` | ColorScheme/str | ColorScheme.TAB10 | Predefined color palette |
| `colorway` | list[str] or None | None | Custom color sequence override |
| **Fonts** | | | |
| `font_family` | str | 'Arial, sans-serif' | Default font family |
| `title_font_size` | int | 20 | Main title font size |
| `axis_title_font_size` | int | 16 | Axis title font size |
| `tick_font_size` | int | 12 | Tick label font size |
| `legend_font_size` | int | 12 | Legend text font size |
| `annotation_font_size` | int | 11 | Annotation text font size |
| `subplot_title_font_size` | int | 14 | Subplot title font size |
| **Legend** | | | |
| `show_legend` | bool | True | Display legend |
| `legend_orientation` | 'v'/'h' | 'v' | Vertical or horizontal legend |
| `legend_x` | float | 1.02 | Legend x position (0-1 scale) |
| `legend_y` | float | 1 | Legend y position (0-1 scale) |
| `legend_xanchor` | str | 'left' | X anchor point ('left', 'center', 'right') |
| `legend_yanchor` | str | 'top' | Y anchor point ('top', 'middle', 'bottom') |
| `legend_bgcolor` | str | 'rgba(255, 255, 255, 0.8)' | Legend background color |
| `legend_bordercolor` | str | 'rgba(0, 0, 0, 0.2)' | Legend border color |
| `legend_borderwidth` | int | 1 | Legend border width |
| **Hover Interaction** | | | |
| `hovermode` | str | 'closest' | Hover mode ('x', 'y', 'closest', 'x unified', 'y unified') |
| `hoverlabel_bgcolor` | str | 'white' | Hover label background color |
| `hoverlabel_bordercolor` | str | 'black' | Hover label border color |
| `hoverlabel_font_size` | int | 12 | Hover label font size |
| **Subplots** | | | |
| `subplot_vertical_spacing` | float or None | None | Vertical spacing between subplots (auto if None) |
| `subplot_horizontal_spacing` | float or None | None | Horizontal spacing between subplots (auto if None) |
| **Ticks** | | | |
| `ticks` | str | 'outside' | Tick position ('outside', 'inside', '') |
| `ticklen` | int | 5 | Tick length in pixels |
| `tickwidth` | int | 1 | Tick line width |
| `tickcolor` | str | 'black' | Tick color |
| **Interactive Features** | | | |
| `dragmode` | str | 'zoom' | Default drag interaction ('zoom', 'pan', 'select', 'lasso', 'orbit', 'turntable') |
| `selectdirection` | str | 'd' | Selection direction ('d'=diagonal, 'h'=horizontal, 'v'=vertical, 'any') |
| **Export Configuration** | | | |
| `toImageButtonOptions` | dict | {'format': 'png', 'width': 1200, 'height': 800, 'scale': 2} | Image export settings |

## Color Schemes

Available color schemes via `ColorScheme` enum:

- `TAB10`: Matplotlib's tab10 color scheme (10 distinct colors)
- `PLOTLY_DARK`: Plotly's dark theme colors
- `PASTEL`: Soft, muted colors
- `DARK`: Dark2 color scheme with rich, deep colors
- `COLORBLIND`: Accessible palette optimized for color vision deficiency

## Example Usage

```python
# Create a custom style
style = PlotStyle(
    width=1200,
    height=800,
    color_scheme=ColorScheme.COLORBLIND,
    title_font_size=24,
    show_grid=True,
    hovermode='x unified'
)

# Apply to a Plotly figure
import plotly.graph_objects as go

fig = go.Figure()
# Add your traces here...
fig.update_layout(**style.get_layout_dict())
```

## Predefined Styles

Use `PlotStyles.get_style()` to access predefined configurations created for different contexts.
You can use this predefined styles as a head start. Note that you can still configure these styles.

```python
from plot_styles import PlotStyles

# Get a predefined style by name
style = PlotStyles.get_style('<style_name>')

# Modify as needed
style.color_scheme = ColorScheme.COLORBLIND
style.show_grid = True
```

### Available Style Names

| Style Name | Description | Dimensions | Primary Use Case |
|------------|-------------|------------|------------------|
| `'paper_single'` | Single-column journal figure | 1050×700 (3.5"×2.33") | Academic papers, single column |
| `'paper_double'` | Two-column journal figure | 2100×1050 (7"×3.5") | Academic papers, full width |
| `'poster'` | Conference poster figure | 2400×1800 (8"×6") | Academic posters |
| `'presentation'` | Slide presentation | 1920×1080 (16:9) | Talks, lectures |
| `'presentation_dark'` | Dark theme presentation | 1920×1080 (16:9) | Talks, lectures |
| `'interactive'` | Web/exploration | 1200×800 | Data exploration in notebooks, web viewing |

