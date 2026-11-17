param(
    [Parameter(Mandatory = $true)]
    [string]$Root
)

$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.IO.Compression.FileSystem
Add-Type -AssemblyName System.IO.Compression

$outputZip = Join-Path $Root "Instalador_Windows_Takeout.zip"
$files = @(
    @{ Path = Join-Path $Root "dist\TakeoutLimpieza.exe"; Name = "TakeoutLimpieza.exe" },
    @{ Path = Join-Path $Root "packaging\windows\Instalar.bat"; Name = "Instalar.bat" },
    @{ Path = Join-Path $Root "packaging\windows\Desinstalar.bat"; Name = "Desinstalar.bat" },
    @{ Path = Join-Path $Root "packaging\windows\CrearAccesos.vbs"; Name = "CrearAccesos.vbs" },
    @{ Path = Join-Path $Root "docs\LEEME_instalacion.txt"; Name = "LEEME.txt" }
)

foreach ($file in $files) {
    if (-not (Test-Path -LiteralPath $file.Path -PathType Leaf)) {
        throw "Falta el archivo requerido: $($file.Path)"
    }
}

if (Test-Path -LiteralPath $outputZip) {
    Remove-Item -LiteralPath $outputZip -Force
}

$archive = [IO.Compression.ZipFile]::Open(
    $outputZip,
    [IO.Compression.ZipArchiveMode]::Create
)
try {
    foreach ($file in $files) {
        [IO.Compression.ZipFileExtensions]::CreateEntryFromFile(
            $archive,
            $file.Path,
            $file.Name,
            [IO.Compression.CompressionLevel]::Optimal
        ) | Out-Null
    }
}
finally {
    $archive.Dispose()
}

Write-Output "Paquete creado: $outputZip"
