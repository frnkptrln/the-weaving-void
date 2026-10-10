"""Build a self-contained reading room from the real reader and interpreter."""
from __future__ import annotations

import argparse
from contextlib import redirect_stdout
import hashlib
import io
import json
from pathlib import Path

from Marginalia.interpreter import MarginaliaInterpreter
from weaves.subtext.reader import load_weave, read_surface, words

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUTPUT = ROOT / "reading-room.html"
TEMPLATE = HERE / "explorer.html.in"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_data() -> dict:
    source = HERE / "multiple_readers/carrier.md"
    original = source.read_text(encoding="utf-8")
    variants = {
        "original": original,
        "reflow": "  \n\n" + "   \n".join(original.splitlines()) + "\n",
        "one-letter": original.replace("bearings.", "bearing."),
    }
    cases = {}
    for variant, surface in variants.items():
        for direction in ("west", "east"):
            profile_path = HERE / f"multiple_readers/{direction}.json"
            profile = load_weave(profile_path)
            readings = read_surface(surface, profile)
            program = "\n".join(r.instruction for r in readings) + "\n"
            stream = io.StringIO()
            states = [{"executed": None, "next": 0, "pointer": 0, "margins": {}, "output": ""}]
            def capture(state):
                states.append({**state, "output": stream.getvalue()})
            with redirect_stdout(stream):
                MarginaliaInterpreter(program).run(max_steps=1000, on_step=capture)
            if variant == "original":
                expected = (HERE / f"multiple_readers/{direction}.mrg").read_text(encoding="utf-8")
                if program != expected or stream.getvalue() != {"west": "GO", "east": "NO"}[direction]:
                    raise ValueError("canonical thread or trace no longer reproduces")
            cases[f"{variant}/{direction}"] = {
                "surface": surface, "profile": profile, "program": program, "states": states,
                "readings": [{"sentence": r.sentence, "initial": r.initial, "instruction": r.instruction,
                              "operand": r.operand, "word_count": len(words(r.sentence)),
                              "tail": words(r.sentence)[-1],
                              "tail_length": sum(c.isalpha() for c in words(r.sentence)[-1])} for r in readings],
                "witness": {"format": "subtext-reading-room/1", "variant": variant,
                            "source_path": str(source.relative_to(ROOT)), "source_sha256": digest(source.read_bytes()),
                            "profile_path": str(profile_path.relative_to(ROOT)), "profile_sha256": digest(profile_path.read_bytes()),
                            "surface_sha256": digest(surface.encode()), "program_sha256": digest(program.encode()),
                            "interpreter_sha256": digest((ROOT / "Marginalia/interpreter.py").read_bytes())},
            }
    return {"format": "subtext-reading-room/1", "cases": cases}


def build_html() -> str:
    payload = json.dumps(build_data(), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    # Text must never close the data element, even if a future authored surface does.
    return TEMPLATE.read_text(encoding="utf-8").replace("__WEAVE_DATA__", payload.replace("<", "\\u003c"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if the committed page is stale")
    args = parser.parse_args()
    page = build_html()
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_bytes() != page.encode("utf-8"):
            parser.exit(1, "reading-room.html is stale; run python -m weaves.subtext.explorer\n")
        print("reading-room.html reproduces exactly")
    else:
        OUTPUT.write_text(page, encoding="utf-8")
        print(OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
