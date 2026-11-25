"""Paket 2. SQL untuk fitur alat (menu 2, 7, 8, 9)."""


class AlatRepository:
    """Hanya berisi SQL, tanpa input/print."""

    def __init__(self, db, pembaca):
        self._db = db
        self._pembaca = pembaca

    def tambah(self, alat):
        """INSERT satu objek Alat. Enum boleh langsung dijadikan params."""
        raise NotImplementedError("Paket 2: AlatRepository.tambah")

    def perbarui(self, alat, status_lama):
        """UPDATE nama, kategori, kondisi, status, dan dihapus berdasarkan kode.

        TODO: WHERE kode = %s AND status = %s (status_lama), supaya alat yang barusan dipinjam
        lewat komputer anggota lain tidak tertimpa. Kembalikan hasil execute (0 = gagal).
        """
        raise NotImplementedError("Paket 2: AlatRepository.perbarui")

    def tandai_dihapus(self, kode):
        """Mengisi dihapus = TRUE, hanya jika alat tidak ada di transaksi aktif.

        TODO, dalam satu `with self._db.transaksi() as trx:`
        1. SELECT baris alat dengan FOR UPDATE (mengunci baris).
        2. Hitung detail_transaksi JOIN transaksi yang statusnya bukan 'selesai'.
        3. Jika ada, raise AturanBisnisError (otomatis rollback). Jika tidak, UPDATE.
        """
        raise NotImplementedError("Paket 2: AlatRepository.tandai_dihapus")

    def cari(self, kata_kunci):
        """List objek Alat yang kode, nama, atau kategorinya mengandung kata_kunci.

        TODO: LIKE dengan params f"%{kata_kunci}%", dan dihapus = FALSE.
        """
        raise NotImplementedError("Paket 2: AlatRepository.cari")

    def daftar_dipinjam(self):
        """List dict alat yang sedang dipinjam beserta peminjamnya.

        TODO: JOIN alat, detail_transaksi (d.status = 'dipinjam'), transaksi, mahasiswa.
        Ambil kode, nama alat, id transaksi, nama mahasiswa, batas_kembali.
        """
        raise NotImplementedError("Paket 2: AlatRepository.daftar_dipinjam")

    def daftar_rusak(self):
        """List objek Alat yang kondisinya bukan baik dan belum dihapus."""
        raise NotImplementedError("Paket 2: AlatRepository.daftar_rusak")
