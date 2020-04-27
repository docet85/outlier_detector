<a name=".filters"></a>
## filters

<a name=".filters.filter_outlier"></a>
#### filter\_outlier

```python
filter_outlier(distribution_id: Any = None, strategy: str = "recursion", **outlier_detector_kwargs: Dict) -> Callable
```

Wraps a generic "pop" or "get" function, returning a sample of a gaussian distribution, with an outlier filter.
When meeting an outlier the filter omits it and, depending on the strategy, it may call recursively the wrapped
function, iteratively call the wrapped function or raising a ``ValueError``. Relies on ``OutlierDetector`` whose
args can be forwarded using the proper argument.

**Arguments**:

- `distribution_id`: unique identifier for the distribution. In case empty, this is inferred runtime. In case
wrapping a method, the first argument hash is used as default.
- `strategy`: 'recursion', 'iteration' or 'exception'
- `outlier_detector_kwargs`: the constructor arguments for the underlying detector

**Raises**:

- `ValueError`: when strategy is invalid
- `OutlierException`: when strategy is 'exception' and an outlier is found

<a name=".filters.destroy_filter"></a>
#### destroy\_filter

```python
destroy_filter(distribution_id: Any)
```

Given an assigned distribution id, destroys the associated detector below the filter. Since the detector
is a singleton instantiated on demand, this is the final effect of deleting the recorded samples buffer.

**Arguments**:

- `distribution_id`: the id associated toa filter on decoration

<a name=".filters.OutlierFilter"></a>
### OutlierFilter

```python
class OutlierFilter(OutlierDetector)
```

Exploits an OutlierDetector to expose the same functionality of the filter decorator.
It wraps a generic "pop" or "get" function, returning a sample of a gaussian distribution, with an outlier filter.
When meeting an outlier the filter omits it and, depending on the strategy, it may raise a ``ValueError``.
Relies on ``OutlierDetector`` whose args can be forwarded using the proper argument.

<a name=".filters.OutlierFilter.__init__"></a>
#### \_\_init\_\_

```python
 | __init__(strategy="iteration", limit=None, **outlier_detector_kwargs)
```

**Arguments**:

- `distribution_id`: unique identifier for the distribution. In case empty, this is inferred runtime. In case
wrapping a method, the first argument hash is used as default.
- `strategy`: 'recursion', 'iteration' or 'exception'
- `outlier_detector_kwargs`: the constructor arguments for the underlying detector

**Raises**:

- `ValueError`: when strategy is invalid

<a name=".filters.OutlierFilter.filter"></a>
#### filter

```python
 | filter(func: Callable, *args: List, **kwargs: Dict) -> float
```

**Raises**:

- `OutlierException`: when strategy is 'exception' and an outlier is found

**Arguments**:

- `func`:
- `args`:
- `kwargs`:

**Returns**:

<a name=".detectors"></a>
## detectors

<a name=".detectors.OutlierDetector"></a>
### OutlierDetector

```python
class OutlierDetector()
```

Detector class, for the recognition of novel outlier in a Gaussian distribution. It holds non-outlier values to fill
a moving window buffer of given length. Computes whether the incoming ``new_value`` is an outlier with respect to
the stored distribution samples in buffer. It computes a double tailed Dixon's Q-test, with the given ``confidence``
, along with testing the standard deviation of the new value considering the boundary (**mean** -``sigma_threshold``
**sigma**, **mean** + ``sigma_threshold``  **sigma** ).

<a name=".detectors.OutlierDetector.__init__"></a>
#### \_\_init\_\_

```python
 | __init__(confidence: float = 0.95, buffer_samples: int = 14, sigma_threshold: float = 2) -> None
```

**Arguments**:

- `buffer_samples`: Accepted length is between 5 and 27 samples.
- `confidence`: The confidence for the outlier estimation: since Dixon's test relies on tabled values the
available confidence steps are: 0.90, 0.95 and 0.99. Defaults to 0.95. Also percentage values are
accepted (i.e. 90, 95 and 99).
- `sigma_threshold`: multiplier for further analysis, samples outside the sigma range are marked as "warning"
It must be greater than 0.

<a name=".detectors.OutlierDetector.is_outlier"></a>
#### is\_outlier

