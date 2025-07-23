import numpy as np
import pysam

from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from uuid import UUID

from ..utils.data_classes import ReadAlignment, AlignedBase, BaseType, SignalRange


class AlignmentExtractor:
    """API for extracting nanopore signal data aligned to genomic positions."""

    def __init__(self, bam_path: Union[str, Path]):
        """
        Initialize the alignment extractor with BAM file path.

        Args:
            bam_path: Path to the BAM alignment file
        """
        self.bam_path = bam_path

    def extract_alignments(
        self,
        contig: str,
        target_position: int,
        target_base: str = None,
        window_size: int = 9,
        exclude_reads_with_indels: bool = True,
        read_ids: Optional[Union[Set[str], List[str]]] = None,
        max_reads: Optional[int] = None,
    ) -> List[ReadAlignment]:
        """
        Extract signal data for reads covering a target genomic position.

        Args:
            target_position: Genomic position of interest
            window_size: Number of bases around target (will be made odd)
            read_ids: Specific read IDs to process (if None, process all)
            max_reads: Maximum number of reads to process

        Returns:
            List of ReadAlignment objects
        """
        if read_ids is not None and isinstance(read_ids, list):
            read_ids = set(read_ids)

        # Ensure window size is odd
        if window_size % 2 == 0:
            window_size += 1

        # Collect alignment data
        read_alignments = self._collect_read_alignments(
            contig,
            target_position,
            target_base,
            window_size,
            exclude_reads_with_indels,
            read_ids,
            max_reads,
        )

        return read_alignments

    def _collect_read_alignments(
        self,
        contig: str,
        target_position: int,
        target_base: str,
        window_size: int,
        exclude_reads_with_indels: bool,
        read_ids: Optional[Set[str]],
        max_reads: Optional[int],
    ) -> List[ReadAlignment]:
        """Collect alignment information for reads covering the target region."""

        # Increasing window size for search to cinsider early insertions
        search_window = window_size * 3

        half_window = (search_window - 1) // 2
        start_pos = target_position - half_window
        end_pos = target_position + half_window

        read_alignments = []
        read_count = 0

        with pysam.AlignmentFile(self.bam_path, mode="rb", threads=16) as bam:

            if contig not in bam.references:
                raise KeyError(f"Contig not found in the bam file")

            region = {
                "contig": contig,
                "start": target_position - half_window,
                "stop": target_position + half_window + 1,
            }

            # Fetching reads
            for read in bam.fetch(**region):
                # Skip if not in read_ids (when specified)
                if read_ids is not None and read.query_name not in read_ids:
                    continue

                try:

                    # Extract aligned bases with signal mapping
                    aligned_bases = self._extract_aligned_bases(
                        read, start_pos, end_pos
                    )

                    # Only fetch reads with the specified target base if target base is provided
                    if target_base is not None:
                        aligned_base = self._get_aligned_base_to_ref_pos(
                            aligned_bases, target_position
                        )
                        if aligned_base is None or aligned_base.query_base != target_base:
                            continue

                    # Only include reads that have some coverage of the region
                    if aligned_bases:
                        read_alignment = ReadAlignment(
                            read_id=read.query_name,
                            aligned_bases=aligned_bases,
                            target_position=target_position,
                            window_size=window_size,
                            is_reversed=read.is_reverse,
                        )
                        if exclude_reads_with_indels:
                            if read_alignment.has_no_indels(window_size=window_size):
                                read_alignments.append(read_alignment)
                                read_count += 1
                        else:
                            read_alignments.append(read_alignment)
                            read_count += 1

                        if max_reads is not None and read_count >= max_reads:
                            break

                except Exception as e:
                    print(f"Skipping read {read.query_name}: {e}")
                    raise e
                    continue

        return read_alignments

    def _extract_aligned_bases(
        self, read: pysam.AlignedSegment, start_pos: int, end_pos: int
    ) -> List[AlignedBase]:
        """Extract aligned bases including insertions and deletions."""
        # Extract nanopore-specific tags
        timestamp_start = self._extract_timestamp(read)
        num_samples = read.get_tag("ns")
        move_table = read.get_tag("mv")
        stride, moves = move_table[0], move_table[1:]

        # Convert moves to base indices
        base_indices = self._moves_to_base_indices(
            moves, stride, timestamp_start, num_samples
        )

        # Determining the direction of alignment
        is_reversed = True  # read.is_reverse

        # Map base positions to signal ranges
        base_to_signal_range = self._base_indices_to_signal_ranges(
            base_indices, len(read.query_sequence), is_reversed
        )

        # Get aligned pairs with reference sequence if available
        if read.has_tag("MD"):
            pairs = read.get_aligned_pairs(with_seq=True)
            has_ref_seq = True
        else:
            pairs = read.get_aligned_pairs()
            has_ref_seq = False

        aligned_bases = []
        in_target_region = False

        # Process all aligned pairs
        for pair_data in pairs:
            if has_ref_seq:
                query_pos, ref_pos, ref_base = pair_data
            else:
                query_pos, ref_pos = pair_data
                ref_base = None

            # Check if we're in or near the target region
            if ref_pos is not None:
                if ref_pos < start_pos:
                    # Not yet in the target region, continue with the next pair
                    continue
                if start_pos <= ref_pos <= end_pos:
                    # Now we are inside the region of interest
                    # A flag will be enabled to capture insertions
                    in_target_region = True
                    pass  # Just for consistency with continue and break
                elif ref_pos > end_pos:
                    in_target_region = (
                        False  # Not required due to break. Included for consistency
                    )
                    # Breaking out of pairs loop
                    break
            else:
                if in_target_region:
                    # Will fall into insertion logic below
                    pass  # Just for consistency with continue and break
                else:
                    continue

            if query_pos is None and ref_pos is not None:
                # Deletion
                base_type = BaseType.DELETION
            elif query_pos is not None and ref_pos is None:
                # Insertion
                base_type = BaseType.INSERTION
            elif query_pos is not None and ref_pos is not None:
                # Match/mismatch
                base_type = BaseType.MATCH
            else:
                continue

            # Get signal range
            if query_pos is not None:
                signal_range = base_to_signal_range.get(query_pos)
                query_base = read.query_sequence[query_pos]
            else:
                # None because of deletion
                signal_range = None
                query_base = None

            aligned_base = AlignedBase(
                reference_pos=ref_pos,
                query_pos=query_pos,
                base_type=base_type,
                signal_range=signal_range,
                reference_base=ref_base,
                query_base=query_base,
            )
            aligned_bases.append(aligned_base)

        return aligned_bases

    def _get_aligned_base_to_ref_pos(self, aligned_bases: List[AlignedBase], ref_pos: int) -> Optional[AlignedBase]:
        """Get the aligned base corresponding to a specific reference position."""
        for base in aligned_bases:
            if base.reference_pos == ref_pos:
                return base
        return None
        

    def _extract_timestamp(self, read: pysam.AlignedSegment) -> int:
        """Extract the TS from read tags."""
        # Try direct tag access
        for tag, val, dtype in read.get_tags(with_value_type=True):
            if tag == "ts" and dtype == "i":
                return val

        # Fallback to string parsing
        sam_string = read.to_string()
        for field in sam_string.split("\t"):
            if field.startswith("ts:i:"):
                try:
                    return int(field.split(":")[2])
                except ValueError:
                    continue

        raise ValueError(f"Read {read.query_name} has no valid ts:i tag")

    def _moves_to_base_indices(
        self, moves: np.ndarray, stride: int, timestamp_start: int, num_samples: int
    ) -> np.ndarray:
        """Convert move array to base position indices."""
        moves_array = np.array(moves, dtype="int8")
        move_positions = np.where(moves_array == 1)[0] * stride + timestamp_start
        return np.append(move_positions, num_samples)

    def _base_indices_to_signal_ranges(
        self, base_indices: np.ndarray, sequence_length: int, is_reversed: bool
    ) -> Dict[int, Tuple[int, int]]:
        """Convert base indices to signal start/end ranges."""
        base_to_range = {}
        for i in range(sequence_length):
            if is_reversed:
                start_idx = base_indices[sequence_length - i - 1].item()
                end_idx = base_indices[sequence_length - i].item()
                base_to_range[i] = SignalRange(start_idx, end_idx)
            else:
                start_idx = base_indices[i].item()
                end_idx = base_indices[i + 1].item()
                base_to_range[i] = SignalRange(start_idx, end_idx)
        return base_to_range
