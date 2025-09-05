from matplotlib.colors import to_rgba
import re


def to_rgba_str(color, alpha=0.2):
    # Handle 'rgb(r,g,b)' or 'rgba(r,g,b,a)' format
    if isinstance(color, str) and color.startswith(("rgb(", "rgba(")):
        # Extract numbers from rgb/rgba string
        numbers = re.findall(r"[\d.]+", color)  # Changed to handle decimals
        if len(numbers) >= 3:
            r, g, b = (
                int(float(numbers[0])),
                int(float(numbers[1])),
                int(float(numbers[2])),
            )
            # If rgba, multiply alphas
            if color.startswith("rgba(") and len(numbers) >= 4:
                existing_alpha = float(numbers[3])
                alpha = existing_alpha * alpha
            return f"rgba({r}, {g}, {b}, {alpha})"

    # For other formats, use matplotlib
    r, g, b, *rest = to_rgba(color)
    # Check if matplotlib returned an alpha
    if rest:
        existing_alpha = rest[0]
        alpha = existing_alpha * alpha
    return f"rgba({int(r*255)}, {int(g*255)}, {int(b*255)}, {alpha})"


def get_contrasting_color(bgcolor):
    """Determine whether black or white text provides better contrast."""
    # Handle 'rgb(r,g,b)' or 'rgba(r,g,b,a)' format
    if isinstance(bgcolor, str) and bgcolor.startswith(("rgb(", "rgba(")):
        # Extract numbers from rgb/rgba string
        numbers = re.findall(r"[\d.]+", bgcolor)
        if len(numbers) >= 3:
            r, g, b = (
                int(float(numbers[0])),
                int(float(numbers[1])),
                int(float(numbers[2])),
            )
        else:
            # Fallback if parsing fails
            r, g, b = 128, 128, 128
    else:
        # For other formats, use matplotlib
        rgba = to_rgba(bgcolor)
        r, g, b = int(rgba[0] * 255), int(rgba[1] * 255), int(rgba[2] * 255)

    # Calculate luminance using W3C formula
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255

    # Return black for light backgrounds, white for dark backgrounds
    return "black" if luminance > 0.5 else "white"
