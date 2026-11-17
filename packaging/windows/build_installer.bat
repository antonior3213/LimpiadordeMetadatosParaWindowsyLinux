@echo off
setlocal
for %%I in ("%~dp0..\..") do set "ROOT=%%~fI"
cd /d "%ROOT%"
if not exist "dist\TakeoutLimpieza.exe" (
  echo No se encuentra dist\TakeoutLimpieza.exe. Compila primero la aplicacion.
  pause
  exit /b 1
)
if not exist "paquete_instalacion_windows" mkdir "paquete_instalacion_windows"
copy /y "dist\TakeoutLimpieza.exe" "paquete_instalacion_windows\TakeoutLimpieza.exe" >nul
copy /y "packaging\windows\Instalar.bat" "paquete_instalacion_windows\Instalar.bat" >nul
copy /y "packaging\windows\Desinstalar.bat" "paquete_instalacion_windows\Desinstalar.bat" >nul
copy /y "packaging\windows\CrearAccesos.vbs" "paquete_instalacion_windows\CrearAccesos.vbs" >nul
copy /y "docs\LEEME_instalacion.txt" "paquete_instalacion_windows\LEEME.txt" >nul
if exist "Instalador_Windows_Takeout.zip" del /q "Instalador_Windows_Takeout.zip"
powershell.exe -NoProfile -Command "Add-Type -AssemblyName System.IO.Compression.FileSystem; [IO.Compression.ZipFile]::CreateFromDirectory('paquete_instalacion_windows','Instalador_Windows_Takeout.zip')"
if errorlevel 1 (
  echo No se pudo crear el ZIP.
  pause
  exit /b 1
)
echo Paquete creado: Instalador_Windows_Takeout.zip
echo Extrae el ZIP y ejecuta Instalar.bat.
pause
