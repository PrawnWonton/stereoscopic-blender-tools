; ##### BEGIN GPL LICENSE BLOCK #####
;
;  This program is free software; you can redistribute it and/or
;  modify it under the terms of the GNU General Public License
;  as published by the Free Software Foundation; either version 2
;  of the License, or (at your option) any later version.
;
;  This program is distributed in the hope that it will be useful,
;  but WITHOUT ANY WARRANTY; without even the implied warranty of
;  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
;  GNU General Public License for more details.
;
;  You should have received a copy of the GNU General Public License
;  along with this program; If not, write to the Free Software Foundation,
;  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
;
; ##### END GPL LICENSE BLOCK #####

; Title: BISE installer
; Author: Jeff Boller (http://3d.simplecarnival.com)
; Description: Installer for BISE (Blender Image Sequence Editor)
; Requirements: Inno Setup 5.5.5 (u), Inno Script Studio 2.1.0.20

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Modifications
;;
;; 1.0.0 - 3/19/15 - First public release on GitHub
;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

#define MyAppName "BISE"
#define MyAppVersion "2.0"
#define MyAppPublisher "Jeff Boller"
#define MyAppURL "http://3d.simplecarnival.com"
#define MyAppExeName "BISE.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{36424D02-9B10-49AF-B4D2-6C0B691B8EBA}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={pf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
LicenseFile=..\source code\BISE\Resources\license.txt
OutputBaseFilename=setup_{#MyAppName}_{#MyAppVersion}
Compression=lzma
SolidCompression=yes
ChangesAssociations=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; 

[Files]
Source: "..\source code\BISE\bin\Release\BISE.exe"; DestDir: "{app}"; Flags: ignoreversion
; NOTE: Don't use "Flags: ignoreversion" on any shared system files
Source: "..\source code\BISE\version history.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{group}\Version History"; Filename: "{app}\version history.txt"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Registry]
Root: HKCR; Subkey: ".bise"; ValueType: string; ValueName: ""; ValueData: "BISEFile"; Flags: uninsdeletevalue 
Root: HKCR; Subkey: "BISEFile"; ValueType: string; ValueName: ""; ValueData: "BISE File"; Flags: uninsdeletekey
Root: HKCR; Subkey: "BISEFile\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\BISE.exe,0"
Root: HKCR; Subkey: "BISEFile\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\BISE.exe"" ""%1"""

