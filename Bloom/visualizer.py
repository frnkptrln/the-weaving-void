import re
import sys

import numpy as np

CHART_WIDTH = 64
CHART_HEIGHT = 12


def parse_bloom(source):
    # Mirrors the minimalist parser in interpreter.py.
    agents = source.count('agent ')
    if agents == 0:
        agents = 1

    mode_match = re.search(r'mode:\s*(\w+)', source)
    mode = mode_match.group(1) if mode_match else 'homeostatic'

    return agents, mode


def simulate(num_agents, mode, source_code):
    # Re-runs the substrate exactly like interpreter.py (same seed,
    # same dynamics) while recording the Δ-Coherence trajectory.
    seed = sum((idx + 1) * ord(char) for idx, char in enumerate(source_code)) % (2**32)
    rng = np.random.default_rng(seed)
    state = rng.random(num_agents) * 10
    dt = 0.01
    pain_threshold = 15.0

    coherence = [1.0 / (1.0 + np.var(state))]
    veto = False

    if 'unbounded_growth' in source_code or 'pain > inf' in source_code:
        for _ in range(100):
            noise = rng.normal(0, 0.1, num_agents)
            grad = -np.abs(state) * 0.5
            state += -0.1 * grad * dt + noise * np.sqrt(dt)
            coherence.append(1.0 / (1.0 + np.var(state)))
            if np.mean(state**2) > pain_threshold:
                veto = True
                break

    elif mode == 'harmonic' or 'resonate' in source_code:
        for _ in range(1000):
            noise = rng.normal(0, 0.1, num_agents)
            grad = np.sin(state - np.mean(state))
            state -= 0.5 * grad * dt + noise * np.sqrt(dt)
            coherence.append(1.0 / (1.0 + np.var(state)))
            if np.var(state) < 0.05:
                break

    else:
        target = 37.0 if 'temperature == 37.0' in source_code else 5.0
        for _ in range(1000):
            noise = rng.normal(0, 0.1, num_agents)
            grad = (state - target)
            state -= 0.1 * grad * dt + noise * np.sqrt(dt)
            coherence.append(1.0 / (1.0 + np.var(state)))
            if np.var(state) < 0.05 and abs(np.mean(state) - target) < 0.5:
                break

    return coherence, veto


def render(coherence, veto):
    steps = len(coherence)
    width = min(CHART_WIDTH, steps)
    columns = [coherence[min(int(col * steps / width), steps - 1)] for col in range(width)]

    lo, hi = min(columns), max(columns)
    if hi - lo < 1e-9:
        lo, hi = lo - 0.01, hi + 0.01
    marks = [int(round((value - lo) / (hi - lo) * CHART_HEIGHT)) for value in columns]

    print(f"Δ-Coherence Trajectory ({steps} recorded steps, 'X' = veto)")
    for row in range(CHART_HEIGHT, -1, -1):
        if row == CHART_HEIGHT:
            label = f"{hi:.3f}"
        elif row == CHART_HEIGHT // 2:
            label = f"{(lo + hi) / 2:.3f}"
        elif row == 0:
            label = f"{lo:.3f}"
        else:
            label = "     "

        cells = []
        for col, mark in enumerate(marks):
            if mark == row:
                cells.append('X' if veto and col == width - 1 else '*')
            else:
                cells.append(' ')
        print(f"{label} |{''.join(cells)}")
    print("      +" + "-" * width)

    if veto:
        print("STATUS: Veto triggered (unbounded_growth). Substrate halted.")
    else:
        print("Status: emergent intelligence detected (non-maximizing)")
    print(f"Final Δ-Coherence: {coherence[-1]:.4f}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 visualizer.py <file.blm>")
        sys.exit(1)

    try:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            code = f.read()
    except FileNotFoundError:
        print(f"Error: {sys.argv[1]} not found in the substrate.")
        sys.exit(1)

    if "veto:" not in code:
        print("Fatal Orchestration Error: A Bloom program requires at least one 'veto' constraint.")
        sys.exit(1)

    num_agents, mode = parse_bloom(code)
    if num_agents < 5 and mode != 'harmonic':
        num_agents = 5
    elif num_agents < 100 and mode == 'harmonic':
        num_agents = 100

    coherence, veto = simulate(num_agents, mode, code)
    render(coherence, veto)


if __name__ == "__main__":
    main()
