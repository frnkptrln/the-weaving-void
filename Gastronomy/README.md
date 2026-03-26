# Gastronomy

**Gastronomy** is an esoteric programming language modeled after culinary recipes. By mimicking the actions of a chef, programmers write fully functional, Turing-complete code.

## Language Specification

Gastronomy uses a standard Brainfuck-style infinite tape of 8-bit cells (0-255). The pointer starts at cell 0, and all cells are initialized to 0.

### Ingredients and Actions (Commands)

| Command | Brainfuck Equivalent | Action |
| :--- | :--- | :--- |
| `Take [Name]` | (None) | Syntactic sugar. Often used to declare a variable (e.g., `Take Flour`) |
| `Add` | `+` | Increment the current ingredient cell (+1) |
| `Reduce` | `-` | Decrement the current ingredient cell (-1) |
| `Mix` | `>` | Move to the next ingredient cell (pointer right) |
| `Stir` | `<` | Move to the previous ingredient cell (pointer left) |
| `Taste` | `.` | Output the current ingredient cell as an ASCII character |
| `Substitute` | `,` | Read one ASCII character from input into the current cell |
| `Simmer until reduced` | `[` | Begin a conditional loop. Skip to `Serve` if the current cell is 0 |
| `Serve` | `]` | End a conditional loop. Jump back to `Simmer until reduced` if cell is non-zero |

### Syntax Rules
- Commands are case-insensitive.
- Any word or text that is not a reserved command is treated as a comment and ignored by the interpreter.
- It's common to format Gastronomy code like a recipe list.

## Usage

### Run the Interpreter
```bash
python3 interpreter.py path/to/recipe.gstr
```

## Example: hello_world.gstr
Refer to `examples/hello_world.gstr` for a complete "Hello World" recipe outputting standard ASCII text.
