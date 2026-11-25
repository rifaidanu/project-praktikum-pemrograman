"""Paket 4. SQL untuk pengembalian (menu 5 dan 6)."""


class PengembalianRepository:
    """Hanya berisi SQL, tanpa input/print."""

    def __init__(self, db, pembaca):
        self._db = db
        self._pembaca = pembaca

    def simpan(self, id_transaksi, daftar_kembali, tgl_kembali):
        """Menyimpan pengembalian sebagai satu transaction. Mengembalikan StatusTransaksi baru.

        daftar_kembali: dict {kode_alat: KondisiAlat}

        TODO, semua di dalam `with self._db.transaksi() as trx:`
        1. SELECT transaksi ... FOR UPDATE, agar dua pengembalian bersamaan tidak salah hitung.
        2. Untuk tiap kode di sorted(daftar_kembali):
           UPDATE detail_transaksi SET status = 'dikembalikan', kondisi_kembali, tgl_kembali
           WHERE id_transaksi = %s AND kode_alat = %s AND status = 'dipinjam'
           Hasil execute bukan 1 berarti sudah kembali / bukan miliknya: raise AturanBisnisError.
           UPDATE alat: kondisi dan status = Alat.status_untuk_kondisi(kondisi) (Aturan 5).
        3. Hitung detail yang masih 'dipinjam'. 0 -> SELESAI, selain itu SEBAGIAN_DIKEMBALIKAN.
        4. UPDATE status transaksi (Aturan 4).
        """
        raise NotImplementedError("Paket 4: PengembalianRepository.simpan")

    def cari_per_mahasiswa(self, kata_kunci):
        """List objek Transaksi yang NIM atau nama mahasiswanya mengandung kata_kunci.

        TODO: self._pembaca.daftar_transaksi("t.nim LIKE %s OR m.nama LIKE %s", (...))
        """
        raise NotImplementedError("Paket 4: PengembalianRepository.cari_per_mahasiswa")
