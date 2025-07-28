import logging
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union, Literal, Any
from dataclasses import dataclass
from collections import OrderedDict, defaultdict

from .readers import AlignmentExtractor
from .readers import SignalExtractor
from .utils import ReadAlignment
from .utils import validate_files
from .utils import PlotStyle, ColorScheme

class DataProcessor:
    """Handles all file I/O, extraction, and data processing."""
    
    def __init__(self, K: int, logger: Optional[logging.Logger] = None):
        """
        Initialize the data processor.
        
        Args:
            K: Number of bases in window (will be made odd)
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        self.logger.debug(f"Initializing DataProcessor with K={K}")
        
        # Ensure window size is odd
        if K % 2 == 0:
            K += 1
            self.logger.debug(f"Adjusted K from {K-1} to {K} (must be odd)")
        
        self.K = K
        
        # Caches for extractors
        self._alignment_cache: Dict[Path, AlignmentExtractor] = {}
        self._signal_cache: Dict[Path, SignalExtractor] = {}
        self.logger.debug("Initialized empty caches for extractors")
        
        self.logger.info(f"Initialized DataProcessor with window size {K}")
    
    def process_reads(self,
                      bam_path: Union[str, Path],
                      pod5_path: Union[str, Path],
                      label: str,
                      contig: str,
                      target_position: int,
                      target_base: str = None,
                      read_ids: Optional[Union[Set[str], List[str]]] = None,
                      max_reads: Optional[int] = None,
                      require_perfect_match: bool = False) -> List[ReadAlignment]:
        """
        Process reads from BAM/POD5 files and prepare for visualization.
        
        Returns:
            List of ReadAlignment objects or None if no reads found
        """
        self.logger.debug(f"process_reads called with label='{label}', contig={contig}, pos={target_position}")
        
        # Convert to Path objects
        bam_path = Path(bam_path)
        pod5_path = Path(pod5_path)
        self.logger.debug(f"Converted paths: BAM={bam_path}, POD5={pod5_path}")
        
        # Validate files
        self.logger.debug("Validating input files...")
        if not validate_files(bam_path):
            self.logger.error(f"BAM file validation failed: {bam_path}")
            raise FileNotFoundError(f"BAM file not found: {bam_path}")
        if not validate_files(pod5_path):
            self.logger.error(f"POD5 file validation failed: {pod5_path}")
            raise FileNotFoundError(f"POD5 file not found: {pod5_path}")
        self.logger.debug("File validation successful")
        
        self.logger.info(f"Looking for reads aligned at position {target_position} of contig {contig} from {bam_path.name}")
        
        # Log extraction parameters
        self.logger.debug(f"Extraction parameters: "
                         f"require_perfect_match={require_perfect_match}, "
                         f"max_reads={max_reads}, "
                         f"read_ids={'provided' if read_ids else 'None'}")
        
        # Extract alignments
        alignments = self._extract_alignments(
            bam_path, contig, target_position, target_base,
            require_perfect_match, read_ids, max_reads
        )
        
        if not alignments:
            self.logger.warning(f"No reads found at {contig}:{target_position}")
            return None

        self.logger.info(f"Found {len(alignments)} reads at {contig}:{target_position}")
        
        # Log some statistics about the alignments
        if self.logger.isEnabledFor(logging.DEBUG):
            forward_count = sum(1 for a in alignments if not a.is_reversed)
            reverse_count = len(alignments) - forward_count
            self.logger.debug(f"Alignment orientation: {forward_count} forward, {reverse_count} reverse")
        
        # Extract signals
        len_fetched = len(alignments)
        self.logger.debug(f"Starting signal extraction for {len_fetched} alignments")
        
        alignments = self._extract_signals(pod5_path, alignments)
        
        if len(alignments) != len_fetched:
            self.logger.warning(f"Signal extraction incomplete: {len(alignments)}/{len_fetched} reads have signals")
            if self.logger.isEnabledFor(logging.DEBUG):
                self.logger.debug(f"Lost {len_fetched - len(alignments)} reads during signal extraction")
        else:
            self.logger.debug(f"Successfully extracted signals for all {len(alignments)} reads")
        
        if not alignments:
            self.logger.warning("No reads with signals found")
            return None
        
        self.logger.info(f"Successfully processed {len(alignments)} reads for condition '{label}'")
        
        # Log summary statistics if in debug mode
        if self.logger.isEnabledFor(logging.DEBUG):
            self._log_alignment_statistics(alignments)
        
        return alignments
    
    def get_summary(self) -> Dict:
        """Get summary of io_processor class."""
        self.logger.debug("get_summary called")
        
        summary = {
            'K': self.K,
            'n_conditions': len(self._extracted_conditions_map),
            'total_reads': sum(len(cond.reads) for cond in self._extracted_conditions_map.values()),
            'conditions': [
                {
                    'label': cond.label,
                    'contig': cond.contig,
                    'position': cond.target_position,
                    'n_reads': len(cond.reads),
                    'bam': str(cond.bam_path),
                    'pod5': str(cond.pod5_path)
                }
                for cond in self._extracted_conditions_map.values()
            ]
        }
        
        self.logger.debug(f"Summary: {summary['n_conditions']} conditions, {summary['total_reads']} total reads")
        return summary
    
    def _extract_alignments(self,
                           bam_path: Path,
                           contig: str,
                           target_position: int,
                           target_base: str,
                           exclude_reads_with_indels: bool,
                           read_ids: Optional[Union[Set[str], List[str]]],
                           max_reads: Optional[int]) -> List[ReadAlignment]:
        """Extract alignments from BAM file."""
        self.logger.debug(f"_extract_alignments: BAM={bam_path.name}, {contig}:{target_position}")
        
        # Check cache
        if bam_path not in self._alignment_cache:
            self.logger.debug(f"Creating new AlignmentExtractor for {bam_path.name}")
            self._alignment_cache[bam_path] = AlignmentExtractor(bam_path)
        else:
            self.logger.debug(f"Using cached AlignmentExtractor for {bam_path.name}")
        
        # Log extraction call
        self.logger.debug(f"Calling extract_alignments with window_size={self.K}")
        
        try:
            alignments = self._alignment_cache[bam_path].extract_alignments(
                contig=contig,
                target_position=target_position,
                target_base=target_base,
                window_size=self.K,
                exclude_reads_with_indels=exclude_reads_with_indels,
                read_ids=read_ids,
                max_reads=max_reads
            )
            self.logger.debug(f"Extraction successful: {len(alignments)} alignments")
            return alignments
            
        except Exception as e:
            self.logger.error(f"Alignment extraction failed: {type(e).__name__}: {str(e)}")
            raise
    
    def _extract_signals(self,
                        pod5_path: Path,
                        alignments: List[ReadAlignment]) -> List[ReadAlignment]:
        """Extract signals from POD5 file."""
        self.logger.debug(f"_extract_signals: POD5={pod5_path.name}, n_alignments={len(alignments)}")
        
        if not alignments:
            self.logger.debug("No alignments to process")
            return alignments
        
        # Check cache
        if pod5_path not in self._signal_cache:
            self.logger.debug(f"Creating new SignalExtractor for {pod5_path.name}")
            self._signal_cache[pod5_path] = SignalExtractor(pod5_path)
        else:
            self.logger.debug(f"Using cached SignalExtractor for {pod5_path.name}")
        
        self.logger.info(f"Extracting signals for {len(alignments)} reads...")
        
        try:
            # Log read IDs if in debug mode
            if self.logger.isEnabledFor(logging.DEBUG):
                read_ids = [a.read_id for a in alignments[:5]]  # First 5
                self.logger.debug(f"First few read IDs: {read_ids}")
                if len(alignments) > 5:
                    self.logger.debug(f"... and {len(alignments) - 5} more")
            
            alignments_with_signals = self._signal_cache[pod5_path].extract_signals(alignments)
            
            self.logger.debug(f"Signal extraction complete: {len(alignments_with_signals)} reads have signals")
            
            # Log any reads that failed signal extraction
            if len(alignments_with_signals) < len(alignments) and self.logger.isEnabledFor(logging.DEBUG):
                original_ids = {a.read_id for a in alignments}
                extracted_ids = {a.read_id for a in alignments_with_signals}
                missing_ids = original_ids - extracted_ids
                self.logger.debug(f"Reads without signals: {list(missing_ids)[:5]}")
                if len(missing_ids) > 5:
                    self.logger.debug(f"... and {len(missing_ids) - 5} more")
            
            return alignments_with_signals
            
        except Exception as e:
            self.logger.error(f"Signal extraction failed: {type(e).__name__}: {str(e)}")
            raise
    
    def _log_alignment_statistics(self, alignments: List[ReadAlignment]):
        """Log detailed statistics about alignments (debug mode only)."""
        if not alignments:
            return
        
        # Orientation statistics
        forward = sum(1 for a in alignments if not a.is_reversed)
        reverse = len(alignments) - forward
        
        # Coverage statistics
        coverage_by_pos = defaultdict(int)
        for alignment in alignments:
            for base in alignment.aligned_bases:
                if base.reference_pos is not None:
                    coverage_by_pos[base.reference_pos] += 1
        
        # Signal statistics
        signal_lengths = []
        for alignment in alignments:
            for base in alignment.aligned_bases:
                if base.has_signal:
                    signal_lengths.append(len(base.signal))
        
        self.logger.debug("Alignment Statistics:")
        self.logger.debug(f"  - Total reads: {len(alignments)}")
        self.logger.debug(f"  - Orientation: {forward} forward, {reverse} reverse")
        self.logger.debug(f"  - Positions covered: {len(coverage_by_pos)}")
        if coverage_by_pos:
            self.logger.debug(f"  - Average coverage: {np.mean(list(coverage_by_pos.values())):.1f}")
        if signal_lengths:
            self.logger.debug(f"  - Signal lengths: min={min(signal_lengths)}, "
                            f"max={max(signal_lengths)}, "
                            f"mean={np.mean(signal_lengths):.1f}")