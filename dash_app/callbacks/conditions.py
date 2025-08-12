from dash import Input, Output, State, callback, ctx, ALL
from dash.exceptions import PreventUpdate

from ..layout.components import create_condition_card
from .initialization import get_visualizer


def register_condition_callbacks():
    """Register all condition management callbacks."""
    
    @callback(
        [Output("conditions", "children"), 
         Output("alert", "children", allow_duplicate=True),
         Output("alert", "is_open", allow_duplicate=True), 
         Output("files-store", "data", allow_duplicate=True),
         Output("conditions-metadata", "data", allow_duplicate=True),
         Output("plot-trigger", "data", allow_duplicate=True)],
        Input("add-condition-button", "n_clicks"),
        [State("files-store", "data"), 
         State("contig", "value"),
         State("position", "value"), 
         State("target-base", "value"), 
         State("max-reads", "value"), 
         State("condition-label", "value"),
         State("condition-color", "value"), 
         State("line-style", "value"), 
         State("line-width", "value"), 
         State("opacity", "value"), 
         State("session-id", "data"),
         State("conditions", "children"),
         State("conditions-metadata", "data"),
         State("plot-trigger", "data")],
        prevent_initial_call=True
    )
    def add_condition(n_clicks, files, contig, pos, target_base, max_reads, 
                     label, color, line_style, line_width, opacity, 
                     session_id, current_conditions, metadata, trigger):
        """Add a new condition."""
        
        # Validate inputs
        if not files.get('bam') or not files.get('pod5'):
            return current_conditions, "Please select both files", True, files, metadata, trigger
        if not contig or not pos:
            return current_conditions, "Please fill required fields", True, files, metadata, trigger
        
        # Get visualizer instance
        viz = get_visualizer(session_id)
        if not viz:
            return current_conditions, "Please initialize visualizer first", True, files, metadata, trigger
        
        # Generate label if not provided
        label = label or f"{contig}:{pos}"
        
        # Add condition to visualizer
        viz.add_condition(
            bam_path=str(files['bam']),
            pod5_path=str(files['pod5']),
            contig=contig,
            target_position=int(pos),
            target_base=target_base,
            max_reads=max_reads,
            label=label,
            color=color,
            line_style=line_style,
            line_width=line_width,
            alpha=opacity/100
        )
        
        # Store condition metadata
        metadata[label] = {
            'color': color,
            'line_style': line_style,
            'line_width': line_width,
            'opacity': opacity
        }
        
        # Create new condition card
        new_condition = create_condition_card(
            label=label,
            color=color,
            line_style=line_style,
            line_width=line_width,
            opacity=opacity
        )
        
        # Update conditions list
        if current_conditions is None:
            conditions = [new_condition]
        else:
            conditions = current_conditions + [new_condition]
        
        # Clear file selections for next condition and trigger plot update
        return conditions, f"Added: {label}", True, {}, metadata, trigger + 1
    
    @callback(
        [Output("conditions", "children", allow_duplicate=True),
         Output("conditions-metadata", "data", allow_duplicate=True),
         Output("plot-trigger", "data", allow_duplicate=True)],
        Input({"type": "remove-btn", "index": ALL}, "n_clicks"),
        [State({"type": "remove-btn", "index": ALL}, "id"),
         State("session-id", "data"), 
         State("conditions-metadata", "data"),
         State("plot-trigger", "data")],
        prevent_initial_call=True
    )
    def remove_condition(clicks, ids, session_id, metadata, trigger):
        """Remove a condition."""
        if not any(clicks):
            raise PreventUpdate
        
        # Use ctx.triggered_id to find which button was actually clicked
        from dash import ctx
        
        triggered_id = ctx.triggered_id
        if not triggered_id or not isinstance(triggered_id, dict):
            raise PreventUpdate
        
        label_to_remove = triggered_id.get("index")
        if not label_to_remove:
            raise PreventUpdate
        
        # Get visualizer and remove condition
        viz = get_visualizer(session_id)
        if viz:
            viz.remove_condition(label_to_remove)
        
        # Remove from metadata
        if label_to_remove in metadata:
            del metadata[label_to_remove]
        
        # Rebuild conditions list from remaining metadata
        conditions = []
        for label, style_data in metadata.items():
            conditions.append(
                create_condition_card(
                    label=label,
                    color=style_data['color'],
                    line_style=style_data['line_style'],
                    line_width=style_data['line_width'],
                    opacity=style_data['opacity']
                )
            )
        
        return conditions, metadata, trigger + 1
    
    @callback(
        [Output("alert", "children", allow_duplicate=True),
         Output("alert", "is_open", allow_duplicate=True),
         Output("conditions-metadata", "data", allow_duplicate=True),
         Output("plot-trigger", "data", allow_duplicate=True)],
        Input({"type": "update-btn", "index": ALL}, "n_clicks"),
        [State({"type": "update-btn", "index": ALL}, "id"),
         State({"type": "color-edit", "index": ALL}, "value"),
         State({"type": "line-style-edit", "index": ALL}, "value"),
         State({"type": "line-width-edit", "index": ALL}, "value"),
         State({"type": "opacity-edit", "index": ALL}, "value"),
         State({"type": "color-edit", "index": ALL}, "id"),
         State("session-id", "data"),
         State("conditions-metadata", "data"),
         State("plot-trigger", "data")],
        prevent_initial_call=True
    )
    def update_condition_style(clicks, btn_ids, colors, line_styles, line_widths, 
                              opacities, color_ids, session_id, metadata, trigger):
        """Update condition visualization style."""
        if not any(clicks):
            raise PreventUpdate
        
        # Find which button was ACTUALLY clicked using ctx.triggered_id
        from dash import ctx
        
        triggered_id = ctx.triggered_id
        if not triggered_id or not isinstance(triggered_id, dict):
            raise PreventUpdate
        
        clicked_label = triggered_id.get("index")
        if not clicked_label:
            raise PreventUpdate
        
        # Get visualizer
        viz = get_visualizer(session_id)
        if not viz:
            return "Visualizer not initialized", True, metadata, trigger
        
        # Find the index of the clicked label in the color_ids array
        correct_idx = None
        for i, id_dict in enumerate(color_ids):
            if id_dict["index"] == clicked_label:
                correct_idx = i
                break
        
        if correct_idx is None:
            return f"Could not find inputs for condition: {clicked_label}", True, metadata, trigger
        
        # Update metadata with the correct values
        metadata[clicked_label] = {
            'color': colors[correct_idx],
            'line_style': line_styles[correct_idx],
            'line_width': line_widths[correct_idx],
            'opacity': opacities[correct_idx]
        }
        
        # Update the condition's visualization parameters
        try:
            # Check if visualizer has the update method
            if hasattr(viz, 'update_condition'):
                viz.update_condition(
                    label=clicked_label,
                    color=colors[correct_idx],
                    line_style=line_styles[correct_idx],
                    line_width=line_widths[correct_idx],
                    alpha=opacities[correct_idx]/100
                )
            else:
                # If the method doesn't exist, we need to update the condition another way
                # Get all conditions and update the specific one
                conditions = getattr(viz, 'conditions', {})
                if clicked_label in conditions:
                    condition = conditions[clicked_label]
                    # Update the style attributes if they exist
                    if hasattr(condition, 'color'):
                        condition.color = colors[correct_idx]
                    if hasattr(condition, 'line_style'):
                        condition.line_style = line_styles[correct_idx]
                    if hasattr(condition, 'line_width'):
                        condition.line_width = line_widths[correct_idx]
                    if hasattr(condition, 'alpha'):
                        condition.alpha = opacities[correct_idx]/100
            
            return f"Updated style for: {clicked_label}", True, metadata, trigger + 1
        except Exception as e:
            return f"Error updating style: {str(e)}", True, metadata, trigger