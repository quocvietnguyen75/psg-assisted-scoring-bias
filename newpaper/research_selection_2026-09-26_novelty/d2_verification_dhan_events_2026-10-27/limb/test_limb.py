import sys
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from event_m1 import TASKS, events, match_events, m1

class TestLimb(unittest.TestCase):
    def test_task_labels_and_clipping(self):
        labels = TASKS['limb'][2]
        rows = [(-2, 5, label) for label in labels]
        rows += [(1, 2, 'Sleep stage N2'), (1, 2, 'RERA'),
                 (10, 2, next(iter(labels))), (-5, 2, next(iter(labels)))]
        self.assertEqual(events(rows, labels, (0, 10)), [(0, 3)] * len(labels))

    def test_empty_and_touching(self):
        self.assertEqual(match_events([], [])['F1'], 1)
        self.assertEqual(match_events([], [(0, 1)])['F1'], 0)
        self.assertEqual(match_events([(0, 1)], [(1, 2)])['F1'], 0)

    def test_greedy_largest_not_maximum_cardinality(self):
        # Largest edge blocks two smaller matches; protocol specifies greedy.
        self.assertEqual(match_events([(0, 10), (9, 11)], [(0, 9.5), (-1, 1)])['matched'], 1)
        self.assertAlmostEqual(match_events([(0, 2), (5, 7)], [(1, 3)])['F1'], 2/3)

    def test_tie_is_recorded(self):
        result = match_events([(0, 2)], [(0, 1), (1, 2)])
        self.assertEqual(result['matched'], 1)
        self.assertEqual(result['tie_conflicts'], 1)

    def test_m1_known_answer_and_negative(self):
        auto = [(0, 2), (5, 7)]
        value, cells = m1(auto, [[(0, 2)]] * 12, [auto] * 12)
        self.assertAlmostEqual(value, 1/3)
        self.assertEqual(len(cells), 12)
        self.assertAlmostEqual(m1(auto, [auto]*12, [[(0, 2)]]*12)[0], -1/3)
        self.assertEqual(m1([], [[]]*12, [[]]*12)[0], 0)

    def test_invalid_duration_and_scorers(self):
        with self.assertRaises(ValueError):
            events([(0, 0, next(iter(TASKS['limb'][2])))], TASKS['limb'][2], (0, 10))
        with self.assertRaises(ValueError):
            m1([], [[]], [[]])

if __name__ == '__main__':
    unittest.main()
