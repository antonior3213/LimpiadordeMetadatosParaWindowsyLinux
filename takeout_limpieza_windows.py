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

BG_TOP = "#edf3ff"
BG_BOTTOM = "#f5f7fb"
INK = "#17233b"
MUTED = "#718099"
BLUE = "#147df5"
BLUE_DARK = "#0969da"
PALE_BLUE = "#f3f7ff"
GLASS = "#fbfcff"
WHITE = "#ffffff"
BORDER = "#e1e8f3"
RED = "#ed5365"


def _mix_color(first: str, second: str, amount: float) -> str:
    a = tuple(int(first[i:i + 2], 16) for i in (1, 3, 5))
    b = tuple(int(second[i:i + 2], 16) for i in (1, 3, 5))
    rgb = tuple(round(x + (y - x) * amount) for x, y in zip(a, b))
    return "#%02x%02x%02x" % rgb


class PillButton(tk.Canvas):
    """Small rounded, glossy button drawn with standard Tk Canvas primitives."""

    def __init__(self, master, text, command, width=150, height=44, kind="glass"):
        super().__init__(master, width=width, height=height, bg=master.cget("bg"),
                         highlightthickness=0, bd=0, cursor="hand2")
        self.label = text
        self.command = command
        self.kind = kind
        self.enabled = True
        self.hovered = False
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self._draw()

    def _colors(self):
        if not self.enabled:
            return "#dce2ec", "#8793a5", "#dce2ec"
        if self.kind == "danger":
            fill = "#e94f63" if self.hovered else RED
            return fill, WHITE, "#ff8a98"
        if self.kind == "primary":
            fill = BLUE_DARK if self.hovered else BLUE
            return fill, WHITE, "#82baff"
        fill = "#e9f1ff" if self.hovered else WHITE
        return fill, BLUE_DARK if self.hovered else INK, "#ffffff"

    def _draw(self):
        self.delete("all")
        width = int(self.cget("width"))
        height = int(self.cget("height"))
        fill, text_color, shine = self._colors()
        radius = height / 2
        points = [radius, 1, width-radius, 1, width-1, height/2,
                  width-radius, height-1, radius, height-1, 1, height/2]
        self.create_polygon(points, smooth=True, splinesteps=32, fill=fill, outline=fill)
        self.create_line(radius * .72, 3, width - radius * .72, 3, fill=shine, width=1)
        self.create_text(width/2, height/2, text=self.label, fill=text_color,
                         font=self.master.winfo_toplevel().ui_font(10, True))

    def _on_enter(self, _event):
        self.hovered = True
        self._draw()

    def _on_leave(self, _event):
        self.hovered = False
        self._draw()

    def _on_click(self, _event):
        if self.enabled:
            self.command()

    def set_enabled(self, enabled: bool):
        self.enabled = enabled
        self.configure(cursor="hand2" if enabled else "arrow")
        self._draw()


