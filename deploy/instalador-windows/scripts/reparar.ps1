# Reconstruye las imágenes y reinicia Aurora (los datos se conservan).
. "$PSScriptRoot\comun.ps1"
Wait-Docker
Invoke-Compose build --pull
Invoke-Compose up -d --force-recreate
if (Wait-Aurora) { Write-Host "Aurora funcionando." -ForegroundColor Green } else { Write-Host "Aurora no respondió." -ForegroundColor Red }
Read-Host "Presione Enter para cerrar"
