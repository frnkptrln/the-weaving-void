import sys

class VortexInterpreter:
    def __init__(self, code, tape_size=1024):
        self.code = self.clean_code(code)
        self.tape_size = tape_size
        self.tape = [0] * tape_size
        self.ptr = 0
        self.pc = 0
        self.loop_map = self.build_loop_map(self.code)

    def clean_code(self, code):
        # Keep only valid Vortex commands
        valid_cmds = "^v><⟪⟫!*"
        return "".join([c for c in code if c in valid_cmds])

    def build_loop_map(self, code):
        loop_stack = []
        loop_map = {}
        for i, char in enumerate(code):
            if char == '⟪':
                loop_stack.append(i)
            elif char == '⟫':
                if not loop_stack:
                    raise SyntaxError(f"Unmatched '⟫' at position {i}")
                start = loop_stack.pop()
                loop_map[start] = i
                loop_map[i] = start
        if loop_stack:
            raise SyntaxError(f"Unmatched '⟪' at position {loop_stack.pop()}")
        return loop_map

    def run(self):
        while self.pc < len(self.code):
            cmd = self.code[self.pc]
            
            if cmd == '^':
                self.tape[self.ptr] = (self.tape[self.ptr] + 1) % 256
            elif cmd == 'v':
                self.tape[self.ptr] = (self.tape[self.ptr] - 1) % 256
            elif cmd == '>':
                self.ptr = (self.ptr + 1) % self.tape_size
            elif cmd == '<':
                self.ptr = (self.ptr - 1) % self.tape_size
            elif cmd == '!':
                print(chr(self.tape[self.ptr]), end='', flush=True)
            elif cmd == '*':
                self.tape[self.ptr] = 0
            elif cmd == '⟪':
                if self.tape[self.ptr] == 0:
                    self.pc = self.loop_map[self.pc]
            elif cmd == '⟫':
                if self.tape[self.ptr] != 0:
                    self.pc = self.loop_map[self.pc]
            
            self.pc += 1

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 interpreter.py <filename>")
        sys.exit(1)
        
    filename = sys.argv[1]
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            code = f.read()
        interpreter = VortexInterpreter(code)
        interpreter.run()
    except FileNotFoundError:
        print(f"Error: File {filename} not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
