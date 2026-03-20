import pysam
from dash import Input, Output, State, callback, ctx, ALL, html, no_update
from dash.exceptions import PreventUpdate

from ..layout.components import create_condition_card
from .initialization import get_visualizer


# ── Helpers ───────────────────────────────────────────────────────────────────


def _validate_inputs(files: dict, contig, pos) -> list[str]:
    errors = []
    if not files.get("bam"):
        errors.append("Please select a BAM file")
    if not files.get("pod5"):
        errors.append("Please select a POD5 directory")
    if not contig:
        errors.append("Please select a valid contig")
    if not pos:
        errors.append("Please select a target position")
    else:
        try:
            if int(pos) <= 0:
                raise ValueError
        except (ValueError, TypeError):
            errors.append("Position must be a positive integer")
    return errors


def _alert_error(msg, conditions, files, metadata):
    """Return tuple for a danger alert without changing conditions."""
    return (
        conditions,
        msg,
        True,
        "danger",
        files,
        files.get("bam"),
        files.get("pod5"),
        metadata,
        no_update,
    )


def _build_error_content(messages: list[str]) -> list:
    content = ["Please fill all of the required fields:"]
    for msg in messages:
        content.extend([html.Br(), f"• {msg}"])
    return content


def _rebuild_condition_cards(metadata: dict) -> list:
    return [
        create_condition_card(
            label=label,
            color=s["color"],
            line_style=s["line_style"],
            line_width=s["line_width"],
            opacity=s["opacity"],
        )
        for label, s in metadata.items()
    ]


def _get_triggered_label() -> str | None:
    """Return the 'index' from ctx.triggered_id if it's a pattern-match dict."""
    tid = ctx.triggered_id
    if not tid or not isinstance(tid, dict):
        return None
    return tid.get("index") or None


# ── Callbacks ─────────────────────────────────────────────────────────────────


