# Clockwork

**Clockwork** is an esoteric programming language based on the concept of a multi-register mechanical machine (a Turing-complete Minsky register machine). It breaks away from Brainfuck's linear tape and embraces direct, named control over distinct geometric "cogs" (registers).

## Language Specification

Memory consists of infinitely many 32-bit unsigned integer registers accessed by their integer ID (0, 1, 2...). 
The machine maintains a **Selected Cog**, which focuses on one register at a time. All operations happen on the currently selected register.

### Instructions

| Command | Argument | Action |
| :--- | :--- | :--- |
| `COG` | `[N]` | Set focus to Register `N`. |
| `SET` | `[V]` | Set the selected register's value to `V`. |
| `WIND` | | Increment the selected register by 1. |
| `UNWIND` | | Decrement the selected register by 1. |
| `CONNECT` | `[N]` | Add the value of Register `N` to the selected register. |
| `CHIME` | | Output the selected register's value as an ASCII character. |
| `RING` | | Output the selected register's value as an integer string. |
| `READ` | | Read one ASCII character from input into the selected register. |
| `MARK` | `[Label]`| Define a jump target label. |
| `SPRING` | `[Label]`| Jump to `[Label]` if the selected register is **NOT** 0. |
| `FALL` | `[Label]`| Jump to `[Label]` if the selected register **IS** 0. |

### Syntax Rules
- Instructions and arguments are separated by whitespace.
- Comments are denoted by `#` and can appear anywhere on a line.
- Labels can be any string without whitespace.

## Example
A simple Hello World in `hello.clk`:
```clockwork
COG 0
SET 72
CHIME
SET 101
CHIME
# ... etc
```
See `examples/` for more complex demonstrations, including nested loops and register mathematics.
