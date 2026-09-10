import io
import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from Marginalia.interpreter import MarginaliaInterpreter
from weaves.subtext.reader import WeaveError, extract_program, load_weave, split_sentences
from weaves.subtext.weaver import ConstructionError, weave_thread


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
NOTE = "Notes stay."
ALTERNATE_NOTE = "Newer days."
QUOTE = "Quiet waves return."


class SubtextWeaverTests(unittest.TestCase):
    def test_construction_errors_are_reader_errors(self):
        self.assertTrue(issubclass(ConstructionError, WeaveError))

    def test_target_order_selects_matching_sentences_from_bank(self):
        bank = [QUOTE, "Nothing waits.", NOTE, "X clears."]
        source = "note 20\nquote\nforget\n"
        surface = weave_thread(source, bank)
        self.assertEqual(surface, f"{NOTE}\n{QUOTE}\nX clears.\n")
        self.assertEqual(extract_program(surface), source)

    def test_first_unused_match_wins_and_bank_is_not_mutated(self):
        bank = [ALTERNATE_NOTE, QUOTE, NOTE]
        original_bank = bank.copy()
        surface = weave_thread("note 20\nnote 20\nquote\n", bank)
        self.assertEqual(surface, f"{ALTERNATE_NOTE}\n{NOTE}\n{QUOTE}\n")
        self.assertEqual(bank, original_bank)

    def test_duplicate_entries_are_distinct_available_sentences(self):
        surface = weave_thread("note 20\nnote 20\n", [NOTE, NOTE])
        self.assertEqual(surface, f"{NOTE}\n{NOTE}\n")

    def test_a_single_entry_cannot_be_reused(self):
        with self.assertRaises(ConstructionError) as raised:
            weave_thread("note 20\nnote 20\n", [NOTE])
        message = str(raised.exception).lower()
        self.assertIn("note 20", message)
        self.assertIn("line 2", message)

    def test_alternate_wording_preserves_the_exact_thread(self):
        source = "note 20\nquote\n"
        first = weave_thread(source, [NOTE, QUOTE])
        second = weave_thread(source, [ALTERNATE_NOTE, "Questions rise."])
        self.assertNotEqual(first, second)
        self.assertEqual(extract_program(first), source)
        self.assertEqual(extract_program(second), source)

    def test_comments_case_and_operand_spelling_are_normalized(self):
        source = "# A visible thread\n\n  NoTe\t+020 # first mark\n\tQuOtE  \n"
        surface = weave_thread(source, [QUOTE, NOTE])
        self.assertEqual(extract_program(surface), "note 20\nquote\n")

    def test_marginalia_integer_spellings_are_normalized(self):
        for operand in ["2_0", "٢٠", '" 20 "']:
            with self.subTest(operand=operand):
                surface = weave_thread(f"note {operand}\n", [NOTE])
                self.assertEqual(extract_program(surface), "note 20\n")

    def test_target_must_be_text(self):
        for source in [None, 20, ["note 20"], b"note 20"]:
            with self.subTest(source=source):
                with self.assertRaises(ConstructionError):
                    weave_thread(source, [NOTE])

    def test_missing_match_reports_instruction_and_original_source_line(self):
        source = "# source lines matter\n\nnote 20\nquote # unavailable\n"
        with self.assertRaises(ConstructionError) as raised:
            weave_thread(source, [NOTE])
        message = str(raised.exception).lower()
        self.assertIn("quote", message)
        self.assertIn("line 4", message)

    def test_similar_operand_is_not_a_match(self):
        with self.assertRaises(ConstructionError) as raised:
            weave_thread("note 21\n", [NOTE])
        self.assertIn("note 21", str(raised.exception).lower())

    def test_empty_or_malformed_targets_are_rejected(self):
        sources = [
            "",
            "  # no instructions\n\n",
            "unknown 20\n",
            "listen\n",
            "note 20.0\n",
            "note 0x14\n",
            'note "20\n',
            "note -20\n",
            "note 0\n",
            "note 8\n",
        ]
        for source in sources:
            with self.subTest(source=source):
                with self.assertRaises(ConstructionError):
                    weave_thread(source, [NOTE, QUOTE])

    def test_required_operands_cannot_use_interpreter_defaults(self):
        for opcode in ["note", "doubt", "right", "left", "verify"]:
            with self.subTest(opcode=opcode):
                with self.assertRaises(ConstructionError):
                    weave_thread(f"{opcode}\n", [NOTE])

    def test_extra_operands_are_rejected_even_for_permissive_runtime_ops(self):
        sources = [
            "note 20 21\n",
            "doubt 20 21\n",
            "right 20 21\n",
            "left 20 21\n",
            "verify 20 21\n",
            "fold 20\n",
            "forget 20\n",
            "quote 20\n",
            "echo 20\n",
            "while 20\nagain\n",
            "while\nagain 20\n",
        ]
        bank = [
            NOTE,
            "Doubts wait.",
            "Right here.",
            "Left home.",
            "Verify hope.",
            "Fold memories.",
            "X clears.",
            QUOTE,
            "Echoes linger.",
            "Wonder returns.",
            "Again.",
        ]
        for source in sources:
            with self.subTest(source=source):
                with self.assertRaises(ConstructionError):
                    weave_thread(source, bank)

    def test_bank_must_be_a_nonempty_list_of_nonempty_strings(self):
        banks = [None, [], NOTE, {"sentence": NOTE}, (NOTE,), [None], [20], [""], [" \n "]]
        for bank in banks:
            with self.subTest(bank=bank):
                with self.assertRaises(ConstructionError):
                    weave_thread("note 20\n", bank)

    def test_every_bank_entry_is_validated_even_when_unused(self):
        invalid_entries = [
            "Broken surfaces do not silently compile.",
            "Notes stay",
            f"{QUOTE} {QUOTE}",
            "...",
            None,
            "",
        ]
        for invalid_entry in invalid_entries:
            with self.subTest(entry=invalid_entry):
                with self.assertRaises(ConstructionError):
                    weave_thread("note 20\n", [NOTE, invalid_entry])

    def test_unmatched_loop_markers_are_rejected(self):
        sources = ["while\n", "again\n", "again\nwhile\n", "while\nwhile\nagain\n"]
        bank = ["Wonder returns.", "Again.", "While waiting."]
        for source in sources:
            with self.subTest(source=source):
                with self.assertRaises(ConstructionError) as raised:
                    weave_thread(source, bank)
                self.assertIn("unmatched", str(raised.exception).lower())

    def test_construction_does_not_execute_a_balanced_loop(self):
        source = "note 20\nwhile\nagain\n"
        with patch.object(MarginaliaInterpreter, "run", side_effect=AssertionError("executed")):
            surface = weave_thread(source, ["Again.", NOTE, "Wonder returns."])
        self.assertEqual(extract_program(surface), source)

    def test_construction_does_not_evaluate_runtime_verification(self):
        source = "verify 20\n"
        with patch.object(MarginaliaInterpreter, "run", side_effect=AssertionError("executed")):
            surface = weave_thread(source, ["Verify hope."])
        self.assertEqual(extract_program(surface), source)

    def test_custom_profile_is_used_for_selection_and_round_trip(self):
        profile = load_weave()
        profile["operations"] = {
            "S": {"opcode": "note", "operand": True},
            "P": {"opcode": "quote", "operand": False},
        }
        source = "note 20\nquote\n"
        surface = weave_thread(source, ["People listen.", "Stories stay."], profile)
        self.assertEqual(surface, "Stories stay.\nPeople listen.\n")
        self.assertEqual(extract_program(surface, profile), source)

    def test_custom_listen_mapping_is_constructed_without_reading_input(self):
        profile = load_weave()
        profile["operations"]["I"] = {"opcode": "listen", "operand": False}
        with patch.object(MarginaliaInterpreter, "run", side_effect=AssertionError("executed")):
            surface = weave_thread("listen\n", ["Inward listening."], profile)
        self.assertEqual(extract_program(surface, profile), "listen\n")

    def test_canonical_thread_can_be_constructed_from_its_existing_prose(self):
        source = (HERE / "extracted.mrg").read_text(encoding="utf-8")
        bank = split_sentences((HERE / "carrier.md").read_text(encoding="utf-8"))
        surface = weave_thread(source, bank)
        self.assertEqual(surface, "\n".join(bank) + "\n")
        self.assertEqual(extract_program(surface), source)

    def test_committed_construction_reproduces_surface_thread_and_trace(self):
        construction = HERE / "construction"
        source = (construction / "target.mrg").read_text(encoding="utf-8")
        bank = json.loads((construction / "sentences.json").read_text(encoding="utf-8"))
        surface = weave_thread(source, bank)
        self.assertEqual(surface, (construction / "carrier.md").read_text(encoding="utf-8"))
        extracted = extract_program(surface)
        self.assertEqual(extracted, source)
        trace = io.StringIO()
        with redirect_stdout(trace):
            MarginaliaInterpreter(extracted).run()
        self.assertEqual(trace.getvalue(), "VOID")
        self.assertEqual(trace.getvalue(), (construction / "trace.txt").read_text(encoding="utf-8").rstrip("\n"))

    def test_reordering_construction_bank_changes_prose_but_preserves_thread(self):
        construction = HERE / "construction"
        source = (construction / "target.mrg").read_text(encoding="utf-8")
        bank = json.loads((construction / "sentences.json").read_text(encoding="utf-8"))
        original = weave_thread(source, bank)
        revised = weave_thread(source, list(reversed(bank)))
        self.assertNotEqual(revised, original)
        self.assertEqual(extract_program(revised), source)


class SubtextWeaverCliTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.directory = Path(self.temporary_directory.name)
        self.target = self.directory / "target.mrg"
        self.bank = self.directory / "bank.json"
        self.target.write_text("note 20\nquote\n", encoding="utf-8")
        self.bank.write_text(json.dumps([QUOTE, NOTE]), encoding="utf-8")

    def run_cli(self, *extra_arguments):
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "weaves.subtext.weaver",
                str(self.target),
                "--bank",
                str(self.bank),
                *map(str, extra_arguments),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )

    def test_stdout_contains_only_the_constructed_surface(self):
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, f"{NOTE}\n{QUOTE}\n")
        self.assertEqual(result.stderr, "")

    def test_output_option_writes_the_surface(self):
        destination = self.directory / "surface.md"
        result = self.run_cli("--output", destination)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertEqual(destination.read_text(encoding="utf-8"), f"{NOTE}\n{QUOTE}\n")

    def test_custom_profile_option(self):
        profile = load_weave()
        profile["operations"] = {
            "S": {"opcode": "note", "operand": True},
            "P": {"opcode": "quote", "operand": False},
        }
        profile_path = self.directory / "profile.json"
        profile_path.write_text(json.dumps(profile), encoding="utf-8")
        self.bank.write_text(json.dumps(["People listen.", "Stories stay."]), encoding="utf-8")
        result = self.run_cli("--weave", profile_path)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "Stories stay.\nPeople listen.\n")

    def test_failed_construction_leaves_existing_output_untouched(self):
        destination = self.directory / "surface.md"
        destination.write_text("Existing prose.\n", encoding="utf-8")
        self.bank.write_text(json.dumps([NOTE]), encoding="utf-8")
        result = self.run_cli("--output", destination)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertIn("Subtext construction error:", result.stderr)
        self.assertIn("quote", result.stderr.lower())
        self.assertIn("line 2", result.stderr.lower())
        self.assertEqual(destination.read_text(encoding="utf-8"), "Existing prose.\n")

    def test_failed_construction_does_not_print_a_partial_surface(self):
        self.bank.write_text(json.dumps([NOTE]), encoding="utf-8")
        result = self.run_cli()
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertIn("Subtext construction error:", result.stderr)

    def test_invalid_bank_json_produces_a_clean_error(self):
        self.bank.write_text("[invalid JSON", encoding="utf-8")
        result = self.run_cli()
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertIn("Subtext construction error:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_missing_input_produces_a_clean_error(self):
        self.target.unlink()
        result = self.run_cli()
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertIn("Subtext construction error:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_unwritable_destination_produces_a_clean_error(self):
        result = self.run_cli("--output", self.directory / "missing" / "surface.md")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertIn("Subtext construction error:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_output_cannot_overwrite_a_construction_input(self):
        for destination in [self.target, self.bank]:
            with self.subTest(destination=destination.name):
                original = destination.read_bytes()
                result = self.run_cli("--output", destination)
                self.assertEqual(result.returncode, 1)
                self.assertEqual(result.stdout, "")
                self.assertIn("Subtext construction error:", result.stderr)
                self.assertEqual(destination.read_bytes(), original)

    def test_output_cannot_overwrite_an_input_through_a_hard_link(self):
        destination = self.directory / "linked-output.md"
        destination.hardlink_to(self.target)
        original = self.target.read_bytes()
        result = self.run_cli("--output", destination)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertIn("Subtext construction error:", result.stderr)
        self.assertEqual(self.target.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
