@echo off
rem Encode every WAV in FOLDER to JieLi F1A, plus a decoded check WAV of each.
rem Usage: encode.bat FOLDER [KBPS]        (KBPS default 12; the encoder accepts at most 16)
rem Output: FOLDER\f1a\*.f1a and FOLDER\check\*.wav (listen to these: it's what the toy plays)
rem Run from the folder holding WMAEncode.exe, test_f1aencode.exe and testf1a_dec.exe.
rem "asf read packet eof" and "overflow in spectral RLE" messages are normal.
set KBPS=%2
if "%KBPS%"=="" set KBPS=12
cd /d "%~dp0"
if not exist "%~1\f1a" mkdir "%~1\f1a"
if not exist "%~1\check" mkdir "%~1\check"
for %%f in ("%~1\*.wav") do (
  WMAEncode.exe "%%f" "%~1\f1a\%%~nf.wma" -b %KBPS% --out-samplerate 16000 --out-channels 1
  test_f1aencode.exe "%~1\f1a\%%~nf.wma" "%~1\f1a\%%~nf.f1a" 0 0 x.raw
  testf1a_dec.exe "%~1\f1a\%%~nf.f1a" "%~1\check\%%~nf.wav"
  del "%~1\f1a\%%~nf.wma"
)
dir /b "%~1\f1a\*.f1a" | find /c ".f1a"
