# Pico job: read-only connection check. The host prepends REGIONS = [(addr, len), ...]
# and EXPECTED = [bytes or None, ...] (None when no reference dump was given).
#
# A bad connection on this kind of setup only ever *loses* 1-bits (MISO has a pull-up
# and the chip's driver gets overpowered), so OR-ing many reads converges on the truth.
# Without a reference we use the OR of 40 reads as the best guess of the truth.


def bits(x):
    return bin(x).count("1")


ids = [read_id() for _ in range(10)]
good = sum(i == JEDEC_ID for i in ids)
print("ID correct: %d/10  (got %s)" % (good, ", ".join(sorted({i.hex() for i in ids}))))
if good == 0:
    print("VERDICT: NO CONTACT - chip not answering. Check clip seating, wiring, power.")
    raise SystemExit

worst = 0
for (addr, n), want in zip(REGIONS, EXPECTED):
    buf = bytearray(n)
    if want is None:
        want = bytearray(n)
        for _ in range(40):
            read_into(addr, buf)
            for i in range(n):
                want[i] |= buf[i]
    ones = sum(bits(x) for x in want) or 1
    acc = bytearray(n); first = None; matched = 0; bogus = 0
    for t in range(1, 151):
        read_into(addr, buf)
        if first is None:
            first = 100 * sum(bits(want[i] & ~buf[i]) for i in range(n)) / ones
            if first > 50:
                break                                   # hopeless, don't bother OR-ing
        for i in range(n):
            acc[i] |= buf[i]
        if acc == want:
            matched = t; break
        bogus = sum(bits(acc[i] & ~want[i]) for i in range(n))
        if bogus:
            break
    print("@0x%05x: single read drops %.1f%% of 1-bits; exact match after %s reads%s" % (
        addr, first, matched or ">%d" % t, "; %d WRONG 1-bits!" % bogus if bogus else ""))
    worst = max(worst, matched if matched else 999)

if good < 10 or worst == 999:
    print("VERDICT: BAD - reseat the clip before writing.")
elif worst <= 60:
    print("VERDICT: GOOD - ready to write.")
else:
    print("VERDICT: MARGINAL - writes will work but verify is slow; reseating may help.")
