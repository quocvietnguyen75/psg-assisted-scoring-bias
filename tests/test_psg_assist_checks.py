"""Synthetic tests for amendment 005 of the assisted-scoring bias study (careport.psg_assist_checks)."""

import itertools
import json
import random
import tempfile
import unittest
from pathlib import Path

from careport.psg_assist_bias import AnalysisError, run_m5, stager_labels
from careport.psg_assist_checks import (
    block_audit_precision,
    drop_short,
    epoch_blocks,
    event_rejection_lift,
    m2_event_min_duration,
    movement_toward,
    overlaps,
    rejected_label_lift,
    run_checks,
)
from test_psg_assist_bias import synthetic_config, synthetic_tree

CONFIG_005 = Path(__file__).resolve().parents[1] / "config" / "preanalysis" / "psg_assist_bias_005_2026-10-12.json"
CHANNELS = ["EEG C4-M1", "EOG E1-M2", "EMG chin"]
STAGER = lambda path, eeg, eog, emg: ["W", "N1", "N2", "N3", "N3", "R", "N1", "W"]


def _labels(values):
    return {k: v for k, v in enumerate(values)}


class RejectedLabelLiftTests(unittest.TestCase):
    def test_selects_on_the_other_scorers_only(self):
        auto = _labels(["A", "A", "A"])
        # Epoch 0: all 11 others reject A. Epoch 1: 8 others reject A. Epoch 2: all others accept A.
        others = [_labels(["B", "B" if i < 8 else "A", "A"]) for i in range(11)]
        scored_manual = _labels(["B", "B", "A"])
        scored_semi = _labels(["A", "A", "A"])
        manual = [scored_manual] + others
        semi = [scored_semi] + [_labels(["B", "B", "A"])] * 11
        n, lift = rejected_label_lift(auto, manual, semi, min_other_rejecting=9)[0]
        self.assertEqual(n, 1)  # only epoch 0 qualifies for the scored expert
        self.assertAlmostEqual(lift, 1.0)

    def test_skips_epochs_the_scored_expert_left_unscored(self):
        auto = _labels(["A", "A"])
        manual = [_labels([None, "B"])] + [_labels(["B", "B"])] * 11
        semi = [_labels(["A", "A"])] + [_labels(["B", "B"])] * 11
        n, lift = rejected_label_lift(auto, manual, semi, min_other_rejecting=9)[0]
        self.assertEqual(n, 1)
        self.assertAlmostEqual(lift, 1.0)

    def test_no_qualifying_epoch_gives_none(self):
        auto = _labels(["A"])
        manual = [_labels(["A"])] * 12
        semi = [_labels(["A"])] * 12
        self.assertEqual(rejected_label_lift(auto, manual, semi, 9)[0], (0, None))

    def test_exchangeable_sessions_give_no_lift_but_self_selection_does(self):
        # Without anchoring, each scorer's two sessions are independent draws of the same distribution.
        rng = random.Random(7)
        n_epochs, n_sc = 3000, 12
        auto = {k: "A" for k in range(n_epochs)}
        p_accept = [rng.choice([0.1, 0.3]) for _ in range(n_epochs)]
        draw = lambda: [{k: ("A" if rng.random() < p_accept[k] else "B") for k in range(n_epochs)} for _ in range(n_sc)]
        manual, semi = draw(), draw()
        loo = [lift for _, lift in rejected_label_lift(auto, manual, semi, min_other_rejecting=9)]
        self.assertLess(abs(sum(loo) / len(loo)), 0.02)
        # R4-style selection that counts the scored expert's own manual label is biased upward.
        self_sel = []
        for s in range(n_sc):
            keys = [k for k in range(n_epochs) if sum(m[k] != "A" for m in manual) >= 10]
            self_sel.append(sum((semi[s][k] == "A") - (manual[s][k] == "A") for k in keys) / len(keys))
        self.assertGreater(sum(self_sel) / n_sc, 0.03)


class EventRejectionLiftTests(unittest.TestCase):
    def test_overlap_requires_positive_intersection(self):
        events = [(0.0, 1.0), (5.0, 6.0)]
        self.assertTrue(overlaps((0.5, 0.7), events))
        self.assertFalse(overlaps((1.0, 2.0), events))  # touching is not overlapping
        self.assertTrue(overlaps((4.0, 5.5), events))
        self.assertFalse(overlaps((7.0, 8.0), events))

    def test_counts_whole_events_and_excludes_the_scored_expert(self):
        auto = [(10.0, 12.0), (20.0, 22.0)]
        # Event 1: all others reject; event 2: all others accept (overlap it).
        others = [[(20.5, 21.0)]] * 11
        manual = [[]] + others
        semi = [[(11.0, 11.5)]] + others
        n, lift = event_rejection_lift(auto, manual, semi, min_rejecting=9, include_self=False)[0]
        self.assertEqual(n, 1)
        self.assertAlmostEqual(lift, 1.0)

    def test_including_self_changes_the_qualifying_units(self):
        auto = [(10.0, 12.0)]
        # 9 of the others reject, so 10 of 12 reject when the scored expert (who rejects) is included.
        manual = [[]] + [[]] * 9 + [[(10.5, 11.0)]] * 2
        semi = [[(10.5, 11.0)]] + [[]] * 11
        self.assertEqual(event_rejection_lift(auto, manual, semi, 10, include_self=True)[0], (1, 1.0))
        self.assertEqual(event_rejection_lift(auto, manual, semi, 10, include_self=False)[0], (0, None))


