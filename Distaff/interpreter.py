import sys
import re

class DistaffInterpreter:
    def __init__(self, code):
        self.code = code
        self.tape = [0] * 30000
        self.ptr = 0
        self.drafts = {
            "cdef": self.open_cell,
            "fedc": self.close_cell,
            "gabC": self.sharpen,
            "Cbag": self.blunt,
            "cegC": self.appear,
            "Cgec": self.disappear,
            "dfac": self.hear,
            "cafd": self.speak,
        }
        self.commands = self.parse(code)
        self.loop_map = self.build_loop_map(self.commands)

    def parse(self, code):
        # Remove comments (lines starting with #)
        code = re.sub(r'#.*', '', code)
        
        # Tokenize: drafts (e.g., c-d-e-f), loops ([ and ]), and pauses (_)
        tokens = []
        # Find drafts: 4 notes separated by hyphens
        # Also find single characters [, ], _
        pattern = r'([cdefgabC]-[cdefgabC]-[cdefgabC]-[cdefgabC])|(\[)|(\])|(_)'
        
        for match in re.finditer(pattern, code):
            if match.group(1):
                # Clean up draft notation (remove hyphens)
                draft = match.group(1).replace('-', '')
                tokens.append(draft)
            elif match.group(2):
                tokens.append('[')
            elif match.group(3):
                tokens.append(']')
            elif match.group(4):
                tokens.append('_')
        
        return tokens

    def build_loop_map(self, tokens):
        loop_stack = []
        loop_map = {}
        for i, token in enumerate(tokens):
            if token == '[':
                loop_stack.append(i)
            elif token == ']':
                if not loop_stack:
                    raise SyntaxError("Unmatched ']' at position " + str(i))
                start = loop_stack.pop()
                loop_map[start] = i
                loop_map[i] = start
        if loop_stack:
            raise SyntaxError("Unmatched '[' at position " + str(loop_stack.pop()))
        return loop_map

    def open_cell(self): pass
    def close_cell(self): pass
    
    def sharpen(self):
        self.tape[self.ptr] = (self.tape[self.ptr] + 1) % 256
        
    def blunt(self):
        self.tape[self.ptr] = (self.tape[self.ptr] - 1) % 256
        
    def appear(self):
        self.ptr += 1
        if self.ptr >= len(self.tape):
            self.tape.extend([0] * 1000)
            
    def disappear(self):
        self.ptr -= 1
        if self.ptr < 0:
            raise RuntimeError("Tape pointer moved below 0")
            
    def hear(self):
        print(chr(self.tape[self.ptr]), end='', flush=True)
        
    def speak(self):
        try:
            char = sys.stdin.read(1)
            self.tape[self.ptr] = ord(char) if char else 0
        except EOFError:
            self.tape[self.ptr] = 0

    def run(self):
        pc = 0
        while pc < len(self.commands):
            cmd = self.commands[pc]
            
            if cmd == '[':
                # Loop start logic: if current cell is 0, jump to matching ]
                # But spec says [ <Draft> _ denotes conditional loop.
                # Actually, standard BF logic is [ jump if 0, ] jump back if not 0.
                if self.tape[self.ptr] == 0:
                    pc = self.loop_map[pc]
            elif cmd == ']':
                if self.tape[self.ptr] != 0:
                    pc = self.loop_map[pc]
            elif cmd == '_':
                # Pause/Condition - can be a no-op if [ and ] handle the jumps
                pass
            elif cmd in self.drafts:
                self.drafts[cmd]()
            else:
                # Should not happen with current parser
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
        interpreter = DistaffInterpreter(code)
        interpreter.run()
    except FileNotFoundError:
        print(f"Error: File {filename} not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
