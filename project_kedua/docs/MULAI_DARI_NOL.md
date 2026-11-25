# Mulai dari Nol

Panduan ini membawa kamu dari laptop kosong sampai mulai mengerjakan fitur. Ikuti berurutan, sekitar 30 menit. Perintah ditulis untuk **PowerShell** di Windows.

Database Aiven sudah dibuat, jadi kamu **tidak perlu** mendaftar Aiven.

## Pembagian

| Anggota | Paket | Folder | Menu |
|---|---|---|---|
| Tama | 1 | `app/fitur/mahasiswa/` | 1 Kelola mahasiswa, 10 Riwayat mahasiswa |
| Diah | 2 | `app/fitur/alat/` | 2 Kelola alat, 7 Tersedia, 8 Dipinjam, 9 Rusak |
| Danu | 3 | `app/fitur/peminjaman/` | 3 Buat transaksi, 4 Tampilkan transaksi |
| Vicko | 4 | `app/fitur/pengembalian/` | 5 Pengembalian, 6 Cari transaksi |

---

## 1. Siapkan alat

| Alat | Cek dengan | Kalau belum ada |
|---|---|---|
| Python 3.10 ke atas | `python --version` | https://www.python.org/downloads/ (centang **Add Python to PATH**) |
| Git | `git --version` | https://git-scm.com/download/win |
| VS Code | — | https://code.visualstudio.com/ |

Atur identitas Git dengan email **akun GitHub kamu sendiri**, supaya commit tercatat sebagai kontribusimu:

```powershell
git config --global user.name "Nama Kamu"
git config --global user.email "email-github-kamu@contoh.com"
```

## 2. Ambil project

Pastikan kamu sudah menjadi collaborator di repo, lalu:

```powershell
git clone https://github.com/Danu-Rifai/praktikumPemrograman.git
cd praktikumPemrograman\project_kedua
```

Sudah pernah clone? Masuk ke folder repo, jalankan `git switch main` lalu `git pull`, kemudian `cd project_kedua`.

> Semua perintah berikutnya dijalankan dari folder **`project_kedua`**.

## 3. Install library

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Kalau berhasil, muncul `(.venv)` di awal baris terminal. Aktifkan lagi dengan baris kedua setiap kali membuka terminal baru.

Muncul error *running scripts is disabled*? Jalankan ini dulu, lalu ulangi aktivasi:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
```

## 4. Sambungkan ke database

1. Minta **isi `.env`** dan **file `ca.pem`** ke Danu lewat chat pribadi.
2. Simpan `ca.pem` di folder `project_kedua`.
3. Salin contoh konfigurasi:

   ```powershell
   Copy-Item .env.example .env
   ```

4. Buka `.env` di VS Code, isi dengan data dari Danu, tetapi **ganti `DB_NAME`** menjadi database pribadimu:

   ```text
   DB_HOST=(dari Danu)
   DB_PORT=(dari Danu)
   DB_USER=(dari Danu)
   DB_PASSWORD=(dari Danu)
   DB_NAME=dev_tama
   DB_SSL_CA=ca.pem
   ```

   Pakai `dev_tama`, `dev_diah`, `dev_danu`, atau `dev_vicko`. Huruf kecil, tanpa spasi.

5. Pastikan file rahasia tidak ikut ke GitHub:

   ```powershell
   git check-ignore .env ca.pem
   ```

   Kedua nama file harus muncul. Kalau tidak, **jangan commit**, tanyakan di grup.

> **Kenapa database pribadi?** Kamu bebas menambah dan menghapus data tanpa mengganggu yang lain. Database bersama (`defaultdb`) dipakai saat semua fitur digabung.

## 5. Buat database pribadi dan isi data dummy

```powershell
python scripts/init_db.py
```

Hasil yang benar:

```text
✅ schema.sql: 4 perintah dijalankan
✅ seed.sql: 4 perintah dijalankan
📋 Tabel di dev_tama: ['alat', 'detail_transaksi', 'mahasiswa', 'transaksi']
```

Isinya 6 mahasiswa, 10 alat, dan 5 transaksi. Datamu berantakan saat mencoba-coba? Ulang dari awal:

```powershell
python scripts/init_db.py --reset
```

## 6. Tes koneksi dan jalankan program

```powershell
python scripts/tes_koneksi.py
python main.py
```

Perintah pertama harus menampilkan `✅ Terhubung!`. Perintah kedua membuka menu utama. Coba salah satu menu milikmu: kalau muncul `Fitur belum dikerjakan -> Paket ...`, **setup kamu selesai**.

## 7. (Opsional) Lihat isi tabel

Pakai DataGrip atau DBeaver: buat koneksi MySQL, isi Host, Port, User, Password sesuai `.env`, Database `dev_namamu`, lalu aktifkan SSL dengan CA file `ca.pem`.

---

## 8. Mulai mengerjakan

### 8.1 Buat branch

```powershell
git switch main
git pull
git switch -c fitur/paket-1
```

Ganti angkanya sesuai paketmu.

### 8.2 Kenali tiga file di folder paketmu

Alurnya: **menu** (input dan tampilan) → **service** (aturan bisnis) → **repository** (SQL) → database.

Kerjakan dari belakang: `repository.py`, lalu `service.py`, lalu `menu.py`. Tiap method sudah berisi petunjuk. Hapus baris `raise NotImplementedError(...)` setelah method diisi.

Mulai dari yang paling mudah, supaya pola kerjanya terasa dulu:

| Anggota | Mulai dari | Lanjut ke | Terakhir |
|---|---|---|---|
| Tama | Cari mahasiswa | Riwayat, Tambah, Edit | Hapus |
| Diah | Alat tersedia (menu 7) | Rusak, Dipinjam, Cari, Tambah | Edit, Hapus |
| Danu | Tampilkan transaksi (menu 4) | Validasi di `service.buat_transaksi` | `repository.simpan` dan menu 3 |
| Vicko | Cari transaksi (menu 6) | Validasi di `service.kembalikan` | `repository.simpan` dan menu 5 |

### 8.3 Contoh mengisi satu method

Contoh ini memakai fitur karangan "daftar kategori", tidak ada di paket siapa pun. Perhatikan polanya.

```python
# repository.py: hanya SQL
def daftar_kategori(self):
    return self._db.fetch_all(
        "SELECT kategori, COUNT(*) AS jumlah FROM alat"
        " WHERE dihapus = %s GROUP BY kategori ORDER BY kategori",
        (False,),
    )
