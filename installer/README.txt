INSTALADOR DE WINDOWS

Este proyecto puede distribuirse mediante un instalador que copia el programa a la carpeta de aplicaciones del usuario, crea un acceso en el menú Inicio y ofrece un acceso directo en el escritorio. Después de instalarlo, se abre desde esos accesos, igual que las demás aplicaciones. El programa instalado sigue conteniendo el ejecutable necesario para funcionar; el instalador evita que tengas que abrirlo desde la carpeta dist.

Para crear el instalador:
1. Genera primero dist\TakeoutLimpieza.exe con build_windows.bat.
2. Instala Inno Setup 6 desde su página oficial (solo hace falta para crear el instalador).
3. Ejecuta build_installer.bat.
4. El instalador aparecerá en installer\Output\Instalador_TakeoutLimpieza_Windows.exe.

Al ejecutarlo, elige si quieres un acceso directo en el escritorio. También quedará disponible en el menú Inicio y en la lista de aplicaciones instaladas, desde donde se puede desinstalar.
