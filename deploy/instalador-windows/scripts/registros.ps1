# Muestra los últimos registros (también los enlaces de activación de cuentas: EMAIL_PROVIDER=console).
. "$PSScriptRoot\comun.ps1"
Wait-Docker
Invoke-Compose logs --tail 200 backend web
Read-Host "Presione Enter para cerrar"
