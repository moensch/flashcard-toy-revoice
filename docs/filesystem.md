# The flash filesystem

The 512 KB chip holds a tiny filesystem in the format JieLi's tools generate: a
flat directory of fixed-size entries at the start of the chip, followed by the
file data. Everything below was worked out from dumps of our chip and confirmed by
writing modified images that the toy played correctly.

`tools/common.py` (`entries()`, `crc16()`, `set_entry()`) implements it;
`tools/fs_list.py` prints it.

## Layout

```
0x00000  root entry "test_dir" (type 3 = directory)
0x00020  file entry 1     ┐
0x00040  file entry 2     │ 247 entries x 32 bytes
  ...                     │
0x01ee0  file entry 247   ┘
0x01f00  file data, back to back, each start aligned to 16 bytes
  ...
0x7ff66  end of data (after our rewrite), rest is 0xFF
```

The data starts right after the last entry (here `0x20 + 247 x 32 = 0x1f00`).
Gaps between files (alignment padding, freed space) are `0xFF`, the erased state of
flash.

## Directory entry (32 bytes, little-endian)

| Offset | Size | Field |
|---|---|---|
| 0 | 2 | **entry CRC**: CRC-16 over bytes 2–31 of this entry |
| 2 | 2 | **data CRC**: CRC-16 over the file's data |
| 4 | 4 | **offset**: absolute address of the data on the chip |
| 8 | 4 | **length** in bytes |
| 12 | 1 | **type**: `2` = file, `3` = directory |
| 13 | 1 | always `FF` |
| 14 | 1 | `01` on the **last** entry of the directory, `00` on all others: apparently an end-of-directory flag |
| 15 | 1 | always `00` |
| 16 | 16 | **name**, ASCII, NUL-terminated, padded with `FF` |

Real examples from our chip:

```
root:  3376 295b 20000000 40f50700 03 ff0000 "test_dir\0" ff...
       crc  dcrc offset=0x20 len=0x7f540 dir
1501:  c886 bc8b 001f0000 ac1a0000 02 ff0000 "1501.f1a\0" ff...
       crc  dcrc offset=0x1f00 len=6828 file
```

**CRC-16** is the XMODEM variant: polynomial `0x1021`, initial value `0`, no
reflection, no final XOR.

The root entry's offset (`0x20`) points at the first child entry, and its length
(`0x7f540`) spans from there to roughly the end of the chip. Its data CRC is not over
any range we could identify. We never updated it, and the toy didn't mind, even
with files placed past the end of the root's nominal span.

## Names or pointers?

**Both: the name identifies, the pointer locates.**

- Card number *N* plays the file named `NNN.f1a`, zero-padded to three digits:
  card 7 is `007.f1a`, card 168 is `168.f1a`. Other sounds have four-digit names
  (`1501.f1a` startup, `1001.f1a` ... noises).
- The firmware follows the entry's **offset/length** to find the data. Our first
  experiment pointed `168.f1a`'s entry (bee) at the data of `167.f1a` (butterfly)
  and fixed the entry CRC. The bee card then said "butterfly".
- So replacing a sound is: put new data somewhere free, point the entry at it,
  update length, data CRC and entry CRC. The names and the order of entries stay
  untouched.
- We never moved or renamed entries, so we can't say whether the firmware searches
  by name or by position in the directory. Keeping both unchanged is the safe choice.
  If you ever add an entry, move the "last entry" flag (byte 14) to it.
- Several entries may point at the same data. We used that to point unused sounds
  at one short beep.
- Data order doesn't matter. Originally the data was stored in directory order;
  after our rewrite it isn't, and the toy is fine.

## What's in the directory (our toy)

| Names | What |
|---|---|
| `001.f1a` – `224.f1a` | the words, one per card side (see `data/cards.csv`) |
| `1001.f1a` – `1017.f1a` (13 files) | sound effects (car, bee, horn, ...) |
| `1501.f1a` | startup jingle with English words |
| `1502.f1a` | "I'm going to rest, bye bye" (auto power-off) |
| `1503.f1a` | "please insert a card" |
| `1504.f1a` | "please reinsert the card" (bad read) |
| `1505.f1a` | "I'm tired, please give me some energy" (battery low) |
| `1506, 1507, 1513–1515.f1a` | short beeps / UI sounds |

## How tools/build_image.py rewrites it

1. Free the space of every file being replaced (and of any `--drop` sounds).
   Consecutive freed files merge into one hole; the free tail of the chip is a hole too.
2. Place each new file 16-byte aligned, preferably back into the hole its old version
   came from, otherwise first-fit into any hole.
3. Update offset, length, data CRC and entry CRC of each changed entry. Point dropped
   entries at a shared short clip.
4. Verify every checksum and that untouched files are byte-identical, then report
   which 4 KB sectors changed. Only those get erased and written.
