import numpy as np
import pysam
import logging

from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from uuid import UUID

from ..utils.data_classes import ReadAlignment, AlignedBase, BaseType, SignalRange


class AlignmentExtractor:
    """API for extracting nanopore signal data aligned to genomic positions."""

    def __init__(
        self,
        bam_path: Union[str, Path],
        logger: Optional[logging.Logger] = None,
        random_state: int = 42,
    ):
        """
        Initialize the alignment extractor with BAM file path.

        Args:
            bam_path: Path to the BAM alignment file
        """
        self.bam_path = Path(bam_path)

        self.logger = logger or logging.getLogger(__name__)
        self.logger.debug(f"Initializing AlignmentExtractor on {self.bam_path.name}")

        self.random_state = random_state

    def extract_alignments(
        self,
        contig: str,
        target_position: int,
        matched_query_base: List[str] = None,
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
        # if both read_ids and max_reads are set, ignore max_reads and use read_ids
        if read_ids is not None and max_reads is not None:
            self.logger.info(
                f"Both read_ids and max_reads are set. Ignoring max_reads and using read_ids."
            )
            max_reads = None

        # Convert read_ids to set for faster lookup
        if read_ids is not None and isinstance(read_ids, list):
            read_ids = set(read_ids)

        # Ensure window size is odd
        if window_size % 2 == 0:
            window_size += 1

        # Normalize matched_query_base to uppercase list
        if not matched_query_base:
            matched_query_base = None
        elif isinstance(matched_query_base, str):
            matched_query_base = [matched_query_base.upper()]
        else:
            matched_query_base = [s.upper() for s in matched_query_base]

        self.logger.info(f"Processing reads from bam file")
        self.logger.info(f"Looking in region {contig}:{target_position}")

        # Collect alignment data
        read_alignments = self._collect_read_alignments(
            contig,
            target_position,
            matched_query_base,
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
        matched_query_base: Optional[List[str]],
        window_size: int,
        exclude_reads_with_indels: bool,
        read_ids: Optional[Set[str]],
        max_reads: Optional[int],
    ) -> List[ReadAlignment]:
        """Collect alignment information for reads covering the target region."""
        # Search window (small bump to catch early indels)
        search_window = window_size + 4
        half_window = (search_window - 1) // 2
        start_pos = max(target_position - half_window, 0)
        end_pos = target_position + half_window

        with pysam.AlignmentFile(self.bam_path, mode="rb", threads=16) as bam:
            if contig not in bam.references:
                raise KeyError(f"Contig {contig!r} not found in BAM references")

            if max_reads is not None and read_ids is None:
                # --- Branch A: fast candidate sampling via pileup, then heavy only for sampled IDs ---
                self.logger.info(
                    f"Sampling up to {max_reads} candidate reads covering {contig}:{target_position}"
                )

                # oversample to account for later rejections (indels etc.)
                oversample = int(np.ceil(max_reads * 1.5))
                candidate_ids = self._sample_candidate_ids_fast(
                    bam=bam,
                    contig=contig,
                    start_pos=start_pos,
                    end_pos=end_pos,
                    matched_query_base=matched_query_base,
                    max_reads=oversample,
                    target_position=target_position,  # focus on the exact site
                )
                if not candidate_ids:
                    self.logger.warning(
                        f"No candidate reads in {contig}:{start_pos}-{end_pos}"
                    )
                    return []

                results = self._collect_alignments_for_ids(
                    bam=bam,
                    contig=contig,
                    start_pos=start_pos,
                    end_pos=end_pos,
                    target_position=target_position,
                    matched_query_base=matched_query_base,
                    window_size=window_size,
                    exclude_reads_with_indels=exclude_reads_with_indels,
                    candidate_ids=set(candidate_ids),
                )

                # Trim to exactly max_reads if we oversampled
                if len(results) > max_reads:
                    rng = np.random.default_rng(self.random_state)
                    keep = set(rng.choice(len(results), size=max_reads, replace=False))
                    results = [r for i, r in enumerate(results) if i in keep]

            # --- Branch B: full scan (either unlimited, or restricted by explicit read_ids) ---
            else:
                results = self._collect_alignments_streaming(
                    bam=bam,
                    contig=contig,
                    start_pos=start_pos,
                    end_pos=end_pos,
                    target_position=target_position,
                    matched_query_base=matched_query_base,
                    window_size=window_size,
                    exclude_reads_with_indels=exclude_reads_with_indels,
                    read_ids=read_ids,
                )

        return results

    def _collect_alignments_for_ids(
        self,
        *,
        bam: pysam.AlignmentFile,
        contig: str,
        start_pos: int,
        end_pos: int,
        target_position: int,
        matched_query_base: Optional[List[str]],
        window_size: int,
        exclude_reads_with_indels: bool,
        candidate_ids: Set[str],
    ) -> List[ReadAlignment]:
        """Heavy extraction but only for the provided candidate IDs."""
        region = dict(contig=contig, start=start_pos, stop=end_pos + 1)
        out: List[ReadAlignment] = []

        for read in bam.fetch(**region):
            if read.query_name not in candidate_ids:
                continue
            ra = self._build_read_alignment(
                read=read,
                start_pos=start_pos,
                end_pos=end_pos,
                target_position=target_position,
                window_size=window_size,
                matched_query_base=matched_query_base,
                exclude_reads_with_indels=exclude_reads_with_indels,
            )
            if ra is not None:
                out.append(ra)
        return out

    def _collect_alignments_streaming(
        self,
        *,
        bam: pysam.AlignmentFile,
        contig: str,
        start_pos: int,
        end_pos: int,
        target_position: int,
        matched_query_base: Optional[List[str]],
        window_size: int,
        exclude_reads_with_indels: bool,
        read_ids: Optional[Set[str]],
    ) -> List[ReadAlignment]:
        """Heavy extraction over all reads in region (or subset if read_ids provided)."""
        region = dict(contig=contig, start=start_pos, stop=end_pos + 1)
        out: List[ReadAlignment] = []

        for read in bam.fetch(**region):
            if read_ids is not None and read.query_name not in read_ids:
                continue
            ra = self._build_read_alignment(
                read=read,
                start_pos=start_pos,
                end_pos=end_pos,
                target_position=target_position,
                window_size=window_size,
                matched_query_base=matched_query_base,
                exclude_reads_with_indels=exclude_reads_with_indels,
            )
            if ra is not None:
                out.append(ra)
        return out

    def _build_read_alignment(
        self,
        *,
        read: pysam.AlignedSegment,
        start_pos: int,
        end_pos: int,
        target_position: int,
        window_size: int,
        matched_query_base: Optional[List[str]],
        exclude_reads_with_indels: bool,
    ) -> Optional[ReadAlignment]:
        """Build ReadAlignment for a single read; return None if it fails filters."""
        try:
            aligned_bases = self._extract_aligned_bases(read, start_pos, end_pos)
            if not aligned_bases:
                return None

            ra = ReadAlignment(
                read_id=read.query_name,
                aligned_bases=aligned_bases,
                target_position=target_position,
                window_size=window_size,
                is_reversed=True,
            )

            if matched_query_base is not None:
                base = ra.get_base_at_ref_pos(target_position)
                if (
                    base is None
                    or base.query_base is None
                    or base.query_base.upper() not in matched_query_base
                ):
                    return None

            if exclude_reads_with_indels and not ra.has_no_indels(
                window_size=window_size
            ):
                return None

            return ra
        except Exception as e:
            self.logger.debug(f"Skipping read {read.query_name}: {e}")
            return None

    def _extract_aligned_bases(
        self, read: pysam.AlignedSegment, start_pos: int, end_pos: int
    ) -> List[AlignedBase]:
        """Extract aligned bases including insertions and deletions."""
        # Extract nanopore-specific tags
        ts = self._extract_ts_tag(read)
        ns = read.get_tag("ns")
        move_table = read.get_tag("mv")
        stride, moves = move_table[0], move_table[1:]

        # Convert moves to base indices
        base_indices = self._moves_to_base_indices(moves, stride, ts, ns)

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

    def _get_aligned_base_to_ref_pos(
        self, aligned_bases: List[AlignedBase], ref_pos: int
    ) -> Optional[AlignedBase]:
        """Get the aligned base corresponding to a specific reference position."""
        for base in aligned_bases:
            if base.reference_pos == ref_pos:
                return base
        return None

    def _extract_ts_tag(self, read: pysam.AlignedSegment) -> int:
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
    ) -> Dict[int, SignalRange]:
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

    def _sample_candidate_ids_fast(
        self,
        *,
        bam: pysam.AlignmentFile,
        contig: str,
        start_pos: int,
        end_pos: int,
        matched_query_base: Optional[List[str]],
        max_reads: int,
        target_position: Optional[int] = None,
    ) -> List[str]:
        rng = np.random.default_rng(self.random_state)
        reservoir: List[str] = []
        seen = 0
        seen_ids: Set[str] = set()

        for col in bam.pileup(
            contig,
            start_pos,
            end_pos,
            truncate=True,
            stepper="samtools",
            max_depth=1_000_000,
        ):
            if target_position is not None and col.reference_pos != target_position:
                continue
            if col.reference_pos is None:
                continue

            for pil in col.pileups:
                read = pil.alignment
                rid = read.query_name
                if rid in seen_ids:
                    continue
                qpos = pil.query_position
                if qpos is None:
                    continue

                if matched_query_base:
                    qb = read.query_sequence[qpos].upper()
                    if qb not in matched_query_base:
                        continue

                seen_ids.add(rid)
                seen += 1
                if len(reservoir) < max_reads:
                    reservoir.append(rid)
                else:
                    j = rng.integers(0, seen)
                    if j < max_reads:
                        reservoir[j] = rid
        return reservoir
