import dash_bootstrap_components as dbc
from dash import dcc, html
from typing import Optional, Dict, Any

from ..config import (
    WINDOW_SIZE_MIN, WINDOW_SIZE_MAX, WINDOW_SIZE_DEFAULT, WINDOW_SIZE_STEP,
    LINE_STYLES, VERBOSITY_LEVELS, STATISTICS_OPTIONS, STYLE_OPTIONS,
    DEFAULT_COLOR, DEFAULT_LINE_WIDTH, DEFAULT_OPACITY
)

def create_label(text, required=False):
    if required:
        return html.Label([
            text, 
            html.Span(" *", style={"color": "#dc3545", "fontWeight": "bold"})
        ], className="modern-label")
    else:
        return html.Label(text, className="modern-label")
    
def create_card(children, className="", style=None):
    """Create a modern glass-morphism card with flat design."""
    default_style = {
        "background": "rgba(255, 255, 255, 0.8)",  # More opaque, less glassy
        "backdropFilter": "blur(10px)",
        "WebkitBackdropFilter": "blur(10px)",
        "borderRadius": "12px",  # Slightly less rounded
        "border": "1px solid rgba(0, 0, 0, 0.08)",  # Subtle border
        "boxShadow": "0 2px 8px 0 rgba(0, 0, 0, 0.08)",  # Softer shadow
        "padding": "24px",
        "transition": "all 0.3s ease"
    }
    if style:
        default_style.update(style)
    
    return html.Div(
        children,
        className=f"glass-card {className}",
        style=default_style
    )


def create_button(text, id, color="primary", size="md", className="", icon=None, **kwargs):
    """Create a flat styled button with optional icon."""
    color_styles = {
        "primary": {
            "background": "#6366f1",
            "border": "none",
            "color": "white",
            "boxShadow": "0 1px 3px 0 rgba(0, 0, 0, 0.1)"
        },
        "success": {
            "background": "#10b981",
            "border": "none",
            "color": "white",
            "boxShadow": "0 1px 3px 0 rgba(0, 0, 0, 0.1)"
        },
        "danger": {
            "background": "#ef4444",
            "border": "none",
            "color": "white",
            "boxShadow": "0 1px 3px 0 rgba(0, 0, 0, 0.1)"
        },
        "warning": {
            "background": "#f5e239",
            "border": "none",
            "color": "#374151",
            "boxShadow": "0 1px 3px 0 rgba(0, 0, 0, 0.1)"
        },
        "info": {
            "background": "#3b82f6",
            "border": "none",
            "color": "white",
            "boxShadow": "0 1px 3px 0 rgba(0, 0, 0, 0.1)"
        },
        "secondary": {
            "background": "#f3f4f6",
            "border": "1px solid #e5e7eb",
            "color": "#374151"
        }
    }
    
    size_styles = {
        "sm": {"padding": "8px 16px", "fontSize": "0.875rem"},
        "md": {"padding": "12px 24px", "fontSize": "1rem"},
        "lg": {"padding": "16px 32px", "fontSize": "1.125rem"}
    }
    
    button_style = {
        "borderRadius": "8px",
        "fontWeight": "500",
        "transition": "all 0.2s ease",
        "cursor": "pointer",
        **color_styles.get(color, color_styles["primary"]),
        **size_styles.get(size, size_styles["md"])
    }
    
    content = [html.I(className=icon, style={"marginRight": "8px"})] if icon else []
    content.append(text)
    
    return dbc.Button(
        content,
        id=id,
        className=f"modern-btn btn-{color} {className}",  # Add color-specific class
        style=button_style,
        **kwargs
    )


def create_input(id, type="text", placeholder="", value=None, className="", **kwargs):
    """Create a flat styled input field."""
    return dbc.Input(
        id=id,
        type=type,
        placeholder=placeholder,
        value=value,
        className="modern-input {className}",
        style={
            "borderRadius": "8px",
            "border": "1px solid #e5e7eb",
            "background": "#ffffff",
            "padding": "12px 16px",
            "transition": "all 0.2s ease",
            "fontSize": "0.95rem"
        },
        **kwargs
    )
    
def create_switch(id: str, label: str, value: bool = False) -> html.Div:
    """Create a flat styled switch component."""
    return html.Div([
        dbc.Switch(
            id=id,
            label=label,
            value=value,
            className="modern-switch form-switch ms-0",  # Add form-switch and ms-0
            style={
                "fontSize": "0.95rem",
                "fontWeight": "500",
                "color": "#4b5563"
            },
            input_class_name="ms-0",  # Remove margin from input
            label_class_name="ms-3"   # Add margin to label
        ),
    ], style={
        "padding": "12px 16px",
        "background": "#f9fafb",
        "borderRadius": "8px",
        "border": "1px solid #e5e7eb",
        "transition": "all 0.2s ease"
    })