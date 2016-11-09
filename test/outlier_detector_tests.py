import unittest


class Outlier_detector_test(unittest.TestCase):
    def test_outlier_detection_class(self):
        from outlier_detector import OutlierDetector
        aset = [1, 2, 3, 1, 2, 2, 3, 1, 2, 2, 3, 8, 4, 2, 2, 1,
                3, 0, 2, 3, 2, -5, 8]
        od = OutlierDetector()
        for el in aset:
            res = od.parse(el)
            if el > 4 or el < 0:
                self.assertTrue(res[0], "Missed outlier")
            else:
                self.assertFalse(res[0], "False positive outlier")

            if el > 3 or el < 1:
                self.assertTrue(res[1], "Missed warning")
            else:
                self.assertFalse(res[1], "False positive warning")

    def test_outlier_detection_single(self):
        from outlier_detector import OutlierDetector
        from copy import copy

        aset = [1, 2, 3, 1, 2, 2, 3, 1, 2, 2, 3, 8, 4, 2, 2, 1,
                3, 0, 2, 3, 2, -5, 8]

        od = OutlierDetector()
        floating_buffer = copy(aset[:5])

        for el in range(6, len(aset)):
            res = od.parse_single(floating_buffer, aset[el])

            if aset[el] > 4 or aset[el] < 0:
                self.assertTrue(res == 2, "Missed outlier: index " + str(el))
            else:
                self.assertFalse(res == 2, "False positive outlier: index " + str(el))

            if aset[el] > 3 or aset[el] < 1:
                self.assertTrue(res >= 1, "Missed warning: index " + str(el))
            else:
                self.assertFalse(res >= 1, "False positive warning: index " + str(el))

            if res < 2:
                floating_buffer.append(aset[el])
                if len(floating_buffer) > 14:
                    floating_buffer = copy(floating_buffer[1:])
