# Subtext

Subtext is the first canonical weave in `the-weaving-void`: ordinary visible
prose carries an executable Marginalia thread.

Subtext is not a separate virtual machine. The committed `weave.json` is a
public reader profile, `reader.py` performs deterministic extraction, and the
existing Marginalia interpreter remains the loom.

## Reading rule

Each sentence participates in both readings:

1. Its first letter selects a Marginalia opcode.
2. Operations that require an argument encode it as
   `8 * word_count + final_word_length`.
3. Sentence-ending punctuation defines the extraction boundary.

The current operation initials are:

| Initial | Marginalia operation |
| :--- | :--- |
| `N` | `note N` |
| `D` | `doubt N` |
| `R` / `L` | `right N` / `left N` |
| `F` | `fold` |
| `X` | `forget` |
| `Q` | `quote` |
| `E` | `echo` |
| `V` | `verify N` |
| `W` / `A` | `while` / `again` |

Every sentence must begin with a mapped initial. Unknown initials are errors;
the reader does not silently discard prose.

## Reproduce the specimen

```bash
python3 weaves/subtext/reader.py weaves/subtext/carrier.md
python3 weaves/subtext/reader.py weaves/subtext/carrier.md --explain
python3 Marginalia/interpreter.py weaves/subtext/extracted.mrg
python3 -m unittest weaves.subtext.test_reader
```

The extracted thread is committed as `extracted.mrg`; its expected execution
trace is committed as `trace.txt`. Tests cover the canonical extraction,
execution, whitespace invariance, shape-preserving substitution, structural
mutation, and rejection of unmapped sentences.

## Construct a carrier from a target thread

The inverse helper selects sentences from a UTF-8 JSON array of authored
strings. Each entry must be exactly one valid Subtext sentence, including
terminal punctuation. All entries are checked, even unused alternatives.

```bash
python3 -m weaves.subtext.weaver weaves/subtext/construction/target.mrg --bank weaves/subtext/construction/sentences.json
# Optionally save the resulting surface:
python3 -m weaves.subtext.weaver weaves/subtext/construction/target.mrg --bank weaves/subtext/construction/sentences.json --output /tmp/subtext-carrier.md
python3 -m weaves.subtext.reader /tmp/subtext-carrier.md --explain
```

For each instruction, selection uses the first unused matching entry in bank
order. Repeated instructions need multiple entries; identical sentence strings
may appear at different indices. The result contains one sentence per line,
with internal whitespace reflowed. A final extraction checks the entire target
before the CLI emits or saves a carrier. A failed construction leaves an
existing output file untouched.

Targets use mapped Marginalia operations. Comments, blank lines, opcode case,
whitespace, and integer spelling are normalized; instruction order and values
are preserved. Every argument-taking operation needs an explicit integer,
including `right` and `left`. This profile's smallest sentence operand is 9
(`8 * 1 + 1`), so smaller and negative values cannot be carried by one sentence.
The helper reports these limits and missing candidates with target line
numbers. It does not substitute a different program with equivalent behavior.

Loop pairing is checked without executing the target. A successful construction
does not guarantee termination or successful runtime verification. Execute
trusted specimens separately with the Marginalia loom. `--weave` accepts an
alternative profile using the same sentence and operand rules and compatible
Marginalia operation mappings.

The [second specimen](construction) contains a bank, target, constructed garden
story, and expected trace. Tests check exact reconstruction, alternate bank
ordering, thread/trace equivalence, and construction failures:

```bash
python3 -m unittest discover -s weaves/subtext -t .
```

## Write, inspect, and repair

The [authoring workflow](AUTHORING.md) extends construction beyond selecting
an entire surface from a bank. It describes sentence shapes for each target
instruction, compares a draft with that target, and proposes a repair that
minimizes sentence edits within supplied candidates. The committed garden
draft demonstrates a one-word structural mutation and its repair.

The [multiple-reader specimen](multiple_readers) asks a complementary question:
how can one unchanged surface carry two executable threads? Two public
profiles route the same story through different Marginalia margins, producing
`GO` and `NO`.

## Epistemic boundary

This specimen demonstrates deterministic dual reading. It does not demonstrate
secrecy, semantic understanding, or a unique hidden interpretation. The weave
is intentionally public and inspectable.

The construction helper searches a finite bank supplied by an author. It does
not evaluate meaning or readability. A structurally valid combination still
needs a human reading; the garden story is a curated example, not evidence of
general semantic construction.
