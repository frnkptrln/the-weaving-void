# Marginalia

*"I do not overwrite context; I leave a trace and test what survives compression."*

**Marginalia** is an esoteric programming language about annotated memory,
revision, and accountable output. A program does not assign values directly.
Instead, it writes notes into an infinite margin tape. The visible value of a
cell is the sum of its notes modulo 256.

Marginalia is meant as a small self-portrait of Codex as a coding agent:
context is gathered, uncertainty is recorded, traces are folded into compact
state, and output can be guarded by verification.

## Memory Model

Marginalia uses an infinite integer-addressed tape. Each address is a margin,
and each margin stores a stack of signed notes.

The current value is:

```text
sum(notes at current margin) mod 256
```

`fold` compresses the entire stack into one preserved value. This mirrors
context compaction: provenance is reduced, but the operational state remains.

## Commands

| Command | Action |
| :--- | :--- |
| `note N` | Add signed note `N` to the current margin. |
| `doubt N` | Add signed note `-N` to the current margin. |
| `right [N]` | Move focus right by `N` margins, default `1`. |
| `left [N]` | Move focus left by `N` margins, default `1`. |
| `fold` | Replace all notes at the current margin with the visible value. |
| `forget` | Clear the current margin. |
| `quote` | Output the current value as an ASCII character. |
| `echo` | Output the current value as an integer. |
| `listen` | Read one input character into the current margin. |
| `verify N` | Halt unless the current value equals `N` modulo 256. |
| `while` | Begin a loop while the current value is not zero. |
| `again` | End the current loop. |

Comments begin with `#`.

## Usage

```bash
python3 interpreter.py examples/self_portrait.mrg
```

## Example

```marginalia
# Output 'C' after two pieces of evidence and one correction.
note 70
doubt 3
fold
verify 67
quote
```

Marginalia is Turing-complete by the usual tape-and-loop construction: `note`,
`doubt`, `left`, `right`, `while`, and `again` can encode Brainfuck-style
computation, while `fold` and `verify` give the language its own character.

`examples/countdown_verified.mrg` shows this at work: evidence is folded
into a count of ten, spoken digit by digit, and the exhausted margin must
pass `verify 0` before the program may announce liftoff.
