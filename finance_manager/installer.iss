; Inno Setup script for Personal Finance Manager
; Requires: Inno Setup 6+ (https://jrsoftware.org/isinfo.php)
; Build the EXE first: python build.py --clean
; Then compile this script in Inno Setup IDE or via:
;   iscc installer.iss

#define AppName      "Personal Finance Manager"
#define AppVersion   "1.0.0"
#define AppPublisher "Finance Manager"
#define AppExeName   "FinanceManager.exe"
#define AppURL       "https://github.com/yourusername/finance-manager"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}

; Install into user's AppData so no admin rights required
DefaultDirName={userpf}\{#AppName}
DefaultGroupName={#AppName}
AllowNoIcons=yes

; Output
OutputDir=dist
OutputBaseFilename=FinanceManagerSetup
SetupIconFile=

; Compression
Compression=lzma2/ultra64
SolidCompression=yes
LZMAUseSeparateProcess=yes

; Appearance
WizardStyle=modern
WizardSizePercent=120

; Minimum Windows version: Windows 10
MinVersion=10.0

; Architecture
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

; Uninstall info
UninstallDisplayName={#AppName}
UninstallDisplayIcon={app}\{#AppExeName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon";   Description: "{cm:CreateDesktopIcon}";   GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startupicon";   Description: "Start {#AppName} on Windows startup"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Main executable (produced by PyInstaller)
Source: "dist\{#AppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Start Menu
Name: "{group}\{#AppName}";           Filename: "{app}\{#AppExeName}"
Name: "{group}\Uninstall {#AppName}"; Filename: "{uninstallexe}"

; Desktop shortcut (optional)
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

; Startup (optional)
Name: "{userstartup}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: startupicon

[Run]
; Offer to launch after install
Filename: "{app}\{#AppExeName}"; \
  Description: "{cm:LaunchProgram,{#StringChange(AppName, '&', '&&')}}"; \
  Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Remove user data directory on uninstall (optional — commented out by default)
; Type: filesandordirs; Name: "{userdocs}\FinanceManager"

[Code]
// Custom page: ask user whether to keep or remove their data on uninstall
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  DataDir: String;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    DataDir := ExpandConstant('{%USERPROFILE}\.finance_manager');
    if DirExists(DataDir) then
    begin
      if MsgBox(
        'Would you like to remove your Finance Manager data (database and settings)?'#13#10 +
        DataDir,
        mbConfirmation, MB_YESNO
      ) = IDYES then
        DelTree(DataDir, True, True, True);
    end;
  end;
end;
