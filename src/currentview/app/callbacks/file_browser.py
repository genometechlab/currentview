from dash import Input, Output, State, callback, ctx, ALL
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from dash import html
from pathlib import Path

from .initialization import get_visualizer
from ..utils.file_utils import get_directory_contents


# ============================================================================
# Shared Helpers
# ============================================================================


def _resolve_path(trigger, prefix: str, current: str) -> str:
    """Resolve the target path based on the callback trigger."""
    if trigger == f"{prefix}-modal-up":
        return str(Path(current).parent)
    if isinstance(trigger, dict) and trigger.get("type") == f"{prefix}-dir":
        return trigger["path"]
    return str(Path(current).resolve())


def _build_file_list(items: list, prefix: str, mode: str) -> dbc.ListGroup:
    """Build a ListGroup from directory items.

    Args:
        items:  Output of get_directory_contents
        prefix: Modal prefix (e.g. "bam", "pod5", "export")
        mode:   "file" | "dir" | "both"
    """
    allow_dir = mode in ("dir", "both")
    show_files = mode in ("file", "both")
    children = []

    for item in items:
        if item["type"] == "dir":
            is_parent = item["name"] == ".."
            if allow_dir and not is_parent:
                # Navigable + selectable directory
                children.append(
                    dbc.ListGroupItem(
                        [
                            html.Div(
                                [
                                    html.I(
                                        className="bi bi-folder-fill text-warning me-2"
                                    ),
                                    html.Span(item["name"]),
                                ],
                                id={"type": f"{prefix}-dir", "path": item["path"]},
                                n_clicks=0,
                                style={"cursor": "pointer", "flex": "1"},
                            ),
                            dbc.Badge(
                                "Select",
                                color="success",
                                id={
                                    "type": f"{prefix}-select-dir",
                                    "path": item["path"],
                                },
                                style={"cursor": "pointer"},
                            ),
                        ],
                        className="d-flex align-items-center",
                        action=False,
                    )
                )
            else:
                # Navigation-only directory (or parent "..")
                children.append(
                    dbc.ListGroupItem(
                        [
                            html.I(className="bi bi-folder-fill text-warning me-2"),
                            item["name"],
                        ],
                        action=True,
                        id={"type": f"{prefix}-dir", "path": item["path"]},
                        n_clicks=0,
                        style={"cursor": "pointer"},
                    )
                )

        elif show_files:
            children.append(
                dbc.ListGroupItem(
                    [
                        html.I(className="bi bi-file-earmark text-primary me-2"),
                        item["name"] + f" ({item.get('size', '')})",
                    ],
                    action=True,
                    id={"type": f"{prefix}-file", "path": item["path"]},
                    n_clicks=0,
                    style={"cursor": "pointer"},
                )
            )

    return dbc.ListGroup(children, flush=True)


# ============================================================================
# File Browser (BAM / POD5)
# ============================================================================


def register_file_browser_callbacks():
    """Register file browser callbacks for all file types."""
    for prefix, ext in [("bam", ".bam"), ("pod5", ".pod5")]:
        _register_browser(prefix, ext)


