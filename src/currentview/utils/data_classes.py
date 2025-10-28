import numpy as np
import pysam
from typing import Dict, List, Optional, Set, Tuple, Union, Any
from dataclasses import dataclass, field
from enum import Enum
from uuid import UUID
from pathlib import Path
from collections import defaultdict


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
                raise ValueError(
                    f"No signal for {self.base_type.value} at ref:{self.reference_pos}"
                )
            raise ValueError(
                "Signal not extracted. Run SignalExtractor.extract_signals() first"
            )
        return self._signal

    @signal.setter
    def signal(self, value: np.ndarray):
        """Set signal data."""
        if self.signal_range is None:
            raise ValueError(f"Cannot set signal for base without signal_range")
        expected_length = self.signal_range.end - self.signal_range.start
        if len(value) != expected_length:
            raise ValueError(
                f"Signal length {len(value)} doesn't match range {expected_length}"
            )
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

    @property
    def bases_by_ref_pos(self) -> Dict[int, AlignedBase]:
        """Get dictionary mapping reference positions to aligned bases."""
        if not hasattr(self, "_bases_by_ref_pos"):
            self._bases_by_ref_pos = {
                base.reference_pos: base
                for base in self.aligned_bases
                if base.reference_pos is not None
            }
        return self._bases_by_ref_pos
    
    @property
    def insertions_by_ref_pos(self) -> Dict[int, AlignedBase]:
        """Return a dictionary mapping of each refrecne position to the inserted bases after it"""
        if not hasattr(self, "_insertions_by_ref_pos"):
            prev_ref_pos = None
            self._insertions_by_ref_pos = defaultdict(list)
            for base in self.aligned_bases:
                if base.reference_pos is not None:
                    prev_ref_pos = base.reference_pos
                else:
                    if prev_ref_pos is not None:
                        self._insertions_by_ref_pos[prev_ref_pos].append(base)
            self._insertions_by_ref_pos = dict(self._insertions_by_ref_pos)  
        return self._insertions_by_ref_pos
        

    def get_base_at_ref_pos(self, ref_pos: int) -> Optional[AlignedBase]:
        """Convenience method to get base at specific reference position."""
        return self.bases_by_ref_pos.get(ref_pos)

    def get_signal(self, K: Optional[int] = None) -> np.ndarray:
        """Get the raw signal segment for the read from start to end."""
        window_size = K // 2 if K is not None else self.window_size
        start = self.target_position - window_size // 2
        end = self.target_position + window_size // 2 + 1
        bases_in_range = [self.get_base_at_ref_pos(pos) for pos in range(start, end)]
        signal_segments = [
            base.signal for base in bases_in_range if base and base.has_signal
        ]
        if not signal_segments:
            return np.array([])
        if self.is_reversed:
            signal_segments = [seg[::-1] for seg in signal_segments]
        return np.concatenate(signal_segments)

    def has_no_indels(self, window_size: int = 3) -> bool:
        """Check if there's a contiguous window of matches (no indels) around the target position."""
        if window_size % 2 == 0:
            raise ValueError(f"window_size must be odd, got {window_size}")

        matched_base = self.get_base_at_ref_pos(self.target_position)
        if matched_base is None or matched_base.query_pos is None:
            return False

        matched_query_pos_to_target = matched_base.query_pos
        half_window = window_size // 2

        # Check all positions in the window
        for idx in range(-half_window, half_window + 1):
            ref_pos = self.target_position + idx
            expected_query_pos = matched_query_pos_to_target + idx

            base = self.get_base_at_ref_pos(ref_pos)
            if base is None or base.query_pos != expected_query_pos:
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
