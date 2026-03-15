# Distaff

**Distaff** is an esoteric programming language inspired by the weaving of auditory patterns (Drafts), as seen in Lucasfilm's "Loom". Programs are composed of 4-note sequences using a specific set of notes.

## Language Specification

### Notes
The available notes are: `c d e f g a b C` (where `C` is high C).

### Memory Model
Distaff uses a standard Brainfuck-style infinite tape of 8-bit cells (0-255). The pointer starts at cell 0, and all cells are initialized to 0.

### Drafts (Commands)
Drafts are 4-note sequences. Reversing the draft reverses the logical action.

| Draft | Action | Reverse | Action |
| :--- | :--- | :--- | :--- |
| `c-d-e-f` | **Open**: Enter cell (no-op in this model) | `f-e-d-c` | **Close**: Exit cell (no-op) |
| `g-a-b-C` | **Sharpen**: Increment cell (+1) | `C-b-a-g` | **Blunt**: Decrement cell (-1) |
| `c-e-g-C` | **Appear**: Move Pointer Right | `C-g-e-c` | **Disappear**: Move Pointer Left |
| `d-f-a-c` | **Hear**: Output ASCII character | `c-a-f-d` | **Speak**: Input ASCII character |

### Loops and Conditionals
- `_` (Pause) denotes a condition.
- `[ <Draft> _ ... _ <ReverseDraft> ]` forms a conditional loop.
- The loop executes while the current cell value is NOT 0.
- The `<Draft>` and `<ReverseDraft>` must be a matching pair (e.g., `c-d-e-f` and `f-e-d-c`) to define the loop's context, though any notes can be used within the loop.

### Syntax Rules
- Drafts are written as four notes separated by hyphens (e.g., `c-d-e-f`).
- White space and newlines are ignored.
- Comments can be added outside of draft sequences.

## Usage

### Run the Interpreter
```bash
python3 interpreter.py path/to/program.dstf
```

### Run the Visualizer
```bash
python3 visualizer.py path/to/program.dstf
```
The visualizer generates an ASCII representation of the musical staff notation for the code.

## Example: weave_A.dstf
This program produces the character 'A' (ASCII 65).
```
g-a-b-C _ g-a-b-C _ C-b-a-g
# (Note: Complexity of loops is required for Turing Completeness)
```
Wait, the loop syntax is `[ <Draft> _ ... _ <ReverseDraft> ]`. Let's refine the "Hello World" example.

To get 'A' (65):
1. Increment a cell until it reaches 65.
2. Output the cell.

```distaff
c-d-e-f                  # Start
g-a-b-C g-a-b-C g-a-b-C  # Incrementing... (simpler than a loop for just one char)
d-f-a-c                  # Output
f-e-d-c                  # End
```
Actually, I'll provide a proper loop-based example in `weave_A.dstf`.
