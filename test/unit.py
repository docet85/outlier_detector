import unittest
from copy import copy
from unittest.mock import patch

from outlier_detector.detectors import OutlierDetector
from outlier_detector.filters import filter_outlier, OutlierFilter
from outlier_detector.functions import get_outlier_score, is_outlier


class InputValidation(unittest.TestCase):
    def setUp(self) -> None:
        # Since this is a validation tests set then we setup a valid input and override it as needed in tests
        self.dist = [0, 1, 2, 3, 4, 6, 7, 8]
        self.sample = 4

    # Function
    def test_given_invalid_type_sample_then_raise(self):
        self.assertRaises(TypeError, get_outlier_score, self.dist, "wrong")

    def test_given_invalid_type_distribution_then_raise(self):
        self.assertRaises(
            TypeError,
            get_outlier_score,
            "definitely wrong, so wrong indeed",
            self.sample,
        )
        self.assertRaises(
            TypeError,
            get_outlier_score,
            ["definitely", "wrong", "so", "wrong", "indeed"],
            self.sample,
        )

    def test_given_short_distribution_then_raise(self):
        self.assertRaises(ValueError, get_outlier_score, self.dist[:3], self.sample)

    def test_given_long_distribution_then_raise(self):
        self.assertRaises(ValueError, get_outlier_score, self.dist * 4, self.sample)

    def test_given_invalid_confidence_then_raise(self):
        self.assertRaises(
            ValueError, get_outlier_score, self.dist, self.sample, confidence=0.2
        )

    def test_given_invalid_sigma_threshold_then_raise(self):
        self.assertRaises(
            ValueError, get_outlier_score, self.dist, self.sample, sigma_threshold=0
        )
        self.assertRaises(
            ValueError, get_outlier_score, self.dist, self.sample, sigma_threshold=-1
        )

    def test_given_valid_inputs_then_return_a_value(self):
        val = get_outlier_score(self.dist, self.sample)
        self.assertIsNotNone(val)

    def test_given_confidence_percentage_then_return_a_value(self):
        val = get_outlier_score(self.dist, self.sample, confidence=99)
        self.assertIsNotNone(val)

    # Filter
    def test_given_invalid_strategy_decorator_then_raise(self):
        try:

            class FailGen:
                @filter_outlier(strategy="invalid")
                def pop(self):
                    pass

            fg = FailGen()
            self.fail("The decorator strategy is not rejected as invalid")
        except ValueError:
            pass

    def test_given_invalid_type_sample_to_decorator_then_raise(self):
        try:

            class FailGen:
                @filter_outlier()
                def pop(self):
                    return "spam"

            fg = FailGen()
            fg.pop()
            self.fail("The function return type is not rejected as invalid")
        except TypeError:
            pass

    @patch("outlier_detector.detectors.OutlierDetector.is_outlier", return_value=False)
    @patch("outlier_detector.detectors.OutlierDetector.__init__", return_value=None)
    def test_given_extra_input_to_decorator_then_they_are_forwarded_to_detector(
        self, mock, _
    ):
        extra_kwargs_for_detector = {
            "sigma_threshold": 4,
            "confidence": 0.99,
            "buffer_samples": 10,
        }

        class GenForward:
            @filter_outlier(**extra_kwargs_for_detector)
            def pop(self):
                pass

        fg = GenForward()
        fg.pop()

        self.assertTrue(mock.called)
        self.assertEqual(mock.call_args[1], extra_kwargs_for_detector)

    def test_given_invalid_strategy_object_then_raise(self):
        try:
            OutlierFilter(strategy="invalid")
            self.fail("The decorator strategy is invalid")
        except ValueError:
            pass

    def test_given_recursion_strategy_object_then_fallback_iterative_limit_20(self):
        od = OutlierFilter(strategy="recursion")
        self.assertEqual(od.strategy, "iteration")
        self.assertEqual(od.limit, 20)

    def test_given_exception_strategy_with_limit_object_then_ignore_limit(self):
        od = OutlierFilter(strategy="exception", limit=10)
        self.assertEqual(od.strategy, "exception")
        self.assertIsNone(od.limit)

    @patch("outlier_detector.detectors.OutlierDetector.is_outlier", return_value=False)
    @patch("outlier_detector.detectors.OutlierDetector.__init__", return_value=None)
    def test_given_extra_input_to_outlier_filter_then_they_are_forwarded_to_detector(
        self, mock, _
    ):
        extra_kwargs_for_detector = {
            "sigma_threshold": 4,
            "confidence": 0.99,
            "buffer_samples": 10,
        }

        of = OutlierFilter(strategy="iteration", limit=15, **extra_kwargs_for_detector)

        self.assertTrue(mock.called)
        self.assertEqual(mock.call_args[1], extra_kwargs_for_detector)

    # Detector
    def test_given_short_buffer_then_raise(self) -> None:
        self.assertRaises(ValueError, OutlierDetector, buffer_samples=3)

    def test_given_long_buffer_then_raise(self):
        self.assertRaises(ValueError, OutlierDetector, buffer_samples=30)

    def test_given_invalid_confidence_to_detector_then_raise(self):
        self.assertRaises(ValueError, OutlierDetector, confidence=0.2)

    def test_given_invalid_sigma_threshold_to_detector_then_raise(self):
        self.assertRaises(ValueError, OutlierDetector, sigma_threshold=0)
        self.assertRaises(ValueError, OutlierDetector, sigma_threshold=-1)

    def test_given_valid_sigma_threshold_to_detector_then_set_it(self):
        from outlier_detector import Qvals

        od = OutlierDetector(confidence=0.99)
        self.assertEqual(od.q, Qvals[0.99], "Confidence error")
        od = OutlierDetector(confidence=99)
        self.assertEqual(od.q, Qvals[0.99], "Confidence error")

    def test_given_invalid_sample_type_to_detector_then_raise(self):
        od = OutlierDetector()
        try:
            od.is_outlier("spam")
            self.fail("Detector not rejecting invalid input type")
        except TypeError:
            pass


