@echo off
rem Decode every F1A file in FOLDER to a playable WAV next to it.
rem Usage: decode.bat FOLDER      (e.g. the output of: python3 tools/fs_list.py dump.bin --extract FOLDER)
rem Run from the folder holding testf1a_dec.exe.
cd /d "%~dp0"
for %%f in ("%~1\*.f1a") do testf1a_dec.exe "%%f" "%~1\%%~nf.wav"
dir /b "%~1\*.wav" | find /c ".wav"
