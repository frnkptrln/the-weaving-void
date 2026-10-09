# One surface, several intended readings

The earlier constructor selects sentences for one program. The joint constructor
accepts several public reader profiles and a target program for each, and requires
every selected sentence to satisfy all readers at the same position.

The crossing now has a second authored surface, [A light left behind](multiple_readers/joint_carrier.md).
The western reading still prints `GO`; the eastern reading still prints `NO`.
The keepers disagree, but the last act leaves a light for the next visitor.

## Reproduce the construction

From the repository root:

```bash
python3 -m weaves.subtext.joint \
  --reader west weaves/subtext/multiple_readers/west.json weaves/subtext/multiple_readers/west.mrg \
  --reader east weaves/subtext/multiple_readers/east.json weaves/subtext/multiple_readers/east.mrg \
  --bank weaves/subtext/multiple_readers/joint_bank.json
```

Add `--json` to reproduce [joint_witness.json](multiple_readers/joint_witness.json).
It records the chosen one-based bank indices, available candidates at each step,
unused and unmapped entries, the surface, and both extracted programs. `--output`
writes the result but refuses to overwrite any input, including symlink/hardlink
aliases. The constructor does not execute the target programs.

Read and run the new surface using the existing tools:

```bash
python3 -m weaves.subtext.reader weaves/subtext/multiple_readers/joint_carrier.md \
  --weave weaves/subtext/multiple_readers/west.json --output /tmp/west.mrg
python3 Marginalia/interpreter.py /tmp/west.mrg
```

Substitute `east.json` for the other reading. Existing carriers and profiles
are unchanged.

## What is solved

For a fixed set of readers, each bank sentence has a tuple of instructions: its
**joint signature**. Sentences are grouped by this tuple. Each target position
consumes the first unused matching bank index. A bank entry can appear only once;
authors may deliberately provide duplicate entries.

Under the current reader contract, one sentence yields one instruction per
reader. Targets must therefore have equal instruction counts. With fixed readers,
candidate groups do not overlap, so greedy selection is complete: it succeeds
exactly when every required signature has enough entries. No backtracking is
needed. Reading the bank costs O(B × R) reader operations and constructing the
surface costs O(T × R), excluding the lengths of the strings and big integers.

If a signature has `n` entries and is needed `k` times, it contributes
`n × (n−1) × … × (n−k+1)` index assignments. The joint example has **9,216**
assignments. This counts arrangements of bank indices, **not distinct stories**,
semantic adequacy, or equivalent traces. Reordering the bank can choose different
prose without changing either target program.

Failure identifies the first target position whose joint signature has no unused
candidate. It is a failure for these exact programs, profiles and finite bank;
it does not prove that another wording or another program with the same output
is impossible. Valid sentences unmapped under a reader are listed as incompatible
in the witness. Malformed sentences and malformed profiles are rejected.

## Check the boundary

```bash
python3 -m unittest weaves.subtext.test_joint -v
python3 -m unittest discover -s weaves/subtext -t .
```

Tests execute both traces, compare the assignment count with an exhaustive small
enumeration, reject individually feasible but jointly incompatible targets, check
bank consumption, and verify the CLI's input-preservation rule. Meaning remains
authored and judged by people; the constructor verifies the executable constraint.
