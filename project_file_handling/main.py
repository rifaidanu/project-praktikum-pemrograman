"""
Program Utama Sistem Peminjaman Alat Laboratorium (versi File Handling .txt)
"""
import os
import sys

from services.lab_manager import LabManager
from data.dummy_data import inisialisasi_dummy_data
from fitur_program.menu_utama import tampilkan_menu_utama

# Folder tempat semua file .txt disimpan (di samping main.py)
FOLDER_DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data_txt")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")  # agar karakter khusus tidak error di console Windows

    lab = LabManager(FOLDER_DATA)

    if lab.muat_data():
        print(f"[INFO] Data dimuat dari folder {FOLDER_DATA}")
    else:
        # Pertama kali dijalankan: isi data contoh, otomatis tersimpan ke .txt
        inisialisasi_dummy_data(lab)
        print(f"[INFO] File data belum ada. Data contoh dibuat di {FOLDER_DATA}")

    tampilkan_menu_utama(lab)


if __name__ == "__main__":
    main()
