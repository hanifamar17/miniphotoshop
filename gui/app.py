import sys
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image as PILImage, ImageTk
import numpy as np

# tambahkan folder build engine ke path, biar bisa import mps_engine
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "engine", "build"))
import mps_engine


class MiniPhotoshopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MiniPhotoshop")
        self.root.geometry("950x600")

        self.current_image = None  # simpan Image object dari engine
        self.original_image = None # simpan citra awal persis saat dibuka
        self.current_filename = None
        self.tk_image = None

        # Undo stack
        self.undo_stack = []

        self._build_menu()
        self._build_layout()
        
        # Shortcut Ctrl+Z untuk Undo
        self.root.bind("<Control-z>", lambda event: self.undo())

    def _build_layout(self):
        # Frame Utama menggunakan panedwindow
        self.paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True)

        # Frame Kiri: Canvas Gambar
        self.left_frame = tk.Frame(self.paned, bg="gray")
        self.paned.add(self.left_frame, weight=3)

        self.canvas = tk.Canvas(self.left_frame, bg="gray")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Frame Kanan: Panel Info Citra
        self.info_frame = tk.LabelFrame(self.paned, text=" Informasi Citra ", padx=10, pady=10, font=("Consolas", 10, "bold"))
        self.paned.add(self.info_frame, weight=1)

        # Text Widget untuk info
        self.info_text = tk.Text(self.info_frame, width=30, height=20, font=("Consolas", 9), relief=tk.FLAT, bg=self.root.cget("bg"))
        self.info_text.pack(fill=tk.BOTH, expand=True)
        self.info_text.insert(tk.END, "Belum ada citra\nyang dibuka.")
        self.info_text.config(state=tk.DISABLED)

    def _build_menu(self):
        menubar = tk.Menu(self.root)

        # Menu Arsip
        menu_arsip = tk.Menu(menubar, tearoff=0)
        menu_arsip.add_command(label="Buka...", command=self.open_file)
        menu_arsip.add_command(label="Simpan...", command=self.save_file)
        menu_arsip.add_separator()
        menu_arsip.add_command(label="Keluar", command=self.root.quit)
        menubar.add_cascade(label="Arsip", menu=menu_arsip)

        # Menu Edit (Undo & Reset)
        menu_edit = tk.Menu(menubar, tearoff=0)
        menu_edit.add_command(label="Undo (Ctrl+Z)", command=self.undo)
        menu_edit.add_command(label="Reset ke Original", command=self.reset_to_original)
        menubar.add_cascade(label="Edit", menu=menu_edit)

        # Menu Olah Citra
        menu_olah = tk.Menu(menubar, tearoff=0)
        menu_olah.add_command(label="Citra Negatif", command=self.apply_negative)
        menu_olah.add_command(label="Ubah ke Grayscale", command=self.apply_grayscale)
        menu_olah.add_command(label="Brightening...", command=self.open_brightening_dialog)
        menubar.add_cascade(label="Olah Citra", menu=menu_olah)

        # Menu Bantuan
        menu_bantuan = tk.Menu(menubar, tearoff=0)
        menu_bantuan.add_command(label="Tentang", command=self.show_about)
        menubar.add_cascade(label="Bantuan", menu=menu_bantuan)

        self.root.config(menu=menubar)

    # ---------- HELPER CLONE IMAGE ----------
    def clone_image(self, img):
        if img is None:
            return None
        # Memanggil brightening dengan nilai 0 untuk membuat salinan tanpa mengubah piksel
        return mps_engine.brighten(img, 0)

    # ---------- UNDO & RESET ----------
    def push_undo(self):
        if self.current_image is not None:
            self.undo_stack.append(self.clone_image(self.current_image))

    def undo(self):
        if not self.undo_stack:
            messagebox.showinfo("Undo", "Tidak ada riwayat perubahan lagi.")
            return

        self.current_image = self.undo_stack.pop()
        self.display_image(self.current_image)
        self.update_info()

    def reset_to_original(self):
        if self.original_image is None:
            messagebox.showwarning("Peringatan", "Belum ada citra yang dibuka.")
            return

        self.push_undo()
        self.current_image = self.clone_image(self.original_image)
        self.display_image(self.current_image)
        self.update_info()

    # ---------- UPDATE PANEL INFO ----------
    def update_info(self):
        if self.current_image is None:
            return

        img = self.current_image
        file_size = os.path.getsize(self.current_filename) if self.current_filename and os.path.exists(self.current_filename) else 0
        file_name_only = os.path.basename(self.current_filename) if self.current_filename else "-"
        format_file = os.path.splitext(self.current_filename)[1].upper().lstrip(".") if self.current_filename else "-"

        arr = img.to_numpy()
        if img.channels == 3:
            jenis = "Berwarna (RGB)"
        elif np.isin(arr, (0, 255)).all():
            jenis = "Biner (hitam-putih)"
        else:
            jenis = "Grayscale"

        info = (
            f"Nama File:\n{file_name_only}\n\n"
            f"Format   : {format_file}\n"
            f"Ukuran   : {img.width} x {img.height} px\n"
            f"Channels : {img.channels}\n"
            f"Jenis    : {jenis}\n\n"
            f"Ukuran File:\n{file_size} byte\n({file_size / 1024:.2f} KB)"
        )

        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete("1.0", tk.END)
        self.info_text.insert(tk.END, info)
        self.info_text.config(state=tk.DISABLED)

    # ---------- BUKA FILE ----------
    def open_file(self):
        filename = filedialog.askopenfilename(
            title="Buka Arsip Citra",
            filetypes=[
                ("Semua format didukung", "*.pbm *.pgm *.ppm *.bmp *.raw"),
                ("PBM files", "*.pbm"),
                ("PGM files", "*.pgm"),
                ("PPM files", "*.ppm"),
                ("BMP files", "*.bmp"),
                ("RAW files", "*.raw"),
                ("All files", "*.*"),
            ]
        )
        if not filename:
            return

        ext = os.path.splitext(filename)[1].lower()
        if ext == ".pbm":
            ok, img = mps_engine.load_pbm(filename)
        elif ext == ".pgm":
            ok, img = mps_engine.load_pgm(filename)
        elif ext == ".ppm":
            ok, img = mps_engine.load_ppm(filename)
        elif ext == ".bmp":
            ok, img = mps_engine.load_bmp(filename)
        elif ext == ".raw":
            ok, img = mps_engine.load_raw(filename)
        else:
            messagebox.showerror("Error", f"Format belum didukung: {ext}")
            return

        if not ok:
            messagebox.showerror("Error", f"Gagal membuka file: {filename}")
            return

        self.undo_stack.clear()
        self.current_image = img
        self.original_image = self.clone_image(img)
        self.current_filename = filename
        
        self.display_image(img)
        self.update_info()

    # ---------- TAMPIL ----------
    def display_image(self, img):
        arr = img.to_numpy()

        if arr.ndim == 3 and arr.shape[2] == 1:
            arr = arr[:, :, 0]

        if arr.ndim == 2:
            if arr.max() > 0:
                arr_display = (arr.astype(np.float32) / arr.max() * 255).astype(np.uint8)
            else:
                arr_display = arr.astype(np.uint8)
        else:
            arr_display = arr.astype(np.uint8)

        pil_img = PILImage.fromarray(arr_display)

        self.canvas.update_idletasks()
        cw = max(self.canvas.winfo_width(), 1)
        ch = max(self.canvas.winfo_height(), 1)
        scale = min(cw / img.width, ch / img.height)
        if scale >= 1:
            scale = int(scale)
            resample = PILImage.NEAREST
        else:
            resample = PILImage.BILINEAR
        new_w = max(int(img.width * scale), 1)
        new_h = max(int(img.height * scale), 1)
        pil_img = pil_img.resize((new_w, new_h), resample)

        self.tk_image = ImageTk.PhotoImage(pil_img)

        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

    # ---------- SIMPAN ----------
    def save_file(self):
        if self.current_image is None:
            messagebox.showwarning("Peringatan", "Belum ada citra yang dibuka")
            return

        filename = filedialog.asksaveasfilename(
            title="Simpan Citra",
            defaultextension=".pgm",
            filetypes=[
                ("PGM files", "*.pgm"),
                ("PPM files", "*.ppm"),
                ("BMP files", "*.bmp"),
            ]
        )
        if not filename:
            return

        ext = os.path.splitext(filename)[1].lower()
        img = self.current_image

        if ext == ".pgm" and img.channels != 1:
            messagebox.showerror("Error", "PGM hanya untuk citra grayscale. Simpan sebagai PPM atau BMP.")
            return
        if ext == ".ppm" and img.channels != 3:
            messagebox.showerror("Error", "PPM hanya untuk citra berwarna. Simpan sebagai PGM atau BMP.")
            return

        if ext == ".pgm":
            ok = mps_engine.save_pgm(filename, img, True)
        elif ext == ".ppm":
            ok = mps_engine.save_ppm(filename, img, True)
        elif ext == ".bmp":
            ok = mps_engine.save_bmp(filename, img)
        else:
            messagebox.showerror("Error", f"Format belum didukung: {ext}")
            return

        if ok:
            messagebox.showinfo("Sukses", f"Berhasil simpan: {filename}")
        else:
            messagebox.showerror("Error", "Gagal menyimpan file")

    # ---------- OLAH CITRA ----------
    def apply_negative(self):
        if self.current_image is None:
            messagebox.showwarning("Peringatan", "Belum ada citra yang dibuka")
            return

        self.push_undo()
        self.current_image = mps_engine.make_negative(self.current_image)
        self.display_image(self.current_image)
        self.update_info()

    def apply_grayscale(self):
        if self.current_image is None:
            messagebox.showwarning("Peringatan", "Belum ada citra yang dibuka")
            return

        if self.current_image.channels == 1:
            messagebox.showinfo("Info", "Citra ini sudah grayscale/biner")
            return

        ok, result = mps_engine.to_grayscale(self.current_image)
        if not ok:
            messagebox.showerror("Error", "Gagal mengubah citra ke grayscale")
            return

        self.push_undo()
        self.current_image = result
        self.display_image(self.current_image)
        self.update_info()

    # ---------- BRIGHTENING DIALOG (SLIDER + PREVIEW) ----------
    def open_brightening_dialog(self):
        if self.current_image is None:
            messagebox.showwarning("Peringatan", "Belum ada citra yang dibuka")
            return

        base_image = self.clone_image(self.current_image)

        dialog = tk.Toplevel(self.root)
        dialog.title("Brightening (Real-time Preview)")
        dialog.geometry("350x180")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        val_var = tk.IntVar(value=0)

        # Fungsi pembaru preview
        def update_preview(*args):
            b_val = val_var.get()
            preview_img = self.clone_image(base_image)
            preview_img = mps_engine.brighten(preview_img, b_val)
            self.display_image(preview_img)

        # Header Label
        tk.Label(dialog, text="Atur Kecerahan Citra (-255 s/d 255):", font=("Helvetica", 9, "bold")).pack(pady=10)

        # Container Slider + Spinbox Input
        ctrl_frame = tk.Frame(dialog)
        ctrl_frame.pack(fill=tk.X, padx=15)

        slider = tk.Scale(
            ctrl_frame, from_=-255, to=255, orient=tk.HORIZONTAL,
            variable=val_var, command=lambda v: update_preview()
        )
        slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        spinbox = tk.Spinbox(
            ctrl_frame, from_=-255, to=255, textvariable=val_var,
            width=5, command=update_preview
        )
        spinbox.pack(side=tk.RIGHT)
        spinbox.bind("<Return>", lambda e: update_preview())

        # Tombol Apply dan Cancel
        def on_apply():
            self.push_undo()
            self.current_image = self.clone_image(base_image)
            self.current_image = mps_engine.brighten(self.current_image, val_var.get())
            self.display_image(self.current_image)
            self.update_info()
            dialog.destroy()

        def on_cancel():
            self.display_image(base_image)
            dialog.destroy()

        dialog.protocol("WM_DELETE_WINDOW", on_cancel)

        btn_frame = tk.Frame(dialog)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=15, padx=15)

        btn_cancel = tk.Button(btn_frame, text="Batal", command=on_cancel, width=10)
        btn_cancel.pack(side=tk.RIGHT, padx=(5, 0))

        btn_apply = tk.Button(btn_frame, text="Terapkan", command=on_apply, width=10, bg="#2b5b84", fg="white")
        btn_apply.pack(side=tk.RIGHT)

    def show_about(self):
        messagebox.showinfo("Tentang", "MiniPhotoshop\nEngine C++ + GUI Python")


if __name__ == "__main__":
    root = tk.Tk()
    app = MiniPhotoshopApp(root)
    root.mainloop()