import os
import tkinter as tk
from tkinter import messagebox

import numpy as np
import mps_engine


class ProcessingMixin:
    # ---------- HELPER STATUS BAR ----------
    def set_status(self, text):
        # Sesuaikan dengan status bar yang sudah ada di aplikasi.
        # Kalau tidak ada satupun atribut di bawah, tidak melakukan apa-apa.
        if hasattr(self, "status_var"):
            self.status_var.set(text)
        elif hasattr(self, "status_label"):
            self.status_label.config(text=text)

    # ---------- HELPER CLONE IMAGE ----------
    def clone_image(self, img):
        if img is None:
            return None
        # Memanggil brightening dengan nilai 0 untuk membuat salinan tanpa mengubah piksel
        return mps_engine.brighten(img, 0)

    # ---------- UNDO & REDO ----------
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
        self._update_history_ui()
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
        
        # Live update histogram
        self.hist_panel.update(self.current_image)

    # ---------- OLAH CITRA LAMA ----------
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

    # ---------- HISTOGRAM EQUALIZATION ----------
    def apply_equalize(self):
        if self.current_image is None:
            messagebox.showwarning("Peringatan", "Belum ada citra yang dibuka")
            return

        self.push_undo()  # wajib sebelum operasi; clone_image menyimpan salinan, jadi aman untuk in-place
        mps_engine.equalize_histogram(self.current_image)  # in-place, tidak return apa-apa
        self.display_image(self.current_image)
        self.update_info()
        self.set_status("Histogram equalization applied")

    # ---------- CONTRAST STRETCHING (MANUAL & OTOMATIS) ----------
    def process_manual_contrast(self, r1, s1, r2, s2):
        if self.current_image is None:
            return

        try:
            self.push_undo()
            self.current_image = mps_engine.contrast_stretching(self.current_image, r1, s1, r2, s2)
            self.display_image(self.current_image)
            self.update_info()
        except ValueError as e:
            messagebox.showerror("Error Engine", str(e))

    def process_auto_contrast(self, a, b):
        if self.current_image is None:
            return

        if self.current_image.channels == 3:
            messagebox.showwarning(
                "Peringatan", 
                "Auto contrast stretching belum mendukung citra RGB. Silakan konversi ke grayscale terlebih dahulu."
            )
            return

        try:
            self.push_undo()
            self.current_image = mps_engine.auto_contrast_stretching(self.current_image, a=a, b=b)
            self.display_image(self.current_image)
            self.update_info()
        except ValueError as e:
            messagebox.showerror("Error Engine", str(e))

    # ---------- OPERASI (LOG, INVERSE LOG, POWER, SLICING) ----------
    def process_log(self):
        if self.current_image is None:
            return
        self.push_undo()
        self.current_image = mps_engine.log_transform(self.current_image)
        self.display_image(self.current_image)
        self.update_info()

    def process_inverse_log(self):
        if self.current_image is None:
            return
        self.push_undo()
        self.current_image = mps_engine.inverse_log_transform(self.current_image)
        self.display_image(self.current_image)
        self.update_info()

    def process_power(self, gamma):
        if self.current_image is None:
            return
        self.push_undo()
        self.current_image = mps_engine.power_transform(self.current_image, gamma=gamma, c=1.0)
        self.display_image(self.current_image)
        self.update_info()

    def process_gray_slicing(self, a, b, preserve):
        if self.current_image is None:
            return
        if self.current_image.channels != 1:
            messagebox.showwarning("Peringatan", "Gray-level slicing hanya dapat diterapkan pada citra grayscale. Silakan konversi ke grayscale terlebih dahulu.")
            return

        self.push_undo()
        self.current_image = mps_engine.gray_slicing(self.current_image, a=a, b=b, preserve=preserve)
        self.display_image(self.current_image)
        self.update_info()

    def process_bit_plane(self, k, binary):
        if self.current_image is None:
            return
        if self.current_image.channels != 1:
            messagebox.showwarning("Peringatan", "Bit-plane slicing hanya dapat diterapkan pada citra grayscale. Silakan konversi ke grayscale terlebih dahulu.")
            return

        try:
            self.push_undo()
            self.current_image = mps_engine.bit_plane_slicing(self.current_image, k=k, binary=binary)
            self.display_image(self.current_image)
            self.update_info()
        except ValueError as e:
            messagebox.showerror("Error Engine", str(e))

    # ---------- FILTER ENGINE (NOISE, SMOOTHING, TEPI) ----------
    # Dipakai dialog preview di view.py. Semuanya fungsi murni: menerima citra,
    # mengembalikan citra hasil, TIDAK menyentuh current_image / undo / Tkinter,
    # jadi aman dipanggil dari thread. Engine yang in-place maupun yang return
    # citra baru sama-sama ditangani. Caller wajib clone_image() dulu.
    # Kalau nama/argumen di mps_engine berbeda, ubah di blok ini saja.
    @staticmethod
    def _engine_fn(*names):
        for n in names:
            fn = getattr(mps_engine, n, None)
            if fn is not None:
                return fn
        raise AttributeError("mps_engine tidak punya: " + " / ".join(names))

    @staticmethod
    def _engine_result(img, out):
        return img if out is None else out

    def filter_salt_pepper(self, img, prob, seed):
        fn = self._engine_fn("add_salt_pepper")
        return self._engine_result(img, fn(img, prob, seed))

    def filter_mean(self, img, ksize):
        fn = self._engine_fn("mean_filter", "mean_blur")
        return self._engine_result(img, fn(img, ksize))

    def filter_median(self, img, ksize):
        fn = self._engine_fn("median_filter")
        return self._engine_result(img, fn(img, ksize))

    def filter_gaussian(self, img, ksize, sigma):
        fn = self._engine_fn("gaussian_filter")
        return self._engine_result(img, fn(img, ksize, sigma))

    def filter_sobel(self, img, mode):
        fn = self._engine_fn("sobel", "sobel_edge", "sobel_edge_detection", "sobel_filter")
        return self._engine_result(img, fn(img, mode))

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