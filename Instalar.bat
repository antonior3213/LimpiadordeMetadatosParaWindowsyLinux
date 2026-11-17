@echo off
setlocal
set "SOURCE=%~dp0TakeoutLimpieza.exe"
set "INSTALL=%LOCALAPPDATA%\Programs\TakeoutLimpieza"

if not exist "%SOURCE%" (
  echo No se encuentra TakeoutLimpieza.exe junto a este instalador.
  pause
  exit /b 1
)
if not exist "%INSTALL%" mkdir "%INSTALL%"
if errorlevel 1 (
  echo No se pudo crear la carpeta de la aplicacion.
  pause
  exit /b 1
)
copy /y "%SOURCE%" "%INSTALL%\TakeoutLimpieza.exe" >nul
if errorlevel 1 (
  echo No se pudo copiar la aplicacion. Cierra el limpiador si esta abierto e intentalo de nuevo.
  pause
  exit /b 1
)
cscript //nologo "%~dp0CrearAccesos.vbs" "instalar" "%INSTALL%\TakeoutLimpieza.exe" "%INSTALL%"
if errorlevel 1 (
  echo La aplicacion se copio, pero no se pudieron crear los accesos directos.
  echo Puedes abrirla desde: %INSTALL%\TakeoutLimpieza.exe
  pause
  exit /b 1
)
echo Instalacion terminada. Busca "Limpiador de Google Takeout" en el escritorio o en el menu Inicio.
pause
