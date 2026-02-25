import dash_bootstrap_components as dbc
from dash import dcc, html
from pathlib import Path
from typing import Optional, List
from .elements import create_input, create_button, create_dropdown


def _create_browser_navigation(modal_id: str, default: str) -> dbc.InputGroup:
    """Create the path navigation bar for file browser modals."""
    return dbc.InputGroup(
        [
            create_input(
                id=f"{modal_id}-path",
                value=str(Path(default)),
                style={"borderRadius": "10px 0 0 10px"},
            ),
            create_button(
                "Go",
                id=f"{modal_id}-go",
                size="md",
                color="primary",
                style={"borderRadius": "0 0 0 0"},
            ),
            create_button(
                "↑",
                id=f"{modal_id}-up",
                size="md",
                color="primary",
                style={"borderRadius": "0 10px 10px 0"},
            ),
        ],
        size="sm",
        className="mb-3",
    )


def _create_file_list(modal_id: str) -> html.Div:
    """Create the scrollable file/directory list area."""
    return html.Div(
        id=f"{modal_id}-list",
        style={
            "height": "400px",
            "overflowY": "auto",
            "padding": "0.5rem",
            "borderRadius": "8px",
            "border": "1px solid #e5e7eb",
            "transition": "all 0.2s ease",
        },
    )


def create_input_modal(
    modal_id: str,
    title: str,
    file_extension: Optional[str] = None,
    mode: str = "file",  # "file" | "dir" | "both"
    default: Optional[str] = None,
) -> dbc.Modal:
    """Create a file/directory selection modal.

    Args:
        modal_id:       Unique identifier for the modal
        title:          Modal title
        file_extension: File extension to filter (e.g., '.bam'). None shows all files.
        mode:           "file" — select files only
                        "dir"  — select directories only
                        "both" — select files or directories
        default:        Default directory path to open

    Returns:
        dbc.Modal component
    """
    placeholders = {
        "file": "No file selected",
        "dir": "No directory selected",
        "both": "No file or directory selected",
    }

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
                        placeholder=placeholders.get(mode, "No file selected"),
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
    """Create a file export/save modal with format selection.

    Args:
        modal_id:           Unique identifier for the modal
        title:              Modal title
        file_extensions:    List of allowed file extensions
        default_extension:  Default file extension (e.g., '.html')
        mode:               "file" — save as file
                            "dir"  — select output directory
        default:            Default directory path to open

    Returns:
        dbc.Modal component
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
