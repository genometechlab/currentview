import logging
import os

import numpy as np
import pysam

from pathlib import Path
from typing import Dict, List, Optional, Set, Union

from ..utils.data_classes import ReadAlignment, AlignedBase, BaseType, SignalRange


def _default_threads() -> int:
    """Pick a sane pysam decompression thread count for this machine."""
    return max(1, min(4, os.cpu_count() or 1))


class AlignmentExtractor:
    """API for extracting nanopore signal data aligned to reference positions."""

    def __init__(
        self,
        bam_path: Union[str, Path],
        logger: Optional[logging.Logger] = None,
        random_state: int = 42,
        threads: Optional[int] = None,
    ):
        """
        Initialize the alignment extractor with BAM file path.

        Args:
            bam_path: Path to the BAM alignment file
            logger: Optional logger instance
            random_state: Seed used when sampling reads
            threads: pysam decompression threads (default: min(4, cpu_count))
        """
        self.bam_path = Path(bam_path)

        self.logger = logger or logging.getLogger(__name__)
        self.logger.debug(f"Initializing AlignmentExtractor on {self.bam_path.name}")

        self.random_state = random_state
        self.threads = threads if threads is not None else _default_threads()

        # Counts why reads were dropped during the most recent extraction, so a
        # zero-read result can explain itself instead of failing silently.
        self._skip_reasons: Dict[str, int] = {}

    def extract_read(self, read_id: str, is_reversed: bool) -> Optional[ReadAlignment]:
        """Fetch a single read by name and build its ReadAlignment, or None."""
        with pysam.AlignmentFile(self.bam_path, mode="rb", threads=self.threads) as bam:
            for read in bam.fetch(until_eof=True):
                if read.query_name == read_id:
                    aligned_bases = self._extract_aligned_bases(read, is_reversed)
                    if not aligned_bases:
                        return None
                    return ReadAlignment(
                        read_id=read.query_name,
                        aligned_bases=aligned_bases,
                        is_reversed=is_reversed,
                    )
        return None

    def extract_aligned_reads_at_position(
        self,
        contig: str,
        target_position: int,
        is_reversed: bool,
        matched_query_base: List[str] = None,
        ignore_non_primaries: bool = True,
        window_size: int = 9,
        exclude_reads_with_indels: bool = True,
        read_ids: Optional[Union[Set[str], List[str]]] = None,
        max_reads: Optional[int] = None,
    ) -> List[ReadAlignment]:
        """
        Extract signal data for reads covering a target referencd position.

        Args:
            target_position: Genomic reference of interest
            window_size: Number of bases around target (will be made odd)
            read_ids: Specific read IDs to process (if None, process all)
            max_reads: Maximum number of reads to process

        Returns:
            List of ReadAlignment objects
        """
        # Handle case when both read_ids and max_reads are set
        if read_ids is not None and max_reads is not None:
            # Convert to list for sampling if needed
            read_ids_list = list(read_ids) if isinstance(read_ids, set) else read_ids

            if max_reads < len(read_ids_list):
                # Sample max_reads from read_ids
                self.logger.info(
                    f"Both read_ids ({len(read_ids_list)} reads) and max_reads ({max_reads}) are set. "
                    f"Randomly sampling {max_reads} reads from provided read_ids."
                )
                rng = np.random.default_rng(self.random_state)
                sampled_ids = rng.choice(read_ids_list, size=max_reads, replace=False)
                read_ids = set(sampled_ids)
                max_reads = None  # Don't use max_reads in downstream logic
            else:
                # max_reads >= len(read_ids), so just use all read_ids
                self.logger.warning(
                    f"Both read_ids ({len(read_ids_list)} reads) and max_reads ({max_reads}) are set. "
                    "Since max_reads >= number of read_ids, ignoring max_reads and using all provided read_ids."
                )
                read_ids = (
                    set(read_ids_list) if isinstance(read_ids, list) else read_ids
                )
                max_reads = None  # Don't use max_reads in downstream logic
        # Convert read_ids to set for faster lookup (if not already handled above)
        elif read_ids is not None and isinstance(read_ids, list):
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

        self.logger.info("Processing reads from bam file")
        self.logger.info(f"Looking in region {contig}:{target_position}")

        self._skip_reasons = {}

        # Collect alignment data
        read_alignments = self._gather_aligned_reads_from_bam(
            contig,
            target_position,
            is_reversed,
            matched_query_base,
            ignore_non_primaries,
            window_size,
            exclude_reads_with_indels,
            read_ids,
            max_reads,
        )

        self._report_skips(len(read_alignments))

        return read_alignments

    def _report_skips(self, n_kept: int) -> None:
        """Summarise why reads were dropped, so an empty result explains itself."""
        if not self._skip_reasons:
            return

        summary = ", ".join(
            f"{reason}: {count}" for reason, count in sorted(self._skip_reasons.items())
        )
        # A structural problem (missing tags) is worth a warning even when some
        # reads survived; ordinary filter rejections are only interesting at DEBUG
        # unless nothing at all came through.
        structural = self._skip_reasons.get("missing_or_invalid_tags", 0)
        if structural or n_kept == 0:
            self.logger.warning(f"Reads skipped during extraction — {summary}")
            if structural:
                self.logger.warning(
                    "Reads were skipped because required basecaller tags "
                    "(mv/ns/ts) were missing or unusable. CurrentView needs a BAM "
                    "with move tables, e.g. produced by Dorado with --emit-moves."
                )
        else:
            self.logger.debug(f"Reads skipped during extraction — {summary}")

    def _gather_aligned_reads_from_bam(
        self,
        contig: str,
        target_position: int,
        is_reversed: bool,
        matched_query_base: Optional[List[str]],
        ignore_non_primaries: bool,
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

        with pysam.AlignmentFile(self.bam_path, mode="rb", threads=self.threads) as bam:
            if contig not in bam.references:
                raise KeyError(f"Contig {contig!r} not found in BAM references")

            if max_reads is not None and read_ids is None:
                # --- Branch A: fast candidate sampling via pileup, then heavy only for sampled IDs ---
                self.logger.info(
                    f"Searching up to {max_reads} candidate reads covering {contig}:{target_position}"
                )

                # oversample to account for later rejections (indels etc.)
                oversample = int(np.ceil(max_reads * 1.5))
                self.logger.info(
                    f"Oversampling to {oversample} reads to account for later filters"
                )
                candidate_ids = self._sample_candidate_ids(
                    bam=bam,
                    contig=contig,
                    start_pos=start_pos,
                    end_pos=end_pos,
                    matched_query_base=matched_query_base,
                    ignore_non_primaries=ignore_non_primaries,
                    max_reads=oversample,
                    target_position=target_position,  # focus on the exact site
                )
                self.logger.info(
                    f"A total of {len(candidate_ids)} candidate reads sampled"
                )
                if not candidate_ids:
                    self.logger.warning(
                        f"No candidate reads in {contig}:{start_pos}-{end_pos}"
                    )
                    return []

                results = self._build_read_alignments_from_region(
                    bam=bam,
                    contig=contig,
                    start_pos=start_pos,
                    end_pos=end_pos,
                    target_position=target_position,
                    is_reversed=is_reversed,
                    matched_query_base=matched_query_base,
                    ignore_non_primaries=ignore_non_primaries,
                    window_size=window_size,
                    exclude_reads_with_indels=exclude_reads_with_indels,
                    read_ids=set(candidate_ids),
                )

                # Trim to exactly max_reads if we
                self.logger.info(
                    f"Collected {len(results)} reads after full extraction and filtering"
                )
                if len(results) > max_reads:
                    self.logger.info(f"Randomly sub-sampling down to {max_reads} reads")
                    rng = np.random.default_rng(self.random_state)
                    keep = set(rng.choice(len(results), size=max_reads, replace=False))
                    results = [r for i, r in enumerate(results) if i in keep]
                elif len(results) < max_reads:
                    self.logger.info(
                        f"Only {len(results)} reads available after filtering (less than max_reads={max_reads}),"
                        "Consider increasing max_reads or changing the random_state for different sampling."
                    )

            # --- Branch B: full scan (either unlimited, or restricted by explicit read_ids) ---
            else:
                results = self._build_read_alignments_from_region(
                    bam=bam,
                    contig=contig,
                    start_pos=start_pos,
                    end_pos=end_pos,
                    target_position=target_position,
                    is_reversed=is_reversed,
                    matched_query_base=matched_query_base,
                    ignore_non_primaries=ignore_non_primaries,
                    window_size=window_size,
                    exclude_reads_with_indels=exclude_reads_with_indels,
                    read_ids=read_ids,
                )

        return results

    def _build_read_alignments_from_region(
        self,
        *,
        bam: pysam.AlignmentFile,
        contig: str,
        start_pos: int,
        end_pos: int,
        target_position: int,
        is_reversed: bool,
        matched_query_base: Optional[List[str]],
        ignore_non_primaries: bool,
        window_size: int,
        exclude_reads_with_indels: bool,
        read_ids: Optional[Set[str]],
    ) -> List[ReadAlignment]:
        """Heavy extraction over all reads in region (or subset if read_ids provided)."""
        region = dict(contig=contig, start=start_pos, stop=end_pos + 1)
        out: List[ReadAlignment] = []

        for read in bam.fetch(**region):
            if ignore_non_primaries:
                if read.is_secondary or read.is_supplementary:
                    continue

            if read_ids is not None and read.query_name not in read_ids:
                continue
            ra = self._build_read_alignment(
                read=read,
                start_pos=start_pos,
                end_pos=end_pos,
                target_position=target_position,
                is_reversed=is_reversed,
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
        is_reversed: bool,
        window_size: int,
        matched_query_base: Optional[List[str]],
        exclude_reads_with_indels: bool,
    ) -> Optional[ReadAlignment]:
        """Build ReadAlignment for a single read; return None if it fails filters."""
        try:
            aligned_bases = self._extract_aligned_bases(read, is_reversed)
        except (KeyError, ValueError, IndexError, TypeError) as e:
            # Missing or unusable mv, ns or ts tags, or a base/signal mismatch.
            # Tracked separately because it means the BAM is unsuitable, not that
            # the read failed a user filter.
            self._count_skip("missing_or_invalid_tags")
            self.logger.debug(f"Skipping read {read.query_name}: {e}")
            return None

        if not aligned_bases:
            self._count_skip("no_aligned_bases")
            return None

        ra = ReadAlignment(
            read_id=read.query_name,
            aligned_bases=aligned_bases,
            is_reversed=is_reversed,
        )

        if matched_query_base is not None:
            base = ra.get_base_at_ref_pos(target_position)
            if (
                base is None
                or base.query_base is None
                or base.query_base.upper() not in matched_query_base
            ):
                self._count_skip("base_mismatch_at_target")
                return None

        if exclude_reads_with_indels and not ra.has_no_indels(
            position=target_position,
            window_size=window_size,
        ):
            self._count_skip("indel_in_window")
            return None

        return ra

    def _count_skip(self, reason: str) -> None:
        self._skip_reasons[reason] = self._skip_reasons.get(reason, 0) + 1

    def _extract_aligned_bases(
        self,
        read: pysam.AlignedSegment,
        is_reversed: bool,
    ) -> List[AlignedBase]:
        """Extract aligned bases including insertions and deletions."""
        if read.query_sequence is None:
            raise ValueError(f"Read {read.query_name} has no query sequence")

        # Extract nanopore-specific tags
        ts = self._extract_ts_tag(read)
        if not read.has_tag("ns"):
            raise KeyError(f"Read {read.query_name} has no ns tag")
        if not read.has_tag("mv"):
            raise KeyError(f"Read {read.query_name} has no mv (move table) tag")

        ns = read.get_tag("ns")
        move_table = read.get_tag("mv")
        stride, moves = move_table[0], move_table[1:]

        # Convert moves to base indices
        base_indices = self._moves_to_base_indices(moves, stride, ts, ns)

        # One index per base plus a trailing end index; anything shorter means the
        # move table and the basecall disagree and the mapping would be garbage.
        seq_len = len(read.query_sequence)
        if base_indices.size < seq_len + 1:
            raise ValueError(
                f"Read {read.query_name}: move table yields {base_indices.size} "
                f"signal boundaries for {seq_len} bases (need {seq_len + 1})"
            )

        # Map base positions to signal ranges
        base_to_signal_range = self._base_indices_to_signal_ranges(
            base_indices, seq_len, is_reversed
        )

        # Get aligned pairs with reference sequence if available
        has_ref_seq = read.has_tag("MD")
        pairs = read.get_aligned_pairs(with_seq=has_ref_seq)
        query_seq = read.query_sequence

        aligned_bases = []

        # Process all aligned pairs
        for pair_data in pairs:
            if has_ref_seq:
                query_pos, ref_pos, ref_base = pair_data
            else:
                query_pos, ref_pos = pair_data
                ref_base = None

            if query_pos is None:
                # Deletion
                base_type = BaseType.DELETION
                signal_range = None
                query_base = None
            elif ref_pos is None:
                # Insertion
                base_type = BaseType.INSERTION
                signal_range = base_to_signal_range.get(query_pos)
                query_base = query_seq[query_pos]
            else:
                # Match/mismatch
                base_type = BaseType.MATCH
                signal_range = base_to_signal_range.get(query_pos)
                query_base = query_seq[query_pos]

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

    def _extract_ts_tag(self, read: pysam.AlignedSegment) -> int:
        """Extract the TS from read tags."""
        # Try direct tag access_
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

    def _sample_candidate_ids(
        self,
        *,
        bam: pysam.AlignmentFile,
        contig: str,
        start_pos: int,
        end_pos: int,
        matched_query_base: Optional[List[str]],
        ignore_non_primaries: bool,
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
                if ignore_non_primaries:
                    if read.is_secondary or read.is_supplementary:
                        continue
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