class AuxiliaryTest(unittest.TestCase):
    new_value = 5
    test_odd_sequence = [1, 4, 6, 8, 10]
    test_even_sequence = [1, 4, 6, 8, 10, 12]
    expected_odd_sequence = [1, 4, 5, 6, 8, 10]
    expected_even_sequence = [1, 4, 5, 6, 8, 10, 12]

    def setUp(self):
        self.test_filter = OutlierDetector(buffer_samples=5)
        self.test_filter._buffer = copy(self.test_odd_sequence)

    def test_given_first_three_vals_then_insertion_points_are_correct(self):
        self.test_filter._buffer = []
        insertion_point = self.test_filter.__sorted_insert__(0)
        self.assertEqual(insertion_point, 0, "Wrong insertion point")
        insertion_point = self.test_filter.__sorted_insert__(1)
        self.assertEqual(insertion_point, 1, "Wrong insertion point")
        insertion_point = self.test_filter.__sorted_insert__(2)
        self.assertEqual(insertion_point, 2, "Wrong insertion point")
        self.assertEqual(self.test_filter._buffer, [0, 1, 2])

    def test_given_new_value_odd_seq_then_insertion_point_is_correct(self):
        insertion_point = self.test_filter.__sorted_insert__(self.new_value)
        self.assertEqual(insertion_point, 2, "Wrong insertion point")
        self.assertEqual(self.test_filter._buffer, self.expected_odd_sequence)

    def test_given_new_value_even_seq_then_insertion_point_is_correct(self):
        self.test_filter._buffer = copy(self.test_even_sequence)
        insertion_point = self.test_filter.__sorted_insert__(self.new_value)
        self.assertEqual(insertion_point, 2, "Wrong insertion point")
        self.assertEqual(self.test_filter._buffer, self.expected_even_sequence)

    def test_given_new_value_at_first_odd_seq_then_insertion_point_is_correct(self):
        insertion_point = self.test_filter.__sorted_insert__(0)
        self.assertEqual(insertion_point, 0, "Wrong insertion point")
        self.assertEqual(self.test_filter._buffer, [0] + self.test_odd_sequence)

    def test_given_new_value_at_first_even_seq_then_insertion_point_is_correct(self):
        self.test_filter._buffer = copy(self.test_even_sequence)
        insertion_point = self.test_filter.__sorted_insert__(0)
        self.assertEqual(insertion_point, 0, "Wrong insertion point")
        self.assertEqual(self.test_filter._buffer, [0] + self.test_even_sequence)

    def test_given_new_value_at_last_odd_seq_then_insertion_point_is_correct(self):
        insertion_point = self.test_filter.__sorted_insert__(15)
        self.assertEqual(insertion_point, 5, "Wrong insertion point")
        self.assertEqual(self.test_filter._buffer, self.test_odd_sequence + [15])

    def test_given_new_value_at_last_even_seq_then_insertion_point_is_correct(self):
        self.test_filter._buffer = copy(self.test_even_sequence)
        insertion_point = self.test_filter.__sorted_insert__(15)
        self.assertEqual(insertion_point, 6, "Wrong insertion point")
        self.assertEqual(self.test_filter._buffer, self.test_even_sequence + [15])

    def test_given_invalid_start_then_raise_assertion_error(self):
        try:
            self.test_filter.__sorted_insert__(4, 0.5, len(self.test_even_sequence))
            self.fail("Start float, assertion fail expected")
        except AssertionError:
            pass

        try:
            self.test_filter.__sorted_insert__(
                4, len(self.test_even_sequence) + 2, len(self.test_even_sequence)
            )
            self.fail("Start out of bounds, assertion fail expected")
        except AssertionError:
            pass

        try:
            self.test_filter.__sorted_insert__(4, -1, len(self.test_even_sequence))
            self.fail("Start out of bounds, assertion fail expected")
        except AssertionError:
            pass

    def test_given_invalid_end_then_raise_assertion_error(self):
        try:
            self.test_filter.__sorted_insert__(4, 0, 3.5)
            self.fail("Start float, assertion fail expected")
        except AssertionError:
            pass

        try:
            self.test_filter.__sorted_insert__(4, 0, len(self.test_even_sequence) + 2)
            self.fail("Start out of bounds, assertion fail expected")
        except AssertionError:
            pass

        try:
            self.test_filter.__sorted_insert__(4, 0, -1)
            self.fail("Start out of bounds, assertion fail expected")
        except AssertionError:
            pass

    def test_given_start_greater_than_end_then_raise_assertion_error(self):
        try:
            self.test_filter.__sorted_insert__(4, 3, 1)
            self.fail("Start out of bounds, assertion fail expected")
        except AssertionError:
            pass


