"""Back up the whole flash chip to a file.

Usage: python3 tools/dump.py OUT.bin [--reads N]

Reads the chip N times (default 2). If all reads agree, that's the dump. If they
don't (typical for an in-circuit clip), they are OR-merged - a flaky connection only
loses 1-bits, never invents them - and the result is checked against the
filesystem's checksums. Each raw read is kept next to OUT as OUT.readK.bin.

Keep the first dump of an untouched chip somewhere safe. It is your only way back.
"""
import os, sys
from common import SIZE, bad_files, entries, fetch, run_job

out = sys.argv[1]
reads = int(sys.argv[sys.argv.index("--reads") + 1]) if "--reads" in sys.argv else 2
stem = os.path.splitext(out)[0]

imgs = []
for k in range(1, reads + 1):
    if run_job("dump"):
        sys.exit("dump failed")
    fetch("dump.bin", "%s.read%d.bin" % (stem, k))
    imgs.append(open("%s.read%d.bin" % (stem, k), "rb").read())
    assert len(imgs[-1]) == SIZE

if all(i == imgs[0] for i in imgs):
    img = imgs[0]
    print("all %d reads identical" % reads)
else:
    img = bytes(SIZE)
    for i in imgs:
        img = bytes(a | b for a, b in zip(img, i))
    differ = sum(1 for k in range(SIZE) if any(i[k] != img[k] for i in imgs))
    print("reads disagree on %d bytes - OR-merged them. More reads (--reads 12) help." % differ)
open(out, "wb").write(img)

n = sum(1 for e in entries(img) if e[2] == 2)
bad = bad_files(img)
print("%s: %d files, %d with checksum errors%s" % (out, n, len(bad), (": " + " ".join(bad)) if bad else ""))
if not n:
    print("No JieLi directory found - wrong chip, or the reads are garbage.")
