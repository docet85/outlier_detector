# Outlier Detector toolkit
[![Build Status](https://travis-ci.com/docet85/outlier_detector.svg?branch=dev)](https://travis-ci.com/docet85/outlier_detector)
[![codecov](https://codecov.io/gh/docet85/outlier_detector/branch/dev/graph/badge.svg)](https://codecov.io/gh/docet85/outlier_detector)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)


This project features a set of tools for outlier detection, marking or filtering away samples
as they come to your Python analysis code.

Most of the tools rely on double tailed Dixon's Q-test (https://en.wikipedia.org/wiki/Dixon%27s_Q_test).

## TL;DR
<details>
   <summary>I have a <code>sample</code>, and a know data <code>distribution</code>: is the sample an outlier?</summary>

```python
sample = 2.7
distribution = [0.1, 1.1, 4.78, 2.0, 7.2, 5.3]

from outlier_detector.functions import is_outlier
print(is_outlier(distribution, sample))
```

</details>

<details>
   <summary>I have a <code>distribution</code> and I iterate over it: is the n-th sample
   is an outlier?</summary>

```python
distribution = [0.1, 1.1, 4.78, 2.0, 7.2, 5.3, 8.1, -4.1, 5.4]
from outlier_detector.detectors import OutlierDetector
od = OutlierDetector(buffer_samples=5)
for x in distribution:
    print(od.is_outlier(x))
```
</details>

<details>
   <summary>I have a generating object from which I <code>pop</code> samples and I want only valid samples, rejecting outliers.</summary>

```python
distribution = [0.1, 1.1, 4.78, 2.0, 7.2, 5.3, 8.1, -14.1, 5.4]
from outlier_detector.filters import filter_outlier

class MyGen:
    def __init__(self):
        self.cursor = -1

    @filter_outlier()
    def pop(self):
        self.cursor += 1
        return distribution[self.cursor]

g = MyGen()
while True:
    try:
        r = g.pop()
        print(r)
    except IndexError:
        print('No more data')

```
</details>

## Documentation
The toolkit is organized so you can exploit one of the following pattern in the easiest way possible:
`functions` for static analysis, `detectors` for objects with internal buffers, and `filters` for decorators.

For documentation see [doc file](https://github.com/docet85/outlier_detector/blob/dev/DOC.md)
