import unittest

from outlier_detector.exceptions import OutlierException
from outlier_detector.filters import filter_outlier, OutlierFilter


class TestGen:
    def __init__(self, data):
        self.data = data
        self.cursor = 0

    def pop(self):
        res = self.data[self.cursor]
        self.cursor += 1
        return res


class EndToEndTest(unittest.TestCase):
    def setUp(self):
        self.aset = [
            1,
            2,
            3,
            1,
            2,
            2,
            3,
            1,
            2,
            2,
            3,
            8,
            4,
            2,
            2,
            1,
            3,
            0,
            2,
            3,
            2,
            -5,
            8,
        ]

    def test_outlier_or_warning_detection_class(self):
        from outlier_detector.detectors import OutlierDetector

        od = OutlierDetector()
        for el in self.aset:
            res = od.get_outlier_score(el)
            if el > 4 or el < 0:
                self.assertTrue(res == 2, "Missed outlier")
            else:
                self.assertFalse(res == 2, "False positive outlier")

            if el > 3 or el < 1:
                self.assertTrue(res >= 1, "Missed warning")
            else:
                self.assertFalse(res >= 1, "False positive warning")

    def test_outlier_detection_class(self):
        from outlier_detector.detectors import OutlierDetector

        od = OutlierDetector()
        for el in self.aset:
            res = od.is_outlier(el)
            if el > 4 or el < 0:
                self.assertTrue(res, "Missed outlier")
            else:
                self.assertFalse(res, "False positive outlier")

    def test_warning_detection_class(self):
        from outlier_detector.detectors import OutlierDetector

        od = OutlierDetector()
        for el in self.aset:
            res = od.is_outside_sigma_bound(el)
            if el > 3 or el < 1:
                self.assertTrue(res, "Missed warning")
            else:
                self.assertFalse(res, "False positive warning")

    def test_outlier_or_warning_function(self):
        from outlier_detector.functions import get_outlier_score
        from copy import copy

        floating_buffer = copy(self.aset[:5])

        for el in range(6, len(self.aset)):
            res = get_outlier_score(floating_buffer, self.aset[el])

            if self.aset[el] > 4 or self.aset[el] < 0:
                self.assertTrue(res == 2, "Missed outlier: index " + str(el))
            else:
                self.assertFalse(res == 2, "False positive outlier: index " + str(el))

            if self.aset[el] > 3 or self.aset[el] < 1:
                self.assertTrue(res >= 1, "Missed warning: index " + str(el))
            else:
                self.assertFalse(res >= 1, "False positive warning: index " + str(el))

            if res < 2:
                floating_buffer.append(self.aset[el])
                if len(floating_buffer) > 14:
                    floating_buffer = copy(floating_buffer[1:])

    def test_outlier_function(self):
        from outlier_detector.functions import is_outlier
        from copy import copy

        floating_buffer = copy(self.aset[:5])

        for el in range(6, len(self.aset)):
            res = is_outlier(floating_buffer, self.aset[el])

            if self.aset[el] > 4 or self.aset[el] < 0:
                self.assertTrue(res, "Missed outlier: index " + str(el))
            else:
                self.assertFalse(res, "False positive outlier: index " + str(el))

            if not res:
                floating_buffer.append(self.aset[el])
                if len(floating_buffer) > 14:
                    floating_buffer = copy(floating_buffer[1:])

    def test_filter_decorator_recursive(self):
        class TempTestGen(TestGen):
            @filter_outlier(strategy="recursion")
            def pop(self):
                return super().pop()

        tg = TempTestGen(self.aset)
        counter = 0
        while counter < len(self.aset):
            try:
                r = tg.pop()
            except IndexError:
                return
            self.assertLessEqual(r, 4, "Not filtered outlier")
            self.assertGreaterEqual(r, 0, "Not filtered outlier")

    def test_filter_decorator_iterative(self):
        class TempTestGen(TestGen):
            @filter_outlier(strategy="iteration")
            def pop(self):
                return super().pop()

        tg = TempTestGen(self.aset)
        counter = 0
        while counter < len(self.aset):
            try:
                r = tg.pop()
            except IndexError:
                return
            self.assertLessEqual(r, 4, "Not filtered outlier")
            self.assertGreaterEqual(r, 0, "Not filtered outlier")

    def test_filter_decorator_generative(self):
        class TempTestGen(TestGen):
            @filter_outlier(strategy="generation")
            def pop(self):
                return super().pop()

        tg = TempTestGen(self.aset)
        try:
            for sample in tg.pop():
                self.assertLessEqual(sample, 4, "Not filtered outlier")
                self.assertGreaterEqual(sample, 0, "Not filtered outlier")
        except IndexError:
            pass

    def test_filter_decorator_raising(self):
        class TempTestGen(TestGen):
            @filter_outlier(strategy="exception")
            def pop(self):
                return super().pop()

        tg = TempTestGen(self.aset)
        counter = 0
        while counter < len(self.aset):
            try:
                r = tg.pop()
            except IndexError:
                return
            except OutlierException as e:
                valid = 0 < e.value < 4
                self.assertFalse(valid, "Filtered valid data")
                continue
            self.assertLessEqual(r, 4, "Not filtered outlier")
            self.assertGreaterEqual(r, 0, "Not filtered outlier")

    def test_filter_object_iterative(self):
        of = OutlierFilter()
        tg = TestGen(self.aset)
        counter = 0
        try:
            for sample in of.filter(tg.pop):
                counter += 1
                self.assertLessEqual(sample, 4, "Not filtered outlier")
                self.assertGreaterEqual(sample, 0, "Not filtered outlier")
        except IndexError:
            pass
        self.assertGreater(counter, 0, "Iterator not run or no test data")

    def test_filter_object_exception_while_true(self):
        of = OutlierFilter(strategy="exception")
        tg = TestGen(self.aset)
        filtered_sample = of.filter(tg.pop)
        counter = 0
        while True:
            counter += 1
            try:
                sample = next(filtered_sample)
            except OutlierException as e:
                valid = 0 < e.value < 4
                self.assertFalse(valid, "Filtered valid data")
                continue
            except (IndexError, StopIteration):
                break
            self.assertLessEqual(sample, 4, "Not filtered outlier")
            self.assertGreaterEqual(sample, 0, "Not filtered outlier")
        self.assertGreater(counter, 0, "Iterator not run or no test data")

    def test_filter_object_exception_for(self):
        of = OutlierFilter(strategy="exception")
        tg = TestGen(self.aset)
        counter = 0
        while True:
            try:
                for sample in of.filter(tg.pop):
                    self.assertLessEqual(sample, 4, "Not filtered outlier")
                    self.assertGreaterEqual(sample, 0, "Not filtered outlier")
                    counter += 1
            except OutlierException as e:
                valid = 0 < e.value < 4
                self.assertFalse(valid, "Filtered valid data")
                counter += 1
                continue
            except IndexError:
                break
        self.assertGreater(counter, 0, "Iterator not run or no test data")

    def test_filter_object_iterative_limit(self):
        of = OutlierFilter(limit=1)
        tg = TestGen(self.aset)
        counter = 0
        try:
            for sample in of.filter(tg.pop):
                counter += 1
                self.assertLessEqual(sample, 4, "Not filtered outlier")
                self.assertGreaterEqual(sample, 0, "Not filtered outlier")
        except OutlierException:
            self.assertGreater(counter, 0, "Iterator not run or no test data")
            return
        self.fail("Expected to hit the outlier limit")
