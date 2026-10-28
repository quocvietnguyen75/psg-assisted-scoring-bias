import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from careport.psg_assist_bias import (
    AnalysisError,
    Annotation,
    choose_channels,
    cohen_kappa,
    normalize_stage_labels,
    run_m5,
    consensus_events,
    consensus_stages,
    crossed_bootstrap,
    event_f1,
    events_in_window,
    lights_window,
    match_events,
    pairwise_agreement,
    parse_annotation_lines,
    run,
    sign_test,
    stage_epochs,
    verify_checksums,
)

CONFIG = Path(__file__).resolve().parents[1] / "config" / "preanalysis" / "psg_assist_bias_001_2026-09-29.json"
HEADER = "Date, Time, Recording onset, Duration, Annotation, Linked channel"


def line(onset: float, duration: float, label: str, channel: str = "") -> str:
    return f"01.01.01, 00.00.00, {onset}, {duration}, {label}, {channel}"


class ParsingTests(unittest.TestCase):
    def test_parse_rows(self) -> None:
        rows = parse_annotation_lines([HEADER, line(0, 30, "Sleep stage ?"), line(83.21, 0, "Lights off", "EMG RAT"),
                                       line(90, 30, "Sleep stage W"), line(120.5, 12.25, "Hypopnea", "Resp nasal")])
        self.assertEqual(rows[1], Annotation(83.21, 0.0, "Lights off"))
        self.assertEqual(rows[3], Annotation(120.5, 12.25, "Hypopnea"))
        self.assertEqual(len(rows), 4)

    def test_lights_window(self) -> None:
        rows = [Annotation(83.21, 0, "Lights off"), Annotation(26980.5, 0, "Lights on")]
        self.assertEqual(lights_window(rows, "Lights off", "Lights on"), (83.21, 26980.5))
        with self.assertRaises(AnalysisError):
            lights_window(rows[:1], "Lights off", "Lights on")

    def test_stage_epochs_use_midpoint_rule_and_drop_unscored(self) -> None:
        rows = [Annotation(0, 30, "Sleep stage ?"), Annotation(30, 30, "Sleep stage ?"), Annotation(60, 30, "Sleep stage W"),
                Annotation(90, 30, "Sleep stage N2"), Annotation(120, 30, "Sleep stage R"), Annotation(95, 3, "EEG arousal")]
        epochs = stage_epochs(rows, ("W", "N1", "N2", "N3", "R"), "Sleep stage ", (40.0, 140.0), 30)
        self.assertEqual(epochs, {1: None, 2: "W", 3: "N2", 4: "R"})

    def test_events_filtered_and_clipped(self) -> None:
        rows = [Annotation(10, 20, "Hypopnea"), Annotation(95, 10, "Obstructive apnea"), Annotation(200, 5, "Hypopnea"),
                Annotation(50, 5, "Limb movement")]
        self.assertEqual(events_in_window(rows, ("Hypopnea", "Obstructive apnea"), (20.0, 100.0)),
                         [(20.0, 30.0), (95.0, 100.0)])


class AgreementTests(unittest.TestCase):
    def test_kappa_known_value(self) -> None:
        self.assertAlmostEqual(cohen_kappa(["W", "W", "N2", "N2"], ["W", "N2", "N2", "N2"]), 0.5)
        self.assertAlmostEqual(cohen_kappa(["W", "N2"], ["W", "N2"]), 1.0)

    def test_greedy_one_to_one_matching(self) -> None:
        ref = [(0.0, 10.0), (20.0, 30.0)]
        pred = [(5.0, 12.0), (8.0, 25.0), (40.0, 45.0)]
        self.assertEqual(match_events(ref, pred), (2, 1, 0))
        self.assertAlmostEqual(event_f1(ref, pred), 0.8)

    def test_f1_edge_cases(self) -> None:
        self.assertEqual(event_f1([], []), 1.0)
        self.assertEqual(event_f1([(0.0, 1.0)], []), 0.0)
        self.assertEqual(event_f1([], [(0.0, 1.0)]), 0.0)

    def test_consensus_stages_needs_majority(self) -> None:
        scorings = [{0: "W", 1: "N2", 2: None}, {0: "W", 1: "N1", 2: "R"}, {0: "N1", 1: "N3", 2: "R"}]
        self.assertEqual(consensus_stages(scorings, 2), {0: "W", 2: "R"})

    def test_consensus_events_on_grid(self) -> None:
        scorings = [[(0.0, 1.0), (5.0, 6.0)], [(0.5, 1.5)], [(5.2, 6.0)]]
        result = consensus_events(scorings, 2, 0.1, (0.0, 10.0))
        self.assertEqual(len(result), 2)
        self.assertAlmostEqual(result[0][0], 0.5)
        self.assertAlmostEqual(result[0][1], 1.0)
        self.assertAlmostEqual(result[1][0], 5.2)
        self.assertAlmostEqual(result[1][1], 6.0)

    def test_pairwise_agreement(self) -> None:
        self.assertAlmostEqual(pairwise_agreement([["a", "b"], ["a", "c"], ["a", "b"]]), (3 + 1) / 6)


