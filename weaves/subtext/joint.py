"""Construct one authored surface against several public readers at once.

Each sentence has one instruction signature across the readers. Matching those
signatures is finite selection, not semantic generation or a search over readers.
No target program is executed by the constructor.
"""
from __future__ import annotations

import argparse
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import sys

from weaves.subtext.reader import WeaveError, extract_program, read_surface, split_sentences, words
from weaves.subtext.weaver import ConstructionError, profile_operations, target_instructions


@dataclass(frozen=True)
class JointConstruction:
    surface: str
    readers: tuple[str, ...]
    selected_bank_entries: tuple[int, ...]
    available_at_selection: tuple[int, ...]
    assignment_count: int
    unused_bank_entries: tuple[int, ...]
    incompatible_bank_entries: tuple[int, ...]
    programs: dict[str, str]


def weave_readers(targets: dict[str, str], bank: list[str], profiles: dict[str, dict]) -> JointConstruction:
    """Return a verified carrier and a witness of finite sentence selection.

    Every bank index can be used at most once. Within a signature, bank order
    breaks ties. ``assignment_count`` counts index assignments, not distinct
    prose surfaces: two identically worded bank entries are distinct indices.
    """
    if not isinstance(targets, dict) or not targets or any(
        not isinstance(name, str) or not name.strip() for name in targets
    ):
        raise ConstructionError("targets must be a nonempty object of named threads")
    if not isinstance(profiles, dict) or set(profiles) != set(targets):
        raise ConstructionError("profiles and target threads must have exactly the same reader names")
    names = tuple(sorted(targets))
    instructions = {}
    for name in names:
        try:
            instructions[name] = target_instructions(targets[name], profile_operations(profiles[name]))
        except WeaveError as exc:
            raise ConstructionError(f"reader {name!r}: {exc}") from exc
    lengths = {len(items) for items in instructions.values()}
    if len(lengths) != 1:
        raise ConstructionError("all targets need the same instruction count: one sentence is one instruction per reader")
    if not isinstance(bank, list) or not bank:
        raise ConstructionError("sentence bank must be a nonempty JSON array of strings")

    candidates = defaultdict(deque)
    incompatible = []
    for index, sentence in enumerate(bank, start=1):
        if not isinstance(sentence, str):
            raise ConstructionError(f"bank entry {index} must be a sentence string")
        sentence = " ".join(sentence.split())
        try:
            parts = split_sentences(sentence)
            if len(parts) != 1 or not words(sentence):
                raise WeaveError("must contain exactly one sentence with words")
        except WeaveError as exc:
            raise ConstructionError(f"bank entry {index}: {exc}") from exc
        try:
            signature = tuple(read_surface(sentence, profiles[name])[0].instruction for name in names)
        except WeaveError:
            # A valid authored sentence can lack a mapping under one reader.
            # It cannot satisfy a joint target, but must remain visible in the witness.
            incompatible.append(index)
            continue
        candidates[signature].append((index, sentence))

    selected, indices, choices = [], [], []
    assignment_count = 1
    for position in range(next(iter(lengths))):
        signature = tuple(instructions[name][position][1] for name in names)
        pool = candidates[signature]
        if not pool:
            detail = ", ".join(f"{name}={instruction!r}" for name, instruction in zip(names, signature))
            raise ConstructionError(f"sentence {position + 1}: no unused bank entry satisfies all readers ({detail})")
        choices.append(len(pool))
        assignment_count *= len(pool)
        index, sentence = pool.popleft()
        selected.append(sentence)
        indices.append(index)
    surface = "\n".join(selected) + "\n"
    programs = {name: "\n".join(instruction for _, instruction in instructions[name]) + "\n" for name in names}
    for name in names:
        if extract_program(surface, profiles[name]) != programs[name]:
            raise ConstructionError(f"constructed surface does not round-trip under reader {name!r}")
    used = set(indices)
    return JointConstruction(
        surface, names, tuple(indices), tuple(choices), assignment_count,
        tuple(index for index in range(1, len(bank) + 1) if index not in used),
        tuple(incompatible), programs,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reader", nargs=3, action="append", required=True, metavar=("NAME", "PROFILE", "THREAD"))
    parser.add_argument("--bank", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json", action="store_true", help="emit the selection witness, including surface and all extracted threads")
    args = parser.parse_args(argv)
    try:
        targets, profiles = {}, {}
        inputs = [args.bank]
        for name, profile_path, thread_path in args.reader:
            if name in targets:
                raise ConstructionError(f"duplicate reader name: {name!r}")
            profile_file, thread_file = Path(profile_path), Path(thread_path)
            inputs.extend((profile_file, thread_file))
            profiles[name] = json.loads(profile_file.read_text(encoding="utf-8"))
            targets[name] = thread_file.read_text(encoding="utf-8")
        result = weave_readers(targets, json.loads(args.bank.read_text(encoding="utf-8")), profiles)
        output = json.dumps(asdict(result), ensure_ascii=False, indent=2) + "\n" if args.json else result.surface
        if args.output:
            if any(args.output.resolve() == source.resolve() or
                   (args.output.exists() and args.output.samefile(source)) for source in inputs):
                raise ConstructionError("output must not overwrite a construction input")
            args.output.write_text(output, encoding="utf-8")
        else:
            print(output, end="")
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"Subtext joint construction error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
