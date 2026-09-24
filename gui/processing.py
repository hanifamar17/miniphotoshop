import os
import tkinter as tk
from tkinter import messagebox

import numpy as np

import mps_engine


class ProcessingMixin:
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
            self.redo_stack.clear() 

    def undo(self):
        if not self.undo_stack:
            messagebox.showinfo("Undo", "Tidak ada riwayat perubahan lagi.")
            return

        self.redo_stack.append(self.clone_image(self.current_image))
        self.current_image = self.undo_stack.pop()
        self.display_image(self.current_image)
        self.update_info()

    def redo(self):
        if not self.redo_stack:
            messagebox.showinfo("Redo", "Tidak ada aksi untuk diulang.")
            return

        self.undo_stack.append(self.clone_image(self.current_image))
        self.current_image = self.redo_stack.pop()
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