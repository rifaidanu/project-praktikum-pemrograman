# Panduan Pengerjaan Paket 3: Peminjaman

Untuk Danu. Paket 3 berisi **menu 3 (Buat transaksi)** dan **menu 4 (Tampilkan transaksi)**. Hanya tiga file di `app/fitur/peminjaman/` yang diubah, dan paket ini tidak menunggu paket lain.

| Langkah | Yang dikerjakan | File |
|---|---|---|
| 0 | Persiapan | `.env`, branch |
| 1 | Menu 4: tampilkan transaksi | ketiganya |
| 2 | Aturan peminjaman | `service.py` |
| 3 | Simpan ke database | `repository.py` |
| 4 | Menu 3: buat transaksi | `menu.py` |
| 5 | Uji semua kasus | — |
| 6 | Kirim | — |

**Sebelum mulai, tanyakan ke grup:** bolehkah mahasiswa berstatus `tidak aktif` meminjam? Panduan ini memakai jawaban **tidak boleh**. Cara mengubahnya ada di Langkah 2.

---

## Langkah 0: Persiapan

1. Ubah `DB_NAME` di file `.env`, supaya percobaanmu tidak masuk ke database bersama:

   ```text
   DB_NAME=dev_danu
   ```

2. Jalankan di PowerShell:

   ```powershell
   cd d:\UNS\TUGAS\praktikumPemrograman
   git switch -c fitur/paket-3
   cd project_kedua
   python scripts/init_db.py
   python main.py
   ```

**Berhasil jika:** baris terakhir `init_db.py` menyebut `Tabel di dev_danu`, dan menu 4 menampilkan `Fitur belum dikerjakan -> Paket 3`.

> Jika yang muncul `Tabel di defaultdb`, berhenti dan periksa lagi `.env`.

---

## Langkah 1: Menu 4, Tampilkan transaksi

Dikerjakan pertama karena hanya membaca data, jadi pola **menu → service → repository** terasa dulu.

### 1.1 `repository.py`

Ganti method `daftar_transaksi`:

```python
    def daftar_transaksi(self):
        """List objek Transaksi lengkap dengan itemnya."""
        return self._pembaca.daftar_transaksi()
```

**Kenapa tidak menulis SQL sendiri?** Query JOIN-nya sudah ada di `PembacaData` dan dipakai paket lain juga.

### 1.2 `service.py`

Ganti method `daftar_transaksi` dan `daftar_alat_tersedia`:

```python
    def daftar_transaksi(self):
        """List objek Transaksi."""
        return self._repository.daftar_transaksi()

    def daftar_alat_tersedia(self):
        """List objek Alat yang siap dipinjam."""
        return self._pembaca.daftar_alat_tersedia()
```

### 1.3 `menu.py`

Ganti method `tampilkan_transaksi`:

```python
    def tampilkan_transaksi(self):
        """Menu 4: Tampilkan transaksi."""
        daftar = self._service.daftar_transaksi()
        if not daftar:
            ui.info("Belum ada transaksi.")
            return
        for t in daftar:
            tanda = " [TERLAMBAT]" if t.terlambat() else ""
            print(
                f"\n[{t.id_transaksi}] {t.nama_mahasiswa} ({t.nim}) | Pinjam: {t.tgl_pinjam}"
                f" | Batas: {t.batas_kembali} | Status: {t.status.value}{tanda}"
            )
            ui.tabel(
                ["Kode", "Nama Alat", "Status", "Kondisi Kembali", "Tgl Kembali"],
                [
                    [
                        item.kode_alat,
                        item.nama_alat,
                        item.status.value,
                        item.kondisi_kembali.value if item.kondisi_kembali else None,
                        item.tgl_kembali,
                    ]
                    for item in t.daftar_item
                ],
            )
```

**Yang perlu dipahami**
- `status` berupa enum, jadi teksnya diambil dengan `.value`.
- `kondisi_kembali` bernilai `None` selama alat masih dipinjam. Tanpa pengecekan `if`, program error. `ui.tabel` menampilkan `None` sebagai `-`.

