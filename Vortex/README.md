# Vortex

**Vortex** is a minimalist Brainfuck successor designed for high-speed execution and concise syntax. It features "Memory Warping," where the pointer automatically wraps around the allocated memory space.

## Syntax

| Symbol | Action |
| :--- | :--- |
| `^` | **Sharpen**: Increment current cell (+1) |
| `v` | **Blunt**: Decrement current cell (-1) |
| `>` | **Spin Right**: Move pointer right (+1) |
| `<` | **Spin Left**: Move pointer left (-1) |
| `⟪` | **Warp In**: Jump past `⟫` if the current cell is 0 |
| `⟫` | **Warp Out**: Jump back to `⟪` if the current cell is not 0 |
| `!` | **Echo**: Output current cell as ASCII |
| `*` | **Void**: Reset current cell to 0 |

### Memory Model
Vortex uses a cyclic tape of 8-bit cells (0-255). The default size is 1024 cells, and the pointer wraps from 1023 to 0 and vice-versa.

## Usage

### Run the Interpreter
```bash
python3 interpreter.py path/to/hello.vtx
```

## Example: hello.vtx
A compact fragment from the full "Hello, World!" example:
```vortex
# H
^^^^^^^^ ⟪ > ^^^^^^^^ < v ⟫ > ^ !
# e
^^^^^^^ !
# l
^^^^^^^ ! !
# o
^^^ !
# ... and so on
```
Run `examples/hello.vtx` for the complete program.

## Example: alphabet.vtx
`examples/alphabet.vtx` prints the full alphabet from a single loop: the
letter cell is built by multiplication (`5 * 13 = 65`), then printed and
incremented 26 times.
