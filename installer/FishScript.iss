; FishScript Windows installer script for Inno Setup.
; Build FishScript.exe first using build_windows.bat.

[Setup]
AppName=FishScript
AppVersion=1.0.0
DefaultDirName={pf}\FishScript
DefaultGroupName=FishScript
OutputBaseFilename=FishScriptInstaller
Compression=lzma
SolidCompression=yes

[Files]
Source: "..\dist\FishScript.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\FishScript"; Filename: "{app}\FishScript.exe"
Name: "{commondesktop}\FishScript"; Filename: "{app}\FishScript.exe"

[Run]
Filename: "{app}\FishScript.exe"; Description: "Launch FishScript"; Flags: nowait postinstall skipifsilent
