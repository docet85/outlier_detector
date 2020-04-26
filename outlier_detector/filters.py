import inspect
from uuid import uuid4

__alive_filters__ = {}
__strategies__ = ["recursion", "iteration", "exception"]

from outlier_detector.exceptions import OutlierException
from outlier_detector.detectors import OutlierDetector
import logging


def filter_outlier(
    distribution_id=None, strategy="recursion", **outlier_detector_kwargs
):
    """Wraps a generic "pop" or "get" function, returning a sample of a gaussian distribution, with an outlier filter.
    When meeting an outlier the filter omits it and, depending on the strategy, it may call recursively the wrapped
    function, iteratively call the wrapped function or raising a ``ValueError``. Relies on ``OutlierDetector`` whose
    args can be forwarded using the proper argument.

    :type distribution_id: any
    :type strategy: str

    :param distribution_id: unique identifier for the distribution. In case empty, this is inferred runtime. In case
           wrapping a method, the first argument hash is used as default.
    :param strategy: 'recursion', 'iteration' or 'exception'
    :param outlier_detector_kwargs: the constructor arguments for the underlying detector
    """
    if strategy not in __strategies__:
        raise ValueError(
            'Strategy "{}" unknown, please pick one in {}'.format(
                strategy, __strategies__
            )
        )

    if distribution_id is None:
        d_id = uuid4()
    else:
        d_id = distribution_id

    if strategy == "iteration":

        def iterative_outlier_filter_generator(func):
            def wrapper(*args, **kwargs):
                od = _retrieve_filter_instance(
                    func, args, d_id, distribution_id, **outlier_detector_kwargs
                )
                sample = func(*args, **kwargs)
                while od.is_outlier(sample):
                    sample = func(*args, **kwargs)
                return sample

            return wrapper

        return iterative_outlier_filter_generator
    elif strategy == "exception":

        def exception_outlier_filter_generator(func):
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

        return exception_outlier_filter_generator
    else:

        def recursive_outlier_filter_generator(func):
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

        return recursive_outlier_filter_generator


def destroy_filter(distribution_id):
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
    def __init__(self, strategy="iteration", limit=None, **kwargs):
        if strategy not in __strategies__:
            raise ValueError(
                'Strategy "{}" unknown, please pick one in {}'.format(
                    strategy, __strategies__
                )
            )

        OutlierDetector.__init__(self, **kwargs)

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

    def filter(self, func, *args, **kwargs):
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
        raise StopIteration("Limit hit for subsequent outliers discarded.")
