import sys

def interpret(code):
    lines = code.strip().split('\n')
    instructions = []
    labels = {}
    
    # Pass 1: Parse and collect labels
    for line in lines:
        parts = line.split('#')[0].strip().split()
        if not parts:
            continue
        cmd = parts[0].upper()
        arg = parts[1] if len(parts) > 1 else None
        
        if cmd == 'MARK':
            if not arg:
                raise ValueError("Syntax Error: MARK requires a label argument")
            labels[arg] = len(instructions)
        else:
            instructions.append((cmd, arg))
            
    # Pass 2: Execute
    registers = {}
    selected_cog = 0
    pc = 0
    
    def get_val(reg=None):
        r = selected_cog if reg is None else reg
        return registers.get(r, 0)
        
    def set_val(val, reg=None):
        r = selected_cog if reg is None else reg
        registers[r] = val & 0xFFFFFFFF  # 32-bit wrap

    while pc < len(instructions):
        cmd, arg = instructions[pc]
        
        if cmd == 'COG':
            if arg is None: raise ValueError("COG requires a register ID")
            selected_cog = int(arg)
        elif cmd == 'SET':
            if arg is None: raise ValueError("SET requires a value")
            set_val(int(arg))
        elif cmd == 'WIND':
            set_val(get_val() + 1)
        elif cmd == 'UNWIND':
            set_val(get_val() - 1)
        elif cmd == 'CONNECT':
            if arg is None: raise ValueError("CONNECT requires a register ID")
            set_val(get_val() + get_val(int(arg)))
        elif cmd == 'CHIME':
            print(chr(get_val() % 256), end='', flush=True)
        elif cmd == 'RING':
            print(get_val(), end='', flush=True)
        elif cmd == 'READ':
            char = sys.stdin.read(1)
            set_val(ord(char) if char else 0)
        elif cmd == 'SPRING':
            if arg is None: raise ValueError("SPRING requires a label")
            if get_val() != 0:
                if arg not in labels: raise ValueError(f"Label '{arg}' not found")
                pc = labels[arg]
                continue
        elif cmd == 'FALL':
            if arg is None: raise ValueError("FALL requires a label")
            if get_val() == 0:
                if arg not in labels: raise ValueError(f"Label '{arg}' not found")
                pc = labels[arg]
                continue
        else:
            raise ValueError(f"Unknown instruction: {cmd}")
        
        pc += 1

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 interpreter.py <file.clk>")
        sys.exit(1)
        
    try:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            code = f.read()
        interpret(code)
    except FileNotFoundError:
        print(f"Error: File {sys.argv[1]} not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error execution halted: {e}")
        sys.exit(1)
