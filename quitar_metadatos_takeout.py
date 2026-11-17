from pathlib import Path

# Google Takeout photo sidecars, such as IMG_123.jpg.json.
PHOTO_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".heic", ".heif",
    ".tif", ".tiff", ".bmp", ".dng", ".cr2", ".cr3", ".nef",
    ".arw", ".orf", ".rw2", ".raf", ".pef", ".srw",
}


def find_takeout_sidecars(folder: Path, recursive: bool) -> list[Path]:
    paths = folder.rglob("*.json") if recursive else folder.glob("*.json")
    matches = []
    for sidecar in paths:
        # Only match the Takeout pattern: photo filename + its extension + .json.
        photo = sidecar.with_suffix("")
        if photo.suffix.lower() in PHOTO_EXTENSIONS and photo.is_file():
            matches.append(sidecar)
    return sorted(matches)


def main() -> None:
    raw_folder = input("Ruta de la carpeta de Google Takeout: ").strip().strip('"')
    folder = Path(raw_folder).expanduser()
    if not folder.is_dir():
        print("Esa carpeta no existe o no es una carpeta.")
        return

    recursive = input("¿Incluir también subcarpetas? (s/N): ").strip().lower() == "s"
    sidecars = find_takeout_sidecars(folder, recursive)
    if not sidecars:
        print("No encontré archivos .json de metadatos asociados a fotos.")
        return

    print(f"\nEncontré {len(sidecars)} archivo(s) .json asociados a fotos:")
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
