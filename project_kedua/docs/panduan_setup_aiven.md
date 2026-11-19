# 🛠 Panduan Setup Database Online (Aiven for MySQL)

Panduan ini membawa kelompok dari **membuat database di Aiven** sampai **program Python berhasil terkoneksi**. Ikuti berurutan.

| Langkah | Dikerjakan oleh | Perkiraan waktu |
|---|---|---|
| 1–3. Buat akun, service, dan database | **1 orang** (admin database) | 10 menit |
| 4. Bagikan detail koneksi | Admin database | 2 menit |
| 5–8. Setup di laptop, tes koneksi, buat tabel | **Setiap anggota** (langkah 8 cukup sekali) | 10 menit |

> ⚠️ Tampilan dashboard Aiven bisa sedikit berubah dari waktu ke waktu. Kalau nama tombol berbeda, cari menu yang artinya sama.

---

## 1. Buat akun Aiven *(admin database saja)*

1. Buka **https://console.aiven.io/signup**.
2. Daftar dengan email atau akun Google/GitHub.
3. Verifikasi email, lalu login. Tidak perlu memasukkan kartu kredit untuk paket gratis.

## 2. Buat service MySQL *(admin database saja)*

1. Di dashboard, klik **Create service**.
2. Pilih **MySQL**.
3. Pilih paket **Free** (gratis).
4. Pilih region yang tersedia (pilih yang paling dekat dengan Indonesia jika ada, misal Singapura).
5. Beri nama service, misal `lab-peminjaman`.
6. Klik **Create service**, lalu tunggu sampai statusnya berubah dari *Rebuilding* menjadi **Running** (beberapa menit).

## 3. Catat detail koneksi *(admin database saja)*

Buka service yang baru dibuat, lalu lihat bagian **Connection information**. Catat:

| Informasi | Contoh | Masuk ke `.env` sebagai |
|---|---|---|
| Host | `lab-peminjaman-xxxx.aivencloud.com` | `DB_HOST` |
| Port | `12345` (bukan 3306) | `DB_PORT` |
| User | `avnadmin` | `DB_USER` |
| Password | `AVNS_xxxxxxxx` (klik ikon mata untuk melihat) | `DB_PASSWORD` |
| Database | `defaultdb` | `DB_NAME` |
| SSL mode | `REQUIRED` | — |

Di halaman yang sama ada tombol untuk mengunduh **CA certificate** (`ca.pem`). Unduh dan simpan, karena akan dipakai jika muncul error SSL.

> 💡 Database bawaan bernama `defaultdb` sudah bisa langsung dipakai. Kalian **tidak wajib** membuat database baru. Panduan ini memakai `defaultdb` supaya sederhana.

## 4. Bagikan detail koneksi ke anggota *(admin database)*

- Kirim isi `.env` (langkah 5) dan file `ca.pem` lewat **chat pribadi/grup kelompok**, misal WhatsApp.
- ❌ **Jangan** kirim lewat repo GitHub, issue, atau README. Siapa pun yang tahu password bisa menghapus semua data.
- Anggota lain **tidak perlu** membuat akun Aiven.

---

## 5. Siapkan project di laptop *(setiap anggota)*

### 5.1 Install library

```bash
pip install mysql-connector-python python-dotenv
```

Tambahkan juga ke `requirements.txt` di root repo:

```text
mysql-connector-python
python-dotenv
```

### 5.2 Buat file `.env` (rahasia, tidak di-commit)

Di root repo, buat file bernama `.env`:

```text
DB_HOST=lab-peminjaman-xxxx.aivencloud.com
DB_PORT=12345
DB_USER=avnadmin
DB_PASSWORD=AVNS_xxxxxxxx
DB_NAME=defaultdb
DB_SSL_CA=
```

`DB_SSL_CA` boleh dikosongkan dulu. Isi dengan path ke `ca.pem` hanya jika muncul error SSL (lihat bagian Troubleshooting).

### 5.3 Buat `.env.example` (boleh di-commit)

Salinan `.env` **tanpa nilai rahasia**, supaya anggota tahu variabel apa saja yang dibutuhkan:

```text
DB_HOST=
DB_PORT=
DB_USER=
DB_PASSWORD=
DB_NAME=defaultdb
DB_SSL_CA=
```

### 5.4 Pastikan `.env` diabaikan Git

Buat atau tambahkan ke file `.gitignore`:

```text
.env
*.pem
__pycache__/
```

Cek dengan `git status`. File `.env` **tidak boleh** muncul di daftar file yang akan di-commit.

> 🚨 Kalau password terlanjur ter-push ke GitHub: segera **reset password** di dashboard Aiven (menu user `avnadmin`), lalu bagikan password baru ke anggota. Menghapus file dari repo saja tidak cukup karena masih ada di histori commit.

---

## 6. Buat class `Database` *(dikerjakan 1 anggota, dipakai semua)*

