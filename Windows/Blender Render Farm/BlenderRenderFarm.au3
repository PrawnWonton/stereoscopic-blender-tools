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

; Title: Blender Render Farm
; Author: Jeff Boller (http://3d.simplecarnival.com)
; Description: I found Blender's built-in render farm to be limited and buggy, so I wrote my own. This code is currently optimized for
;              my specific render farm setup as well as my own stereoscopic workflow and computer configurations. If you're comfortable
;              with scripting, it should be relatively straightforward to read the comments and change things to work on your system.
;              I should note that this is sloppy code and not representative of what I do for my day job as a software developer!
;              Also, this is truly one of the ugliest user interfaces I have ever created. I'm open-sourcing this to encourage more
;              people to explore making stereoscopic images with Blender and so that perhaps someone could build off of this work to
;              make a more polished application. My focus for this project has been on making beautiful stereoscopic Blender videos, not
;              making beautiful code. More detailed documentation is forthcoming.
; Requirements: AutoIt v3.3.8.1 (http://www.autoitscript.com), Blender 2.73a (http://www.blender.org),
;               VirtualDub 1.9.4 (http://virtualdub.org), Lagarith Lossless Codec 1.3.27 (http://lags.leetcode.net/codec.html).

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Modifications
;;
;; 1.0.0 - 6/20/2014 - First version. Works on a single machine; multi-computer rendering probably doesn't work yet
;; 1.0.1 - 6/22/2014 - Multi-computer rendering works. Kill switch works.
;; 1.0.2 - 8/1/2014 - Fixed some bugs, added the abilty to shut down the slave computers after rendering everything.
;; 1.0.3 - 8/4/2014 - Shuts down computer based on shutdown.dat, so the original script is erased before shutting down.
;; 1.0.4 - 9/19/14 - Remembers whether you chose the shut down slave computers option in the registry.
;; 1.1.0 - 12/24/14 - Put the Cancel button in a better place. Also has option to choose Lagarith compression for video. Also has option
;;                    to shut down master computer after rendering. Instead of being allowed to change the BRF file and then generating a
;;                    new one for slave computers on the fly, we now check If the BRF file is the same as what's currently loaded in memory
;;                    and prevents the render from running (on a multicomputer render only). Also automatically removes 0K placeholder files
;;                    If you stop a render before it's done.
;; 1.1.5 - 1/28/2015 - Changed the Blender process to blender-app.exe
;; 1.1.6 - 1/31/2015 - Made font smaller to fit all of the render computers.
;; 1.2.0 - 3/19/2015 - First public release on GitHub
;; 1.3.0 - 7/12/2015 - Wipes out 0kb placeholders that are in placeholder subdirectories per the way 2.75 works with stereoscopic rendering
;; 1.3.1 - 7/28/2015 - Finds out what version of Blender we're using on the local computer and writes it to a log file in the project
;;                     directory. Also grabs the product name (e.g. if it's "Better Blender" it'll pull that).
;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

#RequireAdmin ; This script requires full Administrative rights

#include <GUIConstants.au3>
#include <file.au3>
#include <GUIListBox.au3>
#include <GuiConstantsEx.au3>
#include <Constants.au3>
#include <Array.au3>

Opt("SendKeyDelay", 10)

; Command line parameters:
; 1 - IsSlave: 1 If it's a slave and we're going to send over a brf file. Any other value and we proceed as normal.
; 2 - Absolute path to brf file on the slave computer. Example: "V:\Video\Floor tom\Floor tom.brf"

$isSlave = 0
$saveParams = 1
$slaveStatusLogPath = ""
$slaveBlenderPath = ""
$slaveBRFLocation = ""
$slaveKillDatPath = ""
$slaveShutdownDatPath = ""

If $CMDLINE[0] > 0 Then
	If $CMDLINE[1] = 1 Then
		; We're a slave.
		$isSlave = 1
		$saveParams = 0
		$slaveStatusLogPath = @ScriptDir & "\status.log"
		$slaveKillDatPath = @ScriptDir & "\kill.dat"
		$slaveShutdownPath = @ScriptDir & "\shutdown.dat"
	EndIf

	If $CMDLINE[0] > 1 Then
		$slaveBRFLocation = $CMDLINE[2]
	EndIf
EndIf

WriteStatusLog("Initializing...") ; We need to immediately start a file so our monitoring program (MonitorBlenderSlaveDir) won't launch us twice.

If $isSlave = 0 Then
	If WinExists("BlenderRenderFarm") Then $saveParams = 0 ; Don't save to the registry If this is a 2nd instance!
EndIf
AutoItWinSetTitle("BlenderRenderFarm")

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; User params. Alter the parameters in this block to fit your system.
;;
$defaultBlendFileDir = "D:\Video" ; When we look for an Blender file in the GUI, where do we start?
Dim Const $processBlenderApp = "blender-app.exe" ; What does Blender show up as in Process Manager?
Dim Const $blenderEXE = "C:\Program Files\Blender Foundation\Blender\blender.exe" ; Where is the Blender EXE file?
Dim $virtualDubEXE = "C:\Program Files (x86)\VirtualDub-1.9.4\VirtualDub.exe" ; Where is the VirtualDub EXE file.
If FileExists($virtualDubEXE) = 0 Then
	$virtualDubEXE = "C:\Program Files\VirtualDub-1.9.4\VirtualDub.exe" ; This is an XP machine
EndIf

Dim Const $sleepMinRenderingAVI = 15 ; If we say to shut down the master computer and we're rendering an AVI in VirtualDub, how many minutes should we wait before shutting down the master computer?

; Multi-computer render values
; SI_ consts are used as a poor man's struct with $slaveInfo.
; The syntax is $slaveInfo[computer number][SI_ const]
Dim Const $NUM_OF_COMPUTERS = 6 ; How many computers could we potentially render on (besides this one)?
Dim Const $SI_COMPUTER_NAME = 0 ; What is the human-readable name for this computer? (Used for display purposes only.)
Dim Const $SI_PATH = 1 ; What is the path where we can find this slave?
Dim Const $SI_MASTER_DRIVE_FROM_SLAVE = 2 ; If we're on the slave computer and want to find the Blender file, what do we have to swap out the drive letter with to get there?
Dim Const $SI_ACTIVE = 3 ; Is this slave active? Integer 1 or 0. (This is so you can leave the script relatively unchanged and only sometimes use, say, a laptop computer.)
Dim Const $SI_DONE_RENDERING = 4 ; Is this slave done rendering? Integer 1 or 0.
Dim Const $SI_MAX_INDEX = 5; This should always be one more than the highest SI_ const.

; Set up all the slave computers here.
Dim $slaveInfo[$NUM_OF_COMPUTERS][$SI_MAX_INDEX]

; render1-pc
$slaveInfo[0][$SI_COMPUTER_NAME] = "render1-pc"
$slaveInfo[0][$SI_PATH] = "Q:\Video\Blender slave space"
$slaveInfo[0][$SI_MASTER_DRIVE_FROM_SLAVE] = "V"
$slaveInfo[0][$SI_ACTIVE] = 1

; render2-pc
$slaveInfo[1][$SI_COMPUTER_NAME] = "render2-pc"
$slaveInfo[1][$SI_PATH] = "R:\Video\Blender slave space"
$slaveInfo[1][$SI_MASTER_DRIVE_FROM_SLAVE] = "V"
$slaveInfo[1][$SI_ACTIVE] = 1

; render3-pc
$slaveInfo[2][$SI_COMPUTER_NAME] = "render3-pc"
$slaveInfo[2][$SI_PATH] = "S:\Video\Blender slave space"
$slaveInfo[2][$SI_MASTER_DRIVE_FROM_SLAVE] = "V"
$slaveInfo[2][$SI_ACTIVE] = 1

; render4-pc
$slaveInfo[3][$SI_COMPUTER_NAME] = "render4-pc"
$slaveInfo[3][$SI_PATH] = "T:\Video\Blender slave space"
$slaveInfo[3][$SI_MASTER_DRIVE_FROM_SLAVE] = "V"
$slaveInfo[3][$SI_ACTIVE] = 1

; render5-pc
$slaveInfo[4][$SI_COMPUTER_NAME] = "render5-pc"
$slaveInfo[4][$SI_PATH] = "W:\Video\Blender slave space"
$slaveInfo[4][$SI_MASTER_DRIVE_FROM_SLAVE] = "V"
$slaveInfo[4][$SI_ACTIVE] = 1

; redner6-pc
$slaveInfo[5][$SI_COMPUTER_NAME] = "render6-pc"
$slaveInfo[5][$SI_PATH] = "X:\Video\Blender slave space"
$slaveInfo[5][$SI_MASTER_DRIVE_FROM_SLAVE] = "V"
$slaveInfo[5][$SI_ACTIVE] = 1

;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;
;; Real code starts here. Do not change anything after this unless you know what you're doing!
;;
Dim Const $SL_MSG_DONE = "DONE!" ; The text we use in the status log to indicate that the slave is done rendering.
Dim $lastBRFLocation
Dim $originalBlenderFile
Dim $audioFilePath
Dim $renderLeftRightPNG
Dim $fullRender
Dim $renderLeftAVI
Dim $renderRightAVI
Dim $useLagarithCompression
Dim $multiComputerRender
Dim $framerate
Dim $shutDownSlavesWhenDone
Dim $shutDownMasterWhenDone

_RegistryProgramSettingsLoad()
$mainwindow = GUICreate("Blender Render Farm", 580, 640)

;;;;;;;;;;;;;;;;;;;;;;;; Batch file list area ;;;;;;;;;;;;;;;;;;;;;;;;;;
GUICtrlCreateLabel("Batch File List", 20, 300)
$hListBox = GUICtrlCreateList("", 20, 320, 500, 275, BitOR($LBS_STANDARD, $LBS_EXTENDEDSEL))
GUISetState()

$btnBatchFileAdd = GUICtrlCreateButton("Add", 530, 320)
$btnBatchFileDelete = GUICtrlCreateButton("Delete", 530, 350)
$btnBatchStart = GUICtrlCreateButton("Start Batch", 250, 600)
$chkShutDownSlavesWhenDone = GUICtrlCreateCheckbox("Shut down slaves when done", 350, 592)
$chkShutDownMasterWhenDone = GUICtrlCreateCheckbox("Shut down master when done", 350, 612)
GUICtrlCreateLabel("Blender File:", 20, 30)
$txtFilenameBLEND = GUICtrlCreateInput($originalBlenderFile, 100, 30, 420)
$btnFindFileBLEND = GUICtrlCreateButton("...", 530, 30)
GUICtrlCreateLabel("Audio File:", 20, 60)
$txtFilenameWAV = GUICtrlCreateInput($audioFilePath, 100, 60, 420)
$btnFindFileWAV = GUICtrlCreateButton("...", 530, 60)
GUICtrlCreateLabel("Framerate:", 20, 90)
$txtFramerate = GUICtrlCreateInput($framerate, 100, 90, 50)
$chkRenderLeftRightPNG = GUICtrlCreateCheckbox("Render Left/Right PNGs", 20, 120)
$chkFullRender = GUICtrlCreateCheckbox("Full render (wipe out current L/R/placeholder files)", 40, 140)
$chkRenderLeftAVI = GUICtrlCreateCheckbox("Create Left AVI", 20, 160)
$chkRenderRightAVI = GUICtrlCreateCheckbox("Create Right AVI", 20, 180)
$chkUseLagarithCompression = GUICtrlCreateCheckbox("Use Lagarith compression", 40, 200)
$chkMultiComputerRender = GUICtrlCreateCheckbox("Multi-computer render", 20, 220)
GUICtrlSetState($chkRenderLeftRightPNG, $renderLeftRightPNG)
GUICtrlSetState($chkFullRender, $fullRender)
GUICtrlSetState($chkRenderLeftAVI, $renderLeftAVI)
GUICtrlSetState($chkRenderRightAVI, $renderRightAVI)
GUICtrlSetState($chkUseLagarithCompression, $useLagarithCompression)
GUICtrlSetState($chkMultiComputerRender, $multiComputerRender)

If $shutDownSlavesWhenDone = 1 Then
   GUICtrlSetState($chkShutDownSlavesWhenDone, $GUI_CHECKED)
Else
   GUICtrlSetState($chkShutDownSlavesWhenDone, $GUI_UNCHECKED)
EndIf

If $shutDownMasterWhenDone = 1 Then
   GUICtrlSetState($chkShutDownMasterWhenDone, $GUI_CHECKED)
Else
   GUICtrlSetState($chkShutDownMasterWhenDone, $GUI_UNCHECKED)
EndIf

$btnOpen = GUICtrlCreateButton("Open", 0, 0)
$btnSave = GUICtrlCreateButton("Save", 40, 0)
$btnGo = GUICtrlCreateButton("      Go!      ", 20, 250)
GUICtrlSetState(-1, 512)
GUISetState(@SW_SHOW, $mainwindow)
_SetAppCaption()
$finalMsg = "Done!"; We store the final message here.

If $isSlave = 0 Then
	$hitGo = 0 ; 1= hit go. 2= hit start batch.

	; Run the GUI until the dialog is closed.
	Do
		Local $msg = GUIGetMsg()
		If $msg = $btnFindFileBLEND Then
			$msg = ""
			$var = FileOpenDialog("Choose the Blender file to render.", $defaultBlendFileDir, "Blender (*.blend)", 1 + 4)
			If @error Then
				; No file chosen.
			Else
				$originalBlenderFile = $var
				GUICtrlSetData($txtFilenameBLEND, $originalBlenderFile)
			EndIf
		ElseIf $msg = $btnFindFileWAV Then
			$msg = ""
			$var = FileOpenDialog("Choose the WAV file to use", $defaultBlendFileDir, "WAV (*.wav)", 1 + 4)
			If @error Then
				; No file chosen.
			Else
				$audioFilePath = $var
				GUICtrlSetData($txtFilenameWAV, $audioFilePath)
			EndIf
		ElseIf $msg = $btnOpen Then
			$var = FileOpenDialog("Open Blender Render Farm file", $lastBRFLocation, "BRF (*.BRF)")
			If @error Then
				; No file chosen.
			Else
				; Open it!
				$lastBRFLocation = $var
				OpenBRFFile($lastBRFLocation)
				PutValsIntoGUI()
				_SetAppCaption()
			EndIf
		ElseIf $msg = $btnSave Then
			$var = FileSaveDialog("Save Blender Render Farm file", $lastBRFLocation, "BRF (*.BRF)")
			If @error Then
				; No file chosen.
			Else
				; Save it!
				$lastBRFLocation = $var
				SaveBRFFile($lastBRFLocation)
				_SetAppCaption()
			EndIf
		ElseIf $msg = $btnBatchFileAdd Then
			$var = FileOpenDialog("Open Blender Render Farm file for batch", $defaultBlendFileDir, "BRF (*.BRF)")
			If @error Then
				; No file chosen
			Else
				_GUICtrlListBox_InsertString($hListBox, $var, -1)
			EndIf
		ElseIf $msg = $btnBatchFileDelete Then
			$aItems = _GUICtrlListBox_GetSelItems($hListBox)
			For $iI = $aItems[0] To 1 Step -1
				_GUICtrlListBox_DeleteString($hListBox, $aItems[$iI])
			Next
		ElseIf $msg = $btnBatchStart Then
			$hitGo = 2 ; Hit Start Batch
			ExitLoop
		ElseIf $msg = $btnGo Then
			If GUICtrlRead($chkMultiComputerRender) = $GUI_CHECKED Then
				; Make sure that we actually saved our BRF file before running and that the BRF file matches what's currently on the screen.
				If FileExists($lastBRFLocation) = 0 Then
					MsgBox(0, "Error", "Multicomputer rendering cannot begin until you save the current setup as a BRF file.")
				Else
					; Compare what we have on the screen with what we have in our BRF file. If it doesn't match, prevent rendering.
					; (We need to have a saved BRF file to send to all of the slave units.)
					$file = FileOpen($lastBRFLocation, 0)
					If $file = -1 Then
						MsgBox(0, "Error", "Unable to open BRF file for testing.")
						Exit
					EndIf

					$foundDifferentLine = 0
					If ($originalBlenderFile <> FileReadLine($file)) Then $foundDifferentLine = 1
					If ($audioFilePath <> FileReadLine($file)) Then $foundDifferentLine = 1
					If ($renderLeftRightPNG <> FileReadLine($file)) Then $foundDifferentLine = 1
					If ($fullRender <> FileReadLine($file)) Then $foundDifferentLine = 1
					If ($multiComputerRender <> FileReadLine($file)) Then $foundDifferentLine = 1
					If ($renderLeftAVI <> FileReadLine($file)) Then $foundDifferentLine = 1
					If ($renderRightAVI <> FileReadLine($file)) Then $foundDifferentLine = 1
					If ($framerate <> FileReadLine($file)) Then $foundDifferentLine = 1
					If ($useLagarithCompression <> FileReadLine($file)) Then $foundDifferentLine = 1
					FileClose($file)
					If $foundDifferentLine = 1 Then
						MsgBox(0, "Error", "Multicomputer rendering cannot begin until you save the current setup as a BRF file. (There is a difference between the saved BRF file and the setup currently shown in the user interface.)")
					Else
						; It's OK to let rendering happen.
						$hitGo = 1 ; Hit Go
						ExitLoop
					EndIf
				EndIf
			Else
				$hitGo = 1 ; Hit Go
				ExitLoop
			EndIf
		EndIf
	Until $msg = $GUI_EVENT_CLOSE

	If $hitGo <> 1 And $hitGo <> 2 Then Exit

	GUISetState(@SW_HIDE, $mainwindow)

	If $hitGo = 1 Then
		$timeStart = @HOUR & ":" & @MIN & ":" & @SEC
		StoreGUI()

		; Since we hit the Go button, back up all of our params in the registry
		; (assuming we're not running another instance of this macro... the first instance always gets priority for saving to the registry).
		If ($saveParams = 1) Then
			_RegistryProgramSettingsSave()
		EndIf

		_ChangeAllToRealPaths()
		RenderCurrent()
	ElseIf $hitGo = 2 Then
		$timeStart = @HOUR & ":" & @MIN & ":" & @SEC
		StoreGUI()
		$listboxCount = _GUICtrlListBox_GetCount($hListBox)
		For $iI = 1 To $listboxCount
			$lastBRFLocation = _GUICtrlListBox_GetText($hListBox, $iI - 1)
			OpenBRFFile($lastBRFLocation)
			_SetAppCaption()
			_ChangeAllToRealPaths()
			RenderCurrent()
		Next
	EndIf

    If $shutDownSlavesWhenDone = 1 Then
	  ; Send a signal to the slaves to shut down.
		For $i = 0 To $NUM_OF_COMPUTERS - 1
			If $slaveInfo[$i][$SI_ACTIVE] = 1 Then
			   ; Check to see If it is REALLY active or If this is a tease.
			   If FileExists($slaveInfo[$i][$SI_PATH]) = 0 Then
				  $slaveInfo[$i][$SI_ACTIVE] = 0 ; Bleh. Make this inactive.
			   Else
				  ; Now copy this exact script and its related support files. (It was deleted when it was done rendering, so we need to send it again.)
				  CopyScript($slaveInfo[$i][$SI_PATH])
				  Local $fileWrite = FileOpen($slaveInfo[$i][$SI_PATH] & "\BlenderRenderFarm\shutdown.dat", 2) ; Erase previous contents
				  FileWriteLine($fileWrite, "")
				  FileClose($fileWrite)
			   EndIf
			EndIf
		Next
    EndIf

	If $shutDownMasterWhenDone = 1 Then
		If $renderLeftAVI = 1 Or $renderRightAVI = 1 Then
			; We're rending an AVI. Wait a little bit until it's probably done.
			Sleep(1000 * 60 * $sleepMinRenderingAVI)
		EndIf
		Shutdown(BitOR($SD_SHUTDOWN, $SD_POWERDOWN)) ; Shut down the master computer.
		Exit
	EndIf

	MsgBox(0, "Done!", $finalMsg & @CRLF & @CRLF & "Elapsed time: " & _ElapsedTime($timeStart, @HOUR & ":" & @MIN & ":" & @SEC))
Else
	; We are a slave.
	GUISetState(@SW_HIDE, $mainwindow) ; Hide our main window.
	$lastBRFLocation = $slaveBRFLocation

    ; Open up the BRF file.
	OpenBRFFile($lastBRFLocation)
	_SetAppCaption()
	_ChangeAllToRealPaths()
	RenderCurrent()
EndIf

Exit


Func RenderCurrent()
	; Now figure out our filename.
	Dim $szDrive, $szDir, $szFilename, $szExt, $logFile
	_PathSplit($originalBlenderFile, $szDrive, $szDir, $szFilename, $szExt)
	$stereoFileDir = $szDrive & $szDir
	$logFile = $stereoFileDir & "_logfile.txt"
	$finalFileNameLeft = $szFilename & "-LEFT.avi"
	$finalFileNameRight = $szFilename & "-RIGHT.avi"
	$statusWindow = GUICreate("Rendering...", 780, 640)
	$btnCancel = GUICtrlCreateButton("Cancel", 390, 600)
	GUICtrlSetState(-1, 512)
	GUISetState(@SW_SHOW, $statusWindow)
	$lblStatusMsg = GUICtrlCreateLabel("Please wait......................................................................", 5, 5, 775, 555)
    GUICtrlSetFont($lblStatusMsg, 7)

	If $isSlave = 0 Then
		If $fullRender = 1 Then
			; Clear out all the files before starting.
			FileDelete($stereoFileDir & "_PLACEHOLDERS")
			FileDelete($stereoFileDir & "_LEFT")
			FileDelete($stereoFileDir & "_RIGHT")
		EndIf
	EndIf

	If $multiComputerRender  and $isSlave = 0 Then
		; Before we do anything, clear our $SI_DONE_RENDERING flags.
		For $i = 0 To $NUM_OF_COMPUTERS - 1
			$slaveInfo[$i][$SI_DONE_RENDERING] = 0
		Next

		For $i = 0 To $NUM_OF_COMPUTERS - 1
			If $slaveInfo[$i][$SI_ACTIVE] = 1 Then
				; Check to see If it is REALLY active or If this is a tease.
				If FileExists($slaveInfo[$i][$SI_PATH]) = 0 Then
					$slaveInfo[$i][$SI_ACTIVE] = 0 ; Bleh. Make this inactive.
				Else
					; Now copy this exact script and its related support files.
					GUICtrlSetData($lblStatusMsg, "Copying this script to the slave: " & $slaveInfo[$i][$SI_PATH])
					CopyScript($slaveInfo[$i][$SI_PATH])
					; Make a params.dat file and write it to our slave drive. (These are the startup params that we'll feed to this very script.)
					Dim $szDriveBRF, $szDirBRF, $szFilenameBRF, $szExtBRF
					_PathSplit($lastBRFLocation, $szDriveBRF, $szDirBRF, $szFilenameBRF, $szExtBRF)
					WriteParamsFile($slaveInfo[$i][$SI_MASTER_DRIVE_FROM_SLAVE] & ":" & $szDirBRF & $szFilenameBRF & $szExtBRF, $slaveInfo[$i][$SI_PATH] & "\BlenderRenderFarm\params.dat")
				EndIf
			EndIf
		Next
	EndIf

	If ($renderLeftRightPNG = 1) Then
		_FileWriteLog($logFile, @ComputerName & " : " & _FileGetProperty($blenderEXE, "product name") & " : " & FileGetVersion($blenderEXE) & " : " & $originalBlenderFile & " : Begin rendering")

		; Now run the command line and render these out.
		$DirCmd = Run("""" & $blenderEXE & """ -b """ & $originalBlenderFile & """ -a", "c:\", @SW_SHOW, $STDOUT_CHILD+$STDERR_CHILD)

		Local $ResponseText
		Local $LastLine
		Local $fullDisplayInfo
		Local $thisComputerInfo
		Local $msg
		Do
			$ResponseText = StdoutRead($DirCmd)
			$LastLine = StringLen($ResponseText) - 400
			If $LastLine > 0 Then
				$thisComputerInfo = StringMid($ResponseText, $LastLine)
				WriteStatusLog($thisComputerInfo)
			Else
				If StringLen($ResponseText) > 0 Then
					$thisComputerInfo = $ResponseText
					WriteStatusLog($thisComputerInfo)
				EndIf
			EndIf

			If $isSlave = 0 Then
				; Construct our full display info.
				Local $currentTime = _ElapsedTime($timeStart, @HOUR & ":" & @MIN & ":" & @SEC)
				$fullDisplayInfo = $currentTime & @CRLF & @CRLF & _
					"----- MASTER -----------------------" & @CRLF & _
					$thisComputerInfo & @CRLF & _
					@CRLF

				GUICtrlSetData($lblStatusMsg, GetMsgWithSlaveMsgs($fullDisplayInfo))

				$msg = GUIGetMsg()
				If $msg = $btnCancel Then
					If ReallyCancelRender() = True Then
						If ProcessExists($DirCmd) Then ProcessClose($DirCmd) ; This will close blender.exe only
						; ...and the blender-app exes.
						While ProcessExists($processBlenderApp)
						   ProcessClose($processBlenderApp)
						   Sleep(500)
						WEnd
						Clear0KbPlaceholders($originalBlenderFile);
						MsgBox(0, "Canceled", "The render was canceled.")
						Exit
					EndIf
				EndIf
			Else
			   If FileExists($slaveKillDatPath) Then
				  ; We must abort!
				  If ProcessExists($DirCmd) Then ProcessClose($DirCmd)
				  Exit
			   EndIf

			EndIf

			If @error Then ExitLoop
			Sleep(1000)
		Until ($msg = $GUI_EVENT_CLOSE Or ProcessExists($DirCmd) = 0)

		If ProcessExists($DirCmd) Then ; We clicked the "x" button on the window
			WriteKillDat()
			ProcessClose($DirCmd) ; This will close blender.exe only
			; ...and the blender-app exes.
			While ProcessExists($processBlenderApp)
			   ProcessClose($processBlenderApp)
			   Sleep(500)
			WEnd
			MsgBox(0, "Canceled", "The render was canceled.")
			Exit
		EndIf
	EndIf

	If $isSlave Then
		WriteStatusLog($SL_MSG_DONE) ; Indicate to the master that we're done.
		GUISetState(@SW_HIDE, $statusWindow);
		Exit
	EndIf

	; If we're running slaves, are they all done?
	If $multiComputerRender and $isSlave = 0 Then
		; Wait for the slaves to finish rendering.
		While 1
			$fullDisplayInfo = _ElapsedTime($timeStart, @HOUR & ":" & @MIN & ":" & @SEC) & @CRLF & @CRLF & _
				"----- MASTER -----------------------" & @CRLF & _
				"Waiting for slaves to finish..." & @CRLF & _
				@CRLF

			Local $bAllDoneRendering = 1

			For $i = 0 To $NUM_OF_COMPUTERS - 1
				If $slaveInfo[$i][$SI_ACTIVE] = 1 Then
					If $slaveInfo[$i][$SI_DONE_RENDERING] = 0 Then
						$bAllDoneRendering = 0
					EndIf
				EndIf
			Next

			If $bAllDoneRendering = 1 Then ExitLoop

			For $i = 0 To $NUM_OF_COMPUTERS - 1
				If $slaveInfo[$i][$SI_ACTIVE] = 1 Then
					If $slaveInfo[$i][$SI_DONE_RENDERING] = 0 Then
						If FileExists($slaveInfo[$i][$SI_PATH] & "\BlenderRenderFarm\status.log") Then
							Local $fileRead = FileOpen($slaveInfo[$i][$SI_PATH] & "\BlenderRenderFarm\status.log")
							Local $line = FileReadLine($fileRead)
							FileClose($fileRead)

							$fullDisplayInfo = $fullDisplayInfo & _
								"----- " & $slaveInfo[$i][$SI_COMPUTER_NAME] & " -----------------------" & @CRLF & _
								$line & @CRLF & _
								@CRLF

							If $line = $SL_MSG_DONE Then
								; Delete the stuff in our slave space.
								Local $array = StringSplit(TrimBackslash($szDir), "\", 1)

								GUICtrlSetData($lblStatusMsg, "Deleting " & $slaveInfo[$i][$SI_PATH] & "\" & $array[$array[0]])
								DirRemove($slaveInfo[$i][$SI_PATH] & "\" & $array[$array[0]], 1)

								GUICtrlSetData($lblStatusMsg, "Deleting " & $slaveInfo[$i][$SI_PATH] & "\BlenderRenderFarm")
								DirRemove($slaveInfo[$i][$SI_PATH] & "\BlenderRenderFarm", 1)

								$slaveInfo[$i][$SI_DONE_RENDERING] = 1 ; Set our flag to indicate we're done rendering.
							EndIf
						EndIf
					EndIf
				EndIf
			Next

			GUICtrlSetData($lblStatusMsg, $fullDisplayInfo)

			Local $msg = GUIGetMsg() ; Check for Cancel button
			If $msg = $btnCancel Then
				If ReallyCancelRender() = True Then
				  If ProcessExists($DirCmd) Then ProcessClose($DirCmd) ; This will close blender.Execute
				  ; ...and the blender-app exes.
				  While ProcessExists($processBlenderApp)
					 ProcessClose($processBlenderApp)
					 Sleep(500)
				  WEnd

				  Clear0KbPlaceholders($originalBlenderFile);
				  MsgBox(0, "Canceled", "The render was canceled.")
				  Exit
				EndIf
			EndIf
			If @error Then ExitLoop
			Sleep(1000)
		Wend
	EndIf

	If $renderLeftAVI = 1 Then
		; Now combine everything into a movie.
		GUICtrlSetData($lblStatusMsg, "Combining left files into a movie")
		Run($virtualDubEXE, "", @SW_MAXIMIZE)
		WinWait("VirtualDub")
		Sleep(10000)
		Send("^o")
		Sleep(1000)
		Send($stereoFileDir & "_LEFT\limg0001.png{ENTER}") ; This will bring in the entire movie
		Sleep(10000)
		Send("^r")
		Sleep(1000)
		Send("{DOWN}{TAB}")
		Sleep(1000)
		Send($framerate & "{ENTER}") ; 30 fps
		Sleep(1000)

		If $audioFilePath <> "" Then
			Send("!ao") ; Audio from other file...
			Sleep(1000)
			Send($audioFilePath & "{ENTER}")
			Sleep(1000)
		EndIf

		If $useLagarithCompression = 1 Then
			Send("^p") ; Compression
			Sleep(2000)
			Send("{TAB 2}") ; Go to the video compression list box
			Sleep(1000)
			Send("l") ; Choose Lagarith
			Sleep(1000)
			Send("{ENTER}")
			Sleep(1000)
		EndIf

		Send("{F7}") ; Save AVI
		Sleep(1000)
		Send($stereoFileDir & $finalFileNameLeft & "{ENTER}")
		Sleep(2000)
		Send("!y") ; Overwrite file? Yes
		Sleep(3000)
	EndIf

	If $renderRightAVI = 1 Then
		; Now combine everything into a movie.
		GUICtrlSetData($lblStatusMsg, "Combining right files into a movie")
		Run($virtualDubEXE, "", @SW_MAXIMIZE)
		WinWait("VirtualDub")
		Sleep(10000)
		Send("^o")
		Sleep(1000)
		Send($stereoFileDir & "_RIGHT\rimg0001.png{ENTER}") ; This will bring in the entire movie
		Sleep(10000)
		Send("^r")
		Sleep(1000)
		Send("{DOWN}{TAB}")
		Sleep(1000)
		Send($framerate & "{ENTER}") ; 30 fps
		Sleep(1000)

		If $audioFilePath <> "" Then
			Send("!ao") ; Audio from other file...
			Sleep(1000)
			Send($audioFilePath & "{ENTER}")
			Sleep(1000)
		EndIf

		If $useLagarithCompression = 1 Then
			Send("^p") ; Compression
			Sleep(2000)
			Send("{TAB 2}") ; Go to the video compression list box
			Sleep(1000)
			Send("l") ; Choose Lagarith
			Sleep(1000)
			Send("{ENTER}")
			Sleep(1000)
		EndIf

		Send("{F7}") ; Save AVI
		Sleep(1000)
		Send($stereoFileDir & $finalFileNameRight & "{ENTER}")
		Sleep(2000)
		Send("!y") ; Overwrite file? Yes
		Sleep(3000)
	EndIf

	GUISetState(@SW_HIDE, $statusWindow);

	If $renderLeftAVI = 1 Then
		$finalMsg = $finalMsg & @CRLF & $stereoFileDir & $finalFileNameLeft
	EndIf

	If $renderRightAVI = 1 Then
		$finalMsg = $finalMsg & @CRLF & $stereoFileDir & $finalFileNameRight
	EndIf
EndFunc

Func StoreGUI()
	$originalBlenderFile = GUICtrlRead($txtFilenameBLEND)
	$audioFilePath = GUICtrlRead($txtFilenameWAV)

	If GUICtrlRead($chkShutDownSlavesWhenDone) = $GUI_CHECKED Then
	  $shutDownSlavesWhenDone = 1
	Else
	  $shutDownSlavesWhenDone = 0
	EndIf

	If GUICtrlRead($chkShutDownMasterWhenDone) = $GUI_CHECKED Then
	  $shutDownMasterWhenDone = 1
	Else
	  $shutDownMasterWhenDone = 0
	EndIf

	If GUICtrlRead($chkRenderLeftRightPNG) = $GUI_CHECKED Then
		$renderLeftRightPNG = 1
	Else
		$renderLeftRightPNG = 0
	EndIf

	If GUICtrlRead($chkFullRender) = $GUI_CHECKED Then
		$fullRender = 1
	Else
		$fullRender = 0
	EndIf

	If GUICtrlRead($chkRenderLeftAVI) = $GUI_CHECKED Then
		$renderLeftAVI = 1
	Else
		$renderLeftAVI = 0
	EndIf

	If GUICtrlRead($chkRenderRightAVI) = $GUI_CHECKED Then
		$renderRightAVI = 1
	Else
		$renderRightAVI = 0
	EndIf

	If GUICtrlRead($chkUseLagarithCompression) = $GUI_CHECKED Then
		$useLagarithCompression = 1
	Else
		$useLagarithCompression = 0
	EndIf

	If GUICtrlRead($chkMultiComputerRender) = $GUI_CHECKED Then
		$multiComputerRender = 1
	Else
		$multiComputerRender = 0
	EndIf

	$framerate = GUICtrlRead($txtFramerate)
EndFunc


Func SaveBRFFile($filename)
	If FileExists($filename) Then
		FileDelete($filename) ; Hack. We must do this because FileWrite only appends stuff to a file, not replaces it.
	EndIf

	$file = FileOpen($filename, 1)

	; Check If file opened for writing OK
	If $file = -1 Then
		MsgBox(0, "Error", "Unable to save file.")
		Exit
	EndIf

	StoreGUI()

	FileWrite($file, $originalBlenderFile & @CRLF)
	FileWrite($file, $audioFilePath & @CRLF)
	FileWrite($file, $renderLeftRightPNG & @CRLF)
	FileWrite($file, $fullRender & @CRLF)
	FileWrite($file, $multiComputerRender & @CRLF)
	FileWrite($file, $renderLeftAVI & @CRLF)
	FileWrite($file, $renderRightAVI & @CRLF)
	FileWrite($file, $framerate & @CRLF)
	FileWrite($file, $useLagarithCompression & @CRLF)
	FileClose($file)
EndFunc


Func OpenBRFFile($filename)
	; Open it!
	$file = FileOpen($filename, 0)

	; Check If file opened for writing OK
	If $file = -1 Then
		MsgBox(0, "Error", "Unable to open file.")
		Exit
	EndIf

	$originalBlenderFile = FileReadLine($file)
	$audioFilePath = FileReadLine($file)

	If $isSlave Then
		Dim $szDrive, $szDir, $szFilename, $szExt
		_PathSplit($filename, $szDrive, $szDir, $szFilename, $szExt)
		If StringMid($originalBlenderFile, 2, 1) = ":" Then
			; Replace the drive letter with the BRF drive letter.
			$t = $szDrive & StringMid($originalBlenderFile, 3)
			$originalBlenderFile = $t
			; We don't worry about $audioFilePath since slaves never use that.
		EndIf
	EndIf

	$renderLeftRightPNG = FileReadLine($file)
	$fullRender = FileReadLine($file)
	$multiComputerRender = FileReadLine($file)
	$renderLeftAVI = FileReadLine($file)
	$renderRightAVI = FileReadLine($file)
	$framerate = FileReadLine($file)
	$useLagarithCompression = FileReadLine($file)
	FileClose($file)
EndFunc


Func PutValsIntoGUI()
	; Put it all in the GUI
	GUICtrlSetData($txtFilenameBLEND, $originalBlenderFile)
	GUICtrlSetData($txtFilenameWAV, $audioFilePath)

	If $renderLeftRightPNG = 1 Then
		GUICtrlSetState($chkRenderLeftRightPNG, $GUI_CHECKED)
	Else
		GUICtrlSetState($chkRenderLeftRightPNG, $GUI_UNCHECKED)
	EndIf

	If $fullRender = 1 Then
		GUICtrlSetState($chkFullRender, $GUI_CHECKED)
	Else
		GUICtrlSetState($chkFullRender, $GUI_UNCHECKED)
	EndIf

	If $renderLeftAVI = 1 Then
		GUICtrlSetState($chkRenderLeftAVI, $GUI_CHECKED)
	Else
		GUICtrlSetState($chkRenderLeftAVI, $GUI_UNCHECKED)
	EndIf

	If $renderRightAVI = 1 Then
		GUICtrlSetState($chkRenderRightAVI, $GUI_CHECKED)
	Else
		GUICtrlSetState($chkRenderRightAVI, $GUI_UNCHECKED)
	EndIf

	If $useLagarithCompression = 1 Then
		GUICtrlSetState($chkUseLagarithCompression, $GUI_CHECKED)
	Else
		GUICtrlSetState($chkUseLagarithCompression, $GUI_UNCHECKED)
	EndIf

	If $multiComputerRender = 1 Then
		GUICtrlSetState($chkMultiComputerRender, $GUI_CHECKED)
	Else
		GUICtrlSetState($chkMultiComputerRender, $GUI_UNCHECKED)
	EndIf

	GUICtrlSetData($txtFramerate, $framerate)
EndFunc


Func _ElapsedTime($OldTime, $NewTime)
	$old = StringSplit($OldTime, ":")
	$new = StringSplit($NewTime, ":")
	$Oseconds = $old[3] + ($old[2] * 60) + ($old[1] * 3600)
	$Nseconds = $new[3] + ($new[2] * 60) + ($new[1] * 3600)
	If $Oseconds > $Nseconds Then $Nseconds = $Nseconds + 24 * 3600

	$outsec = $Nseconds - $Oseconds
	$hour = Int($outsec / 3600)
	$min = Int(($outsec - ($hour * 3600)) / 60)
	$sec = $outsec - ($hour * 3600) - ($min * 60)
	$DiffTime = StringFormat("%02i:%02i:%02i", $hour, $min, $sec)
	Return $DiffTime
EndFunc


Func _GetRealPath($relativePath)
	$retVal = $relativePath
	If StringLen($relativePath) > 0 Then
		If StringMid($retVal, 2, 1) <> ":" Then
			; This is a relative path.
			If StringMid($retVal, 1, 1) = "\" Then
				; Remove the backslash at the beginning
				$retVal = StringMid($relativePath, 2)
			EndIf
			If ($lastBRFLocation) = "" Then
				MsgBox(0, "ERROR", "You are using a relative path for files, but you have not saved the brf file (so we know where to start)! Save the BRF file and try this again.")
				Return $relativePath
			EndIf

			Dim $szDrive, $szDir, $szFilename, $szExt
			_PathSplit($lastBRFLocation, $szDrive, $szDir, $szFilename, $szExt)
			$retVal = $szDrive & $szDir & $retVal ; Turn relative into real path.
		EndIf
	EndIf
	Return $retVal
EndFunc


Func _ChangeAllToRealPaths()
	; If we're using relative paths, make them full so we know where to load from.
	; Note that we do this after saving things to the registry (we want to save the relative (not real) paths there.
	$originalBlenderFile = _GetRealPath($originalBlenderFile)
	$audioFilePath = _GetRealPath($audioFilePath)
EndFunc


Func _SetAppCaption()
	If StringLen($lastBRFLocation) > 0 Then
		WinSetTitle($mainwindow, "", "BlenderRenderFarm - " & $lastBRFLocation)
	Else
		WinSetTitle($mainwindow, "", "BlenderRenderFarm")
	EndIf
EndFunc


Func _RegistryProgramSettingsLoad()
	$lastBRFLocation = RegRead("HKEY_CURRENT_USER\Software\BlenderRenderFarm", "lastBRFLocation") ; We need this so we can help determine relative paths
	$originalBlenderFile = RegRead("HKEY_CURRENT_USER\Software\BlenderRenderFarm", "originalBlenderFile")
	$audioFilePath = RegRead("HKEY_CURRENT_USER\Software\BlenderRenderFarm", "audioFilePath")
	$renderLeftRightPNG = RegRead("HKEY_CURRENT_USER\Software\BlenderRenderFarm", "renderLeftRightPNG")
	$fullRender = RegRead("HKEY_CURRENT_USER\Software\BlenderRenderFarm", "fullRender")
	$renderLeftAVI = RegRead("HKEY_CURRENT_USER\Software\BlenderRenderFarm", "renderLeftAVI")
	$renderRightAVI = RegRead("HKEY_CURRENT_USER\Software\BlenderRenderFarm", "renderRightAVI")
	$useLagarithCompression = RegRead("HKEY_CURRENT_USER\Software\BlenderRenderFarm", "useLagarithCompression")
	$multiComputerRender = RegRead("HKEY_CURRENT_USER\Software\BlenderRenderFarm", "multiComputerRender")
	$framerate = RegRead("HKEY_CURRENT_USER\Software\BlenderRenderFarm", "framerate")
	$shutDownSlavesWhenDone = RegRead("HKEY_CURRENT_USER\Software\BlenderRenderFarm", "shutDownSlavesWhenDone")
	$shutDownMasterWhenDone = RegRead("HKEY_CURRENT_USER\Software\BlenderRenderFarm", "shutDownMasterWhenDone")
EndFunc


Func _RegistryProgramSettingsSave()
	RegWrite("HKEY_CURRENT_USER\Software\BlenderRenderFarm", "lastBRFLocation", "REG_SZ", $lastBRFLocation)
	RegWrite("HKEY_CURRENT_USER\Software\BlenderRenderFarm", "originalBlenderFile", "REG_SZ", $originalBlenderFile)
	RegWrite("HKEY_CURRENT_USER\Software\BlenderRenderFarm", "audioFilePath", "REG_SZ", $audioFilePath)
	RegWrite("HKEY_CURRENT_USER\Software\BlenderRenderFarm", "renderLeftRightPNG", "REG_SZ", $renderLeftRightPNG)
	RegWrite("HKEY_CURRENT_USER\Software\BlenderRenderFarm", "fullRender", "REG_SZ", $fullRender)
	RegWrite("HKEY_CURRENT_USER\Software\BlenderRenderFarm", "renderLeftAVI", "REG_SZ", $renderLeftAVI)
	RegWrite("HKEY_CURRENT_USER\Software\BlenderRenderFarm", "renderRightAVI", "REG_SZ", $renderRightAVI)
	RegWrite("HKEY_CURRENT_USER\Software\BlenderRenderFarm", "useLagarithCompression", "REG_SZ", $useLagarithCompression)
	RegWrite("HKEY_CURRENT_USER\Software\BlenderRenderFarm", "multiComputerRender", "REG_SZ", $multiComputerRender)
	RegWrite("HKEY_CURRENT_USER\Software\BlenderRenderFarm", "framerate", "REG_SZ", $framerate)
	RegWrite("HKEY_CURRENT_USER\Software\BlenderRenderFarm", "shutDownSlavesWhenDone", "REG_SZ", $shutDownSlavesWhenDone)
	RegWrite("HKEY_CURRENT_USER\Software\BlenderRenderFarm", "shutDownMasterWhenDone", "REG_SZ", $shutDownMasterWhenDone)
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


Func CopyScript($pathDest)
	$pathSource = @ScriptDir ; Contains no trailing backslash.
	$pathDest = TrimBackslash($pathDest)

	Local $array = StringSplit($pathSource, "\", 1)
	$realDest = $pathDest & "\" & $array[$array[0]]
	DirCreate($realDest)

	FileCopy($pathSource & "\*.*", $realDest & "\", 9) ; Overwrite files and create destination directory If doesn't exist
	Sleep(500)
	DirCopy($pathSource & "\support", $realDest & "\support")
	Sleep(500)
EndFunc


Func WriteStatusLog($line)
	If $isSlave Then ; We don't bother writing anything If we're not a slave.
		Local $fileWrite = FileOpen($slaveStatusLogPath, 2) ; Erase previous contents
		FileWriteLine($fileWrite, $line)
		FileClose($fileWrite)
	EndIf
EndFunc

Func WriteKillDat()
	If $multiComputerRender = 1 and $isSlave=0 Then
		For $i = 0 To $NUM_OF_COMPUTERS - 1
			If $slaveInfo[$i][$SI_ACTIVE] = 1 Then
				Local $fileWrite = FileOpen($slaveInfo[$i][$SI_PATH] & "\BlenderRenderFarm\kill.dat", 2) ; Erase previous contents
				FileWriteLine($fileWrite, "")
				FileClose($fileWrite)
			EndIf
		Next
	EndIf
EndFunc


Func WriteParamsFile($slaveBRFPath, $paramsPath)
	Local $fileWrite = FileOpen($paramsPath, 2) ; Erase previous contents
	FileWriteLine($fileWrite, "1 """ & $slaveBRFPath & """")
	FileClose($fileWrite)
EndFunc


Func GetMsgWithSlaveMsgs($origMsg)
	Local $statusMsg = $origMsg  & @CRLF & @CRLF
	If $isSlave = 0 then
		For $i = 0 To $NUM_OF_COMPUTERS - 1
			If $slaveInfo[$i][$SI_ACTIVE] = 1 Then
				If $slaveInfo[$i][$SI_DONE_RENDERING] = 0 Then
					If FileExists($slaveInfo[$i][$SI_PATH] & "\BlenderRenderFarm\status.log") Then
						Local $fileRead = FileOpen($slaveInfo[$i][$SI_PATH] & "\BlenderRenderFarm\status.log")
						Local $line = FileRead($fileRead)
						FileClose($fileRead)
						$statusMsg = $statusMsg & _
							"----- " & $slaveInfo[$i][$SI_COMPUTER_NAME] & " -----------------------" & @CRLF & _
							$line & @CRLF & _
							@CRLF
					EndIf
				EndIf
			EndIf
		Next
	EndIf
	return $statusMsg
EndFunc


Func ReallyCancelRender()
	If MsgBox(4, "Cancel?", "Really cancel the render?") = 6 Then
		WriteKillDat()
		return true
	EndIf
	return false
EndFunc


Func Clear0KbPlaceholders($blenderFileLocation)
	; Blender will place 0K placeholders in The Simple Carnival Animation Template's _PLACEHOLDERS directory for any images that are currently being created
	; by a render computer. In >2.75, Once the image has been created, the placeholder is a bigger size (around 8K, I believe). It's also directly in the
	; _PLACEHOLDERS directory. In 2.75, the placeholder is the actual rendered picture. AND it's in a subdirectory if you're rendering a stereo image (so we will
	; need to search all subdirectories). If we stop a render before it's done, those 0K placeholder files will still be there. When you restart the render
	; (assuming you don't want to pick up where you left off), it will skip over those 0K placeholder files, which means they won't be rendered. By erasing any
	; 0K placeholders after canceling a render, this will force those in-progress frames to be rendered again the next time you start up the render.

	Dim $szDrive, $szDir, $szFilename, $szExt
	_PathSplit($blenderFileLocation, $szDrive, $szDir, $szFilename, $szExt)
	$placeholderDirectory = $szDrive & $szDir & "_PLACEHOLDERS"
	If DirGetSize($placeholderDirectory) = -1 Then return
	$array = _RecFileListToArray($placeholderDirectory, "*.png", 1, 1, 1)

	If (IsArray($array)) Then
		$iMax = UBound($array)
		for $i=1 to $iMax - 1
			If FileGetSize($array[$i]) = 0 Then
				FileDelete($array[$i])
			EndIf
		Next
	EndIf
EndFunc


; #FUNCTION# ====================================================================================================
; Name...........: _RecFileListToArray
; Description ...: Lists files and\or folders in a specified path (Similar to using Dir with the /B Switch)
; Syntax.........: _RecFileListToArray($sPath[, $sFilter = "*"[, $iFlag = 0[, $iRecur = 0[, $iFullPath = 0]]]])
; Parameters ....: $sPath   - Path to generate filelist for.
;                 $sFilter - Optional the filter to use, default is *. Search the Autoit3 helpfile for the word "WildCards" For details.
;                 $iFlag   - Optional: specifies whether to return files folders or both
;                 |$iFlag=0 (Default) Return both files and folders
;                 |$iFlag=1 Return files only
;                 |$iFlag=2 Return Folders only
;                 $iRecur  - Optional: specifies whether to search in subfolders
;                 |$iRecur=0 (Default) Do not search in subfolders
;                 |$iRecur=1 Search in subfolders
;                 $iFullPath  - Optional: specifies whether to include initial path in result string
;                 |$iFullPath=0 (Default) Do not include initial path
;                 |$iFullPath=1 Include initial path
; Return values .: @Error - 1 = Path not found or invalid
;                 |2 = Invalid $sFilter
;                 |3 = Invalid $iFlag
;                 |4 = Invalid $iRecur
;                 |5 = Invalid $iFullPath
;                 |6 = No File/Folder Found
; Author ........: SolidSnake <MetalGX91 at GMail dot com>
; Modified.......: 22 Jan 09 by Melba23 - added recursive search and full path options
; Remarks .......: The array returned is one-dimensional and is made up as follows:
;                               $array[0] = Number of Files\Folders returned
;                               $array[1] = 1st File\Folder
;                               $array[2] = 2nd File\Folder
;                               $array[3] = 3rd File\Folder
;                               $array[n] = nth File\Folder
; Related .......:
; Link ..........;
; Example .......; Yes
; ====================================================================================================
;Special Thanks to Helge and Layer for help with the $iFlag update
; speed optimization by code65536
;===============================================================================
Func _RecFileListToArray($sPath, $sFilter = "*", $iFlag = 0, $iRecur = 0, $iFullPath = 0)
    Local $asFileList[1], $sFullPath
    If Not FileExists($sPath) Then Return SetError(1, 1, "")
    If StringRight($sPath, 1) <> "\" Then $sPath = $sPath & "\"
    If (StringInStr($sFilter, "\")) Or (StringInStr($sFilter, "/")) Or (StringInStr($sFilter, ":")) Or (StringInStr($sFilter, ">")) Or (StringInStr($sFilter, "<")) Or (StringInStr($sFilter, "|")) Or (StringStripWS($sFilter, 8) = "") Then Return SetError(2, 2, "")
    If Not ($iFlag = 0 Or $iFlag = 1 Or $iFlag = 2) Then Return SetError(3, 3, "")
    If Not ($iRecur = 0 Or $iRecur = 1) Then Return SetError(4, 4, "")
    If $iFullPath = 0 Then
        $sFullPath = $sPath
    ElseIf $iFullPath = 1 Then
        $sFullPath = ""
    Else
        Return SetError(5, 5, "")
    EndIf
    _FLTA_Search($sPath, $sFilter, $iFlag, $iRecur, $sFullPath, $asFileList)
    If $asFileList[0] = 0 Then Return SetError(6, 6, "")
    Return $asFileList
EndFunc  ;==>_FileListToArray

; #INTERNAL_USE_ONLY#=================================================================================
; Name...........: _FLTA_Search
; Description ...: Searches folder for files and then recursively searches in subfolders
; Syntax.........: _FLTA_Search($sStartFolder, $sFilter, $iFlag, $iRecur, $sFullPath, ByRef $asFileList)
; Parameters ....: $sStartFolder - Value passed on from UBound($avArray)
;                 $sFilter - As set in _FileListToArray
;                 $iFlag - As set in _FileListToArray
;                 $iRecur - As set in _FileListToArray
;                 $sFullPath - $sPath as set in _FileListToArray
;                 $asFileList - Array containing found files/folders
; Return values .: None
; Author ........: Melba23 based on code from _FileListToArray by SolidSnake <MetalGX91 at GMail dot com>
; Modified.......:
; Remarks .......: This function is used internally by _FileListToArray.
; Related .......:
; Link ..........;
; Example .......;
; ====================================================================================================
Func _FLTA_Search($sStartFolder, $sFilter, $iFlag, $iRecur, $sFullPath, ByRef $asFileList)

    Local $hSearch, $sFile

    If StringRight($sStartFolder, 1) <> "\" Then $sStartFolder = $sStartFolder & "\"
; First look for filtered files/folders in folder
    $hSearch = FileFindFirstFile($sStartFolder & $sFilter)
    If $hSearch > 0 Then
        While 1
            $sFile = FileFindNextFile($hSearch)
            If @error Then ExitLoop
            Switch $iFlag
                Case 0; Both files and folders
                    If $iRecur And StringInStr(FileGetAttrib($sStartFolder & $sFile), "D") <> 0 Then ContinueLoop
                Case 1; Files Only
                    If StringInStr(FileGetAttrib($sStartFolder & $sFile), "D") <> 0 Then ContinueLoop
                Case 2; Folders only
                    If StringInStr(FileGetAttrib($sStartFolder & $sFile), "D") = 0 Then ContinueLoop
            EndSwitch
            If $iFlag = 1 And StringInStr(FileGetAttrib($sStartFolder & $sFile), "D") <> 0 Then ContinueLoop
            If $iFlag = 2 And StringInStr(FileGetAttrib($sStartFolder & $sFile), "D") = 0 Then ContinueLoop
            _FLTA_Add($asFileList, $sFullPath, $sStartFolder, $sFile)
        WEnd
        FileClose($hSearch)
        ReDim $asFileList[$asFileList[0] + 1]
    EndIf

    If $iRecur = 1 Then
    ; Now look for subfolders
        $hSearch = FileFindFirstFile($sStartFolder & "*.*")
        If $hSearch > 0 Then
            While 1
                $sFile = FileFindNextFile($hSearch)
                If @error Then ExitLoop
                If StringInStr(FileGetAttrib($sStartFolder & $sFile), "D") And ($sFile <> "." Or $sFile <> "..") Then
                ; If folders needed, add subfolder to array
                    If $iFlag <> 1 Then _FLTA_Add($asFileList, $sFullPath, $sStartFolder, $sFile)
                ; Recursive search of this subfolder
                    _FLTA_Search($sStartFolder & $sFile, $sFilter, $iFlag, $iRecur, $sFullPath, $asFileList)
                EndIf
            WEnd
            FileClose($hSearch)
        EndIf
    EndIf

EndFunc

; #INTERNAL_USE_ONLY#=================================================================================
; Name...........: _FLTA_Add
; Description ...: Searches folder for files and then recursively searches in subfolders
; Syntax.........: _FLTA_Add(ByRef $asFileList, $sFullPath, $sStartFolder, $sFile)
; Parameters ....: $asFileList - Array containing found files/folders
;                 $sFullPath - $sPath as set in _FileListToArray
;                 $sStartFolder - Value passed on from UBound($avArray)
;                 $sFile - Full path of file/folder to add to $asFileList
; Return values .: Function only changes $asFileList ByRef
; Author ........: Melba23 based on code from _FileListToArray by SolidSnake <MetalGX91 at GMail dot com>
; Modified.......:
; Remarks .......: This function is used internally by _FileListToArray.
; Related .......:
; Link ..........;
; Example .......;
; ====================================================================================================
Func _FLTA_Add(ByRef $asFileList, $sFullPath, $sStartFolder, $sFile)

    Local $sAddFolder

    $asFileList[0] += 1
    If UBound($asFileList) <= $asFileList[0] Then ReDim $asFileList[UBound($asFileList) * 2]
    If $sFullPath = "" Then
        $sAddFolder = $sStartFolder
    Else
        $sAddFolder = StringReplace($sStartFolder, $sFullPath, "")
    EndIf
    $asFileList[$asFileList[0]] = $sAddFolder & $sFile

EndFunc

;===============================================================================
; Function Name.....: _FileGetProperty
; Description.......: Returns a property or all properties for a file.
; Version...........: 1.0.2
; Change Date.......: 05-16-2012
; AutoIt Version....: 3.2.12.1+
; Parameter(s)......: $FGP_Path - String containing the file path to return the property from.
;                     $FGP_PROPERTY - [optional] String containing the name of the property to return. (default = "")
;                     $iPropertyCount - [optional] The number of properties to search through for $FGP_PROPERTY, or the number of items
;                                       returned in the array if $FGP_PROPERTY is blank. (default = 300)
; Requirements(s)...: None
; Return Value(s)...: Success: Returns a string containing the property value.
;                     If $FGP_PROPERTY is blank, a two-dimensional array is returned:
;                         $av_array[0][0] = Number of properties.
;                         $av_array[1][0] = 1st property name.
;                         $as_array[1][1] = 1st property value.
;                         $av_array[n][0] = nth property name.
;                         $as_array[n][1] = nth property value.
;                     Failure: Returns an empty string and sets @error to:
;                       1 = The folder $FGP_Path does not exist.
;                       2 = The property $FGP_PROPERTY does not exist or the array could not be created.
;                       3 = Unable to create the "Shell.Application" object $objShell.
; Author(s).........: - Simucal <Simucal@gmail.com>
;                     - Modified by: Sean Hart <autoit@hartmail.ca>
;                     - Modified by: teh_hahn <sPiTsHiT@gmx.de>
;                     - Modified by: BrewManNH
; URL...............: http://www.autoitscript.com/forum/topic/34732-udf-getfileproperty/page__view__findpost__p__557571
; Note(s)...........: Modified the script that teh_hahn posted at the above link to include the properties that
;                     Vista and Win 7 include that Windows XP doesn't. Also removed the ReDims for the $av_ret array and
;                     replaced it with a single ReDim after it has found all the properties, this should speed things up.
;                     I further updated the code so there's a single point of return except for any errors encountered.
;                     $iPropertyCount is now a function parameter instead of being hardcoded in the function itself.
;===============================================================================
Func _FileGetProperty($FGP_Path, $FGP_PROPERTY = "", $iPropertyCount = 300)
    If $FGP_PROPERTY = Default Then $FGP_PROPERTY = ""
    $FGP_Path = StringRegExpReplace($FGP_Path, '["'']', "") ; strip the quotes, if any from the incoming string
    If Not FileExists($FGP_Path) Then Return SetError(1, 0, "") ; path not found
    Local Const $objShell = ObjCreate("Shell.Application")
    If @error Then Return SetError(3, 0, "")
    Local Const $FGP_File = StringTrimLeft($FGP_Path, StringInStr($FGP_Path, "\", 0, -1))
    Local Const $FGP_Dir = StringTrimRight($FGP_Path, StringLen($FGP_File) + 1)
    Local Const $objFolder = $objShell.NameSpace($FGP_Dir)
    Local Const $objFolderItem = $objFolder.Parsename($FGP_File)
    Local $Return = "", $iError = 0
    If $FGP_PROPERTY Then
        For $I = 0 To $iPropertyCount
            If $objFolder.GetDetailsOf($objFolder.Items, $I) = $FGP_PROPERTY Then
                $Return = $objFolder.GetDetailsOf($objFolderItem, $I)
            EndIf
        Next
        If $Return = "" Then
            $iError = 2
        EndIf
    Else
        Local $av_ret[$iPropertyCount + 1][2] = [[0]]
        For $I = 1 To $iPropertyCount
            If $objFolder.GetDetailsOf($objFolder.Items, $I) Then
                $av_ret[$I][0] = $objFolder.GetDetailsOf($objFolder.Items, $I - 1)
                $av_ret[$I][1] = $objFolder.GetDetailsOf($objFolderItem, $I - 1)
                $av_ret[0][0] += 1
            EndIf
        Next
        ReDim $av_ret[$av_ret[0][0] + 1][2]
        If Not $av_ret[1][0] Then
            $iError = 2
            $av_ret = $Return
        Else
            $Return = $av_ret
        EndIf
    EndIf
    Return SetError($iError, 0, $Return)
EndFunc   ;==>_FileGetProperty
