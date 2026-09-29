import tkinter as tk
from tkinter import messagebox, ttk
from histogram_view import HistogramPanel


class PowerTransformDialog(tk.Toplevel):
    def __init__(self, parent, theme):
        super().__init__(parent)
        self.title("Power (Gamma) Transformation")
        self.resizable(False, False)
        self.configure(bg=theme["bg_panel"])
        self.result = None

        container = ttk.Frame(self, padding=15)
        container.pack(fill="both", expand=True)

        ttk.Label(container, text="Nilai Gamma (γ):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.gamma_var = tk.DoubleVar(value=1.0)
        self.spinbox = ttk.Spinbox(container, from_=0.1, to=5.0, increment=0.1, textvariable=self.gamma_var, width=8)
        self.spinbox.grid(row=0, column=1, padx=5, pady=5)

        self.slider = ttk.Scale(container, from_=0.1, to=5.0, variable=self.gamma_var, orient='horizontal')
        self.slider.grid(row=1, column=0, columnspan=2, padx=5, pady=10, sticky="we")

        btn_frame = ttk.Frame(container)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=(10, 0))
        ttk.Button(btn_frame, text="OK", command=self.on_ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Batal", command=self.destroy).pack(side=tk.LEFT, padx=5)

        self.transient(parent)
        self.grab_set()
        parent.wait_window(self)

    def on_ok(self):
        try:
            val = float(self.gamma_var.get())
            if val <= 0:
                raise ValueError
            self.result = val
            self.destroy()
        except ValueError:
            messagebox.showerror("Error", "Nilai Gamma harus angka desimal > 0!", parent=self)


class GraySlicingDialog(tk.Toplevel):
    def __init__(self, parent, theme):
        super().__init__(parent)
        self.title("Gray-level Slicing")
        self.resizable(False, False)
        self.configure(bg=theme["bg_panel"])
        self.result = None

        container = ttk.Frame(self, padding=15)
        container.pack(fill="both", expand=True)

        ttk.Label(container, text="Batas A (0–255):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.a_var = tk.IntVar(value=50)
        ttk.Spinbox(container, from_=0, to=255, textvariable=self.a_var, width=8).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(container, text="Batas B (0–255):").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.b_var = tk.IntVar(value=150)
        ttk.Spinbox(container, from_=0, to=255, textvariable=self.b_var, width=8).grid(row=1, column=1, padx=5, pady=5)

        self.preserve_var = tk.BooleanFieldVar(value=False)
        ttk.Checkbutton(container, text="Pertahankan latar (preserve)", variable=self.preserve_var).grid(row=2, column=0, columnspan=2, padx=5, pady=10)

        btn_frame = ttk.Frame(container)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=(5, 0))
        ttk.Button(btn_frame, text="OK", command=self.on_ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Batal", command=self.destroy).pack(side=tk.LEFT, padx=5)

        self.transient(parent)
        self.grab_set()
        parent.wait_window(self)

    def on_ok(self):
        try:
            a, b = self.a_var.get(), self.b_var.get()
            if not (0 <= a <= 255 and 0 <= b <= 255):
                messagebox.showerror("Error", "Nilai A dan B harus di antara 0 - 255!", parent=self)
                return
            if a > b:
                a, b = b, a  # Tukar nilai jika A > B
            self.result = (a, b, self.preserve_var.get())
            self.destroy()
        except tk.TclError:
            messagebox.showerror("Error", "Masukkan nilai integer yang valid!", parent=self)


class BitPlaneDialog(tk.Toplevel):
    def __init__(self, parent, theme):
        super().__init__(parent)
        self.title("Bit-plane Slicing")
        self.resizable(False, False)
        self.configure(bg=theme["bg_panel"])
        self.result = None

        container = ttk.Frame(self, padding=15)
        container.pack(fill="both", expand=True)

        ttk.Label(container, text="Pilih Bit Plane (0–7):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.k_var = tk.IntVar(value=7)
        ttk.Spinbox(container, from_=0, to=7, textvariable=self.k_var, width=8).grid(row=0, column=1, padx=5, pady=5)

        self.binary_var = tk.BooleanFieldVar(value=True)
        ttk.Checkbutton(container, text="Tampilkan biner", variable=self.binary_var).grid(row=1, column=0, columnspan=2, padx=5, pady=10)

        btn_frame = ttk.Frame(container)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=(5, 0))
        ttk.Button(btn_frame, text="OK", command=self.on_ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Batal", command=self.destroy).pack(side=tk.LEFT, padx=5)

        self.transient(parent)
        self.grab_set()
        parent.wait_window(self)

    def on_ok(self):
        try:
            k = self.k_var.get()
            if not (0 <= k <= 7):
                messagebox.showerror("Error", "Nilai Bit Plane (k) harus di antara 0 - 7!", parent=self)
                return
            self.result = (k, self.binary_var.get())
            self.destroy()
        except tk.TclError:
            messagebox.showerror("Error", "Masukkan angka integer 0–7!", parent=self)


class ManualContrastDialog(tk.Toplevel):
    def __init__(self, parent, theme):
        super().__init__(parent)
        self.title("Manual Contrast Stretching")
        self.resizable(False, False)
        self.configure(bg=theme["bg_panel"])
        self.result = None

        container = ttk.Frame(self, padding=15)
        container.pack(fill="both", expand=True)

        ttk.Label(container, text="r1 (0-255):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.r1_var = tk.IntVar(value=50)
        ttk.Spinbox(container, from_=0, to=255, textvariable=self.r1_var, width=8).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(container, text="s1 (0-255):").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.s1_var = tk.IntVar(value=20)
        ttk.Spinbox(container, from_=0, to=255, textvariable=self.s1_var, width=8).grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(container, text="r2 (0-255):").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.r2_var = tk.IntVar(value=150)
        ttk.Spinbox(container, from_=0, to=255, textvariable=self.r2_var, width=8).grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(container, text="s2 (0-255):").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.s2_var = tk.IntVar(value=220)
        ttk.Spinbox(container, from_=0, to=255, textvariable=self.s2_var, width=8).grid(row=1, column=3, padx=5, pady=5)

        btn_frame = ttk.Frame(container)
        btn_frame.grid(row=2, column=0, columnspan=4, pady=(15, 0))
        ttk.Button(btn_frame, text="OK", command=self.on_ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Batal", command=self.destroy).pack(side=tk.LEFT, padx=5)

        self.transient(parent)
        self.grab_set()
        parent.wait_window(self)

    def on_ok(self):
        try:
            r1, s1 = self.r1_var.get(), self.s1_var.get()
            r2, s2 = self.r2_var.get(), self.s2_var.get()

            for val in (r1, s1, r2, s2):
                if not (0 <= val <= 255):
                    messagebox.showerror("Error", "Semua nilai harus di antara 0 - 255!", parent=self)
                    return

            if r1 > r2:
                messagebox.showerror("Error", "Syarat r1 ≤ r2 tidak terpenuhi!", parent=self)
                return

            self.result = (r1, s1, r2, s2)
            self.destroy()
        except tk.TclError:
            messagebox.showerror("Error", "Masukkan nilai integer yang valid!", parent=self)


class AutoContrastDialog(tk.Toplevel):
    def __init__(self, parent, theme):
        super().__init__(parent)
        self.title("Auto Contrast Stretching")
        self.resizable(False, False)
        self.configure(bg=theme["bg_panel"])
        self.result = None

        container = ttk.Frame(self, padding=15)
        container.pack(fill="both", expand=True)

        ttk.Label(container, text="Persen Tergelap (a %):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.a_var = tk.DoubleVar(value=1.0)
        ttk.Spinbox(container, from_=0.0, to=100.0, increment=0.5, textvariable=self.a_var, width=8).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(container, text="Persen Terterang (b %):").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.b_var = tk.DoubleVar(value=99.0)
        ttk.Spinbox(container, from_=0.0, to=100.0, increment=0.5, textvariable=self.b_var, width=8).grid(row=1, column=1, padx=5, pady=5)

        btn_frame = ttk.Frame(container)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=(15, 0))
        ttk.Button(btn_frame, text="OK", command=self.on_ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Batal", command=self.destroy).pack(side=tk.LEFT, padx=5)

        self.transient(parent)
        self.grab_set()
        parent.wait_window(self)

    def on_ok(self):
        try:
            a, b = float(self.a_var.get()), float(self.b_var.get())
            if not (0 <= a < b <= 100):
                messagebox.showerror("Error", "Syarat 0 ≤ a < b ≤ 100 tidak terpenuhi!", parent=self)
                return
            self.result = (a, b)
            self.destroy()
        except tk.TclError:
            messagebox.showerror("Error", "Masukkan nilai desimal yang valid!", parent=self)


# =========================================================================
# CLASS VIEWMIXIN
# =========================================================================

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

        self.root.bind_all("<Control-z>", lambda e: self.undo())
        self.root.bind_all("<Control-Shift-Y>", lambda e: self.redo())
        self.root.bind_all("<Control-Shift-y>", lambda e: self.redo())
        self.root.bind_all("<Control-o>", lambda e: self.open_file())
        self.root.bind_all("<Control-s>", lambda e: self.save_file())
        self.root.bind_all("<Control-equal>", lambda e: self.zoom_in())
        self.root.bind_all("<Control-KP_Add>", lambda e: self.zoom_in())
        self.root.bind_all("<Control-minus>", lambda e: self.zoom_out())
        self.root.bind_all("<Control-KP_Subtract>", lambda e: self.zoom_out())
        self.root.bind_all("<Control-0>", lambda e: self.zoom_fit()) 

        self._setup_style()
        self.root.configure(bg=self.bg)
        self._build_menu()
        self._build_layout()
        self.root.bind("<Button-1>", self._on_root_click, add="+")
        self.root.bind("<Escape>", lambda e: self._close_popup(), add="+")
        self._update_history_ui()
        self._dark_titlebar()
        self.hist_panel.update(None)

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

        style.configure("Bar.TButton", padding=(10, 3))
        style.configure(".", background=self.bg, foreground=self.fg,
                         font=("Segoe UI", 10), borderwidth=0)
        style.configure("Canvas.TFrame", background=self.bg_dark)
        style.configure("Icon.TButton", padding=(10, 6), font=("Segoe UI", 9))

        style.configure("TCombobox", fieldbackground=self.bg_panel, background=self.bg_panel,
               foreground=self.fg, arrowcolor=self.fg, bordercolor=self.border,
               padding=4)
        style.map("TCombobox", fieldbackground=[("readonly", self.bg_panel)],
                  foreground=[("readonly", self.fg)])
        style.configure("TFrame", background=self.bg)
        style.configure("Toolbar.TFrame", background=self.bg_panel)
        style.configure("TPanedwindow", background=self.bg)
        style.configure("TButton", background=self.accent, foreground=self.fg,
                         padding=(14, 8), relief="flat", borderwidth=0)
        style.configure("TLabelframe", background=self.bg, foreground=self.fg,
                         font=("Segoe UI", 10, "bold"), bordercolor=self.border, relief="flat")
        style.configure("TLabelframe.Label", background=self.bg, foreground=self.fg)
        style.configure("TSeparator", background=self.border)

        style.configure("Status.TLabel", background=self.bg_dark, foreground=self.fg_dim,
                         font=("Segoe UI", 9), padding=(8, 4))
        style.configure("Sash", sashthickness=6, gripcount=0,
                background=self.border, bordercolor=self.border,
                lightcolor=self.border, darkcolor=self.border)

        style.map("TButton",
                           background=[("active", self.accent_hover), ("pressed", self.bg_dark)],
                           foreground=[("disabled", self.fg_dim)])

        self.root.option_add("*TCombobox*Listbox.background", self.bg_panel)
        self.root.option_add("*TCombobox*Listbox.foreground", self.fg)
        self.root.option_add("*TCombobox*Listbox.selectBackground", self.accent)
        self.root.option_add("*TCombobox*Listbox.selectForeground", self.fg)
        self.root.option_add("*TCombobox*Listbox.font", ("Segoe UI", 9))

    def _build_menu(self):
        bar = tk.Frame(self.root, bg=self.bg_panel)
        bar.pack(fill=tk.X, side=tk.TOP)
        self._popup = None
        self._popup_owner = None

        def add(label, items):
            lb = tk.Label(bar, text=label, bg=self.bg_panel, fg=self.fg,
                          padx=12, pady=6, font=("Segoe UI", 10))
            lb.pack(side="left")
            lb.bind("<Enter>", lambda e: lb.config(bg=self.accent_hover))
            lb.bind("<Leave>", lambda e: lb.config(bg=self.bg_panel)
                    if self._popup_owner is not lb else None)
            lb.bind("<Button-1>", lambda e: self._toggle_popup(lb, items))

        add("File", [
            dict(label="Open...", command=self.open_file, accelerator="Ctrl+O"),
            dict(label="Save...", command=self.save_file, accelerator="Ctrl+S"),
            None,
            dict(label="Exit", command=self.root.quit),
        ])
        add("Edit", [
            dict(label="Undo", command=self.undo, accelerator="Ctrl+Z",
                 enabled=lambda: bool(self.undo_stack)),
            dict(label="Redo", command=self.redo, accelerator="Ctrl+Shift+Y",
                 enabled=lambda: bool(self.redo_stack)),
            None,
            dict(label="Reset to Original", command=self.reset_to_original),
        ])
        
        # MENU IMAGE BARU (Dilengkapi Contrast Stretching, Log, Power, & Slicing)
        add("Image", [
            dict(label="Negative", command=self.apply_negative),
            dict(label="Grayscale", command=self.apply_grayscale),
            dict(label="Brightness...", command=self.open_brightening_dialog),
            None,
            dict(label="Manual Contrast Stretching...", command=self.open_manual_contrast_dialog),
            dict(label="Auto Contrast Stretching...", command=self.open_auto_contrast_dialog),
            None,
            dict(label="Log Transformation", command=self.apply_log),
            dict(label="Inverse Log Transformation", command=self.apply_inverse_log),
            dict(label="Power (Gamma)...", command=self.open_power_dialog),
            None,
            dict(label="Gray-level Slicing...", command=self.open_gray_slicing_dialog),
            dict(label="Bit-plane Slicing...", command=self.open_bit_plane_dialog),
        ])
        
        add("View", [
            dict(label="Zoom In", command=self.zoom_in, accelerator="Ctrl+(+)"),
            dict(label="Zoom Out", command=self.zoom_out, accelerator="Ctrl+(-)"),
            dict(label="Fit to Screen", command=self.zoom_fit, accelerator="Ctrl+0"),
        ])
        add("Help", [dict(label="About", command=self.show_about)])

        # Undo / Redo rata kanan
        self.btn_redo = ttk.Button(bar, text="Redo", style="Bar.TButton", command=self.redo)
        self.btn_redo.pack(side="right", padx=(0, 8), pady=3)
        self.btn_undo = ttk.Button(bar, text="Undo", style="Bar.TButton", command=self.undo)
        self.btn_undo.pack(side="right", padx=4, pady=3)

    # =========================================================================
    # HANDLER PEMANGGIL DIALOG DARI MENU
    # =========================================================================
    def apply_log(self):
        if hasattr(self, 'process_log'):
            self.process_log()

    def apply_inverse_log(self):
        if hasattr(self, 'process_inverse_log'):
            self.process_inverse_log()

    def open_power_dialog(self):
        if self.current_image is None:
            return
        theme = dict(bg_panel=self.bg_panel)
        dialog = PowerTransformDialog(self.root, theme)
        if dialog.result is not None and hasattr(self, 'process_power'):
            self.process_power(dialog.result)

    def open_gray_slicing_dialog(self):
        if self.current_image is None:
            return
        theme = dict(bg_panel=self.bg_panel)
        dialog = GraySlicingDialog(self.root, theme)
        if dialog.result is not None and hasattr(self, 'process_gray_slicing'):
            a, b, preserve = dialog.result
            self.process_gray_slicing(a, b, preserve)

    def open_bit_plane_dialog(self):
        if self.current_image is None:
            return
        theme = dict(bg_panel=self.bg_panel)
        dialog = BitPlaneDialog(self.root, theme)
        if dialog.result is not None and hasattr(self, 'process_bit_plane'):
            k, binary = dialog.result
            self.process_bit_plane(k, binary)

    def open_manual_contrast_dialog(self):
        if self.current_image is None:
            return
        theme = dict(bg_panel=self.bg_panel)
        dialog = ManualContrastDialog(self.root, theme)
        if dialog.result is not None and hasattr(self, 'process_manual_contrast'):
            r1, s1, r2, s2 = dialog.result
            self.process_manual_contrast(r1, s1, r2, s2)

    def open_auto_contrast_dialog(self):
        if self.current_image is None:
            return
        theme = dict(bg_panel=self.bg_panel)
        dialog = AutoContrastDialog(self.root, theme)
        if dialog.result is not None and hasattr(self, 'process_auto_contrast'):
            a, b = dialog.result
            self.process_auto_contrast(a, b)

    def _build_layout(self):
        # Body
        self.paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True)

        self.left_frame = ttk.Frame(self.paned, style="Canvas.TFrame")
        self.paned.add(self.left_frame, weight=4)

        self.canvas = tk.Canvas(self.left_frame, bg=self.bg_dark, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        self.canvas.bind("<Control-MouseWheel>", self._on_zoom_scroll)

        # panel kanan (informasi citra)
        self.right_paned = ttk.PanedWindow(self.paned, orient=tk.VERTICAL)
        self.paned.add(self.right_paned, weight=1)

        self.info_frame = ttk.LabelFrame(self.right_paned, text=" Informasi Citra ", padding=10)
        self.right_paned.add(self.info_frame, weight=1)

        self.info_text = tk.Text(self.info_frame, width=30, height=12, font=("Consolas", 9),
                                 relief=tk.FLAT, bg=self.bg_dark, fg=self.fg,
                                 insertbackground=self.fg, padx=10, pady=10, wrap=tk.WORD)
        self.info_text.pack(fill=tk.BOTH, expand=True)
        self.info_text.insert(tk.END, "Belum ada citra\nyang dibuka.")
        self.info_text.config(state=tk.DISABLED)

        # panel kanan (histogram)
        self.hist_frame = ttk.LabelFrame(self.right_paned, text=" Histogram ", padding=6)
        self.right_paned.add(self.hist_frame, weight=2)

        theme = dict(bg_dark=self.bg_dark, bg_panel=self.bg_panel,
                    fg=self.fg, fg_dim=self.fg_dim, border=self.border)
        self.hist_panel = HistogramPanel(self.hist_frame, theme, self)
        self.hist_panel.pack(fill="both", expand=True)

        status_bar = ttk.Frame(self.root, style="Toolbar.TFrame")
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        self.status_var = tk.StringVar(value="Ready")
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

        self._sash_initialized = False
        self.paned.bind("<Configure>", self._on_paned_configure)

    def _on_paned_configure(self, event):
        if self._sash_initialized or event.width < 400:
            return
        self._sash_initialized = True
        self.paned.sashpos(0, event.width - 340)

    def _dark_titlebar(self):
        try:
            import ctypes
            self.root.update()
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            for attr in (20, 19):  # 20 = Win10 2004+/11, 19 = build lama
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    hwnd, attr, ctypes.byref(ctypes.c_int(1)), 4)
        except Exception:
            pass

    def _update_history_ui(self):
        can_undo = bool(self.undo_stack)
        can_redo = bool(self.redo_stack)
        self.btn_undo.state(["!disabled"] if can_undo else ["disabled"])
        self.btn_redo.state(["!disabled"] if can_redo else ["disabled"])

    def _toggle_popup(self, owner, items):
        reopen = self._popup_owner is not owner
        self._close_popup()
        if reopen:
            self._open_popup(owner, items)

    def _close_popup(self):
        if self._popup is not None:
            self._popup.destroy()
            self._popup = None
        if self._popup_owner is not None:
            self._popup_owner.config(bg=self.bg_panel)
            self._popup_owner = None

    def _on_root_click(self, e):
        if self._popup is not None and e.widget is not self._popup_owner:
            self._close_popup()

    def _open_popup(self, owner, items):
        pop = tk.Toplevel(self.root)
        pop.withdraw()
        pop.overrideredirect(True)
        pop.configure(bg=self.border)
        body = tk.Frame(pop, bg=self.bg_panel)
        body.pack(padx=1, pady=1)

        for it in items:
            if it is None:
                tk.Frame(body, bg=self.border, height=1).pack(fill="x", pady=4)
                continue
            enabled = it.get("enabled", lambda: True)()
            row = tk.Frame(body, bg=self.bg_panel)
            row.pack(fill="x")
            left = tk.Label(row, text=it["label"], bg=self.bg_panel,
                            fg=self.fg if enabled else self.fg_dim,
                            anchor="w", padx=14, pady=5, font=("Segoe UI", 10))
            left.pack(side="left", fill="x", expand=True)
            right = tk.Label(row, text=it.get("accelerator", ""), bg=self.bg_panel,
                             fg=self.fg_dim, anchor="e", padx=14, font=("Segoe UI", 9))
            right.pack(side="right")
            if not enabled:
                continue

            def on_enter(e, ws=(row, left, right)):
                for w in ws:
                    w.config(bg=self.accent_hover)

            def on_leave(e, ws=(row, left, right)):
                for w in ws:
                    w.config(bg=self.bg_panel)

            def on_click(e, c=it["command"]):
                self._close_popup()
                c()

            for w in (row, left, right):
                w.bind("<Enter>", on_enter)
                w.bind("<Leave>", on_leave)
                w.bind("<Button-1>", on_click)

        pop.update_idletasks()
        pop.geometry(f"+{owner.winfo_rootx()}+{owner.winfo_rooty() + owner.winfo_height()}")
        pop.deiconify()
        pop.attributes("-topmost", True)
        self._popup = pop
        self._popup_owner = owner
        owner.config(bg=self.accent_hover)

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
        if hasattr(self, 'display_image'):
            self.display_image(self.current_image)

    # Info
    def show_about(self):
        messagebox.showinfo("Tentang", "MiniPhotoshop\nEngine C++ + GUI Python")