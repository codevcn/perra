; Inno Setup script for Perra (Persona Radar) --onedir Windows distribution

#ifndef MyAppVersion
  #define MyAppVersion "0.1.0"
#endif

#ifndef SourceOnedir
  #define SourceOnedir "..\dist\perra"
#endif

#ifndef SkillSource
  #define SkillSource "..\skills\perra"
#endif

#define MyAppName "Perra"
#define MyAppFullName "Perra (Persona Radar)"
#define MyAppPublisher "codevcn"
#define MyAppURL "https://github.com/codevcn/perra"
#define MyAppExeName "perra.exe"

[Setup]
AppId={{7D8B4D4E-2B26-4B7A-9F1E-5D9F8D2E1A01}
AppName={#MyAppFullName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppFullName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/issues
AppUpdatesURL={#MyAppURL}/releases
DefaultDirName={localappdata}\Programs\Perra
DefaultGroupName={#MyAppFullName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
LicenseFile=..\LICENSE
OutputBaseFilename=PerraSetup-{#MyAppVersion}-win64
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ChangesEnvironment=yes
CloseApplications=yes
RestartApplications=no
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "addtopath"; Description: "Add Perra CLI directory to user PATH (enables global 'perra' command)"
Name: "skill_antigravity"; Description: "Install 'perra' AI Agent Skill for Antigravity (~/.gemini/config/skills/perra)"; GroupDescription: "AI Agent Skills:"
Name: "skill_codex"; Description: "Install 'perra' AI Agent Skill for Codex (~/.codex/skills/perra)"; GroupDescription: "AI Agent Skills:"
Name: "skill_claude"; Description: "Install 'perra' AI Agent Skill for Claude Code (~/.claude/skills/perra)"; GroupDescription: "AI Agent Skills:"

[Files]
Source: "{#SourceOnedir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#SkillSource}\*"; DestDir: "{%USERPROFILE}\.gemini\config\skills\perra"; Tasks: skill_antigravity; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#SkillSource}\*"; DestDir: "{%USERPROFILE}\.codex\skills\perra"; Tasks: skill_codex; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#SkillSource}\*"; DestDir: "{%USERPROFILE}\.claude\skills\perra"; Tasks: skill_claude; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Perra CLI (Prompt)"; Filename: "{cmd}"; Parameters: "/k ""{app}\{#MyAppExeName}"" --help"; IconFilename: "{app}\{#MyAppExeName}"
Name: "{group}\Perra Web Interface"; Filename: "{app}\{#MyAppExeName}"; Parameters: "--web 5000"; IconFilename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"

[Code]
const
  EnvKey = 'Environment';

function NormalizeDir(const S: string): string;
begin
  Result := Trim(S);
  while (Length(Result) > 3) and (Result[Length(Result)] = '\') do
    Delete(Result, Length(Result), 1);
end;

function PathContainsDir(const PathValue, DirValue: string): Boolean;
var
  Remaining, Entry, Target: string;
  SepPos: Integer;
begin
  Result := False;
  Target := LowerCase(NormalizeDir(DirValue));
  Remaining := PathValue;
  while Length(Remaining) > 0 do
  begin
    SepPos := Pos(';', Remaining);
    if SepPos = 0 then
    begin
      Entry := Remaining;
      Remaining := '';
    end
    else
    begin
      Entry := Copy(Remaining, 1, SepPos - 1);
      Delete(Remaining, 1, SepPos);
    end;
    if LowerCase(NormalizeDir(Entry)) = Target then
    begin
      Result := True;
      Exit;
    end;
  end;
end;

procedure WriteUserPath(const NewPath: string);
begin
  if Pos('%', NewPath) > 0 then
    RegWriteExpandStringValue(HKEY_CURRENT_USER, EnvKey, 'Path', NewPath)
  else
    RegWriteStringValue(HKEY_CURRENT_USER, EnvKey, 'Path', NewPath);
end;

procedure EnvAddPath(const DirToAdd: string);
var
  Paths, NewPaths: string;
begin
  if not RegQueryStringValue(HKEY_CURRENT_USER, EnvKey, 'Path', Paths) then
    Paths := '';

  if PathContainsDir(Paths, DirToAdd) then
    Exit;

  if (Length(Paths) > 0) and (Paths[Length(Paths)] <> ';') then
    NewPaths := Paths + ';' + DirToAdd
  else
    NewPaths := Paths + DirToAdd;

  WriteUserPath(NewPaths);
end;

procedure EnvRemovePath(const DirToRemove: string);
var
  Paths, Remaining, Entry, NewPaths, Target: string;
  SepPos: Integer;
begin
  if not RegQueryStringValue(HKEY_CURRENT_USER, EnvKey, 'Path', Paths) then
    Exit;

  Target := LowerCase(NormalizeDir(DirToRemove));
  Remaining := Paths;
  NewPaths := '';
  while Length(Remaining) > 0 do
  begin
    SepPos := Pos(';', Remaining);
    if SepPos = 0 then
    begin
      Entry := Remaining;
      Remaining := '';
    end
    else
    begin
      Entry := Copy(Remaining, 1, SepPos - 1);
      Delete(Remaining, 1, SepPos);
    end;

    if (Trim(Entry) <> '') and (LowerCase(NormalizeDir(Entry)) <> Target) then
    begin
      if NewPaths <> '' then
        NewPaths := NewPaths + ';' + Entry
      else
        NewPaths := Entry;
    end;
  end;

  WriteUserPath(NewPaths);
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if (CurStep = ssPostInstall) and WizardIsTaskSelected('addtopath') then
    EnvAddPath(ExpandConstant('{app}'));
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usPostUninstall then
    EnvRemovePath(ExpandConstant('{app}'));
end;
