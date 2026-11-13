"""Read-only check of the Pico <-> flash connection. Writes nothing to the chip.

Usage: python3 tools/check_connection.py [REFERENCE.bin]

Reports whether the chip ID reads back stably, what share of 1-bits a single read
drops, and how many OR'ed reads it takes to get an exact match. With a reference
dump it compares against known-good bytes (pick one whose sectors 0x00000 and
0x40000 haven't changed since); without one it uses the OR of 40 reads as truth.

Run it every time you (re)seat the clip. GOOD means ready to write.
"""
import sys
from common import run_job

REGIONS = [(0x00000, 1024), (0x40000, 1024)]

ref = open(sys.argv[1], "rb").read() if len(sys.argv) > 1 else None
expected = [ref[a:a + n] if ref else None for a, n in REGIONS]
sys.exit(run_job("check", "REGIONS = %r\nEXPECTED = %r" % (REGIONS, expected)))