```python
 | is_outlier(new_sample: float) -> bool
```

Evaluates the incoming sample and (in case it is valid) stores it in internal buffer.

Testes if the sample an outlier is an outlier based on Dixon's Q-test with given confidence.

**Arguments**:

- `new_sample`: distribution new sample

**Returns**:

true in case the sample is outlier

<a name=".detectors.OutlierDetector.is_outside_sigma_bound"></a>
#### is\_outside\_sigma\_bound

```python
 | is_outside_sigma_bound(new_sample: float) -> bool
```

Evaluates the incoming sample and (in case it is valid) stores it in internal buffer.

In case the new value is valid the result is False, otherwise if outside the sigma threshold.

**Arguments**:

- `new_sample`: distribution new sample

**Returns**:

True for "warnings" and False for valid samples

<a name=".detectors.OutlierDetector.get_outlier_score"></a>
#### get\_outlier\_score

```python
 | get_outlier_score(new_sample: float) -> int
```

Evaluates the incoming sample and (in case it is valid) stores it in internal buffer.

In case the new value is valid the result is 0, otherwise 1 (outside the sigma threshold) or 2 an outlier
based on Dixon's Q-test with given confidence.

**Arguments**:

- `new_sample`: distribution new sample

**Returns**:

0 for valid samples, 1 for warning, 2 for outliers

<a name=".functions"></a>
## functions

<a name=".functions.get_outlier_score"></a>
#### get\_outlier\_score

```python
get_outlier_score(distribution: List[float], new_value: float, confidence: float = 0.95, sigma_threshold: float = 2) -> int
```

Computes whether the incoming ``new_value`` is an outlier with respect to the given ``distribution``. It computes
a double tailed Dixon's Q-test, with the given ``confidence``, along with testing the standard deviation of the
new value considering the boundary (**mean** -``sigma_threshold`` **sigma**, **mean** + ``sigma_threshold``
**sigma** ). In case the new value is valid the result is 0, otherwise 1 (outside the sigma threshold) or 2 an outlier
based on Dixon's Q-test with given confidence.

**Arguments**:

- `distribution`: The incoming numeric set of values representing the distribution. Ideally this has been removed
the linear monotonic trend or any other drift (in case applicable) so to make it a Gaussian distribution. Any trend
indeed affects the outlier estimation. Accepted length is between 5 and 27 samples.
- `new_value`: The novel sample to be evaluated.
- `confidence`: The confidence for the outlier estimation: since Dixon's test relies on tabled values the
available confidence steps are: 0.90, 0.95 and 0.99. Defaults to 0.95. Also percentage values are accepted (i.e.
90, 95 and 99).
- `sigma_threshold`: multiplier for further analysis, samples outside the sigma boundary (**mean** -
``sigma_threshold`` **sigma**, **mean** + ``sigma_threshold`` **sigma** ) are marked as "warning"

**Returns**:

0 for valid samples, 1 for outside the sigma threshold ("warning"), 2 for outliers

**Raises**:

- `ValueError`: If sigma_threshold is negative or 0

<a name=".functions.is_outlier"></a>
#### is\_outlier

```python
is_outlier(distribution: List[float], new_value: float, confidence: float = 0.95, sigma_threshold: float = 2) -> bool
```

Computes whether the incoming ``new_value`` is an outlier with respect to the given ``distribution``. It computes
a double tailed Dixon's Q-test, with the given ``confidence``. In case the new value is valid the result is False,
otherwise True.

**Arguments**:

- `distribution`: The incoming numeric set of values representing the distribution. Ideally this has been removed
the linear monotonic trend or any other drift (in case applicable) so to make it a Gaussian distribution. Any trend
indeed affects the outlier estimation. Accepted length is between 5 and 27 samples.
- `new_value`: The novel sample to be evaluated.
- `confidence`: The confidence for the outlier estimation: since Dixon's test relies on tabled values the
available confidence steps are: 0.90, 0.95 and 0.99. Defaults to 0.95. Also percentage values are accepted (i.e.
90, 95 and 99).

**Returns**:

False for valid samples, True for outliers

**Raises**:

- `ValueError`: when confidence value set is not tabled;
- `ValueError`: in case distribution  confidence value set is not tabled;
