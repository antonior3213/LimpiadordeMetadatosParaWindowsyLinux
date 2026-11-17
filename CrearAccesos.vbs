Option Explicit
On Error Resume Next
Dim action, exePath, installDir, shell, fso, desktopLink, startRoot, startFolder, appLink
Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
If WScript.Arguments.Count < 3 Then WScript.Quit 2
action = LCase(WScript.Arguments(0))
exePath = WScript.Arguments(1)
installDir = WScript.Arguments(2)
desktopLink = shell.SpecialFolders("Desktop") & "\Limpiador de Google Takeout.lnk"
startRoot = shell.SpecialFolders("Programs")
startFolder = startRoot & "\Limpiador de Google Takeout"
appLink = startFolder & "\Limpiador de Google Takeout.lnk"

If action = "instalar" Then
  If Not fso.FolderExists(startFolder) Then fso.CreateFolder startFolder
  If Err.Number <> 0 Then WScript.Quit 1
  CreateAppShortcut desktopLink, exePath, installDir
  CreateAppShortcut appLink, exePath, installDir
  If Err.Number <> 0 Then WScript.Quit 1
ElseIf action = "desinstalar" Then
  If fso.FileExists(desktopLink) Then fso.DeleteFile desktopLink, True
  If fso.FileExists(appLink) Then fso.DeleteFile appLink, True
  If fso.FolderExists(startFolder) Then fso.DeleteFolder startFolder, True
  If Err.Number <> 0 Then WScript.Quit 1
Else
  WScript.Quit 2
End If
WScript.Quit 0

Sub CreateAppShortcut(shortcutPath, targetPath, workingDirectory)
  Dim shortcut
  Set shortcut = shell.CreateShortcut(shortcutPath)
  shortcut.TargetPath = targetPath
  shortcut.WorkingDirectory = workingDirectory
  shortcut.Description = "Quita los JSON de metadatos de Google Takeout"
  shortcut.Save
End Sub
