# Sistem Peminjaman Alat Lab — Versi File Handling (.txt)

Turunan dari `project_satu`. Fitur, menu, dan aturan bisnisnya sama. Bedanya, data **tidak hilang** saat program ditutup karena disimpan ke file `.txt` (tanpa database, sesuai ketentuan teknis Proyek 1).

## Cara menjalankan

```bash
cd project_file_handling
python main.py
```

- **Pertama kali dijalankan:** folder `data_txt/` belum ada, jadi program mengisi data contoh lalu menyimpannya ke `.txt`.
- **Berikutnya:** data dimuat dari `data_txt/`.
- **Reset data:** hapus folder `data_txt/`.

## Alur data

```
start  -> LabManager.muat_data()   : baca .txt  -> isi Dictionary
menu   -> lab.tambah_/edit_/hapus_/buat_/proses_...
            -> ubah Dictionary
            -> LabManager.simpan_data() : tulis ulang .txt (mode 'w')
            -> catat_log()              : tambah 1 baris log.txt (mode 'a')
```

Selama program berjalan, struktur data utama tetap Dictionary/List di `LabManager`. File hanya dipakai untuk memuat dan menyimpan data.

## Format file (`data_txt/`)

Satu baris berisi satu data, dan kolomnya dipisah `|`. Baris pertama (`# ...`) adalah nama kolom.

| File | Kolom |
|---|---|
| `mahasiswa.txt` | `nim\|nama\|nomor_hp` |
| `alat.txt` | `kode_alat\|nama\|kategori\|kondisi\|status` |
| `transaksi.txt` | `id_transaksi\|nim\|nama_mahasiswa\|tgl_pinjam\|batas_kembali` |
| `detail_transaksi.txt` | `id_transaksi\|kode_alat\|nama_alat\|kategori\|sudah_kembali\|tgl_kembali\|kondisi_kembali` |
| `log.txt` | `waktu\|pesan` |

Catatan desain:
- Satu transaksi bisa berisi banyak alat (Aturan 3). Karena itu item disimpan di file terpisah (`detail_transaksi.txt`), satu baris per alat, lalu dihubungkan lewat `id_transaksi`.
- Status transaksi tidak disimpan. Status dihitung ulang dari item saat dimuat, supaya tidak bisa bertentangan dengan isi item.
- Nama mahasiswa/alat ikut disimpan di transaksi, supaya riwayat tetap terbaca walaupun datanya sudah dihapus.
- Input yang mengandung `|` ditolak karena karakter itu dipakai sebagai pemisah kolom.
- File ditulis ke `.tmp` dulu lalu diganti (`os.replace`), supaya file tidak rusak kalau program berhenti di tengah penulisan.

## File yang berubah dibanding `project_satu`

| File | Perubahan |
|---|---|
| `services/penyimpanan_txt.py` | **Baru.** Class `PenyimpananTxt` untuk baca/tulis/append file `.txt` |
| `services/lab_manager.py` | `muat_data()`, `simpan_data()`, log ditulis ke file, validasi `\|` dan kode ganda |
| `models/transaksi.py` | `ItemPeminjaman` bisa dibuat ulang dari file (status kembali ikut dimuat) |
| `fitur_program/buat_transaksi.py`, `proses_pengembalian.py` | Memakai `LabManager`, tidak lagi punya class `Transaksi` sendiri |
| `fitur_program/tampilkan_log.py` | **Baru.** Menu 12: tampilkan log aktivitas |
| `main.py` | Memuat data dari file, dan data contoh hanya dibuat saat pertama kali |