class FunctionalTests(unittest.TestCase):
    def test_given_flat_distr_return_no_outlier(self):
        value = 2
        distr = [value] * 10
        o = is_outlier(distr, value)
        self.assertFalse(o, "No outlier expected for flat distribution (is_outlier)")
        s = get_outlier_score(distr, value)
        self.assertEqual(
            s, 0, "No outlier expected for flat distribution (get_outlier_score)"
        )

        od = OutlierDetector()
        od._buffer = distr
        o = od.is_outlier(value)
        self.assertFalse(
            o, "No outlier expected for flat distribution (detector.is_outlier)"
        )
        s = od.get_outlier_score(value)
        self.assertEqual(
            s,
            0,
            "No outlier expected for flat distribution (detector.get_outlier_score)",
        )

        class Gen:
            @filter_outlier(distribution_id="test", strategy="exception")
            def pop(self):
                return value

        g = Gen()
        g.pop()
        from outlier_detector.filters import __alive_filters__

        __alive_filters__["test"]._buffer = distr
        self.assertEqual(
            value, g.pop(), "No outlier expected for flat distribution (filter)"
        )

    def test_given_filter_with_known_id_when_remove_it_is_no_more_available(self):
        class Gen:
            @filter_outlier(distribution_id="test", strategy="exception")
            def pop(self):
                return 0

        g = Gen()
        g.pop()
        from outlier_detector.filters import __alive_filters__, destroy_filter

        self.assertIn("test", __alive_filters__)
        destroy_filter("test")
        self.assertNotIn("test", __alive_filters__)
