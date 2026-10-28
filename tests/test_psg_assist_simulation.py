import csv
import json
import math
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from careport.psg_assist_bias import AnalysisError
from careport.psg_assist_simulation import (
    Model,
    calibrate,
    compare_references,
    difficulty_nodes,
    logistic,
    model_targets,
    nelder_mead,
    poisson_binomial,
    run_simulation,
    sequence_targets,
    simulate,
    threshold,
)
from test_psg_assist_bias import synthetic_config, synthetic_tree

CONFIG_003 = Path(__file__).resolve().parents[1] / "config" / "preanalysis" / "psg_assist_bias_003_2026-09-29.json"
BINS = [[12, 12], [10, 11], [8, 9], [0, 7]]
MODEL = Model(clear=0.4, mean=-1.5, sd=1.2, prefill=0.5, alpha=0.35, nodes=120)


class BuildingBlockTests(unittest.TestCase):
    def test_poisson_binomial(self) -> None:
        self.assertEqual(poisson_binomial([0.5, 0.5]), [0.25, 0.5, 0.25])
        for k, v in enumerate(poisson_binomial([0.3] * 4)):
            self.assertAlmostEqual(v, math.comb(4, k) * 0.3 ** k * 0.7 ** (4 - k))
        self.assertAlmostEqual(sum(poisson_binomial([0.1, 0.9, 0.4])), 1.0)

    def test_thresholds(self) -> None:
        self.assertEqual([threshold(n, "majority") for n in (1, 3, 11, 12, 25)], [1, 2, 6, 7, 13])
        self.assertEqual([threshold(n, "supermajority") for n in (1, 3, 5, 11, 12)], [1, 3, 4, 9, 9])
        with self.assertRaises(AnalysisError):
            threshold(3, "plurality")

    def test_logistic_is_stable(self) -> None:
        self.assertAlmostEqual(logistic(0.0), 0.5)
        self.assertEqual(logistic(-1000.0), 0.0)
        self.assertEqual(logistic(1000.0), 1.0)

    def test_nelder_mead_finds_quadratic_minimum(self) -> None:
        x, value = nelder_mead(lambda v: (v[0] - 1) ** 2 + (v[1] + 2) ** 2 + 3, [0.0, 0.0])
        self.assertAlmostEqual(x[0], 1.0, places=4)
        self.assertAlmostEqual(x[1], -2.0, places=4)
        self.assertAlmostEqual(value, 3.0, places=8)


class DifficultyConventionTests(unittest.TestCase):
    """Note 1 of amendment 003: experts are right more often than wrong on every epoch."""

    def test_difficulty_is_folded(self) -> None:
        model = Model(clear=0.1, mean=0.0, sd=3.0, nodes=50)
        nodes = difficulty_nodes(model)
        self.assertAlmostEqual(sum(w for w, _ in nodes), 1.0)
        self.assertTrue(all(b is None or b <= 0 for _, b in nodes))
        auto, manual, _, _ = simulate(model, 20000, 3, seed=3)
        expected = sum(w * (1.0 if b is None else logistic(-b)) for w, b in nodes)
        observed = sum(label == "T" for seq in manual for label in seq) / (3 * 20000)
        self.assertAlmostEqual(observed, expected, delta=0.01)
        self.assertGreater(observed, 0.75)

    def test_calibration_when_experts_follow_prefill_closely(self) -> None:
        targets = {"C1": {"12-12": 0.51, "10-11": 0.25, "8-9": 0.135, "0-7": 0.105}, "C2": 0.82, "C3": 0.84,
                   "C4": 0.05}
        cfg = json.loads(CONFIG_003.read_text(encoding="utf-8"))
        cfg["difficulty_nodes"] = 120
        model, _ = calibrate(targets, 12, BINS, cfg)
        fitted = model_targets(model, 12, 7, 6, 10, BINS)
        self.assertAlmostEqual(fitted["C3"], 0.84, places=6)
        self.assertAlmostEqual(model.alpha, 0.05 / 0.16)
        self.assertTrue(all(b is None or b <= 0 for _, b in difficulty_nodes(model)))


class ReferenceTests(unittest.TestCase):
    def test_no_anchoring_makes_assisted_equal_manual(self) -> None:
        out = compare_references(replace(MODEL, alpha=0.0), 5, "majority")
        for key in ("included", "reference_accuracy", "measured_a", "measured_b", "bias_a", "handicap"):
            self.assertAlmostEqual(out["assisted"][key], out["manual"][key])
        self.assertAlmostEqual(out["signatures"]["M1"], 0.0)
        self.assertAlmostEqual(out["signatures"]["delta_auto"], 0.0)
        self.assertAlmostEqual(out["signatures"]["delta_human"], 0.0)

    def test_full_anchoring_copies_prefill(self) -> None:
        out = compare_references(replace(MODEL, alpha=1.0), 3, "majority")
        self.assertAlmostEqual(out["assisted"]["measured_a"], 1.0)
        self.assertGreater(out["signatures"]["delta_auto"], 0)

    def test_clear_epochs_are_scored_perfectly(self) -> None:
        out = compare_references(replace(MODEL, clear=1.0), 3, "supermajority")
        for ref in ("manual", "assisted"):
            self.assertAlmostEqual(out[ref]["measured_a"], 1.0)
            self.assertAlmostEqual(out[ref]["bias_a"], 0.0)
            self.assertAlmostEqual(out[ref]["included"], 1.0)

    def test_identical_algorithms_break_even_at_zero(self) -> None:
        out = compare_references(replace(MODEL, prefill=0.0, alpha=0.0), 5, "majority")
        self.assertAlmostEqual(out["manual"]["breakeven"], 0.0, places=6)
        self.assertAlmostEqual(out["manual"]["handicap"], 0.0, places=9)

    def test_single_assisted_scorer_shifts_comparison_toward_prefill(self) -> None:
        for alpha in (0.2, 0.6):
            out = compare_references(replace(MODEL, alpha=alpha), 1, "majority")
            self.assertGreater(out["assisted"]["handicap"], out["manual"]["handicap"])
            self.assertIsNone(out["signatures"]["delta_human"])


