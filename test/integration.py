import unittest

from outlier_detector.filters import filter_outlier


class TestGen:
    def __init__(self, data):
        self.data = data
        self.cursor = 0

    def pop(self):
        res = self.data[self.cursor]
        self.cursor += 1
        return res


class IntegrityTest(unittest.TestCase):
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

    def test_filter_crosstalk(self):
        class TempTestGen(TestGen):
            @filter_outlier(strategy="recursion")
            def pop(self):
                return super().pop()

        tg = TempTestGen(self.aset)
        tg_offset = TempTestGen([x + 5 for x in self.aset])
        counter = 0
        while counter < len(self.aset):
            try:
                r = tg.pop()
                r2 = tg_offset.pop()
            except IndexError:
                return
            self.assertLessEqual(r, 4, "Not filtered outlier")
            self.assertGreaterEqual(r, 0, "Not filtered outlier")
            self.assertLessEqual(r2, 9, "Not filtered outlier")
            self.assertGreaterEqual(r2, 5, "Not filtered outlier")

    def test_filter_shared_buffer(self):
        class TempTestGenTwo(TestGen):
            @filter_outlier(strategy="recursion", distribution_id=1)
            def pop(self):
                return super().pop()

        tg = TempTestGenTwo(self.aset)
        tg_offset = TempTestGenTwo([x + 1 for x in self.aset])
        counter = 0
        from outlier_detector.filters import __alive_filters__

        while counter < len(self.aset):
            try:
                r = tg.pop()
                r2 = tg_offset.pop()
                self.assertIn(1, __alive_filters__)
            except IndexError:
                return
            self.assertLessEqual(r, 5, "Not filtered outlier")
            self.assertGreaterEqual(r, 0, "Not filtered outlier")
            self.assertLessEqual(r2, 5, "Not filtered outlier")
            self.assertGreaterEqual(r2, 0, "Not filtered outlier")
