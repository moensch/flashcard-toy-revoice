"""OR-merge several imperfect dumps of the same chip into one.

Usage: python3 tools/merge_reads.py OUT.bin READ1.bin READ2.bin [...]

On a bad connection every read loses a random sprinkling of 1-bits but never gains
any, so OR-ing enough reads recovers the real contents. Reports which files still
fail their checksum, so you know whether more reads are needed.

Caveat: a 16-bit CRC can match by accident. Our first backup had 6 missing bits in
one file whose CRC still passed. When you can, confirm with a clean off-board read.
"""
import sys
from common import SIZE, bad_files

out, reads = sys.argv[1], sys.argv[2:]
img = bytearray(SIZE)
for p in reads:
    d = open(p, "rb").read()
    assert len(d) == SIZE, "%s is not a 512 KB dump" % p
    for i in range(SIZE):
        img[i] |= d[i]
open(out, "wb").write(img)
bad = bad_files(img)
print("merged %d reads -> %s; %d files fail their checksum%s" % (
    len(reads), out, len(bad), (": " + " ".join(bad)) if bad else ""))
