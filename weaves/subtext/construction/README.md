# Constructing a second Subtext surface

This specimen describes neighbors planning a shared garden. Their drawing
changes through discussion and experience; a finished plan still needs care
and work to become a living place. It carries the same Marginalia thread and
`VOID` trace as the original Subtext specimen, through different prose.

`sentences.json` is an ordered bank of authored candidate sentences. For each
target instruction, the weaver chooses the first unused matching sentence in
bank order. It writes one sentence per line. The first eleven candidates form
the committed surface; later candidates offer alternatives for each distinct
instruction. Reordering the bank can change the surface while preserving the
thread, though coherence must still be judged by a reader.

From the repository root:

```bash
python3 -m weaves.subtext.weaver weaves/subtext/construction/target.mrg --bank weaves/subtext/construction/sentences.json
python3 -m weaves.subtext.reader weaves/subtext/construction/carrier.md --explain
python3 Marginalia/interpreter.py weaves/subtext/construction/target.mrg
```

The first command reproduces `carrier.md`. Reading that carrier reproduces
`target.mrg` exactly; executing the target emits `VOID`, recorded in `trace.txt`
with a final newline for file readability.

This is finite selection under visible sentence constraints. The weaver does
not invent prose, understand the intended garden story, or guarantee that
arbitrary candidate combinations remain meaningful. A request fails when the
bank has no unused sentence for an instruction. Extending coverage requires
authoring and checking more candidates. The bank encodes a small set of
choices, not a general solution to construction from meaning or trace.

## Edit and repair the story

`draft.md` changes the first final word from `spaces` to `paths`, leaving its
ten-word sentence one letter short of the desired operand. The authoring
checker identifies `note 85` where the target requires `note 86`. The repair
tool restores the committed carrier with one sentence replacement, selected
by minimum word-token distance from the bank:

```bash
python3 -m weaves.subtext.authoring check weaves/subtext/construction/target.mrg weaves/subtext/construction/draft.md
python3 -m weaves.subtext.authoring repair weaves/subtext/construction/target.mrg weaves/subtext/construction/draft.md --bank weaves/subtext/construction/sentences.json
```

The first command deliberately exits 1 for the mismatch. The second writes the
repaired carrier to stdout and the edit explanation to stderr. See the
[authoring guide](../AUTHORING.md) for planning, structured diagnostics, and
the limits of repair from authored candidates.
