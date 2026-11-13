# Reading and writing the chip

## Setup

```sh
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt          # mpremote
```

Flash MicroPython onto the Pico (from [micropython.org](https://micropython.org/download/)),
wire it per [wiring.md](wiring.md), and plug it in. The tools find the Pico on
`/dev/cu.usbmodem*` / `/dev/ttyACM*`; set `PICO_PORT` otherwise.

## The workflow

```sh
# 0. Every time the clip is (re)seated:
python3 tools/check_connection.py            # want: ID 10/10, VERDICT: GOOD

# 1. Back up. KEEP THE FIRST DUMP OF THE UNTOUCHED CHIP FOREVER.
python3 tools/dump.py backup.bin             # reads twice, should say "identical"
python3 tools/fs_list.py backup.bin --extract originals/   # then windows/decode.bat originals

# 2. Build the new image from the backup plus your encoded files.
python3 tools/build_image.py backup.bin f1a/ new.bin [--drop 55,56]

# 3. Dry run: compares the chip to backup.bin, writes nothing.
python3 tools/write_flash.py backup.bin new.bin --check-only

# 4. Write, then verify independently.
python3 tools/write_flash.py backup.bin new.bin
python3 tools/dump.py after.bin && cmp after.bin new.bin && echo PERFECT
```

`write_flash.py` erases and writes only the 4 KB sectors that differ, verifies each
one, and writes the directory last. If it's interrupted, re-run the same command:
sectors that already hold the new data are skipped.

Writing all 115 changed sectors of our final image took about two minutes off-board.

## Why in-circuit writing is unreliable

Clipping onto the chip while it's still soldered to the toy's board **reads** fine
with patience, but writing was a weeks-long fight. The cause:

1. The clip's 3.3 V on chip pin 8 also powers the rest of the board, including the
   JieLi MCU, from behind the power switch. **The switch position doesn't matter.**
2. The MCU boots, finds its supply low, plays **"I'm tired, please give me some
   energy"** (1505) and **"I'm going to rest, bye bye"** (1502). Then it sleeps,
   and repeats about once a minute.
3. Awake or asleep, it **drives the SPI lines** it shares with the flash (CS high,
   CLK high, DI low). The Pico and the MCU fight over the bus.
4. Result: single reads dropped anywhere from 0% to 99% of the 1-bits, depending on
   what the MCU happened to be doing. The ID read as `87ffff` and similar.

Things that did **not** help: stronger Pico pin drive (12 mA), flash reset (`66`/`99`)
or wake (`AB`) commands, powering from the toy's battery instead (worse: the MCU is
then fully awake).

What we did get in-circuit, with luck and patience:

- **A full backup**, by OR-merging many dumps. A bad contact only loses 1-bits,
  so OR-ing enough reads recovers everything. Check the result against the file
  CRCs (`tools/merge_reads.py`, `tools/dump.py --reads 12`).
- **Small writes**, during lucky quiet windows. Every sector is verified by OR-reads.

Caveat on the OR-merge: a 16-bit CRC can match by accident. Our merged backup had
6 missing bits in one file whose CRC still passed. We only found out from a clean
off-board dump later.

**The reliable way: take the chip off the board.** Off-board on the same clip, reads
were perfect (0% dropped bits, two full dumps byte-identical) and the whole write
just worked. See [soldering.md](soldering.md).
