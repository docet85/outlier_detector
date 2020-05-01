import inspect
from typing import Any, Callable, Dict, List, Iterator
from uuid import uuid4

__alive_filters__ = {}
__strategies_decorator__ = ["recursion", "iteration", "exception", "generation"]
__strategies_obj__ = ["recursion", "iteration", "exception"]

from outlier_detector.exceptions import OutlierException
from outlier_detector.detectors import OutlierDetector
import logging


def filter_outlier(
    distribution_id: Any = None,
    strategy: str = "recursion",
    **outlier_detector_kwargs: Dict
) -> Callable:
    """Wraps a generic "pop" or "get" function, returning a sample of a gaussian distribution, with an outlier filter.
    When meeting an outlier the filter omits it and, depending on the strategy, it may call recursively the wrapped
    function, iteratively call the wrapped function, raise an ``OutlierException``, or wrap it in a generator. It
    relies on ``OutlierDetector`` whose args can be forwarded using the proper argument.

    :param distribution_id: unique identifier for the distribution. In case empty, this is inferred runtime. In case
           wrapping a method, the first argument hash is used as default.
    :param strategy: 'recursion', 'iteration', 'exception' or 'generation'
    :param outlier_detector_kwargs: the constructor arguments for the underlying detector

    :raises ValueError: when strategy is invalid
    :raises OutlierException: when strategy is 'exception' and an outlier is found
    """
    if strategy not in __strategies_decorator__:
        raise ValueError(
            'Strategy "{}" unknown, please pick one in {}'.format(
                strategy, __strategies_decorator__
            )
        )

    if distribution_id is None:
        d_id = uuid4()
    else:
        d_id = distribution_id

    if strategy == "iteration":

        def iterative_outlier_filter(func):
            def wrapper(*args, **kwargs):
                od = _retrieve_filter_instance(
                    func, args, d_id, distribution_id, **outlier_detector_kwargs
                )
                sample = func(*args, **kwargs)
                while od.is_outlier(sample):
                    sample = func(*args, **kwargs)
                return sample

            return wrapper

        return iterative_outlier_filter
    elif strategy == "generation":

        def generative_outlier_filter(func):
            def wrapper(*args, **kwargs):
                od = _retrieve_filter_instance(
                    func, args, d_id, distribution_id, **outlier_detector_kwargs
                )
                while True:
                    sample = func(*args, **kwargs)
                    if not od.is_outlier(sample):
                        yield sample

            return wrapper

        return generative_outlier_filter
    elif strategy == "exception":

        def exception_outlier_filter(func):
            def wrapper(*args, **kwargs):
                od = _retrieve_filter_instance(
                    func, args, d_id, distribution_id, **outlier_detector_kwargs
                )
                sample = func(*args, **kwargs)
                if od.is_outlier(sample):
                    raise OutlierException("Detected Outlier in distribution", sample)
                else:
                    return sample

            return wrapper

        return exception_outlier_filter
    else:

        def recursive_outlier_filter(func):
            def wrapper(*args, **kwargs):
                od = _retrieve_filter_instance(
                    func, args, d_id, distribution_id, **outlier_detector_kwargs
                )
                sample = func(*args, **kwargs)
                if od.is_outlier(sample):
                    return wrapper(*args, **kwargs)
                else:
                    return sample

            return wrapper

        return recursive_outlier_filter


def destroy_filter(distribution_id: Any):
    """
    Given an assigned distribution id, destroys the associated detector below the filter. Since the detector
    is a singleton instantiated on demand, this is the final effect of deleting the recorded samples buffer.
    :param distribution_id: the id associated toa filter on decoration
    """
    if distribution_id in __alive_filters__:
        del __alive_filters__[distribution_id]


def _retrieve_filter_instance(
    func, args, d_id, distribution_id, **outlier_detector_kwargs
):
    global __alive_filters__
    if distribution_id is None:
        full_arg_spec = inspect.getfullargspec(func)
        if full_arg_spec.args and full_arg_spec.args[0] == "self":
            d_id = args[0].__hash__()
    if d_id not in __alive_filters__:
        __alive_filters__[d_id] = OutlierDetector(**outlier_detector_kwargs)
    return __alive_filters__[d_id]


class OutlierFilter(OutlierDetector):
    """Exploits an OutlierDetector to expose the same functionality of the filter decorator.
    It wraps a generic "pop" or "get" function, returning a sample of a gaussian distribution, with an outlier filter.
    When meeting an outlier the filter omits it and, depending on the strategy, it may raise a ``ValueError``.
    Relies on ``OutlierDetector`` whose args can be forwarded using the proper argument.
    """

    def __init__(self, strategy="iteration", limit=None, **outlier_detector_kwargs):
        """

        :param distribution_id: unique identifier for the distribution. In case empty, this is inferred runtime. In case
               wrapping a method, the first argument hash is used as default.
        :param strategy: 'recursion', 'iteration' or 'exception'
        :param outlier_detector_kwargs: the constructor arguments for the underlying detector

        :raises ValueError: when strategy is invalid
        """
        if strategy not in __strategies_obj__:
            raise ValueError(
                'Strategy "{}" unknown, please pick one in {}'.format(
                    strategy, __strategies_obj__
                )
            )

        OutlierDetector.__init__(self, **outlier_detector_kwargs)

        if strategy == "recursion":
            logging.warning(
                "Recursion strategy not available for iterator, fallback to iteration with limit=20"
            )
            strategy = "iteration"
            limit = 20
        elif strategy != "iteration" and limit is not None:
            logging.warning(
                "limit={} has no effect with strategy {}".format(limit, strategy)
            )
            limit = None

        self.limit = limit
        self.strategy = strategy
        self.__outlier_counter__ = 0

    def filter(self, func: Callable, *args: List, **kwargs: Dict) -> Iterator[float]:
        """
        :raises OutlierException: when strategy is 'exception' and an outlier is found

        :param func:
        :param args:
        :param kwargs:
        """
        self.__outlier_counter__ = 0
        while self.limit is None or self.__outlier_counter__ <= self.limit:
            sample = func(*args, **kwargs)
            if not self.is_outlier(sample):
                yield sample
                self.__outlier_counter__ = 0
            else:
                if self.strategy == "exception":
                    raise OutlierException("Detected Outlier in distribution", sample)
                if self.limit is not None:
                    self.__outlier_counter__ += 1
        if self.limit:
            raise OutlierException(
                "Limit of {} subsequent outliers reached", self.limit
            )
