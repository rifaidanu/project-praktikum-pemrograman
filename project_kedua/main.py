"""Titik masuk program. Jalankan dari folder project_kedua: python main.py"""
import sys

from app.database import Database
from app.menu_utama import MenuUtama


def main():
    sys.stdout.reconfigure(encoding="utf-8")  # agar emoji tidak error di console Windows
    db = Database()
    if not db.connect():
        return
    try:
        MenuUtama(db).jalankan()
    except (KeyboardInterrupt, EOFError):
        print()
    finally:
        db.close()
    print("Koneksi ditutup. Semua data sudah tersimpan di database.")


if __name__ == "__main__":
    main()
