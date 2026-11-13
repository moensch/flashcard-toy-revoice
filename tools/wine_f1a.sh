#!/bin/sh
# WMA -> F1A (+ a decoded check WAV) with JieLi's tools under Wine, on macOS or Linux.
# Usage: tools/wine_f1a.sh WMA_DIR OUT_DIR
#   WMA_DIR: output of windows/wav2wma.bat (Microsoft-encoded WMA)
#   OUT_DIR: gets f1a/*.f1a and check/*.wav (listen to these: it's what the toy plays)
# Environment:
#   JIELI_TOOLS  folder holding test_f1aencode.exe and testf1a_dec.exe (required)
#   WINE         wine command (default: wine). CrossOver users, e.g.:
#                WINE="$HOME/Applications/CrossOver.app/Contents/SharedSupport/CrossOver/bin/wine --bottle jieli"
#   WINEPREFIX   a dedicated prefix just for these tools (recommended, see docs/safer-encoding.md)
# Files are copied into the tools folder and back, so the tools never need paths outside it.
set -e
: "${JIELI_TOOLS:?set JIELI_TOOLS to the unzipped jieLi-cli-tools folder}"
WINE=${WINE:-wine}
in=$1; out=$2
mkdir -p "$out/f1a" "$out/check" "$JIELI_TOOLS/work"
for f in "$in"/*.wma; do
  n=$(basename "$f" .wma)
  cp "$f" "$JIELI_TOOLS/work/in.wma"
  (cd "$JIELI_TOOLS" && $WINE test_f1aencode.exe 'work\in.wma' 'work\out.f1a' 0 0 'work\x.raw' >/dev/null 2>&1 &&
                       $WINE testf1a_dec.exe 'work\out.f1a' 'work\check.wav' >/dev/null 2>&1)
  cp "$JIELI_TOOLS/work/out.f1a" "$out/f1a/$n.f1a"
  cp "$JIELI_TOOLS/work/check.wav" "$out/check/$n.wav"
  rm -f "$JIELI_TOOLS"/work/*
  echo "$n"
done
echo "done: $(ls "$out/f1a" | wc -l | tr -d ' ') files in $out/f1a"
