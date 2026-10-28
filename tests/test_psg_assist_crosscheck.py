"""Synthetic tests for the library cross-check of amendment 005, part D3 (careport.psg_assist_crosscheck)."""

import math
import unittest

from careport.psg_assist_bias import cohen_kappa, sign_test
from careport.psg_assist_crosscheck import compare_kappa, compare_sign_tests


def exact_binomial_two_sided(k: int, n: int) -> float:
    upper = sum(math.comb(n, i) for i in range(k, n + 1)) / 2 ** n
    lower = sum(math.comb(n, i) for i in range(0, k + 1)) / 2 ** n
    return min(1.0, 2 * min(upper, lower))


class CompareKappaTests(unittest.TestCase):
    def test_identical_implementations_agree_exactly(self):
        pairs = [(["W", "N1", "N2", "N2"], ["W", "N2", "N2", "N2"]), (["R", "R", "W"], ["R", "W", "W"])]
        out = compare_kappa(pairs, cohen_kappa)
        self.assertEqual(out["pairs"], 2)
        self.assertEqual(out["max_abs_difference"], 0.0)

    def test_a_different_reference_shows_up(self):
        # Observed agreement 0.5, chance agreement 0.25, so the study's kappa is 1/3.
        out = compare_kappa([(["W", "N1"], ["W", "N2"])], lambda a, b: 0.5)
        self.assertAlmostEqual(out["max_abs_difference"], 0.5 - 1 / 3)


class CompareSignTestTests(unittest.TestCase):
    def test_sign_tests_match_an_exact_binomial_reference(self):
        units = {"nineteen_of_twenty": [1.0] * 19 + [-1.0], "all_fifteen": [0.5] * 15, "with_zero": [1.0, 0.0, -2.0]}
        out = compare_sign_tests(units, lambda k, n: exact_binomial_two_sided(k, n))
        self.assertEqual(out["max_abs_difference"], 0.0)
        self.assertEqual(out["tests"]["nineteen_of_twenty"]["n"], 20)
        self.assertEqual(out["tests"]["with_zero"]["n"], 2)  # zeros are dropped, as sign_test does
        self.assertAlmostEqual(out["tests"]["nineteen_of_twenty"]["p_study"], sign_test(units["nineteen_of_twenty"]))


if __name__ == "__main__":
    unittest.main()
