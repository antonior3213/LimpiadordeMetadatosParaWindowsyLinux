from pathlib import Path
from takeout_sidecars import find_takeout_sidecars


def main() -> None:
    raw_folder = input("Ruta de la carpeta de Google Takeout: ").strip().strip('"')
    folder = Path(raw_folder).expanduser()
    if not folder.is_dir():
        print("Esa carpeta no existe o no es una carpeta.")
        return

    recursive = input("¿Incluir también subcarpetas? (s/N): ").strip().lower() == "s"
    sidecars = find_takeout_sidecars(folder, recursive)
    if not sidecars:
        print("No encontré JSON de metadatos asociados a fotos o vídeos.")
        return

    print(f"\nEncontré {len(sidecars)} archivo(s) .json asociados a fotos o vídeos:")
    for path in sidecars:
        print(f"  {path}")
    print("\nSolo se eliminarán esos archivos .json. Las fotos no se abrirán ni modificarán.")
    if input("Escribe ELIMINAR para continuar: ").strip() != "ELIMINAR":
        print("Cancelado. No se eliminó nada.")
        return

    deleted = 0
    for path in sidecars:
        try:
            path.unlink()
            deleted += 1
        except OSError as error:
            print(f"No se pudo eliminar {path}: {error}")
    print(f"Terminado: {deleted} archivo(s) .json eliminado(s). Las fotos siguen intactas.")


if __name__ == "__main__":
    main()


