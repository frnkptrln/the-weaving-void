import re
import sys


class EntanglementInterpreter:
    def __init__(self, code):
        self.vars = {}
        self.links = {}
        self.commands = self.tokenize(code)
        self.loop_map = self.build_loop_map()

    def tokenize(self, code):
        code = re.sub(r"#.*", "", code)
        tokens = []
        pattern = r"(\|)|(~)|(\+)|(-)|(!)|(\?)|(\[)|(\])|\(([^)]+)\)"

        for match in re.finditer(pattern, code):
            if match.group(9):
                args = [arg.strip() for arg in match.group(9).split(",")]
                tokens.append(("ARGS", args))
            elif match.group(1):
                tokens.append(("INIT", "|"))
            elif match.group(2):
                tokens.append(("ENTANGLE", "~"))
            elif match.group(3):
                tokens.append(("ADD", "+"))
            elif match.group(4):
                tokens.append(("SUB", "-"))
            elif match.group(5):
                tokens.append(("MEASURE", "!"))
            elif match.group(6):
                tokens.append(("COHERENCE", "?"))
            elif match.group(7):
                tokens.append(("LOOP_START", "["))
            elif match.group(8):
                tokens.append(("LOOP_END", "]"))

        return tokens

    def build_loop_map(self):
        stack = []
        loop_map = {}

        for index, (token_type, _) in enumerate(self.commands):
            if token_type == "LOOP_START":
                stack.append(index)
            elif token_type == "LOOP_END":
                if not stack:
                    raise SyntaxError(f"Unmatched ']' at token {index}")
                start = stack.pop()
                loop_map[start] = index
                loop_map[index] = start

        if stack:
            raise SyntaxError(f"Unmatched '[' at token {stack[-1]}")

        return loop_map

    def args_after(self, pc, command, count):
        if pc + 1 >= len(self.commands) or self.commands[pc + 1][0] != "ARGS":
            raise SyntaxError(f"{command} requires arguments")

        args = self.commands[pc + 1][1]
        if len(args) != count:
            raise SyntaxError(f"{command} expects {count} argument(s), got {len(args)}")

        return args

    def update_var(self, name, delta, origin=None):
        if name not in self.vars:
            self.vars[name] = 0

        self.vars[name] = (self.vars[name] + delta) % 256

        if name not in self.links:
            return

        partner, rule, role = self.links[name]
        if partner == origin:
            return

        if rule == "EQUAL":
            partner_delta = delta
        elif rule == "OPPOSITE":
            partner_delta = -delta
        elif role == "primary":
            partner_delta = delta * 2
        else:
            partner_delta = delta // 2

        self.update_var(partner, partner_delta, name)

    def measure(self, name):
        value = self.vars.get(name, 0)
        print(chr(value % 256), end="", flush=True)

        if name in self.links:
            partner, _, _ = self.links.pop(name)
            self.links.pop(partner, None)

    def run(self):
        pc = 0

        while pc < len(self.commands):
            token_type, _ = self.commands[pc]

            if token_type == "ARGS":
                raise SyntaxError(f"Unexpected argument list at token {pc}")
            if token_type == "INIT":
                a, b = self.args_after(pc, "|", 2)
                self.vars[a] = 0
                self.vars[b] = 0
                pc += 2
            elif token_type == "ENTANGLE":
                a, b, rule = self.args_after(pc, "~", 3)
                rule = rule.upper()
                if rule not in {"EQUAL", "OPPOSITE", "DOUBLE"}:
                    raise SyntaxError(f"Unknown entanglement rule: {rule}")
                self.links[a] = (b, rule, "primary")
                self.links[b] = (a, rule, "secondary")
                pc += 2
            elif token_type == "ADD":
                name, value = self.args_after(pc, "+", 2)
                self.update_var(name, int(value))
                pc += 2
            elif token_type == "SUB":
                name, value = self.args_after(pc, "-", 2)
                self.update_var(name, -int(value))
                pc += 2
            elif token_type == "MEASURE":
                (name,) = self.args_after(pc, "!", 1)
                self.measure(name)
                pc += 2
            elif token_type == "COHERENCE":
                self.args_after(pc, "?", 1)
                if pc + 2 >= len(self.commands) or self.commands[pc + 2][0] != "LOOP_START":
                    raise SyntaxError("? (name) must be followed by a loop block")
                pc += 2
            elif token_type == "LOOP_START":
                if pc == 0 or self.commands[pc - 1][0] != "ARGS":
                    raise SyntaxError("'[' must follow ? (name)")
                var_name = self.commands[pc - 1][1][0]
                pc = self.loop_map[pc] + 1 if self.vars.get(var_name, 0) <= 0 else pc + 1
            elif token_type == "LOOP_END":
                start_pc = self.loop_map[pc]
                var_name = self.commands[start_pc - 1][1][0]
                pc = start_pc if self.vars.get(var_name, 0) > 0 else pc + 1


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 interpreter.py <filename>")
        sys.exit(1)

    try:
        with open(sys.argv[1], "r", encoding="utf-8") as source_file:
            code = source_file.read()
        EntanglementInterpreter(code).run()
    except Exception as exc:
        print(f"Error: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
