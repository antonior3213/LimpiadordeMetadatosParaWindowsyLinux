#define AppName "Limpiador de Google Takeout"
#define AppVersion "1.0.0"
#define AppExe "TakeoutLimpieza.exe"

[Setup]
AppId={{7B18CA92-5E07-4E64-A1D8-4B9DD352E21F}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher=Proyecto personal
DefaultDirName={localappdata}\Programs\TakeoutLimpieza
DefaultGroupName={#AppName}
UninstallDisplayName={#AppName}
UninstallDisplayIcon={app}\{#AppExe}
OutputDir=Output
OutputBaseFilename=Instalador_TakeoutLimpieza_Windows
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest

[Tasks]
Name: "desktopicon"; Description: "Crear acceso directo en el escritorio"; GroupDescription: "Accesos directos:"; Flags: checkedonce

[Files]
Source: "..\dist\{#AppExe}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\{#AppExe}"; WorkingDir: "{app}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExe}"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExe}"; Description: "Abrir {#AppName}"; Flags: postinstall nowait skipifsilent
