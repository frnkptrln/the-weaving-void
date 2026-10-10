import shlex
import sys
from collections import defaultdict


class MarginaliaInterpreter:
    def __init__(self, source):
        self.instructions = self.parse(source)
        self.loop_map = self.build_loop_map()
        self.margins = defaultdict(list)
        self.ptr = 0
        self.pc = 0

    def parse(self, source):
        instructions = []
        for line_number, line in enumerate(source.splitlines(), start=1):
            stripped = line.split("#", 1)[0].strip()
            if not stripped:
                continue

            try:
                parts = shlex.split(stripped)
            except ValueError as exc:
                raise SyntaxError(f"Line {line_number}: {exc}") from exc

            op = parts[0].lower()
            args = parts[1:]
            instructions.append((op, args, line_number))

        return instructions

    def build_loop_map(self):
        stack = []
        loop_map = {}

        for idx, (op, _, line_number) in enumerate(self.instructions):
            if op == "while":
                stack.append(idx)
            elif op == "again":
                if not stack:
                    raise SyntaxError(f"Line {line_number}: unmatched 'again'")
                start = stack.pop()
                loop_map[start] = idx
                loop_map[idx] = start

        if stack:
            _, _, line_number = self.instructions[stack[-1]]
            raise SyntaxError(f"Line {line_number}: unmatched 'while'")

        return loop_map

    def value(self):
        return sum(self.margins[self.ptr]) % 256

    def require_args(self, op, args, count, line_number):
        if len(args) != count:
            raise SyntaxError(
                f"Line {line_number}: '{op}' expects {count} argument(s), got {len(args)}"
            )

    def parse_int(self, value, op, line_number):
        try:
            return int(value)
        except ValueError as exc:
            raise SyntaxError(
                f"Line {line_number}: '{op}' requires an integer argument"
            ) from exc

    def run(self, *, max_steps=None, on_step=None):
        """Execute, optionally emitting detached snapshots after each instruction.

        Existing unbounded execution is unchanged. A caller can bound a trace
        without duplicating the language's execution rules in another runtime.
        """
        if max_steps is not None and (type(max_steps) is not int or max_steps < 0):
            raise ValueError("max_steps must be a non-negative integer or None")
        steps = 0
        while self.pc < len(self.instructions):
            if max_steps is not None and steps >= max_steps:
                raise RuntimeError(f"execution exceeded {max_steps} steps")
            executed = self.pc
            op, args, line_number = self.instructions[self.pc]

            if op == "note":
                self.require_args(op, args, 1, line_number)
                self.margins[self.ptr].append(self.parse_int(args[0], op, line_number))
            elif op == "doubt":
                self.require_args(op, args, 1, line_number)
                self.margins[self.ptr].append(-self.parse_int(args[0], op, line_number))
            elif op == "right":
                step = self.parse_int(args[0], op, line_number) if args else 1
                self.ptr += step
            elif op == "left":
                step = self.parse_int(args[0], op, line_number) if args else 1
                self.ptr -= step
            elif op == "fold":
                self.margins[self.ptr] = [self.value()]
            elif op == "forget":
                self.margins[self.ptr] = []
            elif op == "quote":
                self.require_args(op, args, 0, line_number)
                print(chr(self.value()), end="", flush=True)
            elif op == "echo":
                self.require_args(op, args, 0, line_number)
                print(self.value(), end="", flush=True)
            elif op == "listen":
                self.require_args(op, args, 0, line_number)
                char = sys.stdin.read(1)
                self.margins[self.ptr] = [ord(char) if char else 0]
            elif op == "verify":
                self.require_args(op, args, 1, line_number)
                expected = self.parse_int(args[0], op, line_number) % 256
                actual = self.value()
                if actual != expected:
                    raise RuntimeError(
                        f"Line {line_number}: verification failed at margin {self.ptr} "
                        f"(expected {expected}, found {actual})"
                    )
            elif op == "while":
                self.require_args(op, args, 0, line_number)
                if self.value() == 0:
                    self.pc = self.loop_map[self.pc]
            elif op == "again":
                self.require_args(op, args, 0, line_number)
                if self.value() != 0:
                    self.pc = self.loop_map[self.pc]
            else:
                raise SyntaxError(f"Line {line_number}: unknown command '{op}'")

            self.pc += 1
            steps += 1
            if on_step is not None:
                on_step({"executed": executed, "next": self.pc, "pointer": self.ptr,
                         "margins": {str(k): list(v) for k, v in sorted(self.margins.items())}})


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 interpreter.py <file.mrg>")
        sys.exit(1)

    try:
        with open(sys.argv[1], "r", encoding="utf-8") as source_file:
            source = source_file.read()
        MarginaliaInterpreter(source).run()
    except FileNotFoundError:
        print(f"Error: {sys.argv[1]} not found in the margin.")
        sys.exit(1)
    except Exception as exc:
        print(f"Error: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
