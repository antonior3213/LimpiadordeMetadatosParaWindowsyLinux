# Google Takeout Metadata Cleaner

Small offline desktop tool for removing Google Takeout photo metadata sidecar files (`photo.jpg.json`) while leaving the photos untouched.

## Features

- Drag and drop a folder, or browse to it.
- Optionally scan subfolders.
- Preview matching sidecar files before deletion.
- Ask for confirmation before removing JSON files.
- Does not open, edit, or delete photos and does not make network requests.

## Run in PyCharm

Open this folder as a project in PyCharm. Install `tkinterdnd2` from `requirements_gui.txt` in the project interpreter, then run:

- Windows: `takeout_limpieza_windows.py`
- Fedora: `takeout_limpieza_fedora.py`

On Fedora, Tkinter may need to be installed with `sudo dnf install python3-tkinter`.

The initial dependency installation may require internet; the application itself runs offline.
