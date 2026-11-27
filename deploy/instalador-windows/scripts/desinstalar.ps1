# La ejecuta el desinstalador: detiene y elimina los contenedores. Con -BorrarDatos también borra la base y las imágenes.
param([switch]$BorrarDatos)
$ErrorActionPreference = "Continue"
$Aurora = Split-Path -Parent $PSScriptRoot
$args2 = @("compose", "--project-directory", $Aurora, "-f", (Join-Path $Aurora "docker-compose.local.yml"),
           "--env-file", (Join-Path $Aurora ".env"), "down")
if ($BorrarDatos) { $args2 += @("-v", "--rmi", "local") }
if (Get-Command docker -ErrorAction SilentlyContinue) { & docker @args2 }
