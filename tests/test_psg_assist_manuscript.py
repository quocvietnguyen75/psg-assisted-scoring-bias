import re
import tempfile
import unittest
from pathlib import Path

from careport.psg_assist_manuscript import (
    TEXT_WIDTH_IN,
    _fda_values,
    build,
    build_figures,
    fmt,
    fmt_int,
    fmt_p,
    fmt_pct,
    load_reports,
    missing_value_keys,
    supplement_refs,
    used_keys,
    write_values,
)

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "newpaper" / "research_selection_2026-09-26_novelty"
MANUSCRIPT = ROOT / "newpaper" / "psg_assist_bias_manuscript" / "main.tex"


class FormattingTests(unittest.TestCase):
    def test_numbers(self) -> None:
        self.assertEqual(fmt(0.0812), "0.081")
        self.assertEqual(fmt(-0.04), "\\ensuremath{-}0.040")
        self.assertEqual(fmt(0.05, 2, signed=True), "+0.05")
        self.assertEqual(fmt(-0.0004, 3, signed=True), "0.000")
        self.assertEqual(fmt(0.0004, 3, signed=True), "0.000")
        self.assertEqual(fmt(-0.0004), "0.000")
        self.assertEqual(fmt_int(5103), "5{,}103")
        self.assertEqual(fmt_int(400000), "400{,}000")
        self.assertEqual(fmt_pct(0.9302), "93\\%")
        self.assertEqual(fmt_pct(0.0584, 1), "5.8\\%")

    def test_p_values(self) -> None:
        self.assertEqual(fmt_p(4.00543212890625e-05), "\\ensuremath{4.0\\times10^{-5}}")
        self.assertEqual(fmt_p(1.9073486328125e-06), "\\ensuremath{1.9\\times10^{-6}}")
        self.assertEqual(fmt_p(0.11531829833984375), "0.12")
        self.assertEqual(fmt_p(0.0061), "0.006")

    def test_values_file_and_key_parsing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "values.tex"
            write_values({"m1-stages-mean": "0.081", "a2-sign-p": "\\ensuremath{1.9\\times10^{-6}}"}, path)
            text = path.read_text(encoding="utf-8")
            self.assertIn("\\expandafter\\def\\csname val@m1-stages-mean\\endcsname{0.081}", text)
            with self.assertRaises(ValueError):
                write_values({"bad key": "1"}, path)
        self.assertEqual(used_keys("x \\val{m1-stages-mean} and \\val{a2-sign-p}."), {"m1-stages-mean", "a2-sign-p"})

    def test_missing_keys_cover_main_text_and_supplement(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "main.tex").write_text("\\val{a} and \\val{b}", encoding="utf-8")
            self.assertEqual(missing_value_keys(folder, {"a": "1", "b": "2"}), {})
            (folder / "supplement.tex").write_text("\\val{a} and \\val{c}", encoding="utf-8")
            self.assertEqual(missing_value_keys(folder, {"a": "1", "b": "2"}), {"supplement.tex": ["c"]})


class SupplementRefsTests(unittest.TestCase):
    def test_supplement_labels_become_links_to_the_supplement_pdf(self) -> None:
        aux = ("\\relax\n"
               "\\providecommand\\hyper@newdestlabel[2]{}\n"
               "\\newlabel{tab:s-fda}{{S9}{5}{How the 22 {\\em FDA} clearances}{table.caption.17}{}}\n"
               "\\bibcite{fda510k}{1}\n"
               "\\newlabel{tab:s-codes}{{S1}{3}{Names}{table.caption.9}{}}\n")
        lines = supplement_refs(aux).splitlines()
        self.assertTrue(lines[0].startswith("%"))
        self.assertEqual(lines[1:], [
            "\\makeatletter",
            "\\newlabel{tab:s-fda}{{S9}{5}{How the 22 {\\em FDA} clearances}{table.caption.17}{supplement.pdf}}",
            "\\newlabel{tab:s-codes}{{S1}{3}{Names}{table.caption.9}{supplement.pdf}}",
            "\\makeatother",
        ])

    def test_rejects_labels_without_hyperref_fields(self) -> None:
        with self.assertRaises(ValueError):
            supplement_refs("\\newlabel{tab:s-fda}{{S9}{5}}\n")

    def test_every_reference_in_main_text_resolves(self) -> None:
        folder = MANUSCRIPT.parent
        text = MANUSCRIPT.read_text(encoding="utf-8")
        generated = "".join(p.read_text(encoding="utf-8") for p in (folder / "generated").glob("*.tex"))
        defined = set(re.findall(r"\\label\{([^}]+)\}", text + generated))
        defined |= set(re.findall(r"\\newlabel\{([^}]+)\}",
                                  (folder / "generated" / "supplement_refs.tex").read_text(encoding="utf-8")))
        self.assertEqual(set(re.findall(r"\\ref\{([^}]+)\}", text)) - defined, set())


