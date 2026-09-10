"""Construct a Subtext carrier for a target thread from authored sentences.

This is finite sentence selection, not natural-language generation: authors
supply both the wording and its intended meaning. No target program is run.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict, deque
from pathlib import Path

from Marginalia.interpreter import MarginaliaInterpreter
from weaves.subtext.reader import (
    DEFAULT_WEAVE,
    WeaveError,
    extract_program,
    load_weave,
    read_surface,
)


class ConstructionError(WeaveError):
    """The target or sentence bank cannot produce the requested carrier."""


# Operations available to a sentence-shaped Marginalia thread. Explicit
# operands are required: a default step or a modulo-equivalent instruction
# would not be the same extracted thread.
OPERANDS = {
    "note": True, "doubt": True, "right": True, "left": True,
    "verify": True, "fold": False, "forget": False, "quote": False,
    "echo": False, "while": False, "again": False, "listen": False,
}


def profile_operations(profile: dict) -> set[str]:
    """Check that the profile describes the supported reader and loom."""
    if not isinstance(profile, dict):
        raise ConstructionError("weave profile must be an object")
    encoding = profile.get("operand_encoding")
    if (not isinstance(encoding, dict)
            or encoding.get("kind") != "octet-words-plus-tail"):
        raise ConstructionError("unsupported operand encoding")
    if profile.get("loom") != "Marginalia":
        raise ConstructionError("construction requires the Marginalia loom")
    if profile.get("sentence_split") != "terminal-punctuation":
        raise ConstructionError("unsupported sentence splitting rule")
    operations = profile.get("operations")
    if not isinstance(operations, dict) or not operations:
        raise ConstructionError("weave defines no operations")
    supported = set()
    for initial, operation in operations.items():
        if (not isinstance(initial, str) or len(initial) != 1
                or not initial.isalpha() or initial.upper() != initial
                or not isinstance(operation, dict)):
            raise ConstructionError("invalid operation mapping in weave profile")
        opcode = operation.get("opcode")
        if (not isinstance(opcode, str) or opcode not in OPERANDS
                or operation.get("operand") is not OPERANDS[opcode]):
            raise ConstructionError(f"unsupported operation mapping for {initial!r}")
        supported.add(opcode)
    return supported


def target_instructions(source: str, supported: set[str]) -> list[tuple[int, str]]:
    """Normalize instructions and validate syntax, including loop pairing."""
    if not isinstance(source, str):
        raise ConstructionError("target thread must be a string")
    try:
        loom = MarginaliaInterpreter(source)
    except (SyntaxError, ValueError) as exc:
        raise ConstructionError(str(exc)) from exc
    if not loom.instructions:
        raise ConstructionError("target thread is empty")
    instructions = []
    for opcode, args, line in loom.instructions:
        if opcode not in supported:
            raise ConstructionError(
                f"line {line}: operation {opcode!r} has no mapping in this weave"
            )
        arity = int(OPERANDS[opcode])
        if len(args) != arity:
            raise ConstructionError(
                f"line {line}: {opcode!r} requires {arity} explicit operand(s)"
            )
        instruction = opcode
        if arity:
            try:
                value = int(args[0])
            except ValueError as exc:
                raise ConstructionError(
                    f"line {line}: {opcode!r} requires an integer operand accepted by Marginalia"
                ) from exc
            if value < 9:
                raise ConstructionError(
                    f"line {line}: {opcode} {value} is not representable by one sentence; "
                    "8 * word_count + final_word_length is at least 9"
                )
            instruction += f" {value}"
        instructions.append((line, instruction))
    return instructions


def weave_thread(source: str, bank: list[str], profile: dict | None = None) -> str:
    """Choose the first unused matching bank entry for each target instruction.

Entries are consumed by index; repeated instructions need repeated candidate
entries. A successful result extracts to the normalized target exactly.
"""
    profile = load_weave() if profile is None else profile
    supported = profile_operations(profile)
    target = target_instructions(source, supported)
    if not isinstance(bank, list) or not bank:
        raise ConstructionError("sentence bank must be a nonempty JSON array of strings")

    candidates = defaultdict(deque)
    for index, sentence in enumerate(bank, start=1):
        if not isinstance(sentence, str):
            raise ConstructionError(f"bank entry {index} must be a sentence string")
        # Reflow whitespace only. Wording and visible punctuation come from
        # the authored bank; no extra payload is added to satisfy the target.
        sentence = " ".join(sentence.split())
        try:
            readings = read_surface(sentence, profile)
        except WeaveError as exc:
            raise ConstructionError(f"bank entry {index}: {exc}") from exc
        if len(readings) != 1:
            raise ConstructionError(f"bank entry {index} must contain exactly one sentence")
        candidates[readings[0].instruction].append(sentence)

    selected = []
    for line, instruction in target:
        if not candidates[instruction]:
            raise ConstructionError(
                f"line {line}: no unused bank sentence encodes {instruction!r}; "
                "add a matching sentence or revise the target"
            )
        selected.append(candidates[instruction].popleft())

    surface = "\n".join(selected) + "\n"
    expected = "\n".join(instruction for _, instruction in target) + "\n"
    if extract_program(surface, profile) != expected:
        raise ConstructionError("constructed surface does not round-trip to the target")
    return surface


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("thread", type=Path, help="target Marginalia program")
    parser.add_argument("--bank", type=Path, required=True, help="JSON array of authored sentences")
    parser.add_argument("--weave", type=Path, default=DEFAULT_WEAVE)
    parser.add_argument("--output", type=Path, help="write the constructed carrier")
    args = parser.parse_args()

    try:
        source = args.thread.read_text(encoding="utf-8")
        bank = json.loads(args.bank.read_text(encoding="utf-8"))
        # Validate here as well as through the library API so malformed JSON
        # profiles produce a normal construction error rather than a traceback.
        profile = json.loads(args.weave.read_text(encoding="utf-8"))
        surface = weave_thread(source, bank, profile)
        if args.output:
            if args.output.resolve() in {
                args.thread.resolve(), args.bank.resolve(), args.weave.resolve()
            }:
                raise ConstructionError("output must not overwrite a construction input")
            args.output.write_text(surface, encoding="utf-8")
        else:
            print(surface, end="")
    except (OSError, UnicodeError, json.JSONDecodeError, WeaveError) as exc:
        print(f"Subtext construction error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
