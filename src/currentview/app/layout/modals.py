import dash_bootstrap_components as dbc
from dash import dcc, html
from pathlib import Path
from typing import Optional
from .elements import create_input, create_button, create_dropdown


def create_input_modal(
    modal_id: str,
    title: str,
    file_extension: Optional[str] = None,
    allow_dir: bool = False,
    default: str = "/data/tRNA",
) -> dbc.Modal:
    """Create a reusable file browser modal.

    Args:
        modal_id: Unique identifier for the modal
        title: Modal title
        file_extension: File extension to filter (e.g., '.bam'). None shows all files.
        allow_dir: If True, allows selecting directories instead of files
        default: Default directory path

    Returns:
        dbc.Modal component
    """
    placeholder = "No directory selected" if allow_dir else "No file selected"

    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle(title)),
            dbc.ModalBody(
                [
                    dbc.InputGroup(
                        [
                            # dbc.Input(id=f"{modal_id}-path", value=str(Path(default))),
                            create_input(
                                id=f"{modal_id}-path", value=str(Path(default))
                            ),
                            # dbc.Button("Go", id=f"{modal_id}-go", size="sm"),
                            create_button(
                                "Go", id=f"{modal_id}-go", size="sm", color="primary"
                            ),
                            # dbc.Button("↑", id=f"{modal_id}-up", size="sm"),
                            create_button(
                                "↑", id=f"{modal_id}-up", size="sm", color="primary"
                            ),
                        ],
                        size="sm",
                        className="mb-3",
                    ),
                    html.Div(
                        id=f"{modal_id}-list",
                        style={
                            "height": "400px",
                            "overflowY": "auto",
                            "padding": "0.5rem",
                            "borderRadius": "8px",
                            "border": "1px solid #e5e7eb",
                            "transition": "all 0.2s ease",
                        },
                    ),
                    # dbc.Input(
                    #    id=f"{modal_id}-selected",
                    #    placeholder=placeholder,
                    #    disabled=True,
                    #    className="mt-3"
                    # )
                    # Store modal configuration
                    dcc.Store(
                        id=f"{modal_id}-config",
                        data={"extension": file_extension, "allow_dir": allow_dir},
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
                        className="g-2",  # small gutter spacing
                    ),
                    # dbc.Button("Cancel", id=f"{modal_id}-cancel", color="secondary"),
                    create_button("Cancel", id=f"{modal_id}-cancel", color="danger"),
                    # dbc.Button("Select", id=f"{modal_id}-select", color="primary"),
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
    file_extensions: Optional[str] = None,
    default_extension: Optional[str] = None,
    allow_dir: bool = False,
    default: str = "/data/tRNA",
) -> dbc.Modal:
    """Create a reusable file browser modal.

    Args:
        modal_id: Unique identifier for the modal
        title: Modal title
        file_extension: File extension to filter (e.g., '.bam'). None shows all files.
        allow_dir: If True, allows selecting directories instead of files
        default: Default directory path

    Returns:
        dbc.Modal component
    """
    value = f"out{default_extension}"

    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle(title)),
            dbc.ModalBody(
                [
                    dbc.InputGroup(
                        [
                            # dbc.Input(id=f"{modal_id}-path", value=str(Path(default))),
                            create_input(
                                id=f"{modal_id}-path", value=str(Path(default))
                            ),
                            # dbc.Button("Go", id=f"{modal_id}-go", size="sm"),
                            create_button(
                                "Go", id=f"{modal_id}-go", size="sm", color="primary"
                            ),
                            # dbc.Button("↑", id=f"{modal_id}-up", size="sm"),
                            create_button(
                                "↑", id=f"{modal_id}-up", size="sm", color="primary"
                            ),
                        ],
                        size="sm",
                        className="mb-3",
                    ),
                    html.Div(
                        id=f"{modal_id}-list",
                        style={
                            "height": "400px",
                            "overflowY": "auto",
                            "padding": "0.5rem",
                            "borderRadius": "8px",
                            "border": "1px solid #e5e7eb",
                            "transition": "all 0.2s ease",
                        },
                    ),
                    # dbc.Input(
                    #    id=f"{modal_id}-selected",
                    #    placeholder=placeholder,
                    #    disabled=True,
                    #    className="mt-3"
                    # ),
                    # Store modal configuration
                    dcc.Store(
                        id=f"{modal_id}-config",
                        data={"extension": default_extension, "allow_dir": allow_dir},
                    ),
                ]
            ),
            dbc.ModalFooter(
                [
                    # First row: input + dropdown
                    dbc.InputGroup(
                        [
                            dbc.Col(
                                create_input(
                                    id=f"{modal_id}-input-path",
                                    value=value,
                                    disabled=False,
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
                        className="g-2",  # small gutter spacing
                    ),
                    # Second row: buttons aligned right
                    dbc.Row(
                        dbc.Col(
                            [
                                create_button(
                                    "Cancel", id=f"{modal_id}-cancel", color="danger"
                                ),
                                create_button(
                                    "Save", id=f"{modal_id}-save", color="success"
                                ),
                            ],
                            width="auto",
                            className="d-flex justify-content-end gap-2",  # align right + spacing
                        ),
                        className="mt-3",
                    ),
                ]
            ),
        ],
        id=modal_id,
        size="lg",
        is_open=False,
    )
