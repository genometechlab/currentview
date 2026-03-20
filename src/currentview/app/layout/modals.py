from pathlib import Path
from typing import Optional, List

import dash_bootstrap_components as dbc
from dash import dcc, html

from .elements import create_input, create_button, create_dropdown
from ..styles.constants import (
    BORDER_RADIUS,
    BORDER_RADIUS_SM,
    COLOR_BORDER,
    TRANSITION,
    RADIUS_LEFT,
    RADIUS_RIGHT,
    RADIUS_NONE,
)


# ── Private helpers ───────────────────────────────────────────────────────────


def _create_browser_navigation(modal_id: str, default: str) -> dbc.InputGroup:
    return dbc.InputGroup(
        [
            create_input(
                id=f"{modal_id}-path",
                value=str(Path(default)),
                style={"borderRadius": RADIUS_LEFT},
            ),
            create_button(
                "Go",
                id=f"{modal_id}-go",
                color="primary",
                style={"borderRadius": RADIUS_NONE},
            ),
            create_button(
                "↑",
                id=f"{modal_id}-up",
                color="primary",
                style={"borderRadius": RADIUS_RIGHT},
            ),
        ],
        size="sm",
        className="mb-3",
    )


def _create_file_list(modal_id: str) -> html.Div:
    return html.Div(
        id=f"{modal_id}-list",
        style={
            "height": "400px",
            "overflowY": "auto",
            "padding": "0.5rem",
            "borderRadius": BORDER_RADIUS_SM,
            "border": f"1px solid {COLOR_BORDER}",
            "transition": TRANSITION,
        },
    )


# ── Placeholder map ───────────────────────────────────────────────────────────

_PLACEHOLDER = {
    "file": "No file selected",
    "dir": "No directory selected",
    "both": "No file or directory selected",
}


# ── Public components ─────────────────────────────────────────────────────────


def create_input_modal(
    modal_id: str,
    title: str,
    file_extension: Optional[str] = None,
    mode: str = "file",  # "file" | "dir" | "both"
    default: Optional[str] = None,
) -> dbc.Modal:
    """File/directory selection modal.

    Args:
        modal_id:       Unique identifier for the modal.
        title:          Modal title.
        file_extension: Extension to filter (e.g. '.bam'). None shows all files.
        mode:           'file' | 'dir' | 'both'
        default:        Default directory path to open.
    """
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle(title)),
            dbc.ModalBody(
                [
                    _create_browser_navigation(modal_id, default),
                    _create_file_list(modal_id),
                    dcc.Store(
                        id=f"{modal_id}-config",
                        data={"extension": file_extension, "mode": mode},
                    ),
                ]
            ),
            dbc.ModalFooter(
                [
                    create_input(
                        id=f"{modal_id}-selected",
                        placeholder=_PLACEHOLDER.get(mode, "No file selected"),
                        disabled=True,
                    ),
                    create_button("Cancel", id=f"{modal_id}-cancel", color="danger"),
                    create_button("Select", id=f"{modal_id}-select", color="success"),
                ]
            ),
        ],
        id=modal_id,
        size="lg",
        is_open=False,
    )


def create_export_modal(
    modal_id: str,
    title: str,
    file_extensions: List[str],
    default_extension: str,
    mode: str = "file",  # "file" | "dir"
    default: Optional[str] = None,
) -> dbc.Modal:
    """File export/save modal with format selection.

    Args:
        modal_id:           Unique identifier for the modal.
        title:              Modal title.
        file_extensions:    List of allowed file extensions.
        default_extension:  Default file extension (e.g. '.html').
        mode:               'file' | 'dir'
        default:            Default directory path to open.
    """
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle(title)),
            dbc.ModalBody(
                [
                    _create_browser_navigation(modal_id, default),
                    _create_file_list(modal_id),
                    dcc.Store(
                        id=f"{modal_id}-config",
                        data={"extension": default_extension, "mode": mode},
                    ),
                ]
            ),
            dbc.ModalFooter(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                create_input(
                                    id=f"{modal_id}-input-path",
                                    value=f"out{default_extension}",
                                    placeholder="Enter filename...",
                                ),
                                width=9,
                            ),
                            dbc.Col(
                                create_dropdown(
                                    id=f"{modal_id}-format",
                                    options=file_extensions,
                                    value=default_extension,
                                    clearable=False,
                                ),
                                width=3,
                            ),
                        ],
                        className="g-2 w-100 mb-3",
                        align="center",
                    ),
                    html.Div(
                        [
                            create_button(
                                "Cancel", id=f"{modal_id}-cancel", color="danger"
                            ),
                            create_button(
                                "Save", id=f"{modal_id}-save", color="success"
                            ),
                        ],
                        className="d-flex justify-content-end gap-2",
                    ),
                ]
            ),
        ],
        id=modal_id,
        size="lg",
        is_open=False,
    )