class App(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("Takeout · Limpieza de metadatos")
        self.geometry("1020x790")
        self.minsize(760, 690)
        self.configure(bg=BG_BOTTOM)
        self.font_family = self.tk.call("font", "actual", "TkDefaultFont", "-family")
        self.folder = None
        self.matches = []
        self.folder_title_var = StringVar(value="Aún no has elegido una carpeta")
        self.folder_path_var = StringVar(value="Arrastra una carpeta de Google Takeout aquí o selecciónala abajo.")
        self.recursive_var = BooleanVar(value=True)
        self.status_var = StringVar(value="Selecciona una carpeta para ver los archivos encontrados.")
        self._style()
        self._build()

    def ui_font(self, size=10, bold=False):
        return (self.font_family, size, "bold") if bold else (self.font_family, size)

    def _style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Root.TFrame", background=BG_BOTTOM)
        style.configure("Glass.TFrame", background=GLASS)
        style.configure("TLabel", background=BG_BOTTOM, foreground=INK, font=self.ui_font(10))
        style.configure("Glass.TLabel", background=GLASS, foreground=INK, font=self.ui_font(10))
        style.configure("Muted.TLabel", background=GLASS, foreground=MUTED, font=self.ui_font(9))
        style.configure("Treeview", rowheight=38, font=self.ui_font(10), background="#ffffff",
                        fieldbackground="#ffffff", foreground=INK, borderwidth=0, relief="flat")
        style.configure("Treeview.Heading", font=self.ui_font(9, True), background="#f5f8fd",
                        foreground=MUTED, relief="flat", padding=(12, 11))
        style.map("Treeview", background=[("selected", "#e8f1ff")], foreground=[("selected", INK)])
        style.configure("Vertical.TScrollbar", background="#e9eef6", troughcolor=WHITE,
                        bordercolor=WHITE, arrowcolor=MUTED, relief="flat")
        style.configure("TCheckbutton", background=BG_BOTTOM, foreground=INK, font=self.ui_font(10),
                        padding=(2, 5))
        style.map("TCheckbutton", background=[("active", BG_BOTTOM)])

    def _build(self):
        self.wallpaper = tk.Canvas(self, highlightthickness=0, bd=0, bg=BG_BOTTOM)
        self.wallpaper.pack(fill="both", expand=True)
        self.content = ttk.Frame(self.wallpaper, style="Root.TFrame", padding=(34, 28, 34, 24))
        self.content_window = self.wallpaper.create_window((0, 0), window=self.content, anchor="n")
        self.wallpaper.bind("<Configure>", self._paint_wallpaper)

        # Floating glass header
        header = tk.Frame(self.content, bg=GLASS, highlightbackground=WHITE, highlightthickness=2,
                          padx=24, pady=20)
        header.pack(fill="x", pady=(0, 18))
        logo = tk.Canvas(header, width=58, height=58, bg=GLASS, highlightthickness=0)
        logo.pack(side="left", padx=(0, 17))
        logo.create_oval(4, 4, 54, 54, fill="#e5efff", outline="#ffffff", width=2)
        logo.create_oval(14, 14, 44, 44, fill=BLUE, outline="#a9ceff", width=1)
        logo.create_text(29, 29, text="✦", fill=WHITE, font=self.ui_font(15, True))
        title_box = tk.Frame(header, bg=GLASS)
        title_box.pack(side="left", fill="x", expand=True)
        tk.Label(title_box, text="Limpieza de Google Takeout", bg=GLASS, fg=INK,
                 font=self.ui_font(22, True)).pack(anchor="w")
        tk.Label(title_box, text="Un espacio más limpio para tus recuerdos.", bg=GLASS, fg=MUTED,
                 font=self.ui_font(10)).pack(anchor="w", pady=(5, 0))
        self.privacy_pill = tk.Label(header, text="●  TODO EN TU EQUIPO", bg="#eef5ff", fg=BLUE_DARK,
                                     font=self.ui_font(8, True), padx=13, pady=8)
        self.privacy_pill.pack(side="right", anchor="n", padx=(8, 0), pady=(2, 0))

        # Soft blue glass folder drop area
        drop_card = tk.Frame(self.content, bg=PALE_BLUE, highlightbackground=WHITE,
                             highlightthickness=2, padx=20, pady=18)
        drop_card.pack(fill="x")
        drop_top = tk.Frame(drop_card, bg=PALE_BLUE)
        drop_top.pack(fill="x")
        icon = tk.Canvas(drop_top, width=52, height=52, bg=PALE_BLUE, highlightthickness=0)
        icon.pack(side="left", padx=(0, 14))
        icon.create_oval(2, 2, 50, 50, fill="#e1edff", outline="#ffffff", width=2)
        icon.create_text(26, 24, text="↓", fill=BLUE, font=self.ui_font(23, True))
        drop_text = tk.Frame(drop_top, bg=PALE_BLUE)
        drop_text.pack(side="left", fill="x", expand=True)
        tk.Label(drop_text, text="Suelta aquí tu carpeta de fotos", bg=PALE_BLUE, fg=INK,
                 font=self.ui_font(12, True)).pack(anchor="w")
        tk.Label(drop_text, text="o selecciónala desde el explorador de archivos", bg=PALE_BLUE, fg=MUTED,
                 font=self.ui_font(9)).pack(anchor="w", pady=(4, 0))
        self.choose_button = PillButton(drop_top, "Elegir carpeta", self.choose_folder,
                                        width=155, height=44, kind="primary")
        self.choose_button.pack(side="right", padx=(12, 0))

        selected = tk.Frame(drop_card, bg="#edf4ff", highlightbackground="#e0eaff", highlightthickness=1,
                            padx=13, pady=10)
        selected.pack(fill="x", pady=(16, 0), padx=(66, 0))
        self.folder_name_label = tk.Label(selected, textvariable=self.folder_title_var, bg="#edf4ff", fg=INK,
                                          font=self.ui_font(9, True), anchor="w")
        self.folder_name_label.pack(fill="x")
        self.folder_path_label = tk.Label(selected, textvariable=self.folder_path_var, bg="#edf4ff", fg=MUTED,
                                          font=self.ui_font(9), anchor="w", justify="left", wraplength=800)
        self.folder_path_label.pack(fill="x", pady=(3, 0))
        drop_targets = [drop_card, drop_top, icon, drop_text, selected,
                        self.folder_name_label, self.folder_path_label, *drop_text.winfo_children()]
        for widget in drop_targets:
            self._register_drop(widget)

        # Preferences and re-scan action
        options = ttk.Frame(self.content, style="Root.TFrame")
        options.pack(fill="x", pady=(14, 15))
        ttk.Checkbutton(options, text="Incluir también las subcarpetas", variable=self.recursive_var,
                        command=self.scan).pack(side="left")
        self.scan_button = PillButton(options, "↻  Volver a buscar", self.scan,
                                      width=160, height=40, kind="glass")
        self.scan_button.pack(side="right")

        # Preview glass panel
        card = tk.Frame(self.content, bg=GLASS, highlightbackground=WHITE, highlightthickness=2,
                        padx=19, pady=17)
        card.pack(fill="both", expand=True)
        heading = tk.Frame(card, bg=GLASS)
        heading.pack(fill="x", pady=(0, 12))
        heading_left = tk.Frame(heading, bg=GLASS)
        heading_left.pack(side="left", fill="x", expand=True)
        tk.Label(heading_left, text="Vista previa", bg=GLASS, fg=INK,
                 font=self.ui_font(13, True)).pack(anchor="w")
        tk.Label(heading_left, text="Revisa los JSON asociados antes de eliminarlos.", bg=GLASS, fg=MUTED,
                 font=self.ui_font(9)).pack(anchor="w", pady=(4, 0))
        self.count_label = tk.Label(heading, text="0 archivos", bg="#edf2f9", fg=MUTED,
                                    font=self.ui_font(9, True), padx=13, pady=8)
        self.count_label.pack(side="right", anchor="n")

        table_shell = tk.Frame(card, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        table_shell.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(table_shell, columns=("name", "location"), show="headings", selectmode="browse")
        self.tree.heading("name", text="ARCHIVO DE METADATOS")
        self.tree.heading("location", text="UBICACIÓN")
        self.tree.column("name", anchor="w", width=440, minwidth=230)
        self.tree.column("location", anchor="w", width=300, minwidth=150)
        self.tree.tag_configure("odd", background="#f7faff")
        self.tree.tag_configure("even", background=WHITE)
        yscroll = ttk.Scrollbar(table_shell, orient="vertical", command=self.tree.yview)
        xscroll = ttk.Scrollbar(card, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=(1, 0), pady=1)
        yscroll.pack(side="right", fill="y", pady=1)
        xscroll.pack(fill="x", pady=(6, 0))

        # Calm, explicit safety footer and delete action
        footer = ttk.Frame(self.content, style="Root.TFrame")
        footer.pack(fill="x", pady=(16, 0))
        status = tk.Frame(footer, bg=BG_BOTTOM)
        status.pack(side="left", fill="x", expand=True, padx=(0, 12))
        self.status_dot = tk.Label(status, text="●", bg=BG_BOTTOM, fg="#aab5c6", font=self.ui_font(9))
        self.status_dot.pack(side="left", padx=(0, 8), pady=(2, 0))
        ttk.Label(status, textvariable=self.status_var, wraplength=460, justify="left").pack(
            side="left", fill="x", expand=True)
        self.delete_button = PillButton(footer, "Eliminar solo los JSON", self.delete,
                                        width=205, height=48, kind="danger")
        self.delete_button.pack(side="right")
        self.delete_button.set_enabled(False)

        tk.Label(self.content, text="Las fotos nunca se abren ni se modifican  ·  Sin conexión a internet",
                 bg=BG_BOTTOM, fg=MUTED, font=self.ui_font(9)).pack(anchor="w", pady=(13, 0))

    def _paint_wallpaper(self, event):
        width, height = max(event.width, 1), max(event.height, 1)
        self.wallpaper.delete("wallpaper")
        band = 12
        count = max(1, (height + band - 1) // band)
        for index in range(count):
            y1 = index * band
            y2 = min(height, y1 + band + 1)
            color = _mix_color(BG_TOP, BG_BOTTOM, index / max(1, count - 1))
            self.wallpaper.create_rectangle(0, y1, width, y2, fill=color, outline=color, tags="wallpaper")
        self.wallpaper.create_oval(width * .68, -150, width + 130, 210, fill="#e3eaff",
                                   outline="", stipple="gray75", tags="wallpaper")
        self.wallpaper.create_oval(-130, height * .57, 270, height + 170, fill="#e8f2ff",
                                   outline="", stipple="gray75", tags="wallpaper")
        self.wallpaper.create_oval(width * .48, height * .72, width * .84, height * 1.28,
                                   fill="#f0eaff", outline="", stipple="gray75", tags="wallpaper")
        self.wallpaper.coords(self.content_window, width / 2, 0)
        self.wallpaper.itemconfigure(self.content_window, width=max(700, width - 42))
        self.wallpaper.tag_lower("wallpaper")

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
                                   bg="#e7f1ff" if count else "#edf2f9", fg=BLUE if count else MUTED)
        if count:
            self.status_var.set("Revisa la lista. Solo se borrarán JSON asociados a fotos o vídeos.")
            self.status_dot.configure(fg=BLUE)
            self.delete_button.set_enabled(True)
        else:
            self.status_var.set("No se encontraron JSON asociados a fotos o vídeos en esta carpeta.")
            self.status_dot.configure(fg="#aab5c6")
            self.delete_button.set_enabled(False)

    def delete(self):
        if not self.matches:
            return
        ok = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Eliminar los {len(self.matches)} archivos .json de la lista?\n\n"
            "Las fotos y vídeos permanecerán intactos. Esta acción no se puede deshacer.",
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
            messagebox.showinfo("Proceso terminado", f"Se eliminaron {deleted} archivos .json.\nTus fotos y vídeos siguen intactos.")


if __name__ == "__main__":
    App().mainloop()


