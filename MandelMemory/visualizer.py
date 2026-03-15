import sys
import re

def is_in_mandelbrot(c, max_iter=100):
    z = complex(0, 0)
    for i in range(max_iter):
        z = z*z + c
        if abs(z) > 2:
            return False
    return True

class MandelMemoryVisualizer:
    def __init__(self, code):
        self.code = code
        self.points = self.extract_points(code)

    def extract_points(self, code):
        # We need to simulate the pointer movement to find accessed points
        code = re.sub(r'#.*', '', code)
        pattern = r'(T\(-?\d*\.?\d*[+-]\d*\.?\d*i\))|(T\(-?\d*\.?\d*i?\))|(\+)|(-)'
        
        z = complex(0, 0)
        points = []
        for match in re.finditer(pattern, code):
            if match.group(1) or match.group(2):
                t_expr = match.group(1) if match.group(1) else match.group(2)
                inner = t_expr[2:-1].replace('i', 'j')
                try:
                    c_val = complex(inner)
                    z = z**2 + c_val
                except: pass
            elif match.group(3) or match.group(4):
                if abs(z) <= 2:
                    points.append(z)
        return points

    def visualize(self, width=80, height=40):
        # Range
        x_min, x_max = -2.0, 0.6
        y_min, y_max = -1.2, 1.2
        
        grid = [[' ' for _ in range(width)] for _ in range(height)]
        
        # Draw Mandelbrot
        for y_idx in range(height):
            for x_idx in range(width):
                x = x_min + (x_max - x_min) * x_idx / width
                y = y_min + (y_max - y_min) * y_idx / height
                if is_in_mandelbrot(complex(x, y)):
                    grid[y_idx][x_idx] = '.'
        
        # Plot points
        for p in self.points:
            x_idx = int((p.real - x_min) / (x_max - x_min) * width)
            y_idx = int((p.imag - y_min) / (y_max - y_min) * height)
            if 0 <= x_idx < width and 0 <= y_idx < height:
                grid[y_idx][x_idx] = 'X'
        
        print("\nMandelMemory Map ('.' = Mandelbrot Set, 'X' = Memory Variable)")
        print("+" + "-" * width + "+")
        for row in grid:
            print("|" + "".join(row) + "|")
        print("+" + "-" * width + "+")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 visualizer.py <filename>")
        sys.exit(1)
        
    filename = sys.argv[1]
    with open(filename, 'r') as f:
        code = f.read()
    
    vis = MandelMemoryVisualizer(code)
    vis.visualize()

if __name__ == "__main__":
    main()
