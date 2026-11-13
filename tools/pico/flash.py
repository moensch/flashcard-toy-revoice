# Pico job: write changed sectors. The host prepends CHECK_ONLY = True/False and uploads
# job.bin: repeated records of [u32 addr][4096 current bytes][4096 target bytes].
#
# Every sector is pre-checked against CURRENT before anything is erased; a sector that
# already holds TARGET (from an interrupted run) is skipped. Reads may drop 1-bits on a
# poor connection, so all comparisons OR repeated reads until they equal the expectation.
import struct

TRIES = 600
REC = 4 + 4096 + 4096


def or_match(addr, want):
    """>0: matched after n reads; <0: saw a 1-bit that shouldn't be there; 0: gave up."""
    n = len(want); acc = bytearray(n); buf = bytearray(n)
    for t in range(1, TRIES + 1):
        read_into(addr, buf)
        for i in range(n):
            acc[i] |= buf[i]
        if acc == want:
            return t
        if any(acc[i] & ~want[i] for i in range(n)):
            return -t
    return 0


def program(addr, data):
    for p in range(0, len(data), 256):
        page = data[p:p + 256]
        if page == b"\xff" * len(page):
            continue
        simple(0x06); cmd_addr(0x02, addr + p)                   # write enable, page program
        for b in page:
            send(b)
        cs(1); time.sleep_ms(10)


def fail(msg):
    print(msg)
    raise SystemExit(1)


ids = [read_id() for _ in range(5)]
print("ID x5:", [i.hex() for i in ids])
if any(i != JEDEC_ID for i in ids):
    fail("ID unstable - reseat the clip. Nothing written.")

job = open("job.bin", "rb")                                      # one sector at a time: too big for RAM
nsec = job.seek(0, 2) // REC


def sector(i):
    job.seek(i * REC); rec = job.read(REC)
    return struct.unpack("<I", rec[:4])[0], rec[4:4100], rec[4100:]


todo = []
for i in range(nsec):
    addr, cur, tgt = sector(i)
    if or_match(addr, cur) > 0:
        todo.append(i); state = "to write"
    elif or_match(addr, tgt) > 0:
        state = "already written"
    else:
        fail("PRE-CHECK FAILED at 0x%05x - chip differs from CURRENT image (or the clip is bad). "
             "Nothing written." % addr)
    print("pre-check 0x%05x: %s" % (addr, state))
print("PRE-CHECK OK, %d of %d sectors to write" % (len(todo), nsec))
if CHECK_ONLY:
    raise SystemExit

for i in todo:
    addr, _, tgt = sector(i)
    simple(0x06); cmd_addr(0x20, addr); cs(1); time.sleep_ms(500)  # write enable, 4 KB sector erase
    program(addr, tgt)
    r = or_match(addr, tgt)
    print("wrote 0x%05x, verify: %s" % (addr, "OK (%d reads)" % r if r > 0 else "FAILED (%d)" % r))
    if r <= 0:
        fail("VERIFY FAILED at 0x%05x - stop. Re-run with the same images to retry." % addr)
print("ALL DONE")
