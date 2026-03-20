import dash_bootstrap_components as dbc
from dash import dcc, html
from typing import Optional, Any, Dict, List

from ..styles.constants import (
    BORDER_RADIUS,
    BORDER_RADIUS_SM,
    BORDER_RADIUS_LG,
    COLOR_BORDER,
    COLOR_BG_INPUT,
    COLOR_BG_SECONDARY,
    COLOR_TEXT,
    COLOR_TEXT_MUTED,
    FORM_CONTROL_HEIGHT,
    FORM_CONTROL_HEIGHT_SM,
    FORM_CONTROL_HEIGHT_LG,
    TRANSITION,
    GRADIENT_PRIMARY,
    COLOR_SUCCESS,
    COLOR_DANGER,
    COLOR_WARNING,
    COLOR_INFO,
    SHADOW_SM,
    SHADOW_COLOR_PRIMARY,
    SHADOW_COLOR_SUCCESS,
    SHADOW_COLOR_DANGER,
    SHADOW_COLOR_WARNING,
    SHADOW_COLOR_INFO,
)


# ── Helpers ──────────────────────────────────────────────────────────────────

_SIZE = {
    "sm": {
        "height": FORM_CONTROL_HEIGHT_SM,
        "fontSize": "0.875rem",
        "borderRadius": BORDER_RADIUS_SM,
    },
    "md": {
        "height": FORM_CONTROL_HEIGHT,
        "fontSize": "0.9375rem",
        "borderRadius": BORDER_RADIUS,
    },
    "lg": {
        "height": FORM_CONTROL_HEIGHT_LG,
        "fontSize": "1rem",
        "borderRadius": BORDER_RADIUS_LG,
    },
}

_INPUT_BASE = {
    "border": f"1.5px solid {COLOR_BORDER}",
    "background": COLOR_BG_INPUT,
    "padding": "0 14px",
    "transition": TRANSITION,
    "color": COLOR_TEXT,
}


# ── Label ─────────────────────────────────────────────────────────────────────


def create_label(text: str, required: bool = False) -> dbc.Label:
    content = [text]
    if required:
        content.append(
            html.Span(" *", style={"color": COLOR_DANGER, "fontWeight": "600"})
        )
    return dbc.Label(
        content,
        className="form-label mb-2",
        style={"fontSize": "0.875rem", "fontWeight": "500", "color": COLOR_TEXT_MUTED},
    )


# ── Card ──────────────────────────────────────────────────────────────────────


def create_card(
    children,
    className: str = "",
    id: str = "",
    style: Optional[Dict] = None,
    variant: str = "default",  # "default" | "flat" | "ghost"
    hoverable: bool = False,
) -> html.Div:
    classes = f"glass-card glass-card--{variant}"
    if hoverable:
        classes += " hoverable"
    if className:
        classes += f" {className}"
    return html.Div(children, className=classes, id=id, style=style or {})


# ── Button ────────────────────────────────────────────────────────────────────

_BTN_COLOR = {
    "primary": {
        "background": GRADIENT_PRIMARY,
        "border": "none",
        "color": "white",
        "boxShadow": f"0 2px 8px {SHADOW_COLOR_PRIMARY}",
    },
    "success": {
        "background": COLOR_SUCCESS,
        "border": "none",
        "color": "white",
        "boxShadow": f"0 2px 8px {SHADOW_COLOR_SUCCESS}",
    },
    "danger": {
        "background": COLOR_DANGER,
        "border": "none",
        "color": "white",
        "boxShadow": f"0 2px 8px {SHADOW_COLOR_DANGER}",
    },
    "warning": {
        "background": COLOR_WARNING,
        "border": "none",
        "color": "white",
        "boxShadow": f"0 2px 8px {SHADOW_COLOR_WARNING}",
    },
    "info": {
        "background": COLOR_INFO,
        "border": "none",
        "color": "white",
        "boxShadow": f"0 2px 8px {SHADOW_COLOR_INFO}",
    },
    "secondary": {
        "background": COLOR_BG_SECONDARY,
        "border": f"1px solid {COLOR_BORDER}",
        "color": COLOR_TEXT_MUTED,
        "boxShadow": "none",
    },
}

_BTN_PADDING = {"sm": "0 16px", "md": "0 24px", "lg": "0 32px"}
_BTN_FONT = {"sm": "0.875rem", "md": "0.95rem", "lg": "1.0625rem"}


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
    btn_style = {
        "fontWeight": "500",
        "transition": TRANSITION,
        "cursor": "pointer",
        "letterSpacing": "0.01em",
        "display": "inline-flex",
        "alignItems": "center",
        "justifyContent": "center",
        "height": _SIZE[size]["height"],
        "borderRadius": _SIZE[size]["borderRadius"],
        "padding": _BTN_PADDING.get(size, _BTN_PADDING["md"]),
        "fontSize": _BTN_FONT.get(size, _BTN_FONT["md"]),
        **_BTN_COLOR.get(color, _BTN_COLOR["primary"]),
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
        style=btn_style,
        **kwargs,
    )


# ── Input ─────────────────────────────────────────────────────────────────────


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
    merged = {**_INPUT_BASE, **_SIZE[size], **(style or {})}
    return dbc.Input(
        id=id,
        type=type,
        placeholder=placeholder,
        value=value,
        className=f"modern-input {className}".strip(),
        style=merged,
        **kwargs,
    )


# ── Select ────────────────────────────────────────────────────────────────────


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
    merged = {**_INPUT_BASE, **_SIZE[size], **(style or {})}
    return dbc.Select(
        id=id,
        options=options,
        value=value,
        placeholder=placeholder,
        className=f"modern-select {className}".strip(),
        style=merged,
        **kwargs,
    )


# ── Switch ────────────────────────────────────────────────────────────────────


def create_switch(id: str, label: str, value: bool = False) -> html.Div:
    return html.Div(
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


# ── Dropdown (dcc) ────────────────────────────────────────────────────────────


def create_dropdown(
    id: str,
    options: List[Dict],
    value: Optional[Any] = None,
    multi: bool = False,
    placeholder: str = "Select...",
    className: str = "",
    size: str = "md",
    **kwargs,
) -> dcc.Dropdown:
    return dcc.Dropdown(
        id=id,
        options=options,
        value=value,
        multi=multi,
        placeholder=placeholder,
        className=f"modern-dropdown dropdown-{size} {className}".strip(),
        **kwargs,
    )


# ── Button Group ──────────────────────────────────────────────────────────────


def create_button_group(
    buttons: List[Dict[str, Any]],
    size: str = "md",
    style: Optional[Dict] = None,
) -> dbc.ButtonGroup:
    """
    Each button dict: {text, id, active (opt), color (opt)}
    """
    merged = {"height": _SIZE[size]["height"], **(style or {})}
    els = [
        dbc.Button(
            btn["text"],
            id=btn["id"],
            outline=True,
            color=btn.get("color", "secondary"),
            size=size,
            active=btn.get("active", False),
            style={"flex": "1"},
        )
        for btn in buttons
    ]
    return dbc.ButtonGroup(els, style=merged)
