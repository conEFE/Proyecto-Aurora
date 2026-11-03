# Script para crear ZIP limpio del proyecto Proyecto Aurora
# Excluye node_modules, venv, archivos temporales y sensibles

param(
    [string]$NombreZip = "Proyecto-Aurora-Limpio.zip"
)

$ErrorActionPreference = "Stop"

# Colores para mensajes
function Write-Success { param($msg) Write-Host $msg -ForegroundColor Green }
function Write-Info { param($msg) Write-Host $msg -ForegroundColor Cyan }
function Write-Warning { param($msg) Write-Host $msg -ForegroundColor Yellow }
function Write-Error { param($msg) Write-Host $msg -ForegroundColor Red }

Write-Info "========================================="
Write-Info "  Creando ZIP limpio del proyecto"
Write-Info "========================================="
Write-Host ""

# Verificar que estamos en el directorio correcto
if (-not (Test-Path "backend") -or -not (Test-Path "src")) {
    Write-Error "Error: Este script debe ejecutarse desde la raíz del proyecto 'Proyecto Aurora'"
    exit 1
}

# Eliminar ZIP anterior si existe
if (Test-Path $NombreZip) {
    Remove-Item $NombreZip -Force
    Write-Warning "ZIP anterior eliminado."
}

# Crear carpeta temporal limpia
$tempDir = "Proyecto-Aurora-Temp"
if (Test-Path $tempDir) {
    Remove-Item $tempDir -Recurse -Force
}
New-Item -ItemType Directory -Path $tempDir | Out-Null

Write-Info "Copiando archivos necesarios..."

# Definir qué excluir
$excluirCarpetas = @("node_modules", "venv", "__pycache__", "dist", "dist-ssr", ".vscode", ".idea")
$excluirArchivos = @("*.pyc", "*.pyo", "*.pyd", "*.log", ".env", ".DS_Store")
$excluirExtensiones = @(".pyc", ".pyo", ".pyd", ".log")

# Función para determinar si un path debe ser excluido
function Test-ShouldExclude {
    param([string]$fullPath, [string]$relativePath)
    
    # Excluir carpetas completas
    foreach ($carpeta in $excluirCarpetas) {
        if ($relativePath -like "*\$carpeta\*" -or $relativePath -like "$carpeta\*") {
            return $true
        }
    }
    
    # Excluir archivos por extensión
    $extension = [System.IO.Path]::GetExtension($fullPath)
    if ($extension -in $excluirExtensiones) {
        return $true
    }
    
    # Excluir archivos específicos
    $fileName = Split-Path $fullPath -Leaf
    if ($fileName -eq ".env" -or $fileName -eq ".DS_Store") {
        return $true
    }
    
    # Excluir archivos de log
    if ($fileName -like "*.log") {
        return $true
    }
    
    return $false
}

# Copiar archivos recursivamente
$totalFiles = 0
$copiedFiles = 0
$excludedFiles = 0

Get-ChildItem -Path . -Recurse -File | ForEach-Object {
    $totalFiles++
    $fullPath = $_.FullName
    $relativePath = $fullPath.Replace((Get-Location).Path + "\", "")
    
    # Saltar si está en la carpeta temporal
    if ($relativePath -like "$tempDir\*") {
        return
    }
    
    if (Test-ShouldExclude -fullPath $fullPath -relativePath $relativePath) {
        $excludedFiles++
        return
    }
    
    $destPath = $fullPath.Replace((Get-Location).Path, $tempDir)
    $destDir = Split-Path $destPath -Parent
    
    if (-not (Test-Path $destDir)) {
        New-Item -ItemType Directory -Path $destDir -Force | Out-Null
    }
    
    Copy-Item $fullPath -Destination $destPath -Force
    $copiedFiles++
}

# Copiar directorios vacíos importantes que podrían no tener archivos
$importantDirs = @("backend/data/images")
foreach ($dir in $importantDirs) {
    if (Test-Path $dir) {
        $destDirPath = Join-Path $tempDir $dir
        if (-not (Test-Path $destDirPath)) {
            New-Item -ItemType Directory -Path $destDirPath -Force | Out-Null
        }
    }
}

Write-Host ""
Write-Info "  Archivos procesados: $totalFiles"
Write-Info "  Archivos copiados: $copiedFiles"
Write-Info "  Archivos excluidos: $excludedFiles"
Write-Host ""

# Crear ZIP
Write-Info "Comprimiendo archivos en ZIP..."
Compress-Archive -Path "$tempDir\*" -DestinationPath $NombreZip -CompressionLevel Optimal -Force

# Verificar que el ZIP se creó correctamente
if (-not (Test-Path $NombreZip)) {
    Write-Error "Error: No se pudo crear el archivo ZIP"
    Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue
    exit 1
}

# Obtener tamaño del ZIP
$zipSize = (Get-Item $NombreZip).Length
$zipSizeMB = [math]::Round($zipSize / 1MB, 2)
$zipSizeKB = [math]::Round($zipSize / 1KB, 2)

# Limpiar carpeta temporal
Write-Info "Limpiando archivos temporales..."
Remove-Item $tempDir -Recurse -Force

Write-Host ""
Write-Success "========================================="
Write-Success "  ZIP creado exitosamente!"
Write-Success "========================================="
Write-Host ""
Write-Info "  Archivo: $NombreZip"
Write-Info "  Tamaño: $zipSizeMB MB ($zipSizeKB KB)"
Write-Info "  Ubicación: $(Get-Location)\$NombreZip"
Write-Host ""
Write-Info "El ZIP está listo para distribuir."
Write-Info "Incluye todo lo necesario para instalar el proyecto desde cero."
Write-Host ""