class FdaValueTests(unittest.TestCase):
    def test_counts_only_statements_about_any_software_among_clearances_with_performance_data(self) -> None:
        def row(k: str, perf: str, ref: str, blind: str, pre: str) -> dict[str, str]:
            return {"k_number": k, "decision_date": "2020-01-01", "clinical_performance_data": perf,
                    "reference_type": ref, "reference_scorers": "3", "blinding_to_device_output": blind,
                    "prescoring_reported": pre}

        devices = [
            row("K1", "yes", "independent_experts", "explicit", "device output only"),
            row("K2", "yes", "routine_clinical_scoring", "implied by design", "not said"),
            row("K3", "yes", "algorithm_reference", "not applicable", "not applicable"),
            row("K4", "no", "no_new_performance_data", "", "not applicable"),
            row("K5", "yes", "not_described", "not stated", "says they did not"),
            {**row("K0", "", "out_of_scope_pre2012", "", ""), "decision_date": "2000-01-01"},
        ]
        values: dict[str, str] = {}
        _fda_values(values, devices)
        self.assertEqual((values["fda-census"], values["fda-modern"], values["fda-perf"]), ("6", "5", "4"))
        self.assertEqual(values["fda-prescoring-reported"], "1")
        self.assertEqual((values["fda-blind-explicit"], values["fda-blind-implied"]), ("1", "1"))
        self.assertEqual(values["fda-unclear"], "2")


