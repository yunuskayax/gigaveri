' VBScript başlatıcı - Çift tıklama ile çalışır
Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Mevcut dizini al
currentDir = fso.GetParentFolderName(WScript.ScriptFullName)

' Komut satırı penceresini açık tut
WshShell.CurrentDirectory = currentDir

' Python'un yüklü olup olmadığını kontrol et
Set pythonCheck = WshShell.Exec("python --version")
pythonCheck.StdOut.Close
pythonCheck.StdErr.Close

' Ana uygulamayı çalıştır
WshShell.Run "cmd /c ""python main.py""", 1, False

Set WshShell = Nothing
Set fso = Nothing

