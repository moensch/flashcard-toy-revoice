"""Convert between card numbers and the 11-position card code. See docs/barcode.md.

Usage: python3 tools/card_code.py 70             -> code to print for sound 70
       python3 tools/card_code.py 00010000110    -> sound that code plays

Codes are written left to right as printed on the card, word side up, 1 = mark.
Remember the code goes on the *other* side of the card from the word it plays.
"""
import sys

# Value of each printed position, left to right. 0 = no sensor / never marked.
WEIGHTS = [0, 0, 128, 64, 32, 16, 0, 8, 2, 4, 1]


def decode(code):
    return sum(w for w, c in zip(WEIGHTS, code) if c == "1")


def encode(n):
    code = ""
    for w in WEIGHTS:
        code += "1" if w and n & w else "0"
    return code


for arg in sys.argv[1:]:
    if len(arg) == len(WEIGHTS) and set(arg) <= {"0", "1"}:
        print(arg, "->", decode(arg))
    else:
        print(arg, "->", encode(int(arg)))
