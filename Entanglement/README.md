# Entanglement

**Entanglement** is a quantum-inspired esoteric language where variables exist in linked pairs. Actions performed on one variable instantaneously affect its entangled partner according to predefined rules.

## Core Concepts

### Entangled Pairs
Variables are not independent. They are created in pairs `(A, B)`. When you modify `A`, `B` changes as well.

### Measurement and Collapse
Until measured with the `!` command, variables exist in a state of potential. Measuring a variable "collapses" the pair, outputs the value, and destroys the entanglement. After measurement, the variables are no longer linked.

## Commands

| Command | Action |
| :--- | :--- |
| `| (A,B)` | **Initialize**: Create a new entangled pair of variables named `A` and `B`. Initially 0. |
| `~ (A,B, rule)` | **Entangle**: Set the link rule between `A` and `B`. Rules: `EQUAL`, `OPPOSITE`, `DOUBLE`. |
| `+ (A, val)` | **Excite**: Add `val` to variable `A` (and affect `B`). |
| `- (A, val)` | **Decay**: Subtract `val` from variable `A` (and affect `B`). |
| `! (A)` | **Measure**: Output variable `A` as ASCII and destroy the `(A,B)` link. |
| `? (A) [ ... ]` | **Coherence**: Loop while variable `A` > 0. |

## Link Rules

- **EQUAL**: $\Delta B = \Delta A$
- **OPPOSITE**: $\Delta B = -\Delta A$
- **DOUBLE**: The first variable is primary. Changes to it apply double delta to its partner; changes to the partner apply integer half delta back to the primary.

## Usage

### Run the Interpreter
```bash
python3 interpreter.py path/to/program.ent
```

## Example: bell_state_logic.ent
```entanglement
| (Alice, Bob)   # Create pair
~ (Alice, Bob, DOUBLE)
+ (Alice, 40)    # Alice = 40, Bob = 80
+ (Bob, 1)       # Bob = 81, Alice remains 40
! (Bob)          # Outputs 'Q' (81)
```
