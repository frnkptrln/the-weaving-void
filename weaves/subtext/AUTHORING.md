# Authoring a Subtext surface

An author can start with a target thread, draft prose, inspect the visible
constraints, and propose repairs. The tools check executable structure. They
do not score the meaning of a sentence or decide whether a revised story works.
Run the commands below from the repository root.

## Plan before writing

```bash
python3 -m weaves.subtext.authoring plan weaves/subtext/construction/target.mrg
```

For `note 86`, the default profile requires initial `N` and
`8 * word_count + final_word_length = 86`. Suggested shapes include ten words
with a six-letter final word, or nine words with a fourteen-letter final word.
The author chooses the wording. No bank is required for planning.

The full arithmetic word-count interval is available in `--json` output.
Displayed suggestions limit the final word to sixteen letters; a larger tail
can still be valid. A shape is an arithmetic possibility, not a promise that
natural wording exists. Non-operand instructions constrain the initial and
sentence boundary while leaving sentence length free.

Words and final letters use the existing reader's rules. Letter words may
include apostrophes, which do not count as letters in the final word. The
reader also counts some visible Unicode numeric tokens such as `²` as words,
although they contain zero alphabetic letters: `Now ².` extracts `note 16`.
The full word-count range includes this zero-letter-tail case; a separate
`zero_letter_tail_possible` flag identifies it. Positive-tail suggestions
remain oriented toward ordinary prose. This describes the existing reader;
the authoring tools do not change its tokenization.
Sentence boundaries remain `.`, `!`, or `?` followed by whitespace. This small
grammar does not parse abbreviations or infer a missing sentence boundary.

## Inspect a draft

```bash
python3 -m weaves.subtext.authoring check weaves/subtext/construction/target.mrg weaves/subtext/construction/draft.md
```

This draft changes the garden story's first final word from `spaces` to
`paths`. The report shows ten words and five final letters: `note 85`, where
the target asks for `note 86`. The other ten instructions still match.

Reports distinguish matching, changed, missing, and extra sentences. Exact
instruction blocks anchor comparison, so an inserted sentence need not make
every following sentence appear wrong. An unmapped initial or missing terminal
punctuation is reported at the affected sentence. Repeated instructions can
make alignment ambiguous; the reported alignment is deterministic and does
not identify intended narrative correspondence.

`check` exits with 0 for an exact thread match, 1 for a draft mismatch, and 2
for invalid target/profile inputs or file errors. `--json` returns the same
diagnosis with source line numbers, actual sentence features, and expected
constraints for use in other tools.

## Propose a repair

```bash
python3 -m weaves.subtext.authoring repair weaves/subtext/construction/target.mrg weaves/subtext/construction/draft.md --bank weaves/subtext/construction/sentences.json --output /tmp/subtext-repaired.md
python3 -m weaves.subtext.authoring check weaves/subtext/construction/target.mrg /tmp/subtext-repaired.md
```

The example restores `spaces`, reproducing the committed `carrier.md`. Repair
preserves matching sentences and can replace, insert, or delete sentences to
reach the target. Every inserted or replacement sentence comes from the
authored bank. The complete result must extract to the target exactly before
it is emitted. The CLI writes the proposed carrier to stdout or `--output`
and explains each sentence edit on stderr. Input files cannot be overwritten
through `--output`; a failed repair leaves an existing output file untouched.

Repair minimizes sentence edits first: replacement, insertion, and deletion
each cost one, while preserving a matching sentence costs zero. Among equal
sentence-edit counts it minimizes the sum of case-sensitive word-token edit
distances. For each insertion or replacement, bank order settles equally close
candidates. Equally scoring alignments prefer keep, replace, insert, then
delete at the earliest differing step. These metrics measure surface changes,
not semantic distance or quality.

Unlike construction's consume-once bank, repair may reuse a candidate at
multiple positions. An empty bank can suffice when all required sentences are
already present and only deletions are needed. Every supplied bank entry is
validated, even when it is unused. Repair fails if the available sentences
cannot supply the target. The dynamic-programming comparison is bounded;
oversized inputs receive an explicit error instead of an unbounded search.

Planning, diagnosis, and repair never execute the target. Loop pairing is
checked, but successful extraction does not establish termination or runtime
verification. The Marginalia loom remains a separate step.

## Read the result again

Inspect whether the revised surface still expresses the intended meaning.
Especially for insertions, deletions, or a reused candidate, exact executable
agreement can coexist with poor prose. Edit the candidate bank or write a new
sentence and repeat the check. A successful construction is one inspectable
answer under supplied constraints, not a unique recovery of an author or
generator.
