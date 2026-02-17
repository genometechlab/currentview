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
                size="sm",
                color="primary",
                style={"borderRadius": "0 0 0 0"},
            ),
            create_button(
                "↑",
                id=f"{modal_id}-up",
                size="sm",
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
    allow_dir: bool = False,
    allow_both: bool = False,
    default: str = "/data/tRNA",
) -> dbc.Modal:
    """Create a file/directory selection modal.

    Args:
        modal_id: Unique identifier for the modal
        title: Modal title
        file_extension: File extension to filter (e.g., '.bam'). None shows all files.
        allow_dir: If True, allows selecting directories instead of files
        allow_both: If True, allows selecting both files AND directories (shows select badges on dirs)
        default: Default directory path

    Returns:
        dbc.Modal component
    """
    placeholder = (
        "No file or directory selected"
        if allow_both
        else ("No directory selected" if allow_dir else "No file selected")
    )

    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle(title)),
            dbc.ModalBody(
                [
                    _create_browser_navigation(modal_id, default),
                    _create_file_list(modal_id),
                    dcc.Store(
                        id=f"{modal_id}-config",
                        data={
                            "extension": file_extension,
                            "allow_dir": allow_dir,
                            "allow_both": allow_both,
                        },
                    ),
                ]
            ),
            dbc.ModalFooter(
                [
                    dbc.InputGroup(
                        [
                            dbc.Col(
                                create_input(
                                    id=f"{modal_id}-selected",
                                    placeholder=placeholder,
                                    disabled=True,
                                    className="mt-3",
                                ),
                            ),
                        ],
                        className="g-2",
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
    allow_dir: bool = False,
    default: str = "/data/tRNA",
) -> dbc.Modal:
    """Create a file export/save modal with format selection.

    Args:
        modal_id: Unique identifier for the modal
        title: Modal title
        file_extensions: List of allowed file extensions
        default_extension: Default file extension (e.g., '.html')
        allow_dir: If True, allows selecting directories instead of files
        default: Default directory path

    Returns:
        dbc.Modal component
    """
    default_filename = f"out{default_extension}"

    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle(title)),
            dbc.ModalBody(
                [
                    _create_browser_navigation(modal_id, default),
                    _create_file_list(modal_id),
                    dcc.Store(
                        id=f"{modal_id}-config",
                        data={"extension": default_extension, "allow_dir": allow_dir},
                    ),
                ]
            ),
            dbc.ModalFooter(
                [
                    # Filename input + format dropdown
                    dbc.InputGroup(
                        [
                            dbc.Col(
                                create_input(
                                    id=f"{modal_id}-input-path",
                                    value=default_filename,
                                    placeholder="Enter filename...",
                                    className="mt-3",
                                ),
                                width=9,
                            ),
                            dbc.Col(
                                create_dropdown(
                                    id=f"{modal_id}-format",
                                    options=file_extensions,
                                    value=default_extension,
                                    clearable=False,
                                    style={"marginTop": "16px"},
                                ),
                                width=3,
                            ),
                        ],
                        className="g-2",
                    ),
                    # Action buttons
                    html.Div(
                        [
                            create_button(
                                "Cancel", id=f"{modal_id}-cancel", color="danger"
                            ),
                            create_button(
                                "Save", id=f"{modal_id}-save", color="success"
                            ),
                        ],
                        className="d-flex justify-content-end gap-2 mt-3",
                    ),
                ]
            ),
        ],
        id=modal_id,
        size="lg",
        is_open=False,
    )
