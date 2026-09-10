import io
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from Marginalia.interpreter import MarginaliaInterpreter
from weaves.subtext.reader import extract_program, load_weave, read_surface


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SPECIMEN = HERE / "multiple_readers"


class SubtextMultipleReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.surface = (SPECIMEN / "carrier.md").read_text(encoding="utf-8")
        cls.profiles = {
            name: load_weave(SPECIMEN / f"{name}.json") for name in ("west", "east")
        }
        cls.programs = {
            name: (SPECIMEN / f"{name}.mrg").read_text(encoding="utf-8")
            for name in cls.profiles
        }
        cls.traces = {
            name: (SPECIMEN / f"{name}.trace.txt").read_text(encoding="utf-8").rstrip("\n")
            for name in cls.profiles
        }

    def execute(self, program):
        output = io.StringIO()
        interpreter = MarginaliaInterpreter(program)
        with redirect_stdout(output):
            interpreter.run()
        return output.getvalue(), interpreter

    def test_each_profile_extracts_its_committed_thread(self):
        for name, profile in self.profiles.items():
            with self.subTest(profile=name):
                self.assertEqual(extract_program(self.surface, profile), self.programs[name])
        self.assertNotEqual(self.programs["west"], self.programs["east"])

    def test_extracted_threads_produce_distinct_printable_traces(self):
        for name, profile in self.profiles.items():
            with self.subTest(profile=name):
                trace, _ = self.execute(extract_program(self.surface, profile))
                self.assertEqual(trace, self.traces[name])
                self.assertEqual(trace, {"west": "GO", "east": "NO"}[name])
                self.assertTrue(trace.isprintable())

    def test_profiles_share_encoding_and_differ_only_in_turn_direction(self):
        west = self.profiles["west"]
        east = self.profiles["east"]
        self.assertEqual(west["operand_encoding"], east["operand_encoding"])
        self.assertEqual(west["sentence_split"], east["sentence_split"])
        self.assertEqual(west["operations"].keys(), east["operations"].keys())
        differences = {
            initial for initial in west["operations"]
            if west["operations"][initial] != east["operations"][initial]
        }
        self.assertEqual(differences, {"T"})
        self.assertEqual(west["operations"]["T"], {"opcode": "left", "operand": True})
        self.assertEqual(east["operations"]["T"], {"opcode": "right", "operand": True})
        readings = {name: read_surface(self.surface, profile) for name, profile in self.profiles.items()}
        self.assertEqual(
            [item.operand for item in readings["west"]],
            [item.operand for item in readings["east"]],
        )
        self.assertEqual(readings["west"][5].operand, 32)

    def test_reader_selects_one_margin_and_preserves_the_other(self):
        for name, chosen, untouched, original in (("west", -32, 32, 78), ("east", 32, -32, 71)):
            with self.subTest(profile=name):
                _, interpreter = self.execute(extract_program(self.surface, self.profiles[name]))
                self.assertEqual(interpreter.ptr, chosen)
                self.assertEqual(interpreter.margins[chosen], [79])
                self.assertEqual(interpreter.margins[untouched], [original])

    def test_whitespace_reflow_preserves_both_threads_and_traces(self):
        reflowed = " \n\t\n".join(self.surface.split())
        for name, profile in self.profiles.items():
            with self.subTest(profile=name):
                program = extract_program(reflowed, profile)
                self.assertEqual(program, self.programs[name])
                self.assertEqual(self.execute(program)[0], self.traces[name])

    def test_shorter_turn_tail_selects_empty_margins_under_both_profiles(self):
        revised = self.surface.replace("Turning changes bearings.", "Turning changes bearing.")
        self.assertNotEqual(revised, self.surface)
        for name, direction, margin in (("west", "left", -31), ("east", "right", 31)):
            with self.subTest(profile=name):
                program = extract_program(revised, self.profiles[name])
                self.assertEqual(program.splitlines()[5], f"{direction} 31")
                self.assertEqual(program.splitlines()[:5], self.programs[name].splitlines()[:5])
                self.assertEqual(program.splitlines()[6:], self.programs[name].splitlines()[6:])
                trace, interpreter = self.execute(program)
                self.assertEqual(trace, "\x00O")
                self.assertEqual(interpreter.ptr, margin)
                self.assertEqual(interpreter.margins[-32], [71])
                self.assertEqual(interpreter.margins[32], [78])

    def test_cli_extracts_each_profile_and_explains_the_turn(self):
        for name, direction in (("west", "left"), ("east", "right")):
            with self.subTest(profile=name):
                result = subprocess.run(
                    [
                        sys.executable, "-m", "weaves.subtext.reader", str(SPECIMEN / "carrier.md"),
                        "--weave", str(SPECIMEN / f"{name}.json"), "--explain",
                    ],
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, self.programs[name])
                self.assertIn(f"06 T -> {direction} 32", result.stderr)


if __name__ == "__main__":
    unittest.main()
