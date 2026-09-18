"""Signal normalization and filtering applied to each read before plotting.

Every entry point below takes explicit keyword-only options rather than a loose
``**kwargs`` bag. A misspelled option therefore raises ``TypeError`` instead of
being silently swallowed and leaving the signal unprocessed.
"""

import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.signal import bessel, filtfilt

# Shared defaults, so the UI, the filter helpers and the dispatcher cannot drift.
DEFAULT_BESSEL_ORDER = 4
DEFAULT_BESSEL_CUTOFF = 0.1
DEFAULT_GAUSSIAN_SIGMA = 1.0


def zscore_signal_normalization(signal):
    """
    Apply z-score normalization to the input signal.

    Parameters:
    signal (np.ndarray): The input signal array.

    Returns:
    np.ndarray: The z-score normalized signal.
    """
    mean = np.mean(signal)
    std = np.std(signal)
    if std == 0:
        return signal - mean  # Avoid division by zero
    return (signal - mean) / std


def bessel_filter_smoothing(
    signal, order=DEFAULT_BESSEL_ORDER, cutoff=DEFAULT_BESSEL_CUTOFF
):
    """
    Apply a Bessel filter to smooth the input signal.

    Parameters:
    signal (np.ndarray): The input signal array.
    order (int): The order of the Bessel filter.
    cutoff (float): The cutoff frequency as a fraction of the Nyquist frequency.

    Returns:
    np.ndarray: The smoothed signal.
    """
    b, a = bessel(order, cutoff, btype="low", analog=False)

    # filtfilt pads the signal by 3 * max(len(a), len(b)); shorter reads would
    # raise. Those are too short to be worth filtering, so pass them through.
    padlen = 3 * max(len(a), len(b))
    if len(signal) <= padlen:
        return signal

    return filtfilt(b, a, signal)


def gaussian_filter_smoothing(signal, sigma=DEFAULT_GAUSSIAN_SIGMA):
    """
    Apply a Gaussian filter to smooth the input signal.

    Parameters:
    signal (np.ndarray): The input signal array.
    sigma (float): The standard deviation of the Gaussian kernel.

    Returns:
    np.ndarray: The smoothed signal.
    """
    return gaussian_filter1d(signal, sigma=sigma)


def min_max_normalization(signal):
    """
    Apply min-max normalization to the input signal.

    Parameters:
    signal (np.ndarray): The input signal array.

    Returns:
    np.ndarray: The min-max normalized signal.
    """
    min_val = np.min(signal)
    max_val = np.max(signal)
    if max_val - min_val == 0:
        return signal - min_val  # Avoid division by zero
    return (signal - min_val) / (max_val - min_val)


def normalize_signal(signal, method="none"):
    """
    Normalize the input signal using the specified method.

    Parameters:
    signal (np.ndarray): The input signal array.
    method (str): The normalization method to apply. Options are "none", "zscore", and "minmax".

    Returns:
    np.ndarray: The normalized signal.
    """
    if method == "zscore":
        return zscore_signal_normalization(signal)
    elif method == "minmax":
        return min_max_normalization(signal)
    elif method == "none":
        return signal
    else:
        raise ValueError(f"Unknown normalization method: {method}")


def filter_signal(
    signal,
    method="none",
    *,
    bessel_order=DEFAULT_BESSEL_ORDER,
    bessel_cutoff=DEFAULT_BESSEL_CUTOFF,
    gaussian_sigma=DEFAULT_GAUSSIAN_SIGMA,
):
    """
    Filter the input signal using the specified method.

    Parameters:
    signal (np.ndarray): The input signal array.
    method (str): "none", "bessel" or "gaussian".
    bessel_order (int): Bessel filter order.
    bessel_cutoff (float): Bessel cutoff as a fraction of the Nyquist frequency.
    gaussian_sigma (float): Standard deviation of the Gaussian kernel.

    Returns:
    np.ndarray: The filtered signal.
    """
    if method in (None, "none"):
        return signal
    if method == "bessel":
        return bessel_filter_smoothing(
            signal, order=bessel_order, cutoff=bessel_cutoff
        )
    if method == "gaussian":
        return gaussian_filter_smoothing(signal, sigma=gaussian_sigma)
    raise ValueError(f"Unknown filtering method: {method}")


def process_signal(
    signal,
    normalization_method="none",
    filtering_method="none",
    *,
    bessel_order=DEFAULT_BESSEL_ORDER,
    bessel_cutoff=DEFAULT_BESSEL_CUTOFF,
    gaussian_sigma=DEFAULT_GAUSSIAN_SIGMA,
):
    """
    Process the input signal by applying filtering first, then normalization.

    Options are keyword-only and explicit: passing an unrecognised name raises
    TypeError rather than silently skipping the step.
    """
    filtered = filter_signal(
        signal,
        method=filtering_method,
        bessel_order=bessel_order,
        bessel_cutoff=bessel_cutoff,
        gaussian_sigma=gaussian_sigma,
    )
    return normalize_signal(filtered, method=normalization_method)
