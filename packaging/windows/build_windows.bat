@echo off
setlocal
for %%I in ("%~dp0..\..") do set "ROOT=%%~fI"
cd /d "%ROOT%"

if not exist ".venv\Scripts\python.exe" py -3 -m venv .venv
if errorlevel 1 goto :error

.venv\Scripts\python.exe -m pip install --upgrade pip
if errorlevel 1 goto :error
.venv\Scripts\python.exe -m pip install -r requirements_gui.txt pyinstaller
if errorlevel 1 goto :error

.venv\Scripts\pyinstaller.exe --noconfirm --clean --onefile --windowed --name TakeoutLimpieza --collect-all tkinterdnd2 takeout_limpieza_windows.py
if errorlevel 1 goto :error

echo.
echo Listo: dist\TakeoutLimpieza.exe
pause
exit /b 0

:error
echo.
echo No se pudo compilar. Revisa que Python 3 este instalado y vuelve a intentarlo.
pause
exit /b 1
