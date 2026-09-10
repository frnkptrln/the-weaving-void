# One surface, two readers

At a river crossing, two keepers offer conflicting advice. The travelers must
choose whom to follow, and neither keeper can make the crossing for them.
This ten-sentence surface also carries two executable readings: `west.json`
extracts a thread that prints `GO`; `east.json` extracts one that prints `NO`.

Both profiles are public. They use the existing Subtext reader, the same
sentence boundaries, and the same operand rule: `8 * word_count +
final_word_length`. Their operation maps differ only at `T`: west means
`left`, east means `right`. Both print through `quote`. The difference is
which stored value they visit, not how an identical value is displayed.

## Follow the crossing

| Sentence | Encoded instruction | Effect |
| :--- | :--- | :--- |
| 1. Lanterns divide darkness. | `left 32` | Move from the empty origin to margin -32. |
| 2. Nearer, the western keeper… | `note 71` | Store the value for `G` at -32. |
| 3. Returning through the square… | `right 64` | Move across the origin to margin +32. |
| 4. Nearby, the eastern keeper… | `note 78` | Store the value for `N` at +32. |
| 5. Listening demands patience. | `left 32` | Return to the origin. |
| 6. Turning changes bearings. | West: `left 32`; east: `right 32` | Select a keeper's margin. |
| 7. Questions follow whichever voice we choose. | `quote` | Print `G` or `N`. |
| 8. Certainty fades as the river rises. | `forget` | Clear the selected margin. |
| 9. Neither voice can carry our feet across the current. | `note 79` | Store the value for `O` in that margin. |
| 10. Quietly, we decide… | `quote` | Complete `GO` or `NO`. |

For example, “Turning changes bearings.” has three words and an eight-letter
final word, so both readers derive operand `8 * 3 + 8 = 32`. The profile
supplies the direction. The unselected margin retains its original value.

## Reproduce both readings

Run from the repository root:

```bash
python3 -m weaves.subtext.reader weaves/subtext/multiple_readers/carrier.md --weave weaves/subtext/multiple_readers/west.json --explain
python3 -m weaves.subtext.reader weaves/subtext/multiple_readers/carrier.md --weave weaves/subtext/multiple_readers/east.json --explain
python3 Marginalia/interpreter.py weaves/subtext/multiple_readers/west.mrg
python3 Marginalia/interpreter.py weaves/subtext/multiple_readers/east.mrg
python3 -m unittest weaves.subtext.test_multireader
```

The reader commands reproduce `west.mrg` and `east.mrg` exactly. The interpreter
commands emit `GO` and `NO` respectively, without a trailing newline. The
committed trace files add one newline for readability. Tests compare each
fresh extraction and execution against these artifacts, check both CLI
readings, and check the resulting margins.

Whitespace reflow preserves both programs. Replacing “bearings” with
“bearing” changes the turn's operand to 31: both readers visit an empty margin
and emit `\x00O` (a NUL followed by `O`). This is a deterministic diagnostic of
the visible constraint; the extractor does not reject a grammatical revision
merely because it no longer reaches the intended values.

## What the example establishes

A surface can support two different executable threads under two explicit
reader profiles. The story makes the choice between voices legible to a human;
the runtime makes the effect of that choice inspectable. No runtime operation
understands the story, and neither trace determines whether crossing the river
is wise. The profiles were deliberately authored together with the surface;
this is not a claim of secrecy, a unique decoder, or automatic discovery of
alternative meanings.
