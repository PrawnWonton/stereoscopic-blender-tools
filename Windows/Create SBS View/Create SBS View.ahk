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

; Title: Create SBS View
; Author: Jeff Boller (http://3d.simplecarnival.com)
; Description: Code to paste inside of your AutoHotKey system script that
;              creates a side-by-side stereo image in Blender (if using
;              the Simple Carnival Stereoscopic Camera and the Simple
;              Carnival Animation Template blend file). Detailed 
;              documentation is forthcoming.              
; Requirements: AutoHotKey v1.0.48.05 (http://www.autohotkey.com), 
;               Blender 2.73a (http://www.blender.org)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Modifications
;;
;; 1.0.0 - 3/19/15 - First public release on GitHub
;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;



#IfWinActive ahk_class GHOST_WindowClass ; Make SBS 3D popup
{
	; NOTE: Make sure to go into Blender and remove the F3 key binding so it can be used here!
	F3::

	; Make LEFT window
	MouseClick ,left,8,42
	Send {SHIFT down}
	MouseClickDrag ,left,8,42,39,42,100
	Send {SHIFT up}
	Sleep 50
	MouseClick ,left,254,38
	Sleep 50
	MouseClick ,left,254,38 ; Must do a slow double-click for some reason to get Blender to respond
	Sleep 100
	Send SBS LEFT{ENTER}
	Sleep 500
	MoveAndResizeWin(0,72,393,281)
	Sleep 100

	; Make RIGHT window
	MouseClick ,left,8,42
	Send {SHIFT down}
	MouseClickDrag ,left,8,42,39,42,100
	Send {SHIFT up}
	Sleep 50
	MouseClick ,left,254,38
	Sleep 50
	MouseClick ,left,254,38 ; Must do a slow double-click for some reason to get Blender to respond
	Sleep 100
	Send SBS Right{ENTER}
	Sleep 500
	MoveAndResizeWin(394,72,393,281)

	return


	MoveAndResizeWin(WinX=0, WinY=0, Width = 0,Height = 0)	
	{
		WinGetPos,X,Y,W,H,A
		If %Width% = 0		
			Width := W

		If %Height% = 0
			Height := H
	
		WinMove,A,,%WinX%,%WinY%,%Width%,%Height%
	}
}
