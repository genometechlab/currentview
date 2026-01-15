from __future__ import annotations

import argparse
import os
import os.path as osp


def register_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "manual",
        help="Run CurrentView with explicit command-line arguments (1–2 conditions).",
        description="CurrentView CLI (manual flags).",
    )

    # Global settings
    parser.add_argument(
        "-k",
        "--window-size",
        type=int,
        default=9,
        help="Size of the window around the genomic position (default: 9).",
    )
    parser.add_argument(
        "--stats",
        type=str,
        default="median,std,duration",
        help="Comma-separated list of statistics to compute (default: median,std,duration).",
    )
    parser.add_argument(
        "--verbosity-level",
        type=int,
        default=1,
        help="Level of verbosity for logging (default: 1).",
    )

    # Condition 1 (required)
    parser.add_argument("--bam-path-1", type=str, required=True, help="Path to the first BAM file.")
    parser.add_argument("--pod5-path-1", type=str, required=True, help="Path to the first POD5 file.")
    parser.add_argument("--contig-1", type=str, required=True, help="Contig name for the first condition.")
    parser.add_argument("--pos-1", type=int, required=True, help="Genomic position for the first condition.")
    parser.add_argument("--max-reads-1", type=int, default=None, help="Max reads for condition 1 (optional).")
    parser.add_argument("--label-1", type=str, default=None, help="Label for condition 1 (optional).")
    parser.add_argument("--color-1", type=str, default=None, help="Color for condition 1 (optional).")
    parser.add_argument("--opacity-1", type=float, default=None, help="Opacity for condition 1 (optional).")

    # Condition 2 (optional)
    parser.add_argument("--bam-path-2", type=str, default=None, help="Path to the second BAM file (optional).")
    parser.add_argument("--pod5-path-2", type=str, default=None, help="Path to the second POD5 file (optional).")
    parser.add_argument("--contig-2", type=str, default=None, help="Contig name for the second condition (optional).")
    parser.add_argument("--pos-2", type=int, default=None, help="Genomic position for the second condition (optional).")
    parser.add_argument("--max-reads-2", type=int, default=None, help="Max reads for condition 2 (optional).")
    parser.add_argument("--label-2", type=str, default=None, help="Label for condition 2 (optional).")
    parser.add_argument("--color-2", type=str, default=None, help="Color for condition 2 (optional).")
    parser.add_argument("--opacity-2", type=float, default=None, help="Opacity for condition 2 (optional).")

    # Output
    parser.add_argument(
        "--output-dir",
        type=str,
        default=".",
        help="Directory to save output files (default: current directory).",
    )
    parser.add_argument(
        "--output-format",
        type=str,
        choices=["png", "pdf", "svg"],
        default="pdf",
        help="Output format (default: pdf).",
    )

    parser.set_defaults(func=cmd_manual)


def cmd_manual(args: argparse.Namespace) -> int:
    from ..genomic_visualizer import GenomicPositionVisualizer

    visualizer = GenomicPositionVisualizer(
        K=args.window_size,
        stats=[s.strip() for s in args.stats.split(",") if s.strip()],
        verbosity=args.verbosity_level,
    )

    # Always add condition 1
    visualizer.add_condition(
        bam_path=args.bam_path_1,
        pod5_path=args.pod5_path_1,
        contig=args.contig_1,
        target_position=args.pos_1,
        max_reads=args.max_reads_1,
        label=args.label_1,
        color=args.color_1,
        alpha=args.opacity_1,
    )

    # Add condition 2 only if the required fields are present
    if args.bam_path_2 and args.pod5_path_2 and args.contig_2 and (args.pos_2 is not None):
        visualizer.add_condition(
            bam_path=args.bam_path_2,
            pod5_path=args.pod5_path_2,
            contig=args.contig_2,
            target_position=args.pos_2,
            max_reads=args.max_reads_2,
            label=args.label_2,
            color=args.color_2,
            alpha=args.opacity_2,
        )

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
