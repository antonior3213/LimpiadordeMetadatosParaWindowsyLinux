@echo off
setlocal
cd /d "%~dp0"

if not exist "dist\TakeoutLimpieza.exe" (
  echo No se encuentra dist\TakeoutLimpieza.exe.
  echo Primero compila la aplicacion con build_windows.bat.
  pause
  exit /b 1
)

set "ISCC="
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not defined ISCC if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not defined ISCC (
  echo No encuentro Inno Setup 6.
  echo Instala Inno Setup 6 desde https://jrsoftware.org/isinfo.php y vuelve a ejecutar este archivo.
  pause
  exit /b 1
)

"%ISCC%" "installer\takeout_limpieza.iss"
if errorlevel 1 exit /b 1
echo.
echo Instalador creado en installer\Output\Instalador_TakeoutLimpieza_Windows.exe
pause
