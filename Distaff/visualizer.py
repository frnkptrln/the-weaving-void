import sys
import re

class DistaffVisualizer:
    def __init__(self, code):
        self.code = code
        self.notes_map = {
            'C': 0, 'b': 1, 'a': 2, 'g': 3, 'f': 4, 'e': 5, 'd': 6, 'c': 7
        }
        self.tokens = self.parse(code)

    def parse(self, code):
        code = re.sub(r'#.*', '', code)
        tokens = []
        # Find drafts: 4 notes separated by hyphens (e.g., c-d-e-f)
        # Find loops ([ and ]), and pauses (_)
        pattern = r'([cdefgabC]-[cdefgabC]-[cdefgabC]-[cdefgabC])|(\[)|(\])|(_)'
        
        for match in re.finditer(pattern, code):
            if match.group(1):
                draft = match.group(1).replace('-', '')
                tokens.append(('draft', draft))
            elif match.group(2):
                tokens.append(('marker', '['))
            elif match.group(3):
                tokens.append(('marker', ']'))
            elif match.group(4):
                tokens.append(('marker', '_'))
        return tokens

    def visualize(self):
        # We'll represent each draft as 4 columns and markers as 1 column each.
        output_rows = ["" for _ in range(8)]
        labels = ['C', 'b', 'a', 'g', 'f', 'e', 'd', 'c']
        
        # Initialize staff lines
        for i in range(8):
            output_rows[i] = f"{labels[i]} |-"

        for type, val in self.tokens:
            if type == 'draft':
                for note in val:
                    pos = self.notes_map[note]
                    for i in range(8):
                        if i == pos:
                            output_rows[i] += "O-"
                        else:
                            output_rows[i] += "--"
                for i in range(8):
                    output_rows[i] += "|"
            else:
                for i in range(8):
                    # Represent markers differently
                    if val == '[':
                        output_rows[i] += "[ "
                    elif val == ']':
                        output_rows[i] += " ]"
                    elif val == '_':
                        output_rows[i] += " _ "
                    else:
                        output_rows[i] += " - "
                for i in range(8):
                    output_rows[i] += "|"

        for row in output_rows:
            print(row)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 visualizer.py <filename>")
        sys.exit(1)
        
    filename = sys.argv[1]
    try:
        with open(filename, 'r') as f:
            code = f.read()
        visualizer = DistaffVisualizer(code)
        visualizer.visualize()
    except FileNotFoundError:
        print(f"Error: File {filename} not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
