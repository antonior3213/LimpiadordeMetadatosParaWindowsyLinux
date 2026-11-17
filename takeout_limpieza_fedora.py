from pathlib import Path
from tkinter import Tk, StringVar, BooleanVar, filedialog, messagebox, ttk
import tkinter as tk

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except ImportError as exc:
    raise SystemExit(
        "Falta tkinterdnd2. Instálalo con: python -m pip install tkinterdnd2\n"
        "La aplicación no usa internet al ejecutarse."
    ) from exc

PHOTO_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".heic", ".heif",
    ".tif", ".tiff", ".bmp", ".dng", ".cr2", ".cr3", ".nef",
    ".arw", ".orf", ".rw2", ".raf", ".pef", ".srw",
}
BG = "#f4f7fb"
INK = "#172b4d"
MUTED = "#63738a"
ACCENT = "#2463eb"


def find_sidecars(folder: Path, recursive: bool) -> list[Path]:
    candidates = folder.rglob("*.json") if recursive else folder.glob("*.json")
    found = []
    for sidecar in candidates:
        photo = sidecar.with_suffix("")
        if photo.suffix.lower() in PHOTO_EXTENSIONS and photo.is_file():
            found.append(sidecar)
    return sorted(found, key=lambda p: str(p).casefold())


class App(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("Takeout · Limpieza de metadatos")
        self.geometry("780x650")
        self.minsize(650, 520)
        self.configure(bg=BG)
        self.folder = None
        self.matches = []
        self.path_var = StringVar()
        self.recursive_var = BooleanVar(value=True)
        self.status_var = StringVar(value="Arrastra una carpeta aquí o selecciónala para empezar.")
        self._style()
        self._build()

    def _style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background=BG)
        style.configure("TLabel", background=BG, foreground=INK, font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 22, "bold"), foreground=INK)
        style.configure("Sub.TLabel", font=("Segoe UI", 10), foreground=MUTED)
        style.configure("Card.TFrame", background="white")
        style.configure("Treeview", rowheight=29, font=("Segoe UI", 9), background="white", fieldbackground="white")
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"), padding=(16, 10), background=ACCENT, foreground="white")
        style.map("Accent.TButton", background=[("active", "#174fc7")])
        style.configure("TButton", font=("Segoe UI", 10), padding=(12, 8))
        style.configure("TCheckbutton", background=BG, foreground=INK, font=("Segoe UI", 10))

    def _build(self):
        outer = ttk.Frame(self, padding=(28, 24))
        outer.pack(fill="both", expand=True)
        ttk.Label(outer, text="Limpieza de Google Takeout", style="Title.TLabel").pack(anchor="w")
        ttk.Label(outer, text="Quita los .json de metadatos y conserva tus fotos intactas.", style="Sub.TLabel").pack(anchor="w", pady=(4, 18))

        drop = tk.Frame(outer, bg="white", highlightbackground="#cbd7e8", highlightthickness=1, padx=18, pady=16)
        drop.pack(fill="x")
        tk.Label(drop, text="Suelta aquí la carpeta de fotos", bg="white", fg=INK, font=("Segoe UI", 12, "bold")).pack()
        tk.Label(drop, text="o selecciónala desde el explorador", bg="white", fg=MUTED, font=("Segoe UI", 9)).pack(pady=(3, 10))
        self.path_entry = ttk.Entry(drop, textvariable=self.path_var, state="readonly")
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        ttk.Button(drop, text="Elegir carpeta…", command=self.choose_folder).pack(side="right")
        drop.drop_target_register(DND_FILES)
        drop.dnd_bind("<<Drop>>", self.on_drop)

        opts = ttk.Frame(outer)
        opts.pack(fill="x", pady=(12, 12))
        ttk.Checkbutton(opts, text="Incluir subcarpetas", variable=self.recursive_var, command=self.scan).pack(side="left")
        ttk.Button(opts, text="Buscar archivos", command=self.scan).pack(side="right")

        card = ttk.Frame(outer, style="Card.TFrame", padding=12)
        card.pack(fill="both", expand=True)
        top = ttk.Frame(card, style="Card.TFrame")
        top.pack(fill="x", pady=(0, 8))
        ttk.Label(top, text="Archivos encontrados", style="TLabel").pack(side="left")
        self.count_label = ttk.Label(top, text="0 archivos", style="Sub.TLabel")
        self.count_label.pack(side="right")
        self.tree = ttk.Treeview(card, columns=("photo",), show="headings")
        self.tree.heading("photo", text="Archivo de metadatos asociado a una foto")
        self.tree.column("photo", anchor="w", width=650)
        scroll = ttk.Scrollbar(card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        bottom = ttk.Frame(outer)
        bottom.pack(fill="x", pady=(14, 0))
        ttk.Label(bottom, textvariable=self.status_var, style="Sub.TLabel").pack(side="left", fill="x", expand=True)
        self.delete_button = ttk.Button(bottom, text="Eliminar solo los .json", style="Accent.TButton", command=self.delete)
        self.delete_button.pack(side="right")
        self.delete_button.state(["disabled"])
        tk.Label(outer, text="Las fotos nunca se abren, cambian ni eliminan. No se realiza ninguna conexión a internet.", bg=BG, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", pady=(13, 0))

    def choose_folder(self):
        selected = filedialog.askdirectory(title="Elige la carpeta de Google Takeout")
        if selected:
            self.set_folder(Path(selected))

    def on_drop(self, event):
        try:
            items = self.tk.splitlist(event.data)
            if items:
                path = Path(items[0])
                if path.is_dir():
                    self.set_folder(path)
                else:
                    messagebox.showinfo("Selecciona una carpeta", "Arrastra una carpeta, no un archivo individual.")
        except (OSError, tk.TclError):
            messagebox.showerror("No se pudo leer", "No pude reconocer la carpeta arrastrada.")

    def set_folder(self, folder):
        self.folder = folder
        self.path_var.set(str(folder))
        self.scan()

    def scan(self):
        if not self.folder or not self.folder.is_dir():
            return
        try:
            self.matches = find_sidecars(self.folder, self.recursive_var.get())
        except OSError as error:
            messagebox.showerror("Error al buscar", str(error))
            return
        self.tree.delete(*self.tree.get_children())
        for path in self.matches:
            self.tree.insert("", "end", values=(str(path),))
        count = len(self.matches)
        self.count_label.configure(text=f"{count} archivo" + ("s" if count != 1 else ""))
        if count:
            self.status_var.set("Revisa la lista. Solo se eliminarán estos archivos .json.")
            self.delete_button.state(["!disabled"])
        else:
            self.status_var.set("No se encontraron .json asociados a fotos en esta carpeta.")
            self.delete_button.state(["disabled"])

    def delete(self):
        if not self.matches:
            return
        ok = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Eliminar los {len(self.matches)} archivos .json de la lista?\n\n"
            "Las fotos permanecerán intactas. Esta acción no se puede deshacer.",
            icon="warning",
        )
        if not ok:
            return
        deleted, errors = 0, []
        for path in self.matches:
            try:
                path.unlink()
                deleted += 1
            except OSError as error:
                errors.append(f"{path}: {error}")
        self.scan()
        if errors:
            messagebox.showwarning("Proceso terminado", f"Eliminados: {deleted}\nNo se pudieron eliminar {len(errors)} archivos.\n\n" + "\n".join(errors[:8]))
        else:
            messagebox.showinfo("Proceso terminado", f"Se eliminaron {deleted} archivos .json.\nTus fotos siguen intactas.")


if __name__ == "__main__":
    App().mainloop()