class MovementTowardTests(unittest.TestCase):
    def test_difference_of_matching_shares(self):
        target = _labels(["B", "B", "B", "B"])
        manual = _labels(["A", "B", "A", None])
        semi = _labels(["B", "B", "A", "B"])
        n, move = movement_toward(target, manual, semi, keys=[0, 1, 2, 3])
        self.assertEqual(n, 3)  # epoch 3 has no manual label
        self.assertAlmostEqual(move, (2 - 1) / 3)


class BlockAuditTests(unittest.TestCase):
    def test_blocks_start_at_the_first_epoch_in_the_window(self):
        blocks = epoch_blocks([10, 11, 12, 13, 15], block_epochs=2, first_epoch=10)
        self.assertEqual(blocks, {0: [10, 11], 1: [12, 13], 2: [15]})

    def test_variance_and_unbiasedness_match_full_enumeration(self):
        # Two strata of blocks of unequal size; units are (y, s).
        strata = [
            [[(1, 1), (0, 1)], [(1, 0)], [(0, 0), (1, 1), (1, 1)]],
            [[(0, 1)], [(1, 1), (1, 0)], [(0, 0)], [(1, 1)]],
        ]
        fraction = 0.5
        out = block_audit_precision(strata, fraction)
        n_total = sum(len(b) for s in strata for b in s)
        target = sum(y for s in strata for b in s for y, _ in b) / n_total
        assisted = sum(x for s in strata for b in s for _, x in b) / n_total
        self.assertAlmostEqual(out["target"], target)
        self.assertAlmostEqual(out["d0_bias"], assisted - target)
        sizes = [max(1, round(fraction * len(s))) for s in strata]
        self.assertEqual(out["audited_blocks_per_stratum"], sizes)
        d1_values, d2_values = [], []
        for picks in itertools.product(*[itertools.combinations(range(len(s)), n) for s, n in zip(strata, sizes)]):
            d1 = d2 = 0.0
            for s, pick, n in zip(strata, picks, sizes):
                expand = len(s) / n
                d1 += expand * sum(y for j in pick for y, _ in s[j])
                d2 += expand * sum(y - x for j in pick for y, x in s[j])
            d1_values.append(d1 / n_total)
            d2_values.append(assisted + d2 / n_total)
        for values, key in ((d1_values, "d1_se"), (d2_values, "d2_se")):
            mean = sum(values) / len(values)
            var = sum((v - mean) ** 2 for v in values) / len(values)
            self.assertAlmostEqual(mean, target)
            self.assertAlmostEqual(out[key] ** 2, var)

    def test_reports_the_expected_audited_share(self):
        strata = [[[(1, 1)] * 2, [(1, 1)] * 4]]
        out = block_audit_precision(strata, 0.5)
        self.assertAlmostEqual(out["expected_share"], 0.5)


class MinimumDurationTests(unittest.TestCase):
    def test_drop_short_keeps_events_at_least_the_minimum(self):
        self.assertEqual(drop_short([(0.0, 2.9), (5.0, 8.0), (9.0, 9.5)], 3.0), [(5.0, 8.0)])

    def test_m2_ignores_consensus_fragments_shorter_than_the_rule(self):
        window, grid = (0.0, 100.0), 0.1
        auto = [(10.0, 20.0)]
        # Manual consensus: one 10-s event; assisted consensus: the same plus a 2-s fragment near the pre-fill's end.
        manual = [[(10.0, 20.0)]] * 12
        semi = [[(10.0, 20.0)]] * 12
        semi_with_fragment = [[(10.0, 20.0), (22.0, 24.0)]] * 7 + [[(10.0, 20.0)]] * 5
        base = m2_event_min_duration(auto, manual, semi, 7, 6, grid, window, 0.0)
        frag = m2_event_min_duration(auto, manual, semi_with_fragment, 7, 6, grid, window, 0.0)
        filtered = m2_event_min_duration(auto, manual, semi_with_fragment, 7, 6, grid, window, 3.0)
        self.assertAlmostEqual(base[0], 0.0)
        self.assertLess(frag[0], 0.0)  # the fragment is an unmatched consensus event
        self.assertAlmostEqual(filtered[0], 0.0)
        self.assertEqual(len(filtered[1]), 12)


