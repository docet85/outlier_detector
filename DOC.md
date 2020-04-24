<a name=".outlier_detector"></a>
## outlier\_detector

<a name=".outlier_detector.filters"></a>
## outlier\_detector.filters

<a name=".outlier_detector.filters.filter_outlier"></a>
#### filter\_outlier

```python
filter_outlier(distribution_id=None, strategy='recursion', **outlier_detector_kwargs)
```

Wraps a generic "pop" or "get" function, returning a sample of a gaussian distribution, with an outlier filter.
When meeting an outlier the filter omits it and, depending on the strategy, it may call recursively the wrapped
function, iteratively call the wrapped function or raising a ``ValueError``. Relies on ``OutlierDetector`` whose
args can be forwarded using the proper argument.

:rtype: function

:type distribution_id: any
:type strategy: str

**Arguments**:

- `distribution_id`: unique identifier for the distribution. In case empty, this is inferred runtime. In case
wrapping a method, the first argument hash is used as default.
- `strategy`: 'recursion', 'iteration' or 'exception'
- `outlier_detector_kwargs`: the constructor arguments for the underlying detector

<a name=".outlier_detector.filters.destroy_filter"></a>
#### destroy\_filter

```python
destroy_filter(distribution_id)
```

Given an assigned distribution id, destroys the associated detector below the filter. Since the detector
is a singleton instantiated on demand, this is the final effect of deleting the recorded samples buffer.

**Arguments**:

- `distribution_id`: the id associated toa filter on decoration

<a name=".outlier_detector.detectors"></a>
## outlier\_detector.detectors

<a name=".outlier_detector.detectors.OutlierDetector"></a>
### OutlierDetector

```python
class OutlierDetector()
```

Detector class, for the recognition of novel outlier in a Gaussian distribution. It holds non-outlier values to fill
a moving window buffer of given length. Computes whether the incoming ``new_value`` is an outlier with respect to
the stored distribution samples in buffer. It computes a double tailed Dixon's Q-test, with the given ``confidence``
, along with testing the standard deviation of the new value considering the boundary (**mean** -``sigma_threshold``
**sigma**, **mean** + ``sigma_threshold``  **sigma** ).

<a name=".outlier_detector.detectors.OutlierDetector.__init__"></a>
#### \_\_init\_\_

```python
 | __init__(confidence=0.95, buffer_samples=14, sigma_threshold=2)
```

:type buffer_samples: int
:type confidence: float
:type sigma_threshold: float

**Arguments**:

- `buffer_samples`: Accepted length is between 5 and 27 samples.
- `confidence`: The confidence for the outlier estimation: since Dixon's test relies on tabled values the
available confidence steps are: 0.90, 0.95 and 0.99. Defaults to 0.95. Also percentage values are
accepted (i.e. 90, 95 and 99).
- `sigma_threshold`: multiplier for further analysis, samples outside the sigma range are marked as "warning"
It must be greater than 0.

<a name=".outlier_detector.detectors.OutlierDetector.is_outlier"></a>
#### is\_outlier

```python
 | is_outlier(new_sample)
```

Evaluates the incoming sample and (in case it is valid) stores it in internal buffer.

Testes if the sample an outlier is an outlier based on Dixon's Q-test with given confidence.

:type new_sample: float

**Arguments**:

- `new_sample`: distribution new sample

**Returns**:

true in case the sample is outlier

<a name=".outlier_detector.detectors.OutlierDetector.is_outside_sigma_bound"></a>
#### is\_outside\_sigma\_bound

```python
 | is_outside_sigma_bound(new_sample)
```

Evaluates the incoming sample and (in case it is valid) stores it in internal buffer.

In case the new value is valid the result is False, otherwise if outside the sigma threshold.

:type new_sample: float

**Arguments**:

- `new_sample`: distribution new sample

**Returns**:

True for "warnings" and False for valid samples

<a name=".outlier_detector.detectors.OutlierDetector.get_outlier_score"></a>
#### get\_outlier\_score

```python
 | get_outlier_score(new_sample)
```

Evaluates the incoming sample and (in case it is valid) stores it in internal buffer.

In case the new value is valid the result is 0, otherwise 1 (outside the sigma threshold) or 2 an outlier
based on Dixon's Q-test with given confidence.
:type new_sample: float

**Arguments**:

- `new_sample`: distribution new sample

**Returns**:

0 for valid samples, 1 for warning, 2 for outliers

<a name=".outlier_detector.functions"></a>
## outlier\_detector.functions

<a name=".outlier_detector.functions.get_outlier_score"></a>
#### get\_outlier\_score

```python
get_outlier_score(distribution, new_value, confidence=0.95, sigma_threshold=2)
```

Computes whether the incoming ``new_value`` is an outlier with respect to the given ``distribution``. It computes
a double tailed Dixon's Q-test, with the given ``confidence``, along with testing the standard deviation of the
new value considering the boundary (**mean** -``sigma_threshold`` **sigma**, **mean** + ``sigma_threshold``
**sigma** ). In case the new value is valid the result is 0, otherwise 1 (outside the sigma threshold) or 2 an outlier
based on Dixon's Q-test with given confidence.

:type distribution: list
:type new_value: float
:type confidence: float
:type sigma_threshold: float

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

<a name=".outlier_detector.functions.is_outlier"></a>
#### is\_outlier

```python
is_outlier(distribution, new_value, confidence=0.95)
```

Computes whether the incoming ``new_value`` is an outlier with respect to the given ``distribution``. It computes
a double tailed Dixon's Q-test, with the given ``confidence``. In case the new value is valid the result is False,
otherwise True.

:type distribution: list
:type new_value: float
:type confidence: float

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

