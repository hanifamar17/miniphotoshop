import queue
import random
import threading
import tkinter as tk
from tkinter import messagebox, ttk

import mps_engine
from histogram_view import HistogramPanel


class PowerTransformDialog(tk.Toplevel):
    def __init__(self, parent, theme):
        super().__init__(parent)
        self.title("Power (Gamma) Transformation")
        self.resizable(False, False)
        self.configure(bg=theme["bg_panel"])
        self.result = None

        # Style khusus agar angka pada Spinbox jelas terbaca
        style = ttk.Style(self)
        style.configure("Gamma.TSpinbox",
                        fieldbackground="#181818", foreground="#ffffff",
                        arrowcolor="#ffffff", insertcolor="#ffffff")

        container = ttk.Frame(self, padding=15)
        container.pack(fill="both", expand=True)

        ttk.Label(container, text="Nilai Gamma (γ):").grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.gamma_var = tk.DoubleVar(value=1.0)
        self.spinbox = ttk.Spinbox(container, from_=0.1, to=5.0, increment=0.1,
                                   textvariable=self.gamma_var, width=8,
                                   format="%.1f", style="Gamma.TSpinbox",
                                   command=self._on_spin)
        self.spinbox.grid(row=0, column=1, padx=5, pady=5)

        # Slider langsung berada di bawah row Spinbox
        self.slider = ttk.Scale(container, from_=0.1, to=5.0, variable=self.gamma_var,
                                orient='horizontal', length=220,
                                command=self._on_slide)
        self.slider.grid(row=1, column=0, columnspan=2, padx=5, pady=10, sticky="we")

        btn_frame = ttk.Frame(container)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=(10, 0))
        ttk.Button(btn_frame, text="OK", command=self.on_ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Batal", command=self.destroy).pack(side=tk.LEFT, padx=5)

        self.transient(parent)
        self.grab_set()
        parent.wait_window(self)

    def _on_slide(self, val):
        v = round(float(val), 1)
        self.gamma_var.set(v)

    def _on_spin(self):
        try:
            v = round(float(self.spinbox.get()), 1)
            self.gamma_var.set(v)
        except ValueError:
            pass

    def on_ok(self):
        try:
            val = round(float(self.spinbox.get()), 1)
            if val <= 0:
                raise ValueError
            self.result = val
            self.destroy()
        except (ValueError, tk.TclError):
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

        # Diperbaiki: Menggunakan tk.BooleanVar
        self.preserve_var = tk.BooleanVar(value=False)
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

        # Diperbaiki: Menggunakan tk.BooleanVar
        self.binary_var = tk.BooleanVar(value=True)
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

        container = ttk.Frame(self, padding=20)
        container.pack(fill="both", expand=True)

        self.r1_var = tk.IntVar(value=50)
        self.s1_var = tk.IntVar(value=20)
        self.r2_var = tk.IntVar(value=150)
        self.s2_var = tk.IntVar(value=220)

        # Indikator angka disesuaikan agar jelas terlihat menggunakan tk.Label kontras
        # Slider r1
        ttk.Label(container, text="Titik Input r1:").grid(row=0, column=0, sticky="w", pady=(0, 2))
        self.r1_lbl = tk.Label(container, text="50", width=4, anchor="e", bg=theme["bg_panel"], fg="#4fc3f7", font=("Segoe UI", 10, "bold"))
        self.r1_lbl.grid(row=0, column=2, sticky="e", pady=(0, 2))
        self.r1_slider = ttk.Scale(container, from_=0, to=255, variable=self.r1_var, 
                                   orient='horizontal', length=240, command=self._on_r1_change)
        self.r1_slider.grid(row=1, column=0, columnspan=3, pady=(0, 10), sticky="we")

        # Slider r2
        ttk.Label(container, text="Titik Input r2:").grid(row=2, column=0, sticky="w", pady=(0, 2))
        self.r2_lbl = tk.Label(container, text="150", width=4, anchor="e", bg=theme["bg_panel"], fg="#4fc3f7", font=("Segoe UI", 10, "bold"))
        self.r2_lbl.grid(row=2, column=2, sticky="e", pady=(0, 2))
        self.r2_slider = ttk.Scale(container, from_=0, to=255, variable=self.r2_var, 
                                   orient='horizontal', length=240, command=self._on_r2_change)
        self.r2_slider.grid(row=3, column=0, columnspan=3, pady=(0, 10), sticky="we")

        # Separator
        ttk.Separator(container, orient='horizontal').grid(row=4, column=0, columnspan=3, sticky="we", pady=10)

        # Slider s1
        ttk.Label(container, text="Titik Output s1:").grid(row=5, column=0, sticky="w", pady=(0, 2))
        self.s1_lbl = tk.Label(container, text="20", width=4, anchor="e", bg=theme["bg_panel"], fg="#4fc3f7", font=("Segoe UI", 10, "bold"))
        self.s1_lbl.grid(row=5, column=2, sticky="e", pady=(0, 2))
        self.s1_slider = ttk.Scale(container, from_=0, to=255, variable=self.s1_var, 
                                   orient='horizontal', length=240, command=lambda v: self.s1_lbl.config(text=str(int(float(v)))))
        self.s1_slider.grid(row=6, column=0, columnspan=3, pady=(0, 10), sticky="we")

        # Slider s2
        ttk.Label(container, text="Titik Output s2:").grid(row=7, column=0, sticky="w", pady=(0, 2))
        self.s2_lbl = tk.Label(container, text="220", width=4, anchor="e", bg=theme["bg_panel"], fg="#4fc3f7", font=("Segoe UI", 10, "bold"))
        self.s2_lbl.grid(row=7, column=2, sticky="e", pady=(0, 2))
        self.s2_slider = ttk.Scale(container, from_=0, to=255, variable=self.s2_var, 
                                   orient='horizontal', length=240, command=lambda v: self.s2_lbl.config(text=str(int(float(v)))))
        self.s2_slider.grid(row=8, column=0, columnspan=3, pady=(0, 15), sticky="we")

        btn_frame = ttk.Frame(container)
        btn_frame.grid(row=9, column=0, columnspan=3, pady=(10, 0))
        ttk.Button(btn_frame, text="Terapkan", command=self.on_ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Batal", command=self.destroy).pack(side=tk.LEFT, padx=5)

        self.transient(parent)
        self.grab_set()
        parent.wait_window(self)

    def _on_r1_change(self, val):
        r1 = int(float(val))
        self.r1_lbl.config(text=str(r1))
        if r1 > self.r2_var.get():
            self.r2_var.set(r1)
            self.r2_lbl.config(text=str(r1))

    def _on_r2_change(self, val):
        r2 = int(float(val))
        self.r2_lbl.config(text=str(r2))
        if r2 < self.r1_var.get():
            self.r1_var.set(r2)
            self.r1_lbl.config(text=str(r2))

    def on_ok(self):
        r1, s1 = self.r1_var.get(), self.s1_var.get()
        r2, s2 = self.r2_var.get(), self.s2_var.get()

        if r1 > r2:
            messagebox.showerror("Error", "Nilai r1 tidak boleh lebih besar dari r2!", parent=self)
            return

        self.result = (r1, s1, r2, s2)
        self.destroy()


class AutoContrastDialog(tk.Toplevel):
    def __init__(self, parent, theme):
        super().__init__(parent)
        self.title("Auto Contrast Stretching")
        self.resizable(False, False)
        self.configure(bg=theme["bg_panel"])
        self.result = None

        container = ttk.Frame(self, padding=20)
        container.pack(fill="both", expand=True)

        self.a_var = tk.DoubleVar(value=1.0)
        self.b_var = tk.DoubleVar(value=99.0)

        # Indikator angka disesuaikan dengan warna kontras dan pembatasan desimal
        # Slider Persen Tergelap (a %)
        ttk.Label(container, text="Potong Persen Tergelap (a %):").grid(row=0, column=0, sticky="w", pady=(0, 2))
        self.a_lbl = tk.Label(container, text="1.0%", width=6, anchor="e", bg=theme["bg_panel"], fg="#4fc3f7", font=("Segoe UI", 10, "bold"))
        self.a_lbl.grid(row=0, column=1, sticky="e", pady=(0, 2))
        self.a_slider = ttk.Scale(container, from_=0.0, to=100.0, variable=self.a_var, 
                                  orient='horizontal', length=240, command=self._on_a_change)
        self.a_slider.grid(row=1, column=0, columnspan=2, pady=(0, 15), sticky="we")

        # Slider Persen Terterang (b %)
        ttk.Label(container, text="Potong Persen Terterang (b %):").grid(row=2, column=0, sticky="w", pady=(0, 2))
        self.b_lbl = tk.Label(container, text="99.0%", width=6, anchor="e", bg=theme["bg_panel"], fg="#4fc3f7", font=("Segoe UI", 10, "bold"))
        self.b_lbl.grid(row=2, column=1, sticky="e", pady=(0, 2))
        self.b_slider = ttk.Scale(container, from_=0.0, to=100.0, variable=self.b_var, 
                                  orient='horizontal', length=240, command=self._on_b_change)
        self.b_slider.grid(row=3, column=0, columnspan=2, pady=(0, 15), sticky="we")

        btn_frame = ttk.Frame(container)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=(10, 0))
        ttk.Button(btn_frame, text="Terapkan", command=self.on_ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Batal", command=self.destroy).pack(side=tk.LEFT, padx=5)

        self.transient(parent)
        self.grab_set()
        parent.wait_window(self)

    def _on_a_change(self, val):
        a = round(float(val), 1)
        self.a_var.set(a)
        self.a_lbl.config(text=f"{a:.1f}%")
        if a >= self.b_var.get():
            new_b = min(100.0, round(a + 0.1, 1))
            self.b_var.set(new_b)
            self.b_lbl.config(text=f"{new_b:.1f}%")

    def _on_b_change(self, val):
        b = round(float(val), 1)
        self.b_var.set(b)
        self.b_lbl.config(text=f"{b:.1f}%")
        if b <= self.a_var.get():
            new_a = max(0.0, round(b - 0.1, 1))
            self.a_var.set(new_a)
            self.a_lbl.config(text=f"{new_a:.1f}%")

    def on_ok(self):
        a = round(self.a_var.get(), 1)
        b = round(self.b_var.get(), 1)

        if a >= b:
            messagebox.showerror("Error", "Syarat batas tergelap (a) < terterang (b) tidak terpenuhi!", parent=self)
            return

        self.result = (a, b)
        self.destroy()



# =============================================================================
# ADAPTER ENGINE  --  kalau nama/urutan argumen di mps_engine berbeda,
# CUKUP UBAH BAGIAN INI.
# Engine boleh in-place (return None) atau return citra baru; dua-duanya ditangani.
# =============================================================================
def _engine_fn(*names):
    for n in names:
        fn = getattr(mps_engine, n, None)
        if fn is not None:
            return fn
    raise AttributeError("mps_engine tidak punya: " + " / ".join(names))


def _result(img, out):
    return img if out is None else out


def run_salt_pepper(img, prob, seed):
    return _result(img, _engine_fn("add_salt_pepper")(img, prob, seed))


def run_mean(img, ksize):
    return _result(img, _engine_fn("mean_filter", "mean_blur")(img, ksize))


def run_median(img, ksize):
    return _result(img, _engine_fn("median_filter")(img, ksize))


def run_gaussian(img, ksize, sigma):
    return _result(img, _engine_fn("gaussian_filter")(img, ksize, sigma))


def run_sobel(img, mode):
    return _result(img, _engine_fn("sobel", "sobel_edge", "sobel_edge_detection",
                                   "sobel_filter")(img, mode))


# =============================================================================
# BASE DIALOG
# =============================================================================
class PreviewDialog(tk.Toplevel):
    TITLE = ""
    APPLIED_MSG = ""
    DEBOUNCE_MS = 150
    WINDOW_SIZES = ("3", "5", "7", "9", "11")

    def __init__(self, app):
        super().__init__(app.root)
        self.app = app
        self.title(self.TITLE)
        self.resizable(False, False)
        self.configure(bg=app.bg_panel)

        ttk.Style(self).configure("Hint.TLabel", foreground=app.fg_dim)

        # Citra asli saat dialog dibuka. Semua preview berasal dari sini.
        self.base = app.clone_image(app.current_image)

        self._token = 0
        self._after_id = None
        self._queue = queue.Queue()
        self._polling = False
        self._result = None
        self._ready = False
        self._closed = False

        outer = ttk.Frame(self, padding=15)
        outer.pack(fill="both", expand=True)

        self.controls = ttk.Frame(outer)
        self.controls.pack(fill="x")
        self.build_controls(self.controls)

        self.busy_var = tk.StringVar(value="")
        ttk.Label(outer, textvariable=self.busy_var, style="Hint.TLabel",
                  wraplength=280).pack(anchor="w", pady=(10, 0))

        btns = ttk.Frame(outer)
        btns.pack(pady=(10, 0))
        self.btn_apply = ttk.Button(btns, text="Terapkan", command=self.on_apply)
        self.btn_apply.pack(side=tk.LEFT, padx=5)
        ttk.Button(btns, text="Batal", command=self.on_cancel).pack(side=tk.LEFT, padx=5)
        self.btn_apply.state(["disabled"])

        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.bind("<Escape>", lambda e: self.on_cancel())
        # Cegah shortcut global (undo/redo/open/save) saat dialog terbuka.
        for seq in ("<Control-z>", "<Control-Shift-Y>", "<Control-Shift-y>",
                    "<Control-o>", "<Control-s>"):
            self.bind(seq, lambda e: "break")

        self.transient(app.root)
        try:
            self.wait_visibility()
            self.grab_set()
        except tk.TclError:
            pass

        self.request_preview(delay=0)   # preview langsung pakai nilai default

    # ----- diisi subclass -----
    def build_controls(self, parent):
        raise NotImplementedError

    def get_params(self):
        raise NotImplementedError

    def compute(self, img, params):
        raise NotImplementedError

    # ----- helper UI -----
    def add_hint(self, parent, text):
        ttk.Label(parent, text=text, style="Hint.TLabel",
                  wraplength=280, justify="left").pack(anchor="w", pady=(8, 0))

    def add_ksize_combo(self, parent, default):
        self.ksize_var = tk.StringVar(value=str(default))
        self.ksize_lbl = ttk.Label(parent, text="")
        self.ksize_lbl.pack(anchor="w")
        box = ttk.Combobox(parent, textvariable=self.ksize_var, values=self.WINDOW_SIZES,
                           state="readonly", width=6)
        box.pack(anchor="w", pady=(2, 0))
        box.bind("<<ComboboxSelected>>", lambda e: self._on_ksize())
        self._refresh_ksize_label()

    def _refresh_ksize_label(self):
        k = int(self.ksize_var.get())
        self.ksize_lbl.config(text=f"Ukuran jendela: {k} × {k}")

    def _on_ksize(self):
        self._refresh_ksize_label()
        self.request_preview(delay=0)

    @property
    def ksize(self):
        return int(self.ksize_var.get())

    # ----- mesin preview -----
    def request_preview(self, delay=None):
        if self._closed:
            return
        if delay is None:
            delay = self.DEBOUNCE_MS
        self._token += 1                     # hasil job lama jadi usang
        self._ready = False
        self.btn_apply.state(["disabled"])
        self.busy_var.set("Memproses...")
        if self._after_id is not None:
            self.after_cancel(self._after_id)
        self._after_id = self.after(delay, self._start_job)

    def _start_job(self):
        self._after_id = None
        if self._closed:
            return
        token = self._token
        params = self.get_params()                  # dibaca di thread utama
        img = self.app.clone_image(self.base)       # selalu dari citra asli

        def work():
            try:
                out = self.compute(img, params)
                self._queue.put((token, out, None))
            except Exception as e:                  # noqa: BLE001
                self._queue.put((token, None, e))

        threading.Thread(target=work, daemon=True).start()
        if not self._polling:
            self._polling = True
            self._poll()

    def _poll(self):
        if self._closed:
            self._polling = False
            return
        try:
            while True:
                token, out, err = self._queue.get_nowait()
                if token != self._token:
                    continue                        # hasil usang, abaikan
                self._finish(out, err)
        except queue.Empty:
            pass
        if self._ready:
            self._polling = False
        else:
            self.after(30, self._poll)

    def _finish(self, out, err):
        if err is not None:
            self.busy_var.set(f"Gagal: {err}")
            return
        self._result = out
        self._ready = True
        self.busy_var.set("")
        self.app.display_image(out)
        self.btn_apply.state(["!disabled"])

    # ----- tombol -----
    def _close(self):
        self._closed = True
        self._token += 1
        if self._after_id is not None:
            self.after_cancel(self._after_id)
            self._after_id = None
        try:
            self.grab_release()
        except tk.TclError:
            pass
        self.destroy()

    def on_apply(self):
        if not self._ready or self._closed:
            return
        app, result = self.app, self._result
        self._close()
        app.push_undo()                  # menyimpan citra asli + kosongkan redo_stack
        app.current_image = result
        app.display_image(result)
        app.update_info()
        app.set_status(self.APPLIED_MSG)

    def on_cancel(self):
        self._close()
        self.app.display_image(self.app.current_image)   # kembali ke citra asli


# =============================================================================
# DIALOG: SALT & PEPPER
# =============================================================================
class SaltPepperDialog(PreviewDialog):
    TITLE = "Salt & Pepper Noise"
    APPLIED_MSG = "Salt & pepper noise applied"

    def build_controls(self, parent):
        self.seed = random.randrange(1, 2 ** 31)      # tetap selama dialog terbuka
        self.pct_var = tk.DoubleVar(value=10)
        self.pct_lbl = ttk.Label(parent, text="Probabilitas: 10%")
        self.pct_lbl.pack(anchor="w")
        ttk.Scale(parent, from_=1, to=50, variable=self.pct_var, orient="horizontal",
                  length=240, command=self._on_slide).pack(anchor="w", pady=(2, 0))
        ttk.Button(parent, text="Acak ulang", command=self._reseed).pack(anchor="w", pady=(10, 0))

    def _pct(self):
        return int(round(self.pct_var.get()))

    def _on_slide(self, _val):
        self.pct_lbl.config(text=f"Probabilitas: {self._pct()}%")
        self.request_preview()

    def _reseed(self):
        self.seed = random.randrange(1, 2 ** 31)
        self.request_preview(delay=0)

    def get_params(self):
        return self._pct() / 100.0, self.seed

    def compute(self, img, params):
        prob, seed = params
        return run_salt_pepper(img, prob, seed)


# =============================================================================
# DIALOG: MEAN / MEDIAN
# =============================================================================
class MeanDialog(PreviewDialog):
    TITLE = "Mean Filter"
    APPLIED_MSG = "Mean filter applied"
    HINT = "Mean = menghaluskan."

    def build_controls(self, parent):
        self.add_ksize_combo(parent, 3)
        self.add_hint(parent, self.HINT)

    def get_params(self):
        return self.ksize

    def compute(self, img, k):
        return run_mean(img, k)


class MedianDialog(MeanDialog):
    TITLE = "Median Filter"
    APPLIED_MSG = "Median filter applied"
    HINT = "Median = hilangkan noise bintik (salt & pepper)."

    def compute(self, img, k):
        return run_median(img, k)


# =============================================================================
# DIALOG: GAUSSIAN
# =============================================================================
class GaussianDialog(PreviewDialog):
    TITLE = "Gaussian Filter"
    APPLIED_MSG = "Gaussian filter applied"

    def build_controls(self, parent):
        self.add_ksize_combo(parent, 5)
        self.sigma_var = tk.DoubleVar(value=1.0)
        self.sigma_lbl = ttk.Label(parent, text="Sigma: 1.0")
        self.sigma_lbl.pack(anchor="w", pady=(10, 0))
        ttk.Scale(parent, from_=0.5, to=3.0, variable=self.sigma_var, orient="horizontal",
                  length=240, command=self._on_sigma).pack(anchor="w", pady=(2, 0))
        self.add_hint(parent, "Seperti Mean, tapi piksel tengah berbobot lebih besar. "
                              "Sigma besar = lebih buram.")

    def _sigma(self):
        return round(self.sigma_var.get(), 1)

    def _on_sigma(self, _val):
        self.sigma_lbl.config(text=f"Sigma: {self._sigma():.1f}")
        self.request_preview()

    def get_params(self):
        return self.ksize, self._sigma()

    def compute(self, img, params):
        k, sigma = params
        return run_gaussian(img, k, sigma)


# =============================================================================
# DIALOG: SOBEL
# =============================================================================
class SobelDialog(PreviewDialog):
    TITLE = "Sobel Edge Detection"
    APPLIED_MSG = "Sobel edge detection applied"
    METHODS = ("0 — |Gx| + |Gy|", "1 — Maksimum", "2 — Akar kuadrat", "3 — Rata-rata")

    def build_controls(self, parent):
        ttk.Label(parent, text="Metode gabungan:").pack(anchor="w")
        self.mode_box = ttk.Combobox(parent, values=self.METHODS, state="readonly", width=24)
        self.mode_box.current(0)                      # preview langsung mode 0
        self.mode_box.pack(anchor="w", pady=(2, 0))
        self.mode_box.bind("<<ComboboxSelected>>", lambda e: self.request_preview(delay=0))

    def get_params(self):
        return self.mode_box.current()                # indeks = nilai argumen mode

    def compute(self, img, mode):
        return run_sobel(img, mode)


# =============================================================================
# PINTU MASUK (dipanggil dari view.py)
# =============================================================================
def _need_image(app):
    if app.current_image is None:
        messagebox.showwarning("Peringatan", "Belum ada citra yang dibuka")
        return False
    return True


def open_salt_pepper(app):
    if _need_image(app):
        SaltPepperDialog(app)


def open_mean(app):
    if _need_image(app):
        MeanDialog(app)


def open_median(app):
    if _need_image(app):
        MedianDialog(app)


def open_gaussian(app):
    if _need_image(app):
        GaussianDialog(app)


def _ask_sobel_rgb(app):
    """True = konversi dulu, False = lanjut apa adanya, None = batal."""
    win = tk.Toplevel(app.root)
    win.title("Sobel")
    win.resizable(False, False)
    win.configure(bg=app.bg_panel)
    choice = {"v": None}

    def pick(v):
        choice["v"] = v
        win.destroy()

    body = ttk.Frame(win, padding=15)
    body.pack()
    ttk.Label(body, text="Sobel bekerja per kanal.\nUbah ke grayscale dulu?",
              justify="left").pack(anchor="w")
    row = ttk.Frame(body)
    row.pack(pady=(12, 0))
    ttk.Button(row, text="Konversi dulu", command=lambda: pick(True)).pack(side=tk.LEFT, padx=5)
    ttk.Button(row, text="Lanjut", command=lambda: pick(False)).pack(side=tk.LEFT, padx=5)

    win.protocol("WM_DELETE_WINDOW", lambda: pick(None))   # X = batal
    win.transient(app.root)
    try:
        win.wait_visibility()
        win.grab_set()
    except tk.TclError:
        pass
    app.root.wait_window(win)
    return choice["v"]


def open_sobel(app):
    if not _need_image(app):
        return
    if app.current_image.channels == 3:
        choice = _ask_sobel_rgb(app)
        if choice is None:
            return
        if choice:
            app.apply_grayscale()                       # sudah push_undo + display
            if app.current_image.channels == 3:         # konversi gagal
                return
    SobelDialog(app)


# CLASS VIEWMIXIN


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
        
            # MENU IMAGE
        add("Image", [
            dict(label="Negative", command=self.apply_negative), 
            dict(label="Grayscale", command=self.apply_grayscale),
            dict(label="Brightness...", command=self.open_brightening_dialog),
            None,
            dict(label="Manual Contrast Stretching...", command=self.open_manual_contrast_dialog),
            dict(label="Auto Contrast Stretching...", command=self.open_auto_contrast_dialog),
            dict(label="Histogram Equalization", command=self.apply_equalize),  
            None,
            dict(label="Log Transformation", command=self.apply_log),
            dict(label="Inverse Log Transformation", command=self.apply_inverse_log),
            dict(label="Power (Gamma)...", command=self.open_power_dialog),
            None,
            dict(label="Gray-level Slicing...", command=self.open_gray_slicing_dialog),
            dict(label="Bit-plane Slicing...", command=self.open_bit_plane_dialog),
            None,
            dict(label="Salt & Pepper Noise...", command=self.open_salt_pepper_dialog),
            dict(label="Mean Filter...", command=self.open_mean_dialog),
            dict(label="Gaussian Filter...", command=self.open_gaussian_dialog),
            dict(label="Median Filter...", command=self.open_median_dialog),
            dict(label="Sobel Edge Detection...", command=self.open_sobel_dialog),
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

    # ---------- DIALOG FILTER (preview langsung, kelas dialog ada di atas) ----------
    def open_salt_pepper_dialog(self):
        open_salt_pepper(self)

    def open_mean_dialog(self):
        open_mean(self)

    def open_gaussian_dialog(self):
        open_gaussian(self)

    def open_median_dialog(self):
        open_median(self)

    def open_sobel_dialog(self):
        open_sobel(self)

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