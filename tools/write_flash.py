"""Write a new image to the chip, touching only the 4 KB sectors that differ.

Usage: python3 tools/write_flash.py CURRENT.bin TARGET.bin [--check-only]

CURRENT.bin must be exactly what the chip holds now: use a fresh tools/dump.py
backup. Before erasing anything, every sector to be written is read back and
compared against CURRENT; if any differs, nothing is written. --check-only stops
after that comparison (a dry run).

Data sectors are written first and the directory sectors (0x0000-0x1fff) last, so
the toy only switches to the new audio once all of it is in place and verified.
A sector that already holds TARGET is skipped, so an interrupted run can simply be
re-run with the same arguments.
"""
import os, struct, sys, tempfile
from common import SECTOR, SIZE, run_job, upload

DIR_END = 0x2000

cur, tgt = (open(p, "rb").read() for p in sys.argv[1:3])
check_only = "--check-only" in sys.argv
assert len(cur) == len(tgt) == SIZE

changed = [a for a in range(0, SIZE, SECTOR) if cur[a:a + SECTOR] != tgt[a:a + SECTOR]]
changed.sort(key=lambda a: a < DIR_END)                       # directory last
if not changed:
    sys.exit("images are identical, nothing to write")
print("%d sectors to %s" % (len(changed), "check" if check_only else "write"))

with tempfile.TemporaryDirectory() as tmp:
    job = os.path.join(tmp, "job.bin")
    with open(job, "wb") as f:
        for a in changed:
            f.write(struct.pack("<I", a) + cur[a:a + SECTOR] + tgt[a:a + SECTOR])
    upload(job, "job.bin")
sys.exit(run_job("flash", "CHECK_ONLY = %r" % check_only))
