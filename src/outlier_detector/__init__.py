Qvals = {}
q90 = [0.941, 0.765, 0.642, 0.56, 0.507, 0.468, 0.437,
       0.412, 0.392, 0.376, 0.361, 0.349, 0.338, 0.329,
       0.32, 0.313, 0.306, 0.3, 0.295, 0.29, 0.285, 0.281,
       0.277, 0.273, 0.269, 0.266, 0.263, 0.26
       ]
Qvals[0.9] = {n: q for n, q in zip(range(3, len(q90) + 1), q90)}

q95 = [0.97, 0.829, 0.71, 0.625, 0.568, 0.526, 0.493, 0.466,
       0.444, 0.426, 0.41, 0.396, 0.384, 0.374, 0.365, 0.356,
       0.349, 0.342, 0.337, 0.331, 0.326, 0.321, 0.317, 0.312,
       0.308, 0.305, 0.301, 0.29
       ]
Qvals[0.95] = {n: q for n, q in zip(range(3, len(q95) + 1), q95)}

q99 = [0.994, 0.926, 0.821, 0.74, 0.68, 0.634, 0.598, 0.568,
       0.542, 0.522, 0.503, 0.488, 0.475, 0.463, 0.452, 0.442,
       0.433, 0.425, 0.418, 0.411, 0.404, 0.399, 0.393, 0.388,
       0.384, 0.38, 0.376, 0.372
       ]
Qvals[0.99] = {n: q for n, q in zip(range(3, len(q99) + 1), q99)}


class OutlierDetector:
    '''
    Builds a moving window buffer to compute a double tailed Dixon's Q-test
    plus a check on data sigma generating warnings
    '''

    def __init__(self, outlier_conf=0.95, window_length=14, warning_sigma_mulipt=2):
        from collections import deque
        if outlier_conf > 1:
            outlier_conf /= 100
        if not (outlier_conf in Qvals):
            raise ValueError("Confidence value not tabled, please pick between 0.90, 0.95, and 0.99")
        self.q = Qvals[outlier_conf]
        self.length = window_length - 1
        self.sigma = warning_sigma_mulipt
        self.buffer = deque()
        return

    @staticmethod
    def parse_single(distribution, new_value, outlier_conf=0.95, warning_sigma_mulipt=2):
        from copy import copy
        from statistics import stdev

        if outlier_conf > 1:
            outlier_conf /= 100
        if not (outlier_conf in Qvals):
            raise ValueError("Confidence value not tabled, please pick between 0.90, 0.95, and 0.99")
        q_vals = Qvals[outlier_conf]

        if len(distribution) < 5:
            raise ValueError('Input distribution must have at least 5 elements')

        mu = sum(distribution) / float(len(distribution))
        sd = stdev(distribution)

        x = copy(distribution)
        x.append(new_value)
        x.sort()

        q = 0
        if new_value == x[0]:
            q = abs(x[1] - x[0])
        if new_value == x[-1]:
            q = abs(x[-1] - x[-2])
        if q == 0:
            return 0

        try:
            q /= abs(x[-1] - x[0])
        except ZeroDivisionError:
            return 0

        if q > q_vals[len(x)]:
            return 2

        if new_value > (mu + float(warning_sigma_mulipt) * sd) or \
                        new_value < (mu - float(warning_sigma_mulipt) * sd):
            return 1
        return 0

    def parse(self, indata):
        from copy import copy
        from statistics import stdev, StatisticsError
        is_outlier = False
        is_warning = False

        drop = None

        try:
            mu = sum(self.buffer) / float(len(self.buffer))
            sd = stdev(self.buffer)
        except (ZeroDivisionError, StatisticsError):
            mu = 0
            sd = 0
            pass
        self.buffer.append(indata)
        # we don't want to produce results if we don't have at least half the buffer
        if len(self.buffer) < self.length / 2 or len(self.buffer) < 3:
            return is_outlier, is_warning
        # we have to drop the oldest value to maintain the buffer len
        if len(self.buffer) > self.length:
            drop = self.buffer.popleft()

        x = sorted(copy(self.buffer))

        q = 0
        if indata == x[0]:
            q = abs(x[1] - x[0])
        if indata == x[-1]:
            q = abs(x[-1] - x[-2])
        try:
            q /= abs(x[-1] - x[0])
        except ZeroDivisionError:
            pass
        if q > self.q[len(x)]:
            self.buffer.pop()  # if it's an outlier than drop it
            if drop is not None:
                self.buffer.appendleft(drop)
            is_outlier = True
            is_warning = True

        if not is_outlier:
            if indata > (mu + float(self.sigma) * sd) or \
                            indata < (mu - float(self.sigma) * sd):
                is_warning = True

        return is_outlier, is_warning
