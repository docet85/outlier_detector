import inspect
from uuid import uuid4

__alive_filters__ = {}
__strategies__ = ["recursion", "iteration", "exception"]

from outlier_detector.detectors import OutlierDetector


def filter_outlier(
    distribution_id=None, strategy="recursion", **outlier_detector_kwargs
):
    """Wraps a generic "pop" or "get" function, returning a sample of a gaussian distribution, with an outlier filter.
    When meeting an outlier the filter omits it and, depending on the strategy, it may call recursively the wrapped
    function, iteratively call the wrapped function or raising a ``ValueError``. Relies on ``OutlierDetector`` whose
    args can be forwarded using the proper argument.

    :rtype: function

    :type distribution_id: any
    :type strategy: str

    :param distribution_id: unique identifier for the distribution. In case empty, this is inferred runtime. In case
           wrapping a method, the first argument hash is used as default.
    :param strategy: 'recursion', 'iteration' or 'exception'
    :param outlier_detector_kwargs: the constructor arguments for the underlying detector
    """
    if strategy not in __strategies__:
        raise ValueError("Strategy {} unknown, please pick one in {}", strategy, [])

    if distribution_id is None:
        d_id = uuid4()
    else:
        d_id = distribution_id

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

    def exception_outlier_filter_generator(func):
        def wrapper(*args, **kwargs):
            od = _retrieve_filter_instance(
                func, args, d_id, distribution_id, **outlier_detector_kwargs
            )
            sample = func(*args, **kwargs)
            if od.is_outlier(sample):
                raise ValueError("Detected Outlier in distribution")
            else:
                return sample

        return wrapper

    if strategy == "iteration":
        return iterative_outlier_filter_generator
    elif strategy == "exception":
        return exception_outlier_filter_generator
    else:
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
