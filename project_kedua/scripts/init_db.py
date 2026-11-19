"""Menjalankan database/schema.sql lalu database/seed.sql ke database online.

Cara pakai (dari folder project_kedua):
    python scripts/init_db.py
File yang belum ada akan dilewati.
"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")  # agar emoji tidak error di console Windows

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from mysql.connector import Error

from app.database import Database


def jalankan_file_sql(db, path):
    """Memecah isi file berdasarkan ';' lalu menjalankannya dalam satu transaction."""
    if not path.exists():
        print(f"⏭  {path.name} belum ada, dilewati")
        return
    isi = path.read_text(encoding="utf-8")
    perintah = [p.strip() for p in isi.split(";") if p.strip()]
    db.run_transaction([(sql, ()) for sql in perintah])
    print(f"✅ {path.name}: {len(perintah)} perintah dijalankan")


db = Database()
if db.connect():
    try:
        jalankan_file_sql(db, ROOT / "database" / "schema.sql")
        jalankan_file_sql(db, ROOT / "database" / "seed.sql")
        tabel = db.fetch_all("SHOW TABLES")
        print("📋 Tabel di database:", [list(t.values())[0] for t in tabel])
    except Error as e:
        print(f"❌ Gagal: {e}")
    finally:
        db.close()