class BuildTests(unittest.TestCase):
    def test_build_from_committed_reports(self) -> None:
        reports = load_reports(REPORTS)
        with tempfile.TemporaryDirectory() as tmp:
            out = build(reports, Path(tmp))
            values = out["values"]
            self.assertEqual(values["m1-sign-pos"], "19")
            self.assertEqual(values["m2-sign-pos"], "20")
            self.assertEqual(values["m1-stages-mean"], "0.081")
            self.assertEqual(values["fda-census"], "37")
            self.assertEqual(values["fda-perf"], "22")
            self.assertEqual(values["fda-prescoring-reported"], "0")
            self.assertEqual(values["fda-blind-explicit"], "1")
            self.assertEqual(values["fda-indep-three"], "8")
            self.assertEqual((values["fda-consensus"], values["fda-notdesc"], values["fda-unclear"]), ("4", "3", "7"))
            self.assertEqual((values["fda-blind-implied"], values["fda-blind-none"]), ("5", "13"))
            self.assertEqual((values["m1-scorers-pos-min"], values["m1-scorers-pos-max"]), ("10", "12"))
            self.assertEqual(values["sim-v2-absdiff"], "0.001")
            self.assertEqual(values["sim-v5-maxdiff"], "0.004")
            self.assertEqual(values["rank-growth"], "0.115")
            self.assertEqual((values["fda-blind-object"], values["fda-blind-na"]), ("2", "1"))
            self.assertEqual((values["sim-bias-lo-r2"], values["sim-bias-hi-r2"]), ("+0.03", "+0.05"))
            # Amendment 005.
            self.assertEqual((values["c1-stages-mean"], values["c1-limb-mean"]), ("+0.169", "+0.374"))
            self.assertEqual((values["c1-sign-pos"], values["c1-sign-n"], values["c1-sign-nonzero"]), ("19", "20", "19"))
            self.assertEqual(values["c1-sign-p"], "\\ensuremath{3.8\\times10^{-6}}")
            self.assertEqual((values["c2-yasa-toward-stager"], values["c2-yasa-toward-prefill"]),
                             ("\\ensuremath{-}0.135", "+0.162"))
            self.assertEqual((values["c2-gssc-toward-stager"], values["c2-gssc-toward-prefill"]),
                             ("\\ensuremath{-}0.156", "+0.183"))
            self.assertEqual((values["c2-yasa-side-assisted-pct"], values["c2-yasa-side-manual-pct"],
                              values["c2-gssc-side-manual-pct"]), ("0\\%", "93\\%", "96\\%"))
            self.assertEqual((values["c3-auto-kappa-pos"], values["c3-auto-kappa-mean"]), ("5", "+0.054"))
            self.assertEqual((values["st-gssc-ahead-manual"], values["st-gssc-ahead-assisted"]), ("3", "0"))
            self.assertEqual((values["st-yasa-ahead-manual"], values["st-yasa-ahead-assisted"]), ("1", "0"))
            self.assertEqual((values["c4-smallest-f"], values["c4-smallest-share"], values["c4-blocks"]),
                             ("10\\%", "12\\%", "87"))
            self.assertEqual(values["c4-gap-f10-d2"], "0.045")
            self.assertEqual((values["c6-sign-pos"], values["c6-sign-p"]), ("15", "\\ensuremath{6.1\\times10^{-5}}"))
            self.assertEqual(values["d3-kappa-pairs"], "130")
            self.assertEqual((values["pred5-c1"], values["pred5-c4"]), ("supported", "not supported"))
            self.assertEqual(values["m4-resp-cat-changed"], "0")
            self.assertTrue((Path(tmp) / "generated" / "tab_s_fda.tex").is_file())
            for name in ("fig_primary.pdf", "fig_mechanism.pdf", "fig_simulation.pdf", "fig_remedy.pdf", "fig_stagers.pdf"):
                self.assertTrue((Path(tmp) / "figures" / name).stat().st_size > 1000, name)
            for name in ("tab_primary.tex", "tab_stagers.tex", "tab_validation.tex", "tab_consequences.tex",
                         "tab_remedy.tex", "tab_s_stagers.tex", "tab_s_indices.tex", "tab_s_m3.tex", "tab_s_blocks.tex"):
                self.assertTrue((Path(tmp) / "generated" / name).is_file(), name)
            self.assertEqual(missing_value_keys(MANUSCRIPT.parent, values), {})


class FigureLegibilityTests(unittest.TestCase):
    def test_figures_print_at_8_pt_or_more_at_text_width(self) -> None:
        import matplotlib.text

        figures = build_figures(load_reports(REPORTS))
        self.assertEqual(sorted(figures), ["fig_mechanism", "fig_primary", "fig_remedy", "fig_simulation", "fig_stagers"])
        for name, fig in figures.items():
            width = fig.get_size_inches()[0]
            self.assertLessEqual(width, TEXT_WIDTH_IN, name)
            scale = TEXT_WIDTH_IN / width
            fig.canvas.draw()
            for text in fig.findobj(matplotlib.text.Text):
                if text.get_visible() and text.get_text().strip():
                    self.assertGreaterEqual(text.get_fontsize() * scale, 8.0 - 1e-9, f"{name}: {text.get_text()!r}")


if __name__ == "__main__":
    unittest.main()


class FidelityAdditionsTests(unittest.TestCase):
    """Tables and values added after the fidelity check of 26 October 2026 (round-1 item R5 and amendment 003 V9, V10)."""

    def _tables_and_values(self):
        from careport.psg_assist_manuscript import collect_values, exploratory_consistency, render_tables
        reports = load_reports(REPORTS)
        expl = exploratory_consistency(reports["sim"]["calibration"]["model"])
        values = collect_values(reports, expl)
        return render_tables(reports, values), values

    def test_unit_table_lists_the_20_recording_task_units(self) -> None:
        tables, values = self._tables_and_values()
        self.assertIn("tab_s_units", tables)
        text = tables["tab_s_units"]
        starts = ("Sleep stages &", "EEG arousals &", "Respiratory events &", "Limb movements &")
        self.assertEqual(sum(line.startswith(starts) for line in text.splitlines()), 20)
        self.assertIn("Sleep stages & SN1 & +0.095 & +0.062 &", text)
        self.assertIn("& +0.074 & +1.000 (25)", text)
        self.assertEqual(values["m2-human-unit-max"], "+0.004")

    def test_validation_table_includes_v9_and_v10(self) -> None:
        tables, _ = self._tables_and_values()
        self.assertIn("(V9)", tables["tab_validation"])
        self.assertIn("(V10)", tables["tab_validation"])

    def test_stager_table_gives_the_percent_session_free_contrast(self) -> None:
        tables, values = self._tables_and_values()
        self.assertIn(values["c3-yasa-sf-pct-mean"], tables["tab_s_stagers"])
        self.assertIn(values["c3-gssc-sf-pct-mean"], tables["tab_s_stagers"])


