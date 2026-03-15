import sys
import re

class MandelMemoryInterpreter:
    def __init__(self, code):
        self.code = code
        self.memory = {} # Key: complex, Value: int
        self.z = complex(0, 0)
        self.pc = 0
        self.commands = self.parse(code)
        self.loop_map = self.build_loop_map(self.commands)
        self.accessed_points = set()

    def parse(self, code):
        # Remove comments
        code = re.sub(r'#.*', '', code)
        
        # Tokens: T(c), +, -, !, ?, [...]
        # T(c) pattern: T(real+imag i) or T(real-imag i) or T(real)
        # We need to be careful with complex number formatting
        tokens = []
        pattern = r'(T\(-?\d*\.?\d*[+-]\d*\.?\d*i\))|(T\(-?\d*\.?\d*i?\))|(\+)|(-)|(!)|(\?)|(\[)|(\])'
        
        for match in re.finditer(pattern, code):
            if match.group(1) or match.group(2):
                # Extract the 1 or 2 group content
                t_expr = match.group(1) if match.group(1) else match.group(2)
                # T(0.1+0.2i) -> 0.1+0.2j
                inner = t_expr[2:-1]
                inner = inner.replace('i', 'j')
                # If it's just 'j' or '+j', complex() might fail if not '1j'
                # But typically it's numbers
                try:
                    c_val = complex(inner)
                    tokens.append(('T', c_val))
                except ValueError:
                    # Handle cases like T(i) which should be 1j
                    if inner == 'i' or inner == 'j': tokens.append(('T', complex(0, 1)))
                    elif inner == '-i' or inner == '-j': tokens.append(('T', complex(0, -1)))
                    else: raise SyntaxError(f"Invalid complex number: {inner}")
            elif match.group(3): tokens.append(('+', None))
            elif match.group(4): tokens.append(('-', None))
            elif match.group(5): tokens.append(('!', None))
            elif match.group(6): tokens.append(('?', None))
            elif match.group(7): tokens.append(('[', None))
            elif match.group(8): tokens.append((']', None))
        
        return tokens

    def build_loop_map(self, tokens):
        loop_stack = []
        loop_map = {}
        for i, (type, val) in enumerate(tokens):
            if type == '[':
                loop_stack.append(i)
            elif type == ']':
                if not loop_stack:
                    raise SyntaxError(f"Unmatched ']' at position {i}")
                start = loop_stack.pop()
                loop_map[start] = i
                loop_map[i] = start
        return loop_map

    def check_stability(self):
        if abs(self.z) > 2:
            raise RuntimeError(f"StabilityError: |z| = {abs(self.z)} > 2 at {self.z}")

    def get_z_key(self):
        # Round to avoid floating point precision issues with dict keys
        return complex(round(self.z.real, 10), round(self.z.imag, 10))

    def run(self):
        pc = 0
        while pc < len(self.commands):
            cmd_type, cmd_val = self.commands[pc]
            
            z_key = self.get_z_key()
            if cmd_type == 'T':
                self.z = self.z**2 + cmd_val
            elif cmd_type == '+':
                self.check_stability()
                self.memory[z_key] = self.memory.get(z_key, 0) + 1
                self.accessed_points.add(z_key)
            elif cmd_type == '-':
                self.check_stability()
                self.memory[z_key] = self.memory.get(z_key, 0) - 1
                self.accessed_points.add(z_key)
            elif cmd_type == '!':
                val = self.memory.get(z_key, 0)
                print(chr(val % 256), end='', flush=True)
            elif cmd_type == '[':
                if self.memory.get(z_key, 0) <= 0:
                    pc = self.loop_map[pc]
            elif cmd_type == ']':
                if self.memory.get(z_key, 0) > 0:
                    pc = self.loop_map[pc]
            elif cmd_type == '?':
                # Separate loop marker as per spec "while value > 0"
                # If '?' is used as a standalone loop marker like BF '['
                pass 
            
            pc += 1

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 interpreter.py <filename>")
        sys.exit(1)
        
    filename = sys.argv[1]
    try:
        with open(filename, 'r') as f:
            code = f.read()
        interpreter = MandelMemoryInterpreter(code)
        interpreter.run()
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
