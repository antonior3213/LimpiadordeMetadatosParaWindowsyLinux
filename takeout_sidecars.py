from pathlib import Path

PHOTO_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".heic", ".heif",
    ".tif", ".tiff", ".bmp", ".dng", ".cr2", ".cr3", ".nef",
    ".arw", ".orf", ".rw2", ".raf", ".pef", ".srw",
}

# Recent Google Photos Takeout exports cap sidecar names at 51 characters,
# preserving the final .json (46-character prefix + .json).
_MAX_SIDECAR_LENGTH = 51
_JSON_SUFFIX = ".json"
_SUPPLEMENTAL_SUFFIX = ".supplemental-metadata"


def _candidate_names(photo_name: str) -> set[str]:
    names = {photo_name + _JSON_SUFFIX}
    supplemental = photo_name + _SUPPLEMENTAL_SUFFIX
    complete = supplemental + _JSON_SUFFIX
    if len(complete) <= _MAX_SIDECAR_LENGTH:
        names.add(complete)
    else:
        names.add(supplemental[:_MAX_SIDECAR_LENGTH - len(_JSON_SUFFIX)] + _JSON_SUFFIX)
    return {name.casefold() for name in names}


def find_takeout_sidecars(folder: Path, recursive: bool) -> list[Path]:
    """Find only JSON sidecars whose expected Takeout name matches a local photo."""
    entries = folder.rglob("*") if recursive else folder.iterdir()
    files = [path for path in entries if path.is_file()]

    photos = [path for path in files if path.suffix.casefold() in PHOTO_EXTENSIONS]
    json_by_folder: dict[Path, dict[str, Path]] = {}
    for path in files:
        if path.suffix.casefold() == _JSON_SUFFIX:
            json_by_folder.setdefault(path.parent, {})[path.name.casefold()] = path

    matches = set()
    for photo in photos:
        siblings = json_by_folder.get(photo.parent, {})
        for name in _candidate_names(photo.name):
            sidecar = siblings.get(name)
            if sidecar is not None:
                matches.add(sidecar)
    return sorted(matches, key=lambda path: str(path).casefold())
