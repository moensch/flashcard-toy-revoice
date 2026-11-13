"""Shared helpers: running jobs on the Pico, and the JieLi flash filesystem.

Configuration (environment variables):
  PICO_PORT  serial port of the Pico   (default: first /dev/cu.usbmodem* or /dev/ttyACM*)
  MPREMOTE   mpremote executable        (default: "mpremote" on PATH)
"""
import glob, os, struct, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SIZE = 512 * 1024
SECTOR = 4096


# --- Pico ------------------------------------------------------------------

def port():
    p = os.environ.get("PICO_PORT") or next(iter(sorted(glob.glob("/dev/cu.usbmodem*") + glob.glob("/dev/ttyACM*"))), None)
    if not p:
        sys.exit("No Pico found. Plug it in, or set PICO_PORT.")
    return p


def mpremote(*args, **kw):
    return subprocess.run([os.environ.get("MPREMOTE", "mpremote"), "connect", port(), *args], **kw)


def run_job(job, prefix=""):
    """Run tools/pico/<job>.py on the Pico, prefixed with the SPI preamble and `prefix`."""
    src = open(os.path.join(HERE, "pico", "spi.py")).read()
    src += "\n" + prefix + "\n" + open(os.path.join(HERE, "pico", job + ".py")).read()
    with tempfile.TemporaryDirectory() as tmp:
        script = os.path.join(tmp, job + ".py")
        open(script, "w").write(src)
        return mpremote("run", script).returncode


def fetch(remote, local):
    mpremote("fs", "cp", ":" + remote, local, check=True, stdout=subprocess.DEVNULL)


def upload(local, remote):
    mpremote("fs", "cp", local, ":" + remote, check=True, stdout=subprocess.DEVNULL)


# --- JieLi filesystem (see docs/filesystem.md) ------------------------------

TYPE_FILE, TYPE_DIR = 2, 3


def crc16(data):
    """CRC-16/XMODEM: poly 0x1021, init 0, no reflection."""
    c = 0
    for b in data:
        c ^= b << 8
        for _ in range(8):
            c = ((c << 1) ^ 0x1021) & 0xFFFF if c & 0x8000 else (c << 1) & 0xFFFF
    return c


def entries(img):
    """Yield (pos, name, type, offset, length, entry_ok, data_crc) for the root and its files."""
    pos = 0
    while pos + 32 <= len(img):
        ent = img[pos:pos + 32]
        if ent[:4] == b"\xff\xff\xff\xff":
            break
        ecrc, dcrc, off, ln = struct.unpack("<HHII", ent[:12])
        if pos and (crc16(ent[2:32]) != ecrc or off <= pos):
            break                                   # past the directory, into file data
        name = ent[16:32].split(b"\0")[0].decode("latin1")
        yield pos, name, ent[12], off, ln, crc16(ent[2:32]) == ecrc, dcrc
        pos += 32


def files(img):
    """{name: (entry_pos, offset, length)} for every file entry."""
    return {name: (pos, off, ln) for pos, name, typ, off, ln, *_ in entries(img) if typ == TYPE_FILE}


def bad_files(img):
    """Names of files whose entry or data checksum fails."""
    return [name for pos, name, typ, off, ln, eok, dcrc in entries(img)
            if typ == TYPE_FILE and not (eok and crc16(img[off:off + ln]) == dcrc)]


def set_entry(img, pos, off, ln, data_crc):
    """Point the entry at `pos` to new data and fix up both checksums."""
    struct.pack_into("<HII", img, pos + 2, data_crc, off, ln)
    struct.pack_into("<H", img, pos, crc16(img[pos + 2:pos + 32]))


def card_file(n):
    """Card or sound number -> file name on the chip: 7 -> 007.f1a, 1501 -> 1501.f1a."""
    return "%03d.f1a" % int(n)
