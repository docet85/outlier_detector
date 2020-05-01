from numbers import Real
from typing import List

from outlier_detector import Qvals


def get_outlier_score(
    distribution: List[float],
    new_value: float,
    confidence: float = 0.95,
    sigma_threshold: float = 2,
) -> int:
    """
    Computes whether the incoming ``new_value`` is an outlier with respect to the given ``distribution``. It computes
    a double tailed Dixon's Q-test, with the given ``confidence``, along with testing the standard deviation of the
    new value considering the boundary (**mean** -``sigma_threshold`` **sigma**, **mean** + ``sigma_threshold``
    **sigma** ). In case the new value is valid the result is 0, otherwise 1 (outside the sigma threshold) or 2 an outlier
    based on Dixon's Q-test with given confidence.

    :param distribution: The incoming numeric set of values representing the distribution. Ideally this has been removed
     the linear monotonic trend or any other drift (in case applicable) so to make it a Gaussian distribution. Any trend
     indeed affects the outlier estimation. Accepted length is between 5 and 27 samples.
    :param new_value: The novel sample to be evaluated.
    :param confidence: The confidence for the outlier estimation: since Dixon's test relies on tabled values the
     available confidence steps are: 0.90, 0.95 and 0.99. Defaults to 0.95. Also percentage values are accepted (i.e.
     90, 95 and 99).
    :param sigma_threshold: multiplier for further analysis, samples outside the sigma boundary (**mean** -
    ``sigma_threshold`` **sigma**, **mean** + ``sigma_threshold`` **sigma** ) are marked as "warning"
    :return: 0 for valid samples, 1 for outside the sigma threshold ("warning"), 2 for outliers
    :raises ValueError: If sigma_threshold is negative or 0
    """
    from statistics import stdev

    if sigma_threshold <= 0:
        raise ValueError("Sigma threshold should be greater than 0")

    if is_outlier(distribution, new_value, confidence=confidence):
        return 2

    mu = sum(distribution) / float(len(distribution))
    sd = stdev(distribution)
    if new_value > (mu + float(sigma_threshold) * sd) or new_value < (
        mu - float(sigma_threshold) * sd
    ):
        return 1
    return 0


def is_outlier(
    distribution: List[float], new_value: float, confidence: float = 0.95
) -> bool:
    """
    Computes whether the incoming ``new_value`` is an outlier with respect to the given ``distribution``. It computes
    a double tailed Dixon's Q-test, with the given ``confidence``. In case the new value is valid the result is False,
    otherwise True.

    :param distribution: The incoming numeric set of values representing the distribution. Ideally this has been removed
     the linear monotonic trend or any other drift (in case applicable) so to make it a Gaussian distribution. Any trend
     indeed affects the outlier estimation. Accepted length is between 5 and 27 samples.
    :param new_value: The novel sample to be evaluated.
    :param confidence: The confidence for the outlier estimation: since Dixon's test relies on tabled values the
     available confidence steps are: 0.90, 0.95 and 0.99. Defaults to 0.95. Also percentage values are accepted (i.e.
     90, 95 and 99).
    :return: False for valid samples, True for outliers
    :raises ValueError: when confidence value set is not tabled;
    :raises ValueError: in case distribution  confidence value set is not tabled;
    """
    from copy import copy

    if confidence > 1:
        confidence /= 100
    if not (confidence in Qvals):
        raise ValueError(
            "Confidence value not tabled, please choose between 0.90, 0.95, and 0.99"
        )
    if not isinstance(distribution, List):
        raise TypeError(
            'Cannot search outliers in not List datatypes "{}"'.format(
                type(distribution).__name__
            )
        )
    if len(distribution) < 5 or len(distribution) > 27:
        raise ValueError(
            "Input distribution must have at least 5 elements and no more than 27"
        )
    if not isinstance(distribution[0], Real):
        raise TypeError(
            'Cannot search outliers in not-a-numeric-list datatypes "List[{}]"'.format(
                type(distribution[0]).__name__
            )
        )
    if not isinstance(new_value, Real):
        raise TypeError(
            'Cannot search outliers of not numeric or not compatible datatypes "{}"'.format(
                type(new_value).__name__
            )
        )

    q_vals = Qvals[confidence]

    x = copy(distribution)
    x.append(new_value)
    x.sort()

    q = 0
    if new_value == x[0]:
        q = abs(x[1] - x[0])
    if new_value == x[-1]:
        q = abs(x[-1] - x[-2])
    if q == 0:
        return False

    q /= abs(x[-1] - x[0])

    if q > q_vals[len(x)]:
        return True

    return False
