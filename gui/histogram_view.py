"""Panel histogram: chart (matplotlib) + statistik + dropdown mode.
Dipanggil dari view.py: HistogramPanel(parent, theme).update(img)
"""
import tkinter as tk
from tkinter import ttk

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import FuncFormatter

import mps_engine

COLORS = {"red": "#ff4d4d", "green": "#4dff88", "blue": "#4d9dff"}
NEUTRAL = "#d4d4d4"

MODES_COLOR = ["Luminosity", "RGB Overlay", "Red", "Green", "Blue"]
MODES_GRAY = ["Grayscale"]

def _fmt_y(val, pos):
    if val >= 1_000_000:
        return f"{val/1_000_000:.1f}M"
    if val >= 1_000:
        return f"{val/1_000:.0f}K"
    if val < 1:
        return f"{val:.3f}"
    return f"{val:.0f}"

class HistogramPanel(tk.Frame):
    def __init__(self, parent, theme, app):
        # theme: dict warna dari ViewMixin._setup_style
        # (bg_dark, bg_panel, fg, fg_dim, border)
        self.t = theme
        self.app = app
        super().__init__(parent, bg=self.t["bg_dark"])

        self._img = None
        self._gray_hist = None
        self._color_hist = None

        self._build_ui()

    def _build_ui(self):
        top = tk.Frame(self, bg=self.t["bg_dark"])
        top.pack(fill="x", padx=8, pady=(8, 0))

        tk.Label(top, text="Mode:", bg=self.t["bg_dark"], fg=self.t["fg"],
                 font=("Segoe UI", 9)).pack(side="left")

        self.mode_var = tk.StringVar(value=MODES_COLOR[1])
        self.mode_btn = tk.Label(top, textvariable=self.mode_var,
                                 bg=self.t["bg_panel"], fg=self.t["fg"],
                                 padx=10, pady=3, font=("Segoe UI", 9),
                                 relief="flat", cursor="hand2")
        self.mode_btn.pack(side="left", padx=8)
        self.mode_btn.bind("<Button-1>", self._open_mode_menu)

        self._modes = MODES_COLOR

        norm_row = tk.Frame(self, bg=self.t["bg_dark"])
        norm_row.pack(fill="x", padx=8, pady=(4, 0))
        self.norm_var = tk.BooleanVar(value=False)
        tk.Checkbutton(norm_row, text="Ternormalisasi", variable=self.norm_var,
                       command=self._redraw, bg=self.t["bg_dark"], fg=self.t["fg"],
                       selectcolor=self.t["bg_panel"], activebackground=self.t["bg_dark"],
                       activeforeground=self.t["fg"], font=("Segoe UI", 9)).pack(side="left")

        self.fig = Figure(figsize=(3.0, 1.8), dpi=100, facecolor=self.t["bg_dark"])
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)

        self.stats_var = tk.StringVar(value="")
        tk.Label(self, textvariable=self.stats_var, bg=self.t["bg_dark"], fg=self.t["fg_dim"],
                 font=("Consolas", 9), justify="left", anchor="w").pack(
            fill="x", padx=8, pady=(0, 8))

    def _open_mode_menu(self, event):
        items = [
            dict(label=m, command=lambda m=m: self._select_mode(m))
            for m in self._modes
        ]
        self.app._toggle_popup(self.mode_btn, items)

    def _select_mode(self, mode):
        self.mode_var.set(mode)
        self._redraw()

    def _autoscale_ignore_extremes(self, *ys):
        trimmed = []
        for y in ys:
            trimmed.extend(list(y)[1:-1])  # buang bin 0 dan 255
        if trimmed and max(trimmed) > 0:
            self.ax.set_ylim(0, max(trimmed) * 1.1)

    # ---------- PUBLIC ----------
    def update(self, img):
        """Panggil ini tiap citra berubah (live update)."""
        self._img = img
        if img is None:
            self._gray_hist = None
            self._color_hist = None
            self._clear()
            return

        if img.channels == 1:
            self._gray_hist = mps_engine.compute_histogram(img)
            self._color_hist = None
            self._modes = MODES_GRAY
            self.mode_var.set(MODES_GRAY[0])
        else:
            self._color_hist = mps_engine.compute_color_histogram(img)
            self._gray_hist = None
            self._modes = MODES_COLOR
            if self.mode_var.get() not in MODES_COLOR:
                self.mode_var.set(MODES_COLOR[1])

        self._redraw()

    # ---------- INTERNAL ----------
    def _clear(self):
        self.ax.clear()
        self._style_axes()
        self.canvas.draw()
        self.stats_var.set("Belum ada citra.")
    
    def _style_axes(self):
        self.ax.set_facecolor(self.t["bg_dark"])
        for spine in ("top", "right"):
            self.ax.spines[spine].set_visible(False)
        for spine in ("left", "bottom"):
            self.ax.spines[spine].set_color(self.t["border"])
        self.ax.tick_params(colors=self.t["fg_dim"], labelsize=8)
        self.ax.set_xlim(0, 255)
        self.ax.yaxis.set_major_formatter(FuncFormatter(_fmt_y))

    def _redraw(self):
        self.ax.clear()
        self._style_axes()
    
        mode = self.mode_var.get()
        normalized = self.norm_var.get()
        x = range(256)
    
        def series(h):
            return h.normalized if normalized else h.counts
    
        if self._gray_hist is not None:
            h = self._gray_hist
            y = series(h)
            self.ax.bar(x, y, width=1, color=NEUTRAL, edgecolor="none")
            self._autoscale_ignore_extremes(y)
            self._set_stats(h)
    
        elif self._color_hist is not None:
            ch = self._color_hist
            if mode == "RGB Overlay":
                ys = []
                for name in ("red", "green", "blue"):
                    h = getattr(ch, name)
                    y = series(h)
                    ys.append(y)
                    self.ax.plot(x, y, color=COLORS[name], linewidth=1.2,
                                alpha=0.85, label=name.capitalize())
                    self.ax.fill_between(x, y, color=COLORS[name], alpha=0.15)
                self._autoscale_ignore_extremes(*ys)
                self._set_stats(ch.red, ch.green, ch.blue)
            elif mode == "Luminosity":
                h = ch.luminosity
                y = series(h)
                self.ax.plot(x, y, color=NEUTRAL, linewidth=1.2)
                self.ax.fill_between(x, y, color=NEUTRAL, alpha=0.15)
                self._autoscale_ignore_extremes(y)
                self._set_stats(h)
            else:  # Red / Green / Blue
                name = mode.lower()
                h = getattr(ch, name)
                y = series(h)
                self.ax.plot(x, y, color=COLORS[name], linewidth=1.2)
                self.ax.fill_between(x, y, color=COLORS[name], alpha=0.15)
                self._autoscale_ignore_extremes(y)
                self._set_stats(h)
    
        self.fig.tight_layout(pad=0.5)
        self.canvas.draw()

    def _set_stats(self, *hists):
        if len(hists) == 1:
            h = hists[0]
            self.stats_var.set(
                f"Total piksel : {h.total_pixels}\n"
                f"Mean          : {h.mean:.2f}\n"
                f"Variance      : {h.variance:.2f}\n"
                f"Std Dev       : {h.stdv:.2f}"
            )
        else:
            labels = ("R", "G", "B")
            lines = ["            " + "  ".join(f"{l:>8}" for l in labels)]
            lines.append("Mean      " + "  ".join(f"{h.mean:8.2f}" for h in hists))
            lines.append("Variance  " + "  ".join(f"{h.variance:8.2f}" for h in hists))
            lines.append("Std Dev   " + "  ".join(f"{h.stdv:8.2f}" for h in hists))
            self.stats_var.set("\n".join(lines))