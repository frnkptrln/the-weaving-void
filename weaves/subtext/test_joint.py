import io
import itertools
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from dataclasses import asdict

from Marginalia.interpreter import MarginaliaInterpreter
from weaves.subtext.joint import weave_readers
from weaves.subtext.reader import extract_program, load_weave, split_sentences
from weaves.subtext.weaver import ConstructionError

HERE = Path(__file__).resolve().parent
SPECIMEN = HERE / "multiple_readers"
ROOT = HERE.parents[1]


class JointConstructionTests(unittest.TestCase):
    def setUp(self):
        self.profiles = {name: load_weave(SPECIMEN / f"{name}.json") for name in ("west", "east")}
        self.targets = {name: (SPECIMEN / f"{name}.mrg").read_text() for name in self.profiles}
        self.bank = split_sentences((SPECIMEN / "carrier.md").read_text())

    def test_joint_reconstruction_executes_both_distinct_traces(self):
        result = weave_readers(self.targets, self.bank, self.profiles)
        for name, expected in (("west", "GO"), ("east", "NO")):
            program = extract_program(result.surface, self.profiles[name])
            self.assertEqual(program, self.targets[name])
            output = io.StringIO()
            with redirect_stdout(output):
                MarginaliaInterpreter(program).run()
            self.assertEqual(output.getvalue(), expected)
        self.assertEqual(len(set(result.selected_bank_entries)), len(self.bank))

    def test_second_authored_surface_and_witness_are_reproducible(self):
        bank = json.loads((SPECIMEN / "joint_bank.json").read_text())
        result = weave_readers(self.targets, bank, self.profiles)
        self.assertEqual(result.surface, (SPECIMEN / "joint_carrier.md").read_text())
        self.assertEqual(json.loads(json.dumps(asdict(result))),
                         json.loads((SPECIMEN / "joint_witness.json").read_text()))
        self.assertEqual(result.assignment_count, 9216)
        self.assertNotEqual(result.surface, (SPECIMEN / "carrier.md").read_text())
        for name, profile in self.profiles.items():
            self.assertEqual(extract_program(result.surface, profile), self.targets[name])

    def test_rejects_individually_possible_but_jointly_inconsistent_targets(self):
        # L maps to left under both readers; T maps left/right. No sentence
        # maps right/left, although each instruction exists individually.
        with self.assertRaisesRegex(ConstructionError, "satisfies all readers"):
            weave_readers({"west":"right 32", "east":"left 32"},
                          ["Turning changes bearings.", "Returning changes bearings.", "Listening demands patience."],
                          self.profiles)

    def test_assignment_count_matches_exhaustive_small_bank(self):
        bank = ["Questions linger.", "Quietly, we listen.", "Questions linger."]
        targets = {name:"quote\nquote" for name in self.profiles}
        result = weave_readers(targets, bank, self.profiles)
        brute = sum(all(extract_program("\n".join(bank[i] for i in indices), profile) == "quote\nquote\n"
                        for profile in self.profiles.values())
                    for indices in itertools.permutations(range(3), 2))
        self.assertEqual(result.assignment_count, brute)
        self.assertEqual(result.assignment_count, 6)  # index assignments, not unique prose
        self.assertEqual(result.selected_bank_entries, (1, 2))
        self.assertEqual(result.available_at_selection, (3, 2))

    def test_input_order_does_not_change_reader_signature_order(self):
        result = weave_readers(dict(reversed(list(self.targets.items()))), self.bank, self.profiles)
        self.assertEqual(result, weave_readers(self.targets, self.bank, self.profiles))

    def test_consumption_and_reader_alignment(self):
        with self.assertRaisesRegex(ConstructionError, "sentence 2"):
            weave_readers({name:"quote\nquote" for name in self.profiles}, ["Quietly."], self.profiles)
        with self.assertRaisesRegex(ConstructionError, "same instruction count"):
            weave_readers({"west":"quote", "east":"quote\nquote"}, ["Quietly."], self.profiles)
        with self.assertRaisesRegex(ConstructionError, "same reader names"):
            weave_readers(self.targets, self.bank, {"west":self.profiles["west"]})

    def test_unmapped_sentences_are_reported_not_silently_erased(self):
        result = weave_readers({name:"quote" for name in self.profiles},
                              ["Zebras wait.", "Quietly."], self.profiles)
        self.assertEqual(result.incompatible_bank_entries, (1,))
        self.assertEqual(result.unused_bank_entries, (1,))

    def test_malformed_bank_is_rejected(self):
        for bank in [None, [], [3], [""], ["no punctuation"], ["Quietly. Questions."]]:
            with self.subTest(bank=bank), self.assertRaises(ConstructionError):
                weave_readers(self.targets, bank, self.profiles)

    def test_cli_witness_and_input_overwrite_guard(self):
        with tempfile.TemporaryDirectory() as directory:
            bank = Path(directory) / "bank.json"
            bank.write_text(json.dumps(self.bank))
            command = [sys.executable, "-m", "weaves.subtext.joint", "--bank", str(bank)]
            for name in self.profiles:
                command += ["--reader", name, str(SPECIMEN / f"{name}.json"), str(SPECIMEN / f"{name}.mrg")]
            run = subprocess.run(command + ["--json"], cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(json.loads(run.stdout)["programs"], self.targets)
            before = bank.read_bytes()
            run = subprocess.run(command + ["--output", str(bank)], cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(run.returncode, 1)
            self.assertIn("overwrite", run.stderr)
            self.assertEqual(bank.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
