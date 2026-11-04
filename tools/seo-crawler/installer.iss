; Windows installer (Inno Setup 6). build_windows.bat builds the app folder and runs this.
; Installs per user (no admin prompt), adds Start Menu / Desktop shortcuts and an uninstaller.

#ifndef AppVersion
  #define AppVersion "1.0.0"
#endif

[Setup]
AppId={{9B2E4C61-3D7A-4F18-8C5E-1A2B3C4D5E6F}
AppName=Free SEO Crawler
AppVersion={#AppVersion}
AppPublisher=Sachin Samria
AppComments=Made by Sachin Samria
DefaultDirName={autopf}\Free SEO Crawler
DefaultGroupName=Free SEO Crawler
PrivilegesRequired=lowest
DisableProgramGroupPage=yes
OutputDir=dist
OutputBaseFilename=FreeSEOCrawler-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\FreeSEOCrawler.exe
UninstallDisplayName=Free SEO Crawler (Made by Sachin Samria)

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "dist\FreeSEOCrawler\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Free SEO Crawler"; Filename: "{app}\FreeSEOCrawler.exe"
Name: "{group}\Uninstall Free SEO Crawler"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Free SEO Crawler"; Filename: "{app}\FreeSEOCrawler.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\FreeSEOCrawler.exe"; Description: "{cm:LaunchProgram,Free SEO Crawler}"; Flags: nowait postinstall skipifsilent
