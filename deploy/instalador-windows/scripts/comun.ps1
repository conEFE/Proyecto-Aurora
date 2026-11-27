# Funciones comunes de los scripts de Aurora (instalación local en Windows).
$ErrorActionPreference = "Stop"
$Aurora = Split-Path -Parent $PSScriptRoot          # carpeta de instalación
$Compose = Join-Path $Aurora "docker-compose.local.yml"
$EnvFile = Join-Path $Aurora ".env"

function Write-Paso($m) { Write-Host "`n==> $m" -ForegroundColor Cyan }
function Salir($m, $code = 1) { Write-Host "`n$m" -ForegroundColor Red; if (-not $env:CI) { Read-Host "Presione Enter para cerrar" }; exit $code }

function Get-EnvValue($name) {
    $l = Get-Content $EnvFile | Where-Object { $_ -match "^$name=" } | Select-Object -First 1
    if ($l) { return $l.Substring($name.Length + 1) } else { return "" }
}

function Open-Url($u) { if ($env:CI) { return }; try { Start-Process $u } catch {} }

function Invoke-Compose { & docker compose --project-directory $Aurora -f $Compose --env-file $EnvFile @args }

function Wait-Docker {
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        Salir "No se encontró Docker. Instale Docker Desktop (https://www.docker.com/products/docker-desktop/) y vuelva a abrir Aurora."
    }
    docker info *> $null
    if ($LASTEXITCODE -eq 0) { return }
    $dd = if ($env:ProgramFiles) { Join-Path $env:ProgramFiles "Docker\Docker\Docker Desktop.exe" } else { "" }
    if ($dd -and (Test-Path $dd)) { Write-Paso "Iniciando Docker Desktop..."; Start-Process $dd }
    for ($i = 0; $i -lt 90; $i++) {
        Start-Sleep 2; docker info *> $null
        if ($LASTEXITCODE -eq 0) { return }
    }
    Salir "Docker no respondió. Abra Docker Desktop, espere a que diga «Engine running» y vuelva a intentarlo."
}

function Wait-Aurora {
    $url = "http://localhost:$(Get-EnvValue 'HTTP_PORT')/api/health"
    for ($i = 0; $i -lt 120; $i++) {
        try { if ((Invoke-WebRequest $url -UseBasicParsing -TimeoutSec 3).StatusCode -eq 200) { return $true } } catch {}
        Start-Sleep 3
    }
    return $false
}
