import unittest

from logging import debug as print


class ReadMeTests(unittest.TestCase):
    def test_function_example(self):
        sample = -14.5
        distribution = [0.1, 1.1, 4.78, 2.0, 7.2, 5.3]

        from outlier_detector.functions import is_outlier

        print(is_outlier(distribution, sample))

    def test_detector_example(self):
        distribution = [0.1, 1.1, 4.78, 2.0, 7.2, 5.3, 8.1, -14.1, 5.4]
        from outlier_detector.detectors import OutlierDetector

        od = OutlierDetector(buffer_samples=5)
        for x in distribution:
            print(od.is_outlier(x))

    def test_filter_example(self):
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
                print("No more data")
                break

    def test_filter_object_example(self):
        distribution = [0.1, 1.1, 4.78, 2.0, 7.2, 5.3, 8.1, -14.1, 5.4]
        from outlier_detector.filters import OutlierFilter

        class MyGen:
            def __init__(self):
                self.cursor = -1

            def pop(self):
                self.cursor += 1
                return distribution[self.cursor]

        g = MyGen()
        of = OutlierFilter()
        try:
            for sample in of.filter(g.pop):
                print(sample)
        except IndexError:
            print("No more data")
