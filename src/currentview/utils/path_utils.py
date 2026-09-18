from pathlib import Path
from typing import Union


def validate_files(path: Union[str, Path]) -> bool:
    """Return True if the given path exists."""
    return Path(path).exists()
