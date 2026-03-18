import dash_bootstrap_components as dbc
from dash import dcc, html
from typing import Optional, Any, Dict, List

from .constants import *


# ============================================================================
# Label Component
# ============================================================================


def create_label(text: str, required: bool = False) -> dbc.Label:
    """Create a modern form label with optional required indicator."""
    content = [text]
    if required:
        content.append(html.Span(" *", style={"color": "#ef4444", "fontWeight": "600"}))

    return dbc.Label(
        content,
        className="form-label mb-2",
        style={
            "fontSize": "0.875rem",
            "fontWeight": "500",
            "color": COLOR_TEXT_MUTED,
        },
    )


# ============================================================================
# Card Component
# ============================================================================


def create_card(
    children,
    className: str = "",
    id: str = "",
    style: Optional[Dict] = None,
    variant: str = "default",  # "default" | "flat" | "ghost"
) -> html.Div:
    """Create a card UI element.

    Variants:
        default — bordered card with shadow (standard)
        flat    — no shadow, subtle border only
        ghost   — no border, no shadow, transparent background
    """
    return html.Div(
        children,
        className=f"glass-card glass-card--{variant} {className}".strip(),
        id=id,
        style=style or {},
    )


# ============================================================================
# Button Component
# ============================================================================


def create_button(
    text: str,
    id: str,
    color: str = "primary",
    size: str = "md",
    className: str = "",
    icon: Optional[str] = None,
    style: Optional[Dict] = None,
    **kwargs,
) -> dbc.Button:
    """Create a button with optional icon and consistent height."""

    # Modern color palette
    color_styles = {
        "primary": {
            "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            "border": "none",
            "color": "white",
            "boxShadow": "0 2px 8px rgba(102, 126, 234, 0.25)",
        },
        "success": {
            "background": "#10b981",
            "border": "none",
            "color": "white",
            "boxShadow": "0 2px 8px rgba(16, 185, 129, 0.25)",
        },
        "danger": {
            "background": "#ef4444",
            "border": "none",
            "color": "white",
            "boxShadow": "0 2px 8px rgba(239, 68, 68, 0.25)",
        },
        "warning": {
            "background": "#f59e0b",
            "border": "none",
            "color": "white",
            "boxShadow": "0 2px 8px rgba(245, 158, 11, 0.25)",
        },
        "info": {
            "background": "#3b82f6",
            "border": "none",
            "color": "white",
            "boxShadow": "0 2px 8px rgba(59, 130, 246, 0.25)",
        },
        "secondary": {
            "background": COLOR_BG_SECONDARY,
            "border": f"1px solid {COLOR_BORDER}",
            "color": COLOR_TEXT_MUTED,
            "boxShadow": "none",
        },
    }

    # Sizes use fixed heights for alignment
    size_styles = {
        "sm": {
            "height": FORM_CONTROL_HEIGHT_SM,
            "padding": "0 16px",
            "fontSize": "0.875rem",
            "borderRadius": BORDER_RADIUS_SM,
        },
        "md": {
            "height": FORM_CONTROL_HEIGHT,
            "padding": "0 24px",
            "fontSize": "0.95rem",
            "borderRadius": BORDER_RADIUS,
        },
        "lg": {
            "height": FORM_CONTROL_HEIGHT_LG,
            "padding": "0 32px",
            "fontSize": "1.0625rem",
            "borderRadius": BORDER_RADIUS_LG,
        },
    }

    button_style = {
        "fontWeight": "500",
        "transition": TRANSITION,
        "cursor": "pointer",
        "letterSpacing": "0.01em",
        "display": "inline-flex",
        "alignItems": "center",
        "justifyContent": "center",
        **color_styles.get(color, color_styles["primary"]),
        **size_styles.get(size, size_styles["md"]),
        **(style or {}),
    }

    content = []
    if icon:
        content.append(html.I(className=icon, style={"marginRight": "6px"}))
    content.append(text)

    return dbc.Button(
        content,
        id=id,
        className=f"modern-btn btn-{color} {className}".strip(),
        style=button_style,
        **kwargs,
    )


# ============================================================================
# Input Component
# ============================================================================


def create_input(
    id: str,
    type: str = "text",
    placeholder: str = "",
    value: Optional[Any] = None,
    className: str = "",
    size: str = "md",
    style: Optional[Dict] = None,
    **kwargs,
) -> dbc.Input:
    """Create a input field with consistent height."""

    # Size-based heights
    size_styles = {
        "sm": {"height": FORM_CONTROL_HEIGHT_SM, "fontSize": "0.875rem"},
        "md": {"height": FORM_CONTROL_HEIGHT, "fontSize": "0.9375rem"},
        "lg": {"height": FORM_CONTROL_HEIGHT_LG, "fontSize": "1rem"},
    }

    default_style = {
        "borderRadius": BORDER_RADIUS,
        "border": f"1.5px solid {COLOR_BORDER}",
        "background": COLOR_BG_INPUT,
        "padding": "0 14px",
        "transition": TRANSITION,
        "color": COLOR_TEXT,
        **size_styles.get(size, size_styles["md"]),
    }

    merged_style = {**default_style, **(style or {})}

    return dbc.Input(
        id=id,
        type=type,
        placeholder=placeholder,
        value=value,
        className=f"modern-input {className}".strip(),
        style=merged_style,
        **kwargs,
    )


