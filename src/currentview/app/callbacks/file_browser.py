from pathlib import Path

from dash import Input, Output, State, callback, ctx, ALL, html, no_update
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

from .initialization import get_visualizer
from ..utils.file_utils import get_directory_contents


# ── Path helpers ──────────────────────────────────────────────────────────────


def _resolve_path(trigger, prefix: str, current: str) -> str:
    if trigger == f"{prefix}-modal-up":
        return str(Path(current).parent)
    if isinstance(trigger, dict) and trigger.get("type") == f"{prefix}-dir":
        return trigger["path"]
    # covers: browse, go, format-change — all use current typed value
    return str(Path(current).resolve())


# ── List builders ─────────────────────────────────────────────────────────────


def _dir_item(item: dict, prefix: str, selectable: bool) -> dbc.ListGroupItem:
    if selectable:
        return dbc.ListGroupItem(
            [
                html.Div(
                    [
                        html.I(className="bi bi-folder-fill text-warning me-2"),
                        html.Span(item["name"]),
                    ],
                    id={"type": f"{prefix}-dir", "path": item["path"]},
                    n_clicks=0,
                    style={"cursor": "pointer", "flex": "1"},
                ),
                dbc.Badge(
                    "Select",
                    color="success",
                    id={"type": f"{prefix}-select-dir", "path": item["path"]},
                    style={"cursor": "pointer"},
                ),
            ],
            className="d-flex align-items-center",
            action=False,
        )
    return dbc.ListGroupItem(
        [html.I(className="bi bi-folder-fill text-warning me-2"), item["name"]],
        action=True,
        id={"type": f"{prefix}-dir", "path": item["path"]},
        n_clicks=0,
        style={"cursor": "pointer"},
    )


def _build_file_list(items: list, prefix: str, mode: str) -> dbc.ListGroup:
    allow_dir = mode in ("dir", "both")
    show_files = mode in ("file", "both")
    children = []

    for item in items:
        if item["type"] == "dir":
            is_parent = item["name"] == ".."
            selectable = allow_dir and not is_parent
            children.append(_dir_item(item, prefix, selectable))
        elif show_files:
            children.append(
                dbc.ListGroupItem(
                    [
                        html.I(className="bi bi-file-earmark text-primary me-2"),
                        f"{item['name']} ({item.get('size', '')})",
                    ],
                    action=True,
                    id={"type": f"{prefix}-file", "path": item["path"]},
                    n_clicks=0,
                    style={"cursor": "pointer"},
                )
            )

    return dbc.ListGroup(children, flush=True)


# ── Registration ──────────────────────────────────────────────────────────────


def register_file_callbacks():
    for prefix, ext in [("bam", ".bam"), ("pod5", ".pod5")]:
        _register_browser(prefix, ext)
    _register_saver("export")


def _register_browser(prefix: str, extension: str):

    @callback(
        Output(f"{prefix}-modal", "is_open"),
        Input(f"{prefix}-browse", "n_clicks"),
        Input(f"{prefix}-modal-cancel", "n_clicks"),
        Input(f"{prefix}-modal-select", "n_clicks"),
        prevent_initial_call=True,
    )
    def toggle_modal(browse, cancel, select):
        return ctx.triggered_id == f"{prefix}-browse"

    @callback(
        Output(f"{prefix}-modal-list", "children"),
        Output(f"{prefix}-modal-path", "value"),
        Input(f"{prefix}-browse", "n_clicks"),
        Input(f"{prefix}-modal-go", "n_clicks"),
        Input(f"{prefix}-modal-up", "n_clicks"),
        Input({"type": f"{prefix}-dir", "path": ALL}, "n_clicks"),
        State(f"{prefix}-modal-path", "value"),
        State(f"{prefix}-modal-config", "data"),
        prevent_initial_call=True,
    )
    def update_browser(browse, go, up, dir_clicks, current, config):
        trigger = ctx.triggered_id
        if isinstance(trigger, dict) and not any(dir_clicks):
            raise PreventUpdate

        mode = (config or {}).get("mode", "file")
        show_files = mode in ("file", "both")
        path = _resolve_path(trigger, prefix, current)

        items, actual_path = get_directory_contents(path, extension, show_files)
        return _build_file_list(items, prefix, mode), actual_path

    @callback(
        Output(f"{prefix}-modal-selected", "value"),
        Input({"type": f"{prefix}-file", "path": ALL}, "n_clicks"),
        Input({"type": f"{prefix}-select-dir", "path": ALL}, "n_clicks"),
        prevent_initial_call=True,
    )
    def select_item(file_clicks, dir_clicks):
        trigger = ctx.triggered_id
        if not trigger:
            raise PreventUpdate
        return trigger["path"]

    @callback(
        Output(f"{prefix}-display", "value"),
        Output("files-store", "data", allow_duplicate=True),
        Input(f"{prefix}-modal-select", "n_clicks"),
        State(f"{prefix}-modal-selected", "value"),
        State("files-store", "data"),
        prevent_initial_call=True,
    )
    def confirm_selection(n, selected, files):
        if not selected:
            raise PreventUpdate
        return selected, {**files, prefix: selected}


def _register_saver(prefix: str):

    @callback(
        Output("alert", "children", allow_duplicate=True),
        Output("alert", "is_open", allow_duplicate=True),
        Output(f"{prefix}-modal", "is_open"),
        Input(f"{prefix}-browse", "n_clicks"),
        Input(f"{prefix}-modal-cancel", "n_clicks"),
        Input(f"{prefix}-modal-save", "n_clicks"),
        State("session-id", "data"),
        State("tabs", "active_tab"),
        prevent_initial_call=True,
    )
    def toggle_modal(browse, cancel, save, session_id, active_tab):
        triggered = ctx.triggered_id

        # Cancel or save just close the modal
        if triggered in (f"{prefix}-modal-cancel", f"{prefix}-modal-save"):
            return no_update, no_update, False

        # Browse: validate before opening
        viz = get_visualizer(session_id)
        if not viz:
            return "No visualizer found", True, False
        if viz.n_conditions == 0:
            return f"No {active_tab} plot is currently available", True, False

        return None, False, True

    @callback(
        Output(f"{prefix}-modal-list", "children"),
        Output(f"{prefix}-modal-path", "value"),
        Input(f"{prefix}-browse", "n_clicks"),
        Input(f"{prefix}-modal-go", "n_clicks"),
        Input(f"{prefix}-modal-up", "n_clicks"),
        Input({"type": f"{prefix}-dir", "path": ALL}, "n_clicks"),
        Input(f"{prefix}-modal-format", "value"),
        State(f"{prefix}-modal-path", "value"),
        State(f"{prefix}-modal-config", "data"),
        prevent_initial_call=True,
    )
    def update_browser(browse, go, up, dir_clicks, fmt, current, config):
        trigger = ctx.triggered_id
        if isinstance(trigger, dict) and not any(dir_clicks):
            raise PreventUpdate

        mode = (config or {}).get("mode", "file")
        show_files = mode in ("file", "both")
        path = _resolve_path(trigger, prefix, current)
        ext = fmt or (config or {}).get("extension", "")

        items, actual_path = get_directory_contents(path, ext, show_files)
        return _build_file_list(items, prefix, mode), actual_path

    @callback(
        Output(f"{prefix}-modal-input-path", "value"),
        Input(f"{prefix}-modal-format", "value"),
        State(f"{prefix}-modal-input-path", "value"),
        prevent_initial_call=True,
    )
    def update_filename_extension(fmt, current):
        if current and not current.endswith(fmt):
            return str(Path(current).with_suffix(fmt))
        return current
