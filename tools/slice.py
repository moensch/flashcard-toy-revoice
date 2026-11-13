"""Slice one recording of several words into one clean WAV per word.

Usage: python3 tools/slice.py IN.m4a OUTDIR [--skip 2,5] [--tempo 1.18] [--pre 0.05] NNNN_word [...]

Read the words in order with a clear pause (about 1 s) between them. Words are
split on >= 0.6 s of silence below -35 dB; slices shorter than 0.15 s are ignored.
If the number of slices doesn't match the number of names, nothing is written and
the detected slices are listed, so you can see what went wrong:

  --skip 2,5   drop detected slices 2 and 5 (a click, a cough, a flubbed take)
  --tempo X    speed up by factor X without changing pitch (we used 1.18: shorter
               files fit in the space of the originals, and it sounds livelier)
  --pre S      seconds kept before each word (default 0.05). Raise it (0.12) for
               words starting with a soft sound like "Pf", "F", "S" or "H", which
               the silence detector otherwise clips.

Each word gets: 120 Hz high-pass, 6.5 kHz low-pass, denoise, gentle compression,
short fades, peak normalized to -1 dB, 16 kHz mono - ready for windows/encode.bat.
"""
import os, re, subprocess, sys

args = sys.argv[1:]


def opt(flag, default):
    if flag not in args:
        return default
    i = args.index(flag); v = args[i + 1]; del args[i:i + 2]
    return v


skip = {int(x) for x in opt("--skip", "").split(",") if x}
tempo = float(opt("--tempo", "1"))
pre = float(opt("--pre", "0.05"))
src, outdir, names = args[0], args[1], args[2:]

log = subprocess.run(["ffmpeg", "-hide_banner", "-i", src, "-af", "silencedetect=n=-35dB:d=0.6", "-f", "null", "-"],
                     capture_output=True, text=True).stderr
starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)]
ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src],
                           capture_output=True, text=True).stdout)
if not starts or starts[0] > 0.05:
    ends = [0.0] + ends                                  # recording starts with sound
else:
    starts = starts[1:]
starts.append(dur)
words = [(a, b) for a, b in zip(ends, starts) if b - a >= 0.15]
words = [w for i, w in enumerate(words, 1) if i not in skip]
print("found %d words, expected %d" % (len(words), len(names)))
for i, (a, b) in enumerate(words):
    print("  %-24s %6.2f-%6.2f (%.2f s)" % (names[i] if i < len(names) else "?", a, b, b - a))
if len(words) != len(names):
    sys.exit("count mismatch - nothing written")

os.makedirs(outdir, exist_ok=True)
chain = ("highpass=f=120,lowpass=f=6500,afftdn=nr=20:nf=-45,"
         "acompressor=threshold=-20dB:ratio=3:attack=5:release=100:makeup=3,"
         "afade=t=in:d=0.01,areverse,afade=t=in:d=0.03,areverse,aresample=16000")
for (a, b), n in zip(words, names):
    tmp = os.path.join(outdir, n + ".tmp.wav"); out = os.path.join(outdir, n + ".wav")
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", "%.3f" % max(0, a - pre),
                    "-to", "%.3f" % min(dur, b + 0.08), "-i", src, "-af", chain, "-ac", "1", tmp], check=True)
    peak = float(re.search(r"max_volume: ([-\d.]+)", subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", tmp, "-af", "volumedetect", "-f", "null", "-"],
        capture_output=True, text=True).stderr).group(1))
    post = "volume=%.2fdB" % (-1 - peak) + (",atempo=%g" % tempo if tempo != 1 else "")
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", tmp, "-af", post,
                    "-ar", "16000", "-ac", "1", out], check=True)
    os.remove(tmp)
print("wrote", len(words), "files to", outdir)
