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

; Title: Monitor Blender Slave Dir
; Author: Jeff Boller (http://3d.simplecarnival.com)
; Description: I found Blender's built-in render farm to be limited and buggy, so I wrote my own. See the AutoHotKey script
;              "BlenderRenderFarm.au3" for the actual render farm. Monitor Blender Slave Dir is a complementary script that runs on
;              every slave computer. This code is currently optimized for my specific render farm setup. If you're comfortable
;              with scripting, it should be relatively straightforward to read the comments and change things to work on your system.
;              I'm open-sourcing this to encourage more people to explore making stereoscopic images with Blender and so that perhaps
;              someone could build off of this work to make a more polished application. My focus for this project has been on making
;              beautiful stereoscopic Blender videos, not making beautiful code. More detailed documentation is forthcoming.
; Requirements: AutoIt v3.3.8.1 (http://www.autoitscript.com), Blender 2.73a (http://www.blender.org)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Modifications
;;
;; 1.0.0 - 9/30/14 - Beta
;; 1.1.0 - 3/19/15 - First public release on GitHub
;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

#RequireAdmin

#include <GUIConstants.au3>
#include <file.au3>
#include <GUIListBox.au3>
#include <GuiConstantsEx.au3>
#include <Constants.au3>

Opt("SendKeyDelay", 10)

Const $processBlender = "blender.exe" ; What does Blender show up as in Process Manager?
Const $BlenderRenderFarm = "BlenderRenderFarm" ; What is the name of BlenderRenderFarm as a window?

$slaveDir = "D:\Video\Blender slave space"
If FileExists($slaveDir) = 0 Then
	$slaveDir = @DesktopDir & "\_SHARED\Blender slave space"
	If FileExists($slaveDir) = 0 Then
		$slaveDir = "C:\Video\Blender slave space" ; We don't have a D: drive
		If FileExists($slaveDir) = 0 Then
			$slaveDir = "C:\D\Video\Blender slave space" ; We don't have a D: drive
			If FileExists($slaveDir) = 0 Then
				MsgBox(0, "Error", "Cannot find $slaveDir: " & @CRLF & @CRLF & $slaveDir & @CRLF & @CRLF & "Are you sure you have this computer set up to be a slave?")
				Exit
			EndIf
		EndIf
	EndIf
EndIf

While 1
	If FileExists($slaveDir & "\BlenderRenderFarm\shutdown.dat") Then

		; Kill all the BlenderRenderFarm scripts (there should only be one running, but still...
		While WinExists("BlenderRenderFarm")
			Local $hwnd = WinGetHandle("BlenderRenderFarm")
				If IsHWnd($hwnd) Then
					If (NOT WinClose($hwnd)) Then WinKill($hwnd)
				EndIf
			Sleep(500)
		WEnd

		; Kill all the Blenders.
		While ProcessExists($processBlender)
			ProcessClose($processBlender)
			Sleep(500)
		WEnd

		; Erase the slave directories.
		DirClear($slaveDir)

		; Annnnnnnd shut down.
		Shutdown(BitOR($SD_SHUTDOWN, $SD_POWERDOWN))
		Exit;

	ElseIf FileExists($slaveDir & "\BlenderRenderFarm\kill.dat") Then

		; Kill all the BlenderRenderFarm scripts (there should only be one running, but still...
		While WinExists("BlenderRenderFarm")
			Local $hwnd = WinGetHandle("BlenderRenderFarm")
			If IsHWnd($hwnd) Then
				If (NOT WinClose($hwnd)) Then WinKill($hwnd)
			EndIf
			Sleep(500)
		WEnd

		; Kill all the Blenders.
		While ProcessExists($processBlender)
			ProcessClose($processBlender)
			Sleep(500)
		WEnd

		; Erase the slave directories.
		DirClear($slaveDir)

	ElseIf FileExists($slaveDir & "\BlenderRenderFarm\BlenderRenderFarm.au3") Then
		If FileExists($slaveDir & "\BlenderRenderFarm\status.log") <> 1 Then
			If FileExists($slaveDir & "\BlenderRenderFarm\params.dat") Then
				Local $fileRead = FileOpen($slaveDir & "\BlenderRenderFarm\params.dat", 0)
				Local $startupParams = FileReadLine($fileRead)
				FileClose($fileRead)

				; Launch it!
				ShellExecute("""" & $slaveDir & "\BlenderRenderFarm\BlenderRenderFarm.au3""", _
							$startupParams)
			EndIf
		EndIf
	EndIf
	Sleep(10000)
WEnd

Exit


Func DirClear($directory)
	FileDelete($directory)
	Local $array = _FileListToArray($directory)
	If IsArray($array) Then
		For $i=1 to $array[0]
			DirRemove(TrimBackslash($directory) & "\" & $array[$i], 1)
		Next
	EndIf
EndFunc


Func TrimBackslash($myPath)
	$retVal = $myPath
	If StringLen($myPath) > 0 Then
		If StringMid($myPath, StringLen($myPath), 1) = "\" Then
			$retVal = StringMid($myPath, 1, StringLen($myPath) - 1)
		EndIf
	EndIf
	Return $retVal
EndFunc
