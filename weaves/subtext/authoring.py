"""Plan sentence constraints, inspect a draft, or repair its executable reading.

The author supplies the meaning. These tools report visible sentence features
and check them against a target thread without executing that thread.
"""

from __future__ import annotations

import argparse
import json
import sys
from difflib import SequenceMatcher
from pathlib import Path

from weaves.subtext.reader import (
    DEFAULT_WEAVE, SENTENCE_BOUNDARY, WeaveError, load_weave, read_surface, words,
)
from weaves.subtext.weaver import ConstructionError, profile_operations, target_instructions


def plan_thread(source: str, profile: dict | None = None) -> list[dict]:
    """Describe each instruction's visible constraints without requiring a bank.

    Suggested shapes have a final word of at most sixteen letters. They are
    arithmetic possibilities, not a claim that suitable natural words exist.
    The full feasible word-count interval is reported separately.
    """
    profile = load_weave() if profile is None else profile
    supported = profile_operations(profile)
    target = target_instructions(source, supported)
    result = []
    for number, (line, instruction) in enumerate(target, start=1):
        parts = instruction.split()
        operand = int(parts[1]) if len(parts) == 2 else None
        initials = sorted(
            initial for initial, operation in profile["operations"].items()
            if operation["opcode"] == parts[0]
        )
        shapes = []
        if operand is not None:
            # Iterating tail lengths keeps planning bounded even for very
            # large integer targets; never enumerate the entire interval.
            for tail in range(1, 17):
                remainder = operand - tail
                if remainder >= 8 and remainder % 8 == 0:
                    shapes.append({"word_count": remainder // 8, "final_word_length": tail})
        result.append({
            "sentence_number": number,
            "source_line": line,
            "instruction": instruction,
            "initials": initials,
            "operand": operand,
            "word_count_range": [1, operand // 8] if operand is not None else None,
            "zero_letter_tail_possible": operand is not None and operand % 8 == 0,
            "suggested_shapes": shapes,
        })
    return result


def diagnose_surface(source: str, surface: str, profile: dict | None = None) -> dict:
    """Align a draft's extracted instructions with a target and report changes.

    Invalid sentences remain inspectable rows. Exact matching instruction
    blocks anchor alignment so a simple inserted sentence does not turn every
    later sentence into a spurious mismatch. Ambiguous repeated instructions
    use SequenceMatcher's deterministic order; this is not semantic alignment.
    """
    profile = load_weave() if profile is None else profile
    plan = plan_thread(source, profile)
    if not isinstance(surface, str):
        raise ConstructionError("surface must be a string")
    sentences = [part.strip() for part in SENTENCE_BOUNDARY.split(surface.strip()) if part.strip()]
    if len(plan) * max(1, len(sentences)) > 1_000_000:
        raise ConstructionError("draft comparison is limited to 1,000,000 instruction/sentence pairs")
    observations = []
    for number, sentence in enumerate(sentences, start=1):
        sentence_words = words(sentence)
        observed = {
            "initial": sentence_words[0][0].upper() if sentence_words else None,
            "word_count": len(sentence_words),
            "final_word_length": sum(c.isalpha() for c in sentence_words[-1]) if sentence_words else 0,
        }
        try:
            actual = read_surface(sentence, profile)[0].instruction
            error = None
        except WeaveError as exc:
            actual = None
            error = str(exc).replace("sentence 1 ", f"sentence {number} ", 1)
        observations.append({"sentence": sentence, "actual": actual, "error": error, "observed": observed})

    rows = []

    def add_row(target_index: int | None, surface_index: int | None):
        expected = plan[target_index] if target_index is not None else None
        actual = observations[surface_index] if surface_index is not None else None
        if expected is None:
            status = "extra"
        elif actual is None:
            status = "missing"
        elif expected["instruction"] == actual["actual"]:
            status = "match"
        else:
            status = "change"
        rows.append({
            "status": status,
            "source_line": expected["source_line"] if expected else None,
            "sentence_number": surface_index + 1 if surface_index is not None else None,
            "expected": expected["instruction"] if expected else None,
            "actual": actual["actual"] if actual else None,
            "sentence": actual["sentence"] if actual else None,
            "error": actual["error"] if actual else None,
            "observed": actual["observed"] if actual else None,
            "constraints": expected,
        })

    alignment = SequenceMatcher(
        a=[item["instruction"] for item in plan],
        b=[item["actual"] for item in observations],
        autojunk=False,
    )
    for tag, start_a, end_a, start_b, end_b in alignment.get_opcodes():
        if tag in {"equal", "replace"}:
            paired = min(end_a - start_a, end_b - start_b)
            for offset in range(paired):
                add_row(start_a + offset, start_b + offset)
            for index in range(start_a + paired, end_a):
                add_row(index, None)
            for index in range(start_b + paired, end_b):
                add_row(None, index)
        elif tag == "delete":
            for index in range(start_a, end_a):
                add_row(index, None)
        else:
            for index in range(start_b, end_b):
                add_row(None, index)
    return {
        "matches": all(row["status"] == "match" for row in rows),
        "expected_count": len(plan), "actual_count": len(sentences), "rows": rows,
    }


def constraint_text(item: dict) -> str:
    start = "start with " + "/".join(item["initials"])
    if item["operand"] is None:
        return start + "; sentence length is free; end with . ! or ?"
    shapes = " or ".join(
        f"{shape['word_count']} words + a {shape['final_word_length']}-letter final word"
        for shape in item["suggested_shapes"]
    )
    text = f"{start}; 8 * words + final letters = {item['operand']}; try {shapes}"
    if item["zero_letter_tail_possible"]:
        text += "; reader also permits a zero-letter Unicode numeric tail"
    return text


def format_plan(plan: list[dict]) -> str:
    lines = ["Sentence constraints (wording and meaning are supplied by the author):"]
    for item in plan:
        lines.append(f"{item['sentence_number']:02d} [target line {item['source_line']}] {item['instruction']}")
        lines.append("   " + constraint_text(item))
    lines.append("Shape suggestions use final words of 1-16 letters; longer tails may also fit.")
    return "\n".join(lines) + "\n"


def format_diagnosis(report: dict) -> str:
    lines = ["Thread matches." if report["matches"] else "Draft differs from the target thread."]
    for row in report["rows"]:
        location = f"sentence {row['sentence_number']}" if row["sentence_number"] else "missing sentence"
        target = f"target line {row['source_line']}" if row["source_line"] else "no target instruction"
        actual = row["actual"] or ("unreadable" if row["sentence"] else "absent")
        expected = row["expected"] or "none"
        lines.append(f"{row['status'].upper()} {location}, {target}: {actual} -> {expected}")
        if row["error"]:
            lines.append("   " + row["error"])
        if row["status"] == "change" and row["observed"]:
            observed = row["observed"]
            lines.append(
                f"   observed: initial {observed['initial']!r}, {observed['word_count']} words, "
                f"{observed['final_word_length']} final letters"
            )
        if row["status"] in {"missing", "change"}:
            lines.append("   " + constraint_text(row["constraints"]))
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("plan", "check", "repair"):
        command = commands.add_parser(name)
        command.add_argument("thread", type=Path)
        command.add_argument("--weave", type=Path, default=DEFAULT_WEAVE)
        if name != "plan":
            command.add_argument("surface", type=Path)
        if name == "repair":
            command.add_argument("--bank", type=Path, required=True)
            command.add_argument("--output", type=Path)
        else:
            command.add_argument("--json", action="store_true", help="emit a structured report")
    args = parser.parse_args()
    try:
        source = args.thread.read_text(encoding="utf-8")
        profile = json.loads(args.weave.read_text(encoding="utf-8"))
        if args.command == "plan":
            plan = plan_thread(source, profile)
            print(json.dumps(plan, indent=2) + "\n" if args.json else format_plan(plan), end="")
            return 0

        surface = args.surface.read_text(encoding="utf-8")
        if args.command == "check":
            report = diagnose_surface(source, surface, profile)
            print(json.dumps(report, indent=2) + "\n" if args.json else format_diagnosis(report), end="")
            return 0 if report["matches"] else 1

        from weaves.subtext.repair import repair_surface

        bank = json.loads(args.bank.read_text(encoding="utf-8"))
        result = repair_surface(source, surface, bank, profile)
        if args.output:
            inputs = (args.thread, args.surface, args.bank, args.weave)
            if any(
                args.output.resolve() == path.resolve()
                or (args.output.exists() and args.output.samefile(path))
                for path in inputs
            ):
                raise ConstructionError("output must not overwrite an authoring input")
            args.output.write_text(result["surface"], encoding="utf-8")
        else:
            print(result["surface"], end="")
        print(f"Repair: {result['cost']} sentence edit(s).", file=sys.stderr)
        for edit in result["edits"]:
            print(
                f"  {edit['kind']} sentence {edit['sentence_number']}, target line {edit['target_line']}: "
                f"{edit['before']!r} -> {edit['after']!r}", file=sys.stderr,
            )
        return 0
    except (OSError, UnicodeError, json.JSONDecodeError, WeaveError) as exc:
        print(f"Subtext authoring error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
