import sys
import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image as PILImage, ImageTk
import numpy as np

# tambahkan folder build engine ke path, biar bisa import mps_engine
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "engine", "build"))
import mps_engine


class MiniPhotoshopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MiniPhotoshop")
        self.root.geometry("800x600")

        self.current_image = None  # simpan Image object dari engine
        self.current_filename = None
        self.tk_image = None

        self._build_menu()
        self._build_canvas()

    def _build_canvas(self):
        self.canvas = tk.Canvas(self.root, bg="gray")
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def _build_menu(self):
        menubar = tk.Menu(self.root)

        # Menu Arsip
        menu_arsip = tk.Menu(menubar, tearoff=0)
        menu_arsip.add_command(label="Buka...", command=self.open_file)
        menu_arsip.add_command(label="Simpan...", command=self.save_file)
        menu_arsip.add_separator()
        menu_arsip.add_command(label="Keluar", command=self.root.quit)
        menubar.add_cascade(label="Arsip", menu=menu_arsip)

        # Menu Citra
        menu_citra = tk.Menu(menubar, tearoff=0)
        menu_citra.add_command(label="Info Citra", command=self.show_info)
        menubar.add_cascade(label="Citra", menu=menu_citra)

        # Menu Bantuan
        menu_bantuan = tk.Menu(menubar, tearoff=0)
        menu_bantuan.add_command(label="Tentang", command=self.show_about)
        menubar.add_cascade(label="Bantuan", menu=menu_bantuan)

        self.root.config(menu=menubar)

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
            return  # user cancel

        # pilih fungsi pembaca berdasarkan ekstensi file
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
            params = self._ask_raw_params()
            if params is None:
                return  # user cancel
            w, h, ch = params
            ok, img = mps_engine.load_raw(filename, w, h, ch)
        else:
            messagebox.showerror("Error", f"Format belum didukung: {ext}")
            return

        if not ok:
            messagebox.showerror("Error", f"Gagal membuka file: {filename}")
            return

        self.current_image = img
        self.current_filename = filename
        self.display_image(img)

    def _ask_raw_params(self):
        # RAW tidak punya header, jadi ukuran harus ditanyakan ke pengguna
        w = simpledialog.askinteger("RAW", "Lebar (px):", parent=self.root, minvalue=1)
        if w is None:
            return None
        h = simpledialog.askinteger("RAW", "Tinggi (px):", parent=self.root, minvalue=1)
        if h is None:
            return None
        ch = simpledialog.askinteger(
            "RAW", "Jumlah channel (1 = grayscale, 3 = RGB):",
            parent=self.root, minvalue=1, maxvalue=3
        )
        if ch is None:
            return None
        if ch not in (1, 3):
            messagebox.showerror("Error", "Channel harus 1 atau 3")
            return None
        return w, h, ch

    # ---------- TAMPIL ----------
    def display_image(self, img):
        arr = img.to_numpy()

        # jaga-jaga kalau bentuknya (h, w, 1), ubah jadi (h, w)
        if arr.ndim == 3 and arr.shape[2] == 1:
            arr = arr[:, :, 0]

        if arr.ndim == 2:
            # grayscale/biner: normalisasi ke 0-255 seperti sebelumnya
            if arr.max() > 0:
                arr_display = (arr.astype(np.float32) / arr.max() * 255).astype(np.uint8)
            else:
                arr_display = arr.astype(np.uint8)
        else:
            # berwarna (h, w, 3): tampilkan apa adanya
            arr_display = arr.astype(np.uint8)

        pil_img = PILImage.fromarray(arr_display)

        # zoom otomatis: muat di dalam area canvas
        self.canvas.update_idletasks()
        cw = max(self.canvas.winfo_width(), 1)
        ch = max(self.canvas.winfo_height(), 1)
        scale = min(cw / img.width, ch / img.height)
        if scale >= 1:
            scale = int(scale)  # citra kecil: perbesar kelipatan bulat
            resample = PILImage.NEAREST
        else:
            resample = PILImage.BILINEAR  # citra besar: perkecil halus
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

        # cocokkan format dengan jumlah channel
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

    # ---------- INFO ----------
    def show_info(self):
        if self.current_image is None:
            messagebox.showwarning("Peringatan", "Belum ada citra yang dibuka")
            return

        img = self.current_image

        # ukuran file di disk, dalam byte
        file_size = os.path.getsize(self.current_filename)
        format_file = os.path.splitext(self.current_filename)[1].upper().lstrip(".")

        # tentukan jenis citra
        arr = img.to_numpy()
        if img.channels == 3:
            jenis = "Berwarna (RGB)"
        elif np.isin(arr, (0, 255)).all():
            jenis = "Biner (hitam-putih)"
        else:
            jenis = "Grayscale"

        info = (
            f"File       : {self.current_filename}\n"
            f"Format     : {format_file}\n"
            f"Ukuran     : {img.width} x {img.height} px\n"
            f"Channels   : {img.channels}\n"
            f"Jenis      : {jenis}\n"
            f"Ukuran file: {file_size} byte ({file_size / 1024:.2f} KB)"
        )
        messagebox.showinfo("Info Citra", info)

    def show_about(self):
        messagebox.showinfo("Tentang", "MiniPhotoshop\nEngine C++ + GUI Python")


if __name__ == "__main__":
    root = tk.Tk()
    app = MiniPhotoshopApp(root)
    root.mainloop()