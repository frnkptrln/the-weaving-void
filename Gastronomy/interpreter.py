import sys

def interpret(file_path):
    try:
        with open(file_path, 'r') as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"Error: Recipe '{file_path}' not found.")
        sys.exit(1)

    tokens = [
        ("simmer until reduced", "["),
        ("serve", "]"),
        ("add", "+"),
        ("reduce", "-"),
        ("mix", ">"),
        ("stir", "<"),
        ("taste", "."),
        ("substitute", ",")
    ]

    bf_code = ""
    lower_source = source_code.lower()
    i = 0
    while i < len(lower_source):
        match_found = False
        for token, bf_char in tokens:
            if lower_source.startswith(token, i):
                # Ensure word boundary (must not be followed by alphabet)
                end_pos = i + len(token)
                if end_pos == len(lower_source) or not lower_source[end_pos].isalpha():
                    bf_code += bf_char
                    i += len(token)
                    match_found = True
                    break
        if not match_found:
            i += 1

    run_bf(bf_code)

def run_bf(code):
    tape = [0] * 30000
    ptr = 0
    pc = 0
    
    # Precompute loop jumps
    loop_map = {}
    stack = []
    for i, char in enumerate(code):
        if char == '[':
            stack.append(i)
        elif char == ']':
            if not stack:
                print("Error: Spoiled recipe. Unmatched 'Serve' (]).")
                sys.exit(1)
            start = stack.pop()
            loop_map[start] = i
            loop_map[i] = start
    if stack:
        print("Error: Spoiled recipe. Unmatched 'Simmer until reduced' ([).")
        sys.exit(1)
        
    while pc < len(code):
        command = code[pc]
        if command == '>':
            ptr = (ptr + 1) % len(tape)
        elif command == '<':
            ptr = (ptr - 1) % len(tape)
        elif command == '+':
            tape[ptr] = (tape[ptr] + 1) % 256
        elif command == '-':
            tape[ptr] = (tape[ptr] - 1) % 256
        elif command == '.':
            sys.stdout.write(chr(tape[ptr]))
            sys.stdout.flush()
        elif command == ',':
            char = sys.stdin.read(1)
            if char:
                tape[ptr] = ord(char)
            else:
                tape[ptr] = 0
        elif command == '[':
            if tape[ptr] == 0:
                pc = loop_map[pc]
        elif command == ']':
            if tape[ptr] != 0:
                pc = loop_map[pc]
        pc += 1

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 interpreter.py <recipe.gstr>")
        sys.exit(1)
    interpret(sys.argv[1])