def _register_browser(prefix: str, extension: str):
    """Register callbacks for a single file browser modal."""

    @callback(
        Output(f"{prefix}-modal", "is_open"),
        [
            Input(f"{prefix}-browse", "n_clicks"),
            Input(f"{prefix}-modal-cancel", "n_clicks"),
            Input(f"{prefix}-modal-select", "n_clicks"),
        ],
        prevent_initial_call=True,
    )
    def toggle_modal(browse, cancel, select):
        return ctx.triggered_id == f"{prefix}-browse"

    @callback(
        [
            Output(f"{prefix}-modal-list", "children"),
            Output(f"{prefix}-modal-path", "value"),
        ],
        [
            Input(f"{prefix}-browse", "n_clicks"),
            Input(f"{prefix}-modal-go", "n_clicks"),
            Input(f"{prefix}-modal-up", "n_clicks"),
            Input({"type": f"{prefix}-dir", "path": ALL}, "n_clicks"),
        ],
        [
            State(f"{prefix}-modal-path", "value"),
            State(f"{prefix}-modal-config", "data"),
        ],
        prevent_initial_call=True,
    )
    def update_browser(browse, go, up, dir_clicks, current, config):
        trigger = ctx.triggered_id

        # Guard: ignore pattern-match trigger if no dir was actually clicked
        if isinstance(trigger, dict) and not any(dir_clicks):
            raise PreventUpdate

        path = _resolve_path(trigger, prefix, current)
        mode = (config or {}).get("mode", "file")
        show_files = mode in ("file", "both")

        items, actual_path = get_directory_contents(path, extension, show_files)
        return _build_file_list(items, prefix, mode), actual_path

    @callback(
        Output(f"{prefix}-modal-selected", "value"),
        [
            Input({"type": f"{prefix}-file", "path": ALL}, "n_clicks"),
            Input({"type": f"{prefix}-select-dir", "path": ALL}, "n_clicks"),
        ],
        prevent_initial_call=True,
    )
    def select_item(file_clicks, dir_clicks):
        trigger = ctx.triggered_id
        if not trigger:
            raise PreventUpdate
        return trigger["path"]

    @callback(
        [
            Output(f"{prefix}-display", "value"),
            Output("files-store", "data", allow_duplicate=True),
        ],
        Input(f"{prefix}-modal-select", "n_clicks"),
        [
            State(f"{prefix}-modal-selected", "value"),
            State("files-store", "data"),
        ],
        prevent_initial_call=True,
    )
    def confirm_selection(n, selected, files):
        if not selected:
            raise PreventUpdate
        files[prefix] = selected
        return selected, files


# ============================================================================
# File Saver (Export)
# ============================================================================


def register_file_saver_callbacks():
    """Register file saver callbacks for all export targets."""
    _register_saver("export")


def _register_saver(prefix: str):
    """Register callbacks for a single file saver modal."""

    @callback(
        [
            Output("alert", "children", allow_duplicate=True),
            Output("alert", "is_open", allow_duplicate=True),
            Output(f"{prefix}-modal", "is_open"),
        ],
        [
            Input(f"{prefix}-browse", "n_clicks"),
            Input(f"{prefix}-modal-cancel", "n_clicks"),
            Input(f"{prefix}-modal-save", "n_clicks"),
        ],
        [
            State("session-id", "data"),
            State("tabs", "active_tab"),
        ],
        prevent_initial_call=True,
    )
    def toggle_modal(browse, cancel, save, session_id, active_tab):
        if not browse:
            raise PreventUpdate

        viz = get_visualizer(session_id)
        if not viz:
            return "No visualizer found", True, False
        if viz.n_conditions == 0:
            return f"No {active_tab} plot is currently available", True, False

        return None, False, ctx.triggered_id == f"{prefix}-browse"

    @callback(
        [
            Output(f"{prefix}-modal-list", "children"),
            Output(f"{prefix}-modal-path", "value"),
        ],
        [
            Input(f"{prefix}-browse", "n_clicks"),
            Input(f"{prefix}-modal-go", "n_clicks"),
            Input(f"{prefix}-modal-up", "n_clicks"),
            Input({"type": f"{prefix}-dir", "path": ALL}, "n_clicks"),
            Input(f"{prefix}-modal-format", "value"),
        ],
        [
            State(f"{prefix}-modal-path", "value"),
            State(f"{prefix}-modal-config", "data"),
        ],
        prevent_initial_call=True,
    )
    def update_browser(browse, go, up, dir_clicks, fmt, current, config):
        trigger = ctx.triggered_id

        if isinstance(trigger, dict) and not any(dir_clicks):
            raise PreventUpdate

        path = _resolve_path(trigger, prefix, current)
        mode = (config or {}).get("mode", "file")
        show_files = mode in ("file", "both")

        items, actual_path = get_directory_contents(path, fmt, show_files)
        return _build_file_list(items, prefix, mode), actual_path

    @callback(
        Output(f"{prefix}-modal-input-path", "value"),
        Input(f"{prefix}-modal-format", "value"),
        State(f"{prefix}-modal-input-path", "value"),
        prevent_initial_call=True,
    )
    def update_filename_extension(fmt, current):
        """Update the filename extension when format changes."""
        if current and not current.endswith(fmt):
            return str(Path(current).with_suffix(fmt))
        return current
