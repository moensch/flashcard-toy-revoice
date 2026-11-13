@echo off
rem WAV -> WMA only (the one step that needs real Windows). No JieLi tools involved.
rem Usage: wav2wma.bat FOLDER [KBPS]        (KBPS default 12; the F1A encoder accepts at most 16)
rem Output: FOLDER\wma\*.wma - bring these back and run tools/wine_f1a.sh on them.
rem Run from the folder holding WMAEncode.exe (or swap in another Microsoft-based WMA encoder).
set KBPS=%2
if "%KBPS%"=="" set KBPS=12
cd /d "%~dp0"
if not exist "%~1\wma" mkdir "%~1\wma"
for %%f in ("%~1\*.wav") do WMAEncode.exe "%%f" "%~1\wma\%%~nf.wma" -b %KBPS% --out-samplerate 16000 --out-channels 1
dir /b "%~1\wma\*.wma" | find /c ".wma"