Ini adalah **satu pintu** akses database (lihat bagian 2 dan 11 di `project_instruction.md`). Semua menu memanggil method class ini, tidak ada SQL di file menu.

Contoh lokasi: `app/database.py` (sesuaikan dengan struktur folder kelompok).

```python
"""Satu pintu akses ke database MySQL online."""
import os

import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()  # membaca file .env di root repo


class Database:
    """Mengelola koneksi, query, dan transaction ke MySQL."""

    def __init__(self):
        self.conn = None

    def connect(self):
        """Membuka koneksi. Mengembalikan True jika berhasil, False jika gagal."""
        try:
            config = {
                "host": os.getenv("DB_HOST"),
                "port": int(os.getenv("DB_PORT", "3306")),
                "user": os.getenv("DB_USER"),
                "password": os.getenv("DB_PASSWORD"),
                "database": os.getenv("DB_NAME"),
                "connection_timeout": 10,
            }
            ssl_ca = os.getenv("DB_SSL_CA")
            if ssl_ca:
                config["ssl_ca"] = ssl_ca
            self.conn = mysql.connector.connect(**config)
            return True
        except (Error, ValueError) as e:
            print(f"⚠️ Gagal terhubung ke database: {e}")
            return False

    def _pastikan_terhubung(self):
        """Menyambung ulang jika koneksi terputus karena lama tidak dipakai."""
        self.conn.ping(reconnect=True, attempts=3, delay=1)

    def fetch_all(self, sql, params=()):
        """SELECT banyak baris. Hasil: list of dict, misal [{'kode': 'A001', ...}]."""
        self._pastikan_terhubung()
        cur = self.conn.cursor(dictionary=True)
        try:
            cur.execute(sql, params)
            return cur.fetchall()
        finally:
            cur.close()

    def fetch_one(self, sql, params=()):
        """SELECT satu baris. Hasil: dict, atau None jika tidak ada."""
        self._pastikan_terhubung()
        cur = self.conn.cursor(dictionary=True)
        try:
            cur.execute(sql, params)
            return cur.fetchone()
        finally:
            cur.close()

    def execute(self, sql, params=()):
        """INSERT/UPDATE/DELETE satu perintah, langsung commit."""
        return self.run_transaction([(sql, params)])

    def run_transaction(self, langkah):
        """Menjalankan beberapa perintah sebagai SATU transaction.

        langkah: list of (sql, params).
        Semua berhasil -> commit. Satu gagal -> rollback semua, lalu error diteruskan.
        """
        self._pastikan_terhubung()
        cur = self.conn.cursor()
        try:
            for sql, params in langkah:
                cur.execute(sql, params)
            self.conn.commit()
            return cur.rowcount
        except Error:
            self.conn.rollback()
            raise
        finally:
            cur.close()

    def close(self):
        """Menutup koneksi. Panggil saat user memilih menu Keluar."""
        if self.conn and self.conn.is_connected():
            self.conn.close()
```

### Contoh pemakaian

```python
db = Database()
if not db.connect():
    exit()

# SELECT, selalu pakai %s, JANGAN f-string
alat = db.fetch_one("SELECT * FROM alat WHERE kode = %s", ("A001",))
tersedia = db.fetch_all("SELECT * FROM alat WHERE status = %s", ("tersedia",))

# INSERT satu baris
db.execute(
    "INSERT INTO mahasiswa (nim, nama, no_hp, status_aktif) VALUES (%s, %s, %s, %s)",
    ("M002", "Budi Santoso", "081298765432", "aktif"),
)

# Peminjaman: beberapa tabel sekaligus dalam SATU transaction
db.run_transaction([
    ("INSERT INTO transaksi (id, nim, tgl_pinjam, batas_kembali, status) VALUES (%s, %s, %s, %s, %s)",
     ("T002", "M002", "2026-11-19", "2026-11-26", "dipinjam")),
    ("INSERT INTO detail_transaksi (id_transaksi, kode_alat, status) VALUES (%s, %s, %s)",
     ("T002", "A001", "dipinjam")),
    ("UPDATE alat SET status = %s WHERE kode = %s", ("dipinjam", "A001")),
])

db.close()
```

> ✅ Benar: `cur.execute("... WHERE kode = %s", (kode,))`, perhatikan koma pada `(kode,)` karena params harus tuple.
> ❌ Salah: `cur.execute(f"... WHERE kode = '{kode}'")`, rawan SQL injection dan error jika input berisi tanda kutip.

---

## 7. Tes koneksi *(setiap anggota)*

Buat file `scripts/tes_koneksi.py`:

```python
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
```

Jalankan dari root repo:

```bash
python scripts/tes_koneksi.py
```

Jika muncul `✅ Terhubung!`, setup di laptop kamu sudah benar. Jika muncul ⚠️, lihat bagian Troubleshooting.

---

## 8. Buat tabel *(cukup sekali, oleh 1 orang)*

