import itertools
import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from careport.psg_assist_bias import AnalysisError, run_m5, stager_labels
from careport.psg_assist_remedy import (
    audit_precision,
    competitor_ability,
    design_moments,
    joint_counts,
    ranking_probabilities,
    run_remedy,
    side_taking,
)
from careport.psg_assist_simulation import Model, poisson_binomial, simulate
from test_psg_assist_bias import synthetic_config, synthetic_tree

CONFIG_004 = Path(__file__).resolve().parents[1] / "config" / "preanalysis" / "psg_assist_bias_004_2026-09-29.json"
CHANNELS = ["EEG C4-M1", "EOG E1-M2", "EMG chin"]
STAGER = lambda path, eeg, eog, emg: ["W", "N1", "N2", "N3", "N3", "R", "N1", "W"]


class StagerCacheTests(unittest.TestCase):
    def test_stager_labels_follow_the_m5_epoch_rule(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            synthetic_tree(tmp_path / "data")
            labels = stager_labels(synthetic_config(tmp_path), tmp_path / "data", STAGER, lambda path: CHANNELS)
            self.assertEqual(sorted(labels), ["SN1", "SN2"])
            self.assertEqual(labels["SN1"], {i: x for i, x in enumerate(STAGER(None, "", "", ""))})


class SideTakingTests(unittest.TestCase):
    def test_changed_units_and_shares(self) -> None:
        auto = ["a", "a", "b", "b", "c", "a"]
        manual = ["a", "b", "b", "a", None, "a"]
        assisted = ["a", "a", "c", "b", "c", None]
        out = side_taking(auto, manual, assisted)
        self.assertEqual(out["n_changed"], 3)
        self.assertAlmostEqual(out["assisted_equals_prefill"], 2 / 3)
        self.assertAlmostEqual(out["manual_equals_prefill"], 1 / 3)
        self.assertAlmostEqual(out["difference"], 1 / 3)

    def test_binary_units(self) -> None:
        out = side_taking([True, False, True, False], [False, True, True, False], [True, False, True, True])
        self.assertEqual(out["n_changed"], 3)
        self.assertAlmostEqual(out["assisted_equals_prefill"] + out["manual_equals_prefill"], 1.0)
        self.assertEqual(side_taking([True], [True], [True])["n_changed"], 0)


class AuditDesignTests(unittest.TestCase):
    STRATA = [[(1, 1), (1, 0), (0, 0), (1, 1), (0, 1)], [(1, 1), (0, 0), (1, 1), (1, 0)]]

    def test_standard_errors_match_full_enumeration(self) -> None:
        fraction = 0.5
        out = audit_precision(self.STRATA, fraction)
        sizes = out["audited_per_stratum"]
        total = sum(len(s) for s in self.STRATA)
        weights = [len(s) / total for s in self.STRATA]
        target = sum(y for s in self.STRATA for y, _ in s) / total
        assisted = sum(x for s in self.STRATA for _, x in s) / total
        d1, d2 = [], []
        for picks in itertools.product(*[itertools.combinations(range(len(s)), k) for s, k in zip(self.STRATA, sizes)]):
            m1 = sum(w * sum(s[i][0] for i in p) / len(p) for w, s, p in zip(weights, self.STRATA, picks))
            m2 = assisted + sum(w * sum(s[i][0] - s[i][1] for i in p) / len(p) for w, s, p in zip(weights, self.STRATA, picks))
            d1.append(m1)
            d2.append(m2)
        for vals, key in ((d1, "d1_se"), (d2, "d2_se")):
            mean = sum(vals) / len(vals)
            self.assertAlmostEqual(mean, target)
            self.assertAlmostEqual((sum((v - mean) ** 2 for v in vals) / len(vals)) ** 0.5, out[key])
        self.assertAlmostEqual(out["target"], target)
        self.assertAlmostEqual(out["d0_bias"], assisted - target)


class SimulationDesignTests(unittest.TestCase):
    MODEL = Model(clear=0.2, mean=-0.5, sd=2.0, prefill=0.3, alpha=0.3, nodes=150)

    def test_joint_counts_factorise_without_consistency(self) -> None:
        pm, ps = [0.9, 0.6, 0.7], [0.8, 0.5, 0.95]
        pairs = [[[a * b, a * (1 - b)], [(1 - a) * b, (1 - a) * (1 - b)]] for a, b in zip(pm, ps)]
        dist = joint_counts(pairs)
        dm, ds = poisson_binomial(pm), poisson_binomial(ps)
        for i in range(4):
            for j in range(4):
                self.assertAlmostEqual(dist[i][j], dm[i] * ds[j])

    def test_competitor_ability_gives_requested_advantage(self) -> None:
        for advantage in (0.0, 0.02):
            ability = competitor_ability(self.MODEL, advantage, (-8.0, 12.0))
            mom = design_moments(self.MODEL, 12, 7, 9, [ability])[0]
            self.assertAlmostEqual(mom["true_advantage"], advantage, places=6)

    def test_design_moments_match_monte_carlo(self) -> None:
        model = replace(self.MODEL, consistency=0.5)
        mom = design_moments(model, 12, 7, 9, [0.8])[0]
        auto, manual, semi, indep = simulate(replace(model, independent=0.8), 40000, 12, seed=4)

        def cons(seqs, m, i):
            t = sum(s[i] == "T" for s in seqs)
            return "T" if t >= m else "C" if len(seqs) - t >= m else None

        rows = []
        for i in range(len(auto)):
            rm, rs, r9 = cons(manual, 7, i), cons(semi, 7, i), cons(semi, 9, i)
            if rm is None:
                continue
            y = (indep[i] == rm) - (auto[i] == rm)
            s = None if rs is None else (indep[i] == rs) - (auto[i] == rs)
            s9 = None if r9 is None else (indep[i] == r9) - (auto[i] == r9)
            rows.append((y, s, s9))
        n = len(rows)
        mean = lambda v: sum(v) / len(v)
        var = lambda v: mean([x * x for x in v]) - mean(v) ** 2
        gap = mom["gap"]
        self.assertAlmostEqual(n / len(auto), mom["population_share"], delta=0.01)
        self.assertAlmostEqual(mean([r[0] for r in rows]), gap["mean_unassisted"], delta=0.01)
        self.assertAlmostEqual(var([r[0] for r in rows]), gap["var_unassisted"], delta=0.01)
        self.assertAlmostEqual(var([r[0] - (r[1] or 0) for r in rows]), gap["var_difference"], delta=0.01)
        assisted = [r[1] for r in rows if r[1] is not None]
        self.assertAlmostEqual(len(assisted) / n, gap["assisted_share"], delta=0.01)
        self.assertAlmostEqual(mean(assisted), gap["mean_assisted"], delta=0.01)
        self.assertAlmostEqual(var(assisted), gap["var_assisted"], delta=0.01)
        sup = [r[2] for r in rows if r[2] is not None]
        self.assertAlmostEqual(len(sup) / n, gap["supermajority_share"], delta=0.01)
        self.assertAlmostEqual(mean(sup), gap["mean_supermajority"], delta=0.01)

    def test_unbiased_designs_do_not_prefer_an_identical_competitor(self) -> None:
        mom = design_moments(self.MODEL, 12, 7, 9, [self.MODEL.prefill])[0]
        probs = ranking_probabilities(mom["gap"], 5000, [0.1])
        self.assertAlmostEqual(probs["D1"][0.1], 0.5, places=6)
        self.assertAlmostEqual(probs["D2"][0.1], 0.5, places=6)
        self.assertLess(probs["D0"], 0.5)


class RunTests(unittest.TestCase):
    def _setup(self, tmp_path: Path) -> tuple[Path, Path, Path]:
        synthetic_tree(tmp_path / "data")
        config1 = synthetic_config(tmp_path)
        run_m5(config1, tmp_path / "data", tmp_path / "m5.json", stager=STAGER,
               channel_reader=lambda path: CHANNELS, verify=False)
        labels = stager_labels(config1, tmp_path / "data", STAGER, lambda path: CHANNELS)
        (tmp_path / "labels.json").write_text(json.dumps(labels), encoding="utf-8")
        (tmp_path / "cal.json").write_text(json.dumps({"calibration": {"model": {
            "clear": 0.3, "mean": -0.5, "sd": 2.0, "prefill": 0.2, "alpha": 0.3, "spread": 0.0, "consistency": 0.0,
            "idiosyncratic": 0.0, "independent": 0.0, "nodes": 60, "alphas": None}}}), encoding="utf-8")
        cfg = json.loads(CONFIG_004.read_text(encoding="utf-8"))
        cfg["stager_cache_check"]["m5_report"] = str(tmp_path / "m5.json")
        cfg["supermajority"] = 3
        cfg["bootstrap"]["resamples"] = 100
        cfg["simulation"].update(calibration_report=str(tmp_path / "cal.json"), scorers=5, majority=3,
                                 supermajority=4, advantages=[0.0, 0.02])
        config4 = tmp_path / "cfg4.json"
        config4.write_text(json.dumps(cfg), encoding="utf-8")
        return config4, config1, tmp_path / "labels.json"

    def test_run_remedy_on_synthetic_tree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config4, config1, labels = self._setup(tmp_path)
            report = run_remedy(config4, config1, tmp_path / "data", labels, tmp_path / "out.json", verify=False)
            self.assertTrue(report["stager_cache_check"]["passed"])
            for key in ("A1_common_support", "A2_side_taking", "A3_closeness", "B1_emulation", "B2_simulation",
                        "predictions"):
                self.assertIn(key, report)
            self.assertEqual(sorted(report["A2_side_taking"]["tasks"]), ["Resp_events", "Sleep_stages"])
            self.assertEqual(report["A2_side_taking"]["sign_test"]["n_units"], 4)
            self.assertEqual(sorted(report["B1_emulation"]["targets"]), ["gap", "prefill", "yasa"])
            self.assertEqual(json.loads((tmp_path / "out.json").read_text(encoding="utf-8")), report)

    def test_cache_that_does_not_reproduce_m5_stops_the_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config4, config1, labels = self._setup(tmp_path)
            data = json.loads(labels.read_text(encoding="utf-8"))
            data["SN1"]["1"] = "W"
            labels.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(AnalysisError):
                run_remedy(config4, config1, tmp_path / "data", labels, tmp_path / "out.json", verify=False)


if __name__ == "__main__":
    unittest.main()
