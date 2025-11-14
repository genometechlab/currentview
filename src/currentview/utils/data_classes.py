import numpy as np
import pysam
from typing import Dict, List, Optional, Set, Tuple, Union, Any
from dataclasses import dataclass, field
from enum import Enum
from uuid import UUID
from pathlib import Path
from collections import defaultdict
from functools import cached_property


class BaseType(Enum):
    MATCH = "match"
    INSERTION = "insertion"
    DELETION = "deletion"


@dataclass
class SignalRange:
    start: int
    end: int

    def __post_init__(self):
        if self.start < 0 or self.end < 0:
            raise ValueError(f"Signal positions must be non-negative: {self.start}, {self.end}")
        if self.start >= self.end:
            raise ValueError(f"Signal start must be before end: {self.start} >= {self.end}")

    @property
    def range(self):
        return (self.start, self.end)
        
    @property
    def length(self) -> int:
        return self.end - self.start
    
    def __len__(self) -> int:
        return self.length


@dataclass
class AlignedBase:
    reference_pos: Optional[int]
    query_pos: Optional[int]
    base_type: BaseType
    signal_range: Optional[SignalRange]
    reference_base: Optional[str] = None
    query_base: Optional[str] = None

    @property
    def has_signal(self) -> bool:
        return self.base_type != BaseType.DELETION

    def get_signal(self, read: "ReadAlignment") -> np.ndarray:
        if self.has_signal:
            sig_start, sig_end = self.signal_range.range
            base_sig = read.signal[sig_start:sig_end]
            return base_sig[::-1] if read.is_reversed else base_sig
        return None

    @property
    def is_exact_match(self) -> bool:
        return self.base_type == BaseType.MATCH

@dataclass
class ReadAlignment:
    read_id: str
    aligned_bases: List[AlignedBase]
    is_reversed: bool
    _signal: Optional[np.ndarray] = field(default=None, repr=False, compare=False)

    @cached_property
    def bases_by_ref_pos(self) -> Dict[int, AlignedBase]:
        """Get dictionary mapping reference positions to aligned bases."""
        return {
            base.reference_pos: base
            for base in self.aligned_bases
            if base.reference_pos is not None
        }
    
    @cached_property
    def insertions_by_ref_pos(self) -> Dict[Optional[int], List[AlignedBase]]:
        """Return a dictionary mapping each reference position to inserted bases after it.
        
        Key is None for insertions at the beginning of the read.
        """
        prev_ref_pos = None
        insertions = defaultdict(list)
        
        for base in self.aligned_bases:
            if base.reference_pos is not None:
                prev_ref_pos = base.reference_pos
            elif base.base_type == BaseType.INSERTION:  # ← Be explicit
                insertions[prev_ref_pos].append(base)
        
        return dict(insertions)

    def get_base_at_ref_pos(self, ref_pos: int) -> Optional[AlignedBase]:
        """Convenience method to get base at specific reference position."""
        return self.bases_by_ref_pos.get(ref_pos)

    @property
    def signal(self) -> np.ndarray:
        return self._signal

    def has_no_indels(self, position: int, window_size: int) -> bool:
        """Check if there's a contiguous window of matches (no indels) around the target position."""
        if window_size % 2 == 0:
            raise ValueError(f"window_size must be odd, got {window_size}")
        
        matched_base = self.get_base_at_ref_pos(position)
        if matched_base is None or matched_base.query_pos is None:
            return False
        
        matched_query_pos_to_target = matched_base.query_pos
        half_window = window_size // 2
        
        # Check all positions in the window
        for idx in range(-half_window, half_window + 1):
            ref_pos = position + idx
            expected_query_pos = matched_query_pos_to_target + idx
            
            # Check for match at this position
            base = self.get_base_at_ref_pos(ref_pos)
            if base is None or base.query_pos != expected_query_pos:
                return False
            
            # Check for insertions after this position
            if ref_pos in self.insertions_by_ref_pos:
                return False
        
        return True


@dataclass
class Condition:
    """Store all data for a processed condition."""

    label: str
    reads: List[ReadAlignment]
    positions: List[int]
    contig: str
    target_position: int
    bam_path: Path
    pod5_path: Path
    stats: Optional[Dict[int, Dict[str, List[float]]]] = field(
        default=None, repr=False, compare=False
    )
    color: Optional[Any] = None
    alpha: Optional[float] = None
    line_width: Optional[float] = None
    line_style: Optional[str] = None

    @property
    def n_reads(self) -> int:
        """Number of reads in this condition."""
        return len(self.reads)

    @property
    def genomic_location(self) -> str:
        """Genomic location as string."""
        return f"{self.contig}:{self.target_position}"
