"""Paket 3. SQL untuk peminjaman (menu 3 dan 4)."""


class PeminjamanRepository:
    """Hanya berisi SQL, tanpa input/print."""

    def __init__(self, db, pembaca):
        self._db = db
        self._pembaca = pembaca

    def simpan(self, nim, daftar_kode, tgl_pinjam, batas_kembali):
        """Menyimpan satu peminjaman sebagai satu transaction. Mengembalikan ID transaksi.

        TODO, semua di dalam `with self._db.transaksi() as trx:`
        1. SELECT mahasiswa ... FOR UPDATE, agar dua peminjaman NIM yang sama tidak lolos
           bersamaan. Tolak jika tidak ada atau sudah dihapus.
        2. Hitung lagi transaksi aktif lewat trx. Tolak jika sudah MAKS_TRANSAKSI_AKTIF.
        3. Buat ID baru: SELECT MAX(CAST(SUBSTRING(id, 2) AS UNSIGNED)) AS nomor FROM transaksi,
           tambah 1 (tabel kosong menghasilkan None), format f"T{nomor:03d}".
        4. INSERT transaksi.
        5. Untuk tiap kode di sorted(daftar_kode):
           UPDATE alat SET status = 'dipinjam'
           WHERE kode = %s AND status = 'tersedia' AND dihapus = FALSE
           Hasil execute bukan 1 berarti alat sudah diambil orang lain: raise AturanBisnisError.
           Lalu INSERT detail_transaksi.
        Error apa pun di dalam blok otomatis membatalkan semuanya (Aturan 7).
        Dua anggota bisa mendapat ID yang sama: tangkap DataGandaError di luar blok, coba ulang.
        """
        raise NotImplementedError("Paket 3: PeminjamanRepository.simpan")

    def daftar_transaksi(self):
        """TODO: self._pembaca.daftar_transaksi()."""
        raise NotImplementedError("Paket 3: PeminjamanRepository.daftar_transaksi")
