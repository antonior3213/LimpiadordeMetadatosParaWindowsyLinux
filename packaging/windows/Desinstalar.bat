@echo off
setlocal
set "INSTALL=%LOCALAPPDATA%\Programs\TakeoutLimpieza"
if not exist "%INSTALL%\TakeoutLimpieza.exe" (
  echo No encuentro la aplicacion en su carpeta de instalacion.
  pause
  exit /b 1
)
choice /M "Quieres desinstalar el Limpiador de Google Takeout"
if errorlevel 2 exit /b 0
cscript //nologo "%~dp0CrearAccesos.vbs" "desinstalar" "%INSTALL%\TakeoutLimpieza.exe" "%INSTALL%"
rmdir /s /q "%INSTALL%"
echo Aplicacion desinstalada.
pause
