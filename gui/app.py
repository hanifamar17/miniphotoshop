import sys
import os
import tkinter as tk
from tkinter import filedialog, messagebox
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
        self.current_filename= None
        self.tk_image= None

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

   def open_file(self):
        filename = filedialog.askopenfilename(
            title="Buka Arsip Citra",
            filetypes=[
                ("Semua format didukung", "*.pbm *.pgm"),
                ("PBM files", "*.pbm"),
                ("PGM files", "*.pgm"),
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
        else:
            messagebox.showerror("Error", f"Format belum didukung: {ext}")
            return

        if not ok:
            messagebox.showerror("Error", f"Gagal membuka file: {filename}")
            return

        self.current_image = img
        self.current_filename = filename
        self.display_image(img)

    def display_image(self, img):
        arr = img.to_numpy()
        if arr.max() > 0:
            arr_display= (arr.astype(np.float32)/arr.max() * 255).astype(np.uint8)
        else:
            arr_display= arr

        pil_img= PILImage.fromarray(arr_display)
        scale= 10
        display_size= (img.width * scale, img.height * scale)
        pill_img_display= pil_img.resize(display_size, PILImage.NEAREST)

        self.tk_image = ImageTk.PhotoImage(pill_img_display)

        self.canvas.delete("all")
        self.canvas.config(width=img.width, height=img.height)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

    def save_file(self):
        if self.current_image is None:
            messagebox.showwarning("Peringatan", "Belum ada citra yang dibuka")
            return

        filename = filedialog.asksaveasfilename(
            title="Simpan Citra",
            defaultextension=".pgm",
            filetypes=[("PGM files", "*.pgm")]
        )
        if not filename:
            return

        ok = mps_engine.save_pgm(filename, self.current_image, True)
        if ok:
            messagebox.showinfo("Sukses", f"Berhasil simpan: {filename}")
        else:
            messagebox.showerror("Error", "Gagal menyimpan file")

    def show_info(self):
        if self.current_image is None:
            messagebox.showwarning("Peringatan", "Belum ada citra yang dibuka")
            return

        img = self.current_image

        # ukuran file di disk, dalam byte
        file_size = os.path.getsize(self.current_filename)

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