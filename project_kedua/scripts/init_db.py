"""Menyiapkan database: menjalankan database/schema.sql lalu database/seed.sql.

Cara pakai (dari folder project_kedua):
    python scripts/init_db.py            membuat tabel dan data dummy
    python scripts/init_db.py --reset    mengulang dari awal, khusus database pribadi dev_*

Database pribadi: isi DB_NAME=dev_<nama> di .env, script ini yang membuat databasenya.
"""
import os
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")  # agar emoji tidak error di console Windows

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from app.database import Database
from app.errors import DatabaseError

# Anak dulu, baru induk, karena FOREIGN KEY
URUTAN_HAPUS = ("detail_transaksi", "transaksi", "alat", "mahasiswa")


def siapkan_database_pribadi(nama):
    """Membuat database dev_* jika belum ada, lewat koneksi ke database bawaan."""
    os.environ["DB_NAME"] = "defaultdb"
    db = Database()
    terhubung = db.connect()
    os.environ["DB_NAME"] = nama
    if not terhubung:
        return False
    try:
        db.execute(f"CREATE DATABASE IF NOT EXISTS {nama}")  # nama sudah dicek regex
        return True
    except DatabaseError as e:
        print(f"❌ Gagal membuat {nama}: {e}")
        return False
    finally:
        db.close()


def jalankan_file_sql(db, path):
    """Memecah isi file berdasarkan ';' lalu menjalankannya satu per satu."""
    baris = [b for b in path.read_text(encoding="utf-8").splitlines()
             if not b.lstrip().startswith("--")]
    perintah = [p.strip() for p in "\n".join(baris).split(";") if p.strip()]
    for sql in perintah:
        db.execute(sql)
    print(f"✅ {path.name}: {len(perintah)} perintah dijalankan")


def main():
    nama = os.getenv("DB_NAME", "")
    pribadi = re.fullmatch(r"dev_[a-z0-9_]+", nama) is not None
    reset = "--reset" in sys.argv
    if reset and not pribadi:
        print(f"❌ --reset ditolak: '{nama}' bukan database pribadi dev_*.")
        return
    if pribadi and not siapkan_database_pribadi(nama):
        return
    db = Database()
    if not db.connect():
        return
    try:
        if reset:
            for tabel in URUTAN_HAPUS:
                db.execute(f"DROP TABLE IF EXISTS {tabel}")
            print(f"🗑  Tabel di {nama} dihapus")
        jalankan_file_sql(db, ROOT / "database" / "schema.sql")
        jalankan_file_sql(db, ROOT / "database" / "seed.sql")
        tabel = db.fetch_all("SHOW TABLES")
        print(f"📋 Tabel di {nama}:", [list(t.values())[0] for t in tabel])
    except DatabaseError as e:
        print(f"❌ Gagal: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
