from outlier_detector import Qvals
from statistics import stdev, StatisticsError


class OutlierDetector:
    """
    Detector class, for the recognition of novel outlier in a Gaussian distribution. It holds non-outlier values to fill
    a moving window buffer of given length. Computes whether the incoming ``new_value`` is an outlier with respect to
    the stored distribution samples in buffer. It computes a double tailed Dixon's Q-test, with the given ``confidence``
    , along with testing the standard deviation of the new value considering the boundary (**mean** -``sigma_threshold``
    **sigma**, **mean** + ``sigma_threshold``  **sigma** ).
    """

    def __init__(self, confidence=0.95, buffer_samples=14, sigma_threshold=2):
        """
        :type buffer_samples: int
        :type confidence: float
        :type sigma_threshold: float

        :param buffer_samples: Accepted length is between 5 and 27 samples.
        :param confidence: The confidence for the outlier estimation: since Dixon's test relies on tabled values the
               available confidence steps are: 0.90, 0.95 and 0.99. Defaults to 0.95. Also percentage values are
               accepted (i.e. 90, 95 and 99).
        :param sigma_threshold: multiplier for further analysis, samples outside the sigma range are marked as "warning"
               It must be greater than 0.
        """
        if confidence > 1:
            confidence /= 100
        if not (confidence in Qvals):
            raise ValueError(
                "Confidence value not tabled, please pick between 0.90, 0.95, and 0.99"
            )
        if buffer_samples < 5 or buffer_samples > 27:
            raise ValueError(
                "Buffer distribution must have at least 5 elements and no more than 27"
            )
        if sigma_threshold <= 0:
            raise ValueError("Sigma threshold should be greater than 0")

        self.q = Qvals[confidence]
        self.buffer_samples = buffer_samples
        self.sigma = sigma_threshold
        self._buffer = []
        self._map = []
        return

    def is_outlier(self, new_sample):
        """
        Evaluates the incoming sample and (in case it is valid) stores it in internal buffer.

        Testes if the sample an outlier is an outlier based on Dixon's Q-test with given confidence.

        :type new_sample: float
        :param new_sample: distribution new sample
        :return: true in case the sample is outlier
        """
        old_sample_position = len(self._buffer)

        # we don't want to produce results if we don't have at least half the buffer
        if len(self._buffer) >= self.buffer_samples / 2 and len(self._buffer) >= 5:
            insertion_point = self._sorted_insert(new_sample)

            q = 0
            if insertion_point == 0:
                q = abs(self._buffer[1] - self._buffer[0])
            elif insertion_point == len(self._buffer) - 1:
                q = abs(self._buffer[-1] - self._buffer[-2])

            try:
                q /= abs(self._buffer[-1] - self._buffer[0])
            except ZeroDivisionError:
                pass

            if q > self.q[len(self._buffer)]:
                del self._buffer[insertion_point]
                return True

            if len(self._buffer) > self.buffer_samples:
                old_sample_position = self._map[0]
                del self._map[0]
                del self._buffer[old_sample_position]
        else:
            insertion_point = self._sorted_insert(new_sample)

        if old_sample_position != insertion_point:
            for i in range(len(self._map)):
                if old_sample_position < self._map[i] < insertion_point:
                    self._map[i] -= 1
                elif old_sample_position > self._map[i] >= insertion_point:
                    self._map[i] += 1

        self._map.append(insertion_point)

        return False

    def is_outside_sigma_bound(self, new_sample):
        """
        Evaluates the incoming sample and (in case it is valid) stores it in internal buffer.

        In case the new value is valid the result is False, otherwise if outside the sigma threshold.

        :type new_sample: float
        :param new_sample: distribution new sample
        :return: True for "warnings" and False for valid samples
        """
        return self.get_outlier_score(new_sample) > 0

    def get_outlier_score(self, new_sample):
        """
        Evaluates the incoming sample and (in case it is valid) stores it in internal buffer.

        In case the new value is valid the result is 0, otherwise 1 (outside the sigma threshold) or 2 an outlier
        based on Dixon's Q-test with given confidence.
        :type new_sample: float
        :param new_sample: distribution new sample
        :return: 0 for valid samples, 1 for warning, 2 for outliers
        """
        result = 0  # valid sample
        old_sample_position = len(self._buffer)

        # we don't want to produce results if we don't have at least half the buffer
        if len(self._buffer) >= self.buffer_samples / 2 and len(self._buffer) >= 5:
            mu = sum(self._buffer) / float(len(self._buffer))
            sd = stdev(self._buffer)

            insertion_point = self._sorted_insert(new_sample)

            q = 0
            if insertion_point == 0:
                q = abs(self._buffer[1] - self._buffer[0])
            elif insertion_point == len(self._buffer) - 1:
                q = abs(self._buffer[-1] - self._buffer[-2])

            try:
                q /= abs(self._buffer[-1] - self._buffer[0])
            except ZeroDivisionError:
                pass

            if q > self.q[len(self._buffer)]:
                del self._buffer[insertion_point]
                return 2  # outlier

            if new_sample > (mu + float(self.sigma) * sd) or new_sample < (
                mu - float(self.sigma) * sd
            ):
                result = 1  # valid, but outside sigma bound

            if len(self._buffer) > self.buffer_samples:
                old_sample_position = self._map[0]
                del self._map[0]
                del self._buffer[old_sample_position]
        else:
            insertion_point = self._sorted_insert(new_sample)

        if old_sample_position != insertion_point:
            for i in range(len(self._map)):
                if old_sample_position < self._map[i] < insertion_point:
                    self._map[i] -= 1
                elif old_sample_position > self._map[i] >= insertion_point:
                    self._map[i] += 1

        self._map.append(insertion_point)

        return result

    def _sorted_insert(self, new_value, start=0, end=None):
        if end is None:
            end = len(self._buffer)
        assert type(start) is int
        assert type(end) is int
        assert 0 <= start <= len(self._buffer)
        assert 0 <= end <= len(self._buffer)
        assert start <= end

        pivot = (end + start) // 2
        insertion = pivot
        if start != end:
            if new_value > self._buffer[pivot]:
                return self._sorted_insert(new_value, pivot + 1, end)
            elif new_value < self._buffer[pivot]:
                return self._sorted_insert(new_value, start, pivot)
        else:
            insertion = start
        self._buffer.insert(insertion, new_value)
        return insertion
