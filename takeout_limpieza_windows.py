from pathlib import Path
from tkinter import Tk, StringVar, BooleanVar, filedialog, messagebox, ttk
import tkinter as tk
from takeout_sidecars import find_takeout_sidecars as find_sidecars

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except ImportError as exc:
    raise SystemExit(
        "Falta tkinterdnd2. Instálalo con: python -m pip install tkinterdnd2\n"
        "La aplicación no usa internet al ejecutarse."
    ) from exc

BG = "#f3f6fb"
INK = "#182b49"
MUTED = "#70809a"
BLUE = "#3975e8"
PALE_BLUE = "#eef4ff"
BORDER = "#dce5f2"
WHITE = "#ffffff"


class App(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("Takeout · Limpieza de metadatos")
        self.geometry("900x720")
        self.minsize(720, 620)
        self.configure(bg=BG)
        self.folder = None
        self.matches = []
        self.folder_title_var = StringVar(value="Aún no has elegido una carpeta")
        self.folder_path_var = StringVar(value="Arrastra aquí una carpeta de Google Takeout o selecciónala abajo.")
        self.recursive_var = BooleanVar(value=True)
        self.status_var = StringVar(value="Selecciona una carpeta para ver los archivos encontrados.")
        self._style()
        self._build()

    def _style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background=BG)
        style.configure("Card.TFrame", background=WHITE)
        style.configure("TLabel", background=BG, foreground=INK, font=("TkDefaultFont", 10))
        style.configure("Card.TLabel", background=WHITE, foreground=INK, font=("TkDefaultFont", 10))
        style.configure("Muted.TLabel", background=WHITE, foreground=MUTED, font=("TkDefaultFont", 9))
        style.configure("Treeview", rowheight=34, font=("TkDefaultFont", 10), background=WHITE,
                        fieldbackground=WHITE, foreground=INK, borderwidth=0)
        style.configure("Treeview.Heading", font=("TkDefaultFont", 9, "bold"),
                        background="#f5f7fb", foreground=MUTED, relief="flat", padding=(10, 9))
        style.map("Treeview", background=[("selected", "#e8f0ff")], foreground=[("selected", INK)])
        style.configure("TButton", font=("TkDefaultFont", 10), padding=(13, 9),
                        background=WHITE, foreground=INK, bordercolor=BORDER)
        style.map("TButton", background=[("active", "#f1f5fb")])
        style.configure("Primary.TButton", font=("TkDefaultFont", 10, "bold"), padding=(14, 10),
                        background=BLUE, foreground=WHITE, bordercolor=BLUE)
        style.map("Primary.TButton", background=[("active", "#2861ca"), ("disabled", "#aab8d0")],
                  foreground=[("disabled", "#f5f7fb")])
        style.configure("Delete.TButton", font=("TkDefaultFont", 10, "bold"), padding=(16, 11),
                        background="#d84d5b", foreground=WHITE, bordercolor="#d84d5b")
        style.map("Delete.TButton", background=[("active", "#bf3949"), ("disabled", "#c9cfd9")],
                  foreground=[("disabled", "#f7f7f7")])
        style.configure("TCheckbutton", background=BG, foreground=INK, font=("TkDefaultFont", 10))

    def _build(self):
        outer = ttk.Frame(self, padding=(28, 24, 28, 20))
        outer.pack(fill="both", expand=True)

        # Branded header
        header = tk.Frame(outer, bg="#182b49", padx=24, pady=20)
        header.pack(fill="x", pady=(0, 18))
        badge = tk.Label(header, text="T", bg="#294b7c", fg=WHITE,
                         font=("TkDefaultFont", 17, "bold"), width=3, height=1)
        badge.pack(side="left", padx=(0, 16))
        title_box = tk.Frame(header, bg="#182b49")
        title_box.pack(side="left", fill="x", expand=True)
        tk.Label(title_box, text="Limpieza de Google Takeout", bg="#182b49", fg=WHITE,
                 font=("TkDefaultFont", 20, "bold")).pack(anchor="w")
        tk.Label(title_box, text="Quita los JSON de metadatos y conserva tus fotos intactas.",
                 bg="#182b49", fg="#c9d7ed", font=("TkDefaultFont", 10)).pack(anchor="w", pady=(4, 0))

        # Folder drop zone
        drop_card = tk.Frame(outer, bg=PALE_BLUE, highlightbackground="#c8d9f5",
                             highlightthickness=1, padx=18, pady=16)
        drop_card.pack(fill="x")
        top = tk.Frame(drop_card, bg=PALE_BLUE)
        top.pack(fill="x")
        tk.Label(top, text="＋", bg=PALE_BLUE, fg=BLUE, font=("TkDefaultFont", 18, "bold")).pack(side="left", padx=(2, 12))
        text_box = tk.Frame(top, bg=PALE_BLUE)
        text_box.pack(side="left", fill="x", expand=True)
        tk.Label(text_box, text="Arrastra aquí la carpeta de fotos", bg=PALE_BLUE, fg=INK,
                 font=("TkDefaultFont", 11, "bold")).pack(anchor="w")
        tk.Label(text_box, text="o búscala en tu equipo", bg=PALE_BLUE, fg=MUTED,
                 font=("TkDefaultFont", 9)).pack(anchor="w", pady=(3, 0))
        self.choose_button = ttk.Button(top, text="Elegir carpeta…", command=self.choose_folder)
        self.choose_button.pack(side="right", padx=(12, 0))
        tk.Label(drop_card, textvariable=self.folder_title_var, bg=PALE_BLUE, fg=INK,
                 font=("TkDefaultFont", 9, "bold"), anchor="w").pack(fill="x", padx=(44, 0), pady=(12, 2))
        self.folder_path_label = tk.Label(drop_card, textvariable=self.folder_path_var, bg=PALE_BLUE,
                                          fg=MUTED, font=("TkDefaultFont", 9), anchor="w", justify="left",
                                          wraplength=760)
        self.folder_path_label.pack(fill="x", padx=(44, 0))
        for widget in (drop_card, top, badge, title_box, text_box, *top.winfo_children()):
            self._register_drop(widget)

        # Search options
        options = ttk.Frame(outer)
        options.pack(fill="x", pady=(14, 14))
        ttk.Checkbutton(options, text="Incluir subcarpetas", variable=self.recursive_var,
                        command=self.scan).pack(side="left")
        ttk.Button(options, text="↻  Buscar de nuevo", command=self.scan).pack(side="right")

        # Preview card
        card = ttk.Frame(outer, style="Card.TFrame", padding=(16, 14))
        card.pack(fill="both", expand=True)
        heading = ttk.Frame(card, style="Card.TFrame")
        heading.pack(fill="x", pady=(0, 10))
        heading_left = ttk.Frame(heading, style="Card.TFrame")
        heading_left.pack(side="left", fill="x", expand=True)
        ttk.Label(heading_left, text="Vista previa", style="Card.TLabel",
                  font=("TkDefaultFont", 12, "bold")).pack(anchor="w")
        ttk.Label(heading_left, text="Reconoce los nombres antiguos y los nuevos de Google Takeout.",
                  style="Muted.TLabel").pack(anchor="w", pady=(3, 0))
        self.count_label = tk.Label(heading, text="0 archivos", bg="#edf2f8", fg=MUTED,
                                    font=("TkDefaultFont", 9, "bold"), padx=11, pady=6)
        self.count_label.pack(side="right", anchor="n")

        table = ttk.Frame(card, style="Card.TFrame")
        table.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(table, columns=("name", "location"), show="headings", selectmode="browse")
        self.tree.heading("name", text="ARCHIVO DE METADATOS")
        self.tree.heading("location", text="CARPETA")
        self.tree.column("name", anchor="w", width=380, minwidth=220)
        self.tree.column("location", anchor="w", width=300, minwidth=150)
        self.tree.tag_configure("odd", background="#f8faff")
        self.tree.tag_configure("even", background=WHITE)
        yscroll = ttk.Scrollbar(table, orient="vertical", command=self.tree.yview)
        xscroll = ttk.Scrollbar(card, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        yscroll.pack(side="right", fill="y")
        xscroll.pack(fill="x", pady=(5, 0))

        # Safe-action footer
        footer = ttk.Frame(outer)
        footer.pack(fill="x", pady=(15, 0))
        status_box = tk.Frame(footer, bg=BG)
        status_box.pack(side="left", fill="x", expand=True, padx=(0, 14))
        self.status_dot = tk.Label(status_box, text="●", bg=BG, fg="#9aa8bb", font=("TkDefaultFont", 9))
        self.status_dot.pack(side="left", padx=(0, 7), pady=(2, 0))
        ttk.Label(status_box, textvariable=self.status_var, style="TLabel", wraplength=450,
                  justify="left").pack(side="left", fill="x", expand=True)
        self.delete_button = ttk.Button(footer, text="Eliminar solo los .json",
                                        style="Delete.TButton", command=self.delete)
        self.delete_button.pack(side="right")
        self.delete_button.state(["disabled"])

        tk.Label(outer, text="Tus fotos no se abren ni se modifican. Todo el proceso es local y sin internet.",
                 bg=BG, fg=MUTED, font=("TkDefaultFont", 9)).pack(anchor="w", pady=(13, 0))

    def _register_drop(self, widget):
        try:
            widget.drop_target_register(DND_FILES)
            widget.dnd_bind("<<Drop>>", self.on_drop)
        except (AttributeError, tk.TclError):
            pass

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
        self.folder_title_var.set(folder.name or str(folder))
        self.folder_path_var.set(str(folder))
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
        for index, path in enumerate(self.matches):
            try:
                relative = path.relative_to(self.folder)
                parent = "Carpeta principal" if str(relative.parent) == "." else str(relative.parent)
            except ValueError:
                parent = str(path.parent)
            self.tree.insert("", "end", values=(path.name, parent), tags=("even" if index % 2 == 0 else "odd",))
        count = len(self.matches)
        self.count_label.configure(text=f"{count} archivo" + ("s" if count != 1 else ""),
                                   bg="#e9f1ff" if count else "#edf2f8", fg=BLUE if count else MUTED)
        if count:
            self.status_var.set("Revisa la lista. Solo se borrarán estos sidecars JSON asociados a fotos.")
            self.status_dot.configure(fg=BLUE)
            self.delete_button.state(["!disabled"])
        else:
            self.status_var.set("No se encontraron JSON asociados a fotos en esta carpeta.")
            self.status_dot.configure(fg="#9aa8bb")
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



