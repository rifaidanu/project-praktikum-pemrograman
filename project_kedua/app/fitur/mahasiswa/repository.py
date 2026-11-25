"""Paket 1. SQL untuk fitur mahasiswa (menu 1 dan 10)."""


class MahasiswaRepository:
    """Hanya berisi SQL, tanpa input/print."""

    def __init__(self, db, pembaca):
        self._db = db
        self._pembaca = pembaca

    def tambah(self, mahasiswa):
        """INSERT satu objek Mahasiswa.

        TODO: self._db.execute("INSERT INTO mahasiswa (...) VALUES (%s, ...)",
                               (mahasiswa.nim, ...))
        """
        raise NotImplementedError("Paket 1: MahasiswaRepository.tambah")

    def perbarui(self, mahasiswa):
        """UPDATE nama, no_hp, status_aktif, dan dihapus berdasarkan nim."""
        raise NotImplementedError("Paket 1: MahasiswaRepository.perbarui")

    def tandai_dihapus(self, nim):
        """Mengisi dihapus = TRUE, hanya jika mahasiswa tidak punya transaksi aktif.

        TODO, dalam satu `with self._db.transaksi() as trx:`
        1. SELECT baris mahasiswa dengan FOR UPDATE (mengunci baris).
        2. Hitung transaksi yang statusnya bukan 'selesai' lewat trx.fetch_one.
        3. Jika ada, raise AturanBisnisError (otomatis rollback). Jika tidak, UPDATE.
        """
        raise NotImplementedError("Paket 1: MahasiswaRepository.tandai_dihapus")

    def cari(self, kata_kunci):
        """List objek Mahasiswa yang NIM atau namanya mengandung kata_kunci.

        TODO: WHERE dihapus = FALSE AND (nim LIKE %s OR nama LIKE %s), params f"%{kata_kunci}%".
        Kata kunci kosong berarti semua mahasiswa. Ubah baris dengan Mahasiswa.dari_baris.
        """
        raise NotImplementedError("Paket 1: MahasiswaRepository.cari")

    def riwayat(self, nim):
        """List objek Transaksi milik mahasiswa, aktif maupun selesai.

        TODO: self._pembaca.daftar_transaksi("t.nim = %s", (nim,))
        """
        raise NotImplementedError("Paket 1: MahasiswaRepository.riwayat")
