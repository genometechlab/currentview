# yourpkg/cli/main.py
from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from .cli import manual, from_tsv


def main() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="currentview",
        description="CurrentView command-line interface",
    )

    subparsers = parser.add_subparsers(
        title="subcommands",
        description="Available subcommands",
        dest="command",
        required=True,
        metavar="{manual,from_tsv}",
        help="Choose how to provide conditions (explicit flags vs TSV).",
    )

    manual.register_subparser(subparsers)
    from_tsv.register_subparser(subparsers)

    args = parser.parse_args()

    return args.func(args)

if __name__ == "__main__":
    raise SystemExit(main())