```

```python
# service.py: hanya aturan. Di atas file: from app.errors import AturanBisnisError
def daftar_kategori(self):
    daftar = self._repository.daftar_kategori()
    if not daftar:
        raise AturanBisnisError("Belum ada alat.")
    return daftar
```

```python
# menu.py: hanya input dan tampilan
def tampilkan_kategori(self):
    daftar = self._service.daftar_kategori()
    ui.tabel(["Kategori", "Jumlah"], [[d["kategori"], d["jumlah"]] for d in daftar])
```

Error tidak perlu ditangkap di `menu.py`, karena `ui.jalankan_aksi` sudah menampilkannya.

Fungsi yang sudah tersedia (`self._db`, `self._pembaca`, `ui`) dan aturan penulisan ada di [PANDUAN_PENGEMBANGAN.md](PANDUAN_PENGEMBANGAN.md) bagian 5 dan 6. **Baca bagian itu sebelum menulis SQL pertama.**

### 8.4 Coba

Jalankan `python main.py`. Coba juga kasus yang **harus ditolak**. Daftar lengkap per paket ada di [PANDUAN_PENGEMBANGAN.md](PANDUAN_PENGEMBANGAN.md) bagian 7.

### 8.5 Simpan dan kirim

```powershell
git status
git add app/fitur/mahasiswa
git commit -m "feat: cari mahasiswa"
git push -u origin fitur/paket-1
```

Ganti nama folder dan branch sesuai paketmu. Commit kecil tetapi sering, misalnya satu commit per fitur. Setelah itu buka repo di GitHub dan buat **Pull Request** ke `main`.

Hanya ubah file di folder paketmu. Perlu mengubah file lain? Bicarakan dulu di grup.

## 9. Setelah semua paket digabung

1. `git switch main` lalu `git pull`.
2. Ubah `DB_NAME=defaultdb` di `.env`.
3. Jalankan `python main.py` dan uji bersama: data yang ditambah satu anggota harus terlihat di laptop anggota lain.

---

## Kalau ada masalah

| Pesan | Solusi |
|---|---|
| `2003: Can't connect` | Minta Danu mengecek service di dashboard Aiven (mungkin sedang mati). Cek juga internet, `DB_HOST`, dan `DB_PORT` |
| `1045: Access denied` | Salin ulang `DB_USER` dan `DB_PASSWORD`, pastikan tanpa spasi |
| `1049: Unknown database` | Jalankan `python scripts/init_db.py` dulu |
| `1146: Table ... doesn't exist` | Jalankan `python scripts/init_db.py` |
| Error berisi `SSL` | Pastikan `ca.pem` ada di `project_kedua` dan `DB_SSL_CA=ca.pem` |
| `--reset ditolak` | `DB_NAME` kamu bukan `dev_...`. Ini pengaman supaya data bersama tidak terhapus |
| `No module named 'mysql'` atau `'dotenv'` | Aktifkan `.venv`, lalu `python -m pip install -r requirements.txt` |
| `can't open file ... main.py` | Terminal belum berada di folder `project_kedua` |
| `.env` seperti tidak terbaca | Pastikan namanya persis `.env`, bukan `.env.txt` |
| `Unknown column 'aktif'` | Teks di SQL harus memakai kutip tunggal: `'aktif'` |

Error lain soal Aiven ada di [panduan_setup_aiven.md](panduan_setup_aiven.md) bagian 9.

## Checklist siap kerja

- [ ] `git config user.email` sama dengan email akun GitHub
- [ ] `git check-ignore .env ca.pem` menampilkan kedua file
- [ ] `DB_NAME` memakai `dev_namamu`
- [ ] `python scripts/init_db.py` menampilkan 4 tabel
- [ ] `python scripts/tes_koneksi.py` menampilkan `✅ Terhubung!`
- [ ] `python main.py` membuka menu
- [ ] Sudah di branch `fitur/paket-...`
