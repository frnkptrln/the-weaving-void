import io
import unittest
from contextlib import redirect_stdout

from Marginalia.interpreter import MarginaliaInterpreter
from weaves.subtext.explorer import OUTPUT, build_data, build_html


class ExplorerTests(unittest.TestCase):
    def test_all_replays_keep_the_canonical_and_mutation_results(self):
        cases = build_data()["cases"]
        self.assertEqual(len(cases), 6)
        for direction, output in (("west", "GO"), ("east", "NO")):
            original, reflow, mutation = (cases[f"{v}/{direction}"] for v in ("original", "reflow", "one-letter"))
            self.assertEqual(original["states"][-1]["output"], output)
            self.assertEqual(original["states"], reflow["states"])
            self.assertEqual(original["program"], reflow["program"])
            self.assertNotEqual(original["witness"]["surface_sha256"], reflow["witness"]["surface_sha256"])
            self.assertEqual(mutation["readings"][5]["operand"], 31)
            self.assertEqual(mutation["states"][-1]["output"], "\x00O")
            self.assertEqual(len(original["states"]), 11)
            unchosen = "32" if direction == "west" else "-32"
            self.assertEqual(original["states"][-1]["margins"][unchosen], [78 if direction == "west" else 71])

    def test_committed_page_reproduces(self):
        self.assertEqual(OUTPUT.read_bytes(), build_html().encode("utf-8"))

    def test_bounded_runtime_and_detached_snapshots(self):
        runtime = MarginaliaInterpreter("note 65\nquote\n")
        def observer(state):
            state["margins"]["0"].append(99)
        output = io.StringIO()
        with redirect_stdout(output):
            runtime.run(max_steps=2, on_step=observer)
        self.assertEqual(output.getvalue(), "A")
        self.assertEqual(runtime.margins[0], [65])
        with self.assertRaisesRegex(RuntimeError, "exceeded 4 steps"):
            MarginaliaInterpreter("note 1\nwhile\nagain").run(max_steps=4)
        for invalid in (-1, True, 1.5):
            with self.assertRaises(ValueError):
                MarginaliaInterpreter("").run(max_steps=invalid)

    def test_loop_trace_preserves_execution_order(self):
        runtime = MarginaliaInterpreter("note 2\nwhile\ndoubt 1\nagain\n")
        states = []
        runtime.run(max_steps=7, on_step=states.append)
        self.assertEqual([s["executed"] for s in states], [0, 1, 2, 3, 2, 3])
        self.assertEqual(runtime.value(), 0)
        self.assertEqual(states[0]["margins"]["0"], [2])


if __name__ == "__main__":
    unittest.main()
