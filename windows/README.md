# Windows tools

**Safer route:** use Windows only for `wav2wma.bat` and run the JieLi tools in Wine.
See [../docs/safer-encoding.md](../docs/safer-encoding.md). The steps below run everything on Windows.

The F1A encoder chain only works fully on real Windows (see
[../docs/audio-format.md](../docs/audio-format.md)). Nothing here is installed; it all
runs from one folder.

1. Download [jieLi-cli-tools.zip](https://github.com/Jihao2048/jieli-audio-whitepaper/releases/download/v1.0.0/jieLi-cli-tools.zip)
   (from [Jihao2048/jieli-audio-whitepaper](https://github.com/Jihao2048/jieli-audio-whitepaper))
   and unzip it into a folder, e.g. `C:\toyflash`.
2. Copy `encode.bat` and `decode.bat` into that same folder.
3. Copy a folder of WAVs from `tools/slice.py` next to them, e.g. `C:\toyflash\colors`.
4. Run `encode.bat colors 12`.
5. Copy `colors\f1a\` back. Listen to `colors\check\`.

To listen to the original sounds: `python3 tools/fs_list.py backup.bin --extract originals`,
copy `originals` over, run `decode.bat originals`.

## Driving it from a Mac or Linux box

We enabled the OpenSSH server on the Windows 11 PC so the whole loop ran from the
Mac (`scp` the WAVs over, `ssh pc "cd toyflash && encode.bat colors 12"`, `scp` the
results back):

```powershell
# admin PowerShell (note: four tildes)
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
Start-Service sshd
Set-Service -Name sshd -StartupType Automatic
```

Gotchas we hit: a VPN client on the PC blocked incoming connections. And for an
account that's an administrator, the public key goes into
`C:\ProgramData\ssh\administrators_authorized_keys` (readable only by Administrators
and SYSTEM), not `~\.ssh\authorized_keys`.
