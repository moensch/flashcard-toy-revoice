# Audio: the F1A format and how to encode it

## What F1A is

F1A is JieLi's proprietary compressed audio format for its low-cost audio chips.
There's no public spec and no open-source encoder. What works is JieLi's own
command-line tools, collected in the
[jieLi-cli-tools.zip](https://github.com/Jihao2048/jieli-audio-whitepaper/releases/download/v1.0.0/jieLi-cli-tools.zip)
release of
[Jihao2048/jieli-audio-whitepaper](https://github.com/Jihao2048/jieli-audio-whitepaper)
(Windows executables). The three we need:

| Tool | Does |
|---|---|
| `WMAEncode.exe` | WAV → WMA, using **Microsoft's** Windows Media encoder |
| `test_f1aencode.exe` | WMA → F1A (`test_f1aencode.exe in.wma out.f1a 0 0 scratch.raw`) |
| `testf1a_dec.exe` | F1A → WAV (`testf1a_dec.exe in.f1a out.wav`), for listening to originals and checking your encodes |

The originals on our chip are 16 kHz mono.

## The pipeline

```
recording.m4a ──tools/slice.py──▶ 16 kHz mono WAV per word ──windows/encode.bat──▶ .f1a (+ decoded check .wav)
```

`windows/encode.bat FOLDER 12` runs, for each WAV:

```
WMAEncode.exe word.wav word.wma -b 12 --out-samplerate 16000 --out-channels 1
test_f1aencode.exe word.wma word.f1a 0 0 x.raw
testf1a_dec.exe word.f1a check\word.wav
```

**Always listen to the decoded check WAVs.** They're exactly what the toy will play.

## Lessons (the expensive ones)

- **The WMA must come from Microsoft's encoder.** ffmpeg can write WMA too, and
  `test_f1aencode.exe` will accept it if you patch the header's bitrate fields
  (ffmpeg won't go below 24 kbps, the F1A encoder refuses more than 16). But the
  result sounds **metallic and garbled** on the toy. Re-encoding an original
  sound through Microsoft's encoder gave a result indistinguishable from the original.
- **Microsoft's encoder needs a real Windows PC.** `WMAEncode.exe` relies on the
  Windows Media runtime. We could not get that runtime into Wine/CrossOver on macOS
  (the WMP installers refuse or fail). The decoder and the F1A encoder do run under
  Wine; the WMA step doesn't. We ran `encode.bat` on a Windows 11 PC over SSH.
- **Bitrate vs. space.** The F1A file size follows the WMA bitrate. At 16 kbps, our
  (slower-spoken) words came out 57% bigger than the originals. At **12 kbps**,
  sped up 18% (`slice.py --tempo 1.18`), all 224 words plus 4 voice prompts fit
  with 11 KB to spare. 12 kbps still sounds clean on the toy's speaker. At 12 kbps
  expect about **2.4 KB per second** of audio.
- The encoder prints `asf read packet eof` and sometimes `overflow in spectral RLE,
  ignoring` for every file. Both are harmless.
