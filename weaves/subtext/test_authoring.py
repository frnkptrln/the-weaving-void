import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from Marginalia.interpreter import MarginaliaInterpreter
from weaves.subtext.authoring import diagnose_surface, plan_thread
from weaves.subtext.reader import extract_program, load_weave
from weaves.subtext.weaver import ConstructionError


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
NOTE = "Notes stay."
QUOTE = "Quiet waves return."


class SubtextPlanTests(unittest.TestCase):
    def test_plan_normalizes_instructions_and_preserves_source_lines(self):
        source = "# A visible thread\n\n  NoTe +020 # first mark\n\tQuOtE\n"
        plan = plan_thread(source)
        self.assertEqual(len(plan), 2)
        first, second = plan
        self.assertEqual(first["sentence_number"], 1)
        self.assertEqual(first["source_line"], 3)
        self.assertEqual(first["instruction"], "note 20")
        self.assertEqual(first["initials"], ["N"])
        self.assertEqual(first["operand"], 20)
        self.assertEqual(first["word_count_range"], [1, 2])
        self.assertEqual(second["sentence_number"], 2)
        self.assertEqual(second["source_line"], 4)
        self.assertEqual(second["instruction"], "quote")
        self.assertEqual(second["initials"], ["Q"])
        self.assertIsNone(second["operand"])
        self.assertIsNone(second["word_count_range"])
        self.assertEqual(second["suggested_shapes"], [])

    def test_suggested_shapes_satisfy_the_actual_operand_equation(self):
        for operand in [9, 16, 17, 20, 32, 86, 255]:
            with self.subTest(operand=operand):
                row = plan_thread(f"note {operand}\n")[0]
                self.assertEqual(row["word_count_range"], [1, operand // 8])
                self.assertTrue(row["suggested_shapes"])
                for shape in row["suggested_shapes"]:
                    count = shape["word_count"]
                    tail = shape["final_word_length"]
                    self.assertGreaterEqual(count, 1)
                    self.assertGreaterEqual(tail, 1)
                    self.assertLessEqual(tail, 16)
                    self.assertEqual(8 * count + tail, operand)

    def test_large_operands_have_bounded_suggestions(self):
        operand = 10**30 + 3
        row = plan_thread(f"note {operand}\n")[0]
        self.assertEqual(row["word_count_range"], [1, operand // 8])
        self.assertTrue(row["suggested_shapes"])
        self.assertLessEqual(len(row["suggested_shapes"]), 16)
        for shape in row["suggested_shapes"]:
            self.assertEqual(8 * shape["word_count"] + shape["final_word_length"], operand)

    def test_plan_includes_word_count_bound_for_zero_letter_unicode_tails(self):
        for operand in [16, 24, 32]:
            with self.subTest(operand=operand):
                row = plan_thread(f"note {operand}\n")[0]
                self.assertEqual(row["word_count_range"], [1, operand // 8])
                self.assertIs(row["zero_letter_tail_possible"], True)
                self.assertTrue(all(shape["final_word_length"] >= 1 for shape in row["suggested_shapes"]))
        for operand in [9, 17, 20, 25]:
            with self.subTest(operand=operand):
                self.assertIs(plan_thread(f"note {operand}\n")[0]["zero_letter_tail_possible"], False)

    def test_custom_profile_lists_every_available_initial(self):
        profile = load_weave()
        profile["operations"] = {
            "S": {"opcode": "note", "operand": True},
            "N": {"opcode": "note", "operand": True},
            "P": {"opcode": "quote", "operand": False},
        }
        plan = plan_thread("note 20\nquote\n", profile)
        self.assertEqual(set(plan[0]["initials"]), {"S", "N"})
        self.assertEqual(plan[1]["initials"], ["P"])

    def test_malformed_or_unrepresentable_targets_are_construction_errors(self):
        for source in [
            "", "# only a comment\n", "note 8\n", "note -20\n", "note\n",
            "note 20 21\n", "note 20.0\n", "unknown\n", "while\n", "again\n",
            None, 20,
        ]:
            with self.subTest(source=source):
                with self.assertRaises(ConstructionError):
                    plan_thread(source)

    def test_profile_validation_and_missing_operation_are_construction_errors(self):
        for profile in [{}, [], {"operations": {}}]:
            with self.subTest(profile=profile):
                with self.assertRaises(ConstructionError):
                    plan_thread("note 20\n", profile)
        profile = load_weave()
        del profile["operations"]["N"]
        with self.assertRaises(ConstructionError):
            plan_thread("note 20\n", profile)


class SubtextDiagnosisTests(unittest.TestCase):
    def test_matching_surface_reports_readings_and_writing_constraints(self):
        source = "# source\nnote 20\n\nquote\n"
        surface = f"{NOTE}\n{QUOTE}\n"
        report = diagnose_surface(source, surface)
        self.assertIs(report["matches"], True)
        self.assertEqual(report["expected_count"], 2)
        self.assertEqual(report["actual_count"], 2)
        self.assertEqual([row["status"] for row in report["rows"]], ["match", "match"])
        first = report["rows"][0]
        self.assertEqual(first["source_line"], 2)
        self.assertEqual(first["sentence_number"], 1)
        self.assertEqual(first["expected"], "note 20")
        self.assertEqual(first["actual"], "note 20")
        self.assertEqual(first["sentence"], NOTE)
        self.assertIsNone(first["error"])
        self.assertEqual(first["observed"], {
            "initial": "N", "word_count": 2, "final_word_length": 4,
        })
        self.assertEqual(first["constraints"], plan_thread(source)[0])
        self.assertEqual(report["rows"][1]["source_line"], 4)

    def test_changed_operand_reports_expected_and_actual_without_cascading(self):
        report = diagnose_surface("note 20\nquote\n", f"Nothing waits.\n{QUOTE}")
        self.assertIs(report["matches"], False)
        self.assertEqual([row["status"] for row in report["rows"]], ["change", "match"])
        changed = report["rows"][0]
        self.assertEqual(changed["expected"], "note 20")
        self.assertEqual(changed["actual"], "note 21")
        self.assertEqual(changed["observed"]["final_word_length"], 5)

    def test_missing_sentence_keeps_later_readings_aligned(self):
        report = diagnose_surface("note 20\nquote\nforget\n", f"{NOTE}\nX clears.")
        self.assertEqual([row["status"] for row in report["rows"]], ["match", "missing", "match"])
        self.assertEqual((report["expected_count"], report["actual_count"]), (3, 2))
        missing = report["rows"][1]
        self.assertEqual(missing["source_line"], 2)
        self.assertEqual(missing["expected"], "quote")
        for field in ["sentence_number", "actual", "sentence", "observed"]:
            self.assertIsNone(missing[field])
        self.assertEqual(report["rows"][2]["sentence_number"], 2)
        self.assertEqual(report["rows"][2]["source_line"], 3)

    def test_extra_sentence_keeps_later_readings_aligned(self):
        report = diagnose_surface("note 20\nquote\n", f"{NOTE}\nEchoes linger.\n{QUOTE}")
        self.assertEqual([row["status"] for row in report["rows"]], ["match", "extra", "match"])
        self.assertEqual((report["expected_count"], report["actual_count"]), (2, 3))
        extra = report["rows"][1]
        self.assertEqual(extra["actual"], "echo")
        self.assertEqual(extra["sentence_number"], 2)
        for field in ["source_line", "expected", "constraints"]:
            self.assertIsNone(extra[field])
        self.assertEqual(report["rows"][2]["sentence_number"], 3)
        self.assertEqual(report["rows"][2]["source_line"], 2)

    def test_empty_surface_reports_all_target_sentences_missing(self):
        for surface in ["", " \n\t "]:
            with self.subTest(surface=surface):
                report = diagnose_surface("note 20\nquote\n", surface)
                self.assertIs(report["matches"], False)
                self.assertEqual(report["actual_count"], 0)
                self.assertEqual([row["status"] for row in report["rows"]], ["missing", "missing"])

    def test_unmapped_sentence_is_a_local_error(self):
        report = diagnose_surface("note 20\nquote\n", f"Broken surfaces.\n{QUOTE}")
        self.assertEqual([row["status"] for row in report["rows"]], ["change", "match"])
        row = report["rows"][0]
        self.assertIsNone(row["actual"])
        self.assertIn("unmapped", row["error"].lower())
        self.assertEqual(row["observed"]["initial"], "B")
        self.assertEqual(row["sentence_number"], 1)

    def test_missing_terminal_punctuation_is_a_local_error(self):
        report = diagnose_surface("note 20\nquote\n", f"{NOTE}\nQuiet waves return")
        self.assertEqual([row["status"] for row in report["rows"]], ["match", "change"])
        row = report["rows"][1]
        self.assertIsNone(row["actual"])
        self.assertIn("punctuation", row["error"].lower())
        self.assertEqual(row["sentence_number"], 2)
        self.assertEqual(row["observed"]["initial"], "Q")

    def test_wordless_sentence_is_a_local_error(self):
        report = diagnose_surface("note 20\nquote\n", f"...\n{QUOTE}")
        self.assertEqual([row["status"] for row in report["rows"]], ["change", "match"])
        self.assertIn("words", report["rows"][0]["error"].lower())

    def test_sentence_numbers_in_errors_refer_to_the_original_surface(self):
        report = diagnose_surface("note 20\nquote\n", f"{NOTE}\nBroken surface.")
        row = report["rows"][1]
        self.assertEqual(row["sentence_number"], 2)
        self.assertIn("sentence 2", row["error"].lower())

    def test_observed_word_features_follow_the_reader_apostrophe_rules(self):
        report = diagnose_surface("note 20\n", "Nora can't.")
        self.assertIs(report["matches"], True)
        self.assertEqual(report["rows"][0]["observed"], {
            "initial": "N", "word_count": 2, "final_word_length": 4,
        })

    def test_zero_letter_unicode_tail_matches_the_existing_reader(self):
        surface = "Now ²."
        self.assertEqual(extract_program(surface), "note 16\n")
        report = diagnose_surface("note 16\n", surface)
        self.assertIs(report["matches"], True)
        row = report["rows"][0]
        self.assertEqual(row["observed"], {
            "initial": "N", "word_count": 2, "final_word_length": 0,
        })
        self.assertEqual(row["constraints"]["word_count_range"], [1, 2])
        self.assertIs(row["constraints"]["zero_letter_tail_possible"], True)

    def test_custom_profile_is_used_for_both_target_and_surface(self):
        profile = load_weave()
        profile["operations"] = {
            "S": {"opcode": "note", "operand": True},
            "P": {"opcode": "quote", "operand": False},
        }
        report = diagnose_surface("note 20\nquote\n", "Stories stay.\nPeople listen.", profile)
        self.assertIs(report["matches"], True)
        self.assertEqual(report["rows"][0]["constraints"]["initials"], ["S"])

    def test_planning_and_diagnosis_never_execute_the_target(self):
        source = "note 20\nwhile\nagain\n"
        with patch.object(MarginaliaInterpreter, "run", side_effect=AssertionError("executed")):
            plan = plan_thread(source)
            report = diagnose_surface(source, f"{NOTE}\nWonder returns.\nAgain.")
        self.assertEqual(len(plan), 3)
        self.assertIs(report["matches"], True)

    def test_invalid_target_is_not_reported_as_a_surface_mismatch(self):
        with self.assertRaises(ConstructionError):
            diagnose_surface("while\n", "Wonder returns.")

    def test_committed_draft_identifies_the_single_word_change(self):
        construction = HERE / "construction"
        source = (construction / "target.mrg").read_text(encoding="utf-8")
        draft = (construction / "draft.md").read_text(encoding="utf-8")
        report = diagnose_surface(source, draft)
        self.assertFalse(report["matches"])
        self.assertEqual([row["status"] for row in report["rows"]], ["change"] + ["match"] * 10)
        self.assertEqual(report["rows"][0]["expected"], "note 86")
        self.assertEqual(report["rows"][0]["actual"], "note 85")


class SubtextAuthoringCliTests(unittest.TestCase):
    def setUp(self):
        temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(temporary_directory.cleanup)
        self.directory = Path(temporary_directory.name)
        self.target = self.directory / "target.mrg"
        self.surface = self.directory / "surface.md"
        self.bank = self.directory / "bank.json"
        self.target.write_text("note 20\nquote\n", encoding="utf-8")
        self.surface.write_text(f"{NOTE}\n{QUOTE}\n", encoding="utf-8")
        self.bank.write_text(json.dumps([NOTE, QUOTE]), encoding="utf-8")

    def run_cli(self, *arguments):
        return subprocess.run(
            [sys.executable, "-m", "weaves.subtext.authoring", *map(str, arguments)],
            cwd=ROOT, capture_output=True, text=True, timeout=10, check=False,
        )

    def test_plan_json_matches_the_library_report(self):
        result = self.run_cli("plan", self.target, "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), plan_thread(self.target.read_text(encoding="utf-8")))
        self.assertEqual(result.stderr, "")

    def test_plan_default_is_readable_and_identifies_target_instructions(self):
        result = self.run_cli("plan", self.target)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("note 20", result.stdout)
        self.assertIn("quote", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_check_json_distinguishes_matches_and_mismatches_by_exit_status(self):
        for surface, expected_code in [(f"{NOTE}\n{QUOTE}", 0), (f"Nothing waits.\n{QUOTE}", 1)]:
            with self.subTest(exit_code=expected_code):
                self.surface.write_text(surface, encoding="utf-8")
                result = self.run_cli("check", self.target, self.surface, "--json")
                self.assertEqual(result.returncode, expected_code, result.stderr)
                self.assertEqual(json.loads(result.stdout), diagnose_surface("note 20\nquote\n", surface))
                self.assertEqual(result.stderr, "")

    def test_invalid_surface_is_a_diagnosis_not_a_cli_failure(self):
        self.surface.write_text(f"{NOTE}\nQuiet waves return", encoding="utf-8")
        result = self.run_cli("check", self.target, self.surface, "--json")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertFalse(json.loads(result.stdout)["matches"])
        self.assertEqual(result.stderr, "")

    def test_malformed_target_and_missing_input_produce_clean_errors(self):
        self.target.write_text("note 8\n", encoding="utf-8")
        for command in [("plan", self.target), ("check", self.target, self.surface), ("plan", self.directory / "missing.mrg")]:
            with self.subTest(command=command):
                result = self.run_cli(*command)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")
                self.assertTrue(result.stderr)
                self.assertNotIn("Traceback", result.stderr)

    def test_plan_and_check_accept_a_custom_weave(self):
        profile = load_weave()
        profile["operations"] = {
            "S": {"opcode": "note", "operand": True},
            "P": {"opcode": "quote", "operand": False},
        }
        profile_path = self.directory / "weave.json"
        profile_path.write_text(json.dumps(profile), encoding="utf-8")
        self.surface.write_text("Stories stay.\nPeople listen.\n", encoding="utf-8")
        planned = self.run_cli("plan", self.target, "--weave", profile_path, "--json")
        checked = self.run_cli("check", self.target, self.surface, "--weave", profile_path, "--json")
        self.assertEqual(planned.returncode, 0, planned.stderr)
        self.assertEqual(json.loads(planned.stdout)[0]["initials"], ["S"])
        self.assertEqual(checked.returncode, 0, checked.stderr)
        self.assertTrue(json.loads(checked.stdout)["matches"])

    def test_repair_stdout_is_only_the_repaired_surface(self):
        self.surface.write_text(f"Nothing waits.\n{QUOTE}\n", encoding="utf-8")
        result = self.run_cli("repair", self.target, self.surface, "--bank", self.bank)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(extract_program(result.stdout), "note 20\nquote\n")
        self.assertEqual(result.stdout, f"{NOTE}\n{QUOTE}\n")
        self.assertTrue(result.stderr)

    def test_repair_output_writes_a_round_tripping_surface(self):
        self.surface.write_text(f"Nothing waits.\n{QUOTE}\n", encoding="utf-8")
        destination = self.directory / "repaired.md"
        result = self.run_cli("repair", self.target, self.surface, "--bank", self.bank, "--output", destination)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertEqual(extract_program(destination.read_text(encoding="utf-8")), "note 20\nquote\n")

    def test_failed_repair_preserves_existing_output(self):
        self.surface.write_text(f"Nothing waits.\n{QUOTE}\n", encoding="utf-8")
        self.bank.write_text(json.dumps([QUOTE]), encoding="utf-8")
        destination = self.directory / "repaired.md"
        destination.write_text("Existing prose.\n", encoding="utf-8")
        result = self.run_cli("repair", self.target, self.surface, "--bank", self.bank, "--output", destination)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(destination.read_text(encoding="utf-8"), "Existing prose.\n")

    def test_repair_cannot_overwrite_any_input_file(self):
        profile_path = self.directory / "weave.json"
        profile_path.write_text(json.dumps(load_weave()), encoding="utf-8")
        for destination in [self.target, self.surface, self.bank, profile_path]:
            with self.subTest(destination=destination.name):
                original = destination.read_bytes()
                result = self.run_cli(
                    "repair", self.target, self.surface, "--bank", self.bank,
                    "--weave", profile_path, "--output", destination,
                )
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")
                self.assertNotIn("Traceback", result.stderr)
                self.assertEqual(destination.read_bytes(), original)

    def test_repair_preserves_input_reached_through_a_hard_link(self):
        destination = self.directory / "linked-output.md"
        destination.hardlink_to(self.target)
        original = self.target.read_bytes()
        result = self.run_cli("repair", self.target, self.surface, "--bank", self.bank, "--output", destination)
        self.assertIn(result.returncode, [0, 2], result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(self.target.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
