import sys

# Turtle headings in 45-degree steps, starting straight up (screen coordinates).
DIRECTIONS = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]
SEGMENT_CHARS = ['|', '/', '-', '\\', '|', '/', '-', '\\']

class SFractVisualizer:
    def __init__(self, filename):
        self.iterations = 0
        self.axiom = ""
        self.rules = {}
        self.load_seed(filename)
        self.stages = self.grow_stages()

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

    def grow_stages(self):
        stages = [self.axiom]
        current = self.axiom
        for _ in range(self.iterations):
            current = "".join(self.rules.get(char, char) for char in current)
            stages.append(current)
        return stages

    def trace_turtle(self, program):
        # Botanical reading of the grown seed: F draws a segment,
        # +/- turn by 45 degrees, [ and ] branch off and return.
        x, y = 0, 0
        heading = 0
        stack = []
        cells = {}

        for cmd in program:
            if cmd == 'F':
                dx, dy = DIRECTIONS[heading]
                x, y = x + dx, y + dy
                cells[(x, y)] = SEGMENT_CHARS[heading]
            elif cmd == '+':
                heading = (heading - 1) % 8
            elif cmd == '-':
                heading = (heading + 1) % 8
            elif cmd == '[':
                stack.append((x, y, heading))
            elif cmd == ']':
                if stack:
                    x, y, heading = stack.pop()

        cells[(0, 0)] = '@'  # the seed itself
        return cells

    def visualize(self, max_render=200000):
        print("SFract Growth Stages")
        for i, stage in enumerate(self.stages):
            shown = stage if len(stage) <= 60 else stage[:57] + "..."
            print(f"  Gen {i}: {len(stage):>6} cells | {shown}")

        program = self.stages[-1]
        if len(program) > max_render:
            print(f"\nSeed too large to sketch ({len(program)} cells).")
            return

        cells = self.trace_turtle(program)
        xs = [x for x, _ in cells]
        ys = [y for _, y in cells]
        x_min, x_max = min(xs), max(xs)
        y_min, y_max = min(ys), max(ys)

        print(f"\nBotanical Sketch ('@' = seed, canopy {x_max - x_min + 1}x{y_max - y_min + 1})")
        for y in range(y_min, y_max + 1):
            row = "".join(cells.get((x, y), ' ') for x in range(x_min, x_max + 1))
            print(row.rstrip())

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 visualizer.py <filename>")
        sys.exit(1)

    filename = sys.argv[1]
    try:
        visualizer = SFractVisualizer(filename)
        visualizer.visualize()
    except FileNotFoundError:
        print(f"Error: File {filename} not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
