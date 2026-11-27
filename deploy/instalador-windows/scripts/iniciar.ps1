# Inicia Aurora y abre el navegador.
. "$PSScriptRoot\comun.ps1"
Wait-Docker
Write-Paso "Iniciando Aurora"
Invoke-Compose up -d
if (-not (Wait-Aurora)) { Salir "Aurora no respondió. Use «Registros de Aurora» en el menú Inicio." }
Open-Url "http://localhost:$(Get-EnvValue 'HTTP_PORT')"
