# Pico job: read the whole chip into dump.bin on the Pico's own filesystem.
SIZE, CHUNK = 512 * 1024, 4096

if read_id() != JEDEC_ID:
    raise SystemExit("ID %s, expected %s - check the wiring." % (read_id().hex(), JEDEC_ID.hex()))
buf = bytearray(CHUNK)
with open("dump.bin", "wb") as f:
    for a in range(0, SIZE, CHUNK):
        read_into(a, buf)
        f.write(buf)
print("dumped", SIZE, "bytes")
