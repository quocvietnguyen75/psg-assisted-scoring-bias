"""Synthetic tests for the GSSC runner of amendment 005, part C5 (careport.psg_assist_bias_gssc)."""

import unittest

from careport.psg_assist_bias_gssc import gssc_stage_names


class StageNameTests(unittest.TestCase):
    def test_gssc_codes_map_to_the_study_labels(self):
        self.assertEqual(gssc_stage_names([0, 1, 2, 3, 4]), ["W", "N1", "N2", "N3", "R"])

    def test_unknown_codes_are_unscored(self):
        self.assertEqual(gssc_stage_names([5, -1, 2]), [None, None, "N2"])

    def test_numpy_like_integers_are_accepted(self):
        class Code(int):
            pass
        self.assertEqual(gssc_stage_names([Code(3)]), ["N3"])


if __name__ == "__main__":
    unittest.main()
