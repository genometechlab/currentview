import logging
import numpy as np
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Union
from collections import OrderedDict

from ..utils.data_classes import ReadAlignment, Condition
from ..utils.plotly_utils import PlotStyle


class BaseSignalVisualizer(ABC):
    """
    Abstract base class for signal visualization backends.
    Handles all shared logic — condition tracking, y-limits, position labels,
    reference base extraction. Subclasses implement only rendering.
    """

    def __init__(
        self,
        K: int,
        window_labels: Optional[List[Union[str, int]]] = None,
        plot_style: Optional[PlotStyle] = None,
        title: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
    ):
        self.logger = logger or logging.getLogger(__name__)
        self.K = K
        self.window_labels = window_labels
        self.style = plot_style or PlotStyle()
        self.title = title or "Nanopore Signal Visualization"

        if self.window_labels and len(self.window_labels) != self.K:
            raise ValueError("window_labels must have length K")

        # Condition tracking
        self._conditions_info: OrderedDict[str, Dict] = OrderedDict()

        # Incremental y-limit tracking (avoids full scan on every update)
        self._y_min: float = np.inf
        self._y_max: float = -np.inf
        self._auto_ylim: bool = True

        # Highlight / annotation tracking (subclasses populate these)
        self._highlight_shapes: List[str] = []
        self._annotation_indices: List[str] = []

        self._create_figure()
        self._add_position_barriers()

        if self.window_labels:
            self._apply_custom_labels()

        self.logger.info(f"Initialized {self.__class__.__name__} with K={K}")

    # =========================================================================
    # Abstract interface — subclasses must implement these
    # =========================================================================

    @abstractmethod
    def _create_figure(self):
        """Create and configure the backend figure object."""

    @abstractmethod
    def _add_position_barriers(self):
        """Draw vertical separator lines between positions."""

    @abstractmethod
    def _apply_custom_labels(self):
        """Apply window_labels to the x-axis."""

    @abstractmethod
    def _update_position_labels(self):
        """Rebuild x-axis tick labels from current conditions."""

    @abstractmethod
    def _plot_signals(self, condition: Condition):
        """Render all reads for a condition onto the figure."""

    @abstractmethod
    def _do_highlight(self, uid: str, window_idx: int, color: str, alpha: float):
        """Draw a single highlight rectangle; uid is for later removal."""

    @abstractmethod
    def _do_clear_highlights(self):
        """Remove all highlight rectangles from the figure."""

    @abstractmethod
    def _do_add_annotation(
        self,
        uid: str,
        x_pos: float,
        y_pos: float,
        text: str,
        color: str,
        fontsize: int,
        fontcolor: str,
        **kwargs,
    ):
        """Draw a single annotation; uid is for later removal."""

    @abstractmethod
    def _do_clear_annotations(self):
        """Remove all annotations from the figure."""

    @abstractmethod
    def _do_set_ylim(self, lo: float, hi: float):
        """Apply y-axis range to the figure."""

    @abstractmethod
    def _do_set_title(self, title: str):
        """Apply title to the figure."""

    @abstractmethod
    def _do_remove_condition_traces(self, label: str):
        """Remove all rendered traces belonging to a condition."""

    @abstractmethod
    def get_fig(self):
        """Return the underlying figure object."""

    @abstractmethod
    def show(self):
        """Display the figure."""

    @abstractmethod
    def save(self, path: Union[str, Path], **kwargs):
        """Save the figure to disk."""

    # =========================================================================
    # Shared public API
    # =========================================================================

    def plot_condition(self, condition: Condition):
        """Add or update a condition on the plot."""
        label = condition.label
        self.logger.debug(f"plot_condition: '{label}', n_reads={len(condition.reads)}")

        if label in self._conditions_info:
            self.logger.warning(f"Condition '{label}' already plotted — replacing.")
            self.remove_condition(label)

        # Extract reference bases for axis labels
        kmer_dict = self._extract_reference_bases(condition.positions, condition.reads)
        position_labels = [f"{pos} - {kmer_dict[pos]}" for pos in condition.positions]

        self._conditions_info[label] = {
            "style": condition.style,
            "pos_labels": position_labels,
        }

        self._plot_signals(condition)
        self._update_global_ylim()

        if not self.window_labels:
            self._update_position_labels()

    def remove_condition(self, label: str) -> bool:
        if label not in self._conditions_info:
            self.logger.warning(f"Condition '{label}' not found")
            return False

        self._do_remove_condition_traces(label)
        self._conditions_info.pop(label)

        # Recompute y limits from scratch since a condition was removed
        self._y_min, self._y_max = np.inf, -np.inf
        self._recompute_ylim_from_figure()
        self._update_global_ylim()

        if not self.window_labels:
            self._update_position_labels()

        return True

    def clear_conditions(self) -> "BaseSignalVisualizer":
        for label in list(self._conditions_info.keys()):
            self._do_remove_condition_traces(label)
        self._conditions_info.clear()
        self._y_min, self._y_max = np.inf, -np.inf

        if not self.window_labels:
            self._update_position_labels()

        return self

    def highlight_position(
        self, window_idx: Optional[int] = None, color: str = "red", alpha: float = 0.2
    ) -> "BaseSignalVisualizer":
        if window_idx is None:
            window_idx = self.K // 2

        uid = f"user_highlight_{len(self._highlight_shapes)}"
        self._do_highlight(uid, window_idx, color, alpha)
        self._highlight_shapes.append(uid)
        return self

    def clear_highlights(self) -> "BaseSignalVisualizer":
        self._do_clear_highlights()
        self._highlight_shapes.clear()
        return self

    def add_annotation(
        self,
        window_idx: int,
        text: str,
        color: str = "rgba(255, 255, 0, 0.7)",
        fontsize: Optional[int] = None,
        fontcolor: Optional[str] = None,
        y_position: Optional[float] = None,
        **kwargs,
    ) -> "BaseSignalVisualizer":
        from ..utils.color_utils import get_contrasting_color

        x_pos = window_idx + 0.5 - self.style.positions_padding / 2
        fontcolor = fontcolor or get_contrasting_color(color)
        fontsize = fontsize or self.style.annotation_font_size

        if y_position is None:
            if np.isfinite(self._y_max):
                y_position = self._y_max * 0.95
            else:
                y_position = 100.0

        uid = f"user_annotation_{len(self._annotation_indices)}"
        self._do_add_annotation(
            uid, x_pos, y_position, text, color, fontsize, fontcolor, **kwargs
        )
        self._annotation_indices.append(uid)
        return self

    def clear_annotations(self) -> "BaseSignalVisualizer":
        self._do_clear_annotations()
        self._annotation_indices.clear()
        return self

    def set_title(self, title: str) -> "BaseSignalVisualizer":
        self.title = title
        self._do_set_title(title)
        return self

    def set_ylim(
        self, bottom: Optional[float] = None, top: Optional[float] = None
    ) -> "BaseSignalVisualizer":
        self._auto_ylim = False
        lo = (
            bottom
            if bottom is not None
            else (self._y_min if np.isfinite(self._y_min) else 0.0)
        )
        hi = (
            top
            if top is not None
            else (self._y_max if np.isfinite(self._y_max) else 1.0)
        )
        self._do_set_ylim(lo, hi)
        return self

    def set_auto_ylim(self, enabled: bool = True) -> "BaseSignalVisualizer":
        self._auto_ylim = enabled
        if enabled:
            self._update_global_ylim()
        return self

    def reset_view(self) -> "BaseSignalVisualizer":
        self.clear_highlights()
        self.clear_annotations()
        self._auto_ylim = True
        self._update_global_ylim()
        return self

    def get_plotted_labels(self) -> List[str]:
        return list(self._conditions_info.keys())

    def has_condition(self, label: str) -> bool:
        return label in self._conditions_info

    # =========================================================================
    # Shared internal helpers
    # =========================================================================

    def _update_global_ylim(self):
        """Apply current y_min/y_max to the figure if auto mode is on."""
        if not self._auto_ylim:
            return
        if not (np.isfinite(self._y_min) and np.isfinite(self._y_max)):
            return
        pad = max(1e-6, (self._y_max - self._y_min) * 0.05)
        self._do_set_ylim(self._y_min - pad, self._y_max + pad)

    def _track_y(self, arr: np.ndarray):
        """Update running y min/max from a signal array (call from _plot_signals)."""
        finite = arr[np.isfinite(arr)]
        if finite.size:
            self._y_min = min(self._y_min, float(finite.min()))
            self._y_max = max(self._y_max, float(finite.max()))

    @abstractmethod
    def _recompute_ylim_from_figure(self):
        """
        Recompute _y_min/_y_max by scanning existing rendered data.
        Called after remove_condition so limits stay correct.
        Subclasses implement this because data lives in backend-specific objects.
        """

    def _extract_reference_bases(
        self, positions: List[int], reads: List[ReadAlignment]
    ) -> Dict[int, str]:
        kmer_dict = {pos: "_" for pos in positions}
        rem = len(kmer_dict)

        for read in reads:
            for base in read.aligned_bases:
                pos = base.reference_pos
                if pos in kmer_dict and kmer_dict[pos] == "_":
                    kmer_dict[pos] = (
                        base.reference_base.upper() if base.reference_base else "*"
                    )
                    rem -= 1
            if rem == 0:
                break

        return kmer_dict

    def _get_base_signal(
        self, read: ReadAlignment, genomic_pos: int
    ) -> Optional[np.ndarray]:
        base = read.get_base_at_ref_pos(genomic_pos)
        if base is None or not base.has_signal:
            return None
        sig = read.get_base_signal(base=base)
        if sig is None:
            return None
        sig = np.asarray(sig, dtype=np.float32).ravel()
        return sig if sig.size else None

    def _get_insertions_signal(
        self, read: ReadAlignment, genomic_pos: int
    ) -> np.ndarray:
        insertions = read.insertions_by_ref_pos.get(genomic_pos)
        if not insertions:
            return np.empty(0, dtype=np.float32)
        parts = [read.get_base_signal(base=ins) for ins in insertions if ins.has_signal]
        return (
            np.concatenate(parts).astype(np.float32)
            if parts
            else np.empty(0, dtype=np.float32)
        )

    def _build_read_arrays(self, read: ReadAlignment, positions: List[int]):
        """
        Build pre-allocated float32 x/y arrays for one read.
        Returns (matched_x, matched_y, ins_x, ins_y) or (None, None, None, None).
        Shared by both backends so neither duplicates this logic.
        """
        pad = self.style.positions_padding
        NAN = np.float32(np.nan)

        # First pass — collect signals and compute buffer sizes
        segments = {}
        matched_total = ins_total = 0

        for pos_idx, genomic_pos in enumerate(positions):
            b = self._get_base_signal(read, genomic_pos)
            if b is None:
                continue
            ins = self._get_insertions_signal(read, genomic_pos)
            segments[pos_idx] = (b, ins)
            matched_total += b.shape[0] + 1  # signal + nan break
            if ins.shape[0]:
                ins_total += 1 + ins.shape[0] + 1  # anchor + ins + nan break

        if not segments:
            return None, None, None, None

        # Second pass — fill pre-allocated buffers
        mx = np.empty(matched_total, dtype=np.float32)
        my = np.empty(matched_total, dtype=np.float32)
        ix = np.empty(ins_total, dtype=np.float32) if ins_total else None
        iy = np.empty(ins_total, dtype=np.float32) if ins_total else None

        mp = ip = 0

        for pos_idx, (b, ins) in segments.items():
            n_b, n_i = b.shape[0], ins.shape[0]
            x0, x1 = float(pos_idx), float(pos_idx + 1 - pad)
            x_arr = np.linspace(x0, x1, n_b + n_i, dtype=np.float32)

            x_base = x_arr[:n_b]
            mx[mp : mp + n_b] = x_base
            my[mp : mp + n_b] = b
            mx[mp + n_b] = my[mp + n_b] = NAN
            mp += n_b + 1

            if n_i:
                x_ins = x_arr[n_b:]
                ix[ip] = x_base[-1]
                iy[ip] = b[-1]  # anchor
                ix[ip + 1 : ip + 1 + n_i] = x_ins
                iy[ip + 1 : ip + 1 + n_i] = ins
                ix[ip + 1 + n_i] = iy[ip + 1 + n_i] = NAN
                ip += 1 + n_i + 1

        return mx, my, ix, iy
