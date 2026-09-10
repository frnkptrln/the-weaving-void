# The Weaving Void

*Visible meaning. Hidden operation. One shared surface.*

**The Weaving Void** is an executable laboratory for artifacts that support
more than one reading: prose and program, surface and generator, visible
meaning and hidden operation.

The repository began as an archive of esoteric programming languages. Those
languages remain as working studies, but the central object is now the
**weave**: the deterministic relation that lets a human-readable surface carry
an executable thread.

## Start here

- **[The Weave](core/the-weave.md)** defines the operational spine and the
  boundary of the project.
- **[Subtext](weaves/subtext)** is the first canonical specimen: ordinary prose
  deterministically compiles to a Marginalia program and leaves the trace
  `VOID`.
- **[Constructing Subtext](weaves/subtext/construction)** takes a first bounded
  step in the inverse direction: select authored sentences for a target thread.
  A second surface tells a garden story while carrying the same `VOID` program.
- **[Authoring Subtext](weaves/subtext/AUTHORING.md)** plans sentence shapes,
  diagnoses a draft, and proposes repairs using authored candidates.
- **[Multiple readers](weaves/subtext/multiple_readers)** gives one crossroads
  story two public readings, yielding `GO` or `NO` through different routing.
- **[Marginalia](Marginalia)** is the first canonical loom, a language of notes,
  doubt, folding, and verification.

```text
surface --reader/key--> thread --loom/runtime--> trace
```

The inverse direction is the harder construction problem: given an intended
human meaning and a desired program or trace, construct a surface that carries
both.

## Reproduce the first weave

```bash
python3 weaves/subtext/reader.py weaves/subtext/carrier.md --explain
python3 Marginalia/interpreter.py weaves/subtext/extracted.mrg
python3 -m unittest weaves.subtext.test_reader
```

The carrier, public reader profile, extracted thread, expected trace, and
mutation tests are all committed together. The specimen uses visible sentence
features only; it is an experiment in dual reading, not secrecy or
cryptography.

## Construct another surface

```bash
python3 -m weaves.subtext.weaver weaves/subtext/construction/target.mrg --bank weaves/subtext/construction/sentences.json
python3 -m unittest discover -s weaves/subtext -t .
```

The weaver chooses the first unused sentence that encodes each target
instruction, then verifies the complete extraction. The ordered bank contains
human-authored alternatives. Changing its order can change the surface without
changing the thread. This is finite sentence selection; it does not generate
meaning or solve construction for arbitrary programs or traces.

To write a carrier yourself, the authoring workflow gives constraints before
you need a sentence bank, then diagnoses your draft:

```bash
python3 -m weaves.subtext.authoring plan weaves/subtext/construction/target.mrg
python3 -m weaves.subtext.authoring check weaves/subtext/construction/target.mrg weaves/subtext/construction/draft.md
```

The supplied draft intentionally differs by one final word; `check` exits 1
and explains the changed operand. See the [authoring guide](weaves/subtext/AUTHORING.md)
for repair, structured reports, and the distinction between minimal sentence
changes and preserving human meaning.

## The archive

The existing languages are retained as studies of different carriers, memory
models, and runtimes:

| Language | Study | Implementation status |
| :--- | :--- | :--- |
| **[Distaff](./Distaff)** | Auditory drafts and a bridge from notation to execution | Working |
| **[Vortex](./Vortex)** | Early cyclic tape-machine and syntax study | Working |
| **[MandelMemory](./MandelMemory)** | Spatial and dynamical memory addressing | Working |
| **[SFract](./SFract)** | Thread construction through L-system growth | Working |
| **[Entanglement](./Entanglement)** | Linked-state variables and destructive observation | Working |
| **[Gastronomy](./Gastronomy)** | Culinary surface vocabulary over a tape machine | Working |
| **[Clockwork](./Clockwork)** | Register-machine computation and synchronization | Working |
| **[Bloom](./Bloom)** | Constraint-oriented continuous simulation | Concept sketch |
| **[Marginalia](./Marginalia)** | Annotated memory, compression, and verification | Working / canonical loom |

New languages should be added only when they test a property that the current
archive cannot: a new kind of surface, reader, loom, trace, or transformation.

## Project discipline

A canonical weave must include:

1. a meaningful human-facing surface;
2. a public deterministic reader;
3. the extracted thread;
4. an executable loom;
5. the expected trace;
6. tests for invariance and structural failure.

Zero-width characters, opaque metadata, appended payloads, and secret binary
blobs are outside the canonical scope because the visible and executable
readings do not depend on the same material.

## Running the archive

Interpreters target Python 3.10+:

```bash
python3 <LanguageFolder>/interpreter.py <SourceFile>
```

Bloom additionally depends on NumPy:

```bash
python3 -m pip install -r Bloom/requirements.txt
```

Run the full archive smoke test with:

```bash
python3 scripts/smoke_test.py
```

## Related work

- [`systems-and-intelligence`](https://github.com/frnkptrln/systems-and-intelligence)
  holds the broader Trace-to-Generator and construction-versus-deduction
  questions. This repository is a narrow executable laboratory for them.
- [`the-weaving-sound`](https://github.com/frnkptrln/the-weaving-sound) explores
  generative organization in sound. Distaff is a deliberate bridge, while the
  projects keep separate runtimes and scopes.

## License

MIT License — see [LICENSE](LICENSE).
