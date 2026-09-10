# The Weave

**Status:** experimental spine

`the-weaving-void` studies artifacts that support more than one reading: a
human-readable surface and an executable structure. Its central object is not
an isolated esoteric language, but the relation that makes one artifact carry
both readings.

## Operational model

```text
surface --reader/key--> thread --loom/runtime--> trace
```

- **Surface** — the visible carrier: prose, notation, spatial structure, or
  another human-facing artifact.
- **Thread** — the symbol stream extracted from that surface.
- **Weave** — the public rule connecting surface features to the thread.
- **Loom** — the interpreter or runtime that executes the thread.
- **Trace** — output or state transition left by execution.
- **Void** — the underdetermined space of alternative readers, threads, and
  generators that a surface does not select by itself.

The complete generator of a trace is therefore not the source text alone. It
includes the reader, its key or profile, the loom, and relevant runtime state.

## Forward and inverse problems

The forward problem is verification:

```text
given surface + weave + loom, derive and execute the thread
```

The inverse problem is construction:

```text
given intended human meaning + desired thread or trace, construct a surface
```

Verification can be mechanical. Construction must satisfy two constraint sets
at once: the surface must remain meaningful to a reader while its visible
structure must encode a valid program. This is the repository's concrete link
to the construction-versus-deduction and Trace-to-Generator questions explored
in `systems-and-intelligence`.

## What counts as a weave

A canonical specimen must satisfy all of these conditions:

1. The surface is meaningful without executing it.
2. The executable structure is derived from visible surface features.
3. The reader is deterministic and inspectable.
4. Surface edits have explainable effects on the extracted thread.
5. The expected thread and trace are committed beside the carrier.
6. Robustness and failure behavior are tested.

Zero-width characters, opaque metadata, appended payloads, and secret binary
blobs do not qualify. They may hide data, but they do not make the two readings
depend on the same visible material. This work is about dual reading, not
secrecy or cryptography.

## First specimen: Subtext

`weaves/subtext` is the first canonical weave. Each sentence remains ordinary
prose while its initial letter selects a Marginalia operation. Sentence shape
provides an operand. The public reader extracts a Marginalia thread, which the
existing Marginalia loom executes.

Subtext is deliberately a weave profile rather than a tenth virtual machine.
It tests whether an existing language can inhabit a second, human-readable
surface.

### A bounded inverse experiment

`weaves/subtext/construction` adds a second surface for the same thread and
trace. A deterministic weaver selects one authored sentence per instruction
from an ordered bank, consumes each selected entry once, and checks that the
result extracts to the requested thread. A missing candidate is an explicit
construction failure.

This demonstrates construction within a finite supplied vocabulary and
non-uniqueness of surface for a fixed reader and thread. It does not infer a
program from a desired trace, generate prose from an intended meaning, or
establish that every bank ordering preserves coherence. The author supplies
the meaning; the tool checks the executable constraints.

## Archive as a set of studies

The existing languages remain useful, but their role is now clearer:

- **Marginalia** is the first canonical loom for textual weaving.
- **SFract** studies a thread constructed through generative growth.
- **MandelMemory** studies spatial and dynamical addressing.
- **Distaff** studies an auditory carrier and forms a narrow bridge to
  `the-weaving-sound`.
- **Clockwork** and **Entanglement** are alternative machine models.
- **Vortex** and **Gastronomy** are early syntax and carrier studies.
- **Bloom** remains a concept sketch until its documented semantics and runtime
  model coincide.

The archive is evidence and material for comparison. New languages should be
added only when they test a new property of surfaces, readers, looms, or traces.

## Next questions

- Which edits preserve the human reading, the executable reading, or both?
- Can several readers extract different valid threads from one surface?
- How much executable constraint can prose carry before readability collapses?
- Can a weaver construct or repair a carrier for a desired trace?
- Given only a surface and trace, which reader/runtime pairs remain plausible?
- When are two woven artifacts the same: by surface, thread, loom, or trace?

These are experimental questions. The repository makes no claim that one
reader is the true interpretation of a surface, or that recovering a generator
from a trace is unique.
