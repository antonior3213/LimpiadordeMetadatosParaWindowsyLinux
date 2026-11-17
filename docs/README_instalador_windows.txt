# Paquete de instalación para Windows

1. Ejecuta `packaging\windows\build_windows.bat` si necesitas regenerar `dist\TakeoutLimpieza.exe`.
2. Ejecuta `packaging\windows\build_installer.bat`. Creará `Instalador_Windows_Takeout.zip` sin necesitar Inno Setup.
3. Extrae el ZIP y ejecuta `Instalar.bat`. La aplicación se instala para tu usuario y crea accesos directos en el escritorio y el menú Inicio.

Para desinstalarla, ejecuta `Desinstalar.bat` desde la carpeta extraída. El programa instalado permanece en `%LOCALAPPDATA%\Programs\TakeoutLimpieza`.