class RunTests(unittest.TestCase):
    """The synthetic tree: three scorers, two recordings. Assisted scorings copy the pre-fill; on stage epochs 3 and 6
    all manual scorings reject it, and the second respiratory pre-fill event is rejected by every manual scoring."""

    def _setup(self, tmp_path: Path) -> tuple[Path, Path, Path]:
        synthetic_tree(tmp_path / "data")
        config1 = synthetic_config(tmp_path)
        run_m5(config1, tmp_path / "data", tmp_path / "m5.json", stager=STAGER,
               channel_reader=lambda path: CHANNELS, verify=False)
        labels = stager_labels(config1, tmp_path / "data", STAGER, lambda path: CHANNELS)
        (tmp_path / "labels.json").write_text(json.dumps(labels), encoding="utf-8")
        (tmp_path / "r4.json").write_text(json.dumps({"R4_error_following": {
            "Sleep_stages": {"mean": 2.0}, "Resp_events": {"mean": 2.0}}}), encoding="utf-8")
        (tmp_path / "b1.json").write_text(json.dumps({"B1_emulation": {
            "targets": {q: {"audits": {"0.05": {"d2_halfwidth": 0.0}}} for q in ("prefill", "yasa", "gap")},
            "smallest_f_D2_halfwidth_below_D0_gap_bias": 0.05}}), encoding="utf-8")
        cfg = json.loads(CONFIG_005.read_text(encoding="utf-8"))
        cfg["stager_cache_check"]["m5_report"] = str(tmp_path / "m5.json")
        cfg["c1_rejected_label_adoption"]["min_other_rejecting"] = 2
        cfg["c1_rejected_label_adoption"]["comparison_rule"]["min_rejecting_including_scored"] = 3
        cfg["c4_block_audit"]["block_epochs"] = 2
        cfg["bootstrap"]["resamples"] = 100
        cfg["r4_report"], cfg["b1_report"] = str(tmp_path / "r4.json"), str(tmp_path / "b1.json")
        config5 = tmp_path / "cfg5.json"
        config5.write_text(json.dumps(cfg), encoding="utf-8")
        return config5, config1, tmp_path / "labels.json"

    def test_run_checks_on_synthetic_tree(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config5, config1, labels = self._setup(tmp_path)
            report = run_checks(config5, config1, tmp_path / "data", labels, tmp_path / "out.json", verify=False)
            self.assertTrue(report["stager_cache_check"]["passed"])
            c1 = report["C1_rejected_label_adoption"]
            self.assertAlmostEqual(c1["tasks"]["Sleep_stages"]["loo_rule"]["mean"], 1.0)
            self.assertEqual(c1["tasks"]["Sleep_stages"]["loo_rule"]["scorer_unit_pairs"], 12)  # 2 epochs x 3 x 2
            self.assertAlmostEqual(c1["tasks"]["Resp_events"]["loo_rule"]["mean"], 1.0)
            self.assertAlmostEqual(c1["tasks"]["Resp_events"]["r4_rule_event_level"]["mean"], 1.0)
            self.assertEqual(c1["sign_test"]["n_units"], 4)
            yasa = report["C2_C5_independent_stagers"]["yasa"]
            self.assertAlmostEqual(yasa["toward_stager"]["mean"], -1.0)  # the experts left the stager's labels
            self.assertAlmostEqual(yasa["toward_prefill"]["mean"], 1.0)
            self.assertNotIn("gssc", report["C2_C5_independent_stagers"])
            self.assertIsNone(report["predictions"]["C5"]["supported"])
            self.assertEqual(len(report["C3_common_support"]["by_recording"]), 2)
            self.assertEqual(sorted(report["C4_block_audit"]["targets"]), ["gap", "prefill", "yasa"])
            self.assertIn("Resp_events", report["C6_event_min_duration"]["tasks"])
            self.assertTrue(report["text_rules"]["C1_keep_rejected_label_argument"] is False)  # p >= 0.05 with 4 units
            self.assertEqual(json.loads((tmp_path / "out.json").read_text(encoding="utf-8")), report)

    def test_second_stager_is_reported_when_supplied(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config5, config1, labels = self._setup(tmp_path)
            report = run_checks(config5, config1, tmp_path / "data", labels, tmp_path / "out.json",
                                gssc_labels_path=labels, verify=False)
            self.assertIn("gssc", report["C2_C5_independent_stagers"])
            self.assertIsNotNone(report["predictions"]["C5"]["supported"])

    def test_labels_that_do_not_reproduce_m5_stop_the_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config5, config1, labels = self._setup(tmp_path)
            data = json.loads(labels.read_text(encoding="utf-8"))
            data["SN1"]["1"] = "W"
            labels.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(AnalysisError):
                run_checks(config5, config1, tmp_path / "data", labels, tmp_path / "out.json", verify=False)


if __name__ == "__main__":
    unittest.main()
