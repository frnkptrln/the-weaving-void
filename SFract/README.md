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

### Run the Visualizer
```bash
python3 visualizer.py path/to/program.frac
```
The visualizer prints the growth stages of the seed and then sketches the
final generation as a plant: `F` draws a segment, `+`/`-` turn the pen by
45 degrees, and `[`/`]` branch off and return.

## Example: fibonacci_tree.frac
```
Iterations: 1
Axiom: A [ F +++ B - ] F ++ !
Rule: A=+++++++++++++++++++++++++++
---
# Outputs 'S' (ASCII 83)
```

After one growth pass, `A` expands into 27 feed operations. The execution phase
then loops 27 times, adding three units to a child node, adds two more, and
outputs `27 * 3 + 2 = 83`.

## Example: grow.frac
Growth does the arithmetic: over two generations `H` expands into 64 feed
operations (`H -> DDDDDDDD -> 64 +`) and `E` into four. Each letter of the
output `GROW` blooms on its own node along a branch.

## Example: botanical_sketch.frac
A silent seed grown purely to be looked at: all feeds hide inside branch
clusters, so execution skips them and the program halts without output.
Render it with the visualizer to watch the shrub unfold over five
generations.