class Amendment006ReadingValuesTests(unittest.TestCase):
    """Amendment 006, parts C and E: values read from the committed records for the round-2 revision (27 October 2026)."""

    def test_reading_only_values(self) -> None:
        from careport.psg_assist_manuscript import collect_values, exploratory_consistency
        reports = load_reports(REPORTS)
        values = collect_values(reports, exploratory_consistency(reports["sim"]["calibration"]["model"]))
        self.assertEqual(values["m2-auto-units-pos"], "20")
        self.assertTrue(values["a2-stages-share"].startswith("3.6"), values["a2-stages-share"])
        self.assertEqual((values["sim-id-ref-cross"], values["sim-id-ref-cross-acc"]), ("+1.0", "0.945"))
        self.assertEqual((values["sim-id-dhuman-flip"], values["sim-id-dhuman-flip-acc"]), ("+1.5", "0.965"))


class RoundTwoTableTests(unittest.TestCase):
    """Round-2 letter items R3, S7, S9 and S25 (27 October 2026): table wording and the per-expert anchoring table."""

    def test_table_wording_and_per_expert_table(self) -> None:
        from careport.psg_assist_manuscript import collect_values, exploratory_consistency, render_tables
        reports = load_reports(REPORTS)
        values = collect_values(reports, exploratory_consistency(reports["sim"]["calibration"]["model"]))
        tables = render_tables(reports, values)
        primary = tables["tab_primary"]
        self.assertNotIn("CI)", primary)
        self.assertIn("95% interval".replace("%", chr(92) + "%"), primary)
        self.assertIn("Experts $>0$: the number of the 12 experts", primary)
        self.assertIn("unrounded", tables["tab_remedy"])
        experts = tables["tab_s_experts"]
        self.assertEqual(sum(line.startswith("Expert ") and line[7].isdigit() for line in experts.splitlines()), 12)
        self.assertIn("Expert 7 & +0.213 &", experts)
        units = tables["tab_s_units"]
        self.assertNotIn("the ones the independent re-implementation reproduced", units)
        self.assertIn("the independent re-implementation reproduced $\\Delta A$ for all 20 units and "
                      "$\\Delta_{\\mathrm{auto}}$, $\\Delta_{\\mathrm{human}}$ and DiD for sleep stages", units)


class Amendment006DerivedValuesTests(unittest.TestCase):
    """Amendment 006, parts A, B and D (approved 27 October 2026): derived quantities for the round-2 revision."""

    def _values_and_tables(self):
        from careport.psg_assist_manuscript import collect_values, exploratory_consistency, render_tables
        reports = load_reports(REPORTS)
        expl = exploratory_consistency(reports["sim"]["calibration"]["model"])
        values = collect_values(reports, expl)
        return values, render_tables(reports, values)

    def test_t_quantile_matches_textbook_values(self) -> None:
        from careport.psg_assist_manuscript import t_quantile
        self.assertAlmostEqual(t_quantile(0.975, 5), 2.571, places=3)
        self.assertAlmostEqual(t_quantile(0.975, 10), 2.228, places=3)
        self.assertAlmostEqual(t_quantile(0.975, 30), 2.042, places=3)
        self.assertAlmostEqual(t_quantile(0.975, 100000), 1.960, places=3)

    def test_part_a_audit_half_widths_with_estimated_variance(self) -> None:
        values, tables = self._values_and_tables()
        self.assertEqual(values["c4-gap-f10-df"], "5")
        self.assertEqual(values["c4-gap-f5-df"], "--")
        self.assertTrue(values["c4-gap-f10-d2-t"].startswith("0.05"), values["c4-gap-f10-d2-t"])
        self.assertIn(values["c4-smallest-f-t"], ("10" + chr(92) + "%", "20" + chr(92) + "%", "none in the grid"))
        self.assertIn("Degrees of", tables["tab_s_blocks"])
        self.assertLess(float(values["c4-gap-f10-d2-t-4dp"]), float(values["c4-gap-bias-4dp"]))
        self.assertIn("multiplier", tables["tab_remedy"])

    def test_part_b_exploratory_configuration(self) -> None:
        values, tables = self._values_and_tables()
        for key in ("expl-m1", "expl-bias-n1", "expl-bias-n25", "expl-v1", "expl-v8"):
            self.assertIn(key, values)
        self.assertTrue(values["expl-m1"].startswith("0.0"), values["expl-m1"])
        self.assertIn("Exploratory", tables["tab_validation"])

    def test_part_d_manual_reference_count(self) -> None:
        values, _ = self._values_and_tables()
        self.assertEqual(values["fda-manual-ref"], "10")  # 10 since the D1 adjudication of K221179 (28 October 2026)