class TargetTests(unittest.TestCase):
    def test_m1_identity_holds_with_heterogeneity(self) -> None:
        model = replace(MODEL, spread=0.5, consistency=0.5)
        t = model_targets(model, 12, 7, 6, 10, BINS)
        self.assertAlmostEqual(t["C4"], model.alpha * (1 - t["C3"]))
        self.assertAlmostEqual(sum(t["C1"].values()), 1.0)
        alphas = tuple(0.05 * j for j in range(12))
        t = model_targets(replace(MODEL, alphas=alphas), 12, 7, 6, 10, BINS)
        for al, c3, c4 in zip(alphas, t["C3_by_scorer"], t["C4_by_scorer"]):
            self.assertAlmostEqual(c4, al * (1 - c3))

    def test_analytic_targets_match_simulated_estimators(self) -> None:
        model = Model(clear=0.4, mean=-1.5, sd=1.2, prefill=0.5, alpha=0.35, spread=0.5, consistency=0.5,
                      idiosyncratic=0.02, nodes=200)
        analytic = model_targets(model, 12, 7, 6, 10, BINS)
        auto, manual, semi, indep = simulate(model, 50000, 12, seed=7)
        mc = sequence_targets(auto, manual, semi, 7, 6, 10, BINS, independent=indep)
        for key in ("C2", "C3", "C4", "V1", "V2", "V3", "V6", "V7", "V8", "V9", "V10"):
            self.assertAlmostEqual(mc[key], analytic[key], delta=0.03, msg=key)
        for group in ("C1", "V4", "V5"):
            for k, v in analytic[group].items():
                self.assertAlmostEqual(mc[group][k], v, delta=0.03, msg=f"{group}:{k}")
        self.assertGreater(analytic["V1"], 0)
        self.assertLess(analytic["V2"], 0)

    def test_calibration_reproduces_targets(self) -> None:
        truth = Model(clear=0.45, mean=-1.8, sd=1.3, prefill=0.7, alpha=0.3, nodes=120)
        t = model_targets(truth, 12, 7, 6, 10, BINS)
        cfg = json.loads(CONFIG_003.read_text(encoding="utf-8"))
        cfg["difficulty_nodes"] = 120
        model, info = calibrate(t, 12, BINS, cfg)
        fitted = model_targets(model, 12, 7, 6, 10, BINS)
        for k in t["C1"]:
            self.assertAlmostEqual(fitted["C1"][k], t["C1"][k], delta=2e-3)
        self.assertAlmostEqual(fitted["C2"], t["C2"], delta=2e-3)
        self.assertAlmostEqual(fitted["C3"], t["C3"], places=6)
        self.assertAlmostEqual(model.alpha, truth.alpha, places=6)
        self.assertIn("loss", info)


class RunTests(unittest.TestCase):
    def _config(self, tmp_path: Path, tolerance: float) -> Path:
        cfg = json.loads(CONFIG_003.read_text(encoding="utf-8"))
        cfg.update(consensus={"full": 2, "leave_one_out": 2}, strong_consensus=3,
                   level_bins=[[3, 3], [2, 2], [0, 1]], difficulty_nodes=40)
        cfg["grid"] = {"alpha": [0.0, 0.5], "prefill_offset": [-1.0, 3.0], "scorers": [1, 3], "rules": ["majority"]}
        cfg["monte_carlo_check"] = {"epochs": 3000, "seed": 1, "tolerance": tolerance}
        cfg["sensitivity"] = {"S2_consistency": {"consistency": 0.5}}
        path = tmp_path / "cfg3.json"
        path.write_text(json.dumps(cfg), encoding="utf-8")
        return path

    def test_run_simulation_on_synthetic_tree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            synthetic_tree(tmp_path / "data")
            report = run_simulation(self._config(tmp_path, 1.0), synthetic_config(tmp_path), tmp_path / "data",
                                    tmp_path / "out", verify=False)
            for key in ("empirical_targets", "calibration", "validation", "monte_carlo_check", "calibrated_point",
                        "identifiability", "sensitivity", "predictions"):
                self.assertIn(key, report)
            self.assertTrue(report["monte_carlo_check"]["passed"])
            self.assertEqual(sorted(report["predictions"]), ["P1", "P2", "P3", "P4", "P5"])
            self.assertIn("S2_consistency", report["sensitivity"])
            with open(tmp_path / "out" / "grid.csv", newline="", encoding="utf-8") as fh:
                self.assertEqual(len(list(csv.DictReader(fh))), 3 * 3 * 2)
            saved = json.loads((tmp_path / "out" / "simulation.json").read_text(encoding="utf-8"))
            self.assertEqual(saved, report)

    def test_failed_monte_carlo_check_stops_the_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            synthetic_tree(tmp_path / "data")
            with self.assertRaises(AnalysisError):
                run_simulation(self._config(tmp_path, 0.0), synthetic_config(tmp_path), tmp_path / "data",
                               tmp_path / "out", verify=False)


if __name__ == "__main__":
    unittest.main()