### Coba

Jalankan `python main.py`, pilih menu 4.

**Berhasil jika:** muncul 5 transaksi dan T004 bertanda `[TERLAMBAT]`. Urutannya T005, T003, T004, T002, T001 karena diurutkan dari tanggal pinjam. T001 ikut terlambat mulai 30 November 2026 dan T002 mulai 1 Desember 2026, itu bukan bug.

```powershell
git add app/fitur/peminjaman
git commit -m "feat: tampilkan transaksi"
```

---

## Langkah 2: Aturan peminjaman di `service.py`

Tambahkan import di **paling atas** file:

```python
"""Paket 3. Aturan bisnis peminjaman (menu 3 dan 4)."""
from datetime import date, timedelta

from app.errors import AturanBisnisError
from app.models import Mahasiswa, StatusMahasiswa, Transaksi
```

Ganti method `buat_transaksi`, lalu tambahkan tiga method pemeriksa di bawahnya:

```python
    def buat_transaksi(self, nim, daftar_kode, lama_hari):
        """Membuat peminjaman. Mengembalikan ID transaksi."""
        self._periksa_mahasiswa(nim)
        self._periksa_daftar_kode(daftar_kode)
        if not 1 <= lama_hari <= Transaksi.MAKS_HARI:
            raise AturanBisnisError(f"Lama pinjam harus 1 sampai {Transaksi.MAKS_HARI} hari.")
        self._periksa_alat(daftar_kode)

        tgl_pinjam = date.today()
        batas_kembali = tgl_pinjam + timedelta(days=lama_hari)
        return self._repository.simpan(nim, daftar_kode, tgl_pinjam, batas_kembali)

    def _periksa_mahasiswa(self, nim):
        mahasiswa = self._pembaca.ambil_mahasiswa(nim)
        if mahasiswa is None:
            raise AturanBisnisError(f"Mahasiswa dengan NIM '{nim}' tidak ditemukan.")
        if mahasiswa.status_aktif != StatusMahasiswa.AKTIF:
            raise AturanBisnisError(f"Mahasiswa {mahasiswa.nama} berstatus tidak aktif.")
        if self._pembaca.hitung_transaksi_aktif(nim) >= Mahasiswa.MAKS_TRANSAKSI_AKTIF:
            raise AturanBisnisError(
                f"{mahasiswa.nama} sudah punya {Mahasiswa.MAKS_TRANSAKSI_AKTIF} transaksi aktif."
            )

    @staticmethod
    def _periksa_daftar_kode(daftar_kode):
        if not daftar_kode:
            raise AturanBisnisError("Pilih minimal satu alat.")
        if len(set(daftar_kode)) != len(daftar_kode):
            raise AturanBisnisError("Ada kode alat yang ditulis lebih dari sekali.")

    def _periksa_alat(self, daftar_kode):
        for kode in daftar_kode:
            alat = self._pembaca.ambil_alat(kode)
            if alat is None:
                raise AturanBisnisError(f"Alat dengan kode '{kode}' tidak ditemukan.")
            if not alat.tersedia():
                raise AturanBisnisError(f"{alat.nama} ({kode}) berstatus {alat.status.value}.")
```

**Yang perlu dipahami**
- `raise` langsung menghentikan method, jadi `simpan` hanya terpanggil jika semua pemeriksaan lolos (Aturan 7).
- Angka 2 dan 7 diambil dari `MAKS_TRANSAKSI_AKTIF` dan `MAKS_HARI`. Jika aturannya berubah, cukup ubah satu tempat.
- **Grup membolehkan mahasiswa tidak aktif meminjam?** Hapus dua baris `if mahasiswa.status_aktif ...` dan `raise` di bawahnya, lalu hapus `StatusMahasiswa` dari import.

### Coba

Menu 3 belum ada, jadi panggil service langsung. Jalankan `python`, lalu tempel:

```python
from app.database import Database
from app.pembaca_data import PembacaData
from app.fitur.peminjaman.repository import PeminjamanRepository
from app.fitur.peminjaman.service import PeminjamanService
db = Database(); db.connect(); p = PembacaData(db)
s = PeminjamanService(PeminjamanRepository(db, p), p)
```

