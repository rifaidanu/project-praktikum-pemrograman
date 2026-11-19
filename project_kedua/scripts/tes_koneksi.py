import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")  # agar emoji tidak error di console Windows
sys.path.append(str(Path(__file__).resolve().parent.parent))  # agar folder app terbaca

from app.database import Database

db = Database()
if db.connect():
    versi = db.fetch_one("SELECT VERSION() AS versi")
    print(f"✅ Terhubung! Versi MySQL: {versi['versi']}")
    db.close()
