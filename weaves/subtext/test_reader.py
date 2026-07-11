import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from Marginalia.interpreter import MarginaliaInterpreter
from weaves.subtext.reader import WeaveError, extract_program


HERE = Path(__file__).resolve().parent


class SubtextReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.surface = (HERE / "carrier.md").read_text(encoding="utf-8")
        cls.expected_program = (HERE / "extracted.mrg").read_text(encoding="utf-8")
        cls.expected_trace = (HERE / "trace.txt").read_text(encoding="utf-8").rstrip("\n")

    def execute(self, program):
        output = io.StringIO()
        with redirect_stdout(output):
            MarginaliaInterpreter(program).run()
        return output.getvalue()

    def test_canonical_surface_extracts_committed_thread(self):
        self.assertEqual(extract_program(self.surface), self.expected_program)

    def test_committed_thread_leaves_committed_trace(self):
        self.assertEqual(self.execute(self.expected_program), self.expected_trace)

    def test_whitespace_reflow_preserves_thread(self):
        reflowed = "  \n\n".join(self.surface.split())
        self.assertEqual(extract_program(reflowed), self.expected_program)

    def test_nonstructural_word_substitution_preserves_thread(self):
        revised = self.surface.replace("attentive", "carefulxx", 1)
        self.assertEqual(extract_program(revised), self.expected_program)

    def test_final_word_length_changes_operand_and_trace(self):
        revised = self.surface.replace("woven traces.", "woven marks.", 1)
        revised_program = extract_program(revised)
        self.assertNotEqual(revised_program, self.expected_program)
        self.assertNotEqual(self.execute(revised_program), self.expected_trace)

    def test_sentence_reordering_changes_thread(self):
        sentences = self.surface.replace("\n", " ").split(". ")
        sentences[0], sentences[1] = sentences[1], sentences[0]
        revised = ". ".join(sentences)
        self.assertNotEqual(extract_program(revised), self.expected_program)

    def test_unmapped_initial_is_rejected(self):
        with self.assertRaisesRegex(WeaveError, "unmapped initial"):
            extract_program("Broken surfaces do not silently compile.")


if __name__ == "__main__":
    unittest.main()
