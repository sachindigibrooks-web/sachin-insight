; Windows installer (Inno Setup 6). Build the app folder first (build_windows.bat does both):
;   ISCC.exe /DAppVersion=1.0.0 installer.iss
; Installs per user (no admin prompt), adds Start Menu / Desktop shortcuts and an uninstaller.

#ifndef AppVersion
  #define AppVersion "1.0.0"
#endif

[Setup]
AppId={{6F1C3E2A-5B7D-4E8F-9A1B-2C3D4E5F6A7B}
AppName=Free Video & Photo Downloader
AppVersion={#AppVersion}
AppPublisher=Sachin Samria
AppComments=Made by Sachin Samria
DefaultDirName={autopf}\Free Video Downloader
DefaultGroupName=Free Video & Photo Downloader
PrivilegesRequired=lowest
DisableProgramGroupPage=yes
OutputDir=dist
OutputBaseFilename=FreeVideoDownloader-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\FreeVideoDownloader.exe
UninstallDisplayName=Free Video & Photo Downloader (Made by Sachin Samria)

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "dist\FreeVideoDownloader\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Free Video & Photo Downloader"; Filename: "{app}\FreeVideoDownloader.exe"
Name: "{group}\Uninstall Free Video & Photo Downloader"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Free Video & Photo Downloader"; Filename: "{app}\FreeVideoDownloader.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\FreeVideoDownloader.exe"; Description: "{cm:LaunchProgram,Free Video & Photo Downloader}"; Flags: nowait postinstall skipifsilent
