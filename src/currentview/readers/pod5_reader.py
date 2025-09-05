from typing import Dict, List, Optional, Set, Tuple, Union
from pathlib import Path
import pod5
from uuid import UUID
import logging

from ..utils.data_classes import ReadAlignment


class SignalExtractor:
    def __init__(
        self, pod5_pth: Union[str, Path], logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the alignment extractor with BAM file path.

        Args:
            bam_path: Path to the BAM alignment file
        """
        self.pod5_pth = pod5_pth
        self.logger = logger

    def extract_signals(self, aligned_reads: List[ReadAlignment]):
        self.logger.info(
            f"Extracting signals for {len(aligned_reads)} reads from pod5s"
        )
        out = []
        alignment_dict = {
            read_alignment.read_id: read_alignment for read_alignment in aligned_reads
        }
        read_ids = set([UUID(read_id) for read_id in alignment_dict.keys()])
        with pod5.DatasetReader(self.pod5_pth, recursive=True) as dataset:
            for read_record in dataset.reads(selection=read_ids):
                fetched_read_id = str(read_record.read_id)
                read_alignment = alignment_dict[fetched_read_id]
                for aligned_base in read_alignment.aligned_bases:
                    # Ignore deletions, since they don't have a range
                    if aligned_base.query_base is None:
                        continue
                    signal = read_record.signal_pa
                    start, end = aligned_base.signal_range.range
                    base_signal = signal[start:end]
                    aligned_base.signal = base_signal
                out.append(read_alignment)

        return out