Lalu satu per satu:

| Ketik | Baris terakhir yang benar |
|---|---|
| `s.buat_transaksi("M001", ["ALT-005"], 3)` | `Andi Pratama sudah punya 2 transaksi aktif.` |
| `s.buat_transaksi("M005", ["ALT-009"], 3)` | `... (ALT-009) berstatus tidak tersedia.` |
| `s.buat_transaksi("M005", [], 3)` | `Pilih minimal satu alat.` |
| `s.buat_transaksi("M005", ["ALT-005"], 8)` | `Lama pinjam harus 1 sampai 7 hari.` |
| `s.buat_transaksi("M005", ["ALT-005"], 3)` | `NotImplementedError: Paket 3: PeminjamanRepository.simpan` |

Baris terakhir memang harus error: validasi sudah lolos dan berhenti di `simpan` yang belum dibuat. Ketik `exit()` untuk keluar.

```powershell
git add app/fitur/peminjaman
git commit -m "feat: validasi peminjaman"
```

---

## Langkah 3: Simpan ke database di `repository.py`

Bagian tersulit. Menyimpan satu peminjaman menyentuh tiga tabel (`transaksi`, `alat`, `detail_transaksi`), jadi harus **semua berhasil atau semua batal**.

Tambahkan import di **paling atas** file:

```python
"""Paket 3. SQL untuk peminjaman (menu 3 dan 4)."""
from app.errors import AturanBisnisError, DataGandaError
from app.models import Mahasiswa, StatusAlat, StatusItem, StatusTransaksi
```

Tambahkan satu baris di dalam class, di atas `__init__`:

```python
    MAKS_PERCOBAAN = 3
```

Ganti method `simpan`, lalu tambahkan method pembantunya:

```python
    def simpan(self, nim, daftar_kode, tgl_pinjam, batas_kembali):
        """Menyimpan satu peminjaman. Mengembalikan ID transaksi."""
        for _ in range(self.MAKS_PERCOBAAN):
            try:
                return self._simpan_sekali(nim, daftar_kode, tgl_pinjam, batas_kembali)
            except DataGandaError:
                continue  # ID sudah dipakai anggota lain, coba lagi dengan ID baru
        raise AturanBisnisError("Sistem sedang sibuk, silakan coba lagi.")

    def _simpan_sekali(self, nim, daftar_kode, tgl_pinjam, batas_kembali):
        """Semua query dalam satu transaction. Ada error -> semuanya batal."""
        with self._db.transaksi() as trx:
            self._kunci_mahasiswa(trx, nim)
            id_baru = self._buat_id(trx)
            trx.execute(
                "INSERT INTO transaksi (id, nim, tgl_pinjam, batas_kembali, status)"
                " VALUES (%s, %s, %s, %s, %s)",
                (id_baru, nim, tgl_pinjam, batas_kembali, StatusTransaksi.DIPINJAM),
            )
            for kode in sorted(daftar_kode):
                self._pinjam_alat(trx, id_baru, kode)
            return id_baru

    @staticmethod
    def _kunci_mahasiswa(trx, nim):
        """Mengunci baris mahasiswa, lalu memeriksa ulang Aturan 2."""
        mahasiswa = trx.fetch_one(
            "SELECT nim FROM mahasiswa WHERE nim = %s AND dihapus = FALSE FOR UPDATE",
            (nim,),
        )
        if mahasiswa is None:
            raise AturanBisnisError(f"Mahasiswa dengan NIM '{nim}' tidak ditemukan.")
        aktif = trx.fetch_one(
            "SELECT COUNT(*) AS jumlah FROM transaksi WHERE nim = %s AND status <> %s",
            (nim, StatusTransaksi.SELESAI),
        )
        if aktif["jumlah"] >= Mahasiswa.MAKS_TRANSAKSI_AKTIF:
            raise AturanBisnisError(
                f"Sudah mencapai batas {Mahasiswa.MAKS_TRANSAKSI_AKTIF} transaksi aktif."
            )

    @staticmethod
    def _buat_id(trx):
        """Nomor terbesar + 1. Tabel kosong menghasilkan T001."""
        baris = trx.fetch_one(
            "SELECT MAX(CAST(SUBSTRING(id, 2) AS UNSIGNED)) AS nomor FROM transaksi"
        )
        return f"T{(baris['nomor'] or 0) + 1:03d}"

    @staticmethod
    def _pinjam_alat(trx, id_transaksi, kode):
        """Menandai alat dipinjam (Aturan 1), lalu mencatatnya di detail_transaksi."""
        jumlah = trx.execute(
            "UPDATE alat SET status = %s WHERE kode = %s AND status = %s AND dihapus = FALSE",
            (StatusAlat.DIPINJAM, kode, StatusAlat.TERSEDIA),
        )
        if jumlah != 1:
            raise AturanBisnisError(f"Alat {kode} baru saja tidak tersedia.")
        trx.execute(
            "INSERT INTO detail_transaksi (id_transaksi, kode_alat, status) VALUES (%s, %s, %s)",
            (id_transaksi, kode, StatusItem.DIPINJAM),
        )
```

