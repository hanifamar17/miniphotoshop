import os
import tkinter as tk
from tkinter import filedialog, messagebox

import numpy as np
from PIL import Image as PILImage, ImageTk

import mps_engine


class FileIOMixin:
    # ---------- BUKA FILE ----------
    def open_file(self):
        filename = filedialog.askopenfilename(
            title="Buka Arsip Citra",
            filetypes=[
                ("Semua format didukung", "*.pbm *.pgm *.ppm *.bmp *.raw *.png *.jpg *.jpeg"),  # BARU: png jpg jpeg
                ("PBM files", "*.pbm"),
                ("PGM files", "*.pgm"),
                ("PPM files", "*.ppm"),
                ("BMP files", "*.bmp"),
                ("RAW files", "*.raw"),
                ("PNG files", "*.png"),         
                ("JPEG files", "*.jpg *.jpeg"), 
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
        elif ext == ".png":                              
            ok, img = mps_engine.load_png(filename)      
        elif ext in (".jpg", ".jpeg"):                   
            ok, img = mps_engine.load_jpg(filename)      
        else:
            messagebox.showerror("Error", f"Format belum didukung: {ext}")
            return

        if not ok:
            messagebox.showerror("Error", f"Gagal membuka file: {filename}")
            return

        self.undo_stack.clear()
        self.redo_stack.clear()
        self.current_image = img
        self.original_image = self.clone_image(img)
        self.current_filename = filename
        
        self.zoom_fit()
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

        scale = self.zoom_level
        resample = PILImage.NEAREST if scale >= 1 else PILImage.BILINEAR
        new_w = max(int(img.width * scale), 1)
        new_h = max(int(img.height * scale), 1)
        pil_img = pil_img.resize((new_w, new_h), resample)

        self.tk_image = ImageTk.PhotoImage(pil_img)

        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
        self.canvas.config(scrollregion=(0, 0, new_w, new_h))

    # ---------- SIMPAN ----------
    def save_file(self):
        if self.current_image is None:
            messagebox.showwarning("Peringatan", "Belum ada citra yang dibuka")
            return

        filename = filedialog.asksaveasfilename(
            title="Simpan Citra",
            defaultextension=".pgm",
            filetypes=[
                ("PBM files", "*.pbm"),
                ("PGM files", "*.pgm"),
                ("PPM files", "*.ppm"),
                ("BMP files", "*.bmp"),
                ("RAW files", "*.raw"),
                ("PNG files", "*.png"),         
                ("JPEG files", "*.jpg *.jpeg"), 
            ]
        )
        if not filename:
            return

        ext = os.path.splitext(filename)[1].lower()
        img = self.current_image

        if ext == ".pbm" and img.channels != 1:
            messagebox.showerror("Error", "PBM hanya untuk citra grayscale/biner. Simpan sebagai PPM atau BMP.")
            return
        if ext == ".pgm" and img.channels != 1:
            messagebox.showerror("Error", "PGM hanya untuk citra grayscale. Simpan sebagai PPM atau BMP.")
            return
        if ext == ".ppm" and img.channels != 3:
            messagebox.showerror("Error", "PPM hanya untuk citra berwarna. Simpan sebagai PGM atau BMP.")
            return
        if ext == ".raw" and img.channels != 1:
            messagebox.showerror("Error", "RAW hanya untuk citra grayscale. Simpan sebagai PPM atau BMP.")
            return

        if ext == ".pbm":
            ok = mps_engine.save_pbm(filename, img, True)
        elif ext == ".pgm":
            ok = mps_engine.save_pgm(filename, img, True)
        elif ext == ".ppm":
            ok = mps_engine.save_ppm(filename, img, True)
        elif ext == ".bmp":
            ok = mps_engine.save_bmp(filename, img)
        elif ext == ".raw":
            ok = mps_engine.save_raw(filename, img)
        elif ext == ".png":                              
            ok = mps_engine.save_png(filename, img)      
        elif ext in (".jpg", ".jpeg"):                   
            ok = mps_engine.save_jpg(filename, img)      
        else:
            messagebox.showerror("Error", f"Format belum didukung: {ext}")
            return

        if ok:
            messagebox.showinfo("Sukses", f"Berhasil simpan: {filename}")
        else:
            messagebox.showerror("Error", "Gagal menyimpan file")