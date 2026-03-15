# S-Fract

**S-Fract** is a biological generative language where source code is a "seed" that grows based on recursive L-System rules before execution.

## Phases

### 1. Growth Phase
The seed consists of an **Axiom** (initial string) and a set of **Rules** (transformations applied to characters). The system expands the Axiom using the Rules for $n$ generations.

### 2. Execution Phase
The resulting string is interpreted as a sequence of commands.

## Architecture

### Memory Model
S-Fract uses a **Tree Memory Model**. The pointer starts at the root node. Commands allow navigation down to children or up to parents. Each node stores an 8-bit value (0-255).

## Commands

| Command | Action |
| :--- | :--- |
| `F` | **Flower**: Move down to the first child node. If it doesn't exist, create it. |
| `B` | **Branch**: Move up to the parent node. |
| `+` | **Feed**: Increment current node value (+1). |
| `-` | **Prune**: Decrement current node value (-1). |
| `?` | **Sprout**: Conditional; if node value > 0, execute the next character, otherwise skip it. |
| `!` | **Bloom**: Output current node value as ASCII character. |
| `[` / `]` | **Cluster**: Loop markers (while current node > 0). |

## Seed Format
The `.frac` file should follow this structure:
```
Iterations: <n>
Axiom: <string>
Rule: <char>=<string>
Rule: <char>=<string>
---
<Optional comments>
```

## Usage

### Run the Interpreter
```bash
python3 interpreter.py path/to/program.frac
```

## Example: fibonacci_tree.frac
```
Iterations: 2
Axiom: A
Rule: A=F+B
---
# This will result in a specific pattern of tree movements.
```
Wait, for a meaningful program, I'll provide a better "Hello" equivalent.
To output 'S' (83):
Axiom: `A`
Rule: `A=+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++!`
Iterations: 1
Result: `83 pluses and an exclamation mark`.
Actually, L-Systems are more interesting for structure.
Rule: `A=F++B`
Iterations: 3
`A` -> `F++B` -> `F++B` (Wait, rules apply to characters).
Rule: `F=F+`
Axiom: `F!`
Iter 1: `F+!`
Iter 2: `F++!`
...
This allows exponential growth of commands!
