# dash_app/utils/validators.py
"""Input validation functions for the Dash application."""

import json
from typing import Optional, Any, Dict


def validate_window_size(value: Optional[int]) -> bool:
    """Validate that window size is odd."""
    return value is None or value % 2 == 0


def validate_json_string(json_str: str) -> tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    """Validate JSON string and return parsed result.
    
    Returns:
        Tuple of (is_valid, parsed_data, error_message)
    """
    if not json_str:
        return True, None, None
    
    try:
        data = json.loads(json_str)
        return True, data, None
    except json.JSONDecodeError as e:
        return False, None, f"Invalid JSON: {str(e)}"


def validate_kmer_labels(kmer_text: str, k: int) -> tuple[bool, Optional[list[str]], Optional[str]]:
    """Validate k-mer labels match the window size.
    
    Returns:
        Tuple of (is_valid, parsed_labels, error_message)
    """
    if not kmer_text:
        return True, None, None
    
    kmers = [l.strip() for l in kmer_text.strip().split('\n') if l.strip()]
    if len(kmers) != k:
        return False, None, f"Need {k} labels, got {len(kmers)}"
    
    return True, kmers, None