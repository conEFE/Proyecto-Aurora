# Detiene Aurora (los datos se conservan).
. "$PSScriptRoot\comun.ps1"
Wait-Docker
Invoke-Compose stop
Write-Host "Aurora detenida. Los datos se conservan." -ForegroundColor Green; Start-Sleep 2
