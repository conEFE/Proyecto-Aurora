# Primera configuración (la ejecuta el instalador): genera .env con secretos aleatorios, construye las imágenes,
# inicia Aurora y crea el primer ADMIN. Los datos del ADMIN llegan en un archivo temporal que se borra al leerlo.
param([string]$DatosAdmin, [int]$Puerto = 0, [switch]$PedirAdmin)
. "$PSScriptRoot\comun.ps1"

function New-Secreto([int]$bytes) {
    $b = New-Object byte[] $bytes
    [System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($b)
    return $b
}
function UrlSafe([byte[]]$b) { [Convert]::ToBase64String($b).Replace('+', '-').Replace('/', '_') }

if (-not $Puerto) { $Puerto = if (Test-Path $EnvFile) { [int](Get-EnvValue 'HTTP_PORT') } else { 8080 } }
Write-Host "Aurora: configuración inicial (solo datos ficticios; IA SIMULADA)" -ForegroundColor Magenta

if (-not (Test-Path $EnvFile)) {
    Write-Paso "Generando la configuración y los secretos"
    $plantilla = Get-Content (Join-Path $Aurora (Join-Path "app" (Join-Path "deploy" ".env.example")))
    $valores = @{
        "POSTGRES_PASSWORD" = (UrlSafe (New-Secreto 24)).TrimEnd('=')
        "SECRET_KEY"        = (UrlSafe (New-Secreto 48)).TrimEnd('=')
        "ENCRYPTION_KEY"    = (UrlSafe (New-Secreto 32))      # clave Fernet: 32 bytes en base64 url-safe
        "PUBLIC_URL"        = "http://localhost:$Puerto"
        "HTTP_PORT"         = "$Puerto"
        "TRUST_PROXY_HEADERS" = "true"
        "INFERENCE_PROVIDER" = "simulated"
        "EMAIL_PROVIDER"    = "console"
    }
    $salida = foreach ($l in $plantilla) {
        if ($l -match '^([A-Z_]+)=' -and $valores.ContainsKey($Matches[1])) { "$($Matches[1])=$($valores[$Matches[1]])" }
        elseif ($l -match '^COMPOSE_PROFILES=') { "# $l" }
        else { $l }
    }
    Set-Content -Path $EnvFile -Value $salida -Encoding ascii
    # Solo el usuario actual puede leer la configuración (contiene secretos)
    if ($env:OS -eq "Windows_NT") { icacls $EnvFile /inheritance:r /grant:r "$($env:USERNAME):(M)" *> $null }
}

Wait-Docker
Write-Paso "Construyendo Aurora (la primera vez tarda entre 5 y 15 minutos y necesita internet)"
Invoke-Compose build
if ($LASTEXITCODE -ne 0) { Salir "Falló la construcción. Revise la conexión a internet y ejecute «Reparar Aurora» desde el menú Inicio." }
Write-Paso "Iniciando Aurora"
Invoke-Compose up -d
if (-not (Wait-Aurora)) { Salir "Aurora no respondió. Revise los registros con «Registros de Aurora» en el menú Inicio." }

$d = $null
if ($DatosAdmin -and (Test-Path $DatosAdmin)) {
    $d = Get-Content $DatosAdmin -Encoding UTF8; Remove-Item $DatosAdmin -Force
} elseif ($PedirAdmin) {
    Write-Paso "Datos del primer administrador (si ya existe, deje el RUT vacío)"
    $rut = Read-Host "RUT (ej. 11111111-1)"
    if ($rut) {
        $p = Read-Host "Contraseña temporal (mín. 10, letras y números)" -AsSecureString
        $d = @($rut, (Read-Host "Nombre"), (Read-Host "Correo"), [System.Net.NetworkCredential]::new("", $p).Password)
    }
}
if ($d) {
    Write-Paso "Creando el primer administrador"
    Invoke-Compose exec -T -e "AURORA_ADMIN_RUT=$($d[0])" -e "AURORA_ADMIN_NAME=$($d[1])" -e "AURORA_ADMIN_EMAIL=$($d[2])" `
        -e "AURORA_ADMIN_PASSWORD=$($d[3])" backend python init_user.py
    if ($LASTEXITCODE -ne 0) { Write-Host "No se pudo crear el administrador (puede que ya exista)." -ForegroundColor Yellow }
}

Write-Host "`nAurora está lista en http://localhost:$Puerto" -ForegroundColor Green
Open-Url "http://localhost:$Puerto"
if (-not $env:CI) { Start-Sleep 3 }
