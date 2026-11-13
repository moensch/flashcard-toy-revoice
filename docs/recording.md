# Recording your own voice

What worked well for us: a phone/laptop voice memo app with AirPods, one recording
per category, then automatic slicing.

## 1. Know the originals

Dump the chip, extract and decode the sounds (see [flashing.md](flashing.md) and
`windows/decode.bat`), and listen through them to build your card list. Ours is
`data/cards.csv`. Name the decoded files `NNNN_word.wav` (e.g. `0103_purple.wav`),
which makes `tools/compare.sh` work.

## 2. Record

- One recording per category, **in ascending card order**, from a printed list.
- About **1 second of silence** between words. The slicer splits on ≥ 0.6 s of quiet.
- Speak a bit faster than feels natural, or plan on `--tempo` (below).
- Botched a word? Pause, say it again, and drop the bad take with `--skip`.
  Or re-record just that word as its own file later.
- Quiet room. The slicer denoises, but it can't remove a dog.

## 3. Slice

```sh
python3 tools/slice.py colors.m4a voice/de --tempo 1.18 \
    0103_purple 0104_brown 0105_red 0106_white 0107_yellow \
    0108_black 0109_blue 0110_green 0111_orange 0112_grey
```

It prints each detected word with its timing. If the count doesn't match the names,
nothing is written:

- **One extra slice** is usually a click at the start of the recording, or a cough.
  Spot it in the printed list (a slice of ~0.2 s) and add `--skip N`.
- **One missing slice** means two words ran together. Re-record those two.
- **A soft first sound gets cut off** ("Pf", "F", "S", "Sch", "H"): re-slice with
  `--pre 0.12`.
- **A click right before a word**: `tools/trim_start.sh voice/de/0134_raincoat.wav 0.11`
  cuts the first 0.11 s off the finished WAV, with a short fade-in.

## 4. Review

```sh
tools/compare.sh originals voice/de 103 104 105 106 107 108 109 110 111 112
```

plays original → yours for each card. Re-take anything you don't like as a single
recording and slice it with just that one name. It overwrites the old file.

## 5. Encode

Copy the WAVs to a Windows PC and run `windows/encode.bat FOLDER 12`. Bring
`FOLDER\f1a\` back and listen to a few files in `FOLDER\check\`. Then continue with
[flashing.md](flashing.md).
