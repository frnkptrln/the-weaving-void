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
- `[` begins a conditional loop.
- `]` ends a conditional loop.
- The loop executes while the current cell value is NOT 0.
- `_` (Pause) is a no-op token used to mark loop rhythm and readability.

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

```distaff
# Set cell 0 to 13, add 5 to cell 1 per loop, then output cell 1.
g-a-b-C g-a-b-C g-a-b-C g-a-b-C g-a-b-C
g-a-b-C g-a-b-C g-a-b-C g-a-b-C g-a-b-C
g-a-b-C g-a-b-C g-a-b-C

[ c-d-e-f _
    c-e-g-C
    g-a-b-C g-a-b-C g-a-b-C g-a-b-C g-a-b-C
    C-g-e-c
    C-b-a-g
_ f-e-d-c ]

c-e-g-C
d-f-a-c
```
