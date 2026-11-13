#!/bin/sh
# Play original and replacement back to back for each sound number (macOS afplay).
# Usage: tools/compare.sh ORIG_DIR NEW_DIR NUM [NUM ...]
#   ORIG_DIR: decoded originals named NNNN_*.wav (see windows/README.md)
#   NEW_DIR:  your sliced words named NNNN_*.wav
#   e.g. tools/compare.sh originals voice/de 103 104 105
orig=$1; new=$2; shift 2
for n in "$@"; do
  n=$(printf %04d "$n")
  for f in "$orig/${n}"_*.wav "$new/${n}"_*.wav; do
    [ -f "$f" ] && afplay "$f" || echo "missing: $f"
  done
done
