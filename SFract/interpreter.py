import sys
import re

class TreeNode:
    def __init__(self, parent=None):
        self.value = 0
        self.parent = parent
        self.children = []

    def get_child(self, index=0):
        while len(self.children) <= index:
            self.children.append(TreeNode(self))
        return self.children[index]

class SFractInterpreter:
    def __init__(self, filename):
        self.iterations = 0
        self.axiom = ""
        self.rules = {}
        self.load_seed(filename)
        self.program = self.grow()
        self.root = TreeNode()
        self.current_node = self.root

    def load_seed(self, filename):
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line in lines:
            line = line.strip()
            if line == "---": break
            if line.startswith("Iterations:"):
                self.iterations = int(line.split(":")[1].strip())
            elif line.startswith("Axiom:"):
                self.axiom = line.split(":")[1].strip()
            elif line.startswith("Rule:"):
                pair = line.split(":")[1].strip()
                if '=' in pair:
                    char, replacement = pair.split('=')
                    self.rules[char.strip()] = replacement.strip()

    def grow(self):
        current = self.axiom
        for _ in range(self.iterations):
            next_str = ""
            for char in current:
                next_str += self.rules.get(char, char)
            current = next_str
        return current

    def run(self):
        pc = 0
        loop_map = self.build_loop_map(self.program)
        
        while pc < len(self.program):
            cmd = self.program[pc]
            
            if cmd == 'F':
                self.current_node = self.current_node.get_child(0)
            elif cmd == 'B':
                if self.current_node.parent:
                    self.current_node = self.current_node.parent
            elif cmd == '+':
                self.current_node.value = (self.current_node.value + 1) % 256
            elif cmd == '-':
                self.current_node.value = (self.current_node.value - 1) % 256
            elif cmd == '!':
                print(chr(self.current_node.value), end='', flush=True)
            elif cmd == '?':
                if self.current_node.value == 0:
                    pc += 1 # Skip next character
            elif cmd == '[':
                if self.current_node.value == 0:
                    pc = loop_map[pc]
            elif cmd == ']':
                if self.current_node.value != 0:
                    pc = loop_map[pc]
            
            pc += 1

    def build_loop_map(self, code):
        loop_stack = []
        loop_map = {}
        for i, char in enumerate(code):
            if char == '[':
                loop_stack.append(i)
            elif char == ']':
                if not loop_stack:
                    raise SyntaxError(f"Unmatched ']' at {i}")
                start = loop_stack.pop()
                loop_map[start] = i
                loop_map[i] = start
        return loop_map

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 interpreter.py <filename>")
        sys.exit(1)
    
    try:
        interpreter = SFractInterpreter(sys.argv[1])
        interpreter.run()
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