def register_condition_callbacks():

    @callback(
        Output("gmm-inputs", "style"),
        Output("umap-inputs", "style"),
        Input("tabs", "active_tab"),
    )
    def toggle_input_bars(active_tab):
        show = {"display": "block"}
        hide = {"display": "none"}
        return (
            show if active_tab == "gmm" else hide,
            show if active_tab == "umap" else hide,
        )

    @callback(
        Output("contig", "options"),
        Output("contig", "disabled"),
        Input("files-store", "data"),
    )
    def populate_contig(files):
        bam_file = files.get("bam")
        if not bam_file:
            return [], True
        with pysam.AlignmentFile(bam_file) as af:
            refs = [{"label": r, "value": r} for r in af.references]
        return refs, False

    @callback(
        Output("conditions", "children"),
        Output("add-condition-alert", "children", allow_duplicate=True),
        Output("add-condition-alert", "is_open", allow_duplicate=True),
        Output("add-condition-alert", "color", allow_duplicate=True),
        Output("files-store", "data", allow_duplicate=True),
        Output("bam-display", "value", allow_duplicate=True),
        Output("pod5-display", "value", allow_duplicate=True),
        Output("conditions-metadata", "data", allow_duplicate=True),
        Output("plot-trigger", "data", allow_duplicate=True),
        Input("add-condition-button", "n_clicks"),
        State("files-store", "data"),
        State("contig", "value"),
        State("position", "value"),
        State("molecule-type-store", "data"),
        State("matched-query-base", "data"),
        State("max-reads", "value"),
        State("condition-label", "value"),
        State("exclude-indels", "value"),
        State("exclude-non-primaries", "value"),
        State("condition-color", "value"),
        State("line-style", "value"),
        State("line-width", "value"),
        State("opacity", "value"),
        State("session-id", "data"),
        State("conditions", "children"),
        State("conditions-metadata", "data"),
        State("plot-trigger", "data"),
        prevent_initial_call=True,
    )
    def add_condition(
        n_clicks,
        files,
        contig,
        pos,
        molecule_type,
        matched_query_base,
        max_reads,
        label,
        exclude_indels,
        exclude_non_primaries,
        color,
        line_style,
        line_width,
        opacity,
        session_id,
        current_conditions,
        metadata,
        trigger,
    ):
        errors = _validate_inputs(files, contig, pos)
        if errors:
            return _alert_error(
                _build_error_content(errors), current_conditions, files, metadata
            )

        viz = get_visualizer(session_id)
        if not viz:
            return _alert_error(
                "Please initialize the visualizer first",
                current_conditions,
                files,
                metadata,
            )

        label = label or f"{contig}:{pos}"

        try:
            viz.add_condition(
                bam_path=str(files["bam"]),
                pod5_path=str(files["pod5"]),
                contig=contig,
                target_position=int(pos),
                molecule_type=molecule_type,
                matched_query_base=matched_query_base or None,
                exclude_reads_with_indels=exclude_indels,
                ignore_non_primaries=exclude_non_primaries,
                max_reads=max_reads,
                label=label,
                color=color,
                line_style=line_style,
                line_width=line_width,
                alpha=opacity / 100,
            )
        except Exception as e:
            return _alert_error(str(e), current_conditions, files, metadata)

        # Guard: verify the condition was actually stored (e.g. no reads found)
        if label not in viz.get_condition_names():
            return _alert_error(
                f"No reads found for '{label}' at {contig}:{pos}. "
                "Check that the BAM and POD5 files match and the position exists.",
                current_conditions,
                files,
                metadata,
            )

        metadata[label] = {
            "color": color,
            "line_style": line_style,
            "line_width": line_width,
            "opacity": opacity,
        }

        conditions = (current_conditions or []) + [
            create_condition_card(
                label=label,
                color=color,
                line_style=line_style,
                line_width=line_width,
                opacity=opacity,
            )
        ]

        files.pop("bam")
        files.pop("pod5")

        return (
            conditions,
            f"Added: {label}",
            True,
            "success",
            files,
            None,
            None,
            metadata,
            trigger + 1,
        )

    @callback(
        Output("conditions", "children", allow_duplicate=True),
        Output("conditions-metadata", "data", allow_duplicate=True),
        Output("plot-trigger", "data", allow_duplicate=True),
        Input({"type": "remove-btn", "index": ALL}, "n_clicks"),
        State({"type": "remove-btn", "index": ALL}, "id"),
        State("session-id", "data"),
        State("conditions-metadata", "data"),
        State("plot-trigger", "data"),
        prevent_initial_call=True,
    )
    def remove_condition(clicks, ids, session_id, metadata, trigger):
        if not any(clicks):
            raise PreventUpdate

        label = _get_triggered_label()
        if not label:
            raise PreventUpdate

        viz = get_visualizer(session_id)
        if viz:
            viz.remove_condition(label)

        metadata.pop(label, None)

        return _rebuild_condition_cards(metadata), metadata, trigger + 1

    @callback(
        Output("conditions", "children", allow_duplicate=True),
        Output("alert", "children", allow_duplicate=True),
        Output("alert", "is_open", allow_duplicate=True),
        Output("conditions-metadata", "data", allow_duplicate=True),
        Output("plot-trigger", "data", allow_duplicate=True),
        Input({"type": "update-btn", "index": ALL}, "n_clicks"),
        State({"type": "update-btn", "index": ALL}, "id"),
        State({"type": "color-edit", "index": ALL}, "value"),
        State({"type": "line-style-edit", "index": ALL}, "value"),
        State({"type": "line-width-edit", "index": ALL}, "value"),
        State({"type": "opacity-edit", "index": ALL}, "value"),
        State({"type": "color-edit", "index": ALL}, "id"),
        State("session-id", "data"),
        State("conditions-metadata", "data"),
        State("plot-trigger", "data"),
        prevent_initial_call=True,
    )
    def update_condition_style(
        clicks,
        btn_ids,
        colors,
        line_styles,
        line_widths,
        opacities,
        color_ids,
        session_id,
        metadata,
        trigger,
    ):
        if not any(clicks):
            raise PreventUpdate

        label = _get_triggered_label()
        if not label:
            raise PreventUpdate

        viz = get_visualizer(session_id)
        if not viz:
            return no_update, "Visualizer not initialized", True, metadata, trigger

        idx = next((i for i, d in enumerate(color_ids) if d["index"] == label), None)
        if idx is None:
            return (
                no_update,
                f"Could not find inputs for: {label}",
                True,
                metadata,
                trigger,
            )

        new_style = {
            "color": colors[idx],
            "line_style": line_styles[idx],
            "line_width": line_widths[idx],
            "opacity": opacities[idx],
        }

        try:
            viz.update_condition(
                label=label,
                color=new_style["color"],
                line_style=new_style["line_style"],
                line_width=new_style["line_width"],
                alpha=new_style["opacity"] / 100,
            )
        except Exception as e:
            return no_update, f"Error updating style: {e}", True, metadata, trigger

        metadata[label] = new_style

        return (
            _rebuild_condition_cards(metadata),
            f"Updated style for: {label}",
            True,
            metadata,
            trigger + 1,
        )
