def validate_files(path):
    """Validate that input files exist."""
    if not path.exists():
        return False
    return True