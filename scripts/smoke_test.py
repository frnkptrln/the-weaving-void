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
            "Entanglement bell",
            ["Entanglement/interpreter.py", "Entanglement/examples/bell_state_logic.ent"],
            "Q",
        ),
        (
            "Gastronomy hello",
            ["Gastronomy/interpreter.py", "Gastronomy/examples/hello_world.gstr"],
            "Hello World!\n",
        ),
        (
            "Clockwork fibonacci",
            ["Clockwork/interpreter.py", "Clockwork/examples/fibonacci.clk"],
            "0 1 1 2 3 5 8 13 21 34 \n",
        ),
        (
            "MandelMemory M",
            ["MandelMemory/interpreter.py", "MandelMemory/examples/hello_mdm.mdm"],
            "M",
        ),
        (
            "SFract S",
            ["SFract/interpreter.py", "SFract/examples/fibonacci_tree.frac"],
            "S",
        ),
        (
            "Marginalia self portrait",
            ["Marginalia/interpreter.py", "Marginalia/examples/self_portrait.mrg"],
            "Codex: I read, fold, verify.\n",
        ),
    ]

    for name, args, expected in exact_cases:
        expect_exact(name, args, expected)

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


if __name__ == "__main__":
    try:
        main()
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
