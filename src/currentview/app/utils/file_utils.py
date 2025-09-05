# dash_app/utils/file_utils.py
"""File system utilities for the Dash application."""

from pathlib import Path
from typing import List, Dict, Tuple, Optional


def get_directory_contents(
    path_str: str, extension: Optional[str] = None, show_files: bool = True
) -> Tuple[List[Dict], str]:
    """Get directory contents with optional filtering.

    Args:
        path_str: Directory path to list
        extension: File extension to filter (e.g., '.bam')
        show_files: If False, only show directories

    Returns:
        Tuple of (items list, actual path string)
    """
    try:
        path = Path(path_str)
        if not path.exists():
            path = Path.home()

        items = []
        if path.parent != path:
            items.append({"name": "..", "type": "dir", "path": str(path.parent)})

        for item in sorted(path.iterdir()):
            try:
                if item.is_dir():
                    items.append({"name": item.name, "type": "dir", "path": str(item)})
                elif show_files and (not extension or item.suffix == extension):
                    size = item.stat().st_size
                    items.append(
                        {
                            "name": item.name,
                            "type": "file",
                            "path": str(item),
                            "size": format_file_size(size),
                        }
                    )
            except:
                continue

        return items, str(path)
    except:
        return [], str(Path.home())


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    if size_bytes > 1024 * 1024:
        return f"{size_bytes/1024/1024:.1f}MB"
    else:
        return f"{size_bytes/1024:.1f}KB"
