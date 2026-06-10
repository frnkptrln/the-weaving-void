# The Weaving Void: An Archival Collection of Esoteric Languages

*"To code is to weave logic into the very fabric of the void."*

Welcome to **The Weaving Void**, an expanding grimoire and repository dedicated to the exploration of unique computational patterns, unusual paradigms, and philosophical concepts expressed through Esoteric Programming Languages (Esolangs).

Every language housed within this collection pushes against conventional programming. The archive is designed not for production efficiency, but as a medium for unconventional problem-solving, cognitive challenges, and digital artistry.

## The Archive

Explore the distinct paradigms we've discovered and documented:

| Language | Paradigm & Concept | Status |
| :--- | :--- | :--- |
| **[Distaff](./Distaff)** | Musical weaving via 4-note auditory sequences. | Working |
| **[Vortex](./Vortex)** | High-speed Brainfuck successor with automated memory warping and nested logic. | Working |
| **[MandelMemory](./MandelMemory)** | Chaos-driven navigation mapped on the Mandelbrot set. | Working |
| **[SFract](./SFract)** | Biological "seed" growth and mutation via L-Systems. | Working |
| **[Entanglement](./Entanglement)** | Quantum-inspired linked logic pairs with entangled states. | Working |
| **[Gastronomy](./Gastronomy)** | Culinary recipe-based tape programming, utilizing ingredients and cooking actions. | Working |
| **[Clockwork](./Clockwork)** | Steampunk-inspired register machine with multi-cog synchronization. | Working |
| **[Bloom](./Bloom)** | Constraint-based continuous simulation, free-energy minimization, and substrate vetos. | Experimental |
| **[Marginalia](./Marginalia)** | Annotation-based contextual tape programming with folding and verification. | Experimental |

## Core Implementation Principles

1. **Computational Expressiveness:** Each language is designed around a concrete computational model, whether through tapes, recursive seeds, registers, graph-like state, or continuous simulation.
2. **Robust Interpreters:** Interpreters are written cleanly in Python 3.10+, featuring clear error handling and distinct tokenization.
3. **Comprehensive Documentation:** Each language has its own detailed `README.md` containing syntax diagrams and memory models.
4. **Verification:** Every language includes a proof-of-concept example plus a loop-driven program that actually computes (countdowns, alphabets, factorials), and the archive includes a smoke test for all of them.
5. **Visualization:** Distaff, MandelMemory, SFract, and Bloom ship a `visualizer.py` that renders programs as staff notation, Mandelbrot maps, botanical sketches, or coherence trajectories.

## Getting Started

To explore a language, navigate to its respective directory and follow the instructions in the local `README.md`.

Generally, you can execute a script by running its interpreter:
```bash
python3 <LanguageFolder>/interpreter.py <SourceFile>
```

Bloom depends on NumPy:
```bash
python3 -m pip install -r Bloom/requirements.txt
```

To run the full archive smoke test:
```bash
python3 scripts/smoke_test.py
```

## License
MIT License - see [LICENSE](LICENSE) for details.
