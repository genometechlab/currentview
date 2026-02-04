# yourpkg/cli/run_tsv.py
from __future__ import annotations

import argparse
import csv
import os
import os.path as osp
from typing import Any, Dict, Optional


REQUIRED_COLS = {"bam_path", "pod5_path", "contig", "pos"}
OPTIONAL_COLS = {"max_reads", "label", "color", "opacity"}


def register_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "from_tsv",
        help="Run CurrentView with conditions provided in a TSV (N conditions).",
        description="CurrentView CLI (TSV-driven).",
    )

    parser.add_argument(
        "--conditions-tsv",
        required=True,
        help="TSV file describing conditions (one row per condition).",
    )
    parser.add_argument(
        "-k",
        "--window-size",
        type=int,
        default=9,
        help="Size of the window around the genomic position (default: 9)",
    )
    parser.add_argument(
        "--stats",
        type=str,
        default="median,std,duration",
        help="Comma-separated list of statistics to compute (default: median,std,duration)",
    )
    parser.add_argument(
        "--verbosity-level",
        type=int,
        default=1,
        help="Level of verbosity for logging (default: 1)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=".",
        help="Directory to save the output files (default: current directory)",
    )
    parser.add_argument(
        "--output-format",
        type=str,
        choices=["png", "pdf", "svg"],
        default="pdf",
        help="Format of the output files (default: pdf)",
    )
    parser.add_argument(
        "--base-dir",
        type=str,
        default=None,
        help="Base directory to resolve relative paths (default: TSV directory)",
    )

    parser.set_defaults(func=cmd_tsv)


def cmd_tsv(args: argparse.Namespace) -> int:
    from ..genomic_visualizer import CurrentView

    conditions = load_conditions_tsv(args.conditions_tsv, base_dir=args.base_dir)

    visualizer = CurrentView(
        K=args.window_size,
        stats=args.stats.split(","),
        verbosity=args.verbosity_level,
    )

    for cond in conditions:
        visualizer.add_condition(**cond)

    os.makedirs(args.output_dir, exist_ok=True)
    visualizer.save_signals(
        path=osp.join(args.output_dir, f"signals.{args.output_format}"),
        format=args.output_format,
    )
    visualizer.save_stats(
        path=osp.join(args.output_dir, f"stats.{args.output_format}"),
        format=args.output_format,
    )

    return 0


def _none_if_empty(x: Optional[str]) -> Optional[str]:
    if x is None:
        return None
    x = x.strip()
    return x if x != "" else None


def _parse_int(x: Optional[str], field: str, row_idx: int) -> Optional[int]:
    x = _none_if_empty(x)
    if x is None:
        return None
    try:
        return int(x)
    except ValueError as e:
        raise ValueError(f"Row {row_idx}: invalid int for '{field}': {x}") from e


def _parse_float(x: Optional[str], field: str, row_idx: int) -> Optional[float]:
    x = _none_if_empty(x)
    if x is None:
        return None
    try:
        return float(x)
    except ValueError as e:
        raise ValueError(f"Row {row_idx}: invalid float for '{field}': {x}") from e


def _resolve_path(p: Optional[str], base_dir: str) -> Optional[str]:
    p = _none_if_empty(p)
    if p is None:
        return None
    return p if osp.isabs(p) else osp.normpath(osp.join(base_dir, p))


def load_conditions_tsv(
    tsv_path: str, base_dir: Optional[str] = None
) -> list[Dict[str, Any]]:
    if base_dir is None:
        base_dir = osp.dirname(osp.abspath(tsv_path))

    conditions: list[Dict[str, Any]] = []
    with open(tsv_path, "r", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        if reader.fieldnames is None:
            raise ValueError("TSV appears to have no header row.")

        header = {h.strip() for h in reader.fieldnames if h is not None}
        missing = REQUIRED_COLS - header
        if missing:
            raise ValueError(
                f"TSV missing required columns: {sorted(missing)}. Found: {sorted(header)}"
            )

        for i, row in enumerate(reader, start=2):  # header is line 1
            bam_path = _resolve_path(row.get("bam_path"), base_dir)
            pod5_path = _resolve_path(row.get("pod5_path"), base_dir)
            contig = _none_if_empty(row.get("contig"))
            pos = _parse_int(row.get("pos"), "pos", i)

            if not bam_path or not pod5_path or not contig or pos is None:
                raise ValueError(f"Row {i}: required fields missing or empty.")

            max_reads = _parse_int(row.get("max_reads"), "max_reads", i)
            label = _none_if_empty(row.get("label"))
            color = _none_if_empty(row.get("color"))
            opacity = _parse_float(row.get("opacity"), "opacity", i)

            conditions.append(
                {
                    "bam_path": bam_path,
                    "pod5_path": pod5_path,
                    "contig": contig,
                    "target_position": pos,
                    "max_reads": max_reads,
                    "label": label,
                    "color": color,
                    "alpha": opacity,
                }
            )

    return conditions