**Yang perlu dipahami** (kemungkinan ditanyakan saat presentasi)

| Pertanyaan | Jawaban |
|---|---|
| Kenapa tidak ada `commit` dan `rollback`? | `with self._db.transaksi()` sudah mengurusnya: selesai berarti commit, error berarti rollback. |
| Kenapa selalu `trx`, bukan `self._db`? | Semua query harus lewat `trx` agar jelas menjadi bagian dari transaction yang sama. |
| Kenapa memeriksa lagi, padahal service sudah? | Di antara pemeriksaan service dan penyimpanan, anggota lain bisa meminjam alat yang sama dari laptopnya. |
| Untuk apa `FOR UPDATE`? | Mengunci baris mahasiswa, sehingga dua peminjaman NIM yang sama diproses bergantian dan tidak lolos dari batas 2. |
| Kenapa `UPDATE ... AND status = 'tersedia'`? | Jika alat sudah diambil orang, tidak ada baris yang cocok, hasilnya 0, dan semuanya dibatalkan. |
| Kenapa ada `DataGandaError`? | Dua anggota bisa menghitung ID yang sama, misalnya T006. `PRIMARY KEY` menolak yang kedua, lalu program mencoba lagi dengan ID baru. |
| Kenapa `try` berada di luar `with`? | Transaction yang gagal harus di-rollback dulu sebelum mencoba lagi. |
| Kenapa `sorted`? | Semua laptop mengunci alat dalam urutan yang sama, sehingga mengurangi risiko saling menunggu (deadlock). |

### Coba

Buka `python`, tempel lagi enam baris dari Langkah 2, lalu:

```python
s.buat_transaksi("M005", ["ALT-005", "ALT-007"], 3)
```

**Berhasil jika:** hasilnya `'T006'` dan T006 muncul di menu 4. Setelah itu `python scripts/init_db.py --reset`.

```powershell
git add app/fitur/peminjaman
git commit -m "feat: simpan peminjaman"
```

---

## Langkah 4: Menu 3 di `menu.py`

Ubah bagian **paling atas** file menjadi:

```python
"""Paket 3. Input dan tampilan peminjaman (menu 3 dan 4)."""
from app import ui
from app.models import Transaksi
```

Ganti method `buat_transaksi`:

```python
    def buat_transaksi(self):
        """Menu 3: Buat transaksi peminjaman."""
        daftar_alat = self._service.daftar_alat_tersedia()
        if not daftar_alat:
            ui.info("Tidak ada alat yang tersedia.")
            return
        ui.tabel(
            ["Kode", "Nama", "Kategori"],
            [[a.kode, a.nama, a.kategori] for a in daftar_alat],
        )
        nim = ui.input_wajib("NIM").upper()
        teks = ui.input_wajib("Kode alat (pisahkan dengan koma)")
        daftar_kode = [k.strip().upper() for k in teks.split(",") if k.strip()]
        lama_hari = ui.input_angka("Lama pinjam (hari)", 1, Transaksi.MAKS_HARI)
        id_transaksi = self._service.buat_transaksi(nim, daftar_kode, lama_hari)
        ui.sukses(f"Peminjaman berhasil. ID transaksi: {id_transaksi}")
```

