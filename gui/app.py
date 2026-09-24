import os
import sys

# tambahkan folder build engine ke path, biar bisa import mps_engine
# (harus SEBELUM import view / file_io / processing)
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "engine", "build"))

import tkinter as tk

from view import ViewMixin
from file_io import FileIOMixin
from processing import ProcessingMixin


class MiniPhotoshopApp(ViewMixin, FileIOMixin, ProcessingMixin):
    pass


if __name__ == "__main__":
    root = tk.Tk()
    MiniPhotoshopApp(root)
    root.mainloop()