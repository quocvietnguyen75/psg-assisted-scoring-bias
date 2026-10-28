"""Synthetic checks, run before the first real-data analysis."""
import random
import unittest

from d2 import consensus, epoch_labels, kappa, lights_window, measures, STAGES


class ProtocolChecks(unittest.TestCase):
    def test_kappa_hand_calculated_and_missing(self):
        # observed=.5, expected=.5 => kappa=0; unknown epoch is excluded.
        self.assertAlmostEqual(kappa(['W', 'W', 'N1', 'N1', None],
                                     ['W', 'N1', 'W', 'N1', 'W']), 0)
        self.assertAlmostEqual(kappa(list(STAGES), list(STAGES)), 1)
        with self.assertRaises(ValueError):
            kappa([None], ['W'])
        with self.assertRaises(ValueError):
            kappa(['W'], ['W'])

    def test_kappa_against_sklearn(self):
        from sklearn.metrics import cohen_kappa_score
        rng = random.Random(17)
        for _ in range(50):
            a = [rng.choice((*STAGES, None)) for _ in range(100)]
            b = [rng.choice((*STAGES, None)) for _ in range(100)]
            pairs = [(x, y) for x, y in zip(a, b) if x is not None and y is not None]
            expected = cohen_kappa_score([x for x, _ in pairs], [y for _, y in pairs], labels=list(STAGES))
            self.assertAlmostEqual(kappa(a, b), expected, places=13)

    def test_majority_not_plurality_or_missing_denominator(self):
        self.assertEqual(consensus([['N1']] * 7 + [['N2']] * 5, 7), ['N1'])
        self.assertEqual(consensus([['N1']] * 6 + [['N2']] * 6, 7), [None])
        self.assertEqual(consensus([['N1']] * 6 + [[None]] * 6, 7), [None])
        self.assertEqual(consensus([['N1']] * 6 + [['N2']] * 5, 6), ['N1'])

    def test_intervals_midpoints_and_context(self):
        rows = [(0, 30, 'Sleep stage W'), (30, 60, 'Sleep stage N2'),
                (90, 30, 'Sleep stage ?'), (0, 120, 'EEG arousal'),
                (15, 0, 'Lights off'), (105, 0, 'Lights on')]
        self.assertEqual(lights_window(rows), (15, 105))
        epochs = [i for i in range(4) if 15 <= i * 30 + 15 < 105]
        self.assertEqual(epoch_labels(rows, epochs), ['W', 'N2', 'N2'])
        self.assertEqual(epoch_labels(rows, [3, 4]), [None, None])
        with self.assertRaises(ValueError):
            epoch_labels([(0, 60, 'Sleep stage W'), (30, 30, 'Sleep stage N1')], [0, 1])

    def test_measures_known_fixture(self):
        # Manual panel: W,W,N1,N1. Assisted panel and auto: W,N1,N1,N1.
        # kappa(manual,auto)=.5; kappa(auto,assisted consensus)=1.
        manual = [['W', 'W', 'N1', 'N1'] for _ in range(12)]
        auto = ['W', 'N1', 'N1', 'N1']
        stats, _, _, _ = measures(auto, manual, [auto[:] for _ in range(12)])
        for key, value in {'M1': .5, 'delta_auto': .5, 'delta_human': -.5, 'DiD': 1}.items():
            self.assertAlmostEqual(stats[key], value)


if __name__ == '__main__':
    unittest.main()
