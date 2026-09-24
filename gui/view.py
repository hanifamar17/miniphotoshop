import tkinter as tk
from tkinter import messagebox, ttk


class ViewMixin:
    def __init__(self, root):
        self.root = root
        self.root.title("MiniPhotoshop")
        self.root.geometry("1000x650")
        self.root.minsize(800, 500)

        self.current_image = None
        self.original_image = None
        self.current_filename = None
        self.tk_image = None
        self.undo_stack = []
        self.redo_stack = []
        self.zoom_level = 1.0

        self._setup_style()
        self.root.configure(bg=self.bg)
        self._build_menu()
        self._build_layout()

        self.root.bind("<Control-z>", lambda e: self.undo())
        self.root.bind("<Control-o>", lambda e: self.open_file())
        self.root.bind("<Control-s>", lambda e: self.save_file())
        self.root.bind("<Control-plus>", lambda e: self.zoom_in())
        self.root.bind("<Control-minus>", lambda e: self.zoom_out())
        self.root.bind("<Control-0>", lambda e: self.zoom_fit())

    def _setup_style(self):
        self.bg = "#1e1e1e"
        self.bg_panel = "#252526"
        self.bg_dark = "#181818"
        self.fg = "#d4d4d4"
        self.fg_dim = "#9a9a9a"
        self.accent = "#3c3f41"
        self.accent_hover = "#4a4d50"
        self.border = "#3a3a3a"

        self.menu_kwargs = dict(
            tearoff=0, bg=self.bg_panel, fg=self.fg,
            activebackground=self.accent_hover, activeforeground=self.fg,
            bd=0, activeborderwidth=0, borderwidth=0, relief="flat",
            font=("Segoe UI", 10, "normal")
        )

        style = ttk.Style(self.root)
        style.theme_use("clam")

        style.configure(".", background=self.bg, foreground=self.fg,
                         font=("Segoe UI", 10), borderwidth=0)
        style.configure("TFrame", background=self.bg)
        style.configure("Toolbar.TFrame", background=self.bg_panel)
        style.configure("Canvas.TFrame", background=self.bg_dark)
        style.configure("TPanedwindow", background=self.bg)

        style.configure("TButton", background=self.accent, foreground=self.fg,
                         padding=(14, 8), relief="flat", borderwidth=0)
        style.map("TButton",
                   background=[("active", self.accent_hover), ("pressed", self.bg_dark)],
                   foreground=[("disabled", self.fg_dim)])

        style.configure("Icon.TButton", padding=(10, 6), font=("Segoe UI", 9))

        style.configure("TSeparator", background=self.border)
        style.configure("TLabelframe", background=self.bg, foreground=self.fg,
                         font=("Segoe UI", 10, "bold"), bordercolor=self.border, relief="flat")
        style.configure("TLabelframe.Label", background=self.bg, foreground=self.fg)
        style.configure("Status.TLabel", background=self.bg_dark, foreground=self.fg_dim,
                         font=("Segoe UI", 9), padding=(8, 4))

    def _build_menu(self):
        menubar = tk.Menu(self.root, **self.menu_kwargs)

        # File
        menu_file = tk.Menu(menubar, **self.menu_kwargs)
        menu_file.add_command(label="Open...", command=self.open_file, accelerator="Ctrl+O")
        menu_file.add_command(label="Save...", command=self.save_file, accelerator="Ctrl+S")
        menu_file.add_separator()
        menu_file.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=menu_file)

        # Edit
        menu_edit = tk.Menu(menubar, **self.menu_kwargs)
        menu_edit.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        menu_edit.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y", state=tk.DISABLED)
        menu_edit.add_separator()
        menu_edit.add_command(label="Reset to Original", command=self.reset_to_original)
        menubar.add_cascade(label="Edit", menu=menu_edit)

        # Image (dulu "Olah Citra")
        menu_image = tk.Menu(menubar, **self.menu_kwargs)
        menu_image.add_command(label="Negative", command=self.apply_negative)
        menu_image.add_command(label="Grayscale", command=self.apply_grayscale)
        menu_image.add_separator()
        menu_image.add_command(label="Brightness...", command=self.open_brightening_dialog)
        menubar.add_cascade(label="Image", menu=menu_image)

        # View (dulu "Tampilan")
        menu_view = tk.Menu(menubar, **self.menu_kwargs)
        menu_view.add_command(label="Zoom In", command=self.zoom_in, accelerator="Ctrl++")
        menu_view.add_command(label="Zoom Out", command=self.zoom_out, accelerator="Ctrl+-")
        menu_view.add_command(label="Fit to Screen", command=self.zoom_fit, accelerator="Ctrl+0")
        menubar.add_cascade(label="View", menu=menu_view)

        # Help
        menu_help = tk.Menu(menubar, **self.menu_kwargs)
        menu_help.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=menu_help)

        self.root.config(menu=menubar)

    def _build_layout(self):
        # Toolbar minimal — cuma aksi paling sering
        toolbar = ttk.Frame(self.root, style="Toolbar.TFrame")
        toolbar.pack(fill=tk.X, side=tk.TOP)

        inner = ttk.Frame(toolbar, style="Toolbar.TFrame")
        inner.pack(fill=tk.X, padx=8, pady=6)

        ttk.Button(inner, text="Buka", style="Icon.TButton", command=self.open_file).pack(side="left", padx=(0, 4))
        ttk.Button(inner, text="Simpan", style="Icon.TButton", command=self.save_file).pack(side="left", padx=4)
        ttk.Separator(inner, orient="vertical").pack(side="left", fill="y", padx=10)
        ttk.Button(inner, text="Undo", style="Icon.TButton", command=self.undo).pack(side="left", padx=4)
        ttk.Button(inner, text="Reset", style="Icon.TButton", command=self.reset_to_original).pack(side="left", padx=4)

        # Body
        self.paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True)

        self.left_frame = ttk.Frame(self.paned, style="Canvas.TFrame")
        self.paned.add(self.left_frame, weight=3)

        self.canvas = tk.Canvas(self.left_frame, bg=self.bg_dark, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        self.canvas.bind("<Control-MouseWheel>", self._on_zoom_scroll)

        self.info_frame = ttk.LabelFrame(self.paned, text=" Informasi Citra ", padding=10)
        self.paned.add(self.info_frame, weight=1)

        self.info_text = tk.Text(
            self.info_frame, width=30, height=20, font=("Consolas", 9),
            relief=tk.FLAT, bg=self.bg_dark, fg=self.fg,
            insertbackground=self.fg, padx=10, pady=10, wrap=tk.WORD
        )
        self.info_text.pack(fill=tk.BOTH, expand=True)
        self.info_text.insert(tk.END, "Belum ada citra\nyang dibuka.")
        self.info_text.config(state=tk.DISABLED)

        status_bar = ttk.Frame(self.root, style="Toolbar.TFrame")
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        self.status_var = tk.StringVar(value="Siap")
        ttk.Label(status_bar, textvariable=self.status_var, style="Status.TLabel",
                  anchor="w").pack(side="left", fill=tk.X, expand=True)

        zoom_box = ttk.Frame(status_bar, style="Toolbar.TFrame")
        zoom_box.pack(side="right", padx=6, pady=2)

        ttk.Button(zoom_box, text="−", style="Icon.TButton", width=3,
                   command=self.zoom_out).pack(side="left", padx=2)
        self.zoom_label_var = tk.StringVar(value="100%")
        ttk.Label(zoom_box, textvariable=self.zoom_label_var, style="Status.TLabel",
                  width=6, anchor="center").pack(side="left")
        ttk.Button(zoom_box, text="+", style="Icon.TButton", width=3,
                   command=self.zoom_in).pack(side="left", padx=2)
        ttk.Button(zoom_box, text="Fit", style="Icon.TButton",
                   command=self.zoom_fit).pack(side="left", padx=(8, 0))

    # ---------- ZOOM ----------
    def _on_zoom_scroll(self, event):
        if self.current_image is None:
            return
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()

    def zoom_in(self):
        if self.current_image is None:
            return
        self.zoom_level = min(self.zoom_level * 1.25, 8.0)
        self._refresh_zoom()

    def zoom_out(self):
        if self.current_image is None:
            return
        self.zoom_level = max(self.zoom_level / 1.25, 0.1)
        self._refresh_zoom()

    def zoom_fit(self):
        if self.current_image is None:
            return

        self.canvas.update_idletasks()
        cw = max(self.canvas.winfo_width(), 1)
        ch = max(self.canvas.winfo_height(), 1)
        img_w = self.current_image.width
        img_h = self.current_image.height
        self.zoom_level = min(cw / img_w, ch / img_h)
        self._refresh_zoom()

    def _refresh_zoom(self):
        self.zoom_label_var.set(f"{int(self.zoom_level * 100)}%")
        self.display_image(self.current_image)

    def show_about(self):
        messagebox.showinfo("Tentang", "MiniPhotoshop\nEngine C++ + GUI Python")