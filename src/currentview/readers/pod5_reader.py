import logging
from pathlib import Path
from typing import List, Optional, Union
from uuid import UUID

import pod5

from ..utils.data_classes import ReadAlignment


class SignalExtractor:
    def __init__(
        self,
        pod5_pth: Union[str, Path],
        signal_processing_fn: Optional[callable] = None,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize the signal extractor with a POD5 file or directory path.

        Args:
            pod5_pth: Path to a POD5 file or a directory of POD5 files
            signal_processing_fn: Optional transform applied to each read's signal
            logger: Optional logger instance
        """
        self.pod5_pth = pod5_pth
        self.logger = logger or logging.getLogger(__name__)
        self.signal_processing_fn = (
            signal_processing_fn if signal_processing_fn else lambda x: x
        )

    def extract_signals(
        self, aligned_reads: List[ReadAlignment]
    ) -> List[ReadAlignment]:
        self.logger.info(
            f"Extracting signals for {len(aligned_reads)} reads from pod5s"
        )
        out: List[ReadAlignment] = []
        alignment_dict = {
            read_alignment.read_id: read_alignment for read_alignment in aligned_reads
        }

        # POD5 selects on UUIDs. Read names that are not UUIDs cannot be looked up,
        # so drop them with an explicit warning rather than failing the whole run.
        read_ids = set()
        non_uuid: List[str] = []
        for read_id in alignment_dict:
            try:
                read_ids.add(UUID(read_id))
            except (ValueError, AttributeError, TypeError):
                non_uuid.append(read_id)

        if non_uuid:
            self.logger.warning(
                f"{len(non_uuid)} read name(s) are not valid UUIDs and cannot be "
                f"looked up in the POD5 file (e.g. {non_uuid[0]!r}). "
                f"CurrentView expects BAM query names to match POD5 read IDs."
            )

        if not read_ids:
            return out

        with pod5.DatasetReader(self.pod5_pth, recursive=True) as dataset:
            for read_record in dataset.reads(selection=read_ids):
                fetched_read_id = str(read_record.read_id)
                read_alignment = alignment_dict.get(fetched_read_id)
                if read_alignment is None:
                    continue

                read_alignment._signal = self.signal_processing_fn(
                    read_record.signal_pa
                )
                out.append(read_alignment)

        return out