# ============================================================================
# Select Component
# ============================================================================


def create_select(
    id: str,
    options: List[Dict],
    value: Optional[Any] = None,
    placeholder: str = "Select...",
    className: str = "",
    size: str = "md",
    style: Optional[Dict] = None,
    **kwargs,
) -> dbc.Select:
    """Create a select dropdown."""

    # Size-based heights
    size_styles = {
        "sm": {"height": FORM_CONTROL_HEIGHT_SM, "fontSize": "0.875rem"},
        "md": {"height": FORM_CONTROL_HEIGHT, "fontSize": "0.9375rem"},
        "lg": {"height": FORM_CONTROL_HEIGHT_LG, "fontSize": "1rem"},
    }

    default_style = {
        "borderRadius": BORDER_RADIUS,
        "border": f"1.5px solid {COLOR_BORDER}",
        "background": COLOR_BG_INPUT,
        "padding": "0 14px",
        "transition": TRANSITION,
        "color": COLOR_TEXT,
        **size_styles.get(size, size_styles["md"]),
    }

    merged_style = {**default_style, **(style or {})}

    return dbc.Select(
        id=id,
        options=options,
        value=value,
        placeholder=placeholder,
        className=f"modern-select {className}".strip(),
        style=merged_style,
        **kwargs,
    )


# ============================================================================
# Switch Component
# ============================================================================


def create_switch(id: str, label: str, value: bool = False) -> html.Div:
    """Create a modern switch component."""
    return html.Div(
        [
            dbc.Switch(
                id=id,
                label=label,
                value=value,
                className="modern-switch form-switch",
                style={
                    "fontSize": "0.9375rem",
                    "fontWeight": "500",
                    "color": COLOR_TEXT_MUTED,
                },
                input_class_name="ms-0",
                label_class_name="ms-3",
            ),
        ],
        style={
            "height": FORM_CONTROL_HEIGHT,
            "padding": "0 18px",
            "display": "flex",
            "alignItems": "center",
            "background": COLOR_BG_SECONDARY,
            "borderRadius": BORDER_RADIUS,
            "border": f"1.5px solid {COLOR_BORDER}",
            "transition": TRANSITION,
        },
    )


# ============================================================================
# Dropdown Component (dcc.Dropdown)
# ============================================================================


def create_dropdown(
    id: str,
    options: List[Dict],
    value: Optional[Any] = None,
    multi: bool = False,
    placeholder: str = "Select...",
    className: str = "",
    size: Optional[str] = "md",
    **kwargs,
) -> dcc.Dropdown:
    """Create a dropdown with consistent modern styling via CSS classes."""

    # Size classes for different heights / font sizes
    size_class = f"dropdown-{size}"  # e.g., "dropdown-sm", "dropdown-md", "dropdown-lg"

    return dcc.Dropdown(
        id=id,
        options=options,
        value=value,
        multi=multi,
        placeholder=placeholder,
        className=f"modern-dropdown {size_class} {className}".strip(),
        **kwargs,
    )


# ============================================================================
# Button Group Component
# ============================================================================


def create_button_group(
    buttons: List[Dict[str, Any]],
    size: str = "md",
    style: Optional[Dict] = None,
) -> dbc.ButtonGroup:
    """Create a button group with consistent heights.

    Args:
        buttons: List of dicts with keys: text, id, active (optional), color (optional)
        size: Size of buttons (sm, md, lg)
        style: Additional styles

    Example:
        create_button_group([
            {"text": "A", "id": "base-a", "active": True},
            {"text": "C", "id": "base-c"},
        ])
    """
    size_styles = {
        "sm": {"height": FORM_CONTROL_HEIGHT_SM},
        "md": {"height": FORM_CONTROL_HEIGHT},
        "lg": {"height": FORM_CONTROL_HEIGHT_LG},
    }

    default_style = {
        **size_styles.get(size, size_styles["md"]),
        **(style or {}),
    }

    button_elements = []
    for btn in buttons:
        button_elements.append(
            dbc.Button(
                btn["text"],
                id=btn["id"],
                outline=True,
                color=btn.get("color", "secondary"),
                size=size,
                active=btn.get("active", False),
                style={"flex": "1"},
            )
        )

    return dbc.ButtonGroup(button_elements, style=default_style)
