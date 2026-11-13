"""Build a new flash image with replacement sounds, reusing the old sounds' space.

Usage: python3 tools/build_image.py BASE.bin F1A_DIR OUT.bin [--drop 55,56] [--shared 1506]

F1A_DIR holds files named NNNN_anything.f1a; each replaces sound NNNN (card 7 is
0007_bus.f1a -> 007.f1a on the chip, 1502_go-to-rest.f1a -> 1502.f1a). Sounds listed
in --drop (e.g. lost cards) give up their space; their entries are pointed at the
short --shared clip (default 1506.f1a, a beep) so the toy never hits a missing file.

Untouched files stay exactly where they are, so only the sectors holding new data
(plus the directory) change. New files go 16-byte aligned into the space freed by
the files they replace, overflowing first-fit into any other free hole. Every
checksum is recomputed and verified before the image is written.
"""
import glob, os, sys
from common import SIZE, SECTOR, bad_files, card_file, crc16, files, set_entry

ALIGN = 16
args = sys.argv[1:]
opt = lambda k, d: args[args.index(k) + 1] if k in args else d
base, f1a_dir, out = args[:3]
drop = {card_file(n) for n in opt("--drop", "").split(",") if n}
shared = card_file(opt("--shared", "1506"))

img = bytearray(open(base, "rb").read())
assert len(img) == SIZE
old = bytes(img)
fs = files(img)
new = {card_file(os.path.basename(p)[:4]): open(p, "rb").read() for p in glob.glob(os.path.join(f1a_dir, "*.f1a"))}
missing = (set(new) | drop | {shared}) - set(fs)
assert not missing, "not on the chip: %s" % sorted(missing)
freed = set(new) | drop
assert shared not in freed,"the shared clip can't be replaced or dropped"

# Holes: runs of consecutive freed files, plus the free tail of the chip.
by_offset = sorted((off, ln, name) for name, (pos, off, ln) in fs.items())
holes, run = [], []
for off, ln, name in by_offset:
    if name in freed:
        run.append((off, name))
    elif run:
        holes.append([run[0][0], off, [n for _, n in run]]); run = []
if run:
    holes.append([run[0][0], SIZE, [n for _, n in run]])
else:
    end = max(off + ln for off, ln, name in by_offset)
    holes.append([(end + ALIGN - 1) // ALIGN * ALIGN, SIZE, []])
for start, stop, _ in holes:
    img[start:stop] = b"\xff" * (stop - start)

# Each hole first takes back its own files, then the overflow goes first-fit.
size = lambda name: (len(new[name]) + ALIGN - 1) // ALIGN * ALIGN
placed, overflow = {}, []
for h in holes:
    for name in h[2]:
        if name in new:
            if h[0] + size(name) <= h[1]:
                placed[name] = h[0]; h[0] += size(name)
            else:
                overflow.append(name)
for name in overflow:
    h = next((h for h in holes if h[0] + size(name) <= h[1]), None)
    if h is None:
        sys.exit("does not fit: %s (%d bytes) - drop more sounds or encode at a lower bitrate"
                 % (name, len(new[name])))
    placed[name] = h[0]; h[0] += size(name)

for name, off in placed.items():
    data = new[name]
    img[off:off + len(data)] = data
    set_entry(img, fs[name][0], off, len(data), crc16(data))
s_pos, s_off, s_len = fs[shared]
for name in drop:
    set_entry(img, fs[name][0], s_off, s_len, crc16(img[s_off:s_off + s_len]))

bad = bad_files(img)
assert not bad, "checksum errors: %s" % bad
assert all(img[off:off + ln] == old[off:off + ln] for name, (pos, off, ln) in fs.items() if name not in freed)
open(out, "wb").write(img)

changed = [a for a in range(0, SIZE, SECTOR) if old[a:a + SECTOR] != img[a:a + SECTOR]]
print("placed %d files (%d overflowed), %d dropped sounds point to %s" % (len(placed), len(overflow), len(drop), shared))
print("free space left: %d bytes" % sum(h[1] - h[0] for h in holes))
print("sectors changed: %d (%d KB)" % (len(changed), len(changed) * 4))
