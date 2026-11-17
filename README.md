# Limpiador de metadatos de Google Takeout

Aplicación gráfica para quitar los archivos de metadatos JSON que Google Takeout guarda junto a las fotos, por ejemplo `IMG_123.jpg.json`. **No abre, modifica ni elimina las fotos.** La aplicación no realiza conexiones a internet.

## Qué hace

- Permite arrastrar una carpeta a la ventana o elegirla con el explorador.
- Puede buscar también dentro de las subcarpetas.
- Solo identifica archivos con forma `foto.ext.json` cuando la foto correspondiente existe en esa carpeta.
- Enseña la lista antes de borrar y pide confirmación.
- Elimina únicamente los `.json` de la lista.

## Ejecutar desde PyCharm

1. Abre esta carpeta como proyecto en PyCharm.
2. Selecciona un intérprete de Python 3.
3. En la terminal de PyCharm, instala la dependencia para arrastrar y soltar:

   ```bash
   python -m pip install -r requirements_gui.txt
   ```

4. Ejecuta `takeout_limpieza_windows.py` en Windows o `takeout_limpieza_fedora.py` en Fedora.
5. Arrastra la carpeta de Takeout a la ventana, o pulsa **Elegir carpeta…**.
6. Revisa la lista y pulsa **Eliminar solo los .json**. Confirma en el diálogo para completar el borrado.

En Fedora puede ser necesario instalar Tkinter primero:

```bash
sudo dnf install python3-tkinter
```

## Crear el ejecutable de Windows

En Windows, con Python 3 instalado, ejecuta `build_windows.bat`. El ejecutable quedará en `dist\TakeoutLimpieza.exe`. La primera compilación instala PyInstaller y `tkinterdnd2` en un entorno virtual del proyecto y requiere conexión para descargar esos paquetes. El programa compilado no usa internet al ejecutarse.

## Crear el paquete RPM de Fedora

El RPM debe construirse en Fedora (o en un entorno Fedora), no en Windows. Consulta `packaging/fedora/README.md` para preparar las dependencias y ejecutar el script de compilación. El paquete instala la aplicación y un acceso al menú de aplicaciones.

## Privacidad y seguridad

El programa no envía archivos ni datos a ningún servicio. La búsqueda se realiza localmente. Antes de confirmar, se puede cancelar sin borrar nada. Una vez confirmada, la eliminación de los `.json` no se puede deshacer desde la aplicación; las fotos permanecen intactas.
