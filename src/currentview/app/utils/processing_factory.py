import numpy as np
from scipy.signal import bessel, filtfilt


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


def bessel_filter_smoothing(signal, order=4, cutoff=0.1):
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
    smoothed_signal = filtfilt(b, a, signal)
    return smoothed_signal


def gaussian_filter_smoothing(signal, sigma=1):
    """
    Apply a Gaussian filter to smooth the input signal.

    Parameters:
    signal (np.ndarray): The input signal array.
    sigma (float): The standard deviation of the Gaussian kernel.

    Returns:
    np.ndarray: The smoothed signal.
    """
    from scipy.ndimage import gaussian_filter1d

    smoothed_signal = gaussian_filter1d(signal, sigma=sigma)
    return smoothed_signal


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


def filter_signal(signal, method="none", **kwargs):
    """
    Filter the input signal using the specified method.

    Parameters:
    signal (np.ndarray): The input signal array.
    method (str): The filtering method to apply. Options are "none" and "bessel".
    kwargs: Additional keyword arguments for the filtering method.

    Returns:
    np.ndarray: The filtered signal.
    """
    if method == "bessel":
        cutoff = kwargs.get("bessel_cutoff", 0.2)
        order = kwargs.get("bessel_order", 4)
        return bessel_filter_smoothing(signal, order=order, cutoff=cutoff)
    elif method == "gaussian":
        sigma = kwargs.get("sigma", 1)
        return gaussian_filter_smoothing(signal, sigma=sigma)
    elif method == "none":
        return signal
    else:
        raise ValueError(f"Unknown filtering method: {method}")


def process_signal(
    signal, normalization_method="none", filtering_method="none", **filter_kwargs
):
    """
    Process the input signal by applying first filtering and then normalization.

    """
    filtered_signal = filter_signal(signal, method=filtering_method, **filter_kwargs)
    normalized_signal = normalize_signal(filtered_signal, method=normalization_method)
    return normalized_signal
