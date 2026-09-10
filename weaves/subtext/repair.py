"""Repair a carrier by selecting finite, authored sentence alternatives.

The primary cost is the number of sentence insertions, replacements and
deletions. Ties minimize total case-sensitive word-token edit distance, then
use bank order and a stable alignment order (keep, replace, insert, delete).
Unlike ``weave_thread``, repair may reuse a bank entry at multiple locations.
It neither writes new prose nor executes the target program.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from functools import lru_cache

from weaves.subtext.reader import (
    SENTENCE_BOUNDARY,
    WeaveError,
    extract_program,
    load_weave,
    read_surface,
    words,
)
from weaves.subtext.weaver import (
    ConstructionError,
    profile_operations,
    target_instructions,
)


# Keep alignment memory and the aggregate word-comparison work bounded. These
# are explicit input limits, rather than a timeout returning a partial repair.
MAX_ALIGNMENT_CELLS = 250_000
MAX_TOKEN_COMPARISON_CELLS = 5_000_000


@dataclass(frozen=True)
class _Candidate:
    index: int
    sentence: str
    tokens: tuple[str, ...]


def _validated_bank(bank: list[str], profile: dict) -> dict[str, list[_Candidate]]:
    if not isinstance(bank, list):
        raise ConstructionError("sentence bank must be a JSON array of strings")
    candidates = defaultdict(list)
    for index, entry in enumerate(bank, start=1):
        if not isinstance(entry, str):
            raise ConstructionError(f"bank entry {index} must be a sentence string")
        # Match the constructor's whitespace treatment for authored candidates.
        sentence = " ".join(entry.split())
        try:
            readings = read_surface(sentence, profile)
        except WeaveError as exc:
            raise ConstructionError(f"bank entry {index}: {exc}") from exc
        if len(readings) != 1:
            raise ConstructionError(f"bank entry {index} must contain exactly one sentence")
        candidates[readings[0].instruction].append(
            _Candidate(index, sentence, tuple(words(sentence)))
        )
    return dict(candidates)


def _token_distance(before: tuple[str, ...], after: tuple[str, ...]) -> int:
    """Levenshtein distance with linear working memory, including empty text."""
    if len(before) < len(after):
        before, after = after, before
    row = list(range(len(after) + 1))
    for i, first in enumerate(before, start=1):
        next_row = [i]
        for j, second in enumerate(after, start=1):
            next_row.append(min(
                row[j] + 1,
                next_row[j - 1] + 1,
                row[j - 1] + (first != second),
            ))
        row = next_row
    return row[-1]


def repair_surface(
    source: str,
    surface: str,
    bank: list[str],
    profile: dict | None = None,
) -> dict:
    """Return ``surface``, ``changed``, ``edits`` and sentence-edit ``cost``.

    Existing sentences that already encode the aligned target instruction are
    preserved verbatim apart from outer whitespace. Sentence boundaries are
    joined with newlines; this formatting alone does not count as a change.
    Invalid existing sentences can be replaced or deleted, and an empty
    surface can be constructed. Every bank entry must be a valid single
    sentence, including entries that will not be used. An empty bank is useful
    when preservation and deletion suffice. Failure returns no partial result.

    Edit coordinates refer to the original surface and the actual target
    source lines. Insertions have no original sentence number; deletions have
    no target line or expected instruction. ``before``/``after`` are ``None``
    on the missing side of an insertion/deletion.
    """
    profile = load_weave() if profile is None else profile
    target = target_instructions(source, profile_operations(profile))
    candidates = _validated_bank(bank, profile)
    if not isinstance(surface, str):
        raise ConstructionError("surface must be a string")
    sentences = [
        part.strip() for part in SENTENCE_BOUNDARY.split(surface.strip())
        if part.strip()
    ]
    sentence_count, target_count = len(sentences), len(target)
    if (sentence_count + 1) * (target_count + 1) > MAX_ALIGNMENT_CELLS:
        raise ConstructionError(
            f"repair alignment is too large (limit {MAX_ALIGNMENT_CELLS} cells); "
            "repair a smaller passage"
        )

    instructions: list[str | None] = []
    for sentence in sentences:
        try:
            instructions.append(read_surface(sentence, profile)[0].instruction)
        except WeaveError:
            instructions.append(None)
    sentence_tokens = [tuple(words(sentence)) for sentence in sentences]
    remaining_comparisons = MAX_TOKEN_COMPARISON_CELLS

    @lru_cache(maxsize=None)
    def distance(before: tuple[str, ...], after: tuple[str, ...]) -> int:
        nonlocal remaining_comparisons
        if not before or not after:
            return len(before) + len(after)
        if before == after:
            return 0
        remaining_comparisons -= len(before) * len(after)
        if remaining_comparisons < 0:
            raise ConstructionError(
                "repair token comparison is too large; use a smaller passage "
                "or sentence bank"
            )
        return _token_distance(before, after)

    @lru_cache(maxsize=None)
    def best_candidate(position: int | None, instruction: str) -> tuple[_Candidate, int]:
        before = () if position is None else sentence_tokens[position]
        scored = [
            (distance(before, candidate.tokens), candidate.index, candidate)
            for candidate in candidates[instruction]
        ]
        token_cost, _, candidate = min(scored, key=lambda item: item[:2])
        return candidate, token_cost

    # Suffix alignment makes a tie preserve the earliest already-matching
    # sentence. Each state stores an additive (sentence edits, token edits)
    # score and one backpointer; no full paths are copied into the matrix.
    scores = [[None] * (target_count + 1) for _ in range(sentence_count + 1)]
    steps = [[None] * (target_count + 1) for _ in range(sentence_count + 1)]
    scores[sentence_count][target_count] = (0, 0)
    for i in range(sentence_count, -1, -1):
        for j in range(target_count, -1, -1):
            if i == sentence_count and j == target_count:
                continue
            options = []

            def offer(next_score, kind, after, token_cost, order):
                if next_score is not None:
                    score = (
                        next_score[0] + (kind != "keep"),
                        next_score[1] + token_cost,
                    )
                    options.append((score, order, kind, after))

            if i < sentence_count and j < target_count:
                instruction = target[j][1]
                following = scores[i + 1][j + 1]
                if instructions[i] == instruction:
                    offer(following, "keep", sentences[i], 0, 0)
                elif following is not None and instruction in candidates:
                    candidate, token_cost = best_candidate(i, instruction)
                    offer(following, "replace", candidate.sentence, token_cost, 1)
            if j < target_count and scores[i][j + 1] is not None:
                instruction = target[j][1]
                if instruction in candidates:
                    candidate, token_cost = best_candidate(None, instruction)
                    offer(scores[i][j + 1], "insert", candidate.sentence, token_cost, 2)
            if i < sentence_count:
                offer(scores[i + 1][j], "delete", None, len(sentence_tokens[i]), 3)
            if options:
                score, _, kind, after = min(options, key=lambda item: item[:2])
                scores[i][j] = score
                steps[i][j] = (kind, after)

    if scores[0][0] is None:
        # Bank-covered instructions can always be inserted. The rest must
        # occur in order in the existing surface; earliest matches leave the
        # most room for subsequent requirements. Report the first real
        # order/count deficit, rather than already-preservable instructions.
        position = 0
        for line, instruction in target:
            if instruction in candidates:
                continue
            while position < sentence_count and instructions[position] != instruction:
                position += 1
            if position == sentence_count:
                raise ConstructionError(
                    f"line {line}: no remaining surface sentence encodes "
                    f"{instruction!r} in the required order, and no bank sentence "
                    "matches; add a matching authored sentence"
                )
            position += 1
        raise ConstructionError("repair could not find a complete alignment")

    repaired = []
    edits = []
    i = j = 0
    while i < sentence_count or j < target_count:
        kind, after = steps[i][j]
        if kind != "keep":
            edits.append({
                "kind": kind,
                "sentence_number": None if kind == "insert" else i + 1,
                "target_line": None if kind == "delete" else target[j][0],
                "before": None if kind == "insert" else sentences[i],
                "after": after,
                "expected_instruction": None if kind == "delete" else target[j][1],
            })
        if kind != "delete":
            repaired.append(after)
            j += 1
        if kind != "insert":
            i += 1

    result = "\n".join(repaired) + "\n"
    expected = "\n".join(instruction for _, instruction in target) + "\n"
    if extract_program(result, profile) != expected:
        raise ConstructionError("repaired surface does not round-trip to the target")
    cost = scores[0][0][0]
    return {"surface": result, "changed": cost > 0, "edits": edits, "cost": cost}
