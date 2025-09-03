from dash import Input, Output, State, callback, ctx, ALL
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from dash import html
from pathlib import Path
from .initialization import get_visualizer

from ..utils.file_utils import get_directory_contents


def register_file_browser_callbacks():
    """Register all file browser related callbacks."""
    
    # Register callbacks for both file types
    for prefix, ext in [("bam", ".bam"), ("pod5", ".pod5")]:
        register_single_browser_callbacks(prefix, ext)


def register_single_browser_callbacks(prefix: str, extension: str):
    """Register callbacks for a single file browser type."""
    
    @callback(
        Output(f"{prefix}-modal", "is_open"),
        [Input(f"{prefix}-browse", "n_clicks"), 
         Input(f"{prefix}-modal-cancel", "n_clicks"),
         Input(f"{prefix}-modal-select", "n_clicks")],
        prevent_initial_call=True
    )
    def toggle_modal(browse, cancel, select):
        """Toggle modal visibility."""
        trigger = ctx.triggered_id
        return trigger == f"{prefix}-browse"
    
    @callback(
        [Output(f"{prefix}-modal-list", "children"),
         Output(f"{prefix}-modal-path", "value")],
        [Input(f"{prefix}-browse", "n_clicks"), 
         Input(f"{prefix}-modal-go", "n_clicks"),
         Input(f"{prefix}-modal-up", "n_clicks"),
         Input({"type": f"{prefix}-dir", "path": ALL}, "n_clicks")],
        [State(f"{prefix}-modal-path", "value"),
         State(f"{prefix}-modal-config", "data")],
        prevent_initial_call=True
    )
    def update_browser(browse, go, up, dir_clicks, current, config):
        """Update file browser contents."""
        trigger = ctx.triggered_id
        
        if trigger == f"{prefix}-modal-up":
            path = str(Path(current).parent)
        elif trigger == f"{prefix}-modal-go":
            path = Path(current).resolve()
        elif trigger == f"{prefix}-browse":
            path = Path(current).resolve()
        elif isinstance(trigger, dict) and trigger.get("type") == f"{prefix}-dir":
            # Check if any directory was actually clicked
            if any(dir_clicks):
                path = trigger["path"]
            else:
                raise PreventUpdate
        else:
            path = Path(current).resolve()
        
        # Get config or use defaults
        ext = config.get("extension") if config else extension
        allow_dir = config.get("allow_dir", False) if config else False
        show_files = not allow_dir
        
        items, actual_path = get_directory_contents(path, ext, show_files)
        
        children = []
        for item in items:
            if item['type'] == 'dir':
                # For directory selection mode, make directories selectable
                if allow_dir and item['name'] != '..':
                    children.append(
                        dbc.ListGroupItem([
                            # Clickable area for navigation
                            html.Div([
                                html.I(className="bi bi-folder-fill text-warning me-2"),
                                html.Span(item['name'])
                            ], 
                            id={"type": f"{prefix}-dir", "path": item['path']},
                            style={"cursor": "pointer", "flex": "1"}),  # Takes up remaining space
                            
                            # Separate clickable area for selection
                            dbc.Badge(
                                "Select", 
                                color="primary", 
                                id={"type": f"{prefix}-select-dir", "path": item['path']},
                                style={"cursor": "pointer"}
                            )
                        ], 
                        className="d-flex align-items-center",
                        action=True  # Remove the default hover effect
                        )
                    )
                else:
                    # Regular navigation for directories
                    children.append(
                        dbc.ListGroupItem([
                            html.I(className="bi bi-folder-fill text-warning me-2"),
                            item['name']
                        ], 
                        action=True,
                        id={"type": f"{prefix}-dir", "path": item['path']},
                        style={"cursor": "pointer"},
                        n_clicks=0)  # Important for preventing event bubbling)
                    )
            else:
                # Files
                children.append(
                    dbc.ListGroupItem([
                        html.I(className="bi bi-file-earmark text-primary me-2"),
                        item['name'] + f" ({item.get('size', '')})"
                    ], 
                    action=True,
                    id={"type": f"{prefix}-file", "path": item['path']},
                    style={"cursor": "pointer"})
                )
        
        return dbc.ListGroup(children, flush=True), actual_path
    
    @callback(
        Output(f"{prefix}-modal-selected", "value"),
        [Input({"type": f"{prefix}-file", "path": ALL}, "n_clicks"),
         Input({"type": f"{prefix}-select-dir", "path": ALL}, "n_clicks")],
        [State({"type": f"{prefix}-file", "path": ALL}, "id"),
         State({"type": f"{prefix}-select-dir", "path": ALL}, "id")],
        prevent_initial_call=True
    )
    def select_item(file_clicks, dir_clicks, file_ids, dir_ids):
        """Handle item selection in the browser."""
        # Check files
        if any(file_clicks):
            idx = next(i for i, c in enumerate(file_clicks) if c)
            return file_ids[idx]["path"]
        # Check directories
        if any(dir_clicks):
            idx = next(i for i, c in enumerate(dir_clicks) if c)
            return dir_ids[idx]["path"]
        raise PreventUpdate
    
    @callback(
        [Output(f"{prefix}-display", "value"),
         Output("files-store", "data", allow_duplicate=True)],
        Input(f"{prefix}-modal-select", "n_clicks"),
        [State(f"{prefix}-modal-selected", "value"),
         State("files-store", "data")],
        prevent_initial_call=True
    )
    def confirm_selection(n, selected, files):
        """Confirm file selection and update store."""
        if not selected:
            raise PreventUpdate
        files[prefix] = selected
        return selected, files
    
    

