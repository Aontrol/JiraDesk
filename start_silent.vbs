' JiraDesk Silent Launcher
Set WshShell = CreateObject("WScript.Shell")
strPath = WshShell.CurrentDirectory
WshShell.Run "pythonw \"" & strPath & "\main.py\"", 0, False
