$ErrorActionPreference = "Stop"

$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[Console]::InputEncoding = $utf8NoBom
[Console]::OutputEncoding = $utf8NoBom
$OutputEncoding = $utf8NoBom
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
$PSDefaultParameterValues["Get-Content:Encoding"] = "UTF8"
chcp 65001 | Out-Null

git config core.autocrlf false
git config core.eol lf
git config i18n.commitEncoding utf-8
git config i18n.logOutputEncoding utf-8
git remote set-url origin git@github.com:DTALEX66/Cognitive-OS.git

Write-Output "Cognitive-OS environment configured: UTF-8 console, SSH origin, LF line endings."
