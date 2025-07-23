import numpy as np
import pysam
from typing import Dict, List, Optional, Set, Tuple, Union, Any
from dataclasses import dataclass, field
from enum import Enum
from uuid import UUID
from pathlib import Path


class BaseType(Enum):
    MATCH = "match"
    INSERTION = "insertion"
    DELETION = "deletion"


@dataclass
class SignalRange:
    start: int
    end: int

    @property
    def range(self):
        return (self.start, self.end)
   

@dataclass
class AlignedBase:
    reference_pos: Optional[int]
    query_pos: Optional[int]
    base_type: BaseType
    signal_range: Optional[SignalRange]
    reference_base: Optional[str] = None
    query_base: Optional[str] = None
    _signal: Optional[np.ndarray] = field(default=None, repr=False, compare=False)
    
    @property
    def signal(self) -> np.ndarray:
        """Get signal data. Raises error if not yet extracted."""
        if self._signal is None:
            if self.signal_range is None:
                raise ValueError(f"No signal for {self.base_type.value} at ref:{self.reference_pos}")
            raise ValueError("Signal not extracted. Run SignalExtractor.extract_signals() first")
        return self._signal
    
    @signal.setter
    def signal(self, value: np.ndarray):
        """Set signal data."""
        if self.signal_range is None:
            raise ValueError(f"Cannot set signal for base without signal_range")
        expected_length = self.signal_range.end - self.signal_range.start
        if len(value) != expected_length:
            raise ValueError(f"Signal length {len(value)} doesn't match range {expected_length}")
        self._signal = value
    
    @property
    def has_signal(self) -> bool:
        """Check if signal has been extracted."""
        return self._signal is not None
    
    @property
    def is_exact_match(self) -> bool:
        return self.base_type == BaseType.MATCH


@dataclass
class ReadAlignment:
    read_id: str
    aligned_bases: List[AlignedBase]
    target_position: int
    window_size: int
    is_reversed: bool

    def has_no_indels(self, window_size: int = 3) -> bool:
        """Check if there's a contiguous window of matches (no indels) around the target position."""
        if window_size % 2 == 0:
            raise ValueError(f"window_size must be odd, got {window_size}")
            
        # Build dictionary of reference positions to query positions
        aligned_dict = {}
        matched_query_pos_to_target = None
        
        for aligned_base in self.aligned_bases:
            if aligned_base.reference_pos is not None:  # Skip insertions
                aligned_dict[aligned_base.reference_pos] = aligned_base.query_pos
            if aligned_base.reference_pos == self.target_position:
                matched_query_pos_to_target = aligned_base.query_pos

        if matched_query_pos_to_target is None:
            return False

        # Define the window range
        half_window = window_size // 2
        
        # Check all positions in the window
        for idx in range(-half_window, half_window + 1):
            ref_pos = self.target_position + idx
            expected_query_pos = matched_query_pos_to_target + idx
            
            # Check if position exists (no deletion)
            if ref_pos not in aligned_dict:
                return False
                
            # Check if query position is consecutive (no insertion)
            if aligned_dict[ref_pos] != expected_query_pos:
                return False
                
        return True
    
@dataclass
class PlottedCondition:
    """Track information about each plotted group."""
    label: str
    color: Any
    alpha: Any
    line_width: float
    line_style: str
    xticklabels: List[str]

@dataclass
class AlignedCondition:
    """Track information about each plotted group."""
    contig: str
    bam_path: Union[str, Path]
    pod5_path: Union[str, Path]
    label: str
    target_position: int
    reads: List[ReadAlignment]