class Amendment005D1Tests(unittest.TestCase):
    """Amendment 005, part D1: the blind second coding of the FDA summaries, adjudicated on 28 October 2026."""

    def _values_and_tables(self):
        from careport.psg_assist_manuscript import collect_values, exploratory_consistency, render_tables
        reports = load_reports(REPORTS)
        expl = exploratory_consistency(reports["sim"]["calibration"]["model"])
        values = collect_values(reports, expl)
        return values, render_tables(reports, values)

    def test_codes_file_loaded(self) -> None:
        reports = load_reports(REPORTS)
        self.assertEqual(len(reports["d1_codes"]), 66)
        self.assertEqual({r["field"] for r in reports["d1_codes"]},
                         {"reference_type", "blinding_to_device_output", "prescoring_reported"})

    def test_agreement_values_match_the_record(self) -> None:
        values, _ = self._values_and_tables()
        self.assertEqual(values["d1-ptd-ref-all-agree"], "21/22")
        self.assertEqual(values["d1-ptd-ref-all-kappa"], "0.937")
        self.assertEqual(values["d1-ptd-ref-blind-agree"], "11/12")
        self.assertEqual(values["d1-ptd-ref-seen-agree"], "10/10")
        self.assertEqual(values["d1-ptd-blind-all-agree"], "22/22")
        self.assertEqual(values["d1-ptd-blind-all-kappa"], "1.000")
        self.assertEqual(values["d1-dhan-ref-all-agree"], "18/22")
        self.assertEqual(values["d1-dhan-ref-all-kappa"], "0.747")
        self.assertEqual(values["d1-dhan-ref-blind-agree"], "8/10")
        self.assertEqual(values["d1-dhan-ref-blind-kappa"], "0.672")
        self.assertEqual(values["d1-dhan-pre-all-kappa"], "0.636")
        self.assertEqual(values["d1-dhan-pre-blind-kappa"], "0.000")
        self.assertEqual((values["d1-agree-min"], values["d1-agree-max"]), ("18", "22"))
        self.assertEqual((values["d1-kappa-min"], values["d1-kappa-max"]), ("0.636", "1.000"))
        self.assertEqual(values["d1-inter-ref-agree"], "19/22")
        self.assertEqual(values["d1-inter-ref-kappa"], "0.810")

    def test_adjudication_values_and_tables(self) -> None:
        values, tables = self._values_and_tables()
        self.assertEqual(values["d1-disagreements"], "8")
        self.assertEqual(values["d1-disagree-summaries"], "5")
        self.assertEqual(values["d1-both-disagree"], "1")
        self.assertEqual(values["d1-changed"], "1")
        self.assertEqual((values["d1-first-routine"], values["d1-first-notdesc"]), ("4", "2"))
        self.assertEqual((values["fda-routine"], values["fda-notdesc"], values["fda-unclear"]), ("3", "3", "7"))
        items = tables["tab_s_d1_items"]
        self.assertEqual(sum(line.startswith("K") for line in items.splitlines()), 8)
        self.assertIn("K221179", items)
        agreement = tables["tab_s_d1"]
        self.assertEqual(agreement.count("& P.T.D. &"), 3)
        self.assertEqual(agreement.count("& D.H.A.N. &"), 3)