Karena database-nya **dipakai bersama**, tabel cukup dibuat satu kali oleh satu orang. Anggota lain langsung bisa memakai.

### Cara A: lewat aplikasi GUI (disarankan, mirip phpMyAdmin)

1. Install **DBeaver Community** atau **MySQL Workbench**.
2. Buat koneksi baru → MySQL → isi Host, Port, User, Password, Database sesuai `.env`.
3. Di pengaturan SSL, aktifkan **Use SSL** (pilih file `ca.pem` jika diminta).
4. Buka SQL editor, tempel isi `database/schema.sql` (contoh ada di `project_instruction.md` bagian 3.1), lalu jalankan.
5. Jalankan juga `database/seed.sql` untuk data contoh.

### Cara B: lewat script Python

Buat file `scripts/init_db.py`:

```python
"""Menjalankan database/schema.sql lalu database/seed.sql ke database online."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from app.database import Database


def jalankan_file_sql(db, path):
    isi = path.read_text(encoding="utf-8")
    perintah = [p.strip() for p in isi.split(";") if p.strip()]
    db.run_transaction([(sql, ()) for sql in perintah])
    print(f"✅ {path.name}: {len(perintah)} perintah dijalankan")


db = Database()
if db.connect():
    jalankan_file_sql(db, ROOT / "database" / "schema.sql")
    jalankan_file_sql(db, ROOT / "database" / "seed.sql")
    db.close()
```

> Script ini memecah perintah berdasarkan `;`, jadi jangan tulis `;` di dalam teks data atau komentar SQL. Gunakan `CREATE TABLE IF NOT EXISTS` di `schema.sql` supaya aman jika dijalankan ulang.

---

## 9. 🩺 Troubleshooting

| Pesan error (potongan) | Penyebab umum | Solusi |
|---|---|---|
| `2003: Can't connect to MySQL server` | Service Aiven sedang **mati/powered off**, host/port salah, atau internet bermasalah | Login ke dashboard Aiven, nyalakan service (**Power on**), tunggu status *Running*. Cek ulang host dan port di `.env` |
| `1045: Access denied for user` | Password atau user salah | Salin ulang password dari dashboard, pastikan tidak ada spasi di `.env` |
| Error berisi `SSL` / `certificate` | Library tidak bisa memverifikasi SSL | Isi `DB_SSL_CA=` dengan path lengkap ke `ca.pem`, misal `DB_SSL_CA=D:/kuliah/ca.pem` |
| `1049: Unknown database` | Nama database di `.env` salah | Pakai `defaultdb`, atau buat dulu database dengan nama yang kamu tulis |
| `1146: Table ... doesn't exist` | Tabel belum dibuat | Jalankan langkah 8 |
| `1062: Duplicate entry` | PK sudah ada (NIM/kode/ID ganda) | Normal untuk input duplikat. Tangkap dengan `try-except` dan tampilkan pesan ramah |
| `1451` / `1452: foreign key constraint fails` | Hapus data yang masih dirujuk, atau insert dengan NIM/kode yang tidak ada | Validasi dulu di program. Urutan insert: mahasiswa & alat sebelum transaksi |
| `2013: Lost connection` / `2055` | Koneksi terputus karena lama diam | Sudah ditangani `_pastikan_terhubung()`. Jika masih terjadi, jalankan ulang program |
| `UnicodeEncodeError: 'charmap' codec can't encode` | Console Windows tidak bisa menampilkan emoji | Tambahkan `sys.stdout.reconfigure(encoding="utf-8")` di awal file yang dijalankan (`main.py`, script) |
| `2003 ... (10060)` dengan port `12345` | Port masih angka contoh dari panduan | Ganti `DB_PORT` dengan port asli dari dashboard Aiven |
| `ModuleNotFoundError: No module named 'mysql'` | Library belum terinstall di Python yang dipakai | `python -m pip install mysql-connector-python python-dotenv` |
| `ModuleNotFoundError: No module named 'app'` | Script dijalankan dari folder yang salah | Jalankan dari root repo: `python scripts/tes_koneksi.py` |
| Nilai dari `.env` terbaca `None` | File `.env` tidak di root, atau salah nama (misal `.env.txt`) | Pastikan nama file persis `.env` dan berada di folder tempat program dijalankan |

---

## 10. ✅ Checklist kelompok

- [ ] Service Aiven berstatus **Running**
- [ ] Detail koneksi sudah dibagikan ke semua anggota lewat jalur pribadi
- [ ] Setiap anggota punya `.env` sendiri dan **tidak ter-commit**
- [ ] `.env.example`, `.gitignore`, dan `requirements.txt` sudah ada di repo
- [ ] `scripts/tes_koneksi.py` berhasil di laptop **semua anggota**
- [ ] Tabel dan data contoh sudah dibuat (langkah 8)
- [ ] Sebelum demo/presentasi: cek dashboard Aiven, pastikan service **tidak dalam keadaan mati**
