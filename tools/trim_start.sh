#!/bin/sh
# Cut a click or noise off the start of a sliced word, with a short fade-in.
# Usage: tools/trim_start.sh WORD.wav SECONDS      e.g. tools/trim_start.sh 0134_raincoat.wav 0.11
set -e
tmp="$1.trim.wav"
ffmpeg -hide_banner -loglevel error -y -i "$1" -af "atrim=start=$2,afade=t=in:d=0.015" "$tmp"
mv "$tmp" "$1"
echo "trimmed $2 s off $1"
