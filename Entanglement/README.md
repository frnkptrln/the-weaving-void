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
- **DOUBLE**: $\Delta B = 2 \times \Delta A$

## Usage

### Run the Interpreter
```bash
python3 interpreter.py path/to/program.ent
```

## Example: bell_state_logic.ent
```entanglement
| (Alice, Bob)   # Create pair
~ (Alice, Bob, DOUBLE) # Bob = 2 * Alice
+ (Alice, 33)    # Alice = 33, Bob = 66
! (Alice)        # Outputs '!' (33)
! (Bob)          # Outputs 'B' (66)
```
Wait, 66 is 'B'. 33 is '!'.
If I want 'E' (69):
Alice = 33, Bob = 66.
+ Alice 1. Alice=34, Bob=68.
Wait, `DOUBLE` means $\Delta B = 2 \Delta A$.
So if Alice starts at 0, and I add 34. Bob becomes 68.
Then I add 1 to Bob? No, only changes to the *primary* affect the *secondary*?
Actually, in Entanglement, any change to either should affect the other.
If Bob = 2 * Alice, then Alice = Bob / 2.
If I add 1 to Bob, Alice increases by 0.5? We should use integers.
Let's define rules for integers:
- `EQUAL`: `B += dA`, `A += dB`
- `OPPOSITE`: `B -= dA`, `A -= dB`
- `DOUBLE`: `B += 2*dA`, `A += dB // 2`

I'll stick to these.
