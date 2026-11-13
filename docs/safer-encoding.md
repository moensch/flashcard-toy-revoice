# Encoding more safely

The encoder chain uses unsigned Windows executables from a third-party GitHub
release. We have no reason to think they're malicious, but we can't vouch for them.
For our first run we copied the whole toolbox to a family member's Windows PC and
ran everything there, under an admin account, with SSH opened and the firewall
off. It worked. We wouldn't do it that way again.

## The split: Windows only for WMA

Only **one** step needs real Windows: WAV → WMA with Microsoft's encoder (Wine can't
run the Windows Media runtime). The JieLi tools themselves run fine under Wine. So:

```
Mac/Linux                      Windows (minimal)              Mac/Linux, in Wine
tools/slice.py → *.wav  ──▶  windows/wav2wma.bat → *.wma  ──▶  tools/wine_f1a.sh → *.f1a + check *.wav
```

```sh
# on Windows:  wav2wma.bat words 12
# back on the Mac:
JIELI_TOOLS=~/jieli/jieLi-cli-tools WINEPREFIX=~/.wine-jieli tools/wine_f1a.sh words/wma words/out
```

`windows/encode.bat` (all three steps on Windows) still works if you prefer.

Status: the two JieLi tools ran under CrossOver on macOS during this project. The
`wav2wma.bat` → `wine_f1a.sh` round trip as a whole has not been run end to end
yet. Compare its check WAVs with a known-good encode the first time.

## Making the Windows step safer

From most to least isolated:

1. **A throwaway Windows VM** (UTM, Parallels, VMware, VirtualBox). Take a snapshot,
   encode, revert. Nothing touches a real PC. (Windows Sandbox would be ideal but
   needs Windows Pro/Enterprise.)
2. **A separate standard (non-admin) Windows account** on an existing PC, used only
   for this. No SSH server, firewall stays on. Delete the account afterwards.
3. **Avoid the third-party wrapper entirely.** `WMAEncode.exe` comes from the same zip.
   Windows itself ships a WMA encoder (Media Foundation), and Microsoft's old
   *Windows Media Encoder 9 Series* has a command-line script. Either should produce the
   "real Microsoft WMA" the F1A encoder wants. Untested; if you get one working,
   please send a PR.

## Making the Wine step safer

Wine is a compatibility layer, **not a sandbox**: a Windows program under Wine can read
and write your files like any other app you run.

- Use a **dedicated prefix/bottle** just for these tools (`WINEPREFIX=~/.wine-jieli`, or a
  CrossOver bottle).
- In that prefix, **remove the `Z:` drive** (it maps your whole filesystem): run
  `winecfg` → Drives, or delete the `dosdevices/z:` link inside the prefix.
  `wine_f1a.sh` copies files into the tools folder so the tools never need `Z:`.
- For stronger isolation, run it under a separate macOS/Linux user account or in a
  Linux VM/container.

## Check the binaries first

Look the files up on [VirusTotal](https://www.virustotal.com/) by hash before running
them. These are the SHA-256 hashes of the copies we used, from the
[v1.0.0 release](https://github.com/Jihao2048/jieli-audio-whitepaper/releases/tag/v1.0.0):

```
2ba9989492f3cb998cdbfdf2a18f9ce064aa345037888e1f15ebdae8fe3541ab  jieLi-cli-tools.zip
25bcc6eacd9c211fd8b68884eb8831a86bbae14dff0bfe0cab84fe2905208515  WMAEncode.exe
0e186d67eace1995fd2d996da2351ae0a7a04e8c91693275e873cd7d21952eb6  test_f1aencode.exe
5b7cca5ae99deb1f4fc32127c5c254122c3a0b272e96e98514e1945c5bc43196  testf1a_dec.exe
```

If your download's hashes differ, find out why before running anything.

## Cleaning up a PC you already used

If you followed our first approach: turn the firewall back on, remove the OpenSSH
server (`Remove-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0`) and any
key in `C:\ProgramData\ssh\administrators_authorized_keys`, delete the tools folder,
and run a Microsoft Defender full scan plus an offline scan.
