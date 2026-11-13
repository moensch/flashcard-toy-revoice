# The card code (unsolved)

Notes for anyone who wants to make custom cards or build a replacement reader.

- Each card edge has **11 positions** (holes or marks). The sensor board
  (`ZP-BBC-N9 V1.1`) has **8** IR sensors that light up. The two far-right
  positions have no sensor, as far as we can tell.
- Each card has two sides with one word each. **The reader reads the code printed
  on the opposite side** from the word facing you. The code under the "69" word is
  the code that plays 70, and vice versa.
- Samples, written left to right as printed (1 = mark) → sound played:

| Code | Plays |
|---|---|
| `00010000011` | 70 |
| `00010001000` | 72 |
| `00010000111` | 71 |
| `00010000110` | 95 |

These don't fit a plain binary encoding, and we didn't decode them. For a custom
reader, a "learn mode" lookup table (scan each card once, store code → number)
avoids the problem entirely.

Ideas for later: if the toy plays `NNN.f1a` for codes beyond 224, a homemade card
plus a new directory entry (see the end-of-directory flag in
[filesystem.md](filesystem.md)) would give you an easter-egg card.
