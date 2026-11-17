# Compilar el paquete RPM en Fedora

Este paquete se crea en Fedora porque los ejecutables de PyInstaller son específicos del sistema operativo. Necesitas Python 3, Tkinter, `rpmbuild` y acceso a internet durante la primera compilación para instalar las herramientas Python.

Instala herramientas del sistema:

```bash
sudo dnf install python3 python3-tkinter rpm-build
```

Desde la carpeta del proyecto:

```bash
bash packaging/fedora/build_rpm.sh
```

La compilación crea un entorno virtual local, instala PyInstaller y `tkinterdnd2`, genera una aplicación empaquetada en `dist/TakeoutLimpieza/` y construye el RPM en `packaging/fedora/rpmbuild/RPMS/`.

Para instalar el RPM generado:

```bash
sudo dnf install packaging/fedora/rpmbuild/RPMS/*/takeout-limpieza-*.rpm
```

El programa no necesita conexión de red para ejecutarse.
