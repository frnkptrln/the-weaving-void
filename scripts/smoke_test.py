import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_command(args):
    result = subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    output = result.stdout + result.stderr
    return result.returncode, output


def expect_exact(name, args, expected):
    returncode, output = run_command(args)
    if returncode != 0:
        raise AssertionError(f"{name} exited with {returncode}:\n{output}")
    if output != expected:
        raise AssertionError(
            f"{name} output mismatch:\nexpected {expected!r}\nfound    {output!r}"
        )
    print(f"ok {name}")


def expect_contains(name, args, expected_parts):
    returncode, output = run_command(args)
    if returncode != 0:
        raise AssertionError(f"{name} exited with {returncode}:\n{output}")

    missing = [part for part in expected_parts if part not in output]
    if missing:
        raise AssertionError(f"{name} missing {missing!r} in output:\n{output}")
    print(f"ok {name}")


def main():
    exact_cases = [
        (
            "Vortex hello",
            ["Vortex/interpreter.py", "Vortex/examples/hello.vtx"],
            "Hello, World!\n",
        ),
        (
            "Vortex multiply",
            ["Vortex/interpreter.py", "Vortex/examples/multiply.vtx"],
            "A",
        ),
        (
            "Vortex alphabet",
            ["Vortex/interpreter.py", "Vortex/examples/alphabet.vtx"],
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        ),
        (
            "Distaff A",
            ["Distaff/interpreter.py", "Distaff/examples/weave_A.dstf"],
            "A",
        ),
        (
            "Distaff Void",
            ["Distaff/interpreter.py", "Distaff/examples/weave_void.dstf"],
            "Void",
        ),
        (
            "Distaff countdown",
            ["Distaff/interpreter.py", "Distaff/examples/weave_countdown.dstf"],
            "54321",
        ),
        (
            "Entanglement bell",
            ["Entanglement/interpreter.py", "Entanglement/examples/bell_state_logic.ent"],
            "Q",
        ),
        (
            "Entanglement twins",
            ["Entanglement/interpreter.py", "Entanglement/examples/twin_alphabet.ent"],
            "AaBbCc",
        ),
        (
            "Gastronomy hello",
            ["Gastronomy/interpreter.py", "Gastronomy/examples/hello_world.gstr"],
            "Hello World!\n",
        ),
        (
            "Gastronomy counting soup",
            ["Gastronomy/interpreter.py", "Gastronomy/examples/counting_soup.gstr"],
            "0123456789",
        ),
        (
            "Clockwork fibonacci",
            ["Clockwork/interpreter.py", "Clockwork/examples/fibonacci.clk"],
            "0 1 1 2 3 5 8 13 21 34 \n",
        ),
        (
            "Clockwork factorial",
            ["Clockwork/interpreter.py", "Clockwork/examples/factorial.clk"],
            "120\n",
        ),
        (
            "MandelMemory M",
            ["MandelMemory/interpreter.py", "MandelMemory/examples/hello_mdm.mdm"],
            "M",
        ),
        (
            "MandelMemory digits",
            ["MandelMemory/interpreter.py", "MandelMemory/examples/digits.mdm"],
            "0123456789",
        ),
        (
            "SFract S",
            ["SFract/interpreter.py", "SFract/examples/fibonacci_tree.frac"],
            "S",
        ),
        (
            "SFract grow",
            ["SFract/interpreter.py", "SFract/examples/grow.frac"],
            "GROW",
        ),
        (
            "SFract botanical sketch (silent)",
            ["SFract/interpreter.py", "SFract/examples/botanical_sketch.frac"],
            "",
        ),
        (
            "Marginalia self portrait",
            ["Marginalia/interpreter.py", "Marginalia/examples/self_portrait.mrg"],
            "Codex: I read, fold, verify.\n",
        ),
        (
            "Marginalia countdown",
            ["Marginalia/interpreter.py", "Marginalia/examples/countdown_verified.mrg"],
            "10 9 8 7 6 5 4 3 2 1 liftoff\n",
        ),
    ]

    for name, args, expected in exact_cases:
        expect_exact(name, args, expected)

    visualizer_cases = [
        (
            "Distaff visualizer",
            ["Distaff/visualizer.py", "Distaff/examples/weave_void.dstf"],
            ["C |-"],
        ),
        (
            "MandelMemory visualizer",
            ["MandelMemory/visualizer.py", "MandelMemory/examples/hello_mdm.mdm"],
            ["MandelMemory Map"],
        ),
        (
            "SFract visualizer",
            ["SFract/visualizer.py", "SFract/examples/botanical_sketch.frac"],
            ["SFract Growth Stages", "Botanical Sketch", "@"],
        ),
    ]

    for name, args, expected_parts in visualizer_cases:
        expect_contains(name, args, expected_parts)

    bloom_success = ["Status: emergent intelligence detected (non-maximizing)"]
    for filename in [
        "hello_emergence.blm",
        "kuramoto_homeostasis.blm",
        "love_as_constraint.blm",
        "fractal_subscale.blm",
    ]:
        expect_contains(
            f"Bloom {filename}",
            ["Bloom/interpreter.py", f"Bloom/examples/{filename}"],
            bloom_success,
        )

    expect_contains(
        "Bloom paperclip veto",
        ["Bloom/interpreter.py", "Bloom/examples/paperclip_veto.blm"],
        ["STATUS: Veto triggered (unbounded_growth). Substrate halted."],
    )

    expect_contains(
        "Bloom visualizer",
        ["Bloom/visualizer.py", "Bloom/examples/hello_emergence.blm"],
        ["Δ-Coherence Trajectory", *bloom_success],
    )

    expect_contains(
        "Bloom visualizer veto",
        ["Bloom/visualizer.py", "Bloom/examples/paperclip_veto.blm"],
        ["STATUS: Veto triggered (unbounded_growth). Substrate halted."],
    )


if __name__ == "__main__":
    try:
        main()
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