def register_file_saver_callbacks():
    """Register all file browser related callbacks."""
    
    # Register callbacks for both file types
    for prefix, ext in [("html", ".html")]:
        register_single_saver_callbacks(prefix, ext)


def register_single_saver_callbacks(prefix: str, extension: str):
    """Register callbacks for a single file browser type."""
    
    @callback(
        [Output("alert", "children", allow_duplicate=True),
         Output("alert", "is_open", allow_duplicate=True),
         Output(f"{prefix}-modal", "is_open")],
        [Input(f"{prefix}-browse", "n_clicks"), 
         Input(f"{prefix}-modal-cancel", "n_clicks"),
         Input(f"{prefix}-modal-save", "n_clicks")],
        [State("session-id", "data"),
         State("tabs", "active_tab")],
        prevent_initial_call=True
    )
    def toggle_modal(n_clicks, cancel, select, session_id, active_tab):
        """Toggle modal visibility."""
        if not n_clicks:
            raise PreventUpdate
        
        viz = get_visualizer(session_id)
        if not viz:
            return "No visualizer to clear", True, False
        
        # Check if there are any conditions
        if viz.n_conditions == 0:
            return f"No {active_tab} plot is currently available", True, False
        
        trigger = ctx.triggered_id
        return None, False, trigger == f"{prefix}-browse"
    
    @callback(
        [Output(f"{prefix}-modal-list", "children"),
         Output(f"{prefix}-modal-path", "value")],
        [Input(f"{prefix}-browse", "n_clicks"), 
         Input(f"{prefix}-modal-go", "n_clicks"),
         Input(f"{prefix}-modal-up", "n_clicks"),
         Input({"type": f"{prefix}-dir", "path": ALL}, "n_clicks")],
        [State(f"{prefix}-modal-path", "value"),
         State(f"{prefix}-modal-config", "data")],
        prevent_initial_call=True
    )
    def update_browser(browse, go, up, dir_clicks, current, config):
        """Update file browser contents."""
        trigger = ctx.triggered_id
        
        if trigger == f"{prefix}-modal-up":
            path = str(Path(current).parent)
        elif trigger == f"{prefix}-modal-go":
            path = Path(current).resolve()
        elif trigger == f"{prefix}-browse":
            path = Path(current).resolve()
        elif isinstance(trigger, dict) and trigger.get("type") == f"{prefix}-dir":
            path = trigger["path"]
        else:
            path = Path(current).resolve()
        
        # Get config or use defaults
        ext = config.get("extension") if config else extension
        allow_dir = config.get("allow_dir", False) if config else False
        show_files = not allow_dir
        
        items, actual_path = get_directory_contents(path, ext, show_files)
        
        children = []
        for item in items:
            if item['type'] == 'dir':
                # For directory selection mode, make directories selectable
                if allow_dir and item['name'] != '..':
                    children.append(
                        dbc.ListGroupItem([
                            html.I(className="bi bi-folder-fill text-warning me-2"),
                            item['name'],
                            dbc.Badge(
                                "Select", 
                                color="primary", 
                                className="ms-auto", 
                                id={"type": f"{prefix}-select-dir", "path": item['path']}
                            )
                        ], 
                        action=True,
                        id={"type": f"{prefix}-dir", "path": item['path']},
                        style={"cursor": "pointer"})
                    )
                else:
                    # Regular navigation for directories
                    children.append(
                        dbc.ListGroupItem([
                            html.I(className="bi bi-folder-fill text-warning me-2"),
                            item['name']
                        ], 
                        action=True,
                        id={"type": f"{prefix}-dir", "path": item['path']},
                        style={"cursor": "pointer"})
                    )
            else:
                # Files
                children.append(
                    dbc.ListGroupItem([
                        html.I(className="bi bi-file-earmark text-primary me-2"),
                        item['name'] + f" ({item.get('size', '')})"
                    ], 
                    action=True,
                    id={"type": f"{prefix}-file", "path": item['path']},
                    style={"cursor": "pointer"})
                )
        
        return dbc.ListGroup(children, flush=True), actual_path
    
    @callback(
        Output(f"{prefix}-modal-inout-path", "value"),
        [Input({"type": f"{prefix}-file", "path": ALL}, "n_clicks"),
         Input({"type": f"{prefix}-select-dir", "path": ALL}, "n_clicks")],
        [State({"type": f"{prefix}-file", "path": ALL}, "id"),
         State({"type": f"{prefix}-select-dir", "path": ALL}, "id")],
        prevent_initial_call=True
    )
    def select_item(file_clicks, dir_clicks, file_ids, dir_ids):
        """Handle item selection in the browser."""
        # Check files
        if any(file_clicks):
            idx = next(i for i, c in enumerate(file_clicks) if c)
            return file_ids[idx]["path"]
        # Check directories
        if any(dir_clicks):
            idx = next(i for i, c in enumerate(dir_clicks) if c)
            return dir_ids[idx]["path"]
        raise PreventUpdate