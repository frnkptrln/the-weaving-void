import sys
import re

class EntanglementInterpreter:
    def __init__(self, code):
        self.code = code
        self.vars = {} # name -> value
        self.links = {} # name -> (partner_name, rule)
        self.pc = 0
        self.commands = self.tokenize(code)
        self.loop_map = self.build_loop_map(self.commands)

    def tokenize(self, code):
        # Remove comments
        code = re.sub(r'#.*', '', code)
        
        # Patterns: 
        # | (A, B)
        # ~ (A, B, rule)
        # + (A, val)
        # - (A, val)
        # ! (A)
        # ? (A) [ ... ]
        
        tokens = []
        pattern = r'(\|)|(~)|(\+)|(-)|(!)|(\?)|(\[)|(\])|\(([^)]+)\)'
        
        for match in re.finditer(pattern, code):
            if match.group(9): # Arguments inside ()
                args = [a.strip() for a in match.group(9).split(',')]
                tokens.append(('ARGS', args))
            elif match.group(1): tokens.append(('INIT', '|'))
            elif match.group(2): tokens.append(('ENTANGLE', '~'))
            elif match.group(3): tokens.append(('ADD', '+'))
            elif match.group(4): tokens.append(('SUB', '-'))
            elif match.group(5): tokens.append(('MEASURE', '!'))
            elif match.group(6): tokens.append(('COHERENCE', '?'))
            elif match.group(7): tokens.append(('LOOP_START', '['))
            elif match.group(8): tokens.append(('LOOP_END', ']'))
        
        return tokens

    def build_loop_map(self, tokens):
        loop_stack = []
        loop_map = {}
        for i, (type, val) in enumerate(tokens):
            if type == 'LOOP_START':
                loop_stack.append(i)
            elif type == 'LOOP_END':
                if not loop_stack:
                    raise SyntaxError(f"Unmatched ']' at {i}")
                start = loop_stack.pop()
                loop_map[start] = i
                loop_map[i] = start
        return loop_map

    def update_var(self, name, delta, origin=None):
        if name not in self.vars:
            self.vars[name] = 0
        
        self.vars[name] = (self.vars[name] + delta) % 256
        
        # Link logic
        if name in self.links:
            partner, rule = self.links[name]
            if partner != origin:
                if rule == 'EQUAL':
                    self.update_var(partner, delta, name)
                elif rule == 'OPPOSITE':
                    self.update_var(partner, -delta, name)
                elif rule == 'DOUBLE':
                    # If this is the primary (A), B gets 2*delta
                    # But wait, how do we know which is primary?
                    # I'll assume the first one passed to ~ is primary for scaling
                    # For simplicity, if rule is DOUBLE, 
                    # and we are updating the first element of the pair
                    pair = sorted([name, partner]) # Stabilize
                    if name == pair[0]:
                        self.update_var(partner, delta * 2, name)
                    else:
                        self.update_var(partner, delta // 2, name)

    def run(self):
        pc = 0
        while pc < len(self.commands):
            cmd_type, _ = self.commands[pc]
            
            if cmd_type == 'INIT':
                pc += 1
                args = self.commands[pc][1]
                self.vars[args[0]] = 0
                self.vars[args[1]] = 0
            elif cmd_type == 'ENTANGLE':
                pc += 1
                args = self.commands[pc][1]
                a, b, rule = args[0], args[1], args[2]
                self.links[a] = (b, rule)
                self.links[b] = (a, rule)
            elif cmd_type == 'ADD':
                pc += 1
                args = self.commands[pc][1]
                self.update_var(args[0], int(args[1]))
            elif cmd_type == 'SUB':
                pc += 1
                args = self.commands[pc][1]
                self.update_var(args[0], -int(args[1]))
            elif cmd_type == 'MEASURE':
                pc += 1
                args = self.commands[pc][1]
                name = args[0]
                val = self.vars.get(name, 0)
                print(chr(val % 256), end='', flush=True)
                # Destroy entanglement
                if name in self.links:
                    partner, _ = self.links[name]
                    del self.links[name]
                    if partner in self.links:
                        del self.links[partner]
            elif cmd_type == 'LOOP_START':
                # Peek at previous COHERENCE check
                # For simplicity, I'll just check the variable in the COHERENCE command
                # But wait, COHERENCE is '?' (A).
                pass
            elif cmd_type == 'COHERENCE':
                pc += 1
                args = self.commands[pc][1]
                name = args[0]
                if self.vars.get(name, 0) <= 0:
                    # Jump past next LOOP_START/LOOP_END block
                    if pc + 1 < len(self.commands) and self.commands[pc+1][0] == 'LOOP_START':
                        pc = self.loop_map[pc+1]
                else:
                    # Continue into loop
                    pass
            elif cmd_type == 'LOOP_END':
                # This is handled by a standard loop jump back if needed
                # But my COHERENCE handles the jump forward.
                # To jump back, I need to know where the COHERENCE was.
                # Let's refine the loop logic.
                pass

            pc += 1
            # Standard while-like jump back for loops is not quite right here
            # I'll stick to a simpler logic: ? (A) [ ... ]
            # If at LOOP_END, jump back to COHERENCE.

    def run_fixed(self):
        # Improved loop logic
        pc = 0
        while pc < len(self.commands):
            cmd = self.commands[pc]
            ctype = cmd[0]
            
            if ctype == 'INIT':
                pc += 1
                args = self.commands[pc][1]
                self.vars[args[0]] = 0
                self.vars[args[1]] = 0
            elif ctype == 'ENTANGLE':
                pc += 1
                args = self.commands[pc][1]
                a, b, rule = args[0], args[1], args[2]
                self.links[a] = (b, rule)
                self.links[b] = (a, rule)
            elif ctype == 'ADD':
                pc += 1
                args = self.commands[pc][1]
                self.update_var(args[0], int(args[1]))
            elif ctype == 'SUB':
                pc += 1
                args = self.commands[pc][1]
                self.update_var(args[0], -int(args[1]))
            elif ctype == 'MEASURE':
                pc += 1
                args = self.commands[pc][1]
                name = args[0]
                val = self.vars.get(name, 0)
                print(chr(val % 256), end='', flush=True)
                if name in self.links:
                    partner, _ = self.links[name]
                    del self.links[name]
                    if partner in self.links: del self.links[partner]
            elif ctype == 'COHERENCE':
                # This marker precedes a loop block
                # We save where it is for jumping back
                pass
            elif ctype == 'LOOP_START':
                # Standard BF loop: while [A]
                # But here it's ? (A) [
                # Need to find the (A) arg which is at pc - 1
                prev_args = self.commands[pc-1][1]
                var_name = prev_args[0]
                if self.vars.get(var_name, 0) <= 0:
                    pc = self.loop_map[pc]
            elif ctype == 'LOOP_END':
                # Jump back to matching LOOP_START
                start_pc = self.loop_map[pc]
                # Re-evaluate from LOOP_START
                pc = start_pc - 1
            
            pc += 1

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 interpreter.py <filename>")
        sys.exit(1)
    
    with open(sys.argv[1], 'r') as f:
        code = f.read()
    
    interpreter = EntanglementInterpreter(code)
    interpreter.run_fixed()

if __name__ == "__main__":
    main()
