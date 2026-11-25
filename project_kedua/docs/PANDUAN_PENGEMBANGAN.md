# Panduan Pengembangan Fitur

Fondasi sudah jadi, fitur masih kosong. Tiap anggota mengerjakan satu paket di foldernya sendiri, dan tidak ada paket yang menunggu paket lain.

## 1. Pembagian paket

| Paket | Folder | Menu | Anggota |
|---|---|---|---|
| 1 | `app/fitur/mahasiswa/` | 1 Kelola mahasiswa, 10 Riwayat mahasiswa | Tama |
| 2 | `app/fitur/alat/` | 2 Kelola alat, 7 Tersedia, 8 Dipinjam, 9 Rusak | Diah |
| 3 | `app/fitur/peminjaman/` | 3 Buat transaksi, 4 Tampilkan transaksi | Danu |
| 4 | `app/fitur/pengembalian/` | 5 Pengembalian, 6 Cari transaksi | Vicko |

## 2. Struktur program

```text
project_kedua/
├── main.py                  titik masuk program
├── app/
│   ├── database.py          fondasi: koneksi, query, transaction
│   ├── errors.py            fondasi: AturanBisnisError, DatabaseError, DataGandaError
│   ├── models/              fondasi: Mahasiswa, Alat, Transaksi, ItemPeminjaman, enum
│   ├── pembaca_data.py      fondasi: pembacaan data lintas fitur
│   ├── ui.py                fondasi: input, tabel, menu
│   ├── menu_utama.py        fondasi: merakit semua fitur
│   └── fitur/
│       ├── mahasiswa/       Paket 1
│       ├── alat/            Paket 2
│       ├── peminjaman/      Paket 3
│       └── pengembalian/    Paket 4
├── database/                schema.sql dan seed.sql
└── scripts/                 tes_koneksi.py dan init_db.py
```

Setiap paket berisi tiga file:

| File | Tugas | Tidak boleh |
|---|---|---|
| `menu.py` | `input`, `print`, memanggil service | SQL, aturan bisnis |
| `service.py` | Memeriksa aturan bisnis, memanggil repository | SQL, `input`, `print` |
| `repository.py` | SQL | `input`, `print` |

Aturan yang bisa bentrok antarkomputer (batas 2 transaksi, alat tersedia) diperiksa lagi di `repository.py`, di dalam transaction.

## 3. Persiapan

Ikuti [MULAI_DARI_NOL.md](MULAI_DARI_NOL.md) sampai bagian 6.

Data dummy sudah berisi transaksi, jadi Paket 4 tidak perlu menunggu Paket 3.

## 4. Cara mengerjakan

1. Buat branch: `git switch -c fitur/paket-1`.
2. Isi `repository.py` dulu, lalu `service.py`, lalu `menu.py`. Petunjuknya ada di tiap method.
3. Hapus baris `raise NotImplementedError(...)` pada method yang sudah diisi.
4. Coba lewat `python main.py`, termasuk kasus yang harus ditolak.
5. Commit dan push dari akun GitHub sendiri, lalu buat pull request ke `main`.

Hanya ubah file di folder paketmu. Kalau fondasi perlu diubah, bicarakan dulu di grup, karena dipakai semua orang.

## 5. Yang disediakan fondasi

```python
from app import ui
from app.errors import AturanBisnisError
from app.models import Alat, KondisiAlat

# repository.py: SELECT, hasilnya list of dict
baris = self._db.fetch_all("SELECT * FROM alat WHERE kondisi <> %s", (KondisiAlat.BAIK,))
daftar = [Alat.dari_baris(b) for b in baris]

# repository.py: satu perubahan, hasilnya jumlah baris yang cocok
jumlah = self._db.execute("UPDATE alat SET nama = %s WHERE kode = %s", (nama, kode))

# repository.py: beberapa perubahan sekaligus. Ada error -> semuanya batal.
# Di dalam blok ini SELALU pakai trx, jangan self._db.
with self._db.transaksi() as trx:
    trx.execute("UPDATE ...", (...))
    trx.execute("INSERT ...", (...))

# service.py: menolak permintaan
raise AturanBisnisError("Alat sedang dipinjam.")

# menu.py: tampilan
nim = ui.input_wajib("NIM").upper()
ui.tabel(["Kode", "Nama"], [[a.kode, a.nama] for a in daftar])
ui.sukses("Data tersimpan.")
```

`self._pembaca` (`PembacaData`) menyediakan: `ambil_mahasiswa`, `ambil_alat`, `daftar_alat_tersedia`, `ambil_transaksi`, `daftar_transaksi`, `hitung_transaksi_aktif`, `alat_di_transaksi_aktif`.

## 6. Aturan penulisan

- Input user masuk lewat `%s`, jangan f-string.
- Teks di SQL memakai kutip tunggal (`'aktif'`). Di server ini kutip ganda dianggap nama kolom.
- Menghapus berarti `dihapus = TRUE`, bukan `DELETE`. Daftar mahasiswa dan alat memakai `dihapus = FALSE`, riwayat transaksi tetap menampilkan semuanya.
- Kondisi dan status memakai enum dari `app.models`, bukan teks seperti `"baik"`.
- Jangan menangkap error di `menu.py`. `ui.jalankan_aksi` sudah menampilkannya dengan ramah.

## 7. Selesai jika

| Paket | Yang harus terbukti (dengan data dummy) |
|---|---|
| 1 | Tambah, edit, cari berhasil. NIM ganda ditolak. Hapus M001 ditolak, hapus M005 berhasil. Riwayat M003 menampilkan T003. |
| 2 | Tambah, edit, cari berhasil. Alat baru yang rusak tidak tersedia. Hapus ALT-001 dan ALT-003 ditolak (transaksinya aktif), hapus ALT-005 berhasil. Menu 7, 8, 9 menampilkan 4, 4, dan 2 alat. |
| 3 | M005 meminjam dua alat sekaligus berhasil. M001 ditolak (sudah 2 transaksi). ALT-009 ditolak. Lama 8 hari ditolak. Penolakan tidak mengubah data. T004 ditandai terlambat. |
| 4 | T001 dikembalikan sebagian, lalu selesai. Kondisi baik kembali tersedia, rusak tidak. T003 ditolak (sudah selesai). Alat yang sama tidak bisa dikembalikan dua kali. Cari M001 menampilkan T001 dan T004. |

Setelah itu pilih minimal 2 tantangan. Buat folder baru di `app/fitur/` dengan pola yang sama, lalu daftarkan di akhir list di `app/menu_utama.py`.

## 8. Perlu diputuskan kelompok

- Bolehkah mahasiswa berstatus `tidak aktif` meminjam? (Paket 3)
- Bolehkah riwayat mahasiswa yang sudah dihapus dilihat? (Paket 1)
