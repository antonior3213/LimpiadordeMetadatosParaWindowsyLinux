@echo off
setlocal
for %%I in ("%~dp0..\..") do set "ROOT=%%~fI"
cd /d "%ROOT%"
if not exist "dist\TakeoutLimpieza.exe" (
  echo No se encuentra dist\TakeoutLimpieza.exe. Compila primero la aplicacion.
  pause
  exit /b 1
)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0build_installer.ps1" -Root "%ROOT%"
if errorlevel 1 (
  echo No se pudo crear el ZIP.
  pause
  exit /b 1
)
echo Paquete creado: Instalador_Windows_Takeout.zip
echo Extrae el ZIP y ejecuta Instalar.bat.
pause
