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


@dataclass(frozen=True, slots=True)
class SignalRange:
    """Half-open signal interval [start, end) in sample indices."""
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
    
    def __post_init__(self):
        if self.base_type != BaseType.DELETION and self.signal_range is None:
            raise ValueError("Non-deletion bases must have a signal_range.")
        if self.base_type == BaseType.DELETION and self.signal_range is not None:
            raise ValueError("Deletion bases must not have a signal_range.")

    @property
    def has_signal(self) -> bool:
        return self.base_type != BaseType.DELETION

    @property
    def is_exact_match(self) -> bool:
        return self.base_type == BaseType.MATCH

@dataclass
class ReadAlignment:
    read_id: str
    aligned_bases: List[AlignedBase]
    is_reversed: bool
    _signal: Optional[np.ndarray] = field(repr=False, compare=False, default=None)
    
    @property
    def signal(self) -> np.ndarray:
        if self._signal is None:
            raise RuntimeError("Signal not loaded")
        return self._signal
    
    def get_base_signal(self, base: AlignedBase) -> Optional[np.ndarray]:
        if not base.has_signal or base.signal_range is None:
            return None

        start, end = base.signal_range.range
        seg = self.signal[start:end]
        return seg[::-1] if self.is_reversed else seg

    def get_span_signal(self, ref_start: int, ref_end: int) -> Optional[np.ndarray]:
        if ref_start > ref_end:
            raise ValueError(f"ref_start must be <= ref_end, got {ref_start} > {ref_end}")

        span_bases = [
            b for b in self.aligned_bases
            if b.reference_pos is not None
            and ref_start <= b.reference_pos <= ref_end
            and b.has_signal
            and b.signal_range is not None
        ]

        if not span_bases:
            return None

        span_bases.sort(key=lambda b: b.reference_pos)

        if self.is_reversed:
            span_start = span_bases[-1].signal_range.start
            span_end = span_bases[0].signal_range.end
        else:
            span_start = span_bases[0].signal_range.start
            span_end = span_bases[-1].signal_range.end

        if span_start > span_end:
            raise ValueError(f"start index > end index, got {span_start} > {span_end}")

        seg = self.signal[span_start:span_end]
        return seg[::-1] if self.is_reversed else seg


    @cached_property
    def bases_by_ref_pos(self) -> Dict[int, AlignedBase]:
        """Get dictionary mapping reference positions to aligned bases."""
        return {
            base.reference_pos: base
            for base in self.aligned_bases
            if base.reference_pos is not None
        }
        
    def get_base_at_ref_pos(self, ref_pos: int) -> Optional[AlignedBase]:
        """Convenience method to get base at specific reference position."""
        return self.bases_by_ref_pos.get(ref_pos)
    
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
