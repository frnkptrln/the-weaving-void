"""Extract a Marginalia program from a Subtext carrier.

The reader intentionally uses only visible, auditable sentence features. It is
not a steganographic security mechanism.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


HERE = Path(__file__).resolve().parent
DEFAULT_WEAVE = HERE / "weave.json"
WORD_PATTERN = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*", re.UNICODE)
SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])\s+")


class WeaveError(ValueError):
    """Raised when a surface cannot be read by the selected weave."""


@dataclass(frozen=True)
class Reading:
    sentence_number: int
    sentence: str
    initial: str
    opcode: str
    operand: int | None

    @property
    def instruction(self) -> str:
        if self.operand is None:
            return self.opcode
        return f"{self.opcode} {self.operand}"


def load_weave(path: Path = DEFAULT_WEAVE) -> dict:
    profile = json.loads(path.read_text(encoding="utf-8"))
    if profile.get("operand_encoding", {}).get("kind") != "octet-words-plus-tail":
        raise WeaveError("unsupported operand encoding")
    if not profile.get("operations"):
        raise WeaveError("weave defines no operations")
    return profile


def split_sentences(surface: str) -> list[str]:
    compact = surface.strip()
    if not compact:
        raise WeaveError("surface is empty")
    sentences = [part.strip() for part in SENTENCE_BOUNDARY.split(compact) if part.strip()]
    for number, sentence in enumerate(sentences, start=1):
        if sentence[-1] not in ".!?":
            raise WeaveError(f"sentence {number} has no terminal punctuation")
    return sentences


def words(sentence: str) -> list[str]:
    return WORD_PATTERN.findall(sentence)


def encoded_operand(sentence: str) -> int:
    sentence_words = words(sentence)
    if not sentence_words:
        raise WeaveError("sentence contains no words")
    final_word_length = sum(character.isalpha() for character in sentence_words[-1])
    return 8 * len(sentence_words) + final_word_length


def read_surface(surface: str, profile: dict | None = None) -> list[Reading]:
    profile = profile or load_weave()
    operations = profile["operations"]
    readings: list[Reading] = []

    for number, sentence in enumerate(split_sentences(surface), start=1):
        sentence_words = words(sentence)
        if not sentence_words:
            raise WeaveError(f"sentence {number} contains no words")
        initial = sentence_words[0][0].upper()
        operation = operations.get(initial)
        if operation is None:
            raise WeaveError(
                f"sentence {number} begins with unmapped initial {initial!r}"
            )
        operand = encoded_operand(sentence) if operation["operand"] else None
        readings.append(
            Reading(number, sentence, initial, operation["opcode"], operand)
        )

    return readings


def extract_program(surface: str, profile: dict | None = None) -> str:
    return "\n".join(reading.instruction for reading in read_surface(surface, profile)) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("surface", type=Path, help="human-readable carrier")
    parser.add_argument("--weave", type=Path, default=DEFAULT_WEAVE)
    parser.add_argument("--output", type=Path, help="write the extracted thread")
    parser.add_argument("--explain", action="store_true", help="show sentence mappings")
    args = parser.parse_args()

    try:
        surface = args.surface.read_text(encoding="utf-8")
        profile = load_weave(args.weave)
        readings = read_surface(surface, profile)
        program = "\n".join(item.instruction for item in readings) + "\n"
    except (OSError, json.JSONDecodeError, WeaveError) as exc:
        print(f"Subtext error: {exc}", file=sys.stderr)
        return 1

    if args.explain:
        for item in readings:
            print(
                f"{item.sentence_number:02d} {item.initial} -> {item.instruction:<12} | "
                f"{item.sentence}",
                file=sys.stderr,
            )

    if args.output:
        args.output.write_text(program, encoding="utf-8")
    else:
        print(program, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
