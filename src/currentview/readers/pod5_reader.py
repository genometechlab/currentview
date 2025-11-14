from typing import Dict, List, Optional, Set, Tuple, Union
from pathlib import Path
import pod5
from uuid import UUID
import logging

from ..utils.data_classes import ReadAlignment


class SignalExtractor:
    def __init__(
        self,
        pod5_pth: Union[str, Path],
        signal_processing_fn: Optional[callable] = None,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize the alignment extractor with BAM file path.

        Args:
            bam_path: Path to the BAM alignment file
        """
        self.pod5_pth = pod5_pth
        self.logger = logger
        self.signal_processing_fn = (
            signal_processing_fn if signal_processing_fn else lambda x: x
        )

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
                read_alignment._signal = read_record.signal_pa

                signal = read_record.signal_pa
                signal = self.signal_processing_fn(signal)
                read_alignment._signal = signal
                out.append(read_alignment)
        return out