class InferenceTests(unittest.TestCase):
    def test_sign_test_exact(self) -> None:
        self.assertAlmostEqual(sign_test([1.0] * 20), 2 * 0.5 ** 20)
        self.assertAlmostEqual(sign_test([1.0, -1.0]), 1.0)
        self.assertAlmostEqual(sign_test([0.0, 0.0, 2.0]), 1.0)

    def test_bootstrap_of_constant_matrix(self) -> None:
        low, high = crossed_bootstrap([[0.2, 0.2], [0.2, 0.2], [0.2, 0.2]], 200, 1)
        self.assertAlmostEqual(low, 0.2)
        self.assertAlmostEqual(high, 0.2)


def write_file(path: Path, rows: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join([HEADER] + rows) + "\n", encoding="utf-8")


def synthetic_tree(root: Path) -> None:
    """Two recordings, three scorers. Semi-automatic scorings copy the pre-fill; manual ones partly differ."""
    stages_auto = ["W", "N1", "N2", "N2", "N3", "R", "N2", "W"]
    stages_manual = [["W", "N1", "N2", "N3", "N3", "R", "N1", "W"],
                     ["W", "N2", "N2", "N3", "N3", "R", "N1", "W"],
                     ["W", "N1", "N1", "N3", "N3", "R", "N1", "W"]]
    frame = [line(0, 0, "Lights off"), line(240, 0, "Lights on")]
    for rec in (1, 2):
        base = root / "Sleep_stages" / "Annotations"
        write_file(base / "auto" / f"SN{rec}_SleepStages_auto.txt",
                   frame + [line(30 * i, 30, f"Sleep stage {s}") for i, s in enumerate(stages_auto)])
        for s in (1, 2, 3):
            write_file(base / "semiauto" / f"SN{rec}_SleepStages_semiauto_scorer{s}.txt",
                       frame + [line(30 * i, 30, f"Sleep stage {x}") for i, x in enumerate(stages_auto)])
            write_file(base / "manual" / f"SN{rec}_SleepStages_manual_scorer{s}.txt",
                       frame + [line(30 * i, 30, f"Sleep stage {x}") for i, x in enumerate(stages_manual[s - 1])])
        context = [line(30 * i, 30, "Sleep stage N2") for i in range(8)]
        auto_events = [line(20, 12, "Hypopnea"), line(100, 15, "Obstructive apnea")]
        manual_events = [[line(21, 11, "Hypopnea"), line(160, 12, "Hypopnea")],
                         [line(22, 10, "Hypopnea"), line(161, 12, "Hypopnea")],
                         [line(160, 11, "Hypopnea")]]
        base = root / "Resp_events" / "Annotations"
        write_file(base / "auto" / f"SN{rec}_Respiration_auto.txt", frame + context + auto_events)
        for s in (1, 2, 3):
            write_file(base / "semiauto" / f"SN{rec}_Respiration_semiauto_scorer{s}.txt", frame + context + auto_events)
            write_file(base / "manual" / f"SN{rec}_Respiration_manual_scorer{s}.txt", frame + context + manual_events[s - 1])


def synthetic_config(tmp: Path) -> Path:
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    config["tasks"] = {k: v for k, v in config["tasks"].items() if k in ("Sleep_stages", "Resp_events")}
    config["n_scorers"] = 3
    config["consensus_majority"] = {"full": 2, "leave_one_out": 2}
    config["inference"]["bootstrap_resamples"] = 200
    config["dataset"]["expected_files"] = None
    path = tmp / "config.json"
    path.write_text(json.dumps(config), encoding="utf-8")
    return path


