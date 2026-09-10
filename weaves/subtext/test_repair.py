import json
import unittest
from pathlib import Path
from unittest.mock import patch

from Marginalia.interpreter import MarginaliaInterpreter
from weaves.subtext.reader import extract_program, load_weave, split_sentences
from weaves.subtext.repair import repair_surface
from weaves.subtext.weaver import ConstructionError


HERE = Path(__file__).resolve().parent
NOTE = "Notes stay."
ALTERNATE_NOTE = "Newer days."
QUOTE = "Quiet waves return."
FORGET = "X clears."


class SubtextRepairTests(unittest.TestCase):
    def test_existing_construction_round_trips_without_edits(self):
        construction = HERE / "construction"
        source = (construction / "target.mrg").read_text(encoding="utf-8")
        surface = (construction / "carrier.md").read_text(encoding="utf-8")
        result = repair_surface(source, surface, [])
        self.assertEqual(result, {
            "surface": surface, "changed": False, "edits": [], "cost": 0,
        })

    def test_damaged_construction_uses_closest_authored_sentence(self):
        construction = HERE / "construction"
        source = (construction / "target.mrg").read_text(encoding="utf-8")
        surface = (construction / "carrier.md").read_text(encoding="utf-8")
        bank = json.loads((construction / "sentences.json").read_text(encoding="utf-8"))
        damaged = surface.replace("shared spaces.", "shared paths.", 1)
        result = repair_surface(source, damaged, bank)
        self.assertEqual(result["surface"], surface)
        self.assertEqual(extract_program(result["surface"]), source)
        self.assertEqual(result["cost"], 1)
        self.assertTrue(result["changed"])
        self.assertEqual(result["edits"], [{
            "kind": "replace",
            "sentence_number": 1,
            "target_line": 1,
            "before": split_sentences(damaged)[0],
            "after": split_sentences(surface)[0],
            "expected_instruction": "note 86",
        }])

    def test_sentence_replacement_preserves_unrelated_wording(self):
        source = "note 20\nquote\nforget\n"
        surface = f"Notes waits.\nQuestions remain in the garden!\n{FORGET}"
        result = repair_surface(source, surface, [ALTERNATE_NOTE, NOTE, QUOTE])
        self.assertEqual(result["surface"], f"{NOTE}\nQuestions remain in the garden!\n{FORGET}\n")
        self.assertEqual(result["cost"], 1)
        self.assertEqual(result["edits"][0]["after"], NOTE)

    def test_extra_sentence_is_deleted_without_cascading_replacements(self):
        source = "note 20\nquote\nforget\n"
        surface = f"{NOTE}\nEchoes remain.\n{QUOTE}\n{FORGET}\n"
        result = repair_surface(source, surface, [NOTE, QUOTE, FORGET])
        self.assertEqual(result["surface"], f"{NOTE}\n{QUOTE}\n{FORGET}\n")
        self.assertEqual(result["cost"], 1)
        self.assertEqual(result["edits"], [{
            "kind": "delete", "sentence_number": 2, "target_line": None,
            "before": "Echoes remain.", "after": None,
            "expected_instruction": None,
        }])

    def test_missing_sentence_is_inserted_before_preserved_suffix(self):
        source = "# actual source coordinates\n\nnote 20\nquote\nforget\n"
        result = repair_surface(source, f"{NOTE}\n{FORGET}\n", [QUOTE])
        self.assertEqual(result["surface"], f"{NOTE}\n{QUOTE}\n{FORGET}\n")
        self.assertEqual(result["cost"], 1)
        self.assertEqual(result["edits"], [{
            "kind": "insert", "sentence_number": None, "target_line": 4,
            "before": None, "after": QUOTE,
            "expected_instruction": "quote",
        }])

    def test_missing_initial_sentence_and_extra_trailing_sentence(self):
        result = repair_surface("note 20\nquote\n", f"{QUOTE}\n{FORGET}", [NOTE])
        self.assertEqual(result["surface"], f"{NOTE}\n{QUOTE}\n")
        self.assertEqual(result["cost"], 2)
        self.assertEqual([edit["kind"] for edit in result["edits"]], ["insert", "delete"])
        self.assertEqual(result["edits"][1]["sentence_number"], 2)

    def test_repeated_instruction_preserves_earliest_sentence_on_equal_cost(self):
        source = "note 20\nquote\n"
        surface = f"{ALTERNATE_NOTE}\n{NOTE}\n{QUOTE}\n"
        for _ in range(3):
            result = repair_surface(source, surface, [NOTE])
            self.assertEqual(result["surface"], f"{ALTERNATE_NOTE}\n{QUOTE}\n")
            self.assertEqual(result["edits"][0]["sentence_number"], 2)

    def test_secondary_token_distance_wins_over_bank_order(self):
        result = repair_surface("note 20\n", "Notes waits.", [ALTERNATE_NOTE, NOTE])
        self.assertEqual(result["surface"], f"{NOTE}\n")

    def test_equal_token_distance_uses_bank_order(self):
        bank = ["Novel days.", ALTERNATE_NOTE]
        result = repair_surface("note 20\n", "Notes waits.", bank)
        self.assertEqual(result["surface"], "Novel days.\n")
        reverse = repair_surface("note 20\n", "Notes waits.", list(reversed(bank)))
        self.assertEqual(reverse["surface"], f"{ALTERNATE_NOTE}\n")

    def test_token_distance_is_case_sensitive(self):
        result = repair_surface("note 20\n", "NOTES waits.", [NOTE, "NOTES stay."])
        self.assertEqual(result["surface"], "NOTES stay.\n")

    def test_insertions_use_shortest_word_distance_then_bank_order(self):
        result = repair_surface("quote\n", "", [QUOTE, "Quiet.", "Questions."])
        self.assertEqual(result["surface"], "Quiet.\n")
        self.assertEqual(result["cost"], 1)

    def test_bank_entries_can_be_reused_at_multiple_repair_locations(self):
        bank = [NOTE]
        result = repair_surface("note 20\nnote 20\nnote 20\n", "", bank)
        self.assertEqual(result["surface"], f"{NOTE}\n{NOTE}\n{NOTE}\n")
        self.assertEqual(result["cost"], 3)
        self.assertEqual(bank, [NOTE])
        self.assertTrue(all(edit["sentence_number"] is None for edit in result["edits"]))

    def test_empty_bank_can_preserve_and_delete(self):
        result = repair_surface("note 20\n", f"{NOTE}\n{QUOTE}", [])
        self.assertEqual(result["surface"], f"{NOTE}\n")
        self.assertEqual(result["cost"], 1)

    def test_missing_final_punctuation_can_be_replaced(self):
        result = repair_surface("note 20\nquote\n", f"{NOTE}\nQuiet waves return", [QUOTE])
        self.assertEqual(result["surface"], f"{NOTE}\n{QUOTE}\n")
        self.assertEqual(result["cost"], 1)
        self.assertEqual(result["edits"][0]["before"], "Quiet waves return")

    def test_unmapped_sentence_can_be_replaced_or_deleted(self):
        for damaged in ["Broken wording.", "...", "123!"]:
            with self.subTest(damaged=damaged):
                replacement = repair_surface("note 20\n", damaged, [NOTE])
                self.assertEqual(replacement["surface"], f"{NOTE}\n")
                self.assertEqual(replacement["edits"][0]["kind"], "replace")
                deletion = repair_surface("note 20\n", f"{damaged}\n{NOTE}", [])
                self.assertEqual(deletion["surface"], f"{NOTE}\n")
                self.assertEqual(deletion["edits"][0]["kind"], "delete")

    def test_formatting_reflow_is_not_an_executable_edit(self):
        result = repair_surface("note 20\nquote\n", f"  {NOTE}   {QUOTE}\n\n", [])
        self.assertEqual(result, {
            "surface": f"{NOTE}\n{QUOTE}\n", "changed": False, "edits": [], "cost": 0,
        })

    def test_preserved_sentence_keeps_internal_whitespace_and_punctuation(self):
        sentence = "Notes   stay!"
        result = repair_surface("note 20\n", f"  {sentence}  ", [])
        self.assertEqual(result["surface"], f"{sentence}\n")
        self.assertFalse(result["changed"])

    def test_authored_bank_sentence_whitespace_matches_constructor(self):
        result = repair_surface("note 20\n", "", ["  Notes\n  stay.  "])
        self.assertEqual(result["surface"], f"{NOTE}\n")

    def test_every_bank_entry_is_validated_even_if_surface_already_matches(self):
        invalid_entries = [None, 20, "", "   ", "Notes stay", "Broken wording.", "...", f"{NOTE} {QUOTE}"]
        for invalid in invalid_entries:
            with self.subTest(invalid=invalid):
                with self.assertRaises(ConstructionError) as raised:
                    repair_surface("note 20\n", NOTE, [NOTE, invalid])
                self.assertIn("bank entry 2", str(raised.exception))

    def test_bank_must_be_a_list(self):
        for bank in [None, NOTE, (NOTE,), {"sentence": NOTE}]:
            with self.subTest(bank=bank):
                with self.assertRaises(ConstructionError):
                    repair_surface("note 20\n", NOTE, bank)

    def test_surface_must_be_text(self):
        for surface in [None, 20, [NOTE], b"Notes stay."]:
            with self.subTest(surface=surface):
                with self.assertRaises(ConstructionError):
                    repair_surface("note 20\n", surface, [NOTE])

    def test_unavailable_bank_fails_without_modifying_inputs(self):
        surface = f"{NOTE}\n{QUOTE}\n"
        bank = [NOTE]
        with self.assertRaises(ConstructionError) as raised:
            repair_surface("note 20\nquote\nforget\n", surface, bank)
        self.assertIn("forget", str(raised.exception))
        self.assertIn("line 3", str(raised.exception))
        self.assertEqual(surface, f"{NOTE}\n{QUOTE}\n")
        self.assertEqual(bank, [NOTE])

    def test_required_order_cannot_be_invented_without_bank_entries(self):
        with self.assertRaises(ConstructionError) as raised:
            repair_surface("quote\nnote 20\n", f"{NOTE}\n{QUOTE}", [])
        message = str(raised.exception)
        self.assertIn("line 2", message)
        self.assertIn("'note 20'", message)
        self.assertIn("required order", message)
        self.assertNotIn("'quote'", message)

    def test_failure_reports_missing_instruction_after_preservable_prefix(self):
        source = "note 20\nnote 20\nnote 20\nforget\n"
        with self.assertRaises(ConstructionError) as raised:
            repair_surface(source, f"{NOTE}\n{NOTE}\n{NOTE}\n", [])
        message = str(raised.exception)
        self.assertIn("line 4", message)
        self.assertIn("'forget'", message)
        self.assertIn("no remaining surface sentence", message)
        self.assertIn("no bank sentence", message)
        self.assertNotIn("'note 20'", message)

    def test_failure_reports_first_unavailable_repetition_and_source_line(self):
        source = "# preserve the first occurrence\nnote 20\n\nnote 20\nnote 20\n"
        with self.assertRaises(ConstructionError) as raised:
            repair_surface(source, NOTE, [])
        message = str(raised.exception)
        self.assertIn("line 4", message)
        self.assertIn("'note 20'", message)
        self.assertNotIn("line 2", message)
        self.assertNotIn("line 5", message)

    def test_custom_profile_and_multiple_initial_aliases(self):
        profile = load_weave()
        profile["operations"] = {
            "S": {"opcode": "note", "operand": True},
            "T": {"opcode": "note", "operand": True},
            "P": {"opcode": "quote", "operand": False},
        }
        source = "note 20\nquote\n"
        result = repair_surface(source, "Stories waits.\nPeople listen.", ["Tales stay."], profile)
        self.assertEqual(result["surface"], "Tales stay.\nPeople listen.\n")
        self.assertEqual(extract_program(result["surface"], profile), source)

    def test_target_syntax_and_profile_are_validated(self):
        for source in ["", "note\n", "while\n", "listen\n", "note 8\n"]:
            with self.subTest(source=source):
                with self.assertRaises(ConstructionError):
                    repair_surface(source, NOTE, [NOTE])
        for profile in [[], {}, {"loom": "Another"}]:
            with self.subTest(profile=profile):
                with self.assertRaises(ConstructionError):
                    repair_surface("note 20\n", NOTE, [NOTE], profile)

    def test_repair_does_not_execute_loops_or_runtime_checks(self):
        source = "note 20\nwhile\nagain\nverify 20\n"
        bank = [NOTE, "While waiting.", "Again.", "Verify hope."]
        with patch.object(MarginaliaInterpreter, "run", side_effect=AssertionError("executed")):
            result = repair_surface(source, "", bank)
        self.assertEqual(extract_program(result["surface"]), source)

    def test_alignment_has_an_explicit_size_limit(self):
        with patch("weaves.subtext.repair.MAX_ALIGNMENT_CELLS", 3):
            with self.assertRaisesRegex(ConstructionError, "alignment is too large"):
                repair_surface("note 20\n", NOTE, [NOTE])

    def test_word_comparison_has_an_explicit_work_limit(self):
        with patch("weaves.subtext.repair.MAX_TOKEN_COMPARISON_CELLS", 0):
            with self.assertRaisesRegex(ConstructionError, "token comparison is too large"):
                repair_surface("note 20\n", "Notes waits.", [NOTE])


if __name__ == "__main__":
    unittest.main()
