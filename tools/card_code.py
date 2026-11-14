"""Convert between card numbers and the 11-position card code. See docs/barcode.md.

Usage: python3 tools/card_code.py 70             -> code to print for sound 70
       python3 tools/card_code.py 00010000110    -> sound that code plays
       python3 tools/card_code.py --510 300      -> same, for the 510-word version

Codes are written left to right as printed on the card, word side up, 1 = mark.
Remember the code goes on the *other* side of the card from the word it plays.
"""
import sys

# Value of each printed position, left to right. 0 = no sensor / never marked.
WEIGHTS = [0, 0, 128, 64, 32, 0, 16, 8, 2, 4, 1]            # our 224-word toy: 2 and 4 swapped
WEIGHTS_510 = [0, 256, 128, 64, 32, 0, 16, 8, 4, 2, 1]      # 510-word version: plain order


def decode(code, weights=WEIGHTS):
    return sum(w for w, c in zip(weights, code) if c == "1")


def encode(n, weights=WEIGHTS):
    assert 0 < n < 2 * max(weights), "%d doesn't fit this code" % n
    return "".join("1" if w and n & w else "0" for w in weights)


if __name__ == "__main__":
    args = sys.argv[1:]
    weights = WEIGHTS
    if args and args[0] == "--510":
        weights, args = WEIGHTS_510, args[1:]
    for arg in args:
        if len(arg) == len(weights) and set(arg) <= {"0", "1"}:
            print(arg, "->", decode(arg, weights))
        else:
            print(arg, "->", encode(int(arg), weights))
