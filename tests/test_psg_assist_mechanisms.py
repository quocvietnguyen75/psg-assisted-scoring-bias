import json
import math
import tempfile
import unittest
from pathlib import Path

from careport.psg_assist_bias import consensus_stages, event_f1
from careport.psg_assist_mechanisms import (
    acceptance_lift_by_stage,
    ambiguity_lift,
    consensus_plurality,
    crossed_bootstrap_nan,
    error_following,
    event_f1_iou,
    run_mechanisms,
    spearman,
    stage_percent_agreement,
)
from test_psg_assist_bias import CONFIG, synthetic_config, synthetic_tree

CONFIG_002 = Path(__file__).resolve().parents[1] / "config" / "preanalysis" / "psg_assist_bias_002_2026-09-29.json"


class ConsensusAndMetricTests(unittest.TestCase):
    def test_plurality_excludes_ties(self) -> None:
        scorings = [{0: "W", 1: "N1", 2: "R"}, {0: "W", 1: "N2", 2: "R"}, {0: "N1", 1: "N3", 2: None}]
        self.assertEqual(consensus_plurality(scorings, 0), {0: "W", 2: "R"})

    def test_percent_agreement_ignores_unscored(self) -> None:
        self.assertAlmostEqual(stage_percent_agreement({0: "W", 1: "N1", 2: None}, {0: "W", 1: "N2", 2: "R"}), 0.5)

    def test_iou_matching_is_stricter_than_overlap(self) -> None:
        ref, pred = [(0.0, 10.0)], [(9.0, 30.0)]
        self.assertEqual(event_f1(ref, pred), 1.0)
        self.assertEqual(event_f1_iou(ref, pred, 0.2), 0.0)
        self.assertEqual(event_f1_iou([(0.0, 10.0)], [(1.0, 10.0)], 0.2), 1.0)
        self.assertEqual(event_f1_iou([], [], 0.2), 1.0)


class MechanismTests(unittest.TestCase):
    def test_acceptance_lift_by_stage(self) -> None:
        auto = {0: "N1", 1: "N1", 2: "N2", 3: "W"}
        manual = {0: "N2", 1: "N1", 2: "N2", 3: None}
        semi = {0: "N1", 1: "N1", 2: "N2", 3: "W"}
        lift = acceptance_lift_by_stage(auto, manual, semi, ["W", "N1", "N2"])
        self.assertEqual(lift["N1"], (2, 0.5))
        self.assertEqual(lift["N2"], (1, 0.0))
        self.assertEqual(lift["W"], (0, None))

    def test_ambiguity_lift_bins_by_manual_agreement(self) -> None:
        auto = ["a", "a", "b"]
        manual = [["a", "b", "b"], ["a", "a", "b"], ["a", "a", "b"]]
        semi = [["a", "a", "b"], ["a", "a", "b"], ["a", "a", "b"]]
        # unit 0: manual labels a,a,a -> level 3; unit 1: b,a,a -> level 2; unit 2: b,b,b -> level 3
        result = ambiguity_lift(auto, manual, semi, [[3, 3], [0, 2]])
        self.assertEqual(result["3-3"]["n_units"], 2)
        self.assertAlmostEqual(result["3-3"]["lift"], 0.0)
        self.assertEqual(result["0-2"]["n_units"], 1)
        self.assertAlmostEqual(result["0-2"]["lift"], 1 / 3)

    def test_error_following_counts_adopted_prefill_errors(self) -> None:
        auto = ["x", "y", "y"]
        manual = [["y", "y", "y"], ["y", "y", "y"], ["y", "y", "y"]]
        semi = [["x", "y", "y"], ["y", "y", "y"], ["x", "y", "y"]]
        # unit 0: strong manual consensus y (3/3) disagrees with pre-fill x
        per_scorer, n_units = error_following(auto, manual, semi, strong=3)
        self.assertEqual(n_units, 1)
        self.assertEqual(per_scorer, [1.0, 0.0, 1.0])

    def test_spearman(self) -> None:
        self.assertAlmostEqual(spearman([1, 2, 3, 4], [10, 20, 30, 40]), 1.0)
        self.assertAlmostEqual(spearman([1, 2, 3, 4], [4, 3, 2, 1]), -1.0)

    def test_bootstrap_skips_missing_cells(self) -> None:
        low, high = crossed_bootstrap_nan([[0.2, None], [0.2, 0.2]], 300, 1)
        self.assertAlmostEqual(low, 0.2)
        self.assertAlmostEqual(high, 0.2)


class RunTests(unittest.TestCase):
    def test_run_mechanisms_on_synthetic_tree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            synthetic_tree(tmp_path / "data")
            cfg2 = json.loads(CONFIG_002.read_text(encoding="utf-8"))
            cfg2["bootstrap"]["resamples"] = 100
            cfg2["R3_bins"] = [[3, 3], [2, 2], [0, 1]]
            cfg2["R4_strong_consensus"] = 3
            cfg2["R6_variants"]["supermajority"]["consensus_majority"] = {"full": 3, "leave_one_out": 2}
            p2 = tmp_path / "cfg2.json"
            p2.write_text(json.dumps(cfg2), encoding="utf-8")
            report = run_mechanisms(p2, synthetic_config(tmp_path), tmp_path / "data", tmp_path / "out.json", verify=False)
            self.assertIn("N1", report["R1_lift_by_stage"])
            self.assertGreater(report["R1_lift_by_stage"]["N2"]["mean"], 0)
            self.assertEqual(report["R1_lift_by_stage"]["N3"]["mean"], 0)
            self.assertIn("hypopnea", report["R2_resp_types"])
            self.assertIn("Sleep_stages", report["R3_ambiguity"])
            self.assertIn("Sleep_stages", report["R4_error_following"])
            for variant in ("plurality_stages", "supermajority", "iou_0.2", "percent_agreement_stages"):
                self.assertIn(variant, report["R6_robustness"])
                self.assertEqual(report["R6_robustness"][variant]["M1_sign_test"]["n_units"], 4)
            self.assertEqual(json.loads((tmp_path / "out.json").read_text(encoding="utf-8")), report)


if __name__ == "__main__":
    unittest.main()
