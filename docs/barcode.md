# The card code

Notes for anyone who wants to make custom cards or build a replacement reader.

## How it's read

- Each card edge has **11 positions** where a black mark can be printed. The sensor
  board (`ZP-BBC-N9 V1.1`) has **8** IR sensors.
- Each card has two sides with one word each. **The reader reads the code printed
  on the opposite side** from the word facing you. The code under the "69" word is
  the code that plays 70, and vice versa.

## Decoding

The code is the sound number in binary, with the bits in an unusual order. Number
the positions 0–10 left to right as printed, word side up:

| Position | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Value | – | – | 128 | 64 | 32 | – | 16 | 8 | **2** | **4** | 1 |

Add up the values of the marked positions to get the sound number, so card *N*
plays `NNN.f1a` (see [filesystem.md](filesystem.md)). Positions 0, 1 and 5 were never
marked on any card we checked, which fits the 8 sensors. Note that 2 and 4 are
swapped compared with plain binary.

`tools/card_code.py` converts both ways:

```
$ python3 tools/card_code.py 70 00010000011
70 -> 00010000110
00010000011 -> 69
```

## Evidence

Every code we photographed decodes to the number on the other side of its card:

| Printed under | Code | Decodes to |
|---|---|---|
| 1 bus | `00000000100` | 2 |
| 2 jeep | `00000000001` | 1 |
| 5 watering cart | `00000000110` | 6 |
| 6 sports car | `00000000011` | 5 |
| 7 excavator | `00000001000` | 8 |
| 8 car | `00000000111` | 7 |
| 9 taxi | `00000001100` | 10 |
| 10 train | `00000001001` | 9 |
| 11 bike | `00000001010` | 12 |
| 12 motorbike | `00000001101` | 11 |
| 13 helicopter | `00000001110` | 14 |
| 14 police car | `00000001011` | 13 |
| 15 ambulance | `00000010000` | 16 |
| 31 washing machine | `00001000000` | 32 |
| 69 potato | `00010000110` | 70 |
| 70 | `00010000011` | 69 |
| 71 | `00010001000` | 72 |
| 72 | `00010000111` | 71 |
| 127 hat | `00100000000` | 128 |
| 223 sit down | `00111000000` | 224 |

The 16 position was the hardest to read from a photo. A printed card with the mark at
position 5 played 16 too low; with it at position 6 the toy read it correctly.

## Printed cards work

We printed replacements for lost cards (59 x 88 mm, folded and glued
back to back) and the toy reads them like the originals: 65/66, 91/92. Keep the marks
on 11 equal slots across the full card width, along a white strip about 8.5 mm high
at the bottom edge, and print them in true black (laser toner). Colour inks and
inkjet "rich black" may be invisible to the IR sensors.

## Custom cards

The 8 bits allow numbers up to 255, so 225–255 are free. For an easter-egg card:

1. Pick a number, e.g. 225, and get its code: `python3 tools/card_code.py 225`.
2. Print or paint that code on the side **opposite** the picture, with marks the same
   size and position as on a real card. Matte black, like the originals, is safest
   for IR.
3. Add a `225.f1a` entry to the directory and move the "last entry" flag to it
   (see [filesystem.md](filesystem.md)). We haven't tested yet whether the firmware
   plays numbers above 224.