**Yang perlu dipahami**
- Input `alt-005, alt-007,` menjadi `["ALT-005", "ALT-007"]`: `split` memecah di koma, `strip` membuang spasi, `upper` membuat huruf besar, dan `if k.strip()` membuang bagian kosong.
- Tidak ada `try-except`. `ui.jalankan_aksi` yang menampilkan pesan penolakan.

```powershell
git add app/fitur/peminjaman
git commit -m "feat: menu buat transaksi"
```

---

## Langkah 5: Uji semua kasus

```powershell
python scripts/init_db.py --reset
python main.py
```

Lakukan **berurutan**. Setelah kasus yang ditolak, buka menu 4 dan pastikan tidak ada transaksi baru.

| # | Input di menu 3 | Hasil yang benar | Lulus |
|---|---|---|---|
| 1 | M001, ALT-005, 3 hari | Ditolak, sudah punya 2 transaksi | ☐ |
| 2 | M005, ALT-009, 3 hari | Ditolak, tidak tersedia | ☐ |
| 3 | M005, `ALT-005,ALT-009`, 3 hari | Ditolak, dan ALT-005 **masih ada** di daftar alat tersedia | ☐ |
| 4 | M005, `ALT-005,ALT-005`, 3 hari | Ditolak, kode ganda | ☐ |
| 5 | `O'Neil`, ALT-005, 3 hari | Ditolak ramah, tidak ada error SQL | ☐ |
| 6 | M005, ALT-XXX, 3 hari | Ditolak, alat tidak ditemukan | ☐ |
| 7 | M005, ALT-005, **8** hari | `Harus antara 1 dan 7`, diminta ulang. Tekan Ctrl+C untuk keluar, lalu jalankan lagi | ☐ |
| 8 | M006, ALT-005, 3 hari | Ditolak, mahasiswa tidak aktif | ☐ |
| 9 | M005, `alt-005, alt-007`, 3 hari | Berhasil, ID **T006** | ☐ |
| 10 | Buka lagi menu 3 | Tersisa ALT-003 dan ALT-010 | ☐ |
| 11 | Keluar, jalankan lagi, menu 4 | T006 masih ada dengan 2 alat | ☐ |

Simpan tangkapan layarnya untuk dokumen hasil pengujian. Kasus 2 dan 3 adalah skenario 3, kasus 9 skenario 2, kasus 11 bagian dari skenario 7, dan kasus 5 bagian dari skenario 10 di `project_instruction.md`.

---

## Langkah 6: Kirim

```powershell
git status
git push -u origin fitur/paket-3
```

Pastikan `git status` tidak menampilkan `.env` atau `ca.pem`. Lalu buka repo di GitHub dan buat **Pull Request** ke `main`.

Setelah semua paket digabung, kembalikan `DB_NAME=defaultdb` untuk uji bersama.

## Kalau ada masalah

| Pesan | Penyebab |
|---|---|
| `NameError: name 'AturanBisnisError' is not defined` | Import di atas file belum ditambahkan |
| `IndentationError` | Method harus menjorok 4 spasi di dalam class |
| `Fitur belum dikerjakan` padahal sudah diisi | Baris `raise NotImplementedError(...)` belum dihapus |
| `'NoneType' object has no attribute 'value'` | Pengecekan `if item.kondisi_kembali` terlewat |
| `Sistem sedang sibuk` terus-menerus | ID baru selalu bentrok, periksa `_buat_id` |
| `ModuleNotFoundError: No module named 'app'` | Terminal belum berada di folder `project_kedua` |

Masalah koneksi ada di [MULAI_DARI_NOL.md](MULAI_DARI_NOL.md).
