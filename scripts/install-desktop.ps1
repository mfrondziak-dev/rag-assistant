$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$target = Join-Path $root "start.bat"

if (-not (Test-Path $target)) {
    Write-Host "Nie znaleziono start.bat / start.bat not found: $target"
    exit 1
}

$desktop = [Environment]::GetFolderPath("Desktop")
$link = Join-Path $desktop "Zapytaj swoje dokumenty.lnk"

$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($link)
$shortcut.TargetPath = $target
$shortcut.WorkingDirectory = $root
$shortcut.IconLocation = "$env:SystemRoot\System32\shell32.dll,13"
$shortcut.Save()

Write-Host "Dodano skrot na pulpicie / Desktop shortcut added:"
Write-Host "  $link"
Write-Host "Uruchom: powershell -ExecutionPolicy Bypass -File scripts\install-desktop.ps1"
