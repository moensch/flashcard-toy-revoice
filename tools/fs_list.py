"""List the JieLi filesystem in a dump, and optionally extract every file.

Usage: python3 tools/fs_list.py DUMP.bin [--extract DIR]

Prints one line per directory entry: position, name, type, offset, length, and
whether the entry and data checksums pass. --extract writes each file to DIR
(e.g. DIR/001.f1a); decode those with testf1a_dec.exe (see windows/README.md).
"""
import os, sys
from common import TYPE_DIR, crc16, entries

img = open(sys.argv[1], "rb").read()
outdir = sys.argv[sys.argv.index("--extract") + 1] if "--extract" in sys.argv else None
if outdir:
    os.makedirs(outdir, exist_ok=True)

n = used = 0
for pos, name, typ, off, ln, eok, dcrc in entries(img):
    kind = "dir " if typ == TYPE_DIR else "file"
    ok = "entry %s, data %s" % ("ok" if eok else "BAD", "-" if typ == TYPE_DIR else
                                ("ok" if crc16(img[off:off + ln]) == dcrc else "BAD"))
    print("0x%04x  %-16s %s  0x%05x  %7d  %s" % (pos, name, kind, off, ln, ok))
    if typ != TYPE_DIR:
        n += 1; used += ln
        if outdir:
            open(os.path.join(outdir, name), "wb").write(img[off:off + ln])
print("%d files, %d bytes of audio%s" % (n, used, ", extracted to " + outdir if outdir else ""))