class RunTests(unittest.TestCase):
    def test_semiauto_copies_prefill_gives_positive_anchoring_and_inflation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            synthetic_tree(tmp_path / "data")
            report = run(synthetic_config(tmp_path), tmp_path / "data", tmp_path / "out" / "report.json", verify=False)
            for task in ("Sleep_stages", "Resp_events"):
                m1 = report["tasks"][task]["M1_anchoring"]
                self.assertGreater(m1["mean"], 0)
                self.assertEqual(len(m1["recording_means"]), 2)
                m2 = report["tasks"][task]["M2_inflation"]
                self.assertTrue(all(d > 0 for d in m2["did_by_recording"]))
            self.assertEqual(report["primary"]["M1_sign_test"]["n_units"], 4)
            self.assertIn("M4_indices", report["tasks"]["Resp_events"])
            self.assertEqual(json.loads((tmp_path / "out" / "report.json").read_text(encoding="utf-8")), report)

    def test_missing_scoring_file_stops(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            synthetic_tree(tmp_path / "data")
            (tmp_path / "data" / "Resp_events" / "Annotations" / "manual" / "SN2_Respiration_manual_scorer3.txt").unlink()
            with self.assertRaises(AnalysisError):
                run(synthetic_config(tmp_path), tmp_path / "data", tmp_path / "out.json", verify=False)


class M5Tests(unittest.TestCase):
    CHANNELS = ["EEG F4-M1", "EEG C4-M1", "EMG chin", "EOG E1-M2", "EOG E2-M2"]

    def test_choose_channels_prefers_c4_then_cz(self) -> None:
        self.assertEqual(choose_channels(self.CHANNELS), ("EEG C4-M1", "EOG E1-M2", "EMG chin"))
        no_c4 = [c for c in self.CHANNELS if c != "EEG C4-M1"] + ["EEG Cz-M1"]
        self.assertEqual(choose_channels(no_c4)[0], "EEG Cz-M1")
        with self.assertRaises(AnalysisError):
            choose_channels(["EEG C4-M1", "EMG chin"])

    def run_m5_with(self, labels: list[str]) -> dict:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            synthetic_tree(tmp_path / "data")
            return run_m5(synthetic_config(tmp_path), tmp_path / "data", tmp_path / "m5.json",
                          stager=lambda path, eeg, eog, emg: list(labels),
                          channel_reader=lambda path: self.CHANNELS, verify=False)

    def test_stager_copying_the_prefill_gains_like_the_prefill(self) -> None:
        report = self.run_m5_with(["W", "N1", "N2", "N2", "N3", "R", "N2", "W"])
        for rec in report["recordings"]:
            self.assertAlmostEqual(rec["delta_yasa"], rec["delta_auto"])
            self.assertGreater(rec["delta_yasa"], 0)
            self.assertEqual(rec["channels"], ["EEG C4-M1", "EOG E1-M2", "EMG chin"])

    def test_stager_matching_human_consensus_loses_against_assisted_reference(self) -> None:
        report = self.run_m5_with(["W", "N1", "N2", "N3", "N3", "R", "N1", "W"])
        self.assertTrue(all(rec["delta_yasa"] < 0 for rec in report["recordings"]))
        self.assertEqual(report["n_delta_yasa_positive"], 0)

    def test_ranking_rows_written_beside_m5(self) -> None:
        """--ranking: the exploratory ranking file (pre-fill and stager kappas per recording) from the same M5 pass."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            synthetic_tree(tmp_path / "data")
            report = run_m5(synthetic_config(tmp_path), tmp_path / "data", tmp_path / "m5.json",
                            stager=lambda path, eeg, eog, emg: ["W", "N1", "N2", "N2", "N3", "R", "N2", "W"],
                            channel_reader=lambda path: self.CHANNELS, verify=False,
                            ranking_path=tmp_path / "ranking.json")
            ranking = json.loads((tmp_path / "ranking.json").read_text(encoding="utf-8"))
            self.assertEqual(ranking["label"], "exploratory, not pre-specified")
            self.assertEqual([r["recording"] for r in ranking["rows"]], [r["recording"] for r in report["recordings"]])
            for row, rec in zip(ranking["rows"], report["recordings"]):
                self.assertEqual(list(row), ["recording", "prefill_vs_manual", "yasa_vs_manual",
                                             "prefill_vs_assisted", "yasa_vs_assisted"])
                self.assertAlmostEqual(row["prefill_vs_assisted"] - row["prefill_vs_manual"], rec["delta_auto"])
                self.assertEqual(row["yasa_vs_manual"], rec["kappa_stager_vs_manual_consensus"])
                self.assertEqual(row["yasa_vs_assisted"], rec["kappa_stager_vs_assisted_consensus"])
            self.assertNotIn("prefill_vs_manual", (tmp_path / "m5.json").read_text(encoding="utf-8"))

    def test_yasa_label_names_are_mapped(self) -> None:
        self.assertEqual(normalize_stage_labels(["WAKE", "N1", "N2", "N3", "REM", "ART", "UNS"]),
                         ["W", "N1", "N2", "N3", "R", None, None])


class ChecksumTests(unittest.TestCase):
    def test_verify_checksums(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.txt").write_text("hello", encoding="utf-8")
            digest = hashlib.sha256(b"hello").hexdigest()
            (root / "SHA256SUMS.txt").write_text(f"{digest} a.txt\n", encoding="utf-8")
            self.assertEqual(verify_checksums(root, "SHA256SUMS.txt", 1), 1)
            (root / "SHA256SUMS.txt").write_text(f"{digest} a.txt\n{digest} b.txt\n", encoding="utf-8")
            with self.assertRaises(AnalysisError):
                verify_checksums(root, "SHA256SUMS.txt", 2)


if __name__ == "__main__":
    unittest.main()
