"""Detect Google Takeout JSON sidecars without matching unrelated JSON files."""

from pathlib import Path
import json

PHOTO_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".heic", ".heif",
    ".tif", ".tiff", ".bmp", ".dng", ".cr2", ".cr3", ".nef",
    ".arw", ".orf", ".rw2", ".raf", ".pef", ".srw",
}
VIDEO_EXTENSIONS = {
    ".mp4", ".mov", ".avi", ".mkv", ".3gp", ".m4v", ".mpg", ".mpeg",
    ".wmv", ".mts", ".m2ts", ".webm",
}
MEDIA_EXTENSIONS = PHOTO_EXTENSIONS | VIDEO_EXTENSIONS

# Takeout caps many sidecar names at 51 characters, including ".json".
_MAX_SIDECAR_LENGTH = 51
_JSON_SUFFIX = ".json"
_SUPPLEMENTAL = "supplemental-metadata"


def _limited_json_name(name: str) -> str:
    """Apply Takeout's 51-character limit (46 characters plus .json)."""
    if len(name) + len(_JSON_SUFFIX) > _MAX_SIDECAR_LENGTH:
        return name[:_MAX_SIDECAR_LENGTH - len(_JSON_SUFFIX)] + _JSON_SUFFIX
    return name + _JSON_SUFFIX


def _sidecar_names(media_name: str) -> set[str]:
    """Return known classic, supplemental, truncated and duplicate variants."""
    names: set[str] = set()

    def add_for_media(name: str, duplicate: str = "") -> None:
        # Classic Google Takeout sidecars: photo.jpg.json
        names.add(_limited_json_name(name + duplicate))

        # Newer exports append a supplemental-metadata marker. Some exports
        # cut this marker at any point to keep the JSON filename within 51 chars.
        supplemental = name + "." + _SUPPLEMENTAL + duplicate
        names.add(_limited_json_name(supplemental))
        for length in range(1, len(_SUPPLEMENTAL) + 1):
            names.add(_limited_json_name(name + "." + _SUPPLEMENTAL[:length] + duplicate))

    add_for_media(media_name)

    # Older Takeout versions also truncated the original media name itself.
    names.add(media_name[:_MAX_SIDECAR_LENGTH - len(_JSON_SUFFIX)] + _JSON_SUFFIX)

    # Duplicate media often puts its (N) marker in a different place in the
    # sidecar name: photo.jpg.supplemental-metadata (1).json / photo.jpg (1).json.
    suffix = Path(media_name).suffix
    stem = media_name[:-len(suffix)] if suffix else media_name
    if stem.endswith(")"):
        marker_start = stem.rfind("(")
        if marker_start >= 0 and stem[marker_start + 1:-1].isdigit():
            base_name = stem[:marker_start].rstrip() + suffix
            marker = stem[marker_start:]
            add_for_media(base_name, marker)
            add_for_media(base_name + marker)
            add_for_media(base_name, " " + marker)

    return {name.casefold() for name in names}


def find_takeout_sidecars(folder: Path, recursive: bool) -> list[Path]:
    """Find Takeout JSON sidecars paired with media in the same folder.

    Matching is deliberately based on the media filename and known Takeout
    naming rules. Standalone JSON documents are left untouched.
    """
    entries = folder.rglob("*") if recursive else folder.iterdir()
    files = [path for path in entries if path.is_file()]

    media_files = [path for path in files if path.suffix.casefold() in MEDIA_EXTENSIONS]
    json_by_folder: dict[Path, dict[str, Path]] = {}
    for path in files:
        if path.suffix.casefold() == _JSON_SUFFIX:
            json_by_folder.setdefault(path.parent, {})[path.name.casefold()] = path

    media_by_folder: dict[Path, dict[str, Path]] = {}
    matches: set[Path] = set()
    for media in media_files:
        media_by_folder.setdefault(media.parent, {})[media.name.casefold()] = media
        siblings = json_by_folder.get(media.parent, {})
        for name in _sidecar_names(media.name):
            sidecar = siblings.get(name)
            if sidecar is not None:
                matches.add(sidecar)

    # Some Takeout variants change or shorten the sidecar filename differently.
    # Their JSON still identifies the original media in its `title` field. Use
    # that exact same-folder title as a safe fallback for alternate formats.
    for parent, siblings in json_by_folder.items():
        media_names = media_by_folder.get(parent, {})
        for sidecar in siblings.values():
            if sidecar in matches:
                continue
            try:
                with sidecar.open("r", encoding="utf-8-sig") as stream:
                    payload = json.load(stream)
            except (OSError, UnicodeError, json.JSONDecodeError):
                continue
            if not isinstance(payload, dict):
                continue
            for key in ("title", "fileName", "filename", "originalFilename"):
                title = payload.get(key)
                if isinstance(title, str) and Path(title).name.casefold() in media_names:
                    matches.add(sidecar)
                    break

    return sorted(matches, key=lambda path: str(path).casefold())
