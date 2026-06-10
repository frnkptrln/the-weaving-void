# MandelMemory

**MandelMemory** is a chaos-driven esoteric language where memory locations are coordinates in the complex number plane. The stability of the system is governed by the rules of the Mandelbrot set.

## Concepts

### The Complex Memory Plane
Instead of a linear tape, MandelMemory uses the complex plane ($z = x + yi$) as its address space. The "pointer" is a complex number $z$.

### Stability Rule
Memory operations (writing with `+` or `-`) are only possible if the current pointer $z$ is "stable" ($|z| \leq 2$). If you attempt to modify a value at an unstable coordinate, a `StabilityError` occurs.

## Commands

| Command | Action |
| :--- | :--- |
| `T(c)` | **Transform**: Update pointer $z_{new} = z_{old}^2 + c$, where $c$ is a complex number (e.g., `T(0.1+0.2i)`). |
| `+` | **Perturb Up**: Increment the value at the current coordinate $z$ (+1). |
| `-` | **Perturb Down**: Decrement the value at the current coordinate $z$ (-1). |
| `!` | **Observe**: Output the value at the current coordinate $z$ as an ASCII character. |
| `[` / `]` | **Fluctuate**: Loop while the value at the current coordinate $z$ is greater than 0. |

## Usage

### Run the Interpreter
```bash
python3 interpreter.py path/to/program.mdm
```

### Run the Visualizer
```bash
python3 visualizer.py path/to/program.mdm
```
The visualizer generates a map showing the coordinates of all variables that were accessed during execution, overlaid on the Mandelbrot set.

## Example: hello_mdm.mdm
```mandelmemory
# Build 77 at the stable coordinate 0.1 and output 'M'.
T(0)
++++++
[
  T(0.1)
  +++++++++++
  T(-0.01)
  -
]
T(0.1)
!
```

The example uses stable transforms that return to known coordinates:
`T(0)` keeps the pointer at `0`, and `T(-0.01)` maps `0.1` back to `0`.

## Example: digits.mdm
`examples/digits.mdm` prints `0123456789` by parking two memory cells on a
stable two-point orbit: `T(-0.75)` maps `0.5` to `-0.5` and `T(0.25)` maps
`-0.5` back to `0.5`, so the loop can hop between counter and digit cell.
