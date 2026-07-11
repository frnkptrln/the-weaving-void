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

## Epistemic boundary

This specimen demonstrates deterministic dual reading. It does not demonstrate
secrecy, semantic understanding, or a unique hidden interpretation. The weave
is intentionally public and inspectable.
